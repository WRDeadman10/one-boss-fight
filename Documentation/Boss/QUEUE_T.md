# Queue T — A7 release evidence and offline readiness (50 tasks)

Prepared by Codex after C-886. Lead trim and ordering are binding per C-887/C-889: kept tasks only, in five-task batches, then no further queue absent new owner input. Never claim a packaged/live gate from an offline artifact. Lead HOTFIX takes priority. No status-only tasks.

## T001–T005 — Round 4 evidence handling

| ID | Task | Acceptance |
|---|---|---|
| T001 | DONE — read-only inventory hashes expected summaries/frames; `--expected` detects changed or missing prior artifacts | `Scripts/Tools/round4_benchmark_report.py inventory`; missing/modified fixtures pass |
| T002 | DONE — strict Round 4 measured-receipt JSON schema plus runtime shape/finite-value checks | `Scripts/Tools/round4_benchmark.schema.json`; six unique route/replicate rows required |
| T003 | DONE — comparability checker enforces shared build, hardware, configuration, route-independent run identity, and header consistency | `round4_benchmark_report.py compare`; seeded resolution/build-hash mismatch is INCOMPARABLE |
| T004 | DONE — owner evidence import steps preserve raw package and explain inventory/receipt/report limits | `Documentation/Boss/T004_ROUND4_EVIDENCE_IMPORT_GUIDE.md` |
| T005 | DONE — report generator computes means of the three per-run FPS/p99 measurements; absent inputs and incomparable deltas are UNKNOWN | `round4_benchmark_report.py report`; fixture covers numeric and missing metrics |

## T006–T010 — A7 gate clarity

| ID | Task | Acceptance |
|---|---|---|
| T006 | DONE BEFORE C-887 TRIM | Accepted by Lead in C-889; retained as historical work |
| T007 | DONE BEFORE C-887 TRIM | Accepted by Lead in C-889; retained as historical work |
| T008 | DONE BEFORE C-887 TRIM | Accepted by Lead in C-889; retained as historical work |
| T009 | DONE BEFORE C-887 TRIM | Accepted by Lead in C-889; retained as historical work |
| T010 | DONE BEFORE C-887 TRIM | Accepted by Lead in C-889; retained as historical work |

## T011–T015 — Package and cook manifest tools

| ID | Task | Acceptance |
|---|---|---|
| T011 | DROPPED BY LEAD C-887 | Not in trimmed execution queue |
| T012 | DROPPED BY LEAD C-887 | Not in trimmed execution queue |
| T013 | DROPPED BY LEAD C-887 | Not in trimmed execution queue |
| T014 | DROPPED BY LEAD C-887 | Not in trimmed execution queue |
| T015 | DROPPED BY LEAD C-887 | Not in trimmed execution queue |

## T016–T020 — Shipping and packaged logs

| ID | Task | Acceptance |
|---|---|---|
| T016 | DONE — audited smoke tokens and checker category severity | `Documentation/Boss/T016_T018_T021_T024_SHIPPING_G2_AUDIT.md`; maps emitters and pass impact |
| T017 | DONE — packaged smoke receipt validator and absent/duplicate/contradictory fixtures | `Scripts/Tools/check_packaged_smoke_receipt.py`; 6 focused cases |
| T018 | DONE — regular-suite Shipping CVar source scan plus guarded/unguarded fixtures | `check_shipping_guards.py`; current scan 35 declarations / 0 Shipping uses |
| T019 | DROPPED BY LEAD C-887 | Not in trimmed execution queue |
| T020 | DROPPED BY LEAD C-887 | Not in trimmed execution queue |

## T021–T025 — G2 selection and recovery

