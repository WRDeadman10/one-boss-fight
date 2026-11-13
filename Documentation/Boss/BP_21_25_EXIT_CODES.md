# BP-21..25: exit-code contract inventory for the allowlisted tools (Queue BP, batch 5 of 10)

C (implementer), 2026-11-12. Validation per X-2295: **static only**. Tool sources were parsed with `ast`; no tool, `main()` or subprocess was run. **No tool behaviour was changed in this batch.**

**Not done:** no Unreal, build, PIE or asset work, no KNOWN_ISSUES status change, no commit or push.

## Contract (BP-23)

| Exit code | Meaning |
|---|---|
| **0** | clean |
| **1** | findings or a failed check |
| **2** | bad input or usage (`argparse` errors via `parser.error`, and `json_input.fail`) |
| **3** | tool-specific "incomplete"; currently only `proof_report` (incomplete run or manual review) and `diff_suite_logs`, which are pinned as allowed exceptions |

## Inventory summary (BP-21)

Of the 91 allowlisted mains:
- **31** return only computed values (for example `return int(bool(x))` or `return 1 if … else 0`).
- **28** have literal `0` only.
- **10** have `0` and `2`; **9** have `0`, `1` and `2`; **6** have `2` only; **3** have `1` only; **2** have `0` and `1`.
- **1** has `2` and `3`, and **1** has `0` to `3`.
- **2 tools never return an explicit value, so they always exit 0:** `audit_source_error_token_coverage` (its failures go through `parser.error`) and `find_orphan_docs`.

## Pin (BP-22)

**New `Scripts/Tools/test_bp_exit_codes.py`, 4 static tests.** It embeds the per-tool snapshot: literal codes, whether a computed return is possible, `parser.error` use and `json_input.fail` use. The tests check that:
- the snapshot covers exactly the allowlist;
- every tool still matches its snapshot, so an exit-behaviour change cannot land silently;
- literal codes stay within the contract (`{0,1,2}`, plus `3` for the two exceptions);
- the implicit-zero set is exactly the 2 known tools.

**Mutation check:** changing `proof_report`'s `return 3` to `return 4` in a temp copy fails the snapshot test.

## Recommendations (BP-24; not implemented, lead decision)

1. **Explicit returns:** make `audit_source_error_token_coverage` and `find_orphan_docs` return explicitly. There is no behaviour change for `audit_source…`. For `find_orphan_docs`, consider exit 1 when orphans are found; that would be a contract change.
2. **`find_orphan_docs` root default:** it defaults `--root` to the string `"."`, a cwd-relative default that the BP-03 scan missed because it looked for `Path(".")`. Fix it with the same parity gate in a later batch.
3. **Bad-input codes:** for tools that return 1 for bad input rather than 2, separating them needs execution probing, which waits on approval.

## Checks run

| Command (from `Scripts/Tools`, `BP_SMOKE_EXECUTE` unset) | Result |
|---|---|
| `python -m unittest test_bp_exit_codes` | Ran 4, OK |

**Paths touched:** the allowlisted tools' source files (read and parsed only).

## Full inventory (BP-25)

