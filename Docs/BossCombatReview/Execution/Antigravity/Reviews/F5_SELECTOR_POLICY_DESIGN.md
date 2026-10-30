# F5 Framework Boss Selector Policy Design

**Document Version:** 1.0.0  
**Date:** 2026-10-30  
**Context:** Order A-280 (responding to C-407).  
**Scope:** Architectural specification for a minimal, deterministic multi-card selector policy for `RPGFrameworkBossCharacter` in Slice F5. Bridges Stage 1 hard eligibility filters and Stage 2 deterministic utility arbitration. Defines explicit mapping to requirements `BOSS-SEL-001..010` from `WITNESS_PLAN_82.md` with exact proposed test assertion lines and structured log signatures.  
**Implementation Constraint:** Pure specification and design; offline only; zero C++ code written.

---

## 1. Executive Summary & Design Principles

The F4 framework slice proved end-to-end execution of a single hardcoded card (`Swing1_Slow`) from walk arrival through damage window hit-registration. Slice F5 expands this pipeline to support dynamic multi-card selection across four candidate attack cards:
1. `Move_Sevarog_SwingSlow` (`Swing1_Slow`)
2. `Move_Sevarog_SwingMedium` (`Swing1_Medium`)
3. `Move_Sevarog_AntiGreed` (`Swing1_FAST_v2`)
4. `Move_Sevarog_HeavySlam` (`Swing3_Slow`)

### 1.1 Core Principles
* **Hard Filters Precede Scoring:** A card failing any geometric or state gate is strictly excluded prior to scoring; no utility calculation or random draw ever evaluates an ineligible candidate.
* **Deterministic Reproducibility:** Card choice is governed either by pure argmax utility or a seeded pseudo-random number generator (`FRandomStream`). Given identical world state and seed, decision sequences are 100% reproducible.
* **Anti-Looping & Pacing:** Explicit per-card cooldown timers and an execution history ring buffer ($K=2$) prevent the boss from spamming a single move.
* **Graceful Fallback:** If zero cards are eligible, the boss transitions safely to neutral strafe/repositioning locomotion without stalls or null-pointer dereferences.

---

## 2. Selector Architecture & Pipeline

The selector operates as a two-stage evaluation pipeline invoked upon decision ticks:

```
+-------------------------------------------------------------------------+
|                           Incoming Decision Tick                         |
|     (Target Transform, Boss Transform, Boss State, Phase, Game Time)    |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                  STAGE 1: HARD ELIGIBILITY FILTERS                       |
|                                                                         |
|  [State Gate]         Is actor neutral or in combo window?              |
|  [Phase Gate]         Card->Spec().PhaseId == CurrentPhaseId?           |
|  [Target Gate]        Target alive, valid, and within sight?            |
|  [Range Gate]         MinRangeCm <= RangeCm <= MaxRangeCm?              |
|  [Cone Gate]          |SignedYawDegrees| <= 0.5 * FrontConeDegrees?     |
|  [Asset Gate]         Montage / Sequence loaded and valid?              |
|  [Cooldown Gate]      ClockSeconds - LastExecutedTime >= CooldownSec?   |
+-------------------------------------------------------------------------+
           |                                              |
     (All Pass)                                     (Any Fail)
           v                                              v
+-----------------------+                    +----------------------------+
| Candidate Admitted to |                    | Card Refused: Emit         |
| Scoring Pool          |                    | [CARD_REFUSAL] Reason=...  |
+-----------------------+                    +----------------------------+
           |
           v
+-------------------------------------------------------------------------+
|                  STAGE 2: DETERMINISTIC UTILITY SCORING                  |
|                                                                         |
|  For each admitted candidate i:                                         |
|    U_base       = Card->Spec().BaseUtility (authored default 1.0)       |
|    F_distance   = Distance sweet-spot factor in [0.5, 1.0]              |
|    P_history    = Anti-repeat penalty factor (0.2 if last, 0.6 if 2nd)  |
|    Score_i      = U_base * F_distance * P_history                       |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                     STAGE 3: ARBITRATION & CHOICE                       |
|                                                                         |
|  Mode A (Pure Deterministic Argmax):                                    |
|    Winner = argmax(Score_i); ties broken alphabetically by MoveId.       |
|                                                                         |
|  Mode B (Seeded Bounded PRNG):                                          |
|    Normalized weight W_i = Score_i / Sum(Score_j);                       |
|    Roulette selection driven by FRandomStream(Seed).                    |
|                                                                         |
|  Emit: [CARD_DECISION] MoveId='...' Score=... Range=... Seed=...        |
+-------------------------------------------------------------------------+
           |                                              |
     (Winner Chosen)                             (Pool is Empty)
           v                                              v
+-----------------------+                    +----------------------------+
| Dispatch Move to      |                    | Fallback Task:             |
| Execution Authority   |                    | Neutral Strafe/Reposition  |
+-----------------------+                    +----------------------------+
```

