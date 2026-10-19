from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone

from app.services.sandbox import DockerSandboxManager, SandboxError
from app.services.tools.registry import ToolDefinition


@dataclass(frozen=True)
class ToolExecutionResult:
    tool_id: str
    tool_version: str
    state: str
    exit_code: int | None
    stdout: str
    stderr: str
    started_at: datetime
    finished_at: datetime


class ToolRunnerError(RuntimeError):
    pass


class SandboxToolRunner:
    """Ejecuta una herramienta dentro del sandbox existente.

    El runner nunca ejecuta el comando directamente en el host.
    """

    def __init__(self, sandbox_manager: DockerSandboxManager | None = None) -> None:
        self.sandbox_manager = sandbox_manager or DockerSandboxManager()

    def execute(self, container_id: str, tool: ToolDefinition) -> ToolExecutionResult:
        started = datetime.now(timezone.utc)
        command = ["docker", "exec", container_id, *tool.command]
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.sandbox_manager.limits.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            finished = datetime.now(timezone.utc)
            return ToolExecutionResult(
                tool_id=tool.tool_id,
                tool_version=tool.version,
                state="TIMEOUT",
                exit_code=None,
                stdout=(exc.stdout or "")[-12000:],
                stderr=(exc.stderr or "")[-12000:],
                started_at=started,
                finished_at=finished,
            )
        except OSError as exc:
            raise ToolRunnerError(f"No fue posible ejecutar {tool.tool_id}") from exc

        finished = datetime.now(timezone.utc)
        return ToolExecutionResult(
            tool_id=tool.tool_id,
            tool_version=tool.version,
            state="COMPLETED" if completed.returncode == 0 else "FAILED",
            exit_code=completed.returncode,
            stdout=completed.stdout[-12000:],
            stderr=completed.stderr[-12000:],
            started_at=started,
            finished_at=finished,
        )
