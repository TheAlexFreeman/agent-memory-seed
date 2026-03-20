"""
Tier 0 — Enhanced read tools.

These extend the existing read-only tool set with:
  - memory_read_file   : returns version_token + parsed frontmatter
  - memory_list_folder : unchanged from existing (re-implemented here)
  - memory_search      : unchanged from existing (re-implemented here)
  - memory_git_log     : recent commit history
    - memory_check_knowledge_freshness : host-repo freshness for knowledge files
  - memory_diff        : working tree status
  - memory_audit_trust : trust decay audit
    - memory_check_aggregation_triggers : ACCESS.jsonl trigger status

All tools are registered onto the FastMCP instance passed in via register().
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from ..path_policy import KNOWN_COMMIT_PREFIXES  # noqa: F401 — re-exported for callers

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP


def _tool_annotations(**kwargs: object) -> Any:
    """Return MCP tool annotations with a relaxed runtime-only type surface."""
    return cast(Any, kwargs)


# Trust decay thresholds (days) — defaults; runtime reads from quick-reference.md
_DEFAULT_LOW_THRESHOLD = 120
_DEFAULT_MEDIUM_THRESHOLD = 180
_IGNORED_NAMES = frozenset(
    {
        ".git",
        ".claude",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
    }
)
_HUMANS_DIRNAME = "HUMANS"
_DEFAULT_AGGREGATION_TRIGGER = 15
_NEAR_TRIGGER_WINDOW = 3
_PERIODIC_REVIEW_DAYS = 30
_STAGE_ORDER = ("Exploration", "Calibration", "Consolidation")


def _parse_trust_thresholds(repo_root: Path) -> tuple[int, int]:
    """Try to read low/medium trust thresholds from meta/quick-reference.md."""
    qr_path = repo_root / "meta" / "quick-reference.md"
    if not qr_path.exists():
        return _DEFAULT_LOW_THRESHOLD, _DEFAULT_MEDIUM_THRESHOLD
    text = qr_path.read_text(encoding="utf-8")
    low = _DEFAULT_LOW_THRESHOLD
    medium = _DEFAULT_MEDIUM_THRESHOLD
    # Look for patterns like "low: 120 days" or "120-day" near "low trust"
    low_m = re.search(r"low.*?(\d+)[- ]day", text, re.IGNORECASE)
    medium_m = re.search(r"medium.*?(\d+)[- ]day", text, re.IGNORECASE)
    if low_m:
        low = int(low_m.group(1))
    if medium_m:
        medium = int(medium_m.group(1))
    return low, medium


def _parse_aggregation_trigger(repo_root: Path) -> int:
    """Read the active ACCESS aggregation trigger from meta/quick-reference.md."""
    qr_path = repo_root / "meta" / "quick-reference.md"
    if not qr_path.exists():
        return _DEFAULT_AGGREGATION_TRIGGER

    text = qr_path.read_text(encoding="utf-8")
    match = re.search(
        r"aggregation trigger\s*\|\s*(\d+)\s+entries",
        text,
        re.IGNORECASE,
    )
    if match is not None:
        return int(match.group(1))

    fallback = re.search(r"aggregate when .*?reach\s*\*\*(\d+)\*\*", text, re.IGNORECASE)
    if fallback is not None:
        return int(fallback.group(1))

    return _DEFAULT_AGGREGATION_TRIGGER


def _effective_date(fm: dict) -> date | None:
    """Return last_verified if present, else created, else None."""
    for key in ("last_verified", "created"):
        val = fm.get(key)
        if val:
            try:
                if isinstance(val, date):
                    return val
                return datetime.strptime(str(val), "%Y-%m-%d").date()
            except ValueError:
                pass
    return None


def _iter_live_access_files(root: Path) -> list[Path]:
    """Return tracked live ACCESS.jsonl files, excluding archives and dot-dirs."""
    access_files: list[Path] = []
    for access_file in root.rglob("ACCESS.jsonl"):
        try:
            rel = access_file.relative_to(root)
        except ValueError:
            continue
        if rel.parts and rel.parts[0].startswith("."):
            continue
        access_files.append(access_file)
    return sorted(access_files)


def _parse_access_entry(raw_line: str) -> dict[str, Any] | None:
    """Parse a JSONL ACCESS entry, returning None for blank or invalid lines."""
    raw_line = raw_line.strip()
    if not raw_line:
        return None
    try:
        parsed = json.loads(raw_line)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    return cast(dict[str, Any], parsed)


def _parse_iso_date(raw_date: object) -> date | None:
    """Parse YYYY-MM-DD strings used in ACCESS.jsonl dates."""
    if raw_date is None:
        return None
    try:
        return datetime.strptime(str(raw_date), "%Y-%m-%d").date()
    except ValueError:
        return None


def _load_access_entries(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return parsed live ACCESS entries and per-file counts for reporting."""
    entries: list[dict[str, Any]] = []
    counts: list[dict[str, Any]] = []

    for access_file in _iter_live_access_files(root):
        try:
            text = access_file.read_text(encoding="utf-8")
        except OSError:
            continue

        live_count = 0
        invalid_count = 0
        for raw_line in text.splitlines():
            if not raw_line.strip():
                continue
            entry = _parse_access_entry(raw_line)
            if entry is None:
                invalid_count += 1
                continue
            entry["_access_file"] = access_file.relative_to(root).as_posix()
            entries.append(entry)
            live_count += 1

        counts.append(
            {
                "access_file": access_file.relative_to(root).as_posix(),
                "folder": access_file.parent.relative_to(root).as_posix(),
                "entries": live_count,
                "invalid_lines": invalid_count,
            }
        )

    return entries, counts


def _filter_access_entries(
    entries: list[dict[str, Any]],
    *,
    folder: str = "",
    file_prefix: str = "",
    start_date: str = "",
    end_date: str = "",
    min_helpfulness: float | None = None,
    max_helpfulness: float | None = None,
) -> list[dict[str, Any]]:
    """Filter ACCESS entries by folder, file prefix, date range, and helpfulness."""
    start = _parse_iso_date(start_date) if start_date else None
    end = _parse_iso_date(end_date) if end_date else None

    filtered: list[dict[str, Any]] = []
    for entry in entries:
        access_file = str(entry.get("_access_file", ""))
        file_path = str(entry.get("file", ""))

        if folder:
            normalized_folder = folder.rstrip("/")
            if not access_file.startswith(f"{normalized_folder}/") and access_file != (
                f"{normalized_folder}/ACCESS.jsonl"
            ):
                continue
        if file_prefix and not file_path.startswith(file_prefix):
            continue

        entry_date = _parse_iso_date(entry.get("date"))
        if start is not None and (entry_date is None or entry_date < start):
            continue
        if end is not None and (entry_date is None or entry_date > end):
            continue

        raw_helpfulness = entry.get("helpfulness")
        if isinstance(raw_helpfulness, (int, float, str)):
            try:
                helpfulness = float(raw_helpfulness)
            except ValueError:
                helpfulness = None  # type: ignore[assignment]
        else:
            helpfulness = None  # type: ignore[assignment]

        if min_helpfulness is not None and (helpfulness is None or helpfulness < min_helpfulness):
            continue
        if max_helpfulness is not None and (helpfulness is None or helpfulness > max_helpfulness):
            continue

        filtered.append(entry)

    return filtered


