# BK-71..75: deferred PIE log schema and success cross-check

Assigned by X-1995 (lead Codex) to C (implementer), 2026-11-11. New and own files only (`verify_bk56_60_receipts.py` and its test, both from BK-66..70); no runner, driver or asset edits; no Unreal, build, PIE or locks. No live claims.

## BK-71: marker schema mapped to source

| Order | Marker (emitter) | Meaning | Proves a selected-route decision? |
|---|---|---|---|
| 1 | `[SevarogLive] PACK_STYLE_READY` (driver `pie_sevarog_framework_live.py:113`) | KI-150 ordering: pack style set before target health is read | no |
| 2 | `[FrameworkProof] selected_route_initialized route=data ... testStartApis=0` (`RPGFrameworkBossCharacter.cpp:167`) | Selected-route initialization; emitted inside `ActivateDeferredSelectionForTest` by `InitializeSelectedEncounterForTest` (`RPGPlayerMovesSubsystem.cpp:1245`), which now passes `bAllowDevTest=false` (`.cpp:115-116`), so `bTestInitialized` is false and the production Tick runs | no (initialization only) |
| 3 | `[EncounterActivation] deferred_selected route=data definition= hash=` (`RPGPlayerMovesSubsystem.cpp:1259`) | Activation succeeded; logged synchronously before `activate()` returns | no (activation only) |
| 4 | `[SevarogLive] DEFERRED_SELECTION route=framework definition= hash= ... test_start_calls=0` (driver `:479`) | Driver confirmation after `activate()` returned | no |
| 5 | `[SevarogLive] SPAWN PASS` (driver `:279`) | Navigation check on a later tick (`validate_spawn_navigation`) | no |
| 6 | `[SevarogLive] DEFERRED_TICK_MONITOR ... selector_trigger=none test_start_calls=0 saves=0` (driver `:372`) | Passive observation starts; no test-start API is called | no (monitor only) |
| any after 3 | `[CARD_DECISION] seq= card= phase=` (`RPGFrameworkBossCharacter.cpp:813`) paired with `[FrameworkProof] decision ... seq=` (`:814`) | The production Tick selector chose a card (then `Executor->StartCard`) | **yes**, when after `deferred_selected` with no test-start evidence |
| 7 | `[SevarogLive] DEFERRED_TICK_RESULT outcome=` (driver `:381` terminal, `:387` TimeCap, `:471` ActivationRefused) | Terminal observation | no on its own |

Outcome semantics, from source:
- `TimeCap activeState=Active` and `BossDefeated` can accompany a success only together with at least one decision.
- `Failed` means the framework called `Fail()`.
- `ActivationRefused` means the activation failed.
- `Succeeded` is set only at `RPGFrameworkBossCharacter.cpp:915`, inside the `bTestInitialized` block at `:899`, so it is unreachable on the selected route; seeing it there is a contradiction.

Receipts: only refusal outcomes exist (BK_56_60 Run_073307..090828, plus Run_072640 raising before a marker). No deferred success log exists, so the success schema is proved from source only.

### Finding for the lead (runner predicate)

`Scripts/Editor/run_bk56_60_deferred_selection.ps1:174` requires `$activation -gt $spawn`, i.e. `deferred_selected` after `SPAWN PASS`. In source, activation happens synchronously inside `spawn_live_boss` (driver `:418-480`, `deferred_selected` logged at `RPGPlayerMovesSubsystem.cpp:1259` before `activate()` returns), while `SPAWN PASS` comes from `validate_spawn_navigation` on a later tick (driver `:836-841`). A real success would therefore fail the runner's own order check, so the runner can never report one. Suggested correction (the runner is a lead-claimed file): require `routeInit < activation < spawn < monitor < result`, `decision > activation` and `decision < result`, matching this verifier. Not applied here.

## BK-72/73: verifier extension (`Scripts/Tools/verify_bk56_60_receipts.py`)

