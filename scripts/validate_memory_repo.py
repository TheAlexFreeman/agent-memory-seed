#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


CONTENT_DIRS = ("identity", "knowledge", "skills")
ACCESS_DIRS = ("identity", "knowledge", "skills", "chats")
IGNORED_DIR_NAMES = {".git", ".claude", "__pycache__", ".pytest_cache"}

REQUIRED_FRONTMATTER_KEYS = (
    "source",
    "origin_session",
    "created",
    "last_verified",
    "trust",
)
ALLOWED_SOURCE_VALUES = {
    "user-stated",
    "agent-inferred",
    "external-research",
    "skill-discovery",
    "template",
    "unknown",
}
ALLOWED_TRUST_VALUES = {"high", "medium", "low"}

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

RUNTIME_GUIDANCE_FILES = (
    Path("README.md"),
    Path("QUICKSTART.md"),
    Path("meta/quick-reference.md"),
    Path("meta/curation-policy.md"),
    Path("meta/update-guidelines.md"),
    Path("meta/session-checklists.md"),
)

FORBIDDEN_RUNTIME_PATTERNS = (
    r"Check the current maturity stage in `meta/system-maturity\.md`",
    r"see `meta/system-maturity\.md` for the stage-appropriate value",
    r"use those values from `meta/system-maturity\.md`",
    r"Thresholds are stage-specific; see `meta/system-maturity\.md`",
    r"The active thresholds are always determined by the system's current maturity stage as assessed in `meta/system-maturity\.md`",
    r"The session boundary is proxied by the `date` field",
    r"groups entries by date, identifies file sets co-occurring",
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
    return Path(__file__).resolve().parents[1]


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


def parse_frontmatter(path: Path, text: str, result: ValidationResult) -> dict[str, str] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    end_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break
    if end_index is None:
        result.error(f"{path}: frontmatter starts with '---' but has no closing delimiter")
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


def validate_iso_date(value: object, path: Path, field_name: str, result: ValidationResult) -> None:
    if not isinstance(value, str):
        result.error(f"{path}: {field_name} must be a string in YYYY-MM-DD format")
        return
    try:
        date.fromisoformat(value)
    except ValueError:
        result.error(f"{path}: {field_name} must be a valid YYYY-MM-DD date, got {value!r}")


def validate_frontmatter(path: Path, result: ValidationResult) -> None:
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
    validate_iso_date(frontmatter["last_verified"], path, "last_verified", result)

    if not frontmatter["origin_session"]:
        result.error(f"{path}: origin_session must not be empty")


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
            result.error(f"{path}:{line_number}: missing required ACCESS fields: {', '.join(missing)}")
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
            result.error(f"{path}:{line_number}: helpfulness must be between 0.0 and 1.0")

        if "session_id" in payload and not isinstance(payload["session_id"], str):
            result.error(f"{path}:{line_number}: session_id must be a string when present")
        if "category" in payload and not isinstance(payload["category"], str):
            result.error(f"{path}:{line_number}: category must be a string when present")

        unknown_keys = set(payload) - REQUIRED_ACCESS_FIELDS - OPTIONAL_ACCESS_FIELDS
        if unknown_keys:
            result.warn(
                f"{path}:{line_number}: unknown ACCESS fields present: {', '.join(sorted(unknown_keys))}"
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
        "Grouping precedence:",
        "`session_id`",
        "`date`",
        "Exploration defaults apply",
    )
    for phrase in required_phrases:
        if phrase not in text:
            result.error(f"{path}: missing required runtime guidance phrase {phrase!r}")


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
                result.error(f"{path}: contains forbidden runtime guidance pattern {pattern!r}")


def validate_repo(root: Path) -> ValidationResult:
    result = ValidationResult()

    validate_quick_reference(root, result)
    validate_runtime_guidance(root, result)

    for path in iter_content_files(root):
        validate_frontmatter(path, result)

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
        print(f"Validation failed with {len(result.errors)} error(s) and {len(result.warnings)} warning(s).")
        return 1

    print(f"Validation passed with {len(result.warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
