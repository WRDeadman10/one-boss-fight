# KI-149: Phase Cooldown Exhaustion and Selectable Card Guarantees

**Document ID**: `KI149_COOLDOWN_EXHAUSTION_DESIGN.md`  
**Author**: Antigravity  
**Lead Orders**: `[C-431]`, `[C-432]`  
**Context**: Root cause analysis, architectural evaluation, and design remedies for Known Issue KI-149 (`Framework.Selector.NoCandidate` under 2-card cooldown exhaustion)  
**Status**: DESIGN COMPLETE  

---

## 1. Executive Summary & Incident Analysis

During the verification of Slice F6c Encounter Restart in `restart_run1` (`Docs/BossCombatReview/Execution/Claude/F6c/restart_run1/editor_raw.log`), the framework boss successfully executed:
1. Generation 1 Attack 1 (`SwingSlow_F5`, Phase 1)
2. Phase Transition to Phase 2 at HP 50/250 (`phase_transition attack=2 from=Phase_1 to=Phase_2`)
3. Generation 1 Attack 2 (`SwingMedium_P2`, Phase 2)
4. Lethal termination (`boss_dead generation=1 executorAborted=1`)
5. Encounter Reset (`encounter_reset generation=2 oldState=Dead executorRearmed=1 bossHealth=250`)
6. Generation 2 Attack 1 (`SwingSlow_F5`, Phase 1)
7. Generation 2 Attack 2 (`AntiGreed_F5`, Phase 1)

However, at Generation 2 Attack 3 (line 782), the encounter abruptly failed closed:
```
[FrameworkProof] refusal attack=3 card=Move_Sevarog_SwingSlow_F5 reason=Selector.Cooldown
[FrameworkProof] refusal attack=3 card=Move_Sevarog_AntiGreed_F5 reason=Selector.Cooldown
[FrameworkProof] refusal attack=3 card=Move_Sevarog_SwingMedium_P2 reason=MoveModel.Phase
[FrameworkProof] refusal attack=3 card=Move_Sevarog_HeavySlam_P2 reason=MoveModel.Phase
[FrameworkProof] cleanup reason=Framework.Selector.NoCandidate modelIdle=1 ownedMontageStopped=1
[FrameworkProof] ERROR token=Framework.Selector.NoCandidate bossInactive=1
```

### Root Cause
In Phase 1, the authored candidate pool contains exactly **two** cards:
- `Move_Sevarog_SwingSlow_F5`: Cooldown = 3.0s (or 1.5s), animation length = 1.70s.
- `Move_Sevarog_AntiGreed_F5`: Cooldown = 2.5s, animation length = 0.53s.

The boss profile authors `AttackCount = 3` (`RPGBossFrameworkProfile.h:47`).
- Attack 1 starts at $t_0$, putting `SwingSlow` on cooldown until $t_0 + 3.0\text{s}$.
- Attack 1 finishes at $t_1 \approx t_0 + 1.7\text{s}$. The boss immediately selects Attack 2 (`AntiGreed`), putting `AntiGreed` on cooldown until $t_1 + 2.5\text{s} \approx t_0 + 4.2\text{s}$.
- Attack 2 finishes at $t_2 \approx t_1 + 0.53\text{s} \approx t_0 + 2.23\text{s}$.
- At $t_2$, the boss enters neutral and evaluates Attack 3:
  * `SwingSlow` remaining cooldown: $3.0 - 2.23 = +0.77\text{s} > 0$. -> Refused `Selector.Cooldown`.
  * `AntiGreed` remaining cooldown: $4.2 - 2.23 = +1.97\text{s} > 0$. -> Refused `Selector.Cooldown`.
  * `SwingMedium_P2` & `HeavySlam_P2`: Phase 2 cards. -> Refused `MoveModel.Phase`.

Because all Phase 1 cards are on cooldown and Phase 2 cards are filtered by phase authority, `Selector.Select` returns `ChosenIndex == INDEX_NONE`.
In `RPGFrameworkBossCharacter.cpp:114`:
```cpp
if (!bAsked || Decision.ChosenIndex == INDEX_NONE) { Fail(TEXT("Framework.Selector.NoCandidate")); return; }
```
The boss character treats cooldown starvation as a fatal state-machine fault and halts the encounter.

