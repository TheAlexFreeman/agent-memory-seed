#!/usr/bin/env python3
"""Resolve the governed-write capability manifest against the MCP runtime."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    import tomli as tomllib


MANIFEST_PATH = Path("HUMANS/tooling/agent-memory-capabilities.toml")
REQUIRED_TOOL_SET_KEYS = (
    "read_support",
    "raw_fallback",
    "semantic_extensions",
    "declared_gaps",
)
REQUIRED_CHANGE_CLASS_KEYS = (
    "approval",
    "user_awareness",
    "ui_affordance",
    "read_only_behavior",
    "notes",
)
REQUIRED_OPERATION_KEYS = (
    "group",
    "tier",
    "change_class",
    "commit_model",
    "writes",
    "owns_frontmatter",
    "owns_summaries",
    "owns_access_logs",
    "owns_review_queue",
    "result_fields",
    "fallback_tools",
    "error_kinds",
)
REQUIRED_RAW_FALLBACK_POLICY_KEYS = (
    "policy",
    "requires_change_class",
    "preview_required_for",
    "read_only_mode",
)


def load_manifest(repo_root: Path) -> dict[str, Any]:
    manifest_text = (repo_root / MANIFEST_PATH).read_text(encoding="utf-8")
    return tomllib.loads(manifest_text)


def runtime_tools(repo_root: Path) -> set[str]:
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from tools.agent_memory_mcp.server import create_mcp

    _, tools, _, _ = create_mcp(repo_root=repo_root)
    return set(tools)


def _ensure_string_list(
    errors: list[str], label: str, value: Any
) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        errors.append(f"{label} must be an array of strings")
        return []
    return value


def resolve_capabilities(
    repo_root: Path, *, include_runtime: bool = True
) -> dict[str, Any]:
    manifest = load_manifest(repo_root)
    errors: list[str] = []
    warnings: list[str] = []

    if manifest.get("version") != 1:
        errors.append(f"{MANIFEST_PATH}: version must be 1")

    tool_sets = manifest.get("tool_sets")
    if not isinstance(tool_sets, dict):
        errors.append(f"{MANIFEST_PATH}: tool_sets must be a TOML table")
        tool_sets = {}

    tool_lists = {
        key: _ensure_string_list(errors, f"tool_sets.{key}", tool_sets.get(key))
        for key in REQUIRED_TOOL_SET_KEYS
    }

    read_support = set(tool_lists["read_support"])
    raw_fallback = set(tool_lists["raw_fallback"])
    semantic_extensions = set(tool_lists["semantic_extensions"])
    declared_gaps = set(tool_lists["declared_gaps"])

    for left_name, left, right_name, right in (
        ("read_support", read_support, "raw_fallback", raw_fallback),
        ("read_support", read_support, "semantic_extensions", semantic_extensions),
        ("raw_fallback", raw_fallback, "semantic_extensions", semantic_extensions),
    ):
        overlap = sorted(left & right)
        if overlap:
            errors.append(
                f"{MANIFEST_PATH}: tool_sets.{left_name} and tool_sets.{right_name} overlap: {overlap!r}"
            )

    shared_result = manifest.get("shared_result")
    if not isinstance(shared_result, dict):
        errors.append(f"{MANIFEST_PATH}: shared_result must be a TOML table")
        shared_result = {}
    shared_fields = _ensure_string_list(
        errors, "shared_result.fields", shared_result.get("fields")
    )
    if shared_fields != [
        "files_changed",
        "commit_sha",
        "commit_message",
        "new_state",
        "warnings",
    ]:
        errors.append(
            f"{MANIFEST_PATH}: shared_result.fields must match the MemoryWriteResult contract"
        )

    change_classes = manifest.get("change_classes")
    if not isinstance(change_classes, dict):
        errors.append(f"{MANIFEST_PATH}: change_classes must be a TOML table")
        change_classes = {}
    for class_name, config in change_classes.items():
        if not isinstance(config, dict):
            errors.append(
                f"{MANIFEST_PATH}: change_classes.{class_name} must be a TOML table"
            )
            continue
        for key in REQUIRED_CHANGE_CLASS_KEYS:
            if not isinstance(config.get(key), str):
                errors.append(
                    f"{MANIFEST_PATH}: change_classes.{class_name}.{key} must be a string"
                )

    raw_fallback_policy = manifest.get("raw_fallback_policy")
    if not isinstance(raw_fallback_policy, dict):
        errors.append(f"{MANIFEST_PATH}: raw_fallback_policy must be a TOML table")
        raw_fallback_policy = {}
    for key in REQUIRED_RAW_FALLBACK_POLICY_KEYS:
        if key not in raw_fallback_policy:
            errors.append(f"{MANIFEST_PATH}: raw_fallback_policy missing {key}")
    if raw_fallback_policy.get("policy") != "inherit_operation_change_class":
        errors.append(
            f"{MANIFEST_PATH}: raw_fallback_policy.policy must be 'inherit_operation_change_class'"
        )
    if raw_fallback_policy.get("requires_change_class") is not True:
        errors.append(
            f"{MANIFEST_PATH}: raw_fallback_policy.requires_change_class must be true"
        )
    preview_required_for = _ensure_string_list(
        errors,
        "raw_fallback_policy.preview_required_for",
        raw_fallback_policy.get("preview_required_for"),
    )
    for class_name in preview_required_for:
        if class_name not in change_classes:
            errors.append(
                f"{MANIFEST_PATH}: raw_fallback_policy.preview_required_for references unknown class {class_name!r}"
            )
    if not isinstance(raw_fallback_policy.get("read_only_mode"), str):
        errors.append(
            f"{MANIFEST_PATH}: raw_fallback_policy.read_only_mode must be a string"
        )

    error_taxonomy = manifest.get("error_taxonomy")
    if not isinstance(error_taxonomy, dict):
        errors.append(f"{MANIFEST_PATH}: error_taxonomy must be a TOML table")
        error_taxonomy = {}

    operations = manifest.get("operations")
    if not isinstance(operations, dict):
        errors.append(f"{MANIFEST_PATH}: operations must be a TOML table")
        operations = {}

    for tool_name in semantic_extensions:
        op = operations.get(tool_name)
        if not isinstance(op, dict):
            errors.append(f"{MANIFEST_PATH}: missing operations.{tool_name} table")
            continue
        for key in REQUIRED_OPERATION_KEYS:
            if key not in op:
                errors.append(f"{MANIFEST_PATH}: operations.{tool_name} missing {key}")
        if op.get("tier") != "semantic":
            errors.append(f"{MANIFEST_PATH}: operations.{tool_name}.tier must be 'semantic'")
        change_class = op.get("change_class")
        if change_class not in change_classes:
            errors.append(
                f"{MANIFEST_PATH}: operations.{tool_name}.change_class references unknown class {change_class!r}"
            )
        fallback_tools = _ensure_string_list(
            errors,
            f"operations.{tool_name}.fallback_tools",
            op.get("fallback_tools"),
        )
        for fallback_tool in fallback_tools:
            if fallback_tool not in raw_fallback:
                errors.append(
                    f"{MANIFEST_PATH}: operations.{tool_name}.fallback_tools references unknown raw tool {fallback_tool!r}"
                )
        error_kinds = _ensure_string_list(
            errors,
            f"operations.{tool_name}.error_kinds",
            op.get("error_kinds"),
        )
        for error_kind in error_kinds:
            if error_kind not in error_taxonomy:
                errors.append(
                    f"{MANIFEST_PATH}: operations.{tool_name}.error_kinds references unknown error {error_kind!r}"
                )

    desktop_operations = manifest.get("desktop_operations")
    if not isinstance(desktop_operations, dict):
        errors.append(f"{MANIFEST_PATH}: desktop_operations must be a TOML table")
        desktop_operations = {}

    implemented_desktop_ops: dict[str, str] = {}
    gap_ops: list[str] = []
    for operation_name, config in desktop_operations.items():
        if not isinstance(config, dict):
            errors.append(
                f"{MANIFEST_PATH}: desktop_operations.{operation_name} must be a TOML table"
            )
            continue
        status = config.get("status")
        change_class = config.get("change_class")
        if change_class not in change_classes:
            errors.append(
                f"{MANIFEST_PATH}: desktop_operations.{operation_name}.change_class references unknown class {change_class!r}"
            )
        if status == "implemented":
            tool_name = config.get("tool")
            if not isinstance(tool_name, str):
                errors.append(
                    f"{MANIFEST_PATH}: desktop_operations.{operation_name}.tool must be a string"
                )
                continue
            if tool_name not in semantic_extensions:
                errors.append(
                    f"{MANIFEST_PATH}: desktop_operations.{operation_name} references non-semantic tool {tool_name!r}"
                )
            if operations.get(tool_name, {}).get("change_class") != change_class:
                errors.append(
                    f"{MANIFEST_PATH}: desktop_operations.{operation_name}.change_class must match operations.{tool_name}.change_class"
                )
            implemented_desktop_ops[operation_name] = tool_name
        elif status == "gap":
            gap_ops.append(operation_name)
            if operation_name not in declared_gaps:
                warnings.append(
                    f"{MANIFEST_PATH}: desktop gap {operation_name!r} is not listed in tool_sets.declared_gaps"
                )
        else:
            errors.append(
                f"{MANIFEST_PATH}: desktop_operations.{operation_name}.status must be 'implemented' or 'gap'"
            )

    runtime_tool_names: set[str] = set()
    if include_runtime:
        runtime_tool_names = runtime_tools(repo_root)
        for tool_name in sorted(read_support | raw_fallback | semantic_extensions):
            if tool_name not in runtime_tool_names:
                errors.append(
                    f"{MANIFEST_PATH}: declared tool {tool_name!r} is not exported by the MCP runtime"
                )

    return {
        "manifest_path": str(repo_root / MANIFEST_PATH),
        "change_classes": change_classes,
        "tool_sets": {
            "read_support": sorted(read_support),
            "raw_fallback": sorted(raw_fallback),
            "semantic_extensions": sorted(semantic_extensions),
            "declared_gaps": sorted(declared_gaps),
        },
        "raw_fallback_policy": raw_fallback_policy,
        "implemented_desktop_operations": implemented_desktop_ops,
        "gap_operations": sorted(gap_ops),
        "operation_change_classes": {
            tool_name: operations[tool_name]["change_class"]
            for tool_name in sorted(semantic_extensions)
            if isinstance(operations.get(tool_name), dict)
            and "change_class" in operations[tool_name]
        },
        "runtime_tools": sorted(runtime_tool_names),
        "errors": errors,
        "warnings": warnings,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve the agent-memory capability manifest against the MCP runtime."
    )
    parser.add_argument(
        "repo_root",
        nargs="?",
        default=".",
        help="Path to the memory repo root.",
    )
    parser.add_argument(
        "--skip-runtime",
        action="store_true",
        help="Only validate manifest structure; do not import the MCP runtime.",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation level for output.",
    )
    return parser.parse_args(argv[1:])


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv)
    repo_root = Path(args.repo_root).resolve()
    resolution = resolve_capabilities(repo_root, include_runtime=not args.skip_runtime)
    json.dump(resolution, sys.stdout, indent=args.indent)
    sys.stdout.write("\n")
    return 1 if resolution["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