| Tool | Literal codes | Computed return | `parser.error` | `json_input.fail` |
|---|---|---|---|---|
| `a7_release_gates` | 0,1,2 |  |  |  |
| `ar_charge_receipt` | 0 |  | yes |  |
| `asset_provenance` | 0,2 |  | yes |  |
| `audit_a5_driver_registration` | — | yes |  |  |
| `audit_editor_map_loads` | — | yes |  |  |
| `audit_editor_save_safety` | 0,2 |  |  |  |
| `audit_framework_schemas` | — | yes |  |  |
| `audit_pie_command` | 0,1,2 |  | yes |  |
| `audit_source_error_token_coverage` | — |  | yes |  |
| `audit_tool_index` | — | yes | yes |  |
| `card_table` | 0 | yes |  | yes |
| `check_bench_kit` | — | yes |  |  |
| `check_bench_kit_manifest` | — | yes |  |  |
| `check_doc_links` | — | yes |  |  |
| `check_evidence_sha256` | 1 | yes |  |  |
| `check_g044_cook_manifest` | 2 | yes |  |  |
| `check_g2_selection_refusal_expected` | 0,1 | yes |  | yes |
| `check_headers_selfcontained` | 0 |  |  |  |
| `check_ki_references` | — | yes |  |  |
| `check_line_endings` | 0 |  |  |  |
| `check_mailbox_ids` | — | yes | yes |  |
| `check_move_card_ids` | — | yes |  | yes |
| `check_packaged_smoke_receipt` | 0,1,2 |  |  |  |
| `check_shipping_guards` | — | yes |  |  |
| `check_stage_identity` | — | yes |  |  |
| `check_test_plan_ids` | — | yes |  |  |
| `check_ue_python_enum_conventions` | — | yes |  |  |
| `check_validator_tokens` | 0,1 |  | yes |  |
| `compare_encounter_parity` | 0,1,2 |  |  |  |
| `compare_framework_tokens` | 0 |  |  |  |
| `compare_parry_runs` | 0 |  | yes |  |
| `detect_duplicate_pie_runs` | — | yes |  |  |
| `diff_a5_nightly_reports` | 0 |  | yes |  |
| `diff_manifests` | 0 |  |  |  |
| `diff_suite_logs` | 2,3 | yes | yes |  |
| `discover_focused_player_tests` | — | yes |  |  |
| `evidence_pack` | 0 |  | yes |  |
| `evidence_pack_hashes` | 0 |  | yes |  |
| `evidence_summary` | 0 |  | yes |  |
| `fight_capture_receipt` | 0 |  | yes |  |
| `find_orphan_docs` | — |  |  |  |
| `framework_results` | — | yes | yes |  |
| `inventory_editor_asset_writers` | 0,2 |  |  |  |
| `lint_expected_sheets` | — | yes | yes |  |
| `list_automation_tests` | 0 |  |  |  |
| `list_cvars` | 0 |  |  |  |
| `list_todo_markers` | 0 |  |  |  |
| `log_failures` | 0 |  | yes |  |
| `mailbox_decision_digest` | 0 |  | yes |  |
| `mailbox_open_items` | 0 |  | yes |  |
| `mailbox_stats` | 0 |  | yes |  |
| `make_fight_video` | 0 |  | yes |  |
| `make_source_manifest` | 0 |  | yes |  |
| `new_profile_field_scaffold` | 0 |  | yes |  |
| `new_rule_scaffold` | 0,2 |  | yes |  |
| `normalize_cook_package_manifest` | 0,2 |  |  |  |
| `normalize_encounter_selection_graph` | 0,2 |  |  |  |
| `plan_camera_default` | — | yes |  |  |
| `plot_framework_timeline` | 0 |  | yes |  |
| `plugin_dependencies` | 0 | yes | yes | yes |
| `profile_dump` | 0 | yes |  | yes |
| `proof_report` | 0,1,2,3 |  | yes |  |
| `round4_benchmark_report` | 2 | yes |  |  |
| `round6_benchmark_report` | 0,2 | yes |  | yes |
| `round6_phase2_intake` | 0,2 |  |  |  |
| `run_bo_lane_tests` | 0 | yes | yes |  |
| `run_offline_suite_timed` | 0,2 | yes | yes |  |
| `scan_pie_driver_safety` | — | yes |  |  |
| `source_metrics` | 0 |  | yes |  |
| `suite_log_report` | 2 | yes | yes |  |
| `summarize_encounter_cost` | 2 | yes |  |  |
| `summarize_er_guard_counter` | 0 |  |  |  |
| `summarize_framework_log` | — | yes |  |  |
| `summarize_memory_soak` | — | yes | yes |  |
| `summarize_packaged_metrics` | 2 | yes |  |  |
| `summarize_parity_set` | — | yes |  |  |
| `token_coverage` | 2 | yes | yes |  |
| `validate_a5_receipt_directory` | 0,1,2 |  |  |  |
| `validate_baked_cards` | — | yes |  | yes |
| `validate_encounter_manifest` | 0,1,2 |  |  |  |
| `validate_owner_approval_envelope` | 1 | yes |  |  |
| `validate_pending_definition_inputs` | 1 | yes |  |  |
| `validate_queue_batches` | — | yes |  |  |
| `verify_bf_x05_selected_route` | — | yes |  |  |
| `verify_bk56_60_receipts` | — | yes |  |  |
| `verify_bk7_shipping_receipt` | 0,1,2 |  |  |  |
| `verify_c1278_x26_live_log` | — | yes | yes |  |
| `verify_encounter_package_graph` | 0,1,2 |  |  |  |
| `verify_evidence_manifest` | — | yes |  |  |
| `verify_framework_perf_receipt` | 0,1,2 |  |  |  |
| `write_a4_parity_receipt` | 0,2 |  |  |  |