---

## 2. Design Evaluation: Static Validator vs Runtime Fallback

Two complementary approaches exist to guarantee that a boss phase never starves itself.

```
                      +---------------------------------------+
                      |       Phase Cooldown Defense          |
                      +---------------------------------------+
                                          |
                +-------------------------+-------------------------+
                |                                                   |
                v                                                   v
    +-----------------------+                           +-----------------------+
    |   Tier 1: Preflight   |                           |    Tier 2: Runtime    |
    |   Profile Validator   |                           |    Neutral Recovery   |
    +-----------------------+                           +-----------------------+
    | * Cardinality >= 2    |                           | * Neutral Idle Delay  |
    | * 0-Cooldown Filler   |                           | * Un-cooldown Fallback|
    | * Worst-case Duration |                           | * Bounded Timeout     |
    +-----------------------+                           +-----------------------+
```

### 2.1 Approach A: Profile Preflight Validator Rule (Static Guarantee)
- **Concept**: Reject invalid boss profiles during asset validation / dependency resolution before PIE or gameplay starts.
- **Hook Location**: `Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp:90-98` in `RPGFramework::ResolveProfile`.
- **Existing Logic**:
  ```cpp
  // Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp:92-97
  if (P->PhaseTwoFraction > 0.f)
  {
      const FName One = D->Candidates[0].Card->Spec().PhaseId; int32 InOne = 0, InTwo = 0;
      for (const auto& C : D->Candidates)
      {
          const FName Id = C.Card->Spec().PhaseId;
          if (Id == One) ++InOne; else if (Id == P->PhaseTwoId) ++InTwo;
          else { Error = TEXT("Framework.Profile.PhaseCards"); return false; }
      }
      if (One == P->PhaseTwoId || InOne < 1 || InTwo < 1) { Error = TEXT("Framework.Profile.PhaseCards"); return false; }
  }
  ```
- **Proposed Enhancement**:
  1. **Minimum Phase Cardinality**:
     If `P->AttackCount >= 2`: each phase must have at least $\min(3, P->AttackCount)$ cards, OR at least one card in each phase must have `CooldownSeconds == 0.0` (un-cooldown-gated baseline filler).
     ```cpp
     int32 ZeroCdOne = 0, ZeroCdTwo = 0;
     for (const auto& C : D->Candidates)
     {
         if (C.CooldownSeconds <= 0.0f)
         {
             if (C.Card->Spec().PhaseId == One) ++ZeroCdOne;
             else ++ZeroCdTwo;
         }
     }
     if ((InOne < 2 && ZeroCdOne == 0) || (InTwo < 2 && ZeroCdTwo == 0))
     {
         Error = TEXT("Framework.Profile.PhaseCooldownStarvation");
         return false;
     }
     ```
  2. **Worst-Case Turnaround Check**:
     For a 2-card phase $\{A, B\}$, $A$ and $B$ cannot starve each other if and only if:
     $$\text{Cooldown}(A) \le \text{RecoveryEnd}(B) \quad \text{and} \quad \text{Cooldown}(B) \le \text{RecoveryEnd}(A)$$
     If either cooldown exceeds the opposing animation's recovery duration, consecutive alternation will inevitably starve.
