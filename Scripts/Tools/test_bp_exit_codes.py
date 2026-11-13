"""BP-21..24 (C, implementer; Queue BP batch 5) under X-2295: static exit-code contract for the allowlisted tools.

No tool, main() or subprocess is run; each tool's source is parsed with ast. The snapshot pins, per tool: the literal
exit codes main() can return or raise, whether it can also return a computed value, and whether it uses parser.error
(argparse exit 2) or json_input.fail (exit 2). Any change to a tool's exit behaviour fails this test until the snapshot
is updated deliberately (and the change is reported to the lead).

Lane contract (documented in BP_21_25_EXIT_CODES.md): 0 = clean, 1 = findings/failed check, 2 = bad input or usage,
3 = tool-specific "incomplete" (pinned exceptions: proof_report, diff_suite_logs).
"""
import ast
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import test_bp_cli_smoke as smoke  # noqa: E402

# tool: (literal codes, may return a computed value, uses parser.error, uses json_input.fail)
SNAPSHOT = {
    'a7_release_gates': ([0, 1, 2], False, False, False),
    'ar_charge_receipt': ([0], False, True, False),
    'asset_provenance': ([0, 2], False, True, False),
    'audit_a5_driver_registration': ([], True, False, False),
    'audit_editor_map_loads': ([], True, False, False),
    'audit_editor_save_safety': ([0, 2], False, False, False),
    'audit_framework_schemas': ([], True, False, False),
    'audit_pie_command': ([0, 1, 2], False, True, False),
    'audit_source_error_token_coverage': ([], False, True, False),
    'audit_tool_index': ([], True, True, False),
    'card_table': ([0], True, False, True),
    'check_bench_kit': ([], True, False, False),
    'check_bench_kit_manifest': ([], True, False, False),
    'check_doc_links': ([], True, False, False),
    'check_evidence_sha256': ([1], True, False, False),
    'check_g044_cook_manifest': ([2], True, False, False),
    'check_g2_selection_refusal_expected': ([0, 1], True, False, True),
    'check_headers_selfcontained': ([0], False, False, False),
    'check_ki_references': ([], True, False, False),
    'check_line_endings': ([0], False, False, False),
    'check_mailbox_ids': ([], True, True, False),
    'check_move_card_ids': ([], True, False, True),
    'check_packaged_smoke_receipt': ([0, 1, 2], False, False, False),
    'check_shipping_guards': ([], True, False, False),
    'check_stage_identity': ([], True, False, False),
    'check_test_plan_ids': ([], True, False, False),
    'check_ue_python_enum_conventions': ([], True, False, False),
    'check_validator_tokens': ([0, 1], False, True, False),
    'compare_encounter_parity': ([0, 1, 2], False, False, False),
    'compare_framework_tokens': ([0], False, False, False),
    'compare_parry_runs': ([0], False, True, False),
    'detect_duplicate_pie_runs': ([], True, False, False),
    'diff_a5_nightly_reports': ([0], False, True, False),
    'diff_manifests': ([0], False, False, False),
    'diff_suite_logs': ([2, 3], True, True, False),
    'discover_focused_player_tests': ([], True, False, False),
    'evidence_pack': ([0], False, True, False),
    'evidence_pack_hashes': ([0], False, True, False),
    'evidence_summary': ([0], False, True, False),
    'fight_capture_receipt': ([0], False, True, False),
    'find_orphan_docs': ([], False, False, False),
    'framework_results': ([], True, True, False),
    'inventory_editor_asset_writers': ([0, 2], False, False, False),
    'lint_expected_sheets': ([], True, True, False),
    'list_automation_tests': ([0], False, False, False),
    'list_cvars': ([0], False, False, False),
    'list_todo_markers': ([0], False, False, False),
    'log_failures': ([0], False, True, False),
    'mailbox_decision_digest': ([0], False, True, False),
    'mailbox_open_items': ([0], False, True, False),
    'mailbox_stats': ([0], False, True, False),
    'make_fight_video': ([0], False, True, False),
    'make_source_manifest': ([0], False, True, False),
    'new_profile_field_scaffold': ([0], False, True, False),
    'new_rule_scaffold': ([0, 2], False, True, False),
    'normalize_cook_package_manifest': ([0, 2], False, False, False),
    'normalize_encounter_selection_graph': ([0, 2], False, False, False),
    'plan_camera_default': ([], True, False, False),
    'plot_framework_timeline': ([0], False, True, False),
    'plugin_dependencies': ([0], True, True, True),
    'profile_dump': ([0], True, False, True),
    'proof_report': ([0, 1, 2, 3], False, True, False),
    'round4_benchmark_report': ([2], True, False, False),
    'round6_benchmark_report': ([0, 2], True, False, True),
    'round6_phase2_intake': ([0, 2], False, False, False),
    'run_bo_lane_tests': ([0], True, True, False),
    'run_bp_lane_tests': ([], True, True, False),
    'run_offline_suite_timed': ([0, 2], True, True, False),
    'scan_pie_driver_safety': ([], True, False, False),
    'source_metrics': ([0], False, True, False),
    'suite_log_report': ([2], True, True, False),
    'summarize_encounter_cost': ([2], True, False, False),
    'summarize_er_guard_counter': ([0], False, False, False),
    'summarize_framework_log': ([], True, False, False),
    'summarize_memory_soak': ([], True, True, False),
    'summarize_packaged_metrics': ([2], True, False, False),
    'summarize_parity_set': ([], True, False, False),
    'token_coverage': ([2], True, True, False),
    'validate_a5_receipt_directory': ([0, 1, 2], False, False, False),
    'validate_baked_cards': ([], True, False, True),
    'validate_encounter_manifest': ([0, 1, 2], False, False, False),
    'validate_owner_approval_envelope': ([1], True, False, False),
    'validate_pending_definition_inputs': ([1], True, False, False),
    'validate_queue_batches': ([], True, False, False),
    'verify_bf_x05_selected_route': ([], True, False, False),
    'verify_bk56_60_receipts': ([], True, False, False),
    'verify_bk7_shipping_receipt': ([0, 1, 2], False, False, False),
    'verify_c1278_x26_live_log': ([], True, True, False),
    'verify_encounter_package_graph': ([0, 1, 2], False, False, False),
    'verify_evidence_manifest': ([], True, False, False),
    'verify_framework_perf_receipt': ([0, 1, 2], False, False, False),
    'write_a4_parity_receipt': ([0, 2], False, False, False),
}
CODE_3_ALLOWED = {"proof_report", "diff_suite_logs"}
IMPLICIT_ZERO = {"audit_source_error_token_coverage", "find_orphan_docs"}  # BP-24 recommendation: return explicitly


