# Offline Boss Review Tools

The source-only Shipping symbol risk scan for test-named declarations is recorded in [SHIPPING_SYMBOL_RISK_AUDIT_S182.md](SHIPPING_SYMBOL_RISK_AUDIT_S182.md); suspected visibility is not binary proof.

The packaged-content check's static-reference scope and named missing-entry fixture are recorded in [PACKAGED_CONTENT_CHECKLIST_AUDIT_S183.md](PACKAGED_CONTENT_CHECKLIST_AUDIT_S183.md).

The Rebuild wrapper's compiler/test exit propagation and log-path handling are recorded in [BUILD_FAILURE_PROPAGATION_AUDIT_S184.md](BUILD_FAILURE_PROPAGATION_AUDIT_S184.md).

The PIE driver timeout, zero-check, and failed-check exit paths are reviewed in [DRIVER_FAILURE_PROPAGATION_AUDIT_S185.md](DRIVER_FAILURE_PROPAGATION_AUDIT_S185.md).

Editor/staging lock diagnosis and PID-scoped process-tree cleanup are documented in the [Gate 4 runbook](../GATE4_RUNBOOK.md#editor-and-staging-locks); `Rebuild.ps1` now targets this checkout's editor processes only.

The S186 source review of editor and staged-game process ownership is recorded in [STALE_PROCESS_LOCK_RUNBOOK_AUDIT_S186.md](STALE_PROCESS_LOCK_RUNBOOK_AUDIT_S186.md).

Source/build/run hash freshness rules for handovers are in [EVIDENCE_HASH_REFRESH_CHECKLIST_S187.md](EVIDENCE_HASH_REFRESH_CHECKLIST_S187.md).

Required code, test, live, and packaged evidence before claiming a profile option release-proven is defined in [FEATURE_PROOF_RELEASE_GATE_S188.md](FEATURE_PROOF_RELEASE_GATE_S188.md).

Profile opt-in defaults and lane/group validation are cross-checked in [OPT_IN_DEFAULT_OFF_AUDIT_S189.md](OPT_IN_DEFAULT_OFF_AUDIT_S189.md); its F3/F4/F5 regression assertions await Lead execution.

Owner-independent boundaries for Queue C closeout and the next queue are recorded in [OWNER_INDEPENDENT_TASK_AUDIT_S190.md](OWNER_INDEPENDENT_TASK_AUDIT_S190.md).

The five-task Lead review receipt format, including verdict and hotfix tracking, is in [QUEUE_C_REVIEW_RECEIPT_TEMPLATE_S191.md](QUEUE_C_REVIEW_RECEIPT_TEMPLATE_S191.md).

The exact intake, isolation, verification, and re-review flow for rejected/partial tasks is in [LEAD_HOTFIX_INTAKE_GUIDE_S192.md](LEAD_HOTFIX_INTAKE_GUIDE_S192.md).

The current Queue C read order, active position, evidence limits, and owner/Lead boundary are recorded in [QUEUE_200_C_HANDOVER_S193.md](QUEUE_200_C_HANDOVER_S193.md).
Queue B and later task deliverables, owners, purposes, and review/build states are inventoried in [QUEUE_ARTIFACT_INVENTORY_S194.md](QUEUE_ARTIFACT_INVENTORY_S194.md).
Open Codex findings, Lead dispositions, next actions, and retained limits are tracked in [OPEN_CODEX_FINDINGS_DISPOSITION_S195.md](OPEN_CODEX_FINDINGS_DISPOSITION_S195.md).
The first ten Queue C submissions and their current suite/evidence boundaries are assembled in [QUEUE_C_MIDPOINT_REVIEW_PACKAGE_S196.md](QUEUE_C_MIDPOINT_REVIEW_PACKAGE_S196.md).
Per-task Queue C verdicts and pending review items are tracked in [QUEUE_C_FINAL_REVIEW_PACKAGE_S197.md](QUEUE_C_FINAL_REVIEW_PACKAGE_S197.md); it remains open until the Lead fills the pending dispositions.
Task counts for the active S163–S200 continuation, with no implicit acceptance, are in [QUEUE_C_STATUS_DASHBOARD_S198.md](QUEUE_C_STATUS_DASHBOARD_S198.md).
Cross-queue overlaps, reasons to retain/merge them, and C-734's next-queue themes are compared in [QUEUE_C_NEXT_QUEUE_DELTA_S199.md](QUEUE_C_NEXT_QUEUE_DELTA_S199.md).
Queue C's final evidence/count reconciliation and current checkout verification boundary are in [QUEUE_C_FINAL_CONSISTENCY_S200.md](QUEUE_C_FINAL_CONSISTENCY_S200.md).
The active Queue D proposal and its ranked 200 tasks are in [QUEUE_200_D_PROPOSAL.md](QUEUE_200_D_PROPOSAL.md); D1's current selector/start parity map is [SELECTOR_START_PARITY_D1.md](SELECTOR_START_PARITY_D1.md).
D2's field-by-field snapshot/test coverage and wrapper fixture boundaries are in [SELECTOR_START_SNAPSHOT_GAP_D2.md](SELECTOR_START_SNAPSHOT_GAP_D2.md).
D3's proposed cone-slack boundary and start-route tests are in [CONE_SLACK_START_ROUTE_TEST_PLAN_D3.md](CONE_SLACK_START_ROUTE_TEST_PLAN_D3.md).
D4's immediate and delayed combo refusal/fallback coverage boundary is in [COMBO_FALLBACK_BOUNDARY_AUDIT_D4.md](COMBO_FALLBACK_BOUNDARY_AUDIT_D4.md).
D5's selector cooldown comparison and regression matrix are in [SELECTOR_COOLDOWN_BOUNDARY_MATRIX_D5.md](SELECTOR_COOLDOWN_BOUNDARY_MATRIX_D5.md).
D6's repeat-history and tie-seed reset lifecycle audit is in [SELECTOR_REPEAT_MEMORY_LIFECYCLE_AUDIT_D6.md](SELECTOR_REPEAT_MEMORY_LIFECYCLE_AUDIT_D6.md).
D7's seeded tie-band threshold/determinism audit is in [SELECTOR_TIE_BAND_DETERMINISM_AUDIT_D7.md](SELECTOR_TIE_BAND_DETERMINISM_AUDIT_D7.md).
D8's executor refusal order and potential member-state mutation are in [EXECUTOR_INVALID_START_REFUSAL_AUDIT_D8.md](EXECUTOR_INVALID_START_REFUSAL_AUDIT_D8.md).
D9's generation reset/recovery ordering and component-wrapper test boundary are in [EXECUTOR_GENERATION_RESET_AUDIT_D9.md](EXECUTOR_GENERATION_RESET_AUDIT_D9.md).
D10's encounter attack-count boundaries and actor-loop coverage gap are in [ENCOUNTER_ATTACK_BUDGET_BOUNDARY_AUDIT_D10.md](ENCOUNTER_ATTACK_BUDGET_BOUNDARY_AUDIT_D10.md).

These scripts inspect local source or logs. They do not launch Unreal or modify game assets.

The path and flag audit for the active continuation handover is recorded in [HANDOVER_LINK_AUDIT_S160.md](HANDOVER_LINK_AUDIT_S160.md).

The editor-script asset deletion scan and its reference-safety limits are recorded in [EDITOR_ASSET_DELETION_AUDIT_S161.md](EDITOR_ASSET_DELETION_AUDIT_S161.md).

Asset import/create collision policies are mapped in [EDITOR_ASSET_OVERWRITE_AUDIT_S162.md](EDITOR_ASSET_OVERWRITE_AUDIT_S162.md).

World load/create/save paths and the `sevarog_pack_04_level.py` destination mismatch are recorded in [EDITOR_MAP_SAVE_AUDIT_S163.md](EDITOR_MAP_SAVE_AUDIT_S163.md).

Literal editor `set_editor_property` names and the unverified names needing reflection/content readback are inventoried in [EDITOR_PROPERTY_NAME_AUDIT_S164.md](EDITOR_PROPERTY_NAME_AUDIT_S164.md).

Boolean editor property spellings are compared with project and UE 5.5 declarations in [EDITOR_BOOLEAN_PROPERTY_AUDIT_S165.md](EDITOR_BOOLEAN_PROPERTY_AUDIT_S165.md).

Former-user absolute paths in editor scripts and repo-relative alternatives are listed in [EDITOR_ABSOLUTE_PATH_AUDIT_S166.md](EDITOR_ABSOLUTE_PATH_AUDIT_S166.md).

The non-executing Python parse inventory and exact syntax failures are in [PYTHON_SYNTAX_INVENTORY_S167.md](PYTHON_SYNTAX_INVENTORY_S167.md).

PowerShell parse status and native child-process exit-code gaps are recorded in [POWERSHELL_PARSE_AND_EXIT_AUDIT_S168.md](POWERSHELL_PARSE_AND_EXIT_AUDIT_S168.md).

Python subprocess and editor-wrapper exit propagation findings are recorded in [SUBPROCESS_EXIT_CODE_AUDIT_S169.md](SUBPROCESS_EXIT_CODE_AUDIT_S169.md).

Windows path resolution and the isolated spaces/separators/Unicode fixture are documented in [PATH_NORMALIZATION_AUDIT_S170.md](PATH_NORMALIZATION_AUDIT_S170.md).

Atomic publication of offline tool manifests/reports and its failure-injection fixture are documented in [JSON_WRITE_ATOMICITY_AUDIT_S171.md](JSON_WRITE_ATOMICITY_AUDIT_S171.md).

Scratch-root cleanup and legacy scripts that remove shared files are audited in [TEMP_DIRECTORY_CLEANUP_AUDIT_S172.md](TEMP_DIRECTORY_CLEANUP_AUDIT_S172.md).

Required CLI inputs, malformed-file diagnostics, and side-effect ordering are reviewed in [CLI_INPUT_VALIDATION_AUDIT_S173.md](CLI_INPUT_VALIDATION_AUDIT_S173.md).

The offline tool network scan found only URL parsing, with no network requests; see [OFFLINE_TOOL_NETWORK_AUDIT_S174.md](OFFLINE_TOOL_NETWORK_AUDIT_S174.md).

Top-level Python utility imports were statically checked for editor, filesystem, and process side effects in [SCRIPT_IMPORT_SIDE_EFFECT_AUDIT_S175.md](SCRIPT_IMPORT_SIDE_EFFECT_AUDIT_S175.md).

Repeated pure-temp output comparisons for four offline CLIs are recorded in [DETERMINISTIC_TOOL_OUTPUT_AUDIT_S176.md](DETERMINISTIC_TOOL_OUTPUT_AUDIT_S176.md).

Absolute-path and raw-line exposure in local CLI reports is reviewed in [REPORT_REDACTION_AUDIT_S177.md](REPORT_REDACTION_AUDIT_S177.md).

Generated rule scaffold license, module-path, and proof-caveat conventions are checked in [SCAFFOLD_HEADER_AUDIT_S178.md](SCAFFOLD_HEADER_AUDIT_S178.md).

Documented command examples and their `--help` support are checked in [TOOL_USAGE_CONSISTENCY_AUDIT_S179.md](TOOL_USAGE_CONSISTENCY_AUDIT_S179.md).

- Per-instance telemetry summary: `py Scripts/Tools/summarize_framework_log.py path/to/editor_raw.log`.
- Text timeline for a PIE log: `py Scripts/Tools/plot_framework_timeline.py path/to/editor_raw.log --limit 300`.
- Seen versus registered telemetry tokens: `py Scripts/Tools/token_coverage.py --root .` (optional explicit log paths narrow the scan).
- Duplicate Unreal run chunks: `py Scripts/Tools/detect_duplicate_pie_runs.py path/to/combined.log`; reports byte-identical engine-start-to-next-start/end chunks with original line boundaries (exit 1 on duplicates, 2 on missing input/run marker).
- Evidence summary CSV: `py Scripts/Tools/evidence_summary.py --root . --output Documentation/Boss/FRAMEWORK_EVIDENCE_SUMMARY_S138.csv`; one row per retained `editor_raw.log`, with map/profile as `unknown` when no identity fields are present, timestamp, last outcome, schema/semantic validation status, and SHA-256.
- Audit recorded PIE arguments: `py Scripts/Tools/audit_pie_command.py path/to/command.json path/to/FEATURE_EXPECTED.md`; expected sheets may include a fenced `command-requirements` JSON block with `required_args`, `required_cvars`, and exact `allowed_exec_cmds`. Missing inline requirements and unlisted `-ExecCmds`/known mutation switches fail. CVars applied inside a referenced Python driver are not proven by `command.json`; declare them separately in driver evidence.
- Asset provenance report: `py Scripts/Tools/asset_provenance.py path/to/create_content.py --evidence path/to/content_run/editor_raw.log`; shows statically declared source and destination path variables, literal `/Game/...` references, and matching evidence lines. Dynamic/unattributed sources are shown as unknown; the report is read-only and never edits assets.
- Source/test counts by top-level module: `py Scripts/Tools/source_metrics.py --root .`.
- Static header include suspects: `py Scripts/Tools/check_headers_selfcontained.py --root .`; this is a heuristic report, not a standalone compile.
- Mixed line endings: `py Scripts/Tools/check_line_endings.py --root .` (project source, scripts, docs, and config text).
- Shipping guard suspects: `py Scripts/Tools/check_shipping_guards.py --root .` (static heuristic for console-variable registration and `ForTest` declarations/definitions).
- TODO/FIXME/XXX markers: `py Scripts/Tools/list_todo_markers.py .` (Source, Scripts, and Documentation; skips vendored/generated/archive trees).
- Source KI references: `py Scripts/Tools/check_ki_references.py --root .` (checks C++ mentions against `KNOWN_ISSUES.md`).
- BUILD row IDs: `py Scripts/Tools/check_test_plan_ids.py --root .` (reports duplicate or unsorted BUILD rows in `TEST_PLAN.md`).
- Evidence bundle: `py Scripts/Tools/evidence_pack.py editor_raw.log out/evidence --pre-state before.json --post-state after.json` (copies inputs and writes SHA-256 manifest files).
- Source manifest delta: `py Scripts/Tools/diff_manifests.py before_source_sha256.txt after_source_sha256.txt`.
- Profile JSON table: `py Scripts/Tools/profile_dump.py profile_export.json` (recursive flattened field/value listing).
- Baked card timings: `py Scripts/Tools/card_table.py baked_cards.json` (reads card export JSON, including per-window baked sample counts).
- Mailbox counts: `py Scripts/Tools/mailbox_stats.py Documentation/TEAM_MAILBOX.md` (messages per party code and day).
- Unreal log failures: `py Scripts/Tools/log_failures.py path/to/build_raw.log --limit 100` (line-numbered keyword matches; inspect context before treating matches as build failures).
- CVar references: `py Scripts/Tools/list_cvars.py --root .` (project `rpg.*` mentions in C++ and config).
- Plugin declarations: `py Scripts/Tools/plugin_dependencies.py --root .` (project plugin enables and project-local descriptor dependencies).
- Legacy source names: `py Scripts/Tools/retired_source_names.py --root .` (occurrence list for selected legacy implementation/pack identifiers; not a verdict).
- Automation registrations: `py Scripts/Tools/list_automation_tests.py --root .` (test macro names and source lines).
- FrameworkProof token delta: `py Scripts/Tools/compare_framework_tokens.py before.log after.log`.
- Baked trajectory sanity: `py Scripts/Tools/validate_baked_cards.py card_export.json` (finite 3D points and strictly increasing in-window times).
- Duplicate move IDs: `py Scripts/Tools/check_move_card_ids.py export_a.json export_b.json`.
- FrameworkProof results: `py Scripts/Tools/framework_results.py editor_raw.log` (line-numbered RESULT key/value fields).
- FrameworkProof RESULT validation and generation association: the same command identifies malformed/missing fields, repeated RESULT rows, and explicit unknown generation labels; nonnegative integer counter fields are checked.
- Unreal automation suite summary: `py Scripts/Tools/suite_log_report.py tests_raw.log --json` emits stable JSON totals, failure identities, duplicate identities, line-numbered test rows, and completion-marker status. Missing `TEST COMPLETE. EXIT CODE: 0` exits 2 by default; `--allow-partial` is for intentional partial reads and cannot certify a pass.
- Suite comparison: `py Scripts/Tools/diff_suite_logs.py before.log after.log` reports added/removed/changed tests (exit 0 identical complete logs, 1 changed complete logs, 2 invalid/no-row input, 3 when either log lacks the terminal success marker; prints `PARTIAL`).
- Verify one evidence bundle: `py Scripts/Tools/verify_evidence_manifest.py out/evidence/evidence_manifest.json` checks listed paths and SHA-256 without changing files. For a complete Queue L pack, add `--require-bytes --verify-source-references --strict-membership` to require byte counts, reject unlisted payload files, and verify JSON `source_log` references stay inside the pack, are listed, and match their hashes.
- Proof report: `py Scripts/Tools/proof_report.py enabled_editor_raw.log FEATURE_EXPECTED.md --control-log control_editor_raw.log --expect-map L_Proof --expect-profile DA_Proof --expect-run-id run-01 --require-complete-run --manifest out/evidence/evidence_manifest.json`; positive checklist tokens are checked against enabled evidence and `no TOKEN` assertions against the paired control. Optional expected identities compare `map=`, `profile=`, and `run_id=`/`runId=` where present; missing fields are UNKNOWN, and mismatches print before checklist rows and fail the report. `--require-complete-run` classifies missing FrameworkProof RESULT or orderly `LogExit: Exiting.` as INCOMPLETE (exit 2), distinct from gameplay FAIL. The report prints resolved input path, UTC mtime, and SHA-256. Without `--control-log`, legacy single-log semantics remain. Stale/hash-invalid evidence is separate from gameplay PASS/FAIL (exit 3 for stale evidence when gameplay checks have no harder failure).
- Framework schema sample inventory: `py Scripts/Tools/token_coverage.py --root . --samples-output Documentation/Boss/FRAMEWORK_SCHEMA_SAMPLE_BUNDLE_S133.json`; scans retained Claude logs, maps each registered token to its first real sample path/line, and labels tokens with no real occurrence instead of fabricating a sample.
- Lint proof expected sheets: `py Scripts/Tools/lint_expected_sheets.py path/to/FEATURE_EXPECTED.md` checks registered `[FrameworkProof]` token names and required Setup/Control/PASS/FAIL sections; untagged manual numeric checks remain manual.
- Audit this tool index: `py Scripts/Tools/audit_tool_index.py --root .` verifies each indexed script exists and supports `--help`.
- Source snapshot: `py Scripts/Tools/make_source_manifest.py out/source_sha256.txt --root .` (SHA-256 list suitable for `diff_manifests.py`).
- Full schema/emitter/log sample audit: `py Scripts/Tools/audit_framework_schemas.py --root .` (source and retained-log inventory; read-only).
- Documentation link audit: `py Scripts/Tools/check_doc_links.py .` (checks local relative Markdown targets; external URLs are parsed but not fetched).
- Retained evidence hash audit: `py Scripts/Tools/check_evidence_sha256.py .` (checks existing `B_*` evidence hash lists; read-only).
- Mailbox ID audit: `py Scripts/Tools/check_mailbox_ids.py Documentation/TEAM_MAILBOX.md` (checks duplicate/malformed sequence IDs; read-only).
- Validator token audit: `py Scripts/Tools/check_validator_tokens.py --root .` (compares emitters, schemas, and both token indexes; read-only).
- Parry run comparison: `py Scripts/Tools/compare_parry_runs.py before.log after.log` (two log inputs; report-only).
- Profile-field checklist: `py Scripts/Tools/new_profile_field_scaffold.py --field ExampleField` (prints a checklist; writes no files).
- Rule scaffold generator: `py Scripts/Tools/new_rule_scaffold.py --name Example --requirement-id BOSS-EXAMPLE-001 --slug example --output-root <empty-temporary-root>` (creates three files; use an empty temporary root, not the project tree).

Queue D D15's normal/combo selector-memory route comparison is in [SELECTOR_MEMORY_COMBO_START_AUDIT_D15.md](SELECTOR_MEMORY_COMBO_START_AUDIT_D15.md).

Queue D D16's no-run pack-boss arena parry driver contract is in [PACK_BOSS_ARENA_PARRY_DRIVER_CONTRACT_D16.md](PACK_BOSS_ARENA_PARRY_DRIVER_CONTRACT_D16.md).

Queue D D17's parry timing boundary/source-test map is in [PARRY_TIMING_BOUNDARY_AUDIT_D17.md](PARRY_TIMING_BOUNDARY_AUDIT_D17.md).

Queue D D18's parry cooldown-edge and state-mutation audit is in [PARRY_COOLDOWN_EDGE_AUDIT_D18.md](PARRY_COOLDOWN_EDGE_AUDIT_D18.md).

Queue D D19's parry stamina-cost and insufficient-input audit is in [PARRY_STAMINA_COST_BOUNDARY_AUDIT_D19.md](PARRY_STAMINA_COST_BOUNDARY_AUDIT_D19.md).

Queue D D20's parry-grade transition and feedback-consumer map is in [PARRY_GRADE_FEEDBACK_AUDIT_D20.md](PARRY_GRADE_FEEDBACK_AUDIT_D20.md).

Queue D D21's duplicate-contact/one-shot parry resolution audit is in [PARRY_DUPLICATE_CONTACT_SUPPRESSION_AUDIT_D21.md](PARRY_DUPLICATE_CONTACT_SUPPRESSION_AUDIT_D21.md).

Queue D D22's resolver target and self/friendly filter map is in [PARRY_TARGET_FILTER_AUDIT_D22.md](PARRY_TARGET_FILTER_AUDIT_D22.md).

Queue D D23's parry-recovery timing, combo, and stagger-order audit is in [PARRY_RECOVERY_ORDER_AUDIT_D23.md](PARRY_RECOVERY_ORDER_AUDIT_D23.md).

Queue D D24's parry visual/sound implementation inventory is in [PARRY_PRESENTATION_INVENTORY_D24.md](PARRY_PRESENTATION_INVENTORY_D24.md).

Queue D D25's parry feedback event fan-out map is in [PARRY_FEEDBACK_FANOUT_AUDIT_D25.md](PARRY_FEEDBACK_FANOUT_AUDIT_D25.md).

Queue D D26's player parry input bind/retry/teardown audit is in [PLAYER_PARRY_INPUT_BINDING_AUDIT_D26.md](PLAYER_PARRY_INPUT_BINDING_AUDIT_D26.md).

Queue D D27's player stamina spend/refund inventory is in [PLAYER_STAMINA_SPEND_REFUND_AUDIT_D27.md](PLAYER_STAMINA_SPEND_REFUND_AUDIT_D27.md).

Queue D D28's player dodge-invulnerability/parry overlap map is in [PLAYER_DAMAGE_IMMUNITY_OVERLAP_AUDIT_D28.md](PLAYER_DAMAGE_IMMUNITY_OVERLAP_AUDIT_D28.md).

Queue D D29's player death/unpossess during-parry lifecycle map is in [PLAYER_DEATH_DURING_PARRY_AUDIT_D29.md](PLAYER_DEATH_DURING_PARRY_AUDIT_D29.md).

Queue D D30's parry telemetry schema/emitter cross-check is in [PARRY_TELEMETRY_SCHEMA_AUDIT_D30.md](PARRY_TELEMETRY_SCHEMA_AUDIT_D30.md).

Queue D D31's pack melee parry driver source audit is in [PACK_MELEE_PARRY_DRIVER_SOURCE_AUDIT_D31.md](PACK_MELEE_PARRY_DRIVER_SOURCE_AUDIT_D31.md).

Queue D D32's paired pack-arena parry proof sheet is in [PACK_ARENA_PARRY_EXPECTED_D32.md](PACK_ARENA_PARRY_EXPECTED_D32.md).

Queue D D33's gap-closer source/asset inventory is in [GAP_CLOSER_ANIMATION_ASSET_INVENTORY_D33.md](GAP_CLOSER_ANIMATION_ASSET_INVENTORY_D33.md).

Queue D D34's gap-closer timing/motion boundary audit is in [GAP_CLOSER_TIMING_MOTION_AUDIT_D34.md](GAP_CLOSER_TIMING_MOTION_AUDIT_D34.md).

Queue D D35's gap-closer proof token audit is in [GAP_CLOSER_PROOF_TELEMETRY_AUDIT_D35.md](GAP_CLOSER_PROOF_TELEMETRY_AUDIT_D35.md).

Queue D D36's strafe-stuck geometry and evidence audit is in [STRAFE_STUCK_PROOF_GEOMETRY_AUDIT_D36.md](STRAFE_STUCK_PROOF_GEOMETRY_AUDIT_D36.md).

Queue D D37's detector-edge coverage audit is in [STRAFE_STUCK_DETECTOR_EDGE_AUDIT_D37.md](STRAFE_STUCK_DETECTOR_EDGE_AUDIT_D37.md).

Queue D D38's reposition-turn latch test audit is in [REPOSITION_TURN_LATCH_TEST_AUDIT_D38.md](REPOSITION_TURN_LATCH_TEST_AUDIT_D38.md).

Queue D D39's reposition budget source audit is in [REPOSITION_BUDGET_SOURCE_AUDIT_D39.md](REPOSITION_BUDGET_SOURCE_AUDIT_D39.md).

Queue D D40's arena-leash boundary evidence audit is in [ARENA_LEASH_BOUNDARY_PROOF_AUDIT_D40.md](ARENA_LEASH_BOUNDARY_PROOF_AUDIT_D40.md).

Queue D D41's LOS memory lifecycle audit is in [LOS_MEMORY_LIFECYCLE_AUDIT_D41.md](LOS_MEMORY_LIFECYCLE_AUDIT_D41.md).

Queue D D42's LOS proof-token audit is in [LOS_PROOF_SHEET_TOKEN_AUDIT_D42.md](LOS_PROOF_SHEET_TOKEN_AUDIT_D42.md).

Queue D D43's yaw-probe endpoint/wrap audit is in [YAW_PROBE_BOUNDARY_AUDIT_D43.md](YAW_PROBE_BOUNDARY_AUDIT_D43.md).

Queue D D44's turn-rate ramp coverage audit is in [TURN_RATE_RAMP_TEST_AUDIT_D44.md](TURN_RATE_RAMP_TEST_AUDIT_D44.md).

Queue D D45's move-card warp-curve edge audit is in [MOVE_CARD_WARP_CURVE_EDGE_AUDIT_D45.md](MOVE_CARD_WARP_CURVE_EDGE_AUDIT_D45.md).

Queue D D38's reposition-turn latch test audit is in [REPOSITION_TURN_LATCH_TEST_AUDIT_D38.md](REPOSITION_TURN_LATCH_TEST_AUDIT_D38.md).

The complete 43-command inventory and support-file exclusions are recorded in [OFFLINE_TOOL_INVENTORY_AUDIT_S180.md](OFFLINE_TOOL_INVENTORY_AUDIT_S180.md).

Test/proof CVar Shipping guards and the refreshed 45-registration inventory are recorded in [SHIPPING_GUARD_INVENTORY_AUDIT_S181.md](SHIPPING_GUARD_INVENTORY_AUDIT_S181.md).

The maintained CLI input/output, deliberate exit-status, and side-effect contracts for every script under `Scripts/Tools/` are indexed in [`Scripts/Tools/CLI_AUTHOR_GUIDE_S154.md`](../../Scripts/Tools/CLI_AUTHOR_GUIDE_S154.md). The script-directory README lists all maintained commands; `test_*.py` files are test modules, not user-facing CLIs.

Queue D D46's baked trajectory freshness boundary between structural validation, path guard, point-drift verifier, and unwired fingerprint comparison is audited in [BAKED_TRAJECTORY_FRESHNESS_AUDIT_D46.md](BAKED_TRAJECTORY_FRESHNESS_AUDIT_D46.md).

Queue D D47's validator endpoint mutations and runtime baked-pose interpolation coverage boundary are in [BAKED_SAMPLE_ENDPOINT_MUTATION_AUDIT_D47.md](BAKED_SAMPLE_ENDPOINT_MUTATION_AUDIT_D47.md).

Queue D D48's card hold/warp boundary-to-consumer matrix is in [MOVE_CARD_HOLD_WARP_TIMING_MATRIX_D48.md](MOVE_CARD_HOLD_WARP_TIMING_MATRIX_D48.md).

Queue D D49's strafe-resume predicate examples, missing deterministic property generator, and unwired-caller boundary are recorded in [STRAFE_RESUME_PROPERTY_TEST_AUDIT_D49.md](STRAFE_RESUME_PROPERTY_TEST_AUDIT_D49.md).

Queue D D50's approach-driver timeout, movement, bridge-status, and log-retention contract audit is in [BOSS_APPROACH_DRIVER_FAILURE_CONTRACT_AUDIT_D50.md](BOSS_APPROACH_DRIVER_FAILURE_CONTRACT_AUDIT_D50.md).

Queue D D51's Framework RESULT parser requiredness, numeric fields, duplicates, unknown labels, and completeness boundary are audited in [FRAMEWORK_RESULT_PARSER_CONTRACT_AUDIT_D51.md](FRAMEWORK_RESULT_PARSER_CONTRACT_AUDIT_D51.md).

Queue D D52 re-ran the token/schema/index and retained-sample audits; results and stale census reconciliation are in [FRAMEWORK_VALIDATOR_TOKEN_INDEX_CROSSCHECK_D52.md](FRAMEWORK_VALIDATOR_TOKEN_INDEX_CROSSCHECK_D52.md).

Queue D D53 verified every retained sample path/line against the current validator and preserved five explicit no-sample entries; see [FRAMEWORK_PROOF_SAMPLE_PATH_FRESHNESS_AUDIT_D53.md](FRAMEWORK_PROOF_SAMPLE_PATH_FRESHNESS_AUDIT_D53.md).

Queue D D54's evidence-manifest traversal, resolved-path containment, duplicate, and fixture coverage limits are in [EVIDENCE_MANIFEST_PATH_SAFETY_TEST_AUDIT_D54.md](EVIDENCE_MANIFEST_PATH_SAFETY_TEST_AUDIT_D54.md).

Queue D D55's failure-injected per-file manifest write behavior and evidence-pack partial-publication limit are audited in [EVIDENCE_MANIFEST_ATOMIC_WRITE_AUDIT_D55.md](EVIDENCE_MANIFEST_ATOMIC_WRITE_AUDIT_D55.md).

Queue D D56's positive/control token routing, legacy behavior, and proof-report exit precedence are in [PROOF_REPORT_PAIRED_CONTROL_BOUNDARY_AUDIT_D56.md](PROOF_REPORT_PAIRED_CONTROL_BOUNDARY_AUDIT_D56.md).

Queue D D57's proof-report map/profile/run ID extraction and its missing/mismatch/control-log boundaries are in [PROOF_REPORT_IDENTITY_FIELD_AUDIT_D57.md](PROOF_REPORT_IDENTITY_FIELD_AUDIT_D57.md).

Queue D D58's optional terminal RESULT/orderly-exit requirement and status distinction are in [PROOF_REPORT_COMPLETE_RUN_AUDIT_D58.md](PROOF_REPORT_COMPLETE_RUN_AUDIT_D58.md).

Queue D D59's suite-summary versus suite-diff duplicate identity behavior is in [SUITE_LOG_DUPLICATE_IDENTITY_AUDIT_D59.md](SUITE_LOG_DUPLICATE_IDENTITY_AUDIT_D59.md).

Queue D D60's suite-diff empty, partial, duplicate, identical, and changed result classifications are in [SUITE_DIFF_CLASSIFICATION_AUDIT_D60.md](SUITE_DIFF_CLASSIFICATION_AUDIT_D60.md).

Queue D D61's Source-only manifest inclusion/exclusion boundary and operational caveats are in [SOURCE_MANIFEST_SCOPE_AUDIT_D61.md](SOURCE_MANIFEST_SCOPE_AUDIT_D61.md).

Queue D D62's read-only retained evidence hash inventory and its listed-file-only boundary are in [RETAINED_EVIDENCE_HASH_INVENTORY_AUDIT_D62.md](RETAINED_EVIDENCE_HASH_INVENTORY_AUDIT_D62.md).

Queue D D63's mailbox ID checker gap/duplicate, malformed-header, and ordering behavior is audited in [MAILBOX_ID_CHECKER_FIXTURE_AUDIT_D63.md](MAILBOX_ID_CHECKER_FIXTURE_AUDIT_D63.md).

Queue D D64's temporary-root link checker fixtures and the path-only/no-network boundary are recorded in [DOC_LINK_CHECKER_FIXTURE_AUDIT_D64.md](DOC_LINK_CHECKER_FIXTURE_AUDIT_D64.md).

Queue D D65's expected-sheet linter negative cases and exact CLI diagnostics are recorded in [EXPECTED_SHEET_LINTER_NEGATIVE_FIXTURES_D65.md](EXPECTED_SHEET_LINTER_NEGATIVE_FIXTURES_D65.md).

Claude's C-752 duplicate-identity/truncated-suite-log disposition is implemented and verified in [QUEUE_D_SUITE_LOG_HOTFIX.md](QUEUE_D_SUITE_LOG_HOTFIX.md).

Queue D D66's source-derived 43-tool argument/default synopsis, checked against each CLI's `--help`, is in [CLI_ARGUMENT_INDEX_D66.md](CLI_ARGUMENT_INDEX_D66.md).

Queue D D67's source exit-path cross-check and three corrected S154 rows are in [CLI_EXIT_CONTRACT_AUDIT_D67.md](CLI_EXIT_CONTRACT_AUDIT_D67.md).

Queue D D68's source-level write-boundary and per-file atomic publication audit is in [OFFLINE_TOOL_WRITE_BOUNDARY_AUDIT_D68.md](OFFLINE_TOOL_WRITE_BOUNDARY_AUDIT_D68.md).

Queue D D69's repeated temp-fixture output comparison for source manifests, suite JSON, and evidence packs is in [OFFLINE_TOOL_DETERMINISM_SAMPLE_D69.md](OFFLINE_TOOL_DETERMINISM_SAMPLE_D69.md).

Queue D D70's Windows/UTF-8 temporary-path fixture coverage and end-to-end limits are in [OFFLINE_TOOL_UNICODE_PATH_FIXTURES_D70.md](OFFLINE_TOOL_UNICODE_PATH_FIXTURES_D70.md).

Queue D D71's injected denied-publication, temp cleanup, and multi-file partial-output boundaries are in [OFFLINE_TOOL_PERMISSION_ERROR_AUDIT_D71.md](OFFLINE_TOOL_PERMISSION_ERROR_AUDIT_D71.md).

Queue D D72's source-level complexity and bounded-input assumptions are in [OFFLINE_TOOL_COMPLEXITY_REVIEW_D72.md](OFFLINE_TOOL_COMPLEXITY_REVIEW_D72.md); no benchmark was run.

Queue D D73's 43-tool module-load probe and static import-side-effect audit are in [OFFLINE_TOOL_IMPORT_SAFETY_AUDIT_D73.md](OFFLINE_TOOL_IMPORT_SAFETY_AUDIT_D73.md).

Queue D D74's standard-library/local-module inventory and Python 3.10 compatibility floor are in [OFFLINE_TOOL_DEPENDENCY_INVENTORY_D74.md](OFFLINE_TOOL_DEPENDENCY_INVENTORY_D74.md).

Queue D D75's PowerShell wrapper exit propagation changes and isolated native-exit mock are in [POWERSHELL_WRAPPER_EXIT_FIXTURE_AUDIT_D75.md](POWERSHELL_WRAPPER_EXIT_FIXTURE_AUDIT_D75.md).

Queue D D76's Rebuild wrapper/test raw-log naming and overwrite-risk trace is in [REBUILD_LOG_ASSOCIATION_AUDIT_D76.md](REBUILD_LOG_ASSOCIATION_AUDIT_D76.md).

Queue D D77's Rebuild refusal for missing terminal marker, zero tests, truncated output, or failed rows is in [REBUILD_INCOMPLETE_SUITE_REFUSAL_AUDIT_D77.md](REBUILD_INCOMPLETE_SUITE_REFUSAL_AUDIT_D77.md).

Queue D D78's packaged launcher path, log lookup, Shipping fallback, and PID-tree cleanup boundaries are in [PACKAGED_SMOKE_PATH_AUDIT_D78.md](PACKAGED_SMOKE_PATH_AUDIT_D78.md).

Queue D D79's staged UFS manifest checker coverage, plugin mount roots, and generated-content exclusions are in [STAGED_CONTENT_MANIFEST_COVERAGE_AUDIT_D79.md](STAGED_CONTENT_MANIFEST_COVERAGE_AUDIT_D79.md).

Queue D D80's bounded staged Shipping binary check and narrow interpretation plan is in [SHIPPING_BINARY_CHECK_PLAN_D80.md](SHIPPING_BINARY_CHECK_PLAN_D80.md).

Queue D D81's 332-registration source inventory and complete name/location index are in [AUTOMATION_REGISTRATION_INVENTORY_AUDIT_D81.md](AUTOMATION_REGISTRATION_INVENTORY_AUDIT_D81.md) and [AUTOMATION_REGISTRATION_INDEX_D81.md](AUTOMATION_REGISTRATION_INDEX_D81.md).

Queue D D82's source-only world/object ownership and shared-state scan is in [AUTOMATION_FIXTURE_ISOLATION_AUDIT_D82.md](AUTOMATION_FIXTURE_ISOLATION_AUDIT_D82.md).

Queue D D83's fixed-seed, opaque-GUID, and clock/order dependency inventory is in [AUTOMATION_DETERMINISM_AUDIT_D83.md](AUTOMATION_DETERMINISM_AUDIT_D83.md).

Queue D D84's source-generated exact Unreal automation IDs and naming/coverage classification are in [AUTOMATION_TEST_ID_INDEX_D84.md](AUTOMATION_TEST_ID_INDEX_D84.md) and [AUTOMATION_TEST_NAMING_COVERAGE_AUDIT_D84.md](AUTOMATION_TEST_NAMING_COVERAGE_AUDIT_D84.md).

Queue D D85's PIE/editor/packaged-driver per-step and outer timeout comparison is in [DRIVER_TIMEOUT_BUDGET_AUDIT_D85.md](DRIVER_TIMEOUT_BUDGET_AUDIT_D85.md); RunDrivers' deadline begins only after the synchronous bridge wrapper returns.

Queue D D86's process ownership and termination-scope inventory is in [DRIVER_PROCESS_CLEANUP_SCOPE_AUDIT_D86.md](DRIVER_PROCESS_CLEANUP_SCOPE_AUDIT_D86.md); it flags missing descendant cleanup in RunEditorScript and unbounded/un-finalized waits in benchmark tooling.

Queue D D87's bridge startup handshake and task-result failure audit is in [DRIVER_BRIDGE_READINESS_AUDIT_D87.md](DRIVER_BRIDGE_READINESS_AUDIT_D87.md); status payloads are discarded, and the PowerShell caller does not propagate the Python runner's exit code.

Queue D D88's retained benchmark/evidence copy failure audit is in [DRIVER_EVIDENCE_COPY_FAILURE_AUDIT_D88.md](DRIVER_EVIDENCE_COPY_FAILURE_AUDIT_D88.md); BenchKit_Collect can report a success-like archive path after non-terminating copy failures.

Queue D D89's 340-file editor Python action/flag index is in [EDITOR_PYTHON_COMMAND_INVENTORY_D89.md](EDITOR_PYTHON_COMMAND_INVENTORY_D89.md) and [EDITOR_PYTHON_COMMAND_INDEX_D89.csv](EDITOR_PYTHON_COMMAND_INDEX_D89.csv); its text scan records asset/world/file operations and import replacement flags without executing scripts.

Queue D D90's editor-script dry-run control-flow review is in [EDITOR_SCRIPT_DRY_RUN_BOUNDARY_AUDIT_D90.md](EDITOR_SCRIPT_DRY_RUN_BOUNDARY_AUDIT_D90.md); only three scripts expose source-constant `DRY` gates, with no CLI-wide dry-run convention.

Queue D D91's pure-rule nonfinite and overflow scan is in [BOSS_RULE_FINITE_INPUT_AUDIT_D91.md](BOSS_RULE_FINITE_INPUT_AUDIT_D91.md); it flags an `int32` flask threshold overflow and unchecked geometry/result boundaries, with existing test limits recorded.

Queue D D92's reciprocal damage-scaler edge and nonfinite-path comparison is in [DAMAGE_SCALER_RECIPROCAL_FINITE_AUDIT_D92.md](DAMAGE_SCALER_RECIPROCAL_FINITE_AUDIT_D92.md); exact and adjacent-outside window tests exist in both directions, while nonfinite branches remain untested.

Queue D's bounded driver/evidence hotfix after C-756 is recorded in `Scripts/RunDrivers.ps1`, `RunBenchmark.ps1`, `RunPerfExperiments.ps1`, and `BenchKit_Collect.ps1`: absolute bridge startup deadline, runner exit propagation, benchmark process timeout with owned PID-tree cleanup, sampler `finally` cleanup, checked run-folder copies, summary exit check, and nonempty archive validation. PowerShell parser passed on all four files; no driver, benchmark, copy, archive, or Unreal run was performed.

Queue D D93's bleed integer/threshold boundary map is in [BLEED_RULE_INTEGER_THRESHOLD_AUDIT_D93.md](BLEED_RULE_INTEGER_THRESHOLD_AUDIT_D93.md); current repeated-hit and exact-threshold tests are distinguished from extreme finite and signed-count boundaries.

Queue D D94's pure poise-regeneration delay/ramp equation and zero-ramp fixture comparison is in [POISE_REGEN_ZERO_RAMP_AUDIT_D94.md](POISE_REGEN_ZERO_RAMP_AUDIT_D94.md); the helper has no mutable reset state, so caller lifecycle is separate.

Queue D D95's unknown phase and neutral stagger-scale fallback map is in [STAGGER_RESISTANCE_UNKNOWN_PHASE_AUDIT_D95.md](STAGGER_RESISTANCE_UNKNOWN_PHASE_AUDIT_D95.md); non-1/2 phase IDs return neutral after common scale validation, and runtime wiring remains absent.

Queue D D96's aggro-band hysteresis and threshold map is in [AGGRO_BAND_TRANSITION_BOUNDARY_AUDIT_D96.md](AGGRO_BAND_TRANSITION_BOUNDARY_AUDIT_D96.md); strict range entry/exit and asymmetric dodge-rate comparisons are cross-referenced to current tests.

Queue D D97's difficulty interpolation endpoint and invalid-input map is in [DIFFICULTY_INTERPOLATION_ENDPOINT_AUDIT_D97.md](DIFFICULTY_INTERPOLATION_ENDPOINT_AUDIT_D97.md); all three max endpoints and a seeded-free monotonic sweep are present, while adjacent scalar edges and wiring remain unproved.

Queue D D98's enrage ramp threshold and repeat-state audit is in [ENRAGE_THRESHOLD_MUTATION_AUDIT_D98.md](ENRAGE_THRESHOLD_MUTATION_AUDIT_D98.md); the pure helper recomputes from elapsed time without mutable threshold/reset state.

Queue D D99's consecutive-whiff counter and reset-trigger map is in [FATIGUE_RULE_LIFECYCLE_AUDIT_D99.md](FATIGUE_RULE_LIFECYCLE_AUDIT_D99.md); caller source resets on contact, phase transition, and encounter restart, while those stateful paths lack a focused fixture.

Queue D D100's punish count/cooldown boundary map is in [PUNISH_LIMITER_BOUNDARY_AUDIT_D100.md](PUNISH_LIMITER_BOUNDARY_AUDIT_D100.md); the counter is count-only and unwired, while the adjacent defense cooldown gate passes at exactly 3 seconds.

Queue D D101's reactive dodge state/budget audit is in [REACTIVE_DODGE_BUDGET_AUDIT_D101.md](REACTIVE_DODGE_BUDGET_AUDIT_D101.md); the pure rule has no attempt/generation state, and the arithmetic has an untested extreme int32 boundary (KI-180).

Queue D D102's retreat close-range and threat gate map is in [RETREAT_CLOSE_BOUNDARY_AUDIT_D102.md](RETREAT_CLOSE_BOUNDARY_AUDIT_D102.md); exact strict range boundary and inclusive threat threshold are covered, but vertical gating is absent from the helper API.

Queue D D103's gap-closer exit/start boundary map is in [GAP_CLOSER_EXIT_BOUNDARY_AUDIT_D103.md](GAP_CLOSER_EXIT_BOUNDARY_AUDIT_D103.md); exact threshold comparisons are covered, while adjacent representable values and actual movement endpoint behavior are not.

Queue D D104's cue-jitter deterministic sample audit is in [CUE_JITTER_SEEDED_PROPERTY_AUDIT_D104.md](CUE_JITTER_SEEDED_PROPERTY_AUDIT_D104.md); repeated seeded tuples and safe-range containment are tested, but statistical uniformity and cue association are not claimed.

Queue D D105's selector zero-weight eligibility map is in [SELECTOR_ZERO_WEIGHT_CANDIDATE_AUDIT_D105.md](SELECTOR_ZERO_WEIGHT_CANDIDATE_AUDIT_D105.md); initialization rejects zero weight, and ordinary no-eligible fallback is tested separately.

Queue D D106's selector tie ordering audit is in [SELECTOR_TIE_ORDER_DETERMINISM_AUDIT_D106.md](SELECTOR_TIE_ORDER_DETERMINISM_AUDIT_D106.md); exact ties preserve first input order at zero tie band, and seeded tiers retain input order.

Queue D D107's selector reset idempotence map is in [SELECTOR_RESET_IDEMPOTENCE_AUDIT_D107.md](SELECTOR_RESET_IDEMPOTENCE_AUDIT_D107.md); cooldown, repeat, tie-start count, and cone memory are reset while initialization remains active.

Queue D D108's executor open-window cleanup map is in [EXECUTOR_OPEN_WINDOW_CLEANUP_AUDIT_D108.md](EXECUTOR_OPEN_WINDOW_CLEANUP_AUDIT_D108.md); model terminal paths converge on `CloseAndClear`, but direct executor window-count assertions remain absent.

Queue D D109's executor hit acceptance ordering map is in [EXECUTOR_HIT_ACCEPTANCE_ORDER_AUDIT_D109.md](EXECUTOR_HIT_ACCEPTANCE_ORDER_AUDIT_D109.md); accepted, guarded, and parried counters update only after resolver outcome classification, with no direct executor-counter tests found.

Queue D D110's encounter completion/restart matrix is in [ENCOUNTER_COMPLETION_RESTART_MATRIX_D110.md](ENCOUNTER_COMPLETION_RESTART_MATRIX_D110.md); source permits newer-generation restart after success/death and refuses sticky failure, while no actor-level matrix fixture was found.

Claude's additive Queue D tooling dispositions for D50/D54/D57/D58 are recorded in [QUEUE_D_LEAD_DISPOSITIONS_HOTFIX.md](QUEUE_D_LEAD_DISPOSITIONS_HOTFIX.md); the offline focused suite passed 24 tests with one host-dependent symlink skip. Live PIE behavior remains pending Lead verification.
