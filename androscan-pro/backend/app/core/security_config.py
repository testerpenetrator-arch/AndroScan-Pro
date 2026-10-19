"""Validaciones de configuración segura para despliegues de producción."""

INSECURE_VALUES = {
    "change-me",
    "changeme",
    "replace-with-a-random-secret",
    "development-secret-change-me-32-bytes!!",
    "androscan-development-only",
    "androscan",
}


def validate_production_secrets(settings) -> None:
    """Falla de forma cerrada si producción conserva secretos vacíos o predeterminados."""
    checks = {
        "JWT_SECRET_KEY": settings.jwt_secret_key,
        "S3_SECRET_KEY": settings.s3_secret_key,
    }
    problems = []
    for name, value in checks.items():
        if not value or value.strip().lower() in INSECURE_VALUES:
            problems.append(f"{name} ausente o predeterminado")
    if len(settings.jwt_secret_key or "") < 32:
        problems.append("JWT_SECRET_KEY debe tener al menos 32 caracteres")
    if problems:
        raise RuntimeError("Configuración insegura para producción: " + "; ".join(problems))
