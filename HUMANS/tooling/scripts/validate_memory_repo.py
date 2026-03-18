#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    import tomli as tomllib


CONTENT_DIRS = ("identity", "knowledge", "skills", "plans")
ACCESS_DIRS = ("identity", "knowledge", "skills", "plans", "chats")
IGNORED_DIR_NAMES = {".git", ".claude", "__pycache__", ".pytest_cache"}

REQUIRED_FRONTMATTER_KEYS = (
    "source",
    "origin_session",
    "created",
    "trust",
)
ALLOWED_SOURCE_VALUES = {
    "user-stated",
    "agent-inferred",
    "agent-generated",
    "external-research",
    "skill-discovery",
    "template",
    "unknown",
}
ALLOWED_TRUST_VALUES = {"high", "medium", "low"}
ALLOWED_PLAN_STATUS_VALUES = {"active", "paused", "complete"}
CANONICAL_ORIGIN_SESSION_RE = re.compile(r"^chats/\d{4}/\d{2}/\d{2}/chat-\d{3}$")
LEGACY_ORIGIN_SESSION_RE = re.compile(r"^chat-\d{3}$")
SPECIAL_ORIGIN_SESSION_VALUES = {"setup", "manual", "unknown"}

REQUIRED_ACCESS_FIELDS = {"file", "date", "task", "helpfulness", "note"}
OPTIONAL_ACCESS_FIELDS = {"session_id", "category"}

EXPECTED_QUICK_REFERENCE_PARAMETERS = (
    "Low-trust retirement threshold",
    "Medium-trust flagging threshold",
    "Staleness trigger (no access)",
    "Aggregation trigger",
    "Identity churn alarm",
    "Knowledge flooding alarm",
    "Task similarity method",
    "Cluster co-retrieval threshold",
)

BOOTSTRAP_MANIFEST_PATH = Path("agent-bootstrap.toml")
EXPECTED_BOOTSTRAP_MODES = (
    "first_run",
    "returning",
    "full_bootstrap",
    "periodic_review",
    "automation",
)
EXPECTED_BOOTSTRAP_COST_VALUES = {"light", "medium", "heavy"}
EXPECTED_BOOTSTRAP_TOKEN_BUDGETS = {
    "first_run": 20000,
    "returning": 7000,
    "full_bootstrap": 25000,
    "periodic_review": 25000,
    "automation": 7000,
}
EXPECTED_BOOTSTRAP_PREFER_SUMMARIES = {
    "first_run": False,
    "returning": True,
    "full_bootstrap": True,
    "periodic_review": True,
    "automation": True,
}
EXPECTED_RETURNING_STEP_PATHS = (
    "meta/quick-reference.md",
    "identity/SUMMARY.md",
    "chats/SUMMARY.md",
    "plans/SUMMARY.md",
    "scratchpad/USER.md",
    "scratchpad/CURRENT.md",
)
EXPECTED_FIRST_RUN_STEP_PATHS = (
    "meta/quick-reference.md",
    "README.md",
    "meta/first-run.md",
)
EXPECTED_FULL_BOOTSTRAP_STEP_PATHS = (
    "meta/quick-reference.md",
    "README.md",
    "identity/SUMMARY.md",
    "chats/SUMMARY.md",
    "plans/SUMMARY.md",
    "scratchpad/USER.md",
    "scratchpad/CURRENT.md",
    "CHANGELOG.md",
    "meta/curation-policy.md",
    "meta/update-guidelines.md",
)
EXPECTED_PERIODIC_REVIEW_STEP_PATHS = EXPECTED_FULL_BOOTSTRAP_STEP_PATHS + (
    "meta/system-maturity.md",
    "meta/belief-diff-log.md",
    "meta/review-queue.md",
    "meta/integrity-checklist.md",
)
EXPECTED_AUTOMATION_STEP_PATHS = (
    "meta/quick-reference.md",
    "scratchpad/USER.md",
    "scratchpad/CURRENT.md",
    "plans/SUMMARY.md",
)
EXPECTED_MODE_STEP_PATHS = {
    "first_run": EXPECTED_FIRST_RUN_STEP_PATHS,
    "returning": EXPECTED_RETURNING_STEP_PATHS,
    "full_bootstrap": EXPECTED_FULL_BOOTSTRAP_STEP_PATHS,
    "periodic_review": EXPECTED_PERIODIC_REVIEW_STEP_PATHS,
    "automation": EXPECTED_AUTOMATION_STEP_PATHS,
}
EXPECTED_BOOTSTRAP_ON_DEMAND = ("knowledge/SUMMARY.md", "skills/SUMMARY.md")
EXPECTED_BOOTSTRAP_MAINTENANCE_PROBES = (
    "meta/review-queue.md:load_only_when_non_placeholder",
    "ACCESS.jsonl:count_non_empty_lines",
)

