try:
    from celery import Celery
except ModuleNotFoundError:  # pragma: no cover - solo permite importar/testear sin extras instalados
    class _LocalTask:
        def __init__(self, fn):
            self.fn = fn

        def __call__(self, *args, **kwargs):
            return self.fn(*args, **kwargs)

        def delay(self, *args, **kwargs):
            return self.fn(*args, **kwargs)

    class _LocalCelery:
        def __init__(self, *args, **kwargs):
            self.conf = {}

        def task(self, name=None):
            def decorator(fn):
                return _LocalTask(fn)
            return decorator

    Celery = _LocalCelery

from app.core.config import get_settings

settings = get_settings()
celery_app = Celery("androscan", broker=settings.redis_url, backend=settings.redis_url)
try:
    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
    )
except AttributeError:
    pass


@celery_app.task(name="androscan.health_check_task")
def health_check_task() -> str:
    return "ok"


# Importación explícita para registrar la tarea de orquestación.
from app.services import analysis_tasks  # noqa: E402,F401
