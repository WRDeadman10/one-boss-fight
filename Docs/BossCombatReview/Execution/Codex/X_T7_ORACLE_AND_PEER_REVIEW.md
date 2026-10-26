# X-T7 independent oracle / peer review

2026-10-26. Draft-only test changes. No UE compile/automation/PIE run by Codex. Read actual AG16 Rev03 script/JSON, current raw notify export, AG30 and AG36 against staged/live code. C++ checks below are AUTHORED, NOT PASSED.

## AG16 Rev03 verdict: scalar subset accepted; traversal oracle still partial

Ran read-only `python -I Docs/BossCombatReview/Execution/Codex/WP6Support/check_timeline_oracle.py`: loads AG definitions without invoking its writing main;27 input hashes match JSON; recompiles14 montage dictionaries exactly equal to delivered JSON; nine self-tests reproduce9/9. Independently sampled A2 length3.4000000953674316, collision1.567..1.760 and1.925..2.104, sounds1.593/1.817, movement overhang4.933 projected3.4 with RawEnd retained.

Current raw export SHA256 **950c611ee5eae7bcdd7abca1ea56c051c3b42d988b427cf64452829142ab0b31**. JSON digest **c385998278dd0c0f2c1560043da5d2f4c99dba37e2831bdfa0b7b038b6becc32**. AG16 prose still lists old c72b... and older sidecar hashes, whereas JSON input_hashes match actual files. This is a provenance-report defect; do not silently treat old/new raw files as identical or assert why bytes changed. Staged scalar fixture repinned explicitly to actual current export; scalar values agree.

New independently reproduced defects:

1. `timeline_reference.py:307` bounds guard lacks finite checks. `evaluate_crossing(A2, NaN, 0.5)` returns **MATCH**, not INCONCLUSIVE. NaN comparisons are all false; no events is not valid traversal. C++ draft already checks finite observation values at compiler.cpp:87; add an AG regression before using it as full oracle.
2. `timeline_reference.py:345` only splits ForwardLoop when curr<prev. `ForwardLoop(prev=.1,curr=.2,prev_loop=0,loop=1)` returns MATCH with **zero crossings**, omitting the tail and new head of the declared full wrap. Even with curr>=prev, one verified loop implies traversal through end/start. C++ known-loop path adds both spans independently; do not copy this AG bug into it.
3. Unverified section topology/full binary notify payload remain explicitly unavailable. ForwardLoop is mathematical caller-declared input, not proof of a real engine loop/section graph. Whole-montage canonical JSON digest is not a uasset hash or full binary payload digest.

Clean checks: SectionJump and out-of-bounds now return INCONCLUSIVE; begin>=length rejects before projection; duplicate ids shared across windows/markers reject; nonfinite compile bounds reject; current27 input hashes agree with disk;14 regenerated records match delivered JSON. These bounded checks do not waive defects1/2.

## Staged C++ scalar tests updated

RPGTimelineTests DraftA2Golden now uses the matched Rev03 scalar subset, an independent eight-event expected time/id/edge sequence, both full hitch AND205 incremental60Hz samples, per-step half-open active-collision state reconstructed from emitted begin/end edges, and a zero-rate stationary sample after every frame. This is a crossing-stream oracle, not an internal Active-set API or live animation test. Added inverted/zero-duration/NaN compile negatives. Binding test adds generation decrement/zero rejection. No claimed new runtime state algorithm or P1 behavior.

## AG30 disposition

- F1/F2/F3 source fixes accepted (X-T1). F8 positive resolving coverage exists and C140 nonlegacy negative now actually reaches resolving. Full leases/cook/ABI negative proof is not established simply by that one test.
- F5 "requested instead of Same" is rejected: Pick returns SetBuild's Same, source/preimage and Loadout426-435. Alias raw pre-check existed before DD1.
- F6 direct item->all references is not actual required pack topology. Nevertheless combined arbitrary-property text is not sufficient typed compatible-edge validation. Keep full-spec condition open.
- F7 programmatic first3 compatibility exception is not a human key/mouse bypass; actual constrained viewport/focus/diagnostic obligations still open. "Headless CI would fail" is a rationale, not a reproduced necessity here.

## AG36 every finding