def profile(tool):
    tree = ast.parse((HERE / f"{tool}.py").read_text(encoding="utf-8"))
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    literals, computed = set(), False
    for node in ast.walk(main):
        if isinstance(node, ast.Return):
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, int):
                literals.add(node.value.value)
            elif node.value is not None:
                computed = True
        if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call) and getattr(node.exc.func, "id", "") == "SystemExit":
            args = node.exc.args
            if args and isinstance(args[0], ast.Constant) and isinstance(args[0].value, int):
                literals.add(args[0].value)
            else:
                computed = True
    calls = {getattr(c.func, "attr", getattr(c.func, "id", "")) for c in ast.walk(main) if isinstance(c, ast.Call)}
    return sorted(literals), computed, "error" in calls, "fail" in calls


class ExitCodeContract(unittest.TestCase):
    def test_snapshot_covers_the_allowlist(self):
        self.assertEqual(set(SNAPSHOT), set(smoke.ALLOWLIST))

    def test_each_tool_matches_its_snapshot(self):
        for tool, expected in sorted(SNAPSHOT.items()):
            with self.subTest(tool=tool):
                lits, comp, perr, jfail = profile(tool)
                self.assertEqual((lits, comp, perr, jfail), (list(expected[0]), expected[1], expected[2], expected[3]))

    def test_literal_codes_stay_in_contract(self):
        for tool, (lits, *_rest) in SNAPSHOT.items():
            with self.subTest(tool=tool):
                allowed = {0, 1, 2, 3} if tool in CODE_3_ALLOWED else {0, 1, 2}
                self.assertLessEqual(set(lits), allowed)

    def test_implicit_zero_tools_are_known(self):
        implicit = {tool for tool, (lits, comp, *_r) in SNAPSHOT.items() if not lits and not comp}
        self.assertEqual(implicit, IMPLICIT_ZERO)


if __name__ == "__main__":
    unittest.main()
