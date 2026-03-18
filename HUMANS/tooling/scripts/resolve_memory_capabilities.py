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
    "commit_category_hint",
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
REQUIRED_FALLBACK_PROFILE_KEYS = (
    "trigger",
    "raw_tools_allowed",
    "requires_change_class",
    "requires_contract_preservation",
    "result",
)
REQUIRED_FALLBACK_PROFILES = (
    "semantic_gap",
    "uninterpretable_target",
    "preview_only",
    "read_only",
)
REQUIRED_APPROVAL_PREVIEW_KEYS = (
    "required_for",
    "sections",
    "show_resulting_state",
    "show_warnings",
)
REQUIRED_APPROVAL_FLOW_KEYS = (
    "trigger",
    "primary_action",
    "secondary_actions",
    "deferred_outcome",
    "copy_style",
)
REQUIRED_APPROVAL_PREVIEW_SECTIONS = (
    "summary",
    "reasoning",
    "target_files",
    "invariant_effects",
    "commit_suggestion",
    "fallback_behavior",
)
ALLOWED_COMMIT_CATEGORY_HINTS = {
    "chat",
    "curation",
    "identity",
    "knowledge",
    "plan",
    "scratchpad",
    "system",
}


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


def _ensure_bool(errors: list[str], label: str, value: Any) -> bool:
    if not isinstance(value, bool):
        errors.append(f"{label} must be a boolean")
        return False
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

    fallback_behavior = manifest.get("fallback_behavior")
    if not isinstance(fallback_behavior, dict):
        errors.append(f"{MANIFEST_PATH}: fallback_behavior must be a TOML table")
        fallback_behavior = {}
    for profile_name in REQUIRED_FALLBACK_PROFILES:
        profile = fallback_behavior.get(profile_name)
        if not isinstance(profile, dict):
            errors.append(
                f"{MANIFEST_PATH}: fallback_behavior.{profile_name} must be a TOML table"
            )
            continue
        for key in REQUIRED_FALLBACK_PROFILE_KEYS:
            if key not in profile:
                errors.append(
                    f"{MANIFEST_PATH}: fallback_behavior.{profile_name} missing {key}"
                )
        if not isinstance(profile.get("trigger"), str):
            errors.append(
                f"{MANIFEST_PATH}: fallback_behavior.{profile_name}.trigger must be a string"
            )
        _ensure_bool(
            errors,
            f"fallback_behavior.{profile_name}.raw_tools_allowed",
            profile.get("raw_tools_allowed"),
        )
        if profile.get("requires_change_class") is not True:
            errors.append(
                f"{MANIFEST_PATH}: fallback_behavior.{profile_name}.requires_change_class must be true"
            )
        _ensure_bool(
            errors,
            f"fallback_behavior.{profile_name}.requires_contract_preservation",
            profile.get("requires_contract_preservation"),
        )
        if not isinstance(profile.get("result"), str):
            errors.append(
                f"{MANIFEST_PATH}: fallback_behavior.{profile_name}.result must be a string"
            )

    expected_fallback_flags = {
        "semantic_gap": {"raw_tools_allowed": True, "requires_contract_preservation": True},
        "uninterpretable_target": {
            "raw_tools_allowed": False,
            "requires_contract_preservation": True,
        },
        "preview_only": {
            "raw_tools_allowed": False,
            "requires_contract_preservation": False,
        },
        "read_only": {
            "raw_tools_allowed": False,
            "requires_contract_preservation": False,
        },
    }
    for profile_name, expectations in expected_fallback_flags.items():
        profile = fallback_behavior.get(profile_name)
        if not isinstance(profile, dict):
            continue
        for key, expected in expectations.items():
            if profile.get(key) != expected:
                errors.append(
                    f"{MANIFEST_PATH}: fallback_behavior.{profile_name}.{key} must be {expected!r}"
                )

    approval_ux = manifest.get("approval_ux")
    if not isinstance(approval_ux, dict):
        errors.append(f"{MANIFEST_PATH}: approval_ux must be a TOML table")
        approval_ux = {}

    preview = approval_ux.get("preview")
    if not isinstance(preview, dict):
        errors.append(f"{MANIFEST_PATH}: approval_ux.preview must be a TOML table")
        preview = {}
    for key in REQUIRED_APPROVAL_PREVIEW_KEYS:
        if key not in preview:
            errors.append(f"{MANIFEST_PATH}: approval_ux.preview missing {key}")
    preview_required_for = _ensure_string_list(
        errors,
        "approval_ux.preview.required_for",
        preview.get("required_for"),
    )
    for class_name in preview_required_for:
        if class_name not in change_classes:
            errors.append(
                f"{MANIFEST_PATH}: approval_ux.preview.required_for references unknown class {class_name!r}"
            )
    for class_name in ("proposed", "protected"):
        if class_name not in preview_required_for:
            errors.append(
                f"{MANIFEST_PATH}: approval_ux.preview.required_for must include {class_name!r}"
            )
    preview_sections = _ensure_string_list(
        errors,
        "approval_ux.preview.sections",
        preview.get("sections"),
    )
    for section_name in REQUIRED_APPROVAL_PREVIEW_SECTIONS:
        if section_name not in preview_sections:
            errors.append(
                f"{MANIFEST_PATH}: approval_ux.preview.sections must include {section_name!r}"
            )
    _ensure_bool(
        errors,
        "approval_ux.preview.show_resulting_state",
        preview.get("show_resulting_state"),
    )
    _ensure_bool(
        errors,
        "approval_ux.preview.show_warnings",
        preview.get("show_warnings"),
    )

    approval_flows: dict[str, dict[str, Any]] = {}
    for class_name in ("proposed", "protected"):
        flow = approval_ux.get(class_name)
        if not isinstance(flow, dict):
            errors.append(
                f"{MANIFEST_PATH}: approval_ux.{class_name} must be a TOML table"
            )
            flow = {}
        approval_flows[class_name] = flow
        for key in REQUIRED_APPROVAL_FLOW_KEYS:
            if key not in flow:
                errors.append(f"{MANIFEST_PATH}: approval_ux.{class_name} missing {key}")
        if not isinstance(flow.get("trigger"), str):
            errors.append(
                f"{MANIFEST_PATH}: approval_ux.{class_name}.trigger must be a string"
            )
        if not isinstance(flow.get("primary_action"), str):
            errors.append(
                f"{MANIFEST_PATH}: approval_ux.{class_name}.primary_action must be a string"
            )
        _ensure_string_list(
            errors,
            f"approval_ux.{class_name}.secondary_actions",
            flow.get("secondary_actions"),
        )
        if not isinstance(flow.get("deferred_outcome"), str):
            errors.append(
                f"{MANIFEST_PATH}: approval_ux.{class_name}.deferred_outcome must be a string"
            )
        if not isinstance(flow.get("copy_style"), str):
            errors.append(
                f"{MANIFEST_PATH}: approval_ux.{class_name}.copy_style must be a string"
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
        commit_category_hint = op.get("commit_category_hint")
        if commit_category_hint not in ALLOWED_COMMIT_CATEGORY_HINTS:
            errors.append(
                f"{MANIFEST_PATH}: operations.{tool_name}.commit_category_hint must be one of {sorted(ALLOWED_COMMIT_CATEGORY_HINTS)!r}"
            )
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
            fallback_profile = config.get("fallback_profile")
            if not isinstance(fallback_profile, str):
                errors.append(
                    f"{MANIFEST_PATH}: desktop_operations.{operation_name}.fallback_profile must be a string for gap operations"
                )
            elif fallback_profile not in fallback_behavior:
                errors.append(
                    f"{MANIFEST_PATH}: desktop_operations.{operation_name}.fallback_profile references unknown fallback profile {fallback_profile!r}"
                )
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
        "fallback_behavior": fallback_behavior,
        "approval_ux": {
            "preview": preview,
            "proposed": approval_flows.get("proposed", {}),
            "protected": approval_flows.get("protected", {}),
        },
        "implemented_desktop_operations": implemented_desktop_ops,
        "gap_operations": sorted(gap_ops),
        "gap_operation_fallback_profiles": {
            operation_name: desktop_operations[operation_name]["fallback_profile"]
            for operation_name in sorted(gap_ops)
            if isinstance(desktop_operations.get(operation_name), dict)
            and "fallback_profile" in desktop_operations[operation_name]
        },
        "operation_change_classes": {
            tool_name: operations[tool_name]["change_class"]
            for tool_name in sorted(semantic_extensions)
            if isinstance(operations.get(tool_name), dict)
            and "change_class" in operations[tool_name]
        },
        "operation_commit_categories": {
            tool_name: operations[tool_name]["commit_category_hint"]
            for tool_name in sorted(semantic_extensions)
            if isinstance(operations.get(tool_name), dict)
            and "commit_category_hint" in operations[tool_name]
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
