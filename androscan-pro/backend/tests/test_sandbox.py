from unittest.mock import patch

import pytest

from app.services.sandbox import DockerSandboxManager, SandboxError


def test_sandbox_create_uses_security_boundary(monkeypatch):
    monkeypatch.setenv("SANDBOX_IMAGE", "alpine:test")
    manager = DockerSandboxManager()
    fake = type("R", (), {"stdout": "container-123\n"})()

    with patch("app.services.sandbox.subprocess.run", return_value=fake) as run:
        result = manager.create("analysis-1")

    assert result == "container-123"
    command = run.call_args.args[0]
    assert "--network" in command and command[command.index("--network") + 1] == "none"
    assert "--read-only" in command
    assert "--cap-drop" in command and command[command.index("--cap-drop") + 1] == "ALL"
    assert "--security-opt" in command
    assert "no-new-privileges:true" in command
    assert "--pids-limit" in command
    assert "--memory" in command
    assert "--cpus" in command


def test_sandbox_create_failure_is_controlled():
    manager = DockerSandboxManager()
    with patch("app.services.sandbox.subprocess.run", side_effect=OSError("docker missing")):
        with pytest.raises(SandboxError):
            manager.create("analysis-1")


def test_sandbox_remove_calls_force_remove():
    manager = DockerSandboxManager()
    with patch("app.services.sandbox.subprocess.run") as run:
        manager.remove("container-123")
    assert run.call_args.args[0] == ["docker", "rm", "-f", "container-123"]


def test_sandbox_configuration_is_positive():
    manager = DockerSandboxManager()
    assert manager.limits.cpu > 0
    assert manager.limits.memory_mb > 0
    assert manager.limits.pids > 0
    assert manager.limits.timeout_seconds > 0
    assert manager.limits.storage_mb > 0