RUNTIME_GUIDANCE_FILES = (
    Path("README.md"),
    Path("HUMANS/docs/QUICKSTART.md"),
    Path("meta/quick-reference.md"),
    Path("meta/curation-policy.md"),
    Path("meta/update-guidelines.md"),
    Path("meta/session-checklists.md"),
)
PROMPT_COPY_FILES = (
    Path("setup/setup.sh"),
    Path("setup/setup.html"),
    Path("HUMANS/docs/QUICKSTART.md"),
)
SETUP_GUIDANCE_FILES = (
    Path("setup/setup.sh"),
    Path("HUMANS/docs/QUICKSTART.md"),
)
ONBOARDING_EXPORT_TEMPLATE_PATH = Path("HUMANS/tooling/onboard-export-template.md")
ONBOARDING_EXPORT_REQUIRED_PHRASE = (
    "bash HUMANS/tooling/scripts/onboard-export.sh <file>"
)
ONBOARDING_EXPORT_FORBIDDEN_PATTERNS = (
    r"bash scripts/onboard-export\.sh(?: <file>)?",
)
ADAPTER_FILES = (Path("AGENTS.md"), Path("CLAUDE.md"), Path(".cursorrules"))
ROOT_SETUP_TARGETS = {
    Path("setup.sh"): "setup/setup.sh",
    Path("setup.html"): "setup/setup.html",
}
CANONICAL_SETUP_FILES = (Path("setup/setup.sh"), Path("setup/setup.html"))

PROMPT_START_LINE = (
    "Start with `meta/quick-reference.md` and follow its routing and context-loading rules."
)
PROMPT_ROUTE_LINE = (
    "Use the compact returning manifest for normal sessions. If `meta/quick-reference.md` routes you to first-run or full bootstrap, read `README.md` and follow the referenced docs."
)
PROMPT_MCP_LINE = (
    "If local agent-memory MCP tools are available, prefer them for memory reads, search, and governed writes; fall back to direct file access only when the MCP surface is unavailable or lacks the needed operation."
)
LIVE_CONFIG_LINE = (
    "meta/quick-reference.md is the live runtime config; do not use hardcoded thresholds."
)
ADAPTER_ROUTING_PHRASE = "follow the routing rules in `meta/quick-reference.md`"
ADAPTER_MCP_PHRASE = "When local agent-memory MCP tools are available, prefer them for memory reads, search, and governed writes"
README_START_PHRASE = "Start every session with `meta/quick-reference.md`."
README_ARCHITECTURE_PHRASE = (
    "Read this file in full when `meta/quick-reference.md` routes you to a first run, full bootstrap, or periodic review"
)
README_MCP_PHRASE = (
    "When local agent-memory MCP tools are available, prefer them for memory reads, search, and governed writes; fall back to direct file access only when the MCP surface is unavailable or lacks the needed operation."
)
QUICK_REFERENCE_ROUTER_PHRASE = (
    "Use this file as the operational router for every session:"
)
FIRST_RUN_MCP_PHRASE = README_MCP_PHRASE
SESSION_CHECKLISTS_MCP_PHRASE = README_MCP_PHRASE
SKILLS_SUMMARY_MCP_PHRASE = (
    "When local agent-memory MCP tools are available, prefer them for memory reads, search, and governed writes while executing these skills; fall back to direct file access only when the MCP surface is unavailable or lacks the needed operation."
)
ONBOARDING_SKILL_MCP_PHRASE = (
    "When local agent-memory MCP tools are available, prefer them for memory reads, search, and governed writes during onboarding; fall back to direct file access only when the MCP surface is unavailable or lacks the needed operation."
)
SESSION_START_SKILL_MCP_PHRASE = (
    "When local agent-memory MCP tools are available, prefer them for memory reads and search during session start; fall back to direct file access only when the MCP surface is unavailable or lacks the needed operation."
)
SESSION_SYNC_SKILL_MCP_PHRASE = (
    "When local agent-memory MCP tools are available, prefer them for memory reads and writes during checkpointing; fall back to direct file access only when the MCP surface is unavailable or lacks the needed operation."
)
SESSION_WRAPUP_SKILL_MCP_PHRASE = (
    "When local agent-memory MCP tools are available, prefer them for memory reads, search, and governed writes during wrap-up; fall back to direct file access only when the MCP surface is unavailable or lacks the needed operation."
)
SESSION_CHECKLISTS_ON_DEMAND_PHRASE = "Load this file on demand"
SETUP_GUIDANCE_REQUIRED_PATTERNS = (
    r"live routing (?:in|from)\s+`?meta/quick-reference\.md`?",
)
SETUP_GUIDANCE_FORBIDDEN_PATTERNS = (
    r"follow the bootstrap sequence",
)
SESSION_START_SKILL_PATH = Path("skills/session-start.md")
SESSION_START_REQUIRED_PHRASES = (
    "compact returning manifest in `meta/quick-reference.md`",
    "Load `meta/session-checklists.md` only when you want more detail",
    "If `meta/review-queue.md` still contains only its placeholder, skip it.",
    "Load it only when there are real pending items or the user asks about them.",
    SESSION_START_SKILL_MCP_PHRASE,
)
SESSION_START_FORBIDDEN_PATTERNS = (
    r"after README\.md has been read",
    r"^- Read `meta/review-queue\.md`\.",
    r"compact checklist in `meta/session-checklists\.md` is sufficient",
)
SESSION_WRAPUP_SKILL_PATH = Path("skills/session-wrapup.md")
SESSION_WRAPUP_REQUIRED_PHRASES = (
    "Load `meta/session-checklists.md` only when you want",
    "session-end runbook",
    SESSION_WRAPUP_SKILL_MCP_PHRASE,
)
SESSION_WRAPUP_FORBIDDEN_PATTERNS = (
    r"compact checklist in `meta/session-checklists\.md` is sufficient",
)
SKILLS_SUMMARY_PATH = Path("skills/SUMMARY.md")
ONBOARDING_SKILL_PATH = Path("skills/onboarding.md")
SESSION_SYNC_SKILL_PATH = Path("skills/session-sync.md")

