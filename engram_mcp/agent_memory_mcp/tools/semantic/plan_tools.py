"""Plan-oriented semantic tools."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, cast

from ...path_policy import validate_session_id, validate_slug
from ...preview_contract import build_governed_preview, preview_target

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP


def _tool_annotations(**kwargs: object) -> Any:
    return cast(Any, kwargs)


def _plan_path(plan_id: str) -> str:
    return f"plans/{validate_slug(plan_id, field_name='plan_id')}.md"


def _plan_summary_title(fm_dict: dict[str, object], body: str, plan_id: str) -> str:
    """Resolve a human-readable plan title for plans/SUMMARY.md."""
    title = fm_dict.get("title")
    if isinstance(title, str) and title.strip():
        return title.strip()

    heading_match = re.search(r"(?m)^#\s+(.+?)\s*$", body)
    if heading_match is not None:
        return heading_match.group(1).strip()

    return plan_id


def register_tools(mcp: "FastMCP", get_repo, get_root) -> dict[str, object]:
    """Register plan-oriented semantic tools."""

    @mcp.tool(
        name="memory_mark_plan_item_complete",
        annotations=_tool_annotations(
            title="Mark Plan Item Complete",
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    async def memory_mark_plan_item_complete(
        plan_id: str,
        phase_index: int,
        item_index: int,
        version_token: str | None = None,
    ) -> str:
        """Mark a plan checklist item ☐→☑ and keep all invariants in sync.

        Invariants maintained (all atomically committed):
          1. ☐ → ☑ for the target item in the plan file
          2. Phase counter updated: N/M → (N+1)/M; phase → ☑ if all done
          3. next_action frontmatter updated to first remaining unchecked item;
                 status → 'complete' if all phases done
          4. last_verified updated to today
          5. Progress log table gets a new row
          6. plans/SUMMARY.md BEGIN/END block updated

        Args:
                plan_id:       Plan identifier without .md extension
                                           (e.g. 'react-stack-research').
                phase_index:   0-based phase number.
                item_index:    0-based item number within the phase.
                version_token: Optional version token for the plan file.

        Returns:
                MemoryWriteResult JSON with new_state:
                  next_action    (str|null)  Description of next unchecked item
                  phase_progress [done,total]
                  plan_progress  [done,total]
                  status         (str)       'active' or 'complete'
        """
        from ...errors import NotFoundError
        from ...frontmatter_utils import (
            add_progress_log_row,
            build_plan_summary_block,
            mark_plan_item_complete,
            parse_plan_items,
            read_with_frontmatter,
            replace_begin_end_block,
            today_str,
        )
        from ...models import MemoryWriteResult

        repo = get_repo()
        root = get_root()
        warnings: list[str] = []

        plan_path = _plan_path(plan_id)
        abs_plan = repo.abs_path(plan_path)
        if not abs_plan.exists():
            raise NotFoundError(f"Plan not found: {plan_path}")

        repo.check_version_token(plan_path, version_token)

        content = abs_plan.read_text(encoding="utf-8")
        fm_dict, body = read_with_frontmatter(abs_plan)

        new_content, stats = mark_plan_item_complete(content, phase_index, item_index)

        phases = parse_plan_items(content)
        item_text = phases[phase_index]["items"][item_index]["text"]
        fn_match = re.search(r"[\w./_-]+\.(?:md|py|ts|js)\b", item_text)
        item_filename = fn_match.group(0).split("/")[-1] if fn_match else item_text[:40]

        plan_done, plan_total = stats["plan_progress"]

        action_desc = f"Completed {item_filename} ({plan_id} {plan_done}/{plan_total})"
        new_content = add_progress_log_row(new_content, action_desc)

        all_complete = stats["all_complete"]
        fm_updates = {
            "next_action": stats["next_action"],
            "last_verified": today_str(),
        }
        if all_complete:
            fm_updates["status"] = "complete"

        import frontmatter as fmlib  # type: ignore[import-untyped]

        post = fmlib.loads(new_content)
        for key, value in fm_updates.items():
            if value is None:
                post.metadata.pop(key, None)
            else:
                post.metadata[key] = value
        final_content = fmlib.dumps(post)

        abs_plan.write_text(final_content, encoding="utf-8")
        repo.add(plan_path)

        summary_path = "plans/SUMMARY.md"
        abs_summary = root / summary_path
        if abs_summary.exists():
            summary_content = abs_summary.read_text(encoding="utf-8")
            trust = fm_dict.get("trust", "medium")
            status_str = "complete" if all_complete else "active"
            summary_title = _plan_summary_title(fm_dict, body, plan_id)
            new_block = build_plan_summary_block(
                plan_id=plan_id,
                title=summary_title,
                status=status_str,
                trust=trust,
                next_action=stats["next_action"],
                plan_progress=(plan_done, plan_total),
            )
            updated_summary = replace_begin_end_block(summary_content, plan_id, new_block)
            if updated_summary is None:
                warnings.append(
                    f"BEGIN/END anchor for '{plan_id}' not found in plans/SUMMARY.md. "
                    "Summary not updated — add anchors manually."
                )
            else:
                abs_summary.write_text(updated_summary, encoding="utf-8")
                repo.add(summary_path)

        commit_msg = f"[plan] Mark {item_filename} complete ({plan_id} {plan_done}/{plan_total})"
        commit_result = repo.commit(commit_msg)

        new_state = {
            "next_action": stats["next_action"],
            "phase_progress": stats["phase_progress"],
            "plan_progress": stats["plan_progress"],
            "status": "complete" if all_complete else "active",
        }
        result = MemoryWriteResult.from_commit(
            files_changed=[plan_path] + ([summary_path] if abs_summary.exists() else []),
            commit_result=commit_result,
            commit_message=commit_msg,
            new_state=new_state,
            warnings=warnings,
        )
        return result.to_json()

    @mcp.tool(
        name="memory_create_plan",
        annotations=_tool_annotations(
            title="Create Research Plan",
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    async def memory_create_plan(
        plan_id: str,
        title: str,
        description: str,
        content: str,
        next_action: str,
        session_id: str,
        plan_type: str = "research-plan",
        preview: bool = False,
    ) -> str:
        """Create a new plan file and add it to plans/SUMMARY.md."""
        from ...errors import ValidationError
        from ...frontmatter_utils import append_plan_to_summary, build_plan_summary_block, today_str
        from ...models import MemoryWriteResult

        repo = get_repo()
        root = get_root()
        warnings: list[str] = []

        validate_session_id(session_id)
        plan_path = _plan_path(plan_id)
        abs_plan = repo.abs_path(plan_path)
        if abs_plan.exists():
            raise ValidationError(
                f"Plan already exists: {plan_path}. "
                "Use memory_write to overwrite, or choose a different plan_id."
            )

        today = today_str()
        fm_dict: dict[str, object] = {
            "source": "agent-generated",
            "type": plan_type,
            "title": title,
            "created": today,
            "last_verified": today,
            "trust": "medium",
            "status": "active",
            "next_action": next_action,
            "origin_session": session_id,
        }

        import frontmatter as fmlib  # type: ignore[import-untyped]

        post = fmlib.Post(content, **fm_dict)
        files_changed = [plan_path]

        summary_path = "plans/SUMMARY.md"
        abs_summary = root / summary_path
        updated_summary: str | None = None
        if abs_summary.exists():
            summary_content = abs_summary.read_text(encoding="utf-8")
            new_block = build_plan_summary_block(
                plan_id=plan_id,
                title=title,
                status="active",
                trust="medium",
                next_action=next_action,
                plan_progress=(0, 0),
                description=description,
            )
            updated_summary = append_plan_to_summary(summary_content, new_block)
            files_changed.append(summary_path)
        else:
            warnings.append(f"{summary_path} not found — plan entry not added to index.")

        commit_msg = f"[plan] Create {plan_id}"
        new_state = {"plan_path": plan_path, "status": "active"}
        preview_payload = build_governed_preview(
            mode="preview" if preview else "apply",
            change_class="proposed",
            summary=f"Create plan {plan_id} and register it in the plans index.",
            reasoning="Plan creation is a proposed durable-memory write because it adds a new active roadmap entry.",
            target_files=[
                preview_target(plan_path, "create"),
                *([preview_target(summary_path, "update")] if abs_summary.exists() else []),
            ],
            invariant_effects=[
                "Creates a governed plan file with standard frontmatter and active status.",
                "Updates plans/SUMMARY.md when the plan index exists.",
            ],
            commit_message=commit_msg,
            resulting_state=new_state,
            warnings=warnings,
        )
        if preview:
            result = MemoryWriteResult(
                files_changed=files_changed,
                commit_sha=None,
                commit_message=None,
                new_state=new_state,
                warnings=warnings,
                preview=preview_payload,
            )
            return result.to_json()

        abs_plan.parent.mkdir(parents=True, exist_ok=True)
        abs_plan.write_text(fmlib.dumps(post), encoding="utf-8")
        repo.add(plan_path)

        if abs_summary.exists() and updated_summary is not None:
            abs_summary.write_text(updated_summary, encoding="utf-8")
            repo.add(summary_path)

        commit_result = repo.commit(commit_msg)

        result = MemoryWriteResult.from_commit(
            files_changed=files_changed,
            commit_result=commit_result,
            commit_message=commit_msg,
            new_state=new_state,
            warnings=warnings,
            preview=preview_payload,
        )
        return result.to_json()

    @mcp.tool(
        name="memory_update_plan_next_action",
        annotations=_tool_annotations(
            title="Update Plan Next Action",
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    async def memory_update_plan_next_action(
        plan_id: str,
        next_action: str,
        version_token: str | None = None,
    ) -> str:
        """Update only next_action and last_verified in a plan's frontmatter."""
        from ...errors import NotFoundError
        from ...frontmatter_utils import (
            build_plan_summary_block,
            parse_plan_items,
            read_with_frontmatter,
            replace_begin_end_block,
            today_str,
        )
        from ...models import MemoryWriteResult

        repo = get_repo()
        root = get_root()
        warnings: list[str] = []

        plan_path = _plan_path(plan_id)
        abs_plan = repo.abs_path(plan_path)
        if not abs_plan.exists():
            raise NotFoundError(f"Plan not found: {plan_path}")

        repo.check_version_token(plan_path, version_token)

        import frontmatter as fmlib  # type: ignore[import-untyped]

        text = abs_plan.read_text(encoding="utf-8")
        post = fmlib.loads(text)
        post.metadata["next_action"] = next_action
        post.metadata["last_verified"] = today_str()
        abs_plan.write_text(fmlib.dumps(post), encoding="utf-8")
        repo.add(plan_path)

        files_changed = [plan_path]

        summary_path = "plans/SUMMARY.md"
        abs_summary = root / summary_path
        if abs_summary.exists():
            summary_content = abs_summary.read_text(encoding="utf-8")
            content = abs_plan.read_text(encoding="utf-8")
            phases = parse_plan_items(content)
            plan_done = sum(1 for ph in phases for it in ph["items"] if it["done"])
            plan_total = sum(ph["total"] for ph in phases)
            fm_dict, body = read_with_frontmatter(abs_plan)
            summary_title = _plan_summary_title(fm_dict, body, plan_id)

            new_block = build_plan_summary_block(
                plan_id=plan_id,
                title=summary_title,
                status=fm_dict.get("status", "active"),
                trust=fm_dict.get("trust", "medium"),
                next_action=next_action,
                plan_progress=(plan_done, plan_total),
            )
            updated = replace_begin_end_block(summary_content, plan_id, new_block)
            if updated is None:
                warnings.append(f"BEGIN/END anchor for '{plan_id}' not found in {summary_path}.")
            else:
                abs_summary.write_text(updated, encoding="utf-8")
                repo.add(summary_path)
                files_changed.append(summary_path)

        commit_msg = f"[plan] Update next-action for {plan_id}"
        commit_result = repo.commit(commit_msg)

        result = MemoryWriteResult.from_commit(
            files_changed=files_changed,
            commit_result=commit_result,
            commit_message=commit_msg,
            new_state={"next_action": next_action},
            warnings=warnings,
        )
        return result.to_json()

    @mcp.tool(
        name="memory_list_plans",
        annotations=_tool_annotations(
            title="List Memory Plans",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    async def memory_list_plans(status: str | None = None) -> str:
        """List all plans in the plans/ directory with their frontmatter metadata."""
        import json as _json

        from ...frontmatter_utils import read_with_frontmatter

        root = get_root()
        plans_dir = root / "plans"
        if not plans_dir.is_dir():
            return _json.dumps([])

        plans = []
        for plan_file in sorted(plans_dir.glob("*.md")):
            if plan_file.name in ("SUMMARY.md",):
                continue
            try:
                fm, _ = read_with_frontmatter(plan_file)
            except Exception:
                fm = {}
            plan_id = plan_file.stem
            plan_status = fm.get("status", "unknown")
            if status is not None and plan_status != status:
                continue
            plans.append(
                {
                    "plan_id": plan_id,
                    "status": plan_status,
                    "trust": fm.get("trust", "unknown"),
                    "next_action": fm.get("next_action", ""),
                    "created": str(fm.get("created", "")),
                    "last_verified": str(fm.get("last_verified", "")),
                }
            )

        plans.sort(key=lambda plan: (0 if plan["status"] == "active" else 1, plan["plan_id"]))
        return _json.dumps(plans, indent=2)

    return {
        "memory_mark_plan_item_complete": memory_mark_plan_item_complete,
        "memory_create_plan": memory_create_plan,
        "memory_update_plan_next_action": memory_update_plan_next_action,
        "memory_list_plans": memory_list_plans,
    }


__all__ = ["register_tools"]
