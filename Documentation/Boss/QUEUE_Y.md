# Queue Y — Codex follow-on lane

Started 2026-11-06 under the owner's instruction to continue the established batch cadence. Ten batches of five. Inspect the mailbox each cycle; post one batch receipt; proceed to the next unblocked batch without waiting for review; fix rejected items first on the next cycle. Claude owns build/Editor/PIE/package execution. Owner choices, visual changes, and destructive cleanup remain gated.

Current status: Y001-Y050 complete locally. R6 raw performance return remains WAITING ON LEAD/owner; all four A7 packaged gates remain open. KI-190/art choices remain open; no Lead P35 census or cleanup authorization. Four tool gaps have specific regression/acceptance specifications but remain unfixed and untested. Queue Z is drafted for Lead review.

## Batch 1 — Round 6 intake and integrity

| ID | Task | Target / acceptance |
|---|---|---|
| Y001 | Recheck R6 return availability | `Saved/bench_return`, mailbox; report exact missing/present evidence only. |
| Y002 | Verify returned R6 package identity | package ID, executable hash, manifest and run-log hashes; fail intake on identity drift. |
| Y003 | Independently recompute R6 summaries | raw `summary.json` / `frames.csv`; reproducible per-arm median and p99 or WAITING status. |
| Y004 | Cross-check R6 active-mode witnesses | each treatment matched to raw `game.log` mode and build identity; no plan-only inference. |
| Y005 | Batch receipt | retain failed/unrun runs and separate owner image-quality gate. |

## Batch 2 — input latency and telegraph captures

| ID | Task | Target / acceptance |
|---|---|---|
| Y006 | Intake six Lead latency sessions | W-C036 sheet and raw logs; route/action/FPS/cadence identity table. |
| Y007 | Assess latency driver timing fields | `pie_input_montage_latency.py`; quantify arm/injection/sample intervals from logs or specify minimal diagnostic change. |
| Y008 | Intake paired A1–A3 captures | synchronized clips/logs; measured, inconclusive, and unrun states separated. |
| Y009 | Intake paired A4–A6 captures | same fields and classification; no configured time treated as reaction time. |
| Y010 | Batch receipt | cite evidence hashes and preserve every absent capture gate. |

## Batch 3 — hit feedback runtime evidence

| ID | Task | Target / acceptance |
|---|---|---|
| Y011 | Read back active boss shake settings | Lead Editor receipt and build identity; values by event or UNKNOWN. |
| Y012 | Match hit-stop captures to events | W-C037 matrix plus synchronized logs; verify trigger, duration and route. |
| Y013 | Map audio cues to event/source assets | authored cue and capture inventory; no filename-only confirmation. |
| Y014 | Reconcile parry/riposte feedback routes | source, active Blueprint values, raw capture; preserve absent-channel limits. |
| Y015 | Batch receipt | no subjective feel claim without capture and defined observation. |

## Batch 4 — A7 current package and cook closure

| ID | Task | Target / acceptance |
|---|---|---|
| Y016 | Intake authoritative package cook manifest | current package ID and manifest hash; reject historical H2 as substitute. |
| Y017 | Resolve selected-definition dependency closure | manifest/package paths mapped to expected roots; exact missing paths reported. |
| Y018 | Recheck content caller inventory | Lead graph scan, asset identities, and search scope recorded; do not infer from C++ search. |
| Y019 | Reconcile Shipping selector proof | real caller, setter behavior, binary identity, raw log; defer if no caller. |
| Y020 | Batch receipt | retain A7-SHIPPING and A7-SAVE/COOK gates until evidence passes. |

## Batch 5 — A7 refusal and owner-visible recovery

| ID | Task | Target / acceptance |
|---|---|---|
| Y021 | Intake packaged valid-selection case | fresh process, route identity, selected state and legacy absence. |
| Y022 | Intake packaged missing-definition case | exact refusal token, cleanup snapshot, visible owner-session capture. |
| Y023 | Intake packaged invalid-definition case | identity-bound fixture, fail-closed result and visible recovery. |
| Y024 | Verify empty-selector fallback control | fresh process confirms legacy behavior while A7=B remains active. |
| Y025 | Batch receipt | update only gates with package-bound evidence; no release declaration. |

## Batch 6 — open owner decisions

| ID | Task | Target / acceptance |
|---|---|---|
| Y026 | Recheck KI-190 owner response | mailbox and `KNOWN_ISSUES.md`; exact answer or keep OPEN. |
| Y027 | Review Strength Light cost implementation proposal | source/table/driver; no change without scoped owner answer. |
| Y028 | Recheck Tier 2 art choice | mailbox and owner brief; exact option/deferral or leave untouched. |
| Y029 | Reconcile selected art option to safe-default plan | only after choice; preserve optional defaults and D5 parity scope. |
| Y030 | Batch receipt | no decision inferred from silence. |