FORBIDDEN_RUNTIME_PATTERNS = (
    r"Check the current maturity stage in `meta/system-maturity\.md`",
    r"see `meta/system-maturity\.md` for the stage-appropriate value",
    r"use those values from `meta/system-maturity\.md`",
    r"Thresholds are stage-specific; see `meta/system-maturity\.md`",
    r"The active thresholds are always determined by the system's current maturity stage as assessed in `meta/system-maturity\.md`",
    r"The session boundary is proxied by the `date` field",
    r"groups entries by date, identifies file sets co-occurring",
    r"start with README\.md and follow its routing rules",
    r"Use meta/first-run\.md for blank-slate onboarding, meta/session-checklists\.md for returning sessions",
    r"This file is loaded every session",
    r"follow the bootstrap sequence and rules in README\.md",
    r"This file is your entry point\. Read it fully before doing anything else\.",
    r"Normal day-to-day use via `meta/session-checklists\.md`",
    r"Use `meta/session-checklists\.md` § \"Session start\"",
    r"compact returning-session checklist",
    r"~2,000–5,000",
)


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def repo_root_from_argv(argv: list[str]) -> Path:
    if len(argv) > 1:
        return Path(argv[1]).resolve()
    return Path(__file__).resolve().parents[3]


def read_text(path: Path, result: ValidationResult) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        result.error(f"{path}: could not decode as UTF-8 ({exc})")
    except OSError as exc:
        result.error(f"{path}: could not read file ({exc})")
    return None


def should_ignore(path: Path) -> bool:
    return any(part in IGNORED_DIR_NAMES for part in path.parts)


def iter_content_files(root: Path) -> list[Path]:
    paths: list[Path] = []
    for dirname in CONTENT_DIRS:
        base = root / dirname
        if not base.exists():
            continue
        for path in base.rglob("*.md"):
            if should_ignore(path.relative_to(root)):
                continue
            if path.name == "SUMMARY.md":
                continue
            paths.append(path)
    return sorted(paths)


def iter_access_files(root: Path) -> list[Path]:
    paths: list[Path] = []
    for dirname in ACCESS_DIRS:
        base = root / dirname
        if not base.exists():
            continue
        for path in base.rglob("ACCESS*.jsonl"):
            if should_ignore(path.relative_to(root)):
                continue
            paths.append(path)
    return sorted(paths)