---

## 3. Mathematical Utility Model

### 3.1 Distance Sweet-Spot Weighting ($F_{\text{distance}}$)
Each card has a kinematic sweet spot $D_{\text{sweet}} = 0.5 \times (\text{MinRangeCm} + \text{MaxRangeCm})$.
The distance alignment factor penalizes candidates operating near the extreme boundaries of their range band:
$$F_{\text{distance}}(D) = 1.0 - 0.5 \times \left( \frac{|D - D_{\text{sweet}}|}{0.5 \times (\text{MaxRangeCm} - \text{MinRangeCm})} \right)^2$$
Bounded within $[0.50, 1.00]$.

### 3.2 Anti-Repeat History Penalty ($P_{\text{history}}$)
The selector maintains an execution history ring buffer: $H = [M_{t-1}, M_{t-2}]$.
* If candidate $M_i == M_{t-1}$ (executed on immediately preceding step):
  $$P_{\text{history}} = 0.20 \quad \text{[DESIGN VALUE, PROPOSED]}$$
* If candidate $M_i == M_{t-2}$ (executed 2 steps ago):
  $$P_{\text{history}} = 0.60 \quad \text{[DESIGN VALUE, PROPOSED]}$$
* Otherwise (not in recent history):
  $$P_{\text{history}} = 1.00$$

### 3.3 Cooldown Hard Lockout
In addition to the soft anti-repeat history penalty, each card possesses an explicit cooldown duration:
* `CooldownSeconds` authored per card (e.g., $3.0\text{ s}$ for `HeavySlam`, $1.5\text{ s}$ for `SwingSlow`).
* Hard rejection: if $t_{\text{current}} - t_{\text{last\_executed}} < \text{CooldownSeconds}$, the card is refused in Stage 1 with reason `MoveModel.Cooldown`.

---

## 4. Mapping to WITNESS_PLAN_82 Requirements (BOSS-SEL-001..010)

This matrix defines the exact verification method, proposed C++ test assertion file and line, and structured log signature required to graduate each row from `PARTIAL` / `NOT YET` to `WITNESSED`:

