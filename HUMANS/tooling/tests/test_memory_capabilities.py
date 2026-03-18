from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    import tomli as tomllib


REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = REPO_ROOT / "HUMANS" / "tooling" / "agent-memory-capabilities.toml"
RESOLVER_PATH = (
    REPO_ROOT / "HUMANS" / "tooling" / "scripts" / "resolve_memory_capabilities.py"
)

SPEC = importlib.util.spec_from_file_location("resolve_memory_capabilities", RESOLVER_PATH)
assert SPEC is not None
resolver = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = resolver
SPEC.loader.exec_module(resolver)


class MemoryCapabilitiesTests(unittest.TestCase):
    def test_current_seed_manifest_resolves_against_runtime(self) -> None:
        resolution = resolver.resolve_capabilities(REPO_ROOT)
        self.assertEqual(resolution["errors"], [], "\n".join(resolution["errors"]))

    def test_manifest_declares_expected_desktop_gaps(self) -> None:
        manifest = tomllib.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        declared_gaps = manifest["tool_sets"]["declared_gaps"]

        self.assertEqual(
            declared_gaps,
            ["append_access_entry", "record_session_reflection"],
        )
        self.assertEqual(
            manifest["desktop_operations"]["append_access_entry"]["status"], "gap"
        )
        self.assertEqual(
            manifest["desktop_operations"]["record_session_reflection"]["status"],
            "gap",
        )
        self.assertEqual(
            manifest["desktop_operations"]["append_access_entry"]["change_class"],
            "automatic",
        )

    def test_semantic_operations_own_required_contract_fields(self) -> None:
        manifest = tomllib.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        raw_fallback = set(manifest["tool_sets"]["raw_fallback"])
        change_classes = set(manifest["change_classes"])

        for tool_name in manifest["tool_sets"]["semantic_extensions"]:
            operation = manifest["operations"][tool_name]
            self.assertEqual(operation["tier"], "semantic")
            self.assertIn(operation["change_class"], change_classes)
            self.assertIn("auto_commit", operation["commit_model"])
            self.assertIsInstance(operation["writes"], list)
            self.assertIsInstance(operation["owns_frontmatter"], list)
            self.assertIsInstance(operation["owns_summaries"], list)
            self.assertIsInstance(operation["owns_access_logs"], list)
            self.assertIsInstance(operation["owns_review_queue"], list)
            self.assertIsInstance(operation["result_fields"], list)
            self.assertTrue(set(operation["fallback_tools"]).issubset(raw_fallback))

    def test_manifest_declares_change_classes_and_raw_fallback_policy(self) -> None:
        manifest = tomllib.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        change_classes = manifest["change_classes"]
        raw_fallback_policy = manifest["raw_fallback_policy"]

        self.assertEqual(
            sorted(change_classes),
            ["automatic", "proposed", "protected"],
        )
        self.assertEqual(
            change_classes["automatic"]["read_only_behavior"],
            "defer_and_emit_summary",
        )
        self.assertEqual(
            raw_fallback_policy["policy"], "inherit_operation_change_class"
        )
        self.assertTrue(raw_fallback_policy["requires_change_class"])
        self.assertEqual(
            raw_fallback_policy["preview_required_for"],
            ["proposed", "protected"],
        )

    def test_manifest_declares_hybrid_integration_boundary(self) -> None:
        manifest = tomllib.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        boundary = manifest["integration_boundary"]

        self.assertEqual(boundary["model"], "hybrid")
        self.assertEqual(boundary["prefer"], "repo_local_semantic_mcp")
        self.assertEqual(boundary["native_semantic_scope"], "generic_only")
        self.assertTrue(boundary["manifest_required_for_repo_specific_semantics"])
        self.assertEqual(
            boundary["degradation_order"],
            [
                "repo_local_semantic_mcp",
                "codex_native_preview_and_policy",
                "raw_fallback_or_defer",
            ],
        )
        self.assertTrue(
            {
                "approval_ux",
                "change_class_enforcement",
                "capability_discovery",
                "preview_rendering",
                "result_presentation",
                "fallback_selection",
            }.issubset(boundary["desktop_owns"])
        )
        self.assertTrue(
            {
                "semantic_execution",
                "repo_specific_invariants",
                "schema_validation",
                "authoritative_mutation",
                "structured_result_state",
            }.issubset(boundary["repo_local_mcp_owns"])
        )
        self.assertEqual(
            boundary["native_fallback_owns"],
            [
                "generic_preview",
                "raw_tool_orchestration",
                "deferred_action_summary",
            ],
        )

    def test_manifest_declares_fallback_behavior_profiles_for_raw_and_deferred_paths(
        self,
    ) -> None:
        manifest = tomllib.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        fallback_behavior = manifest["fallback_behavior"]
        desktop_operations = manifest["desktop_operations"]

        self.assertEqual(
            sorted(fallback_behavior),
            ["preview_only", "read_only", "semantic_gap", "uninterpretable_target"],
        )
        self.assertTrue(fallback_behavior["semantic_gap"]["raw_tools_allowed"])
        self.assertTrue(
            fallback_behavior["semantic_gap"]["requires_contract_preservation"]
        )
        self.assertFalse(
            fallback_behavior["uninterpretable_target"]["raw_tools_allowed"]
        )
        self.assertEqual(
            fallback_behavior["preview_only"]["result"],
            "return_preview_without_writing",
        )
        self.assertEqual(
            fallback_behavior["read_only"]["result"],
            "return_deferred_action_summary",
        )
        self.assertEqual(
            desktop_operations["append_access_entry"]["fallback_profile"],
            "semantic_gap",
        )
        self.assertEqual(
            desktop_operations["record_session_reflection"]["fallback_profile"],
            "semantic_gap",
        )

    def test_manifest_declares_approval_preview_and_confirmation_flows(self) -> None:
        manifest = tomllib.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        approval_ux = manifest["approval_ux"]

        self.assertEqual(
            approval_ux["preview"]["required_for"],
            ["proposed", "protected"],
        )
        self.assertEqual(
            approval_ux["preview"]["sections"],
            [
                "summary",
                "reasoning",
                "target_files",
                "invariant_effects",
                "commit_suggestion",
                "fallback_behavior",
            ],
        )
        self.assertTrue(approval_ux["preview"]["show_resulting_state"])
        self.assertTrue(approval_ux["preview"]["show_warnings"])
        self.assertEqual(approval_ux["proposed"]["trigger"], "before_write")
        self.assertEqual(
            approval_ux["proposed"]["primary_action"],
            "apply_after_confirmation",
        )
        self.assertEqual(
            approval_ux["protected"]["primary_action"],
            "approve_and_apply",
        )
        self.assertEqual(
            approval_ux["protected"]["secondary_actions"],
            ["open_files", "defer", "cancel"],
        )

    def test_desktop_operation_change_classes_match_semantic_tools(self) -> None:
        manifest = tomllib.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        desktop_operations = manifest["desktop_operations"]
        operations = manifest["operations"]

        self.assertEqual(
            operations["memory_create_plan"]["change_class"],
            "proposed",
        )
        self.assertEqual(
            operations["memory_mark_plan_item_complete"]["change_class"],
            "automatic",
        )
        self.assertEqual(
            operations["memory_update_identity_trait"]["change_class"],
            "proposed",
        )
        self.assertEqual(
            operations["memory_flag_for_review"]["change_class"],
            "automatic",
        )
        self.assertEqual(
            desktop_operations["create_plan"]["change_class"],
            operations["memory_create_plan"]["change_class"],
        )
        self.assertEqual(
            desktop_operations["flag_for_review"]["change_class"],
            operations["memory_flag_for_review"]["change_class"],
        )

    def test_semantic_operations_declare_commit_category_hints(self) -> None:
        manifest = tomllib.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        operations = manifest["operations"]

        self.assertEqual(
            operations["memory_create_plan"]["commit_category_hint"],
            "plan",
        )
        self.assertEqual(
            operations["memory_add_knowledge_file"]["commit_category_hint"],
            "knowledge",
        )
        self.assertEqual(
            operations["memory_update_identity_trait"]["commit_category_hint"],
            "identity",
        )
        self.assertEqual(
            operations["memory_record_chat_summary"]["commit_category_hint"],
            "chat",
        )
        self.assertEqual(
            operations["memory_flag_for_review"]["commit_category_hint"],
            "curation",
        )

    def test_error_taxonomy_marks_already_done_as_declared_but_not_emitted(self) -> None:
        manifest = tomllib.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        errors = manifest["error_taxonomy"]

        self.assertEqual(errors["ConflictError"]["status"], "implemented")
        self.assertEqual(errors["ValidationError"]["status"], "implemented")
        self.assertEqual(
            errors["AlreadyDoneError"]["status"], "defined_not_currently_emitted"
        )

    def test_resolver_returns_integration_boundary(self) -> None:
        resolution = resolver.resolve_capabilities(REPO_ROOT, include_runtime=False)
        boundary = resolution["integration_boundary"]

        self.assertEqual(boundary["model"], "hybrid")
        self.assertEqual(boundary["prefer"], "repo_local_semantic_mcp")
        self.assertEqual(
            boundary["degradation_order"],
            [
                "repo_local_semantic_mcp",
                "codex_native_preview_and_policy",
                "raw_fallback_or_defer",
            ],
        )


if __name__ == "__main__":
    unittest.main()