def parse_frontmatter(
    path: Path, text: str, result: ValidationResult
) -> dict[str, str] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    end_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break
    if end_index is None:
        result.error(
            f"{path}: frontmatter starts with '---' but has no closing delimiter"
        )
        return None

    data: dict[str, str] = {}
    for offset, line in enumerate(lines[1:end_index], start=2):
        if not line.strip():
            continue
        if ":" not in line:
            result.error(f"{path}:{offset}: malformed frontmatter line {line!r}")
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key or not value:
            result.error(f"{path}:{offset}: malformed frontmatter key/value pair")
            continue
        data[key] = value
    return data


def validate_iso_date(
    value: object, path: Path, field_name: str, result: ValidationResult
) -> None:
    if not isinstance(value, str):
        result.error(f"{path}: {field_name} must be a string in YYYY-MM-DD format")
        return
    try:
        date.fromisoformat(value)
    except ValueError:
        result.error(
            f"{path}: {field_name} must be a valid YYYY-MM-DD date, got {value!r}"
        )


def validate_frontmatter(path: Path, root: Path, result: ValidationResult) -> None:
    text = read_text(path, result)
    if text is None:
        return

    frontmatter = parse_frontmatter(path, text, result)
    if frontmatter is None:
        result.warn(f"{path}: missing YAML frontmatter")
        return

    missing = [key for key in REQUIRED_FRONTMATTER_KEYS if key not in frontmatter]
    if missing:
        result.error(f"{path}: missing required frontmatter keys: {', '.join(missing)}")
        return

    source = frontmatter["source"]
    if source not in ALLOWED_SOURCE_VALUES:
        result.error(f"{path}: invalid source {source!r}")

    trust = frontmatter["trust"]
    if trust not in ALLOWED_TRUST_VALUES:
        result.error(f"{path}: invalid trust {trust!r}")

    validate_iso_date(frontmatter["created"], path, "created", result)
    if "last_verified" in frontmatter:
        validate_iso_date(frontmatter["last_verified"], path, "last_verified", result)

    origin_session = frontmatter["origin_session"]
    if origin_session in SPECIAL_ORIGIN_SESSION_VALUES:
        pass
    elif CANONICAL_ORIGIN_SESSION_RE.fullmatch(origin_session):
        pass
    elif LEGACY_ORIGIN_SESSION_RE.fullmatch(origin_session):
        result.warn(
            f"{path}: legacy origin_session {origin_session!r}; prefer chats/YYYY/MM/DD/chat-NNN"
        )
    else:
        result.error(
            f"{path}: origin_session must be chats/YYYY/MM/DD/chat-NNN, setup, manual, or unknown"
        )

    relative_path = path.relative_to(root)
    if relative_path.parts[0] == "plans":
        plan_type = frontmatter.get("type")
        if not plan_type:
            result.error(f"{path}: plan files must define frontmatter key 'type'")
        elif not plan_type.endswith("-plan"):
            result.error(f"{path}: plan type must end with '-plan', got {plan_type!r}")

        status = frontmatter.get("status")
        if not status:
            result.error(f"{path}: plan files must define frontmatter key 'status'")
        elif status not in ALLOWED_PLAN_STATUS_VALUES:
            result.error(
                f"{path}: plan status must be one of {sorted(ALLOWED_PLAN_STATUS_VALUES)!r}, got {status!r}"
            )

        next_action = frontmatter.get("next_action")
        if not next_action:
            result.error(f"{path}: plan files must define non-empty frontmatter key 'next_action'")


def validate_access_file(path: Path, result: ValidationResult) -> None:
    text = read_text(path, result)
    if text is None:
        return

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            result.error(f"{path}:{line_number}: malformed JSON ({exc.msg})")
            continue

        if not isinstance(payload, dict):
            result.error(f"{path}:{line_number}: ACCESS entry must decode to an object")
            continue

        missing = sorted(REQUIRED_ACCESS_FIELDS - payload.keys())
        if missing:
            result.error(
                f"{path}:{line_number}: missing required ACCESS fields: {', '.join(missing)}"
            )
            continue

        if not isinstance(payload["file"], str):
            result.error(f"{path}:{line_number}: file must be a string")
        validate_iso_date(payload["date"], path, f"line {line_number} date", result)
        if not isinstance(payload["task"], str):
            result.error(f"{path}:{line_number}: task must be a string")
        if not isinstance(payload["note"], str):
            result.error(f"{path}:{line_number}: note must be a string")

        helpfulness = payload["helpfulness"]
        if not isinstance(helpfulness, (int, float)):
            result.error(f"{path}:{line_number}: helpfulness must be numeric")
        elif not 0.0 <= float(helpfulness) <= 1.0:
            result.error(
                f"{path}:{line_number}: helpfulness must be between 0.0 and 1.0"
            )

        if "session_id" in payload:
            session_id = payload["session_id"]
            if not isinstance(session_id, str):
                result.error(
                    f"{path}:{line_number}: session_id must be a string when present"
                )
            elif not CANONICAL_ORIGIN_SESSION_RE.fullmatch(session_id):
                result.error(
                    f"{path}:{line_number}: session_id must match chats/YYYY/MM/DD/chat-NNN when present, got {session_id!r}"
                )
        if "category" in payload and not isinstance(payload["category"], str):
            result.error(
                f"{path}:{line_number}: category must be a string when present"
            )

        unknown_keys = set(payload) - REQUIRED_ACCESS_FIELDS - OPTIONAL_ACCESS_FIELDS
        if unknown_keys:
            result.warn(
                f"{path}:{line_number}: unknown ACCESS fields present: {', '.join(sorted(unknown_keys))}"
            )


