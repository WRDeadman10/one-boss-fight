# Offline tools

Scripts here inspect source, docs, manifests, JSON exports, mailboxes or existing logs. They do not require Unreal to be open unless a tool's own usage says otherwise. Run a script's `--help` before using unfamiliar arguments. Main usage collection: `Documentation/Boss/TOOLS.md`.

File outputs use the shared `atomic_io.py` helper where replacement or no-overwrite publication is needed; the S171 audit and failure-injection fixture are linked from `Documentation/Boss/TOOLS.md`.

| Script | Purpose |
|---|---|
| `audit_a5_driver_registration.py` | Compare all receipt-registered A5 drivers with RunDrivers and fresh-process runner registration. |
| `audit_source_test_coverage.py` | Heuristic source-to-native-test inventory for Queue U; reports primary types without a direct automation source reference and flags helper files needing manual mapping. |
| `audit_editor_map_loads.py` | Find literal known-map paths passed to `load_asset` in Editor scripts. |
| `audit_editor_save_safety.py` | Report explicit first-save lines and earlier assertion/guard markers in Editor writers. |
| `round4_benchmark_report.py` | Inventory Round 4 evidence, compare route identity, or validate Round 5 DLSS mode evidence, report per-mode avg FPS/p99/GPU p99 and deltas vs TSR, and detect >5% repeated-baseline drift. |
| `check_bench_kit_manifest.py` | Check MakeBenchKit copy destinations for duplicates and missing sources. |
| `check_g2_selection_refusal_expected.py` | Check G2 expected-sheet case/token coverage in its PIE driver. |
| `check_packaged_smoke_receipt.py` | Validate captured PackagedSmoke tokens against configuration and process exit code. |
| `check_ue_python_enum_conventions.py` | Audit confirmed UENUM name/member conventions and integer coercion patterns. |
| `inventory_editor_asset_writers.py` | Classify Editor scripts as creators, modifiers, map setup, or read-only. |
| `validate_a5_receipt_directory.py` | Check expected A5 pair IDs and legacy/data receipt arms. |
| `card_table.py` | Card timing and baked sample count table from JSON. |
| `check_doc_links.py` | Broken relative Markdown link scan. |
| `check_evidence_sha256.py` | Verify Claude evidence hash manifests. |
| `check_headers_selfcontained.py` | Heuristic header include suspects; not standalone compilation. |
| `check_ki_references.py` | Source KI references against KNOWN_ISSUES.md. |
| `check_line_endings.py` | Mixed CRLF/LF and lone-CR text files. |
| `check_mailbox_ids.py` | Mailbox sequence/duplicate header IDs. |
| `check_move_card_ids.py` | Duplicate MoveId values across JSON card exports. |
| `check_shipping_guards.py` | Actual console variable registrations outside Shipping guards. |
| `check_test_plan_ids.py` | Duplicate/out-of-order BUILD rows. |
| `CheckDocLineCounts.ps1` | Ensure changed tracked Markdown documents have not shrunk relative to HEAD; used by `Scripts/Gate.ps1`. |
| `compare_framework_tokens.py` | FrameworkProof token count delta between logs. |
| `compare_parry_runs.py` | Compare two parry proof runs without timestamps. |
| `diff_manifests.py` | Added/removed/changed paths between SHA-256 manifests. |
| `detect_duplicate_pie_runs.py` | Find byte-identical Unreal run chunks in concatenated raw logs; retain source line boundaries. |
| `evidence_pack.py` | Copy a raw log and optional before/after states; write hash manifests. |
| `verify_evidence_manifest.py` | Read-only verification of JSON evidence paths, sizes, and SHA-256 hashes. |
| `proof_report.py` | Compare telemetry presence with EXPECTED.md; paired negative-control logs, optional map/profile/run identity checks, input path/mtime/hash, and manifest freshness. |
| `lint_expected_sheets.py` | Registered telemetry token and Setup/Control/PASS/FAIL structure checks. |
| `audit_tool_index.py` | Check indexed script existence and CLI `--help` support. |
| `audit_pie_command.py` | Compare captured command arguments with structured requirements in a proof expected sheet. |
| `asset_provenance.py` | Read authoring-script source/destination asset declarations and find matching evidence-log references; never changes assets. |
| `suite_log_report.py` | Summarize Unreal automation completion lines; requires terminal success marker unless `--allow-partial` is explicit. |
| `test_gate_script.py` | Contract tests for Gate.ps1 step order, editor refusal and dry-run behavior. |
| `test_audit_source_test_coverage.py` | Fixture tests for the source/test gap inventory heuristic. |
| `test_memory_soak_driver.py` | Offline syntax/contract tests for the opt-in U-C05 PIE memory soak driver. |
| `diff_a5_nightly_reports.py` | Compare two complete 31-pair A5 nightly Markdown reports; reject partial reports and show new failures, fixes, and count changes. |
| `summarize_memory_soak.py` | Validate and summarize two 50-reset post-GC memory-soak logs; reports counts/trends without declaring a leak. |
| `test_tier1_visual_wiring_contract.py` | Source contract for opt-in Tier 1 Niagara event wiring, defaults, and Shipping CVar guards. |
| `diff_suite_logs.py` | Compare two automation suite logs; reports incomplete inputs as `PARTIAL` (exit 3). |
| `evidence_summary.py` | CSV index of retained editor logs with identity, date, outcome, validator status, and SHA-256. |
| `framework_results.py` | Parse FrameworkProof RESULT lines. |
| `list_automation_tests.py` | Automation registration names and locations. |
| `list_cvars.py` | Actual `rpg.*` registrations, including perf macro expansions. |
| `list_todo_markers.py` | TODO/FIXME/XXX markers in owned code/docs. |
| `log_failures.py` | Error/fatal/failure-like Unreal log lines for manual context review. |
| `mailbox_stats.py` | TEAM_MAILBOX message counts by party and date. |
| `make_source_manifest.py` | SHA-256 snapshot of Source files. |
| `plot_framework_timeline.py` | Text timeline of FrameworkProof events. |
| `plugin_dependencies.py` | Project-enabled plugins and local descriptor dependencies. |
| `profile_dump.py` | Flatten nested profile JSON into field/value rows. |
| `retired_source_names.py` | Occurrences of selected legacy identifiers; not a verdict. |
| `source_metrics.py` | File/line/test counts by folder. |
| `summarize_framework_log.py` | Per-token, outcome and per-card proof log summary. |
| `token_coverage.py` | Compare schema tokens with evidence logs; optionally emit first-real-sample path/line manifest. |
| `validate_baked_cards.py` | Baked sample time/coordinate sanity on card JSON. |

Reports can contain heuristic suspects. Read the code/context before treating a match as a defect; these tools do not replace builds, automation tests, PIE evidence, or owner review.

## Additional maintained CLIs

These are also maintained under this folder and are covered by [`CLI_AUTHOR_GUIDE_S154.md`](CLI_AUTHOR_GUIDE_S154.md):

- `audit_framework_schemas.py`
- `check_validator_tokens.py`
- `new_profile_field_scaffold.py`
- `new_rule_scaffold.py`

The complete input, output, deliberate exit status, and side-effect contract for all 43 CLI tools is in [`CLI_AUTHOR_GUIDE_S154.md`](CLI_AUTHOR_GUIDE_S154.md).