- **Evaluation**:
  * *Strengths*: Completely eliminates static authoring flaws at build/cook time; zero runtime cost in Tick.
  * *Weaknesses*: Cannot account for dynamic conditions (e.g. if the player moves out of range of Card $A$, only Card $B$ is in range, so Card $B$ still starves even if Card $A$'s cooldown expired).

---

### 2.2 Approach B: Runtime Neutral Recovery & Fallback (Dynamic Guarantee)
- **Concept**: When all cards in the current phase are valid by range and model but temporarily on cooldown, the boss does **not** fail closed. Instead, the boss treats this as normal combat pacing.
- **Hook Location**: `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:100-112`.
- **Existing Logic**:
  ```cpp
  // Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:114
  if (!bAsked || Decision.ChosenIndex == INDEX_NONE) { Fail(TEXT("Framework.Selector.NoCandidate")); return; }
  ```
- **Proposed Runtime Recovery Mechanisms**:

#### Option B1: Neutral Pacing / Cooldown Wait Loop (Recommended for Souls-like Fidelity)
In Souls combat, when a boss finishes an attack and its follow-up moves are on cooldown, the boss remains in neutral (strafe, track player, idle breathing) until an attack cooldown elapses.
- In `RPGFrameworkBossCharacter.cpp`:
  Inspect `Decision.Traces`:
  * If ANY trace has `bEligible == false` with a non-cooldown refusal (e.g. `MoveModel.Phase`, `MoveModel.Dead`, `MoveModel.Stagger`), that is expected filtering.
  * If ALL candidates belonging to `CurrentPhaseId` were refused **exclusively** by `Selector.Cooldown`:
    The boss is in **Temporary Cooldown Starvation**.
  * Action: Do NOT call `Fail(...)`!
    - Leave `bStartedMove = false;`
    - Let Tick continue on subsequent frames.
    - The character movement continues facing/tracking the player in neutral.
    - On the subsequent frame where `ClockSeconds - LastStartClock[i] >= CooldownSeconds`, `Select` successfully returns the ready card!
  * Safety Gate: Introduce a bounded wait watchdog: `PhaseCooldownWaitSeconds += Delta;`. If `PhaseCooldownWaitSeconds > MaxAllowedCooldownWait` (e.g. 5.0s), fail closed with `Framework.Selector.CooldownTimeout`.

#### Option B2: Un-Cooldown-Gated Fallback Attack
- If `Decision.ChosenIndex == INDEX_NONE`, fall back to a designated default move (e.g. `DefaultAttackCard` or the phase card with the smallest remaining cooldown delta):
  ```cpp
  // Soft cooldown relaxation for emergency fallback
  int32 BestCandidate = FindCardWithSmallestCooldownRemaining();
  ```
- *Weakness*: Violates strict authoring cooldowns; can cause visual repetition.

---

## 3. Comparison & Synthesis

| Criterion | Static Preflight (Approach A) | Runtime Neutral Delay (Approach B1) | Runtime Fallback Card (Approach B2) |
|:---|:---:|:---:|:---:|
| **Prevents Authoring Blunders** | **YES (Compile/Preflight)** | No (Hides bad decks) | No |
| **Resilient to Player Kiting / Range** | No | **YES** | **YES** |
| **Souls-Like Combat Pacing** | Neutral | **YES (Natural strafe/wait)** | No (Spams moves) |
| **Respects Authored Cooldowns** | **YES** | **YES** | No (Violates cooldowns) |
| **Risk of CI Hang / Freeze** | **Zero** | Low (Watchdog bounded) | Zero |

---

## 4. Recommended Architectural Specification

We recommend a **Dual-Tier Guard**:

1. **Tier 1 (Authoring Rule in `RPGBossFrameworkProfile.cpp:92`)**:
   Enforce that each phase in `URPGBossFrameworkProfile` must contain:
   - At least 2 cards.
   - At least one card with `CooldownSeconds <= 0.0f` OR at least 3 cards if all cooldowns are positive.
   - Emits preflight rejection token `Framework.Profile.PhaseCards` on violation.

2. **Tier 2 (Resilient Runtime Neutral Gate in `RPGFrameworkBossCharacter.cpp:114`)**:
   When `Decision.ChosenIndex == INDEX_NONE`:
   - Query if every phase-matched card was refused solely by `Selector.Cooldown`.
   - If yes: Log `[FrameworkProof] neutral_wait phase=<id> reason=CooldownStarvation`, remain in neutral (`bStartedMove = false`), and allow Tick to poll until the earliest cooldown expires (bounded by `WalkTimeoutSeconds`).
   - If no (e.g. zero cards configured for phase or all cards out of range): Fail closed immediately with `Framework.Selector.NoCandidate`.

This dual architecture guarantees that automated test runs never suffer spurious state-machine crashes from cooldown starvation while strictly upholding authoring invariants.
