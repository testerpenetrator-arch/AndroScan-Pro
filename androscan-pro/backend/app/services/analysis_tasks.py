from __future__ import annotations

import os
import tempfile

from app.db.session import SessionLocal
from app.models.analysis import Analysis
from app.models.application import APKVersion
from app.models.tool_execution import ToolExecution
from app.models.organization_configuration import OrganizationConfiguration
from app.services.analysis_orchestrator import transition_analysis
from app.services.apk_storage import ObjectStorageError, S3ObjectStorage
from app.services.sandbox import DockerSandboxManager, SandboxError
from app.services.tools.registry import get_enabled_tools
from app.services.tools.runner import SandboxToolRunner, ToolRunnerError
from app.worker import celery_app


def _copy_apk_into_sandbox(manager: DockerSandboxManager, container_id: str, apk_path: str) -> None:
    try:
        import subprocess
        subprocess.run(
            ["docker", "cp", apk_path, f"{container_id}:/work/input.apk"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SandboxError("No fue posible copiar el APK al sandbox") from exc


@celery_app.task(name="androscan.queue_analysis")
def queue_analysis_task(analysis_id: str) -> str:
    """Prepara el sandbox y ejecuta herramientas estáticas dentro de él."""
    db = SessionLocal()
    manager = DockerSandboxManager()
    try:
        analysis = db.get(Analysis, analysis_id)
        if not analysis or analysis.state != "QUEUED":
            return "ignored"

        version = db.get(APKVersion, analysis.apk_version_id)
        if not version:
            analysis.error_code = "APK_VERSION_NOT_FOUND"
            analysis.error_message = "No se encontró la versión APK asociada"
            transition_analysis(db, analysis, "FAILED")
            db.commit()
            return "analysis_failed"

        transition_analysis(db, analysis, "PREPARING")
        try:
            container_id = manager.create(analysis.id)
            with tempfile.NamedTemporaryFile(prefix="androscan-", suffix=".apk", delete=False) as tmp:
                apk_path = tmp.name
            try:
                S3ObjectStorage().download_to_file(version.storage_key, apk_path)
                _copy_apk_into_sandbox(manager, container_id, apk_path)
            finally:
                try:
                    os.unlink(apk_path)
                except FileNotFoundError:
                    pass
        except (SandboxError, ObjectStorageError) as exc:
            analysis.sandbox_status = "FAILED"
            analysis.error_code = "SANDBOX_PREPARATION_FAILED"
            analysis.error_message = str(exc)
            transition_analysis(db, analysis, "FAILED")
            db.commit()
            return "sandbox_failed"

        analysis.sandbox_container_id = container_id
        analysis.sandbox_status = "READY"
        db.commit()

        transition_analysis(db, analysis, "RUNNING")
        db.commit()

        runner = SandboxToolRunner(manager)
        org_config = db.scalar(select(OrganizationConfiguration).where(
            OrganizationConfiguration.organization_id == analysis.organization_id
        ))
        enabled_ids = (org_config.tool_policy_json.get("enabled_tools", ["jadx", "apktool", "mobsf"])
                       if org_config else [tool.tool_id for tool in get_enabled_tools()])
        results = []
        for tool in get_enabled_tools():
            if tool.tool_id not in enabled_ids:
                continue
            try:
                result = runner.execute(container_id, tool)
            except ToolRunnerError as exc:
                execution = ToolExecution(
                    analysis_id=analysis.id,
                    tool_id=tool.tool_id,
                    tool_name=tool.name,
                    tool_version=tool.version,
                    state="FAILED",
                    exit_code=None,
                    stdout="",
                    stderr=str(exc)[-12000:],
                    started_at=analysis.started_at,
                    finished_at=analysis.started_at,
                )
            else:
                execution = ToolExecution(
                    analysis_id=analysis.id,
                    tool_id=result.tool_id,
                    tool_name=tool.name,
                    tool_version=result.tool_version,
                    state=result.state,
                    exit_code=result.exit_code,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    started_at=result.started_at,
                    finished_at=result.finished_at,
                )
            db.add(execution)
            results.append(execution)
            db.commit()

        transition_analysis(db, analysis, "PROCESSING_RESULTS")
        analysis.summary_json = {
            "tools_total": len(results),
            "tools_completed": sum(1 for item in results if item.state == "COMPLETED"),
            "tools_failed": sum(1 for item in results if item.state in {"FAILED", "TIMEOUT"}),
            "execution_backend": "sandbox",
            "provenance": "tool_execution",
        }
        transition_analysis(db, analysis, "COMPLETED")
        db.commit()
        return "analysis_completed"
    except Exception:
        db.rollback()
        analysis = db.get(Analysis, analysis_id)
        if analysis and analysis.state not in {"COMPLETED", "FAILED", "CANCELLED"}:
            analysis.error_code = "ANALYSIS_EXECUTION_FAILED"
            analysis.error_message = "Error controlado durante la ejecución de herramientas"
            try:
                transition_analysis(db, analysis, "FAILED")
            except ValueError:
                pass
            db.commit()
        return "analysis_failed"
    finally:
        try:
            analysis = db.get(Analysis, analysis_id)
            if analysis and analysis.sandbox_container_id:
                try:
                    manager.remove(analysis.sandbox_container_id)
                    analysis.sandbox_status = "REMOVED"
                    analysis.sandbox_container_id = None
                    db.commit()
                except SandboxError:
                    analysis.sandbox_status = "CLEANUP_FAILED"
                    db.commit()
        finally:
            db.close()