## Batch 7 — P35 cleanup evidence

| ID | Task | Target / acceptance |
|---|---|---|
| Y031 | Intake Lead P35 referencer census | `[P35_REFERENCERS_JSON]`, tool/build identity, all candidates accounted. |
| Y032 | Independently verify candidate identity | package paths, file hashes and referencer output agree. |
| Y033 | Classify direct and transitive references | report each candidate and limits; zero direct references is not authorization. |
| Y034 | Recheck owner cleanup authorization | mailbox/decision record; no authorization means no removal. |
| Y035 | Batch receipt | no asset move/delete; preserve owner gate. |

## Batch 8 — comparator and audit-tool gaps

| ID | Task | Target / acceptance |
|---|---|---|
| Y036 | Specify G044 comparison false-match fix | `compare_manifest_to_legacy_defaults.py`; source-token binding regression fixture. |
| Y037 | Specify parity health-mismatch coverage | `compare_encounter_parity.py`; structured state-metric regression fixture. |
| Y038 | Review R6 failure-log retention | `RunBenchmark.ps1`; timeout/nonzero fixtures preserve run-local logs. |
| Y039 | Review requirements matrix registration mapping | CSV/validator; reconcile stale IDs and source paths or mark unknown explicitly. |
| Y040 | Batch receipt | keep tool tests separate from live/package acceptance. |

## Batch 9 — artifact and documentation consistency

| ID | Task | Target / acceptance |
|---|---|---|
| Y041 | Refresh residual risk register | current raw evidence and decision records; each state has source. |
| Y042 | Cross-check witness ledger | existing verifier plus semantic exceptions; no unsupported ledger promotion. |
| Y043 | Reconcile TASKS/STATE/TEST_PLAN/issues/decisions | no conflicting current status; historical snapshots labeled. |
| Y044 | Refresh owner handover | open decisions, evidence, owners and next actions in one page. |
| Y045 | Batch receipt | link every updated artifact and preserve unresolved gates. |

## Batch 10 — release-readiness check and roll

| ID | Task | Target / acceptance |
|---|---|---|
| Y046 | Review A7 gate checklist against fresh receipts | each gate OPEN/CLOSED only with its named evidence. |
| Y047 | Verify package/build identity chain | source revision, executable, package manifest, logs and captures match. |
| Y048 | Audit remaining owner-facing claims | citations and evidence class per number; no count without a source. |
| Y049 | Recheck all Queue Y unresolved rows | exact WAITING/OPEN dispositions and named evidence owner. |
| Y050 | Batch receipt and next-lane draft | ten five-task batches with targets and acceptance, subject to Lead review. |

Owner-gated choices, destructive asset operations, and look-changing defaults remain outside this audit queue. Claude owns build/Editor/PIE/package execution.


## Current status addendum - Y011 through Y015

BUILD-231 paired pie_legend_t2 receipts are 25/25 per route with comparator MATCH. They instrument A2/A6/roar shake behavior, riposte hit-stop, parry slow-motion, and reset restoration. Exact serialized shake settings and per-event audio playback remain unverified. L4 samples are about 0.093-0.098 s against a nominal 0.08 s target while passing the driver’s broad 0.04-0.20 s interval. Reconciliation: `Y011_Y014_HIT_FEEDBACK_RUNTIME_RECONCILIATION.md`; earlier X-C034 source-only statement corrected. Continue Y016-Y020 without waiting.

## Current status addendum - Y016 through Y020

The R6 kit contains Shipping and Development `Manifest_UFSFiles_Win64.txt` files. Shipping SHA-256 is `c1336388ea9448013e1b441a7b386f390930a5c19a49bc6d73f159fdc77eefbd`; Development SHA-256 is `4afafd7d633d3cd8b70c3af07c793a56a39e404c1b20b1aa3b7bcb4532c0f413`. The Shipping file has 11,502 lines and 3,787 unique `/Game` package paths. BUILD_INFO gives executable timestamp/size and stage-presence flags, but no package ID or executable SHA-256, so neither manifest is cryptographically bound to the staged binary. No UAT log or normalized schema manifest was found.

Comparing Shipping's normalized package paths against the retained H2 census gives all 3 roots present and 78/156 unioned `/Game` closure paths present; 78 are absent: 28 Manny poses, 28 Quinn poses, 4 rigs, 12 Quinn textures, 2 Quinn material instances, and 4 meshes. This exactly matches the categories already dispositioned as editor-only skeleton references in C-878; it does not independently establish those paths' editor-only status or runtime irrelevance. The current package manifest is partial evidence and does not replace identity-bound UAT/cook proof. Full comparison: `Y016_Y020_A7_COOK_MANIFEST_RECONCILIATION.md`.