A purported `SUCCESS` (`status.txt`) now also runs `verify_pie_log` on `deferred_pie.log`. The check fails closed when the log is missing. It requires:
- Each of the seven single markers exactly once (missing and duplicate markers are rejected), in the source order above (out-of-order is rejected, including the runner-predicate order).
- Route identity: `deferred_selected` and `DEFERRED_SELECTION` name the same definition (path forms `/Game/A/B` and `/Game/A/B.B` are equivalent) and the same hash.
- At least one `[CARD_DECISION]` after `deferred_selected` and before the result, each with a matching `[FrameworkProof] decision` trace, and seq values that are unique and increasing.
- A terminal outcome of `TimeCap` with `activeState=Active` or `BossDefeated`, and `saves=0` on the result. `Succeeded` (test-route-only), `Failed` and `ActivationRefused` are rejected.
- No test-start evidence (`autonomous_test_selection`, `COMBO_START`, `CARD accepted`, `PHASE2_PROBE`, `combo_test_start`), no save evidence (`saves=` nonzero, `LogSavePackage`, `Saving package`), and no refusal marker.

Existing failure classification is unchanged: a well-formed `failure_status.txt` is still `FAILURE` (exit 1).

## BK-74: fixtures (`Scripts/Tools/test_verify_bk56_60_receipts.py`)

A source-shaped `good_log()` builder copies the marker text from the emitting lines. 16 new cases:
- **Success:** TimeCap with two decisions, BossDefeated with one decision, and both definition path forms.
- **Rejected for missing evidence:** missing log (fail closed), TimeCap without a decision, a result marker alone, and a refusal log.
- **Rejected markers:** each of the seven markers missing, a duplicate marker, and the runner-predicate order.
- **Rejected identity and outcomes:** hash mismatch; outcomes `Succeeded`, `Failed`, `ActivationRefused`, and TimeCap without `activeState=Active`.
- **Rejected decisions:** a decision before activation, after the result, or without a trace; duplicate seq.
- **Rejected test-start and save evidence.**
- **Unchanged:** failure classification.

The earlier 17 cases now use the good log by default.

## BK-75: validation (exact)

- From `Scripts/Tools`: `python -I -m unittest discover -s . -p "test_verify_bk56_60_receipts.py"` → `Ran 33 tests ... OK`.
- `python -I -m py_compile Scripts/Tools/verify_bk56_60_receipts.py Scripts/Tools/test_verify_bk56_60_receipts.py` → OK.
- `git diff --check` on both files: clean.
- The real refusal log `BK_56_60/Run_20261111_090828/deferred_pie.log` through `verify_pie_log` is rejected: missing activation, spawn and monitor markers; outcome ActivationRefused; no decision; refusal marker.

## Limits (lead input)

1. "One production selector decision": the verifier requires at least one. A 45 s production Tick normally decides repeatedly, so "exactly one" would reject legitimate runs. Say so if exactly one is wanted.
2. The success schema is source-derived; no real deferred success log exists yet.
3. The runner predicate (above) blocks any success until it is corrected.
4. The success rule still requires `PIE_EXIT=0` (BK-66..70 limit): a successful run that crashes at exit would be `INVALID`.
5. A multi-line refusal snapshot splits the result line; this only affects refusal logs, which can never be a success anyway.

## Lead review and runner-order hotfix

Codex accepted the verifier/log-schema work after independently checking the source-order finding. The report is correct: `spawn_live_boss()` synchronously logs selected activation before returning, while `tick()` returns and waits for a later navigation-ready tick to log `SPAWN PASS`. The lead-owned runner incorrectly required activation after spawn, making a legitimate run fail its order gate. Codex corrected the order to `PACK_STYLE_READY < selected_route_initialized < deferred_selected < SPAWN PASS`, with a production decision after activation and before the result, and requires the monitor after spawn. Added an offline source contract pinning this source/runner order. Focused contracts pass 8/8 and the receipt verifier suite passes 33/33; PowerShell parse passes. The first live no-save run still needs owner-approved data and C-1155. No Unreal/build/PIE was run in this review.
