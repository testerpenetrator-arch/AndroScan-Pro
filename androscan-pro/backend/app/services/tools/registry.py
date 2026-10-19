from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ToolDefinition:
    tool_id: str
    name: str
    version: str
    kind: str
    command: tuple[str, ...]
    output_dir: str
    enabled: bool = True


# Versions are intentionally configurable and must be pinned in deployment.
TOOL_REGISTRY: tuple[ToolDefinition, ...] = (
    ToolDefinition(
        tool_id="jadx",
        name="JADX",
        version="1.5.3-bundled",
        kind="static",
        command=("jadx", "-q", "-d", "/work/jadx", "/work/input.apk"),
        output_dir="/work/jadx",
    ),
    ToolDefinition(
        tool_id="apktool",
        name="Apktool",
        version="3.0.3-bundled",
        kind="static",
        command=("apktool", "d", "--force", "/work/input.apk", "-o", "/work/apktool"),
        output_dir="/work/apktool",
    ),
    ToolDefinition(
        tool_id="mobsf",
        name="MobSF",
        version="4.5.3",
        kind="static",
        command=("mobsf-scan",),
        output_dir="/work/mobsf",
    ),
)


def get_enabled_tools() -> list[ToolDefinition]:
    return [tool for tool in TOOL_REGISTRY if tool.enabled]


def get_tool(tool_id: str) -> ToolDefinition | None:
    return next((tool for tool in TOOL_REGISTRY if tool.tool_id == tool_id), None)