def extract_manifest_row(text: str, session_type: str) -> str | None:
    pattern = re.compile(
        rf"^\| \*\*{re.escape(session_type)}\*\* \| (?P<body>.+?) \|$",
        re.MULTILINE,
    )
    match = pattern.search(text)
    if match is None:
        return None
    return match.group("body")


def validate_agent_bootstrap_manifest(root: Path, result: ValidationResult) -> None:
    path = root / BOOTSTRAP_MANIFEST_PATH
    if not path.exists():
        result.error(f"{path}: missing bootstrap manifest")
        return

    text = read_text(path, result)
    if text is None:
        return

    try:
        manifest = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        result.error(f"{path}: invalid TOML ({exc})")
        return

    version = manifest.get("version")
    if version != 1:
        result.error(f"{path}: version must be 1, got {version!r}")

    router = manifest.get("router")
    if router != "meta/quick-reference.md":
        result.error(
            f"{path}: router must be 'meta/quick-reference.md', got {router!r}"
        )
    elif not (root / router).exists():
        result.error(f"{path}: router target {router!r} does not exist")

    default_mode = manifest.get("default_mode")
    if default_mode != "returning":
        result.error(f"{path}: default_mode must be 'returning', got {default_mode!r}")

    adapter_files = manifest.get("adapter_files")
    expected_adapter_files = [str(adapter_path) for adapter_path in ADAPTER_FILES]
    if adapter_files != expected_adapter_files:
        result.error(
            f"{path}: adapter_files must be {expected_adapter_files!r}, got {adapter_files!r}"
        )

    mode_detection = manifest.get("mode_detection")
    if not isinstance(mode_detection, dict):
        result.error(f"{path}: mode_detection must be a TOML table")
    else:
        for key in EXPECTED_BOOTSTRAP_MODES:
            value = mode_detection.get(key)
            if not isinstance(value, str) or not value.strip():
                result.error(
                    f"{path}: mode_detection.{key} must be a non-empty string"
                )
        for key in (
            "warn_on_detached_head",
            "warn_on_worktree_branch_drift",
            "warn_on_branch_checked_out_elsewhere",
        ):
            if not isinstance(mode_detection.get(key), bool):
                result.error(f"{path}: mode_detection.{key} must be a boolean")

    modes = manifest.get("modes")
    if not isinstance(modes, dict):
        result.error(f"{path}: modes must be a TOML table")
        return

    missing_modes = [mode for mode in EXPECTED_BOOTSTRAP_MODES if mode not in modes]
    if missing_modes:
        result.error(
            f"{path}: missing required bootstrap modes: {', '.join(missing_modes)}"
        )

    for mode_name in EXPECTED_BOOTSTRAP_MODES:
        mode = modes.get(mode_name)
        if not isinstance(mode, dict):
            result.error(f"{path}: modes.{mode_name} must be a TOML table")
            continue

        expected_budget = EXPECTED_BOOTSTRAP_TOKEN_BUDGETS[mode_name]
        if mode.get("token_budget") != expected_budget:
            result.error(
                f"{path}: modes.{mode_name}.token_budget must be {expected_budget}, got {mode.get('token_budget')!r}"
            )

        expected_prefer_summaries = EXPECTED_BOOTSTRAP_PREFER_SUMMARIES[mode_name]
        if mode.get("prefer_summaries") is not expected_prefer_summaries:
            result.error(
                f"{path}: modes.{mode_name}.prefer_summaries must be {expected_prefer_summaries!r}"
            )

        if mode_name != "first_run":
            if mode.get("on_demand") != list(EXPECTED_BOOTSTRAP_ON_DEMAND):
                result.error(
                    f"{path}: modes.{mode_name}.on_demand must be {list(EXPECTED_BOOTSTRAP_ON_DEMAND)!r}"
                )
            if mode.get("maintenance_probes") != list(
                EXPECTED_BOOTSTRAP_MAINTENANCE_PROBES
            ):
                result.error(
                    f"{path}: modes.{mode_name}.maintenance_probes must be {list(EXPECTED_BOOTSTRAP_MAINTENANCE_PROBES)!r}"
                )

        steps = mode.get("steps")
        if not isinstance(steps, list) or not steps:
            result.error(f"{path}: modes.{mode_name}.steps must be a non-empty array")
            continue

        step_paths: list[str] = []
        seen_paths: set[str] = set()
        for index, step in enumerate(steps, start=1):
            if not isinstance(step, dict):
                result.error(
                    f"{path}: modes.{mode_name}.steps[{index}] must be a table"
                )
                continue

            step_path = step.get("path")
            if not isinstance(step_path, str) or not step_path:
                result.error(
                    f"{path}: modes.{mode_name}.steps[{index}].path must be a non-empty string"
                )
                continue
            if step_path in seen_paths:
                result.error(
                    f"{path}: modes.{mode_name} declares duplicate step path {step_path!r}"
                )
            seen_paths.add(step_path)
            step_paths.append(step_path)

            if not (root / step_path).exists():
                result.error(
                    f"{path}: modes.{mode_name}.steps[{index}] references missing path {step_path!r}"
                )

            role = step.get("role")
            if not isinstance(role, str) or not role.strip():
                result.error(
                    f"{path}: modes.{mode_name}.steps[{index}].role must be a non-empty string"
                )

            if not isinstance(step.get("required"), bool):
                result.error(
                    f"{path}: modes.{mode_name}.steps[{index}].required must be a boolean"
                )

            cost = step.get("cost")
            if cost not in EXPECTED_BOOTSTRAP_COST_VALUES:
                result.error(
                    f"{path}: modes.{mode_name}.steps[{index}].cost must be one of {sorted(EXPECTED_BOOTSTRAP_COST_VALUES)!r}, got {cost!r}"
                )

            skip_if = step.get("skip_if")
            if skip_if is not None and not isinstance(skip_if, str):
                result.error(
                    f"{path}: modes.{mode_name}.steps[{index}].skip_if must be a string when present"
                )

        expected_step_paths = list(EXPECTED_MODE_STEP_PATHS[mode_name])
        if step_paths != expected_step_paths:
            result.error(
                f"{path}: modes.{mode_name}.steps must load {expected_step_paths!r}, got {step_paths!r}"
            )


