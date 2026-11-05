# Selector/start parity audit (Queue C S1, 2026-11-03)

## Result

No unintentional eligibility mismatch found in the current start paths. The ordinary selector path evaluates a card through `FRPGBossMoveModel::IsEligible`, then passes the same decision snapshot to `StartCard`; the only selector-memory value needed at start is cone slack, and that is copied from the chosen trace. Combo continuation and delayed combo starts bypass selector choice/cooldown/repeat scoring and use their current/fresh snapshots. However, every successful route calls `Selector.NoteStarted`, so combo cards update cooldown clocks, recent history, and tie offset for later normal selections; refusals do not. A model refusal ends the combo and resumes ordinary selection instead of failing the encounter. See Queue D D15 for the detailed audit.

## Filter comparison

| Condition | Selection | Start | Finding |
|---|---|---|---|
| Phase, target validity, neutral/model state, domain | `RPGBossMoveSelector.cpp:44–48` calls the shared model filter. | `RPGFrameworkMoveExecutor.cpp:120–126` calls the same `Model_.IsEligible`. | Same predicate. |
| Range and vertical limit | Shared `FRPGBossMoveModel::IsEligible` (`RPGBossMoveModel.cpp:30–44`). | Same model check at executor `:126`. | Same snapshot fields; no separate range-band recheck. |
| Cone / hysteresis | Selector builds a per-card snapshot and stores its `ConeHoldSlackDegrees` in the trace (`RPGBossMoveSelector.cpp:41–48`). | Normal start copies chosen trace slack before `StartCard` (`RPGFrameworkBossCharacter.cpp:518–519`). | AWR-004 fix keeps the selected card eligible at start. |
| Cooldown, repeat penalty, score, tie band | Selector-only scheduling/scoring (`RPGBossMoveSelector.cpp:50–78`). | Not checked by the move model at start. | Combo continuations follow authored edges and bypass these checks when choosing the next card; after successful start they still update selector memory via `NoteStarted` (`RPGFrameworkBossCharacter.cpp:799,815`), influencing future normal choices. |
| Range band and reposition | Boss movement branch handles outside-band return and inside-band turn before normal start (`RPGFrameworkBossCharacter.cpp:465–484`). | No card-start filter; card's own range is rechecked in shared model. | These are movement policy, not hidden duplicate eligibility conditions. |

## All StartCard callsites

- `RPGFrameworkBossCharacter.cpp:518–519`: normal selector start; passes snapshot used for selection plus the chosen trace's cone slack.
- `RPGFrameworkBossCharacter.cpp:795`: combo continuation start; uses current gate snapshot and bypasses selector policy for the authored edge; successful start records selector memory at `:799`, while refusal emits `combo_end` and falls through to normal next-decision logic.
- `RPGFrameworkBossCharacter.cpp:811`: paused combo continuation; calls `MakeSnapshot()` after the pause and bypasses selector policy for the authored edge; successful start records selector memory at `:815`, while refusal ends combo and returns to ordinary decision flow.

The F3-style pure `FRPGBossMoveModel` check does not know a boss band or reposition state. Those remain caller-level movement policy; adding them to `IsEligible` would change the model contract and is not indicated by the current code. No runtime change proposed.

## Regression coverage matrix (Queue C S5)

| Property | Existing coverage | Gap / next test |
|---|---|---|
| Range and phase refusal shared by selection/start | `RPGBossMoveSelectorTests.cpp` policy cases; `RPGBossMoveModelTests.cpp` eligibility cases. | Integrated selection-to-start same-snapshot test added in Queue C S2. |
| Cone slack copied to normal start | `StartConeSlack` selector regression and live 8-attack evidence (BUILD-173). | Integrated model start assertion added in Queue C S2. |
| Cooldown is selector-only | Selector policy tests exercise cooldown boundary; model start intentionally does not consume selector state. | Integrated two-card simulation will assert the selector controls next choice. |
| Reposition/band movement | Character code handles caller-level walk/turn; no pure card-model filter exists for it. | Live/proof coverage remains profile-specific; do not invent a StartCard eligibility rule. |
| Combo fresh-snapshot fallback | Source branches at `:795,811` explicitly end combo on refusal. | A pure integration test will verify the selector/model generation lifecycle; world movement remains outside this no-engine test. |

Sources: `RPGBossMoveSelector.cpp`, `RPGBossMoveModel.cpp`, `RPGFrameworkMoveExecutor.cpp`, and `RPGFrameworkBossCharacter.cpp` at the lines above. No build, test, or editor run was performed for this audit.
