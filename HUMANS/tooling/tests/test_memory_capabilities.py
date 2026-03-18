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

    def test_error_taxonomy_marks_already_done_as_declared_but_not_emitted(self) -> None:
        manifest = tomllib.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        errors = manifest["error_taxonomy"]

        self.assertEqual(errors["ConflictError"]["status"], "implemented")
        self.assertEqual(errors["ValidationError"]["status"], "implemented")
        self.assertEqual(
            errors["AlreadyDoneError"]["status"], "defined_not_currently_emitted"
        )


if __name__ == "__main__":
    unittest.main()