def validate_quick_reference(root: Path, result: ValidationResult) -> None:
    path = root / "meta" / "quick-reference.md"
    text = read_text(path, result)
    if text is None:
        return

    for parameter in EXPECTED_QUICK_REFERENCE_PARAMETERS:
        if parameter not in text:
            result.error(f"{path}: missing active parameter name {parameter!r}")

    required_phrases = (
        "single authoritative source",
        QUICK_REFERENCE_ROUTER_PHRASE,
        "Grouping precedence:",
        "`session_id`",
        "`date`",
        "Exploration defaults apply",
        "metadata-first maintenance probes",
        "Count non-empty lines in `ACCESS.jsonl` files",
        "task-relevant `knowledge/SUMMARY.md` and/or `skills/SUMMARY.md`",
    )
    for phrase in required_phrases:
        if phrase not in text:
            result.error(f"{path}: missing required runtime guidance phrase {phrase!r}")

    compact_row = extract_manifest_row(text, "Compact returning")
    if compact_row is None:
        result.error(f"{path}: missing manifest row for 'Compact returning'")
        return

    required_compact_markers = (
        "identity/SUMMARY.md",
        "chats/SUMMARY.md",
        "plans/SUMMARY.md",
        "scratchpad/USER.md",
        "scratchpad/CURRENT.md",
        "task-relevant `knowledge/SUMMARY.md` and/or `skills/SUMMARY.md`",
    )
    for marker in required_compact_markers:
        if marker not in compact_row:
            result.error(f"{path}: compact manifest is missing {marker!r}")

    forbidden_compact_markers = ("README.md", "session-checklists")
    for marker in forbidden_compact_markers:
        if marker in compact_row:
            result.error(
                f"{path}: compact manifest must not require {marker!r} on returning sessions"
            )