| Req ID | Title | Selector Mechanism | Verification Mechanism | Proposed C++ Test Assertion / Exact Log Signature |
| :--- | :--- | :--- | :--- | :--- |
| **BOSS-SEL-001** | Legal decision gates | Selector verifies boss is in neutral locomotion state or open combo cancel window before querying cards. | Automation Unit Test + PIE | `TestTrue(TEXT("State refusal"), Error.Contains(TEXT("MoveModel.State")));`<br>Log: `[CARD_REFUSAL] Card=Move_Sevarog_SwingSlow Reason=MoveModel.State State=Staggered` |
| **BOSS-SEL-002** | Hard-filter precedence | Range, cone, and phase checks execute prior to utility scoring; failed candidates produce 0 score calls. | Automation Unit Test | `RPGBossMoveModelTests.cpp:46` (`TestTrue("Refusal range", Error.Contains(TEXT("MoveModel.Range")))`);<br>Log: `[CARD_REFUSAL] Card=Move_Sevarog_SwingSlow Reason=MoveModel.Range Range=250.0 Min=100.0 Max=200.0` |
| **BOSS-SEL-003** | Executable asset gate | Cards missing sequence/montage or skeleton bindings are refused during profile load and selector tick. | Automation Unit Test | `RPGBossMoveCardTests.cpp:96` (`TestTrue("Refusal missing sequence", Issues.Errors.Contains(TEXT("Card.Sequence.Invalid")))`);<br>Log: `[CARD_REFUSAL] Card=Move_NullAnim Reason=Card.Sequence.Invalid` |
| **BOSS-SEL-004** | Normalized utility | `ScoreMove` evaluates candidate utility deterministically; candidate with highest composite score is selected. | Automation Unit Test | `TestEqual(TEXT("Argmax selects highest utility"), SelectedCard->MoveId, TEXT("Move_Sevarog_SwingSlow"));`<br>Log: `[CARD_DECISION] Selected=Move_Sevarog_SwingSlow Score=1.85 CandidateCount=3` |
| **BOSS-SEL-005** | Bounded randomness | Seeded PRNG selection (`FRandomStream(Seed)`) produces 100% identical sequence across 1000 iterations. | 1000-iteration Seeded Test | `TestEqual(TEXT("Deterministic seed reproducibility"), RunA_History, RunB_History);`<br>Log: `[SELECTOR_SEED_TEST] Iterations=1000 Seed=1337 DivergenceCount=0` |
| **BOSS-SEL-006** | Cooldown semantics | Card executed at $t_0$ is hard-filtered until $t_0 + \text{CooldownSeconds}$ has elapsed. | Automation Unit Test | `TestTrue(TEXT("Cooldown active refusal"), Error.Contains(TEXT("MoveModel.Cooldown")));`<br>Log: `[CARD_REFUSAL] Card=Move_Sevarog_HeavySlam Reason=MoveModel.Cooldown Elapsed=1.2s Required=3.0s` |
| **BOSS-SEL-007** | Anti-repeat memory | Last executed card receives $0.2\times$ utility penalty, forcing alternate card selection when scores are close. | Automation Unit Test | `TestEqual(TEXT("Anti-repeat selects alternative"), SelectedCard->MoveId, TEXT("Move_Sevarog_SwingMedium"));`<br>Log: `[CARD_SCORE] Card=Move_Sevarog_SwingSlow Base=1.00 HistoryPenalty=0.20 FinalScore=0.20` |
| **BOSS-SEL-008** | No-candidate fallback | When all offensive cards refuse, selector returns null token without error; AI triggers strafe locomotion. | Automation Test + PIE | `TestNull(TEXT("No candidate returns null token"), SelectedToken);`<br>Log: `[SELECTOR_FALLBACK] EligibleCount=0 Action=NeutralStrafe / Reposition` |
| **BOSS-SEL-009** | Reaction latency & budget | Boss counter-attack trigger to player action (flask / heavy recovery) is bounded by reaction window $[0.20, 0.40]\text{ s}$. | Automation Test / Probe | `TestTrue(TEXT("Reaction delay bounded"), Delay >= 0.20f && Delay <= 0.40f);`<br>Log: `[CARD_REACTION] Trigger=PlayerFlask Latency=0.25s CounterCard=Move_Sevarog_AntiGreed` |
| **BOSS-SEL-010** | Decision trace | Every decision tick emits a single structured telemetry line detailing chosen card, score, range, cone, and seed. | Telemetry Log Probe | Regex Match: `^\[CARD_DECISION\] MoveId=\S+ Score=\S+ Range=\S+ Cone=\S+ Seed=\S+$`<br>Log: `[CARD_DECISION] MoveId=Move_Sevarog_SwingMedium Score=1.45 Range=145.2 Cone=12.4 Seed=1337 Cooldown=0.0` |

---

## 5. Candidate Move-Card Profile Setup for Slice F5

To support multi-card testing, the boss profile data asset must bind the four reach-derived cards with their respective cooldowns and base utilities:

| Card ID | Target Animation | Derived Range $[\text{Min}, \text{Max}]$ | Derived Cone | Cooldown | Base Utility | Strategic Role |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`Move_Sevarog_SwingSlow`** | `Swing1_Slow` | $[100.0, 200.0]\text{ cm}$ | $90.0^\circ$ | $1.5\text{ s}$ | $1.00$ | Baseline heavy frontal sweep |
| **`Move_Sevarog_SwingMedium`**| `Swing1_Medium` | $[90.0, 180.0]\text{ cm}$ | $90.0^\circ$ | $1.0\text{ s}$ | $1.20$ | Fast frontal combo starter |
| **`Move_Sevarog_AntiGreed`** | `Swing1_FAST_v2` | $[90.0, 185.0]\text{ cm}$ | $100.0^\circ$ | $2.5\text{ s}$ | $1.50$ | Fast punish / flask counter |
| **`Move_Sevarog_HeavySlam`** | `Swing3_Slow` | $[90.0, 180.0]\text{ cm}$ | $60.0^\circ$ | $3.5\text{ s}$ | $1.30$ | Focused vertical slam |

---

## 6. Execution Authority & Rollback Interface

The selector coordinates with the character execution authority:
1. **Decision Query:** Character ticks -> calls `FRPGBossMoveModel::SelectMove(BlackboardState, Seed)`.
2. **Reservation Token:** If a candidate is chosen, a reservation token (`FRPGBossMoveInstanceToken`) is stamped `State = Committed` prior to montage dispatch (satisfying `BOSS-EXE-002`).
3. **Playback Dispatch:** Character calls `PlayAnimMontage(Card->ResolvedMontage())`.
4. **Failure Rollback:** If `PlayAnimMontage` returns $0.0\text{ s}$, character immediately cancels the reservation token and transitions back to `Idle` (satisfying `BOSS-EXE-003`).
5. **Completion Handshake:** Montage completion notify or timeout watchdog stamps `State = Completed`, updates `LastExecutedTimestamp = ClockSeconds`, and pushes the card ID into the history ring buffer.
