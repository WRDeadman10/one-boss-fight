# Offline tools

Scripts here inspect source, docs, manifests, JSON exports, mailboxes or existing logs. They do not require Unreal to be open unless a tool's own usage says otherwise. Run a script's `--help` before using unfamiliar arguments. Main usage collection: `Documentation/Boss/TOOLS.md`.

File outputs use the shared `atomic_io.py` helper where replacement or no-overwrite publication is needed; the S171 audit and failure-injection fixture are linked from `Documentation/Boss/TOOLS.md`.

Fail-closed exit codes and the opt-in `--redact` flag for sharing report output (lane BO, KI-163..167): `Documentation/Boss/BO_TOOL_BEHAVIOUR_GUIDE.md`. Run the lane's tests with `python Scripts/Tools/run_bo_lane_tests.py`.

| Script | Purpose |
|---|---|
| `audit_a5_driver_registration.py` | Compare all receipt-registered A5 drivers with RunDrivers and fresh-process runner registration. |
| `mailbox_decision_digest.py` | Read-only JSON digest of Claude mailbox messages in an inclusive C-id range. |
| `mailbox_open_items.py` | Compact index of explicit open-state mentions in the last N mailbox posts; does not infer closure. |
| `evidence_pack_hashes.py` | No-overwrite SHA-256 manifest writer for supplied build/parity evidence folders. |
| `summarize_parity_set.py` | Fail-closed summary of the five BUILD-232 default-off comparator reports. |
| `check_bench_kit.py` | Validate staged bench-kit inputs, build identity, expected files and PDB exclusion before zip publication. |
| `check_packaged_g044_cook.py` | Validate the normalized selected-encounter cook manifest and G044/VFX closure against a package stage. |
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
| `discover_focused_player_tests.py` | Deterministic AST-only inventory of focused offline player contract tests; does not import or execute them. |
| `validate_queue_batches.py` | Validate AA-C/AB-C ID order and ten groups of five task rows. |
| `test_discover_focused_player_tests.py` | Fixture tests for deterministic focused player test discovery. |
| `test_validate_queue_batches.py` | Queue validator tests for valid groups, duplicate/missing IDs, and malformed grouping. |
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
| `a7_release_gates.py` | Validate and render the evidence state of the A7 release gates. |
| `air_light_receipt.py` | Fail-closed parser for timestamped Air Light action-context records. |
| `aq_evidence_freshness.py` | Classify evidence identity metadata without opening or changing raw artifacts. |
| `ar_charge_receipt.py` | Read-only parser for retained ER control-latency R2 hold log rows. |
| `ar_charge_repeat_receipt.py` | Stamp and aggregate independent route-identified R2 charge trial receipts. |
| `ar_er_cook_manifest.py` | Read-only same-build check for the eight ER/Tier 2 cook package paths. |
| `audit_framework_schemas.py` | Audit FrameworkProof schema duplicates, source/docs mapping, log samples, and regex looseness. |
| `audit_source_error_token_coverage.py` | Inventory source error/refusal tokens and show literal references in native tests. |
| `aura_warmup_receipt.py` | Validate that approved/candidate aura captures followed a bright warmup in the same run. |
| `bind_owner_approval.py` | BK-97 (C, implementer; X-2003): pure binding adapter between a raw owner mailbox message, the approval envelope |
| `bind_receipt_source.py` | BK-122/123 (C, implementer; X-2012, X-2013): pure adapter that binds a Sevarog executor receipt to its owner mailbox source. |
| `build_parry_addendum_reel.py` | Build Parry SFX Addendum Audition Reel (C-1186). |
| `build_sfx_audition_reel.py` | Build the Owner SFX Audition Reel (SFX-03) using ffmpeg. |
| `build_sfx_batch3_reel.py` | Build the Owner SFX Batch 3 Audition Reel (C-1204) using ffmpeg. |
| `camera_probe_receipt.py` | Fail-closed validation for dynamic camera probe JSONL samples. |
| `check_g044_cook_manifest.py` | Compare required G044 /Game package paths with a packaged cook manifest. |
| `check_stage_identity.py` | Read-only preflight for distinct Shipping and Development UAT stage roots. |
| `check_validator_tokens.py` | Check FrameworkProof UE_LOG tokens against validator and documentation indexes. |
| `compare_determinism_runs.py` | Validate and compare the six U-C07 Lead-run determinism arms. |
| `compare_encounter_parity.py` | Fail-closed comparison of paired legacy/data encounter-driver JSON receipts. |
| `compare_manifest_to_legacy_defaults.py` | Compare every typed G044 boss/player setting against cited legacy defaults. |
| `diff_phase_two_auras.py` | Read-only parameter diff between approved baseline NS_Boss_PhaseTwoAura and candidate NS_Boss_PhaseTwoAura_Boost. |
| `encounter_parity_receipt.py` | Pure builders and strict validation for captured encounter parity receipts. |
| `fight_capture_receipt.py` | Validate a single-run full-fight capture log and return machine-readable evidence. |
| `fight_review_observation.py` | Validate human-coded visual observations against same-run frame identities. |
| `find_orphan_docs.py` | Finds unreferenced (.md, .patch, .txt) documents under Documentation/ and Docs/ that are candidates for cleanup. |
| `make_fight_video.py` | Turn [FullFight] game-time frames and action markers into ffmpeg/ASS inputs. |
| `new_profile_field_scaffold.py` | Print the project's eight review sites for adding an opt-in profile field. |
| `new_rule_scaffold.py` | Generate a header, automation-test, and designer-reference skeleton for a pure rule. |
| `normalize_cook_package_manifest.py` | Normalize an explicit captured cook-manifest export without inferring packages. |
| `normalize_encounter_selection_graph.py` | Normalize an explicit Editor selection-graph export for cook reachability checks. |
| `plan_camera_default.py` | Print a no-write plan for a future, owner-authorized camera default. |
| `plan_sevarog_definition_repair.py` | BK-92/93 (C, implementer; X-2002): PROPOSAL-ONLY planner for an in-place Sevarog definition repair. |
| `round6_benchmark_report.py` | Validate and summarize Round 6 receipts; never edits benchmark evidence. |
| `round6_phase2_intake.py` | Strict offline intake gate for the owner-approved Round 6 Phase 2 receipt. |
| `run_bo_lane_tests.py` | BO-46: one-command offline runner for the lane BO test suites (KI-163..167 tool hardening and --redact). |
| `run_offline_suite_timed.py` | Run the Scripts/Tools unittest suite and enforce its wall-time budget. |
| `runner_status_receipt_proposal.py` | BK-167..169 (C, implementer; X-2033): PROPOSED versioned status receipt for C-1155 runners, with a pure validator. |
| `runner_status_receipt_proposal_v1_1.py` | BK-171..175 (C, implementer; X-2034): PROPOSED status receipt v1.1 for C-1155 runners - stricter successor of |
| `runner_status_receipt_proposal_v1_2.py` | BK-176..180 (C, implementer; X-2038): PROPOSED status receipt v1.2 for C-1155 runners - successor of v1.1 |
| `scan_doc_citations.py` | scan_doc_citations.py - Scanner to detect uncited measurements in Lane A documents. |
| `scan_pie_driver_safety.py` | Offline inventory of PIE driver RESULT and key-release readiness risks. |
| `sevarog_executor_contract.py` | BK-102 (C, implementer; X-2004): pure state-machine contract for a FUTURE Sevarog definition executor. |
| `sevarog_receipt_v2_proposal.py` | BK-132..135 (C, implementer; X-2017): PROPOSED v2 evidence schema for Sevarog executor receipts. |
| `summarize_encounter_cost.py` | Summarize cold/warm Lead cost samples without dropping run identities. |
| `summarize_er_guard_counter.py` | Summarize retained ER guard-counter probe markers without inferring a hit. |
| `summarize_packaged_metrics.py` | Summarize Lead-captured packaged metrics by phase without mixing identities. |
| `validate_encounter_manifest.py` | Validate the canonical G044 membership receipt without Unreal or file writes. |
| `validate_owner_approval_envelope.py` | BK-86..89 (C, implementer; X-1999): read-only validator for a SYNTHETIC owner approval envelope. |
| `validate_pending_definition_inputs.py` | BK-78 (C, implementer; X-1996): read-only validator for a PENDING definition-input provenance manifest. |
| `validate_sevarog_executor_receipt.py` | BK-112: pure schema validator for future Sevarog executor receipts; validates claims, performs no operations. |
| `verify_bf_x05_selected_route.py` | Fail-closed predicate checker for a Lead-transcribed BF-X05 evidence receipt. |
| `verify_bk56_60_receipts.py` | BK-66..68 (C, implementer; X-1993): read-only verifier for one BK-56..60 runner receipt bundle. |
| `verify_bk7_shipping_receipt.py` | Fail-closed structural and artifact-hash validation for BK-7 Shipping receipts. |
| `verify_c1278_x26_live_log.py` | Check a Lead PIE log against the C-1278 X26 live acceptance table. |
| `verify_encounter_package_graph.py` | Verify normalized encounter soft-reference reachability against a cook package manifest. |
| `verify_framework_perf_receipt.py` | Validate explicit framework CPU scope receipts without treating frame GPU as boss-attributed. |
| `write_a4_parity_receipt.py` | Finalize an A4 driver capture as a v2 receipt after the source log is closed. |
| `run_bp_lane_tests.py` | BP-46: run the Queue BP static and in-process test suites in this process and print one row per suite. |

Reports can contain heuristic suspects. Read the code/context before treating a match as a defect; these tools do not replace builds, automation tests, PIE evidence, or owner review.

## Additional maintained CLIs

These are also maintained under this folder and are covered by [`CLI_AUTHOR_GUIDE_S154.md`](CLI_AUTHOR_GUIDE_S154.md):

- `audit_framework_schemas.py`
- `check_validator_tokens.py`
- `new_profile_field_scaffold.py`
- `new_rule_scaffold.py`

The complete input, output, deliberate exit status, and side-effect contract for indexed CLIs is in [`CLI_AUTHOR_GUIDE_S154.md`](CLI_AUTHOR_GUIDE_S154.md).