def validate_runtime_guidance(root: Path, result: ValidationResult) -> None:
    for relative_path in RUNTIME_GUIDANCE_FILES:
        path = root / relative_path
        if not path.exists():
            result.error(f"{path}: missing runtime guidance file")
            continue
        text = read_text(path, result)
        if text is None:
            continue
        for pattern in FORBIDDEN_RUNTIME_PATTERNS:
            if re.search(pattern, text):
                result.error(
                    f"{path}: contains forbidden runtime guidance pattern {pattern!r}"
                )


def validate_setup_entrypoints(root: Path, result: ValidationResult) -> None:
    for path, target in ROOT_SETUP_TARGETS.items():
        absolute = root / path
        if not absolute.exists():
            result.error(f"{absolute}: missing repo-root setup entrypoint")
            continue
        text = read_text(absolute, result)
        if text is None:
            continue
        if target not in text:
            result.error(f"{absolute}: expected to reference {target!r}")

    for path in CANONICAL_SETUP_FILES:
        absolute = root / path
        if not absolute.exists():
            result.error(f"{absolute}: missing canonical setup implementation")


def validate_adapter_routing(root: Path, result: ValidationResult) -> None:
    for relative_path in ADAPTER_FILES:
        path = root / relative_path
        if not path.exists():
            result.error(f"{path}: missing adapter file")
            continue
        text = read_text(path, result)
        if text is None:
            continue
        if "meta/quick-reference.md" not in text:
            result.error(f"{path}: must point agents to meta/quick-reference.md")
        if ADAPTER_ROUTING_PHRASE not in text:
            result.error(f"{path}: missing adapter routing phrase {ADAPTER_ROUTING_PHRASE!r}")
        if ADAPTER_MCP_PHRASE not in text:
            result.error(f"{path}: missing MCP preference phrase {ADAPTER_MCP_PHRASE!r}")


def validate_prompt_copy(root: Path, result: ValidationResult) -> None:
    for relative_path in PROMPT_COPY_FILES:
        path = root / relative_path
        if not path.exists():
            result.error(f"{path}: missing prompt-copy file")
            continue
        text = read_text(path, result)
        if text is None:
            continue
        for phrase in (PROMPT_START_LINE, PROMPT_ROUTE_LINE, PROMPT_MCP_LINE, LIVE_CONFIG_LINE):
            if phrase not in text:
                result.error(f"{path}: missing prompt-copy phrase {phrase!r}")


def validate_setup_guidance(root: Path, result: ValidationResult) -> None:
    for relative_path in SETUP_GUIDANCE_FILES:
        path = root / relative_path
        if not path.exists():
            result.error(f"{path}: missing setup-guidance file")
            continue
        text = read_text(path, result)
        if text is None:
            continue
        for pattern in SETUP_GUIDANCE_REQUIRED_PATTERNS:
            if not re.search(pattern, text):
                result.error(
                    f"{path}: missing setup-guidance pattern {pattern!r}"
                )
        for pattern in SETUP_GUIDANCE_FORBIDDEN_PATTERNS:
            if re.search(pattern, text):
                result.error(
                    f"{path}: contains forbidden setup-guidance pattern {pattern!r}"
                )


def validate_onboarding_export_template(root: Path, result: ValidationResult) -> None:
    path = root / ONBOARDING_EXPORT_TEMPLATE_PATH
    if not path.exists():
        result.error(f"{path}: missing onboarding export template")
        return

    text = read_text(path, result)
    if text is None:
        return

    if ONBOARDING_EXPORT_REQUIRED_PHRASE not in text:
        result.error(
            f"{path}: missing onboarding-export phrase {ONBOARDING_EXPORT_REQUIRED_PHRASE!r}"
        )

    for pattern in ONBOARDING_EXPORT_FORBIDDEN_PATTERNS:
        if re.search(pattern, text):
            result.error(
                f"{path}: contains forbidden onboarding-export pattern {pattern!r}"
            )


