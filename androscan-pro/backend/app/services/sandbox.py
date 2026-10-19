from __future__ import annotations

import subprocess
from dataclasses import dataclass

from app.core.config import get_settings


class SandboxError(RuntimeError):
    pass


@dataclass(frozen=True)
class SandboxLimits:
    cpu: float
    memory_mb: int
    pids: int
    timeout_seconds: int
    storage_mb: int


class DockerSandboxManager:
    """Gestiona un contenedor aislado para una ejecución de análisis.

    F9.5 prepara el perímetro de aislamiento; todavía no ejecuta APK ni herramientas.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self.image = settings.sandbox_image
        self.limits = SandboxLimits(
            cpu=settings.sandbox_cpu,
            memory_mb=settings.sandbox_memory_mb,
            pids=settings.sandbox_pids,
            timeout_seconds=settings.sandbox_timeout_seconds,
            storage_mb=settings.sandbox_storage_mb,
        )

    def create(self, analysis_id: str) -> str:
        name = f"androscan-sbx-{analysis_id}"
        memory = f"{self.limits.memory_mb}m"
        storage = f"size={self.limits.storage_mb}m"
        command = [
            "docker", "create",
            "--name", name,
            "--network", "none",
            "--read-only",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges:true",
            "--pids-limit", str(self.limits.pids),
            "--cpus", str(self.limits.cpu),
            "--memory", memory,
            "--tmpfs", f"/tmp:rw,nosuid,nodev,noexec,{storage}",
            "--tmpfs", f"/work:rw,nosuid,nodev,noexec,{storage}",
            "--tmpfs", "/home/mobsf/.MobSF:rw,nosuid,nodev,noexec,size=512m",
            self.image,
            "sleep", str(self.limits.timeout_seconds),
        ]
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
        except (OSError, subprocess.CalledProcessError) as exc:
            raise SandboxError("No fue posible crear el sandbox") from exc
        container_id = result.stdout.strip()
        if not container_id:
            raise SandboxError("Docker no devolvió el identificador del sandbox")
        return container_id

    def remove(self, container_id: str) -> None:
        try:
            subprocess.run(
                ["docker", "rm", "-f", container_id],
                check=True,
                capture_output=True,
                text=True,
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            raise SandboxError("No fue posible eliminar el sandbox") from exc
