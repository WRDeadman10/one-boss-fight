"""BP-04 (C, implementer; Queue BP batch 1) after the C-1511 incident and the X-2288 hotfix: CLI smoke for Scripts/Tools.

SAFETY MODEL (X-2288):
  * Nothing is discovered and executed automatically. Only tools on the explicit, source-reviewed ALLOWLIST may ever be
    executed, and every allowlisted tool must satisfy `cli_static_contract.analyse` (an AST proof that `--help` exits
    inside argparse before any side effect).
  * Every other executable tool is pinned in NO_RUN with a reason; library modules (no `__main__`) are in LIBRARIES.
    A completeness test fails when a new file is unclassified, so nothing new can run before review.
  * X-2290: the contract is sequential and fail-closed (see cli_static_contract.py and test_bp_static_contract.py). The
    earlier no-argument execution class and its bounded "read-only" scan were removed; BP-03 parity evidence is
    pre-incident evidence only (BP_01_05_CLI_SMOKE.md).
  * EXECUTION IS OFF BY DEFAULT. The classes that execute tools only run when BP_SMOKE_EXECUTE=1 is set, which needs
    lead approval (X-2286). A plain `python -m unittest test_bp_cli_smoke` runs the static checks only.
"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
import cli_static_contract  # noqa: E402

EXECUTE = os.environ.get("BP_SMOKE_EXECUTE") == "1"
HELPER_MODULES = {'atomic_io', 'cli_static_contract', 'json_input', 'process_test_support', 'redaction', 'text_input'}

# Generated 2026-11-12 from the X-2290 contract and reviewed; every entry must still pass it (test_allowlist_is_proven).
ALLOWLIST = (
    'a7_release_gates', 'ar_charge_receipt', 'asset_provenance', 'audit_a5_driver_registration',
    'audit_editor_map_loads', 'audit_editor_save_safety', 'audit_framework_schemas', 'audit_pie_command',
    'audit_source_error_token_coverage', 'audit_tool_index', 'card_table', 'check_bench_kit',
    'check_bench_kit_manifest', 'check_doc_links', 'check_evidence_sha256', 'check_g044_cook_manifest',
    'check_g2_selection_refusal_expected', 'check_headers_selfcontained', 'check_ki_references',
    'check_line_endings', 'check_mailbox_ids', 'check_move_card_ids', 'check_packaged_smoke_receipt',
    'check_shipping_guards', 'check_stage_identity', 'check_test_plan_ids', 'check_ue_python_enum_conventions',
    'check_validator_tokens', 'compare_encounter_parity', 'compare_framework_tokens', 'compare_parry_runs',
    'detect_duplicate_pie_runs', 'diff_a5_nightly_reports', 'diff_manifests', 'diff_suite_logs',
    'discover_focused_player_tests', 'evidence_pack', 'evidence_pack_hashes', 'evidence_summary',
    'fight_capture_receipt', 'find_orphan_docs', 'framework_results', 'inventory_editor_asset_writers',
    'lint_expected_sheets', 'list_automation_tests', 'list_cvars', 'list_todo_markers', 'log_failures',
    'mailbox_decision_digest', 'mailbox_open_items', 'mailbox_stats', 'make_fight_video', 'make_source_manifest',
    'new_profile_field_scaffold', 'new_rule_scaffold', 'normalize_cook_package_manifest',
    'normalize_encounter_selection_graph', 'plan_camera_default', 'plot_framework_timeline', 'plugin_dependencies',
    'profile_dump', 'proof_report', 'round4_benchmark_report', 'round6_benchmark_report', 'round6_phase2_intake',
    'run_bo_lane_tests', 'run_bp_lane_tests', 'run_offline_suite_timed', 'scan_pie_driver_safety', 'source_metrics',
    'suite_log_report', 'summarize_encounter_cost', 'summarize_er_guard_counter', 'summarize_framework_log',
    'summarize_memory_soak', 'summarize_packaged_metrics', 'summarize_parity_set', 'token_coverage',
    'validate_a5_receipt_directory', 'validate_baked_cards', 'validate_encounter_manifest',
    'validate_owner_approval_envelope', 'validate_pending_definition_inputs', 'validate_queue_batches',
    'verify_bf_x05_selected_route', 'verify_bk56_60_receipts', 'verify_bk7_shipping_receipt',
    'verify_c1278_x26_live_log', 'verify_encounter_package_graph', 'verify_evidence_manifest',
    'verify_framework_perf_receipt', 'write_a4_parity_receipt',
)

# Executable tools that must never be run by tests: reason = static-contract failure or incident.
NO_RUN = {
    'ar_charge_repeat_receipt': "module line 15: calls ['spec_from_file_location']",
    'ar_er_cook_manifest': "module line 14: calls ['spec_from_file_location']",
    'audit_source_test_coverage': 'C-1511: no argparse; --help runs the full inventory',
    'aura_warmup_receipt': 'main() line 177: Import before parse_args (only direct setup allowed)',
    'build_parry_addendum_reel': 'C-1511: runs ffmpeg -y and overwrites the owner reels on D: (no argparse)',
    'build_sfx_audition_reel': 'C-1511: runs ffmpeg -y and overwrites the owner reels on D: (no argparse)',
    'build_sfx_batch3_reel': 'C-1511: runs ffmpeg -y and overwrites the owner reels on D: (no argparse)',
    'check_packaged_g044_cook': "module line 14: calls ['spec_from_file_location']",
    'compare_determinism_runs': 'module line 8: nested definition in an assignment',
    'compare_manifest_to_legacy_defaults': 'module line 116: default value of emit_legacy_baseline() calls code',
    'diff_phase_two_auras': 'C-1511: no argparse; --help runs the asset diff',
    'fight_review_observation': 'main() line 42: Import before parse_args (only direct setup allowed)',
    'retired_source_names': 'module line 10: nested definition in an assignment',
    'scan_doc_citations': 'main() line 106: Try before parse_args (only direct setup allowed)',
}

LIBRARIES = (
    'air_light_receipt', 'aq_evidence_freshness', 'bind_owner_approval', 'bind_receipt_source',
    'camera_probe_receipt', 'encounter_parity_receipt', 'plan_sevarog_definition_repair',
    'runner_status_receipt_proposal', 'runner_status_receipt_proposal_v1_1', 'runner_status_receipt_proposal_v1_2',
    'sevarog_executor_contract', 'sevarog_receipt_v2_proposal', 'validate_sevarog_executor_receipt',
)

def run(args, cwd, timeout=300):
    return subprocess.run([sys.executable, *map(str, args)], cwd=cwd, capture_output=True, text=True, timeout=timeout)


class StaticSafety(unittest.TestCase):
    """Always runs; executes no tool."""

    def test_every_file_is_classified_exactly_once(self):
        files = {p.stem for p in HERE.glob("*.py") if not p.stem.startswith("test_")}
        groups = [set(ALLOWLIST), set(NO_RUN), set(LIBRARIES), set(HELPER_MODULES)]
        self.assertEqual(set().union(*groups), files, "classify new tools before they can run")
        self.assertEqual(sum(len(g) for g in groups), len(files), "a tool is in more than one group")

    def test_allowlist_is_proven(self):
        for tool in ALLOWLIST:
            with self.subTest(tool=tool):
                ok, reason = cli_static_contract.analyse(HERE / f"{tool}.py")
                self.assertTrue(ok, reason)

    def test_incident_tools_are_never_allowlisted(self):
        for tool in ("build_parry_addendum_reel", "build_sfx_audition_reel", "build_sfx_batch3_reel",
                     "audit_source_test_coverage", "diff_phase_two_auras"):
            self.assertIn(tool, NO_RUN)
            self.assertNotIn(tool, ALLOWLIST)

    def test_contract_rejects_the_incident_tools(self):
        for tool in ("build_parry_addendum_reel", "build_sfx_audition_reel", "build_sfx_batch3_reel"):
            ok, _ = cli_static_contract.analyse(HERE / f"{tool}.py")
            self.assertFalse(ok, f"{tool} must fail the static contract")

    def test_libraries_have_no_main_block(self):
        for tool in LIBRARIES:
            with self.subTest(tool=tool):
                self.assertNotIn("__main__", (HERE / f"{tool}.py").read_text(encoding="utf-8", errors="replace"))


@unittest.skipUnless(EXECUTE, "tool execution needs BP_SMOKE_EXECUTE=1 and lead approval (X-2286)")
class HelpExecution(unittest.TestCase):
    def test_help_script_and_module(self):
        with tempfile.TemporaryDirectory() as foreign:
            for tool in ALLOWLIST:
                for style in ("script", "module"):
                    with self.subTest(tool=tool, style=style):
                        if style == "script":
                            r = run([HERE / f"{tool}.py", "--help"], cwd=foreign)
                        else:
                            r = run(["-m", f"Scripts.Tools.{tool}", "--help"], cwd=REPO)
                        self.assertNotIn("Traceback", r.stderr, r.stderr[-300:])
                        self.assertEqual(r.returncode, 0, r.stderr[-300:])
                        self.assertIn("usage", r.stdout.lower())


if __name__ == "__main__":
    unittest.main()
