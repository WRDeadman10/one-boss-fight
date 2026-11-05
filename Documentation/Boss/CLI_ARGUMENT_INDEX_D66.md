# Offline CLI argument index (D66)

Date: 2026-11-03. Compared every maintained tool in `Scripts/Tools/CLI_AUTHOR_GUIDE_S154.md` with source `add_argument` declarations and invoked each command with `--help` (43/43 returned exit 0). This complements the I/O/exit/side-effect table in S154. Defaults below are parser defaults; `None/False` denotes argparse implicit optional-action defaults. All positional args are required unless marked optional.

| CLI | Observed `--help` usage | Arguments and defaults |
|---|---|---|
| `asset_provenance.py` | `asset_provenance.py [-h] [--evidence EVIDENCE] script` | script (required positional); --evidence (optional option, default []; action='append') |
| `audit_framework_schemas.py` | `audit_framework_schemas.py [-h] [--root ROOT]` | --root (optional option, default Path(__file__).resolve().parents[2]) |
| `audit_pie_command.py` | `audit_pie_command.py [-h] command expected` | command (required positional); expected (required positional) |
| `audit_tool_index.py` | `audit_tool_index.py [-h] [--root ROOT] [--index INDEX]` | --root (optional option, default Path(__file__).resolve().parents[2]); --index (optional option, default Path('Documentation/Boss/TOOLS.md')) |
| `card_table.py` | `card_table.py [-h] card_json` | card_json (required positional) |
| `check_doc_links.py` | `check_doc_links.py [-h] [root]` | root (optional positional, default Path('.'); nargs='?') |
| `check_evidence_sha256.py` | `check_evidence_sha256.py [-h] [root]` | root (optional positional, default Path('.'); nargs='?') |
| `check_headers_selfcontained.py` | `check_headers_selfcontained.py [-h] [--root ROOT]` | --root (optional option, default Path('.')) |
| `check_ki_references.py` | `check_ki_references.py [-h] [--root ROOT]` | --root (optional option, default Path('.')) |
| `check_line_endings.py` | `check_line_endings.py [-h] [--root ROOT]` | --root (optional option, default Path('.')) |
| `check_mailbox_ids.py` | `check_mailbox_ids.py [-h] [mailbox]` | mailbox (optional positional, default Path('Documentation/TEAM_MAILBOX.md'); nargs='?') |
| `check_move_card_ids.py` | `check_move_card_ids.py [-h] exports [exports ...]` | exports (required positional, nargs='+') |
| `check_shipping_guards.py` | `check_shipping_guards.py [-h] [--root ROOT]` | --root (optional option, default Path('.')) |
| `check_test_plan_ids.py` | `check_test_plan_ids.py [-h] [--root ROOT]` | --root (optional option, default Path('.')) |
| `check_validator_tokens.py` | `check_validator_tokens.py [-h] [--root ROOT]` | --root (optional option, default Path(__file__).resolve().parents[2]) |
| `compare_framework_tokens.py` | `compare_framework_tokens.py [-h] before after` | before (required positional); after (required positional) |
| `compare_parry_runs.py` | `compare_parry_runs.py [-h] baseline candidate` | baseline (required positional); candidate (required positional) |
| `detect_duplicate_pie_runs.py` | `detect_duplicate_pie_runs.py [-h] logs [logs ...]` | logs (required positional, nargs='+') |
| `diff_manifests.py` | `diff_manifests.py [-h] before after` | before (required positional); after (required positional) |
| `diff_suite_logs.py` | `diff_suite_logs.py [-h] before after` | before (required positional); after (required positional) |
| `evidence_pack.py` | `evidence_pack.py [-h] [--pre-state PRE_STATE] [--post-state POST_STATE] raw_log output` | raw_log (required positional); output (required positional); --pre-state (optional option, default None/False); --post-state (optional option, default None/False) |
| `evidence_summary.py` | `evidence_summary.py [-h] [--root ROOT] [--evidence EVIDENCE] --output OUTPUT` | --root (optional option, default Path('.')); --evidence (optional option, default Path('Docs/BossCombatReview/Execution/Claude')); --output (required option) |
| `framework_results.py` | `framework_results.py [-h] log` | log (required positional) |
| `lint_expected_sheets.py` | `lint_expected_sheets.py [-h] [--root ROOT] paths [paths ...]` | paths (required positional, nargs='+'); --root (optional option, default Path(__file__).resolve().parents[2]) |
| `list_automation_tests.py` | `list_automation_tests.py [-h] [--root ROOT]` | --root (optional option, default Path('.')) |
| `list_cvars.py` | `list_cvars.py [-h] [--root ROOT]` | --root (optional option, default Path('.')) |
| `list_todo_markers.py` | `list_todo_markers.py [-h] [root]` | root (optional positional, default Path('.'); nargs='?') |
| `log_failures.py` | `log_failures.py [-h] [--limit LIMIT] log` | log (required positional); --limit (optional option, default 100) |
| `mailbox_stats.py` | `mailbox_stats.py [-h] [mailbox]` | mailbox (optional positional, default Path('Documentation/TEAM_MAILBOX.md'); nargs='?') |
| `make_source_manifest.py` | `make_source_manifest.py [-h] [--root ROOT] output` | output (required positional); --root (optional option, default Path('.')) |
| `new_profile_field_scaffold.py` | `new_profile_field_scaffold.py [-h] --field FIELD [--error-token ERROR_TOKEN] [--log-token LOG_TOKEN] [--test-control]` | --field (required option); --error-token (optional option, default None/False); --log-token (optional option, default None/False); --test-control (optional option, default None/False; action='store_true') |
| `new_rule_scaffold.py` | `new_rule_scaffold.py [-h] --name NAME --requirement-id REQUIREMENT_ID --slug SLUG --output-root OUTPUT_ROOT` | --name (required option); --requirement-id (required option); --slug (required option); --output-root (required option) |
| `plot_framework_timeline.py` | `plot_framework_timeline.py [-h] [--limit LIMIT] log` | log (required positional); --limit (optional option, default 300) |
| `plugin_dependencies.py` | `plugin_dependencies.py [-h] [--root ROOT]` | --root (optional option, default Path('.')) |
| `profile_dump.py` | `profile_dump.py [-h] profile_json` | profile_json (required positional) |
| `proof_report.py` | `proof_report.py [-h] [--control-log CONTROL_LOG] [--manifest MANIFEST] [--expect-map EXPECT_MAP] [--expect-profile EXPECT_PROFILE] [--expect-run-id EXPECT_RUN_ID] [--require-complete-run] log expected` | log (required positional); expected (required positional); --control-log (optional option, default None/False); --manifest (optional option, default None/False); --expect-map (optional option, default None/False); --expect-profile (optional option, default None/False); --expect-run-id (optional option, default None/False); --require-complete-run (optional option, default None/False; action='store_true') |
| `retired_source_names.py` | `retired_source_names.py [-h] [--root ROOT]` | --root (optional option, default Path('.')) |
| `source_metrics.py` | `source_metrics.py [-h] [--root ROOT]` | --root (optional option, default Path('.')) |
| `suite_log_report.py` | `suite_log_report.py [-h] [--json] log` | log (required positional); --json (optional option, default None/False; action='store_true') |
| `summarize_framework_log.py` | `summarize_framework_log.py [-h] logs [logs ...]` | logs (required positional, nargs='+') |
| `token_coverage.py` | `token_coverage.py [-h] [--root ROOT] [--samples-output SAMPLES_OUTPUT] [logs ...]` | --root (optional option, default Path('.')); --samples-output (optional option, default None/False); logs (optional positional, nargs='*') |
| `validate_baked_cards.py` | `validate_baked_cards.py [-h] cards_json` | cards_json (required positional) |
| `verify_evidence_manifest.py` | `verify_evidence_manifest.py [-h] manifest` | manifest (required positional) |

## Error behavior

All 43 `--help` invocations succeeded. Invalid CLI syntax is handled by argparse and exits 2. Missing input files are not uniform: some CLIs call `parser.error` (2), some print a finding and return 1, and some surface an uncaught I/O/parse exception (nonzero traceback); see the per-tool exit/error column in `CLI_AUTHOR_GUIDE_S154.md`. This is argument/usage inventory only, not semantic validation or execution of normal commands.
