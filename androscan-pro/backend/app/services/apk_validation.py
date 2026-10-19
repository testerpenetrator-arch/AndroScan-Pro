from __future__ import annotations

import hashlib
import re
import stat
import zipfile
from dataclasses import dataclass
from pathlib import PurePosixPath

from fastapi import UploadFile


@dataclass
class APKValidationResult:
    size_bytes: int
    sha256: str
    metadata: dict


class APKValidationError(ValueError):
    pass


PACKAGE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)+$")


def _validate_zip_entries(infos: list[zipfile.ZipInfo]) -> None:
    required = {"AndroidManifest.xml", "classes.dex"}
    normalized = set()
    for info in infos:
        name = info.filename
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or "\\" in name or "\x00" in name:
            raise APKValidationError("El APK contiene una ruta de archivo no permitida")
        if name.endswith("/"):
            continue
        mode = (info.external_attr >> 16) & 0xFFFF
        if stat.S_ISLNK(mode):
            raise APKValidationError("El APK contiene un enlace simbólico no permitido")
        normalized.add(name)
    missing = sorted(required - normalized)
    if missing:
        raise APKValidationError(f"El APK no contiene estructuras requeridas: {', '.join(missing)}")


def validate_package_name(value: str) -> None:
    if not PACKAGE_RE.fullmatch(value):
        raise APKValidationError("El package_name no tiene un formato Android válido")


async def validate_apk(upload: UploadFile, max_size_bytes: int) -> APKValidationResult:
    if not upload.filename or not upload.filename.lower().endswith(".apk"):
        raise APKValidationError("El archivo debe tener extensión .apk")

    await upload.seek(0)
    header = await upload.read(4)
    if header != b"PK\x03\x04":
        raise APKValidationError("La firma del archivo no corresponde a un ZIP/APK válido")
    await upload.seek(0)

    sha = hashlib.sha256()
    size = 0
    while True:
        chunk = await upload.read(1024 * 1024)
        if not chunk:
            break
        size += len(chunk)
        if size > max_size_bytes:
            raise APKValidationError("El APK supera el límite configurado")
        sha.update(chunk)

    await upload.seek(0)
    try:
        with zipfile.ZipFile(upload.file) as archive:
            if archive.testzip() is not None:
                raise APKValidationError("El APK contiene una entrada ZIP corrupta")
            infos = archive.infolist()
            _validate_zip_entries(infos)
            names = {info.filename for info in infos}
            metadata = {
                "zip_entries": len(infos),
                "has_resources_arsc": "resources.arsc" in names,
                "has_res_directory": any(name.startswith("res/") for name in names),
                "has_lib_directory": any(name.startswith("lib/") for name in names),
            }
    except zipfile.BadZipFile as exc:
        raise APKValidationError("El archivo no es un contenedor ZIP/APK válido") from exc
    finally:
        await upload.seek(0)

    return APKValidationResult(size_bytes=size, sha256=sha.hexdigest(), metadata=metadata)