def validate_contract_consistency(root: Path, result: ValidationResult) -> None:
    readme = read_text(root / "README.md", result)
    if readme is not None:
        for phrase in (README_START_PHRASE, README_ARCHITECTURE_PHRASE, README_MCP_PHRASE):
            if phrase not in readme:
                result.error(f"{root / 'README.md'}: missing contract phrase {phrase!r}")

    session_checklists = read_text(root / "meta" / "session-checklists.md", result)
    if session_checklists is not None:
        if SESSION_CHECKLISTS_ON_DEMAND_PHRASE not in session_checklists:
            result.error(
                f"{root / 'meta' / 'session-checklists.md'}: missing on-demand guidance"
            )
        if SESSION_CHECKLISTS_MCP_PHRASE not in session_checklists:
            result.error(
                f"{root / 'meta' / 'session-checklists.md'}: missing MCP preference guidance"
            )

    first_run = read_text(root / "meta" / "first-run.md", result)
    if first_run is not None and FIRST_RUN_MCP_PHRASE not in first_run:
        result.error(
            f"{root / 'meta' / 'first-run.md'}: missing MCP preference guidance"
        )

    session_start = root / SESSION_START_SKILL_PATH
    if session_start.exists():
        text = read_text(session_start, result)
        if text is not None:
            for phrase in SESSION_START_REQUIRED_PHRASES:
                if phrase not in text:
                    result.error(f"{session_start}: missing startup-skill phrase {phrase!r}")
            for pattern in SESSION_START_FORBIDDEN_PATTERNS:
                if re.search(pattern, text, re.MULTILINE):
                    result.error(
                        f"{session_start}: contains forbidden startup-skill pattern {pattern!r}"
                    )

    session_wrapup = root / SESSION_WRAPUP_SKILL_PATH
    if session_wrapup.exists():
        text = read_text(session_wrapup, result)
        if text is not None:
            for phrase in SESSION_WRAPUP_REQUIRED_PHRASES:
                if phrase not in text:
                    result.error(
                        f"{session_wrapup}: missing wrapup-skill phrase {phrase!r}"
                    )
            for pattern in SESSION_WRAPUP_FORBIDDEN_PATTERNS:
                if re.search(pattern, text, re.MULTILINE):
                    result.error(
                        f"{session_wrapup}: contains forbidden wrapup-skill pattern {pattern!r}"
                    )

    skills_summary = read_text(root / SKILLS_SUMMARY_PATH, result)
    if skills_summary is not None and SKILLS_SUMMARY_MCP_PHRASE not in skills_summary:
        result.error(
            f"{root / SKILLS_SUMMARY_PATH}: missing MCP preference guidance"
        )

    onboarding_skill = read_text(root / ONBOARDING_SKILL_PATH, result)
    if (
        onboarding_skill is not None
        and ONBOARDING_SKILL_MCP_PHRASE not in onboarding_skill
    ):
        result.error(
            f"{root / ONBOARDING_SKILL_PATH}: missing MCP preference guidance"
        )

    session_sync = read_text(root / SESSION_SYNC_SKILL_PATH, result)
    if session_sync is not None and SESSION_SYNC_SKILL_MCP_PHRASE not in session_sync:
        result.error(
            f"{root / SESSION_SYNC_SKILL_PATH}: missing MCP preference guidance"
        )


def validate_quarantine(root: Path, result: ValidationResult) -> None:
    unverified = root / "knowledge" / "_unverified"
    if not unverified.exists():
        return

    for path in sorted(unverified.rglob("*.md")):
        if should_ignore(path.relative_to(root)):
            continue
        if path.name == "SUMMARY.md":
            continue
        text = read_text(path, result)
        if text is None:
            continue

        frontmatter = parse_frontmatter(path, text, result)
        if frontmatter is None:
            continue

        trust = frontmatter.get("trust")
        if trust and trust != "low":
            result.error(f"{path}: quarantine file must have trust: low, got {trust!r}")

        source = frontmatter.get("source")
        if source and source != "external-research":
            result.warn(
                f"{path}: quarantine file expected source: external-research, got {source!r}"
            )

        if "last_verified" in frontmatter:
            result.error(
                f"{path}: quarantine file must omit last_verified until explicitly reviewed and promoted"
            )


def validate_repo(root: Path) -> ValidationResult:
    result = ValidationResult()

    validate_agent_bootstrap_manifest(root, result)
    validate_quick_reference(root, result)
    validate_runtime_guidance(root, result)
    validate_setup_entrypoints(root, result)
    validate_adapter_routing(root, result)
    validate_prompt_copy(root, result)
    validate_setup_guidance(root, result)
    validate_onboarding_export_template(root, result)
    validate_contract_consistency(root, result)
    validate_quarantine(root, result)

    for path in iter_content_files(root):
        validate_frontmatter(path, root, result)

    for path in iter_access_files(root):
        validate_access_file(path, result)

    return result


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv
    root = repo_root_from_argv(argv)
    result = validate_repo(root)

    for warning in result.warnings:
        print(f"WARNING: {warning}")
    for error in result.errors:
        print(f"ERROR: {error}")

    if result.errors:
        print(
            f"Validation failed with {len(result.errors)} error(s) and {len(result.warnings)} warning(s)."
        )
        return 1

    print(f"Validation passed with {len(result.warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