The C-876 content caller inventory still records zero Blueprint references in 11,738 Content packages and no current setter caller. Under J049=A/A7=B, packaged setter proof remains deferred until a real caller exists; no caller or test asset was created. Y019 is therefore deferred, and packaged refusal/recovery proof remains open. The earlier X-C037 statement that no cooked manifest was present under Saved was too broad: a staged UFS manifest was found in the R6 transfer kit. Corrected in `X_C036_C039_RELEASE_GATE_AUDIT.md`, the residual-risk register, and owner handover.

## Current status addendum - Y021 through Y025

No package-bound valid-selection, missing-definition, invalid-definition, or empty-selector case was found in the R6 kit or project staged-output locations. `B_G044_LIVE/selected` and `selected_v2_tracker` are successful headless Editor/PIE selected-route receipts (raw hashes `2b8ab3ff8f8493f07430003a04ab9e9df9c98c25e75497f2282c1912043bd301` and `4fc69675a6debe241a87e664b87061e48bd51138eb1e44ebf04ffdad56b0200c`), not packaged runs. C872 G2 v2 (`3a631b2bba5b5f8e3a9c88d829144abef610524543889b3aeebcaa1d98b550eb`) passes 13/13 in Editor/PIE: missing path refuses with `EncounterSelection.AssetLoad`; a corrupted-hash definition copied into `/Engine/Transient` refuses with `EncounterDefinition.ManifestShape`; explicit empty selection restores `LegacyNoSelection` and the legacy boss bundle. Its UI screenshots were black/unusable in the agent session. Thus the PIE checks inform recovery behavior but do not satisfy T025's fresh-package identity, packaged logs, or owner-visible screenshot requirements; all four A7 gates remain OPEN. No project staging executable or matching run/visual artifacts are present. Reconciliation: `Y021_Y025_A7_PACKAGED_RECOVERY_INTAKE.md`.

## Current status addendum - Y026 through Y030

No new owner decision for KI-190 or Tier 2 art appears after C-935/A-563. KI-190 remains open: native defaults leave Strength Light at `StaminaCost=-1` (pack base 15), while the source comment assigns 35 to heavy swings. `pie_stamina_cost.py` verifies 15 on a no-cost row and exercises 35 through a test override; it does not prove a real Strength Light loadout costs 35. Do not change values without owner scope and a real loadout check. Tier 2 brief options A/B/C remain alternatives only; A is recommended in the brief but not selected. Keep the current opt-in empty-default plan, no art creation/wiring/default change. Full review: `Y026_Y029_OWNER_GATES_RECHECK.md`.

## Current status addendum - Y031 through Y035

All seven P35 candidate package files remain present; current byte sizes and SHA-256 are recorded in `Y031_Y035_P35_REFERENCER_INTAKE.md`. No actual `[P35_REFERENCERS_JSON]` Lead Editor output/tool identity or owner cleanup authorization was found. Direct and transitive reference status remain UNKNOWN. No candidate was changed. Continue Y036-Y040 without waiting.

## Current status addendum - Y036 through Y040

Specified: source-token binding for the G044 defaults comparator; structured health parity observables; per-run failure-log retention plus timeout/nonzero/success fixture requirements; and registration/source mapping semantics for the coverage matrix. Current tool behavior and counterexamples are grounded in existing audit reports. These are fix specifications only; no source/test edits or test execution. Details: `Y036_Y039_TOOL_GAP_SPEC.md`.

## Current status addendum - Y041 through Y045

Refreshed residual-risk register and owner handover; re-ran the specified witness verifier (4/4; 82 IDs/61 deltas; 80/2/0; 470 citations/94 files; formatting clean), without editing ledger rows. Reconciled current statuses across Queue Y, TASKS, PROJECT_STATE, TEST_PLAN, KNOWN_ISSUES, DECISIONS, A7 gate JSON and mailbox. No unsupported promotion or new owner decision found. Details: `Y041_Y045_STATUS_LEDGER_HANDOVER.md`.

## Current status addendum - Y046 through Y050

Verified all four A7 gates remain OPEN; computed hashes for staged launchers and inner binaries; no source/build ID, manifest-to-binary link, or run/capture chain is available. Audited current owner-facing numeric claims and marked Tier 2 per-asset sizes/costs/timings as unmeasured proposals. Reconciled unresolved Y rows and evidence owners. Queue Z contains 50 unique ordered read-only audit tasks in ten five-task batches, pending Lead review. Evidence and claim details: `Y046_Y049_RELEASE_READINESS_RECHECK.md`; next-lane draft: `QUEUE_Z.md`.