| ID | Task | Acceptance |
|---|---|---|
| T021 | DONE — expected-sheet case/token coverage checker and omission fixture | `Scripts/Tools/check_g2_selection_refusal_expected.py`; expected JSON covers driver |
| T022 | DROPPED BY LEAD C-887 | Not in trimmed execution queue |
| T023 | DROPPED BY LEAD C-887 | Not in trimmed execution queue |
| T024 | DONE — AST audit for literal known-map `load_asset` calls | `Scripts/Tools/audit_editor_map_loads.py`; map and data-asset fixtures |
| T025 | DONE — packaged recovery matrix with separate failure/recovery evidence slots | `Documentation/Boss/T025_G2_PACKAGED_RECOVERY_MATRIX.md`; Shipping/Development fields remain blank/open |

## T026–T030 — Definition and parity report integrity

| ID | Task | Acceptance |
|---|---|---|
| T026 | DROPPED BY LEAD C-887 | Not in trimmed execution queue |
| T027 | DROPPED BY LEAD C-887 | Not in trimmed execution queue |
| T028 | DROPPED BY LEAD C-887 | Not in trimmed execution queue |
| T029 | DROPPED BY LEAD C-887 | Not in trimmed execution queue |
| T030 | DROPPED BY LEAD C-887 | Not in trimmed execution queue |

## T031–T035 — A5 parity operations

| ID | Task | Acceptance |
|---|---|---|
| T031 | DONE — A5 registration audit across receipt registry, RunDrivers and runner | `Scripts/Tools/audit_a5_driver_registration.py`; 31 matches, missing/extra fixtures |
| T032 | DROPPED BY LEAD C-887 | Not in trimmed execution queue |
| T033 | DROPPED BY LEAD C-887 | Not in trimmed execution queue |
| T034 | DONE — validator for duplicate/missing A5 receipt pair IDs and arms | `Scripts/Tools/validate_a5_receipt_directory.py`; duplicate, missing, and contradiction fixtures |
| T035 | DROPPED BY LEAD C-887 | Not in trimmed execution queue |

## T036–T040 — Offline test and kit reliability

| ID | Task | Acceptance |
|---|---|---|
| T036 | DONE — dependency scan detects PowerShell dot-source targets | `test_make_bench_kit_dependencies.py`; quoted missing target fixture fails |
| T037 | DONE — kit manifest checker rejects duplicate destinations and missing sources | `Scripts/Tools/check_bench_kit_manifest.py`; existing 8-entry inventory passes |
| T038 | DROPPED BY LEAD C-887 | Not in trimmed execution queue |
| T039 | DROPPED BY LEAD C-887 | Not in trimmed execution queue |
| T040 | DONE — scaffold collision fixture preserves existing output and reports refusal | `test_new_rule_scaffold_collision.py`; existing bytes/files remain unchanged, exit 2 |

## T041–T045 — Documentation and source audit helpers

| ID | Task | Acceptance |
|---|---|---|
| T041 | DROPPED BY LEAD C-887 | Not in trimmed execution queue |
| T042 | DROPPED BY LEAD C-887 | Not in trimmed execution queue |
| T043 | DONE — source-only classification of every Editor Python script | `Documentation/Boss/T043_EDITOR_ASSET_SCRIPT_INVENTORY.md`; 357 scripts in four categories |
| T044 | DONE — static UE Python UENUM prefix/member/value fixtures | `Scripts/Tools/test_ue_python_enum_conventions.py`; flags E-prefix, wrong member, and integer coercion |
| T045 | DONE — first explicit save, earlier assertions, and guard-marker inventory | `Documentation/Boss/T045_EDITOR_SAVE_SAFETY_AUDIT.md`; reports all 140 source-classified writer scripts |

## T046–T050 — Handover and next-cycle readiness

| ID | Task | Acceptance |
|---|---|---|
| T046 | DROPPED BY LEAD C-887 | Not in trimmed execution queue |
| T047 | DROPPED BY LEAD C-887 | Not in trimmed execution queue |
| T048 | DROPPED BY LEAD C-887 | Not in trimmed execution queue |
| T049 | DROPPED BY LEAD C-887 | Not in trimmed execution queue |
| T050 | DONE — closed trimmed Queue T and recorded handoff condition | `Documentation/Boss/T050_QUEUE_T_CLOSEOUT.md`; no next queue until owner evidence/decision creates work |
