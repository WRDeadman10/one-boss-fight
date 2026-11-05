# Move selector and cone memory

`FRPGBossMoveSelector` is deterministic selection logic; it does not read the world or start playback. The public contract says stage one applies model eligibility and cooldown, then stage two scores eligible cards by configured weight, range preference, repeat penalty, and pattern factors. Highest score wins; ties use lowest index unless the opt-in seeded `TieBand` is enabled (`RPGBossMoveSelector.h:39-45`).

## Decision path

`Initialize` validates and stores candidate/config data and resets per-card start clocks, recent history, and cone memory (`RPGBossMoveSelector.cpp:8-30`). `Select` creates a trace for every candidate, applies model eligibility and cooldown refusal first, and only then computes its score (`:33-68`). The optional tie band uses a bounded seeded pick from the top score tier (`:70-80`). `ChosenIndex == INDEX_NONE` means no eligible candidate; caller policy decides whether to fail, wait, or use a fallback (`RPGBossMoveSelector.h:32-37`).

## Reading the runtime trace

The boss assigns one monotonic `seq` to each selector decision and emits it on each candidate, refusal, and decision row (`RPGFrameworkBossCharacter.cpp:455-467,515-520`; `RPGFrameworkBossCharacter.h:73-74`). `attack` is `AttacksDone+1`, the attack-budget slot; it is not a unique decision ID and can repeat after an aborted start. `seq` is the correlation key. Candidate `score` is dimensionless: `Weight × RangeFactor × RepeatFactor × PatternFactor`; `range` on the chosen decision is centimeters. Pattern multipliers may include kite/hug, back-dodge, greed, and preferred aggro band (`RPGBossMoveSelector.cpp:60-68`). The trace prints the final score, not each factor, weight, candidate range, cooldown clock, recent-history membership, or active pattern-factor breakdown.

| Runtime row | Interpretation |
|---|---|
| `candidate attack=N card=... score=S seq=Q` | Model and cooldown filters passed; `S` is the final dimensionless score. |
| `refusal attack=N card=... reason=MoveModel.* seq=Q` | Model hard-filter refusal, e.g. `MoveModel.Range`, `.Cone`, `.Phase`, `.Vertical`, `.Generation`, or `.State`. |
| `refusal ... reason=Selector.Cooldown` | Model checks passed, but the card's prior-start clock is still inside `CooldownSeconds`. |
| `decision attack=N chosen=... score=S range=R phase=P seq=Q` | The selected candidate after score/tie handling; `R` is cm and `P` is the decision phase. |
| `cone_hysteresis degrees=D seq=Q` | Configured extra full-cone slack in degrees. This aggregate line does not log each candidate's actual `ConeHoldSlackDegrees`; that value is retained in the in-memory trace and copied into the matching start snapshot (`RPGFrameworkMoveSelector.h:37-40`; boss `.cpp:518`). |

| Config/trace field | Unit / meaning |
|---|---|
| `RepeatPenalty` | Dimensionless score multiplier in (0,1]. |
| `RepeatMemory` | Count of most recently started cards remembered (1..8). |
| `TieBand` | Dimensionless fraction of best score defining the top tier (0..0.5); 0 disables seeded tie selection. |
| `TieSeed` | Integer seed; actual stream seed adds `StartedCount`. |
| Candidate `CooldownSeconds` | Seconds since the same card last successfully started. |
| Candidate `Weight` and kite/hug/back-dodge/greed multipliers | Dimensionless positive score factors. |
| `ConeHysteresisDegrees` / `ConeHoldSlackDegrees` | Degrees of extra full-cone width; model expands each side by half that amount. |
| Snapshot/decision `RangeCm` | Horizontal boss-target distance in cm. |
| Candidate/decision `Score` | Dimensionless final score; no physical unit. |
| Trace `attack` / `seq` | Integer attack-budget slot / monotonically increasing decision correlation sequence, respectively. |

With `TieBand=0`, equal scores resolve to the lowest candidate index. With positive `TieBand`, candidates scoring at least `best × (1-TieBand)` form the top tier and a seeded stream chooses within it; seed offset is the number of cards actually started (`RPGBossMoveSelector.cpp:70-82,85-89`). Current runtime rows do not emit the configured band, seed, tier members, or random pick, so logs alone cannot establish that a near-tie occurred or why a chosen candidate entered the tier. Read the profile/config alongside the trace. Do not infer a tie from rounded display scores.

Example: retained `B_AWR002/pie_shift/editor_raw.log:1778-1782` correlates `seq=2`: the slow card is refused for cooldown, medium and heavy cards for range, AntiGreed is eligible at score `0.509475`, then selected at range `184.1 cm` in `Phase_1`. The row proves the emitted decision and reasons for that run; it does not expose the candidate's factor decomposition. In `B_AWR004/pie_run1/editor_raw.log:1581-1586`, `cone_hysteresis degrees=6`, two candidate scores, and the chosen decision share `seq=1`; per-card slack is not printed.

## Cone hysteresis

When configured above zero, `ConeInside` remembers which candidates were inside the cone on the previous selection. Those candidates receive extra cone slack on the next check, reducing edge flapping. A cone refusal clears that candidate's memory, and disabling the feature clears all cone memory (`RPGBossMoveSelector.cpp:44-53`). The model treats `FrontConeDegrees` and added slack as full-cone widths, so the signed-yaw half-angle grows by `slack / 2` (`RPGBossMoveModel.cpp:35-42`). This mutable map is observational selector state despite `Select` being `const` (`RPGBossMoveSelector.h:65-69`).

Cooldown begins only after the caller confirms the card really started with `NoteStarted`; that call also updates bounded repeat history (`RPGBossMoveSelector.cpp:84-89`). `Reset` clears cooldown clocks, repeat history, tie-seed offset and cone memory for a new encounter (`:91-94`).
