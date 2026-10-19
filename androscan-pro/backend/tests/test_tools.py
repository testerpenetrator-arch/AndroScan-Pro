from unittest.mock import patch

from app.services.tools.registry import get_enabled_tools
from app.services.tools.runner import SandboxToolRunner


def test_static_tool_registry_contains_expected_tools():
    ids = {tool.tool_id for tool in get_enabled_tools()}
    assert {"jadx", "apktool", "mobsf"}.issubset(ids)


def test_tool_runner_uses_docker_exec_and_never_host_command():
    manager = type("M", (), {"limits": type("L", (), {"timeout_seconds": 900})()})()
    runner = SandboxToolRunner(manager)
    tool = next(tool for tool in get_enabled_tools() if tool.tool_id == "jadx")
    fake = type("R", (), {"returncode": 0, "stdout": "ok", "stderr": ""})()

    with patch("app.services.tools.runner.subprocess.run", return_value=fake) as run:
        result = runner.execute("sandbox-1", tool)

    command = run.call_args.args[0]
    assert command[:3] == ["docker", "exec", "sandbox-1"]
    assert result.state == "COMPLETED"
    assert result.tool_id == "jadx"


def test_tool_runner_records_failure_without_raising_for_nonzero_exit():
    manager = type("M", (), {"limits": type("L", (), {"timeout_seconds": 900})()})()
    runner = SandboxToolRunner(manager)
    tool = next(tool for tool in get_enabled_tools() if tool.tool_id == "apktool")
    fake = type("R", (), {"returncode": 2, "stdout": "", "stderr": "decode error"})()

    with patch("app.services.tools.runner.subprocess.run", return_value=fake):
        result = runner.execute("sandbox-1", tool)

    assert result.state == "FAILED"
    assert result.exit_code == 2
    assert "decode error" in result.stderr