| ID | Disposition | Change / reason / remaining proof |
|---|---|---|
| OW1 | FIXED in staged test |60Hz versus exact scalar sequence + per-sample half-open state + full hitch. Not run. AG's proposed snippet reset StepObs.Sample each iteration, which would itself duplicate samples; our monotonic Sample is retained across frames. |
| OW2 | FIXED bounded staged assertions | Added non-Shipping read-only GetRecordJsonForTest and Python JSON structure/hash/id/null/finite/ordering checks for every buffered row per observer. Full run-header provenance/flush and off/on outcome parity remain separate. |
| OW3 | OPEN known fixture dependency, not a false-pass defect | Driver explicitly requires preauthored two-encounter fixture and fails without it. Do NOT install in L_SevarogArena gate. Creating fixture/startup adapters still required. |
| OW4 | OPEN known proof boundary | Plain-actor synthetic worlds test registry isolation only. Real Character/mesh/skeleton/BeginPlay fixtures remain necessary; no unit test upgrade can claim actual duel parity. |
| MN1 | FIXED in staged test | Stationary rate0 sample repeated205 times, no duplicate crossings. Compiler itself uses no division by playback rate; alleged infinite loop was hypothetical, not observed. |
| MN2 | FIXED test gap; implementation defect REJECTED | Compile already rejects nonfinite and End<=Begin at45-50. Added inverted, degenerate and NaN tests rather than redundant production logic. |
| MN3 | OPEN tests/policy | Duplicate slots already rejected in BindEncounter; dedicated negative fixture test missing. Self-target policy must distinguish participant roles, not ban every self-associated presentation actor blindly. Boss attack self-target remains disallowed design intent. |
| MN4 | OPEN | Three-plan configure rollback + registration-failure poison tests missing. Core does not claim registration is reversible. |
| MN5 | OPEN | Callback can destroy owner/reenter on same game thread; not arbitrary asynchronous UObject access. Strong component leases do not prove owner validity after callback; full negative test and postcallback owner guards needed before product promotion. |
| MN6 | FIXED in staged test | Existing strict NewGeneration>current branch; added zero/decrement checks. Same generation already covered. |
| DB1 | PARTIAL | Replaced PIE start/end fixed waits with bounded condition polls.25s passive observation remains a declared capture interval; actual readiness/natural-activity fixture still needs stronger bounded polling. GC0.5 is a settling interval, not evidence by itself. |
| DB2 | OPEN / claim narrowed | No forcing in passive driver. Requires naturally active fixture/operator scenario; zero meaningful samples must FAIL, not pass. Original "crashes" is inaccurate: check records failure; missing wake is a coverage/setup issue, not a shown exception. |
| DB3 | FIXED source, runtime unverified | command selects live game world OR explicit editor world; raises if neither exists. AG's proposed UnrealEditorSubsystem.execute_console_command is not assumed available. Claimed None always fails was not independently reproduced. Restoration readback still needed. |
| SS1 | FIXED bounded guard, wider contract OPEN | TGuardValue suppresses recursive observation broadcasts, not subscriber gameplay mutation/destruction. Bool is game-thread guard, NOT thread-safe mutex. Private scoped subscription still preferred before product use. |
| SS2 | FIXED staged validity checks | Tracker/owner/character/mesh/anim/montage checked with IsValid. AddUObject/weak unsubscribe already existed; not an unguarded general raw lifetime subscription. Teardown stress proof remains. |

## Promotion refresh

Both concrete scaffold patches regenerated after draft changes. Tracker seam now5 added header lines/13 added cpp lines, zero removed lines (not whole-file CRLF replacement). Read-only git apply --check passes. They remain scaffolds: hydration/adapters/importer/fixtures absent. Python syntax is checked offline with ast.parse, not Unreal imports/PIE. No report turns these authored tests into41/41 results.

## A93 follow-up: AG16 Rev04 independently rechecked

Read revised guards and reran the same read-only helper: **11/11** self-tests,27 matching input hashes,14 exact regenerated dictionaries. NaN now INCONCLUSIVE; declared loop .1->.2 loop0->1 emits the seven tail crossings plus start0 on loop1 in traversal order. Both X136 counterexamples are closed. Current JSON SHA256 `9e06073022e09fcdb78e20fd1581e1cc51fea1338eae2e86dadeac8747bfd967`; raw export remains950c611e.... Previous c3859982... is historical Rev03 JSON, not current. A2 scalar fixture values remain identical, so no patch republish needed for this oracle correction. Text-export scalar/topology/binary-payload limitations remain unchanged.
