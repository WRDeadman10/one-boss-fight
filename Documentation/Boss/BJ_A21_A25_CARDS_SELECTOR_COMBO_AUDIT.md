# BJ-A21..BJ-A25: Move Cards, Weighted Selector & Combo Graph Audit

**Authority:** [`QUEUE_BJ_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BJ_AG.md) Batch 5 (`BJ-A21..BJ-A25`)  
**Scope:** Strictly read-only C++/test-source audit (`0` asset/build/engine/commit operations).

---

## 1. `BJ-A21`: Card Validation vs Consumers (`RPGBossMoveCard.cpp`, `RPGBossMoveModel.cpp`)

- [`RPGBossMoveCards::Validate`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossMoveCard.cpp#L55-L210) validates identity (`Schema == 1`, `MoveId`, `FamilyId`, `PhaseId`), `AdditionalPhaseIds` (`<= 4`, distinct, `!= PhaseId`), single animation source (`Sequence != Montage`), skeleton match, `SlotName`/`SectionName`, `!bUsesRootMotion`, finite numeric bounds `[0, 1e6]`, mutually exclusive add-ons (`AreaEffect` vs `ChannelDrain` vs `bDefensive`), warp/hold/cue bounds, and ordered/non-overlapping hit windows.
- [`FRPGBossMoveModel::IsEligible`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossMoveModel.cpp#L16-L46) re-checks `RPGBossMoveCards::Validate` cleanly before phase (`IsEligibleInPhase`), range `[MinRangeCm, MaxRangeCm]`, cone (`FrontConeDegrees` + `ConeHoldSlackDegrees`), vertical limit (`MaxVerticalDeltaCm`), and strictly increasing `FrameId` (`>` `LastStartFrame`) / non-decreasing `ClockSeconds`.

---

## 2. `BJ-A22`: Weighted Selector Cooldown, Repeat & Tie Behavior (`RPGBossMoveSelector.cpp`)

Verified [`FRPGBossMoveSelector`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossMoveSelector.cpp#L8-L96):
- Hard filter order: `Model.IsEligible` -> `Selector.Cooldown` (`LastStartClock[I] >= 0.0 && Clock - LastStartClock[I] < CooldownSeconds`, `:55`) -> score (`Weight * RangeFactor * Repeat * Pattern`, `:60-66`).
- Deterministic ties (`TieBand == 0`): first lowest-index max wins (`T.Score > Out.Score`, `:67`); `TieBand > 0`: seeded `FRandomStream(TieSeed + StartedCount)` over top tier (`Score >= Out.Score * (1 - TieBand)`, `:72-82`).
- **Minor Edge Conditions (`Low`):**
  1. `RPGBossMoveSelector.cpp:52-54`: `ConeInside` hysteresis memory only clears on explicit `"MoveModel.Cone"` refusal (`Error == TEXT("MoveModel.Cone")`); if candidate `I` fails `MoveModel.Phase` or `MoveModel.Range` first while leaving cone inside, `ConeInside[I]` stays `true` until a future `"MoveModel.Cone"` failure or `Reset()`.
  2. `RPGBossMoveSelector.cpp:22-25, 66`: Extreme domain-valid multipliers (up to `1e6` each across `Weight`, `Kite`, `Hug`, `BackDodge`, `Greed`) cast `double -> float` can overflow `FLT_MAX` (`+inf`), making `Out.Score * (1 - TieBand)` evaluate `+inf` cleanly (`Threshold == +inf`) while masking relative scores of finite contenders.

---

## 3. `BJ-A23`: Combo Graph Validation & Abort Fallback (`RPGBossComboRules.h`, `RPGBossComboAbortRules.h`)

- `Validate(Graph)` (`RPGBossComboRules.h:50-71`) rejects empty graphs, `MaxDepth` outside `[1..3]`, missing `Root`, empty/duplicate nodes, unknown targets or empty `MoveId`, out-of-range edge domains (`Min <= Max`, `Yaw in [0,180]`, `Pause in [0,5]`), cycles anywhere (including unreachable nodes via `LongestPathFrom`), and root path `> MaxDepth`.
- `Step(Graph, State, Gate)` (`:74-92`): ignores stale `Gate.GateId == S.LastGateId`, refuses `GateId == 0` / invalid target (`Recover`), finishes on leaf (`Edges.Num() == 0` -> `Finished`), else selects first matching edge in authored order or falls back to `Combo.DefaultRecovery` (`Recover`).
- `RPGBossComboAbort::ShouldAbort`: strictly requires `bComboActive && AcceptedHits == 0 && bFirstHitParried`. If a selected continuation fails fresh `Model.Start(...)` (e.g. phase switch or cone exit), `FBossComboFallbackAfterModelRefusal` leaves `Model` `Idle` for normal `Selector.Select` fallback.

---

## 4. `BJ-A24..BJ-A25`: Test Comparison & Bounded Disposition

- **Mapped Tests (`0` pure-rule defects):** `RPGBossMoveCardTests.cpp` (+ Hold/Warp boundary/mutation suites), `RPGBossMoveModelTests.cpp`, `RPGBossMoveSelectorTests.cpp`, `RPGBossComboTests.cpp`, `RPGBossComboFallbackTests.cpp`, `RPGBossComboPropertyTests.cpp`, `RPGBossComboParriedSampleTests.cpp`, `RPGBossComboAbortRulesTests.cpp`.
- **Named Follow-Up Test Cases:** (a) `ConeInside` retention across non-cone refusal (`MoveModel.Range`/`MoveModel.Phase`), and (b) selector float-score clamp/finite guard if high multipliers `> 1e9` are ever authored (`0` edits made offline).