def _summarize_access_by_file(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Summarize ACCESS entries per file for aggregation reports."""
    per_file: dict[str, dict[str, Any]] = {}

    for entry in entries:
        file_path = str(entry.get("file", ""))
        if not file_path:
            continue
        bucket = per_file.setdefault(
            file_path,
            {
                "file": file_path,
                "folder": file_path.split("/", 1)[0],
                "entry_count": 0,
                "helpfulness_values": [],
                "session_ids": set(),
                "last_access_date": None,
                "source_access_logs": set(),
            },
        )
        bucket["entry_count"] += 1

        raw_helpfulness = entry.get("helpfulness")
        if isinstance(raw_helpfulness, (int, float, str)):
            try:
                bucket["helpfulness_values"].append(float(raw_helpfulness))
            except ValueError:
                pass

        session_id = entry.get("session_id")
        if session_id:
            bucket["session_ids"].add(str(session_id))

        access_file = entry.get("_access_file")
        if access_file:
            bucket["source_access_logs"].add(str(access_file))

        entry_date = _parse_iso_date(entry.get("date"))
        if entry_date is not None:
            last_access = bucket["last_access_date"]
            if last_access is None or entry_date > last_access:
                bucket["last_access_date"] = entry_date

    summaries: list[dict[str, Any]] = []
    for bucket in per_file.values():
        helpfulness_values = cast(list[float], bucket.pop("helpfulness_values"))
        session_ids = sorted(cast(set[str], bucket.pop("session_ids")))
        source_access_logs = sorted(cast(set[str], bucket.pop("source_access_logs")))
        last_access_date = cast(date | None, bucket["last_access_date"])
        mean_helpfulness = (
            round(sum(helpfulness_values) / len(helpfulness_values), 3)
            if helpfulness_values
            else None
        )
        summaries.append(
            {
                **bucket,
                "mean_helpfulness": mean_helpfulness,
                "session_count": len(session_ids),
                "session_ids": session_ids,
                "last_access_date": str(last_access_date) if last_access_date is not None else None,
                "source_access_logs": source_access_logs,
            }
        )

    summaries.sort(key=lambda item: (-int(item["entry_count"]), str(item["file"])))
    return summaries


def _detect_co_retrieval_clusters(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Detect same-session pairwise co-retrieval clusters."""
    session_files: dict[str, set[str]] = {}
    for entry in entries:
        session_id = entry.get("session_id")
        file_path = entry.get("file")
        if not session_id or not file_path:
            continue
        session_files.setdefault(str(session_id), set()).add(str(file_path))

    pair_counts: dict[tuple[str, str], set[str]] = {}
    for session_id, files in session_files.items():
        ordered_files = sorted(files)
        for idx, left in enumerate(ordered_files):
            for right in ordered_files[idx + 1 :]:
                pair_counts.setdefault((left, right), set()).add(session_id)

    clusters: list[dict[str, Any]] = []
    for (left, right), sessions in pair_counts.items():
        if len(sessions) < 3:
            continue
        folders = sorted({left.split("/", 1)[0], right.split("/", 1)[0]})
        clusters.append(
            {
                "files": [left, right],
                "folders": folders,
                "co_retrieval_count": len(sessions),
                "session_ids": sorted(sessions),
            }
        )

    clusters.sort(key=lambda item: (-int(item["co_retrieval_count"]), item["files"]))
    return clusters


def _parse_last_periodic_review(repo_root: Path) -> date | None:
    """Read the last periodic review date from meta/quick-reference.md."""
    qr_path = repo_root / "meta" / "quick-reference.md"
    if not qr_path.exists():
        return None

    text = qr_path.read_text(encoding="utf-8")
    match = re.search(r"\*\*Date:\*\*\s*(\d{4}-\d{2}-\d{2})", text)
    if match is None:
        return None
    return _parse_iso_date(match.group(1))


def _parse_current_stage(repo_root: Path) -> str:
    """Read the active maturity stage from meta/quick-reference.md."""
    qr_path = repo_root / "meta" / "quick-reference.md"
    if not qr_path.exists():
        return "Exploration"

    text = qr_path.read_text(encoding="utf-8")
    match = re.search(r"## Current active stage:\s*([^\n]+)", text)
    if match is None:
        return "Exploration"

    stage = match.group(1).strip()
    if stage not in _STAGE_ORDER:
        return "Exploration"
    return stage


def _load_content_files(root: Path) -> set[str]:
    """Return repo-relative content files covered by maturity and review rules."""
    content_files: set[str] = set()
    for dirname in ("knowledge", "plans", "identity", "skills"):
        dir_path = root / dirname
        if not dir_path.is_dir():
            continue
        for md in dir_path.rglob("*.md"):
            try:
                content_files.add(md.relative_to(root).as_posix())
            except ValueError:
                continue
    return content_files


def _compute_maturity_signals(
    root: Path,
    repo: Any,
    all_entries: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Compute the maturity signals used during periodic review."""
    import statistics

    from ..frontmatter_utils import read_with_frontmatter

    if all_entries is None:
        all_entries, _ = _load_access_entries(root)

    session_ids: set[str] = set()
    write_session_ids: set[str] = set()
    for entry in all_entries:
        sid = entry.get("session_id")
        if sid:
            sid_str = str(sid)
            session_ids.add(sid_str)
            mode_value = entry.get("mode")
            if isinstance(mode_value, str) and mode_value in {"write", "update", "create"}:
                write_session_ids.add(sid_str)
    total_sessions = len(session_ids)
    write_sessions = len(write_session_ids)

    access_density = len(all_entries)

    content_files = _load_content_files(root)
    total_content_files = len(content_files)

    accessed_files: set[str] = set()
    for entry in all_entries:
        file_path = entry.get("file")
        if file_path and file_path in content_files:
            accessed_files.add(str(file_path))
    files_accessed = len(accessed_files)
    file_coverage_pct = (
        round(100.0 * files_accessed / total_content_files, 1) if total_content_files else 0.0
    )

    high_trust_count = 0
    for rel_str in content_files:
        fp = root / rel_str
        try:
            fm, _ = read_with_frontmatter(fp)
        except Exception:
            continue
        if fm and fm.get("trust") == "high":
            high_trust_count += 1
    confirmation_ratio = (
        round(high_trust_count / total_content_files, 3) if total_content_files else 0.0
    )

    identity_stability: int | None = None
    try:
        proc = repo._run(
            ["git", "log", "-1", "--format=%ad", "--date=short", "--", "identity/profile.md"],
            check=False,
        )
        last_change_str = proc.stdout.strip()
        if last_change_str:
            last_change = datetime.strptime(last_change_str, "%Y-%m-%d").date()
            session_dates: dict[str, date] = {}
            for entry in all_entries:
                sid = entry.get("session_id")
                date_str = entry.get("date")
                if not sid or not date_str:
                    continue
                try:
                    entry_date = datetime.strptime(str(date_str), "%Y-%m-%d").date()
                except ValueError:
                    continue
                sid_str = str(sid)
                if sid_str not in session_dates or entry_date < session_dates[sid_str]:
                    session_dates[sid_str] = entry_date
            identity_stability = sum(
                1 for entry_date in session_dates.values() if entry_date > last_change
            )
    except Exception:
        identity_stability = None

    helpfulness_values: list[float] = []
    for entry in all_entries:
        helpfulness = entry.get("helpfulness")
        if helpfulness is None:
            continue
        try:
            helpfulness_values.append(float(helpfulness))
        except (TypeError, ValueError):
            continue
    mean_helpfulness = round(statistics.mean(helpfulness_values), 3) if helpfulness_values else 0.0

    return {
        "total_sessions": total_sessions,
        "access_density": access_density,
        "file_coverage_pct": file_coverage_pct,
        "files_accessed": files_accessed,
        "total_content_files": total_content_files,
        "confirmation_ratio": confirmation_ratio,
        "high_trust_files": high_trust_count,
        "identity_stability": identity_stability,
        "write_sessions": write_sessions,
        "mean_helpfulness": mean_helpfulness,
        "helpfulness_sample_size": len(helpfulness_values),
        "computed_at": str(date.today()),
    }


def _classify_signal_stage(metric: str, value: object) -> str | None:
    """Map a maturity signal value to its typical stage bucket."""
    if value is None:
        return None
    if not isinstance(value, (int, float, str)):
        return None
    try:
        numeric = float(value)
    except ValueError:
        return None
    if metric == "total_sessions":
        if numeric < 20:
            return "Exploration"
        if numeric <= 80:
            return "Calibration"
        return "Consolidation"
    if metric == "access_density":
        if numeric < 50:
            return "Exploration"
        if numeric <= 200:
            return "Calibration"
        return "Consolidation"
    if metric == "file_coverage_pct":
        if numeric < 30:
            return "Exploration"
        if numeric <= 60:
            return "Calibration"
        return "Consolidation"
    if metric == "confirmation_ratio":
        if numeric < 0.3:
            return "Exploration"
        if numeric <= 0.6:
            return "Calibration"
        return "Consolidation"
    if metric == "identity_stability":
        if numeric < 5:
            return "Exploration"
        if numeric <= 20:
            return "Calibration"
        return "Consolidation"
    if metric == "mean_helpfulness":
        if numeric < 0.5:
            return "Exploration"
        if numeric <= 0.75:
            return "Calibration"
        return "Consolidation"
    return None


def _assess_maturity_stage(signals: dict[str, Any], current_stage: str) -> dict[str, Any]:
    """Assess the recommended maturity stage from the six periodic-review signals."""
    metrics = (
        "total_sessions",
        "access_density",
        "file_coverage_pct",
        "confirmation_ratio",
        "identity_stability",
        "mean_helpfulness",
    )
    votes = {stage: 0 for stage in _STAGE_ORDER}
    signal_votes: dict[str, str] = {}
    for metric in metrics:
        stage = _classify_signal_stage(metric, signals.get(metric))
        if stage is None:
            continue
        votes[stage] += 1
        signal_votes[metric] = stage

    majority_stage: str | None = None
    for stage in reversed(_STAGE_ORDER):
        if votes[stage] >= 4:
            majority_stage = stage
            break

    recommended_stage = current_stage
    transition_recommended = False
    regression_flag = False
    rationale = "Retain current stage; no later-stage majority reached."

    current_index = _STAGE_ORDER.index(current_stage)
    if majority_stage is not None:
        majority_index = _STAGE_ORDER.index(majority_stage)
        if majority_index > current_index:
            recommended_stage = majority_stage
            transition_recommended = True
            rationale = f"Advance to {majority_stage}; {votes[majority_stage]} of 6 signals favor the later stage."
        elif majority_index < current_index:
            regression_flag = True
            rationale = f"{votes[majority_stage]} of 6 signals favor an earlier stage; flag for reassessment rather than auto-regressing."
        else:
            rationale = f"Retain {current_stage}; current stage still has majority support."

    return {
        "current_stage": current_stage,
        "recommended_stage": recommended_stage,
        "transition_recommended": transition_recommended,
        "regression_flag": regression_flag,
        "vote_counts": votes,
        "signal_votes": signal_votes,
        "rationale": rationale,
    }


def _parse_review_queue_entries(root: Path) -> list[dict[str, str]]:
    """Parse review-queue markdown entries into structured metadata."""
    queue_path = root / "meta" / "review-queue.md"
    if not queue_path.exists():
        return []

    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    in_code_block = False
    for raw_line in queue_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        match = re.match(r"### \[(\d{4}-\d{2}-\d{2})\] (.+)", line)
        if match is not None:
            if current is not None:
                entries.append(current)
            current = {
                "date": match.group(1),
                "title": match.group(2),
            }
            continue
        if current is None:
            continue
        field_match = re.match(r"\*\*(.+?):\*\*\s*(.+)", line)
        if field_match is not None:
            key = field_match.group(1).strip().lower().replace(" ", "_")
            current[key] = field_match.group(2).strip()
    if current is not None:
        entries.append(current)
    return entries


def _find_conflict_tags(root: Path) -> list[str]:
    """Return files in identity/ or knowledge/ that still contain [CONFLICT]."""
    matches: list[str] = []
    for dirname in ("identity", "knowledge"):
        dir_path = root / dirname
        if not dir_path.is_dir():
            continue
        for md_file in dir_path.rglob("*.md"):
            try:
                text = md_file.read_text(encoding="utf-8")
            except OSError:
                continue
            if "[CONFLICT]" in text:
                matches.append(md_file.relative_to(root).as_posix())
    return sorted(matches)


def _scan_unverified_content(root: Path, low_threshold: int) -> dict[str, Any]:
    """Summarize low-trust files in knowledge/_unverified/ for periodic review."""
    from ..frontmatter_utils import read_with_frontmatter

    folder = root / "knowledge" / "_unverified"
    files: list[dict[str, Any]] = []
    overdue: list[dict[str, Any]] = []
    if not folder.is_dir():
        return {"files": files, "overdue": overdue}

    today = date.today()
    for md_file in folder.rglob("*.md"):
        if md_file.name == "SUMMARY.md":
            continue
        try:
            fm_dict, _ = read_with_frontmatter(md_file)
        except Exception:
            continue
        eff_date = _effective_date(fm_dict)
        age_days = (today - eff_date).days if eff_date is not None else None
        item = {
            "path": md_file.relative_to(root).as_posix(),
            "trust": fm_dict.get("trust") if fm_dict else None,
            "source": fm_dict.get("source") if fm_dict else None,
            "effective_date": str(eff_date) if eff_date is not None else None,
            "age_days": age_days,
        }
        files.append(item)
        if item["trust"] == "low" and age_days is not None and age_days > low_threshold:
            overdue.append(item)

    files.sort(key=lambda item: (-(item["age_days"] or -1), str(item["path"])))
    overdue.sort(key=lambda item: (-(item["age_days"] or -1), str(item["path"])))
    return {"files": files, "overdue": overdue}


def _summarize_access_by_folder(file_summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate file-level ACCESS summaries to top-level folder summaries."""
    folder_totals: dict[str, dict[str, Any]] = {}
    for item in file_summaries:
        folder = str(item.get("folder", ""))
        if not folder:
            continue
        bucket = folder_totals.setdefault(
            folder,
            {
                "folder": folder,
                "entry_count": 0,
                "files": 0,
                "high_value_files": 0,
                "low_value_files": 0,
            },
        )
        bucket["entry_count"] += int(item.get("entry_count", 0))
        bucket["files"] += 1
        mean_helpfulness = item.get("mean_helpfulness")
        if mean_helpfulness is not None and float(mean_helpfulness) >= 0.7:
            bucket["high_value_files"] += 1
        if mean_helpfulness is not None and float(mean_helpfulness) <= 0.3:
            bucket["low_value_files"] += 1

    summaries = list(folder_totals.values())
    summaries.sort(key=lambda item: (-int(item["entry_count"]), str(item["folder"])))
    return summaries


def _detect_access_anomalies(
    root: Path,
    entries: list[dict[str, Any]],
    staleness_days: int,
) -> list[dict[str, Any]]:
    """Detect read-only anomaly candidates for periodic review."""
    from ..frontmatter_utils import read_with_frontmatter

    by_file: dict[str, list[dict[str, Any]]] = {}
    for entry in entries:
        file_path = str(entry.get("file", ""))
        if not file_path:
            continue
        by_file.setdefault(file_path, []).append(entry)

    anomalies: list[dict[str, Any]] = []
    for file_path, file_entries in by_file.items():
        try:
            fm_dict, _ = read_with_frontmatter(root / file_path)
        except Exception:
            fm_dict = {}

        if (
            len(file_entries) >= 5
            and not fm_dict.get("last_verified")
            and fm_dict.get("source") != "user-stated"
        ):
            anomalies.append(
                {
                    "type": "never_approved_high_retrieval",
                    "file": file_path,
                    "entry_count": len(file_entries),
                    "recommended_action": "Review provenance",
                }
            )

        dated_entries: list[tuple[date, str | None]] = []
        for entry in file_entries:
            entry_date = _parse_iso_date(entry.get("date"))
            if entry_date is None:
                continue
            session_id = str(entry.get("session_id")) if entry.get("session_id") else None
            dated_entries.append((entry_date, session_id))
        if not dated_entries:
            continue
        dated_entries.sort()
        latest_date = dated_entries[-1][0]
        window_start = latest_date.fromordinal(latest_date.toordinal() - staleness_days)
        recent_session_counts: dict[str, int] = {}
        prior_recent = 0
        for entry_date, session_id in dated_entries:
            if entry_date < window_start:
                continue
            if session_id is None:
                prior_recent += 1
                continue
            recent_session_counts[session_id] = recent_session_counts.get(session_id, 0) + 1
        if prior_recent == 0:
            for session_id, count in recent_session_counts.items():
                if count >= 3:
                    anomalies.append(
                        {
                            "type": "dormant_file_spike",
                            "file": file_path,
                            "session_id": session_id,
                            "entry_count": count,
                            "recommended_action": "Investigate access pattern",
                        }
                    )
                    break

    anomalies.sort(key=lambda item: (str(item["type"]), str(item["file"])))
    return anomalies


def _collect_recent_reflections(root: Path, limit: int = 5) -> list[dict[str, str]]:
    """Collect recent reflection files with a short preview line."""
    reflections: list[dict[str, str]] = []
    for reflection_path in sorted(root.glob("chats/**/reflection.md"), reverse=True):
        try:
            text = reflection_path.read_text(encoding="utf-8")
        except OSError:
            continue
        preview = ""
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            preview = stripped
            break
        reflections.append(
            {
                "path": reflection_path.relative_to(root).as_posix(),
                "preview": preview,
            }
        )
        if len(reflections) >= limit:
            break
    return reflections


def _git_changed_files_since(repo: Any, since_date: date | None) -> list[str]:
    """Return repo-relative files touched since the given review date."""
    if since_date is None:
        return []
    try:
        proc = repo._run(
            ["git", "log", "--since", since_date.isoformat(), "--name-only", "--format="],
            check=False,
        )
    except Exception:
        return []

    files = {line.strip() for line in proc.stdout.splitlines() if line.strip()}
    return sorted(files)


def _build_access_summary_for_file(
    entries: list[dict[str, Any]],
    rel_path: str,
) -> dict[str, Any]:
    """Return file-level ACCESS summary for a single repo-relative path."""
    summaries = _summarize_access_by_file(
        [entry for entry in entries if str(entry.get("file", "")) == rel_path]
    )
    if summaries:
        return summaries[0]
    return {
        "file": rel_path,
        "folder": rel_path.split("/", 1)[0] if "/" in rel_path else rel_path,
        "entry_count": 0,
        "mean_helpfulness": None,
        "session_count": 0,
        "session_ids": [],
        "last_access_date": None,
        "source_access_logs": [],
    }


def _git_file_history(repo: Any, rel_path: str, limit: int = 10) -> list[dict[str, str]]:
    """Return recent commit history for a single file."""
    safe_limit = min(max(limit, 1), 20)
    result = repo._run(
        [
            "git",
            "log",
            f"-{safe_limit}",
            "--follow",
            "--format=%H%x1f%s%x1f%aI%x1f%an%x1f%ae",
            "--",
            rel_path,
        ],
        check=False,
    )
    if result.returncode not in (0, 1):
        return []

    history: list[dict[str, str]] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\x1f")
        if len(parts) != 5:
            continue
        history.append(
            {
                "sha": parts[0].strip(),
                "message": parts[1].strip(),
                "author_date": parts[2].strip(),
                "author_name": parts[3].strip(),
                "author_email": parts[4].strip(),
            }
        )
    return history


def _commit_metadata(repo: Any, sha: str) -> dict[str, str | None]:
    """Return author/date metadata for a specific commit."""
    result = repo._run(
        ["git", "show", "--quiet", "--format=%aI%x1f%an%x1f%ae", sha],
        check=False,
    )
    if result.returncode != 0:
        return {
            "author_date": None,
            "author_name": None,
            "author_email": None,
        }

    parts = result.stdout.strip().split("\x1f")
    if len(parts) != 3:
        return {
            "author_date": None,
            "author_name": None,
            "author_email": None,
        }
    return {
        "author_date": parts[0].strip() or None,
        "author_name": parts[1].strip() or None,
        "author_email": parts[2].strip() or None,
    }


def _recognized_commit_prefix(message: str) -> str | None:
    """Return the bracketed commit prefix when it is in the allowed set."""
    match = re.match(r"^(\[[^\]]+\])", message)
    if match is None:
        return None
    prefix = match.group(1)
    if prefix not in KNOWN_COMMIT_PREFIXES:
        return None
    return prefix


def _requires_provenance_pause(path: str, frontmatter: dict[str, Any]) -> bool:
    """Apply the retrieval provenance pause rule to a file path."""
    top_level = path.split("/", 1)[0]
    if top_level in {"meta", "chats", "HUMANS"}:
        return False
    source = frontmatter.get("source")
    last_verified = frontmatter.get("last_verified")
    return not (source == "user-stated" or bool(last_verified))


def _repo_relative(path: Path, root: Path) -> Path:
    """Return a path relative to the repo root."""
    return path.relative_to(root)


def _is_humans_path(path: Path, root: Path) -> bool:
    """Return True when a path is under HUMANS/."""
    relative = _repo_relative(path, root)
    return bool(relative.parts) and relative.parts[0] == _HUMANS_DIRNAME


def _resolve_host_repo(root: Path) -> Path | None:
    """Return the configured host repo root from agent-bootstrap.toml, if any."""
    bootstrap_path = root / "agent-bootstrap.toml"
    if not bootstrap_path.exists():
        return None

    match = re.search(
        r'^host_repo_root\s*=\s*"(?P<path>[^"]+)"',
        bootstrap_path.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    if match is None:
        return None

    candidate = Path(match.group("path")).expanduser()
    if not candidate.is_absolute():
        candidate = (root / candidate).resolve()
    return candidate.resolve()


def _get_git_repo_for_log(root: Path, repo, *, use_host_repo: bool):
    """Resolve the git repo to inspect for memory_git_log."""
    if not use_host_repo:
        return repo

    from ..errors import ValidationError
    from ..git_repo import GitRepo

    host_root = _resolve_host_repo(root)
    if host_root is None:
        raise ValidationError("host_repo_root is not configured in agent-bootstrap.toml")

    try:
        host_root.relative_to(root)
    except ValueError:
        pass
    else:
        raise ValidationError("host_repo_root must not point inside the memory worktree")

    try:
        return GitRepo(host_root)
    except ValueError as exc:
        raise ValidationError(str(exc)) from exc


def _get_host_git_repo(root: Path, repo):
    """Return the configured host repo, if present."""
    if _resolve_host_repo(root) is None:
        return None
    return _get_git_repo_for_log(root, repo, use_host_repo=True)


def _split_csv_or_lines(raw: str) -> list[str]:
    items: list[str] = []
    for chunk in re.split(r"[,\n]", raw):
        value = chunk.strip()
        if value:
            items.append(value)
    return list(dict.fromkeys(items))


def _coerce_path_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return _split_csv_or_lines(value)
    if isinstance(value, (list, tuple)):
        items: list[str] = []
        for entry in value:
            text = str(entry).strip()
            if text:
                items.append(text)
        return list(dict.fromkeys(items))
    text = str(value).strip()
    return [text] if text else []


def _resolve_requested_knowledge_paths(root: Path, raw_paths: str) -> list[tuple[str, Path]]:
    from ..errors import NotFoundError, ValidationError

    resolved: list[tuple[str, Path]] = []
    for requested in _split_csv_or_lines(raw_paths):
        rel_path = Path(requested)
        if rel_path.is_absolute():
            raise ValidationError(f"Knowledge path must be repo-relative: {requested}")

        abs_path = (root / rel_path).resolve()
        try:
            abs_path.relative_to(root)
        except ValueError as exc:
            raise ValidationError(f"Knowledge path escapes repository root: {requested}") from exc

        rel = abs_path.relative_to(root).as_posix()
        if not rel.startswith("knowledge/"):
            raise ValidationError(f"Knowledge path must live under knowledge/: {requested}")
        if not abs_path.exists() or not abs_path.is_file():
            raise NotFoundError(f"File not found: {requested}")
        resolved.append((rel, abs_path))

    if not resolved:
        raise ValidationError("Provide at least one knowledge path")
    return list(dict.fromkeys(resolved))


def _resolve_host_source_path(host_repo, candidate: str) -> str | None:
    from ..errors import MemoryPermissionError, ValidationError

    raw_path = Path(candidate)
    if raw_path.is_absolute():
        abs_path = raw_path.resolve()
        try:
            abs_path.relative_to(host_repo.root)
        except ValueError as exc:
            raise ValidationError(f"Host source path escapes repository root: {candidate}") from exc
    else:
        try:
            abs_path = host_repo.abs_path(candidate)
        except MemoryPermissionError as exc:
            raise ValidationError(str(exc)) from exc

    if not abs_path.exists() or not abs_path.is_file():
        return None
    return abs_path.relative_to(host_repo.root).as_posix()


def _infer_host_source_files(rel_path: str, host_repo) -> list[str]:
    parts = Path(rel_path).parts
    if len(parts) < 3 or parts[0] != "knowledge" or parts[1] != "codebase":
        return []

    candidate = Path(*parts[2:])
    candidates: list[Path] = [candidate]
    if candidate.suffix == ".md":
        candidates.append(candidate.with_suffix(""))

    inferred: list[str] = []
    for item in candidates:
        if not item.parts:
            continue
        resolved = _resolve_host_source_path(host_repo, item.as_posix())
        if resolved is not None:
            inferred.append(resolved)
    return list(dict.fromkeys(inferred))


def _suggest_freshness_action(
    *,
    status: str,
    trust: str | None,
    host_changes_since: int | None,
    verified_against_commit: str | None,
    current_head: str | None,
) -> str:
    if status == "unknown":
        return "none"
    if status == "fresh":
        if trust == "low" and verified_against_commit and current_head == verified_against_commit:
            return "promote"
        return "none"
    if trust == "high" and (host_changes_since or 0) >= 20:
        return "downgrade_trust"
    return "reverify"


def _build_knowledge_freshness_report(root: Path, repo, rel_path: str, abs_path: Path) -> dict[str, object]:
    from ..frontmatter_utils import read_with_frontmatter

    fm_dict, _ = read_with_frontmatter(abs_path)
    trust_value = fm_dict.get("trust")
    trust = str(trust_value) if trust_value else None
    verified_value = fm_dict.get("verified_against_commit")
    verified_against_commit = str(verified_value) if verified_value else None
    last_verified_date = _effective_date(fm_dict)
    host_repo = _get_host_git_repo(root, repo)
    source_files: list[str] = []
    current_head: str | None = None
    host_changes_since: int | None = None
    status = "unknown"

    if host_repo is not None:
        current_head = host_repo.current_head()
        explicit_sources = _coerce_path_list(fm_dict.get("related"))
        for candidate in explicit_sources:
            resolved = _resolve_host_source_path(host_repo, candidate)
            if resolved is not None:
                source_files.append(resolved)
        if not source_files:
            source_files.extend(_infer_host_source_files(rel_path, host_repo))
        source_files = list(dict.fromkeys(source_files))

        if source_files and last_verified_date is not None:
            host_changes_since = host_repo.commit_count_since(
                f"{last_verified_date} 23:59:59",
                paths=source_files,
            )
            status = "fresh" if host_changes_since == 0 else "stale"
        elif verified_against_commit and current_head:
            status = "fresh" if verified_against_commit == current_head else "stale"

    payload: dict[str, object] = {
        "path": rel_path,
        "trust": trust,
        "last_verified": str(last_verified_date) if last_verified_date is not None else None,
        "verified_against_commit": verified_against_commit,
        "current_head": current_head,
        "source_files": source_files,
        "host_changes_since": host_changes_since,
        "status": status,
    }
    payload["suggested_action"] = _suggest_freshness_action(
        status=status,
        trust=trust,
        host_changes_since=host_changes_since,
        verified_against_commit=verified_against_commit,
        current_head=current_head,
    )
    return payload


def register(mcp: "FastMCP", get_repo, get_root) -> dict[str, object]:
    """Register all Tier 0 read tools and return their callables."""

    # ------------------------------------------------------------------
    # memory_read_file
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_read_file",
        annotations=_tool_annotations(
            title="Read Memory File",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    async def memory_read_file(path: str) -> str:
        """Read a file from the memory repository.

        Returns the file content along with a version_token (git object hash)
        for optimistic locking, and parsed frontmatter if present.

        Args:
            path: Repo-relative path (e.g. 'identity/profile.md',
                  'knowledge/_unverified/django/celery-canvas.md').

        Returns:
            JSON with keys:
              content      (str)       Full file text
              version_token (str)      Git SHA-1 of the file; pass back to write
                                       tools to detect concurrent modifications
              frontmatter  (dict|null) Parsed YAML frontmatter, or null
        """
        from ..errors import NotFoundError
        from ..frontmatter_utils import read_with_frontmatter

        repo = get_repo()
        abs_path = repo.abs_path(path)
        if not abs_path.exists():
            raise NotFoundError(f"File not found: {path}")

        fm_dict, body = read_with_frontmatter(abs_path)
        version_token = repo.hash_object(path)

        result = {
            "content": abs_path.read_text(encoding="utf-8"),
            "version_token": version_token,
            "frontmatter": fm_dict or None,
        }
        return json.dumps(result, indent=2, default=str)

    # ------------------------------------------------------------------
    # memory_list_folder
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_list_folder",
        annotations=_tool_annotations(
            title="List Memory Folder",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    async def memory_list_folder(
        path: str = ".",
        include_hidden: bool = False,
        include_humans: bool = False,
    ) -> str:
        """List the contents of a folder in the memory repository.

        Args:
            path:           Repo-relative folder path (default: repo root '.').
            include_hidden: Include dot-files/folders (default: False).
            include_humans: Include the human-facing HUMANS/ tree when browsing
                            broad scopes like '.' (default: False).

        Returns:
            Markdown-formatted directory listing with file sizes.
        """
        root = get_root()
        folder = (root / path).resolve()
        if not folder.exists():
            return f"Error: Folder not found: {path}"
        if not folder.is_dir():
            return f"Error: Not a directory: {path}"

        explicit_humans_request = _is_humans_path(folder, root)
        lines = [f"# {path}/\n"]
        try:
            all_entries = list(folder.iterdir())
        except PermissionError:
            return f"Error: Permission denied reading {path}"

        def _keep(entry: Path) -> bool:
            if entry.name in _IGNORED_NAMES:
                return False
            if not include_hidden and entry.name.startswith("."):
                return False
            if not explicit_humans_request and not include_humans and _is_humans_path(entry, root):
                return False
            return True

        entries = sorted(
            [entry for entry in all_entries if _keep(entry)],
            key=lambda p: (p.is_file(), p.name),
        )

        for entry in entries:
            rel = str(entry.relative_to(root))
            if entry.is_dir():
                lines.append(f"📁 {entry.name}/")
            else:
                size = entry.stat().st_size
                lines.append(f"📄 {entry.name}  ({size:,} bytes)  `{rel}`")

        if len(lines) == 1:
            lines.append("_(empty)_")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # memory_search
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_search",
        annotations=_tool_annotations(
            title="Search Memory Files",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    async def memory_search(
        query: str,
        path: str = ".",
        glob_pattern: str = "**/*.md",
        case_sensitive: bool = False,
        max_results: int = 30,
        include_humans: bool = False,
    ) -> str:
        """Search for a pattern across files in the memory repository.

        Uses git grep for tracked files (fast — git maintains an index), then
        falls back to a Python glob walk for any untracked files. Results are
        grouped by file with line numbers.

        Args:
            query:          Search string or Python regex (POSIX ERE via git grep).
            path:           Folder to search within (default: '.').
            glob_pattern:   File glob filter (default: '**/*.md').
            case_sensitive: Case-sensitive match (default: False).
            max_results:    Max matching lines to return (default: 30, max 100).
            include_humans: Include the human-facing HUMANS/ tree when searching
                            broad scopes like '.' (default: False).

        Returns:
            Matching lines grouped by file with line numbers, or a not-found message.
        """
        from ..errors import StagingError

        root = get_root()
        search_root = (root / path).resolve()
        if not search_root.exists():
            return f"Error: Path not found: {path}"

        # Validate regex early so we can report a helpful error before spawning git
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            python_pattern = re.compile(query, flags)
        except re.error as e:
            return f"Error: Invalid regex pattern: {e}"

        max_results = min(max_results, 100)
        explicit_humans_search = _is_humans_path(search_root, root)

        # Build the git-grep path prefix (repo-relative) so git restricts the search scope
        try:
            scope_prefix = search_root.relative_to(root).as_posix()
        except ValueError:
            scope_prefix = "."

        # Derive a simple glob extension for git grep from glob_pattern
        # e.g. "**/*.md" → "*.md"; "*.txt" → "*.txt"
        simple_glob = glob_pattern.lstrip("*/")  # strip leading **/ or */
        if not simple_glob:
            simple_glob = "*"

        # Build the path spec for git grep
        if scope_prefix in (".", ""):
            git_pathspec = simple_glob
        else:
            git_pathspec = f"{scope_prefix}/{simple_glob}"

        # Try git grep first (fast path for tracked files)
        repo = get_repo()
        try:
            raw_matches = repo.grep(
                query,
                glob=git_pathspec,
                case_sensitive=case_sensitive,
            )
        except StagingError:
            # git grep unavailable or failed — fall through to Python fallback
            raw_matches = None

        # Build per-file match groups from git grep output
        results: list[str] = []
        total_matches = 0
        seen_files: set[str] = set()

        if raw_matches is not None:
            # Group matches by file
            from itertools import groupby

            for file_rel, file_matches_iter in groupby(raw_matches, key=lambda t: t[0]):
                grouped_matches = list(file_matches_iter)
                file_path = root / file_rel

                # Apply HUMANS/ filter
                if (
                    not explicit_humans_search
                    and not include_humans
                    and _is_humans_path(file_path, root)
                ):
                    continue

                # Apply _IGNORED_NAMES filter
                if any(part in _IGNORED_NAMES for part in file_path.parts):
                    continue

                seen_files.add(file_rel)
                file_output: list[str] = []
                for _, line_no, line_text in grouped_matches:
                    file_output.append(f"  {line_no}: {line_text.rstrip()}")
                    total_matches += 1
                    if total_matches >= max_results:
                        break

                if file_output:
                    results.append(f"\n**{file_rel}**")
                    results.extend(file_output)

                if total_matches >= max_results:
                    results.append(
                        f"\n_(truncated at {max_results} matches — use a narrower query or path)_"
                    )
                    break

        # Python fallback: search untracked files git grep wouldn't see
        if total_matches < max_results:
            for file_path in sorted(search_root.glob(glob_pattern)):
                if any(part in _IGNORED_NAMES for part in file_path.parts):
                    continue
                if not file_path.is_file():
                    continue
                try:
                    file_rel = file_path.relative_to(root).as_posix()
                except ValueError:
                    continue
                if file_rel in seen_files:
                    continue  # already handled by git grep
                if (
                    not explicit_humans_search
                    and not include_humans
                    and _is_humans_path(file_path, root)
                ):
                    continue
                try:
                    text = file_path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue

                file_output = []
                for line_no, line in enumerate(text.splitlines(), 1):
                    if python_pattern.search(line):
                        file_output.append(f"  {line_no}: {line.rstrip()}")
                        total_matches += 1
                        if total_matches >= max_results:
                            break

                if file_output:
                    results.append(f"\n**{file_rel}** _(untracked)_")
                    results.extend(file_output)

                if total_matches >= max_results:
                    results.append(f"\n_(truncated at {max_results} matches)_")
                    break

        if not results:
            return f"No matches found for {query!r} in {path!r}."

        return "\n".join(results)

    # ------------------------------------------------------------------
    # memory_git_log
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_git_log",
        annotations=_tool_annotations(
            title="Git Log for Memory Repo",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    async def memory_git_log(n: int = 10, use_host_repo: bool = False) -> str:
        """Return recent commit history for the memory repository.

        Useful at session start to see what changed since the last session.

        Args:
            n: Number of commits to return (default: 10, max: 50).
            use_host_repo: When true, read from host_repo_root in agent-bootstrap.toml.

        Returns:
            JSON list of commits, each with sha, message, date, files_changed.
        """
        root = get_root()
        repo = _get_git_repo_for_log(root, get_repo(), use_host_repo=use_host_repo)
        n = min(n, 50)
        commits = repo.log(n)
        return json.dumps(commits, indent=2)

    # ------------------------------------------------------------------
    # memory_check_knowledge_freshness
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_check_knowledge_freshness",
        annotations=_tool_annotations(
            title="Check Knowledge Freshness",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    async def memory_check_knowledge_freshness(paths: str) -> str:
        """Check knowledge-file freshness against the configured host repository.

        Args:
            paths: Comma-separated or newline-separated knowledge file paths.

        Returns:
            JSON with one freshness report per requested knowledge file.
        """
        root = get_root()
        repo = get_repo()
        reports = [
            _build_knowledge_freshness_report(root, repo, rel_path, abs_path)
            for rel_path, abs_path in _resolve_requested_knowledge_paths(root, paths)
        ]
        payload = {
            "checked_at": str(date.today()),
            "files_checked": len(reports),
            "reports": reports,
        }
        return json.dumps(payload, indent=2)

    # ------------------------------------------------------------------
    # memory_check_aggregation_triggers
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_check_aggregation_triggers",
        annotations=_tool_annotations(
            title="ACCESS Aggregation Trigger Status",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    async def memory_check_aggregation_triggers() -> str:
        """Report which live ACCESS logs are below, near, or above aggregation trigger.

        Uses the active aggregation threshold from meta/quick-reference.md and
        counts valid non-empty entries in each live ACCESS.jsonl file.

        Returns:
            JSON with trigger metadata, per-log counts, and lists of files that
            are near or above the aggregation threshold.
        """
        root = get_root()
        trigger = _parse_aggregation_trigger(root)
        _, access_counts = _load_access_entries(root)

        report: list[dict[str, Any]] = []
        above_trigger: list[str] = []
        near_trigger: list[str] = []

        for item in access_counts:
            entry_count = int(item["entries"])
            remaining = max(trigger - entry_count, 0)
            if entry_count >= trigger:
                status = "above"
                above_trigger.append(cast(str, item["access_file"]))
            elif remaining <= _NEAR_TRIGGER_WINDOW:
                status = "near"
                near_trigger.append(cast(str, item["access_file"]))
            else:
                status = "below"

            report.append(
                {
                    **item,
                    "trigger": trigger,
                    "remaining_to_trigger": remaining,
                    "status": status,
                }
            )

        payload = {
            "aggregation_trigger": trigger,
            "near_trigger_window": _NEAR_TRIGGER_WINDOW,
            "files_checked": len(report),
            "above_trigger": above_trigger,
            "near_trigger": near_trigger,
            "reports": report,
        }
        return json.dumps(payload, indent=2)

    # ------------------------------------------------------------------
    # memory_aggregate_access
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_aggregate_access",
        annotations=_tool_annotations(
            title="Aggregate ACCESS Logs",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    async def memory_aggregate_access(
        folder: str = "",
        file_prefix: str = "",
        start_date: str = "",
        end_date: str = "",
        min_helpfulness: float | None = None,
        max_helpfulness: float | None = None,
    ) -> str:
        """Aggregate live ACCESS.jsonl entries into a maintenance report.

        The first cut is read-only. It computes file-level access summaries,
        high-value and low-value candidates, same-session co-retrieval clusters,
        and preview targets for follow-up curation work.

        Returns:
            JSON report with filters, file summaries, clusters, and proposed
            follow-up outputs for summary updates, review queue entries, and
            archive targets.
        """
        root = get_root()
        trigger = _parse_aggregation_trigger(root)
        all_entries, access_counts = _load_access_entries(root)
        filtered_entries = _filter_access_entries(
            all_entries,
            folder=folder,
            file_prefix=file_prefix,
            start_date=start_date,
            end_date=end_date,
            min_helpfulness=min_helpfulness,
            max_helpfulness=max_helpfulness,
        )
        file_summaries = _summarize_access_by_file(filtered_entries)
        clusters = _detect_co_retrieval_clusters(filtered_entries)

        high_value_files = [
            item
            for item in file_summaries
            if int(item["entry_count"]) >= 5
            and item["mean_helpfulness"] is not None
            and float(item["mean_helpfulness"]) >= 0.7
        ]
        low_value_files = [
            item
            for item in file_summaries
            if int(item["entry_count"]) >= 3
            and item["mean_helpfulness"] is not None
            and float(item["mean_helpfulness"]) <= 0.3
        ]

        archive_targets: list[str] = []
        if folder:
            normalized_folder = folder.rstrip("/")
            archive_targets = [
                cast(str, item["access_file"])
                for item in access_counts
                if cast(str, item["access_file"]).startswith(f"{normalized_folder}/")
                and int(item["entries"]) >= trigger
            ]
        else:
            archive_targets = [
                cast(str, item["access_file"])
                for item in access_counts
                if int(item["entries"]) >= trigger
            ]

        summary_update_targets = {
            f"{item['folder']}/SUMMARY.md"
            for item in high_value_files + low_value_files
            if isinstance(item.get("folder"), str)
        }
        for cluster in clusters:
            for folder_name in cast(list[str], cluster["folders"]):
                summary_update_targets.add(f"{folder_name}/SUMMARY.md")
        sorted_summary_update_targets = sorted(summary_update_targets)
        review_queue_candidates = [
            {
                "file": item["file"],
                "reason": "Consistently low-value ACCESS pattern",
                "entry_count": item["entry_count"],
                "mean_helpfulness": item["mean_helpfulness"],
            }
            for item in low_value_files
        ]
        task_group_candidates = [
            {
                "files": cluster["files"],
                "folders": cluster["folders"],
                "co_retrieval_count": cluster["co_retrieval_count"],
            }
            for cluster in clusters
            if len(cast(list[str], cluster["folders"])) >= 2
        ]

        payload = {
            "filters": {
                "folder": folder or None,
                "file_prefix": file_prefix or None,
                "start_date": start_date or None,
                "end_date": end_date or None,
                "min_helpfulness": min_helpfulness,
                "max_helpfulness": max_helpfulness,
            },
            "aggregation_trigger": trigger,
            "entries_considered": len(filtered_entries),
            "files_considered": len(file_summaries),
            "high_value_files": high_value_files,
            "low_value_files": low_value_files,
            "co_retrieval_clusters": clusters,
            "file_summaries": file_summaries,
            "proposed_outputs": {
                "summary_update_targets": sorted_summary_update_targets,
                "access_archive_targets": archive_targets,
                "review_queue_candidates": review_queue_candidates,
                "task_group_candidates": task_group_candidates,
            },
        }
        return json.dumps(payload, indent=2)

    # ------------------------------------------------------------------
    # memory_run_periodic_review
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_run_periodic_review",
        annotations=_tool_annotations(
            title="Periodic Review Report",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    async def memory_run_periodic_review() -> str:
        """Run the ordered periodic-review checklist as a read-only report.

        The tool mirrors the checklist in meta/update-guidelines.md and returns
        structured findings plus deferred write targets rather than mutating any
        protected files directly.
        """
        root = get_root()
        repo = get_repo()
        low_threshold, _ = _parse_trust_thresholds(root)
        current_stage = _parse_current_stage(root)
        last_review = _parse_last_periodic_review(root)
        today = date.today()
        days_since_review = (today - last_review).days if last_review is not None else None

        all_entries, access_counts = _load_access_entries(root)
        file_summaries = _summarize_access_by_file(all_entries)
        low_value_files = [
            item
            for item in file_summaries
            if int(item["entry_count"]) >= 3
            and item["mean_helpfulness"] is not None
            and float(item["mean_helpfulness"]) <= 0.3
        ]
        clusters = _detect_co_retrieval_clusters(all_entries)
        folder_summaries = _summarize_access_by_folder(file_summaries)
        review_queue_entries = _parse_review_queue_entries(root)
        security_entries = [
            entry for entry in review_queue_entries if entry.get("type") == "security"
        ]
        pending_security_entries = [
            entry
            for entry in security_entries
            if entry.get("status", "pending") in {"pending", "investigated"}
        ]
        pending_non_security_entries = [
            entry
            for entry in review_queue_entries
            if entry.get("type") != "security" and entry.get("status", "pending") == "pending"
        ]
        false_positive_security = [
            entry for entry in security_entries if entry.get("status") == "false-positive"
        ]

        unverified = _scan_unverified_content(root, low_threshold)
        conflicts = _find_conflict_tags(root)
        signals = _compute_maturity_signals(root, repo, all_entries)
        maturity = _assess_maturity_stage(signals, current_stage)
        anomaly_candidates = _detect_access_anomalies(root, all_entries, low_threshold)
        reflections = _collect_recent_reflections(root)
        recently_touched_files = _git_changed_files_since(repo, last_review)

        if last_review is None:
            review_due_reason = "No recorded periodic review date."
        elif days_since_review is not None and days_since_review > _PERIODIC_REVIEW_DAYS:
            review_due_reason = f"Last periodic review was {days_since_review} days ago, beyond the {_PERIODIC_REVIEW_DAYS}-day cadence."
        else:
            review_due_reason = "Periodic review cadence not yet exceeded."

        folder_candidates = {
            "high_access": [item for item in folder_summaries if int(item["entry_count"]) >= 15],
            "low_access": [item for item in folder_summaries if int(item["entry_count"]) <= 2],
        }
        governance_review_queue_count = len(
            [entry for entry in pending_non_security_entries if entry.get("type") == "governance"]
        )
        governance_evaluation = {
            "threshold_effectiveness": {
                "overdue_low_trust_files": len(cast(list[dict[str, Any]], unverified["overdue"])),
                "low_value_files": len(low_value_files),
            },
            "signal_quality": {
                "security_entries_total": len(security_entries),
                "security_false_positive_count": len(false_positive_security),
                "security_false_positive_ratio": (
                    round(len(false_positive_security) / len(security_entries), 3)
                    if security_entries
                    else None
                ),
                "anomaly_candidates": anomaly_candidates,
            },
            "consistency_targets": [
                "README.md",
                "meta/quick-reference.md",
                "meta/update-guidelines.md",
            ],
            "user_friendliness_notes": [
                "Keep protected changes in deferred output rather than applying them silently.",
                "Preserve metadata-first checks before loading expensive governance files.",
            ],
            "context_efficiency_notes": [
                "Compact returning path remains the default routing surface.",
                "Aggregation and periodic review stay read-first until a user approves protected writes.",
            ],
            "missing_coverage_prompt": governance_review_queue_count == 0,
        }

        summary_update_targets = {
            f"{item['folder']}/SUMMARY.md"
            for item in low_value_files
            if isinstance(item.get("folder"), str)
        }
        for cluster in clusters:
            for folder_name in cast(list[str], cluster["folders"]):
                summary_update_targets.add(f"{folder_name}/SUMMARY.md")

        deferred_write_targets = ["meta/belief-diff-log.md"]
        if (
            pending_non_security_entries
            or pending_security_entries
            or anomaly_candidates
            or unverified["overdue"]
        ):
            deferred_write_targets.append("meta/review-queue.md")
        if (
            days_since_review is None
            or (days_since_review is not None and days_since_review > _PERIODIC_REVIEW_DAYS)
            or maturity["transition_recommended"]
        ):
            deferred_write_targets.append("meta/quick-reference.md")
        deferred_write_targets.extend(sorted(summary_update_targets))

        new_files_since_review = []
        for rel_path in _load_content_files(root):
            try:
                text = (root / rel_path).read_text(encoding="utf-8")
            except OSError:
                continue
            created_match = re.search(r"^created:\s*(\d{4}-\d{2}-\d{2})$", text, re.MULTILINE)
            if created_match is None or last_review is None:
                continue
            created_date = _parse_iso_date(created_match.group(1))
            if created_date is not None and created_date > last_review:
                new_files_since_review.append(rel_path)

        payload = {
            "review_due": {
                "last_periodic_review": str(last_review) if last_review is not None else None,
                "days_since_review": days_since_review,
                "due": last_review is None
                or (days_since_review is not None and days_since_review > _PERIODIC_REVIEW_DAYS),
                "reason": review_due_reason,
            },
            "ordered_checks": {
                "security_flags": {
                    "pending_count": len(pending_security_entries),
                    "pending_entries": pending_security_entries,
                    "generated_candidates": anomaly_candidates,
                },
                "unverified_content": {
                    "total_files": len(cast(list[dict[str, Any]], unverified["files"])),
                    "overdue_count": len(cast(list[dict[str, Any]], unverified["overdue"])),
                    "overdue_files": unverified["overdue"],
                },
                "conflict_resolution": {
                    "count": len(conflicts),
                    "files": conflicts,
                },
                "review_queue": {
                    "pending_non_security_count": len(pending_non_security_entries),
                    "pending_non_security_entries": pending_non_security_entries,
                },
                "unhelpful_memory": {
                    "count": len(low_value_files),
                    "files": low_value_files,
                },
                "maturity_assessment": {
                    **maturity,
                    "signals": signals,
                },
                "governance_evaluation": governance_evaluation,
                "folder_structure": {
                    "folder_summaries": folder_summaries,
                    "candidates": folder_candidates,
                },
                "emergent_categorization": {
                    "cluster_count": len(clusters),
                    "clusters": clusters,
                },
                "session_reflection_themes": {
                    "reflection_count": len(reflections),
                    "recent_reflections": reflections,
                },
            },
            "belief_diff_preview": {
                "new_files_since_review": sorted(new_files_since_review),
                "recently_touched_files": recently_touched_files,
            },
            "aggregation_status": {
                "trigger": _parse_aggregation_trigger(root),
                "logs": access_counts,
            },
            "proposed_outputs": {
                "deferred_write_targets": sorted(set(deferred_write_targets)),
                "summary_update_targets": sorted(summary_update_targets),
                "review_queue_candidates": [
                    {
                        "type": "security",
                        "title": candidate["type"],
                        "file": candidate["file"],
                        "recommended_action": candidate["recommended_action"],
                    }
                    for candidate in anomaly_candidates
                ],
            },
        }
        return json.dumps(payload, indent=2)

    # ------------------------------------------------------------------
    # memory_get_file_provenance
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_get_file_provenance",
        annotations=_tool_annotations(
            title="File Provenance",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    async def memory_get_file_provenance(path: str, history_limit: int = 10) -> str:
        """Return provenance, ACCESS history, and git history for one file."""
        from ..errors import NotFoundError
        from ..frontmatter_utils import read_with_frontmatter

        root = get_root()
        repo = get_repo()
        abs_path = repo.abs_path(path)
        if not abs_path.exists() or not abs_path.is_file():
            raise NotFoundError(f"File not found: {path}")

        frontmatter, _ = read_with_frontmatter(abs_path)
        version_token = repo.hash_object(path)
        access_entries, _ = _load_access_entries(root)
        access_summary = _build_access_summary_for_file(access_entries, path)
        commit_history = _git_file_history(repo, path, limit=history_limit)
        latest_commit = commit_history[0] if commit_history else None
        first_tracked_date = repo.first_tracked_author_date(path)
        effective_date = _effective_date(frontmatter)

        payload = {
            "path": path,
            "version_token": version_token,
            "tracked": first_tracked_date is not None,
            "first_tracked_date": str(first_tracked_date)
            if first_tracked_date is not None
            else None,
            "effective_date": str(effective_date) if effective_date is not None else None,
            "frontmatter": frontmatter or None,
            "requires_provenance_pause": _requires_provenance_pause(path, frontmatter),
            "access_summary": access_summary,
            "latest_commit": latest_commit,
            "commit_history": commit_history,
        }
        return json.dumps(payload, indent=2, default=str)

    # ------------------------------------------------------------------
    # memory_inspect_commit
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_inspect_commit",
        annotations=_tool_annotations(
            title="Inspect Commit",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    async def memory_inspect_commit(sha: str) -> str:
        """Return structured metadata for a commit plus basic scope analysis."""
        repo = get_repo()
        commit = repo.inspect_commit(sha)
        metadata = _commit_metadata(repo, str(commit["sha"]))
        files_changed = [str(path) for path in cast(list[object], commit["files_changed"])]
        top_levels = sorted({path.split("/", 1)[0] for path in files_changed if path})
        message = str(commit["message"])

        payload = {
            **commit,
            **metadata,
            "requested_sha": sha,
            "recognized_prefix": _recognized_commit_prefix(message),
            "file_count": len(files_changed),
            "top_level_paths": top_levels,
            "is_head": str(commit["sha"]) == repo.current_head(),
        }
        return json.dumps(payload, indent=2)

    # ------------------------------------------------------------------
    # memory_diff
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_diff",
        annotations=_tool_annotations(
            title="Working Tree Diff Status",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    async def memory_diff() -> str:
        """Show working tree status — staged, unstaged, and untracked files.

        Call before memory_commit to verify what will be included in the commit.

        Returns:
            JSON with keys staged, unstaged, untracked (each a list of paths).
        """
        repo = get_repo()
        status = repo.diff_status()
        return json.dumps(status, indent=2)

    # ------------------------------------------------------------------
    # memory_audit_trust
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_audit_trust",
        annotations=_tool_annotations(
            title="Trust Decay Audit",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    async def memory_audit_trust(
        include_categories: str = "",
    ) -> str:
        """Audit trust decay across the memory repository.

                Checks all files with trust frontmatter against the decay thresholds
                from meta/quick-reference.md, and treats files without frontmatter as
                implicit medium-trust when a git-backed effective date is available:
          - low-trust files:    overdue at 120 days, flagged at 90 days
          - medium-trust files: overdue at 180 days, flagged at 150 days
                    - frontmatterless tracked files: audited as implicit medium-trust
                    - frontmatterless untracked files: reported as unevaluable

        Does not modify any files — pure read operation.

        Args:
            include_categories: Comma-separated list of top-level folders to scan
                                 (e.g. 'knowledge,plans'). Empty = scan all.

        Returns:
            JSON with overdue/upcoming buckets plus unevaluable files,
            checked_at, and files_checked count.
        """
        from ..frontmatter_utils import read_with_frontmatter

        root = get_root()
        low_threshold, medium_threshold = _parse_trust_thresholds(root)
        low_warn = low_threshold - 30
        medium_warn = medium_threshold - 30

        categories = [c.strip() for c in include_categories.split(",") if c.strip()]
        if not categories:
            categories = ["knowledge", "plans", "identity", "skills"]

        today = date.today()
        overdue_low = []
        overdue_medium = []
        upcoming_low = []
        upcoming_medium = []
        unevaluable = []
        files_checked = 0
        repo = get_repo()
        host_repo = _get_host_git_repo(root, repo)
        untracked_files = set(repo.diff_status()["untracked"])

        for cat in categories:
            cat_path = root / cat
            if not cat_path.is_dir():
                continue
            for md_file in cat_path.rglob("*.md"):
                if not md_file.is_file():
                    continue
                try:
                    fm_dict, _ = read_with_frontmatter(md_file)
                except Exception:
                    continue

                rel = md_file.relative_to(root).as_posix()
                trust = fm_dict.get("trust")
                implicit_medium = False
                if trust in ("low", "medium", "high"):
                    pass
                elif fm_dict:
                    continue
                else:
                    trust = "medium"
                    implicit_medium = True

                files_checked += 1
                eff_date = _effective_date(fm_dict)
                if eff_date is None and implicit_medium:
                    if rel in untracked_files:
                        unevaluable.append(
                            {
                                "path": rel,
                                "trust": trust,
                                "reason": "untracked_without_frontmatter",
                                "implicit_trust": True,
                            }
                        )
                        continue
                    eff_date = repo.first_tracked_author_date(rel)
                if eff_date is None:
                    if implicit_medium:
                        unevaluable.append(
                            {
                                "path": rel,
                                "trust": trust,
                                "reason": "missing_effective_date",
                                "implicit_trust": True,
                            }
                        )
                    continue

                days = (today - eff_date).days

                entry = {
                    "path": rel,
                    "trust": trust,
                    "effective_date": str(eff_date),
                    "days_since_verified": days,
                }
                if implicit_medium:
                    entry["implicit_trust"] = True

                freshness_report = None
                freshness_status = "unknown"
                if host_repo is not None:
                    freshness_report = _build_knowledge_freshness_report(root, repo, rel, md_file)
                    freshness_status = str(freshness_report["status"])
                    for key in (
                        "current_head",
                        "verified_against_commit",
                        "host_changes_since",
                        "source_files",
                    ):
                        if freshness_report.get(key) is not None:
                            entry[key] = freshness_report[key]
                    entry["freshness_status"] = freshness_status

                if trust == "low":
                    threshold = low_threshold
                    warn = low_warn
                    entry["days_until_threshold"] = max(0, threshold - days)
                    if days >= threshold:
                        if freshness_status == "fresh":
                            entry["action_required"] = "review"
                            upcoming_low.append(entry)
                        else:
                            entry["action_required"] = "archive"
                            overdue_low.append(entry)
                    elif days >= warn or freshness_status == "stale":
                        entry["action_required"] = "review"
                        upcoming_low.append(entry)
                elif trust == "medium":
                    threshold = medium_threshold
                    warn = medium_warn
                    entry["days_until_threshold"] = max(0, threshold - days)
                    if days >= threshold:
                        if freshness_status == "fresh":
                            entry["action_required"] = "review"
                            upcoming_medium.append(entry)
                        else:
                            entry["action_required"] = "flag"
                            overdue_medium.append(entry)
                    elif days >= warn or freshness_status == "stale":
                        entry["action_required"] = (
                            "reverify" if freshness_status == "stale" else "review"
                        )
                        upcoming_medium.append(entry)

        result = {
            "overdue_low": overdue_low,
            "overdue_medium": overdue_medium,
            "upcoming_low": upcoming_low,
            "upcoming_medium": upcoming_medium,
            "unevaluable": unevaluable,
            "checked_at": str(today),
            "files_checked": files_checked,
            "thresholds": {
                "low_days": low_threshold,
                "medium_days": medium_threshold,
            },
        }
        return json.dumps(result, indent=2)

    # ------------------------------------------------------------------
    # memory_validate
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_validate",
        annotations=_tool_annotations(
            title="Validate Memory Repository",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    async def memory_validate() -> str:
        """Run the structural validator against the memory repository.

        Checks frontmatter keys, ACCESS.jsonl structure, and governance
        consistency. Returns a validation report.

        Returns:
            Validation report with errors and warnings, or a clean-pass message.
        """
        root = get_root()
        validator_path = root / "HUMANS" / "tooling" / "scripts" / "validate_memory_repo.py"
        if not validator_path.exists():
            return "Validator not found at HUMANS/tooling/scripts/validate_memory_repo.py"
        try:
            result = subprocess.run(
                [sys.executable, str(validator_path), str(root)],
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=30,
                stdin=subprocess.DEVNULL,
            )
            output = result.stdout + result.stderr
            return output.strip() or "Validation complete (no output)."
        except subprocess.TimeoutExpired:
            return "Error: Validator timed out after 30 seconds."
        except Exception as e:
            return f"Error running validator: {e}"

    # ------------------------------------------------------------------
    # memory_get_maturity_signals
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_get_maturity_signals",
        annotations=_tool_annotations(
            title="Maturity Signals",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    async def memory_get_maturity_signals() -> str:
        """Compute all six maturity signals for the periodic review.

        These signals drive the maturity stage assessment in
        meta/system-maturity.md and determine whether to retain the current
        parameter set or transition to the next stage.  All values are derived
        from ACCESS.jsonl files and content-file frontmatter — no network calls
        are made.

        Returns:
            JSON with the following keys:
              total_sessions          (int)   Distinct session_id values across
                                              all ACCESS.jsonl files
              access_density          (int)   Total ACCESS.jsonl entries across
                                              all folders
              file_coverage_pct       (float) % of content files accessed at
                                              least once (0–100)
              files_accessed          (int)   Count of distinct files in
                                              ACCESS.jsonl entries
              total_content_files     (int)   Total .md files in knowledge/,
                                              plans/, identity/, skills/
              confirmation_ratio      (float) trust:high files / total content
                                              files (0.0–1.0)
              high_trust_files        (int)   Count of trust:high content files
              identity_stability      (int|null)
                                              Sessions since last change to
                                              identity/profile.md; null if the
                                              file has no tracked commit history
              write_sessions         (int)   Distinct session_id values with at
                                              least one non-read ACCESS entry
              mean_helpfulness        (float) Mean helpfulness score across all
                                              ACCESS entries that carry the field
              helpfulness_sample_size (int)   Number of entries with a
                                              helpfulness score
              computed_at             (str)   ISO date of computation
        """
        root = get_root()
        repo = get_repo()
        signals = _compute_maturity_signals(root, repo)
        return json.dumps(signals, indent=2)

    return {
        "memory_read_file": memory_read_file,
        "memory_list_folder": memory_list_folder,
        "memory_search": memory_search,
        "memory_git_log": memory_git_log,
        "memory_check_knowledge_freshness": memory_check_knowledge_freshness,
        "memory_check_aggregation_triggers": memory_check_aggregation_triggers,
        "memory_aggregate_access": memory_aggregate_access,
        "memory_run_periodic_review": memory_run_periodic_review,
        "memory_get_file_provenance": memory_get_file_provenance,
        "memory_inspect_commit": memory_inspect_commit,
        "memory_diff": memory_diff,
        "memory_audit_trust": memory_audit_trust,
        "memory_validate": memory_validate,
        "memory_get_maturity_signals": memory_get_maturity_signals,
    }
