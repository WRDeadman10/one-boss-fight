# SPEC M4: phase transition versus stance break (TASKS G2-6 rest, G2-8 rest)

Written 2026-10-21 by a read-only design agent. No file under Source/, Content/, Config/ or Scripts/ was changed. Paths without a folder are in `Source/OneBossFight/Player/`.
"Freeze N" is a line number of `Documentation/Master_Design_Freeze_v1_2_AI_Implementation_Ready.md`. Evidence words: read = I read the code on 2026-10-21; bridge = read-only editor query on 2026-10-21; unverified = not checked.
Known conflict inside the Freeze, resolved here: Freeze 729 (17.3 item 8) and 891 (21) leave the queue open; Freeze 770 (18.1) and 1201 (30.2 item 8, binding addendum) say "queue the transition behind the stance break". We follow 30.2 item 8.

## 1. Goal and Freeze requirements

Goal: every pair of (stance break, riposte, phase transition, death, encounter reset, A1 to A6 move) follows the Freeze priority table, no state can get stuck, and the change stays small (no new state machine, pack untouched).

| Ref | Freeze lines | Rule used here |
|---|---|---|
| States | 431-436, 445-448 (10.2, 10.3) | Staggered clears attack collision and owns the critical window. PhaseTransition blocks attack selection. Dead wins over every state. Resetting cancels montages, abilities, effects, timers, traces, tags, posture. |
| Priority | 889-896, 898 (21) | 1 Dead, 2 Reset, 3 Phase transition (except one queued behind an active riposte), 4 Accepted riposte, 5 Stagger, 6 Committed attack, 7 Selection (incl. heal punish), 8 Cosmetic. |
| Posture | 713-715 (17.2) | One break at zero. Clamp to zero and ignore more posture damage during the break. Refill to max at the end of the get-up. A cooldown must be visible, never a hidden ignore. |
| Break entry | 722-729 (17.3) | Item 2: disable traces, projectiles, attack windows. Item 3: cancel legal abilities, record what was cancelled. Item 8: PhaseTransition must not be interrupted by a normal break; Dead wins. |
| Riposte | 739, 742, 745 (17.4); 754, 757 (17.5) | Once per break. Fail-safe on every exit. Exactly one stagger when several hits cross zero. |
| Transition | 764-771 (18.1) | Idempotent. Evaluated only while alive and not transitioning. At start: block attack selection, clear traces, cancel pending heal punishes (766), pause posture regeneration and interaction by a documented policy, transition protection. Queue behind stagger and riposte, never start both (770). Remove protection at the end (771). |
| Queue | 1201 (30.2 item 8) | Non-lethal crossing during Staggered or an accepted riposte: queue until the earned critical opportunity resolves or expires. Lethal: Dead wins. |
| Death | 776-785 (18.2); 1269 (32.3) | Dead first. Cancel attack, stagger, riposte, phase. A lethal hit gets no posture damage, hit stun or new phase action. |
| Reset | 789-804 (18.3); 1265 (32.2) | Restore stagger, stance-break cooldown, critical window, riposte, phase flag, pending punish, projectiles. Safe twice. Stale callbacks check the generation. |
| Debug | 919, 922 (22) | Show posture, stance-break cooldown, phase flag, transition time, pending queued transition. |
| Tests | 994-996, 1001 (S05, S06, S07, S12); 985 (P07); 1005-1015 (L01 to L11) | Mapped in section 6. |
| Values | 1363, 1370, 1371 (36) | Threshold 0.60, stagger hold 2.5 s, cooldown 5.0 s (project default is 0 by decision G0-5, see section 8). |

## 2. Current state (read)

| # | Fact | Where |
|---|---|---|
| F1 | Phases polls health every 0.1 s. Start condition is `!bStaggered && Health/Max <= PhaseTwoHealthFraction` (0.6). Death (health <= 0) and dormancy return before it. | RPGBossPhases.cpp:49, 92-108; .h:29 |
| F2 | While `bTransition` the tick only waits for `TransitionEnd` (start + `TransitionSeconds` 1.8 s), then `FinishTransition`. | RPGBossPhases.cpp:84-91; .h:33 |
| F3 | `StartTransition` sets `bPhaseTwo` and `bTransition`, `++PhaseTwoCount`, holds the behaviour, applies `GE_HitStunImmune`, stops movement, plays the roar montage. It does not cancel A5, javelins, wave, blade, and does not touch posture. A missing roar montage is silent. | RPGBossPhases.cpp:157-199 |
| F4 | `FinishTransition`: death check (no buffs, no resume), buffs once (`bBuffsApplied`), leap unlock, resume. It never removes the immunity effect. The file has no "Remove Active Gameplay Effect" call (read, 475 lines). Effect duration is 4 s per DECISIONS.md:356 and RPGBossStagger.h:99 (not re-read). | RPGBossPhases.cpp:201-220, 222-244 |
| F5 | `ResetPhases`: clears `bTransition`, stops the roar, `bHeld=false`, removes buffs, `bPhaseTwo=false`. It does not remove the immunity effect. | RPGBossPhases.cpp:397-417 |
| F6 | `IsStaggered()` is `Phase != Idle` (Down or GetUp). The break entry is the edge of the pack's hit stun ability becoming active, plus `ForceBreakForTest`. Neither checks transition, death or dormancy. The cooldown is checked on the edge path only and only logged. | RPGBossStagger.h:104, 129; .cpp:68-89, 292-300 |
| F7 | `StartStagger` ends the pack flinch, applies immunity, holds behaviour, plays the fall clip (replaces the boss montage). It does not touch A5, javelin, wave, blade, posture or Phases. | RPGBossStagger.cpp:127-191 |
| F8 | `EndStagger` sets `CooldownEnd = Now + CooldownSeconds` (also when called by a reset), removes immunity by class, writes poise = max, optionally resumes behaviour. No hand-off to Phases. | RPGBossStagger.cpp:193-226 |
| F9 | `AbortStagger` returns at once when Idle, so a running cooldown survives a reset. | RPGBossStagger.cpp:302-307 |
| F10 | Death inside a stagger ends it without stopping the fall clip. A health rise (pack reset) ends it with resume. The riposte multiplier applies to the first hit after an accepted press within 1.2 s. | RPGBossStagger.cpp:323-361 |
| F11 | The riposte is a flag inside Down (`RiposteArmedUntil`, `bRiposteUsed`). No execution montage or lock exists yet (TASKS G2-7 open). The Light Attack handler needs `IsStaggered()`. | RPGBossStagger.h:149-150; .cpp:228-232; RPGRiposteInput.cpp:65 |
| F12 | Posture ticks every 0.05 s. Regeneration needs 0 < posture < max and 6 s since the last drain. The pack's own regeneration is disabled. Posture knows nothing about stagger or transition. | RPGBossPosture.cpp:37, 56-58, 79-93 |
| F13 | The pack gate (`GA_BaseHitReaction` "Can Activate Ability?") subtracts 20 (50 heavy) and at <= 0 refills the pool (DECISIONS.md:231, 312). Bridge node list of that function: Modify Attribute (-20), Get Current Attribute Value, float <= float, Set Current Attribute Value, Get Max Attribute Value; the execution wiring was not traced. The gate runs before the activation-blocked-tag check (DECISIONS.md:349). `BP_PoiseExtendedAttribute` has an empty EventGraph and its parent only forwards value updates (bridge): poise at 0 has no side effect inside the attribute Blueprints. | see left |
| F14 | A5 pending request ends by: "interrupted before the release", "never started" after 0.5 s, death, new generation. Flying javelins end only on hit, expiry, death, reset. No external cancel. | RPGBossHealPunish.cpp:62-70, 192-204, 239-245; RPGBossJavelin.cpp:96-114 |
| F15 | A4 blade ends when the tracker window closes ("move interrupted"), death or reset. Damage is our own code. | RPGBossLowSweep.cpp:137-203 |
| F16 | A6 wave ends only at max radius, death or reset. | RPGBossShockwave.cpp:143-146, 162-165 |
| F17 | Tracker ends an attack when the montage changes, vetoes a new attack during stagger, transition or dormancy, and `IsNeutral` includes all three plus dead. | RPGAttackTracker.cpp:126-138, 271-279, 300-318 |
| F18 | Encounter reset: `++Generation`, `AbortStagger`, `ResetPhases`, health and poise to max, sleep. | RPGBossEncounter.cpp:222-299 |
| F19 | A6 is locked until `FinishTransition`, so in normal play an A6 cannot be in flight when the single transition starts. | RPGBossPhases.cpp:75-78, 212-214 |
| F20 | HUD prompt needs `IsCriticalWindowOpen`. Overlay state label order is Dormant, PhaseTransition, Staggered; no Dead label; no counters for dropped breaks. | RPGBossHud.cpp:468; RPGCombatDebug.cpp:74-96 |
| F21 | Existing coverage: `pie_phase_reset.py` (queue behind a stagger, no gap timing), `pie_attack_rules.py` R1 to R3, `pie_a2_interrupts.py` (stagger and reset 12/12 each), `pie_a5_heal_punish.py` P04, P04b, P07, P09, `pie_player_death_reset.py`, `pie_leap_wave.py` W5, `pie_a4_low_sweep.py` S7, S8. | TEST_PLAN.md |

## 3. Gaps

| Gap | What is wrong | Matrix cells |
|---|---|---|
| G1 | No single priority gate for a break. Hook path breaks the roar. Real path relies on the pack immunity only. | BK08, BK09 |
| G2 | The immunity effect outlives the transition (about 2.2 s) and a reset. A legal break in that time is silently lost (Freeze 715). | BK08, RS01 |
| G3 | No posture policy in the roar. The pack gate refills the pool at 0, so built-up posture is lost. Freeze 766 wants a documented policy. | BK08, PO01 |
| G4 | During a break the pool shows full (the gate refilled it) and keeps cycling. Freeze 713 wants zero and ignore. | PO02 |
| G5 | Queue gap: the transition starts up to 0.1 s after the stagger ended and after the behaviour was resumed. | PH07 to PH09 |
| G6 | A stagger or a transition does not cancel javelins or the wave, does not clear A5 explicitly, and the blade ends one frame late. | BK03 to BK06, PH03 to PH06 |
| G7 | A dead boss can start a stagger (hook; real path unverified). The fall clip is never stopped. | BK10 |
| G8 | A dormant boss can start a stagger and wake up through `ResumeBehaviour`. | BK11 |
| G9 | The stagger cooldown survives a reset, and a reset during a stagger starts one. Harmless at the default 0. | RS02, RS03 |
| G10 | No counters or overlay lines for dropped breaks, queued transition, cooldown, posture hold (Freeze 919, 922). | BK12 |
| G11 | A break and a crossing in the same frame depend on component tick order. | PH13 |
| G12 | A missing roar montage or immunity class is silent. | edge cases |
| G13 | No driver covers break during the roar, immunity timeline, posture policy, hand-off gap, javelin or wave cancel. | all |

## 4. Design

### 4.1 Interaction matrix

Legend: Today = what the code does now (read). Required = Freeze rule. Change = the smallest edit. "none" = already right.

BREAK requested (BK):

| ID | State | Event | Today | Required | Change |
|---|---|---|---|---|---|
| BK01 | Neutral | break | Stagger starts (Stagger.cpp:77-83). | 17.3 | none; posture held at 0 (PO02) |
| BK02 | Committed attack with a pack trace (A1, A2, A3) | break | Fall clip replaces the attack, tracker ends it, no damage (A2-INT 12/12). | 17.3 items 2, 3, 5; log what was cancelled | `CancelOffence` logs the cancelled move |
| BK03 | A4 blade active | break | Blade ends when the tracker sees the montage change; up to one frame of damage in the break frame. | Blade off at once | `LowSweep.Cancel` |
| BK04 | A5 pending | break | Cleared next tick (tracker path) or after 0.5 s (never started). | Cleared at the break (21, 17.3) | `HealPunish.CancelAll` |
| BK05 | A5 javelin in flight | break | Flies on. | 17.3 item 2: projectiles disabled | `CancelAll` cancels it (data flag, Q1) |
| BK06 | A6 wave in flight | break | Runs to 1100 cm. | 17.3 item 2 | `Shockwave.Cancel` |
| BK07 | Down or GetUp | second break or several in one frame | Ignored silently. | Exactly one stagger (713, 754) | `RequestBreak` returns "staggered", counted |
| BK08 | Phase transition | break by real hits | Pack immunity blocks the flinch, no stagger. The gate refills the pool at 0 (progress lost). Nothing logged. | Transition not interrupted (729); posture paused (766) | Pool pinned, drains counted |
| BK09 | Phase transition | break by `RequestBreak` or `ForceBreakForTest` | Not gated. Fall clip replaces the roar, then `FinishTransition` resumes behaviour while the boss is down. | Dropped | `RequestBreak` gate "transition"; ends the pack flinch |
| BK10 | Dead | break | Hook: stagger starts, ends next tick, fall clip never stopped (can replace the death clip). Real path unverified. | No hit stun after a lethal hit (1269) | Gate "dead"; ends the pack flinch |
| BK11 | Dormant | break | Stagger, then `EndStagger(true)` resumes behaviour: awake boss that the encounter calls dormant. | No break while dormant | Gate "dormant" |
| BK12 | Idle, cooldown running (CooldownSeconds > 0) | break | Ignored, one log line (Stagger.cpp:85). | Visible (715) | Counter "cooldown", overlay line; the pack flinch plays so the hit visibly matters |

THRESHOLD crossing (PH):

| ID | State | Event | Today | Required | Change |
|---|---|---|---|---|---|
| PH01 | Neutral | crossing | Transition at the next Phases tick, <= 0.1 s (Phases.cpp:101-107). | 764-766 | none |
| PH02 | Committed attack | crossing | Roar clip replaces it, tracker ends it. | Transition (3) outranks attack (6) | `CancelOffence` at start |
| PH03 | A4 blade active | crossing | Ends next tick. | Off at once (766) | `LowSweep.Cancel` |
| PH04 | A5 pending | crossing | Cleared by the tracker path; up to 0.5 s late if the clip never started. | Cleared at transition start (766, L03) | `CancelAll` |
| PH05 | A5 javelin in flight | crossing | Flies on. | Not specified; same rule as BK05 | `CancelAll` (Q1) |
| PH06 | A6 wave | crossing | Cannot happen in play (F19); only with forced test starts. | n/a | `Shockwave.Cancel` (free) |
| PH07 | Down, no riposte yet | crossing | Skipped while `IsStaggered` (Phases.cpp:103). Starts at the first Phases tick after `EndStagger`; the behaviour was already resumed (Stagger.cpp:221-224). | Queue; never two montages (770, 905, 1201) | Hand-off inside `EndStagger`, no resume in between |
| PH08 | Riposte armed, or the riposte hit crossed | crossing | Same as PH07 (the riposte is a flag inside Down). | Earned opportunity kept (1201) | Same; contract for G2-7 in 4.4 |
| PH09 | GetUp | crossing | Same as PH07. | Same | Same |
| PH10 | Transition | crossing again | Ignored (`bPhaseTwo`, Phases.cpp:84-91). | Idempotent (764) | none |
| PH11 | Dead or lethal crossing | crossing | No transition (Phases.cpp:97); `FinishTransition` checks death (:204). | Dead wins (L08, 765, 1269) | none; rules header |
| PH12 | Dormant | crossing | Nothing until awake (Phases.cpp:92). | n/a | none |
| PH13 | Same frame as a break | crossing and break | Depends on tick order (Phases every 0.1 s, Stagger every frame). | The break the hit earned is kept (1201) | Phases ticks after Stagger (tick prerequisite) |

RIPOSTE (RP), DEATH (DT), RESET (RS), HEAL (HL), POSTURE (PO):

| ID | State | Event | Today | Required | Change |
|---|---|---|---|---|---|
| RP01 | Transition | Light Attack press | Ignored (handler needs `IsStaggered`), not counted. | No riposte outside Down | none |
| RP02 | Down, queued crossing | press | Accepted, x2.5 once; transition afterwards. | 1201 | none (driver S05) |
| RP03 | Down, lethal riposte hit | death | `ApplyCritical` ends the stagger; no transition. | 1269 | none (mode death_stagger) |
| DT01 | Transition | boss dies | Roar ends at `TransitionEnd`, no buffs, no resume (Phases.cpp:204-210). | 776-783 | none; posture pin ends at `TransitionEnd` |
| DT02 | Down or GetUp with queued crossing | boss dies | Stagger ends, no resume (Stagger.cpp:330-335); no transition. | 776-783 | `EndStagger(false)` never hands off; stop fall and get-up clips |
| DT03 | Attack, blade, A5, wave | boss dies | Each ends within 0.1 s by its own death check. | 777-778 | none (existing drivers) |
| RS01 | Transition | reset | Roar stopped, no buffs. Immunity effect stays. | 448, 789-802 | `ResetPhases` removes immunity, releases posture hold |
| RS02 | Down or GetUp | reset | `AbortStagger` ends it and starts a cooldown. | Cooldown restored (791) | Abort clears the cooldown |
| RS03 | Idle, cooldown running | reset | Early return; cooldown survives. | Restored | Abort always clears it |
| RS04 | Down, queued crossing | reset | No stored flag, health full: nothing starts. | No transition after reset | none (queue is derived from health) |
| RS05 | any | reset twice | Idempotent (pie_phase_reset L10a to d). | L10 | none |
| RS06 | Transition | player dies | Pack respawns after about 4 s; roar is over; reset on the new pawn. | 785, L09 | none |
| HL01 | Transition | heal | Discarded (`IsNeutral`, HealPunish.cpp:89). | 670-671 | none |
| HL02 | Down | heal | Discarded. | 671 | none (P04b) |
| HL03 | After the transition | heal | Accepted if legal. | No stuck flag | none |
| PO01 | Transition | posture hits | Pool drains and refills freely (F13). | Pause (766) | Pin at the start value; resume 6 s after the end |
| PO02 | Down or GetUp | posture hits | Pool shows full and cycles (G4). | Zero and ignore (713); refill at the end (714) | Hold at 0; refill at `EndStagger` |
| PO03 | After the transition | regeneration | Normal. | Resumes by the normal rule | `LastDrainTime = now` at the end: regeneration starts 6.0 s later |
| PO04 | Cooldown across a transition | time | `CooldownEnd` is a world time; the roar counts toward it. | Documented | none (documented) |

### 4.2 New header `Player/RPGBossRules.h` (pure, header only)

One place for the Freeze 21 order, so the code and an automation test share it.

```cpp
namespace RPGBossRules
{
	struct FFlags { bool bDead=false, bDormant=false, bTransition=false, bStaggered=false, bPhaseTwo=false, bCooldown=false; };
	enum class EBreakResult : uint8 { Started, Dead, Dormant, Transition, AlreadyStaggered, Cooldown };
	enum class ETransitionResult : uint8 { Start, NotReady, Dead, Dormant, AlreadyDone, AboveThreshold, QueuedBehindStagger };
	const TCHAR* Name(EBreakResult R);        // "started" "dead" "dormant" "transition" "staggered" "cooldown"
	const TCHAR* Name(ETransitionResult R);
	// Order: Dead, Dormant, Transition, AlreadyStaggered, Cooldown (skipped when bIgnoreCooldown), else Started.
	inline EBreakResult ResolveBreak(const FFlags& F, bool bIgnoreCooldown);
	// Order: Max <= 0 NotReady, Health <= 0 Dead, Dormant, bPhaseTwo AlreadyDone (set at the same time as bTransition, Phases.cpp:160-161),
	// Health/Max > Fraction AboveThreshold, bStaggered QueuedBehindStagger, else Start. Equality (<=) starts.
	inline ETransitionResult ResolveTransition(const FFlags& F, double Health, double Max, float Fraction);
}
```
Resetting needs no flag: `ResetEncounter` runs to completion inside one tick (Encounter.cpp:222-299).

### 4.3 New helper `Player/RPGBossInterrupt.h/.cpp`

`void RPGBossInterrupt::CancelOffence(AActor* Boss, const TCHAR* Reason)` (Freeze 17.3 items 2, 3; 18.1 item at 766):
1. Log one line: reason, tracker move, phase name and montage position before the cancel (Freeze 724 "record what was canceled").
2. `URPGBossLowSweep::Cancel(Reason)`, `URPGBossShockwave::Cancel(Reason)`, `URPGBossHealPunish::CancelAll(Reason)`.
3. It does not touch the tracker, montages or pack abilities. The montage that replaces the attack ends them, as already proven for the stagger by A2-INT. If M1 adds an explicit weapon-trace stop, call it here too.
Idempotent and cheap when nothing is running.

### 4.4 `URPGBossStagger` (owner of the break, Freeze 10.1 line 421)

- New public `RPGBossRules::EBreakResult RequestBreak(bool bIgnoreCooldown)`. It builds `FFlags` (dead = health <= 0 read now, dormant from `URPGBossEncounter`, transition from `URPGBossPhases`, staggered = `Phase != Idle`, cooldown = `Now < CooldownEnd`), calls `ResolveBreak`, and:
  - `Started`: `StartStagger()`.
  - `Dead` or `Transition`: `EndPackFlinch()` (the "End Ability" snippet of Stagger.cpp:139-152 moved into a helper) so the 0.8 s flinch cannot play over the roar or the death clip. For `Transition` log a WARNING when the flinch was active (the immunity effect failed).
  - Every drop: `++Dropped[reason]`, `LastBreakResult`, one log line "break dropped: <reason>".
  - `Cooldown`: keep today's behaviour (the pack flinch plays) plus the counter.
- `TickComponent` idle edge (Stagger.cpp:75-88) calls `RequestBreak(false)` instead of its inline cooldown test.
- `FString ForceBreakForTest()` (return type changes from void; existing drivers ignore it): `bWasActive = true; return Name(RequestBreak(true))`. New `FString TryBreakForTest()` = `RequestBreak(false)` (obeys the cooldown). Hooks go through the real gate, so tests exercise the production rule.
- `StartStagger()` start: `RPGBossInterrupt::CancelOffence(Owner, "stance break")`; if `bHoldPostureAtZero` then `Posture->BeginHold(Zero)`.
- `EndStagger(bool bResumeBehaviour, bool bClearCooldown=false)`: set `LastEndTime = Now`; cooldown = `bClearCooldown ? 0 : Now + CooldownSeconds`; remove the immunity (as now); `Posture->EndHold(true)` (refill; keep the direct poise write as fallback when the component is missing). Then, only when `bResumeBehaviour`: `if (Phases && Phases->TryStartQueuedTransition(true))` { `bBehaviourHeld = false` (Phases owns the hold now); skip `ResumeBehaviour` } else `ResumeBehaviour()`.
- `AbortStagger()`: no early return. Always `CooldownEnd = 0`, `RiposteArmedUntil = -1`, `bRiposteUsed = false`, `Posture->EndHold(true)`; if not Idle also stop the clips and `EndStagger(false, true)`.
- Death inside a stagger (Stagger.cpp:330-335): also `Montage_Stop(0.1)` on the fall and get-up assets only (never `Montage_Stop()` without argument: it would stop the pack death clip).
- New: `Dropped[5]` with `UFUNCTION int32 GetDroppedBreakCount(const FString& Reason)` (reasons "transition", "dead", "dormant", "staggered", "cooldown"), `GetLastBreakResult()`, `GetLastEndTime()`, `GetCooldownRemaining()`, property `bool bHoldPostureAtZero = true`.
- Contract for G2-7: the future synchronized execution keeps `Phase != Idle` until it finishes and always leaves through `EndStagger`. Then the queue rule needs no change.

### 4.5 `URPGBossPhases`

- `BeginPlay`: `if (Stagger) AddTickPrerequisiteComponent(Stagger)` (engine API, ActorComponent.h:1139). In a frame where both tick, Stagger consumes the pack hit stun edge first, so a break and a crossing caused by the same hit resolve as "break first, transition queued" (PH13).
- Tick (Phases.cpp:96-108): read health, build `FFlags`, `if (!bPhaseTwo && ResolveTransition(...) == Start) StartTransition(false)`.
- `bool TryStartQueuedTransition(bool bBehaviourAlreadyHeld)` (public): same test; on `Start` call `StartTransition(bBehaviourAlreadyHeld)` and `++QueuedStarts`.
- `UFUNCTION bool IsTransitionQueued() const` = `ResolveTransition(...) == QueuedBehindStagger`. No stored queue flag: a reset or a death clears it by itself (stateless).
- `StartTransition(bool bHeldAlready)`: as today, plus `LastTransitionStart = Now`; `RPGBossInterrupt::CancelOffence(Owner, "phase transition")`; `Posture->BeginHold(Pinned)` if `bPausePostureInTransition`; `bImmunityApplied = true` when the effect class loaded; WARNING when the roar montage or the effect class fails to load; behaviour: `if (bHeldAlready) bHeld = true; else HoldBehaviour();`.
- `FinishTransition()`: alive path only: `RemoveImmunity()` (the "Remove Active Gameplay Effect By Class" call of Stagger.cpp:204-213, copied), `Posture->EndHold(false)`, then the existing buffs, leap unlock, resume. Dead path: `Posture->EndHold(false)`, nothing else (as today).
- `ResetPhases()`: if `bImmunityApplied` then `RemoveImmunity()`; `Posture->EndHold(true)`; clear `bImmunityApplied`.
- New: `GetLastTransitionStartTime()`, `GetQueuedStartCount()`, property `bool bPausePostureInTransition = true`.
- Kept: `TransitionSeconds` 1.8 s guarded timer (Freeze 767 allows a guarded timer; the roar clip is 1.5 s so the timer is the longer one).

### 4.6 `URPGBossPosture` hold

```cpp
enum class EHold : uint8 { None, Zero, Pinned };
void BeginHold(EHold Mode);  // Zero: write 0 now. Pinned: keep the current attribute value.
void EndHold(bool bRefill);  // bRefill: write the maximum. Always: LastDrainTime = now (regeneration waits RegenDelaySeconds). No-op when not held.
UFUNCTION FString GetHoldName() const;  UFUNCTION int32 GetSuppressedDrainCount() const;
```
While held, `TickComponent` reads the attribute; if it differs from `HeldValue` by more than 0.01 it writes `HeldValue` back and `++SuppressedDrains`; the cached `Posture` (what the HUD and tests read) stays `HeldValue`; it returns before drain counting and regeneration. Latency is one tick (0.05 s). Poise 0 has no side effect in the attribute Blueprints (F13).

### 4.7 Cancel methods (small public wrappers)

- `URPGBossLowSweep::Cancel(Reason)` = `End(Reason)`.
- `URPGBossShockwave::Cancel(Reason)` = `Stop(Reason)`.
- `ARPGBossJavelin::Cancel(Reason)` = `Finish(Cancelled, Reason)`.
- `URPGBossHealPunish::CancelAll(Reason)`: `ClearPending(Reason)`; `bStarted = false`; if `bCancelJavelinsOnInterrupt` cancel every live javelin of a new `TArray<TWeakObjectPtr<ARPGBossJavelin>> Flying` (filled in `Release()`, pruned here). The cooldown is not touched (it starts at the release only, Freeze 675). New property `bCancelJavelinsOnInterrupt = true`.

### 4.8 Debug overlay (`RPGCombatDebug.cpp:74-96`)

State label gains `Dead` first. Two new lines (Freeze 919, 922):
- `  stance break cooldown %.1f s  breaks dropped: transition %d dead %d dormant %d staggered %d cooldown %d  last: %s`
- `  transition queued %d  last start %.1f s  queued starts %d  posture hold %s  suppressed posture hits %d`

### 4.9 Policy table: posture, regeneration, cooldown, protection

| State | Posture pool | Regeneration | Stance-break cooldown | Immunity effect |
|---|---|---|---|---|
| Neutral | Pack gate drains (20 light, 50 heavy). | 6 s after the last drain, 13 per s (unchanged). | Counts down from the last `EndStagger`. | none |
| Stagger Down, GetUp | Held at 0; more hits ignored and counted. | none | Not started yet. | Applied at start, removed at `EndStagger`. |
| End of get-up | Refill to max (714). | n/a (full) | Starts (default 0 s). | Removed. |
| Queued transition | Same as the stagger. | none | As above. | As above. |
| Transition | Pinned at the value at its start; hits ignored and counted. | none | Keeps counting (world time). | Applied at start, removed at `FinishTransition` (new). |
| End of transition | Stays at the pinned value. | Starts 6.0 s after the end. | unchanged | Removed. |
| Reset | Max, hold cleared. | normal | Cleared (new). | Removed (new). |
| Dead | not touched | n/a | n/a | Removed by `EndStagger`; transition leaves it (boss is gone). |

### 4.10 Not changed

Pack Blueprints and assets, the pack poise gate numbers, `GE_HitStunImmune`, behaviour tree, tracker logic and veto, encounter component (it already calls `AbortStagger` and `ResetPhases`), HUD, riposte input, dodge, A4 and A6 damage numbers, `TransitionSeconds`, `StaggerSeconds`, `CooldownSeconds` (0), phase buffs and leap lock, fireball (off).

## 5. Edge cases and failure modes

| Case | Rule | Where |
|---|---|---|
| Interruption | A pack flinch during the roar or death is ended and logged; any other montage during the roar is stopped by the tracker veto. | `RequestBreak`; tracker :300-318 |
| Death | Dead is the first test of both rules. Dead inside a stagger ends it without hand-off and stops only our two clips. A lethal crossing never starts a transition. | `RPGBossRules`; Stagger death branch |
| Reset and generation | New state is component-local and has no callbacks, so no token is needed. Queue is derived from health. Reset clears hold, cooldown, immunity. Javelin and wave keep their generation checks. Reset twice is a no-op the second time. | `AbortStagger`, `ResetPhases` |
| Phase transition | Break dropped, posture pinned, A5 and projectiles cancelled, immunity removed at the end. Crossing during Down, GetUp or riposte: queued, started inside `EndStagger`. | 4.4, 4.5 |
| Frame rate | All timers use world seconds. The hand-off is synchronous. Crossing latency is one Phases tick (0.1 s) plus a frame at any fps. Driver block S21 runs at 30 and 120. | section 6 |
| Time dilation (M3 hit stop, slow motion) | Timers use dilated world time like the montages, so they stay in step. A hit stop stretches `StaggerSeconds` by the dilated length; accepted. | no change |
| PIE end | No statics added. `EndPlay` of the stagger sets Idle. The driver restores `t.MaxFPS` and unregisters its tick callback. | driver `finish()` |
| Tick order | Prerequisite makes Stagger run before Phases. Residual risk: the pack starts its hit stun one frame later than the damage (unverified); then the roar wins and the break is dropped and counted. Acceptable by 729. | 4.5 |
| Component missing | Every lookup is null-checked; behaviour falls back to today's. | all |
| Missing asset | Roar montage or effect class missing: WARNING log, the 1.8 s guarded timer still ends the transition. | 4.5 |
| Health unreadable | Treated as alive and not crossed (as today). | `ReadFlags` |
| Behaviour hold ownership | One owner at a time: Stagger from start to end or hand-off, Phases from start to finish or reset, Encounter on reset. The hand-off skips the second `StopBehaviorLogic`. | 4.4 |
| Lethal hit that also breaks posture | Gate "dead" drops it and ends the flinch (1269). | `RequestBreak` |
| Immunity expiry margin | Stagger sequence is about 3.9 s against a 4 s effect (F4); a hit in the last 0.1 s could replay a flinch. Not changed here; risk R5. | section 8 |

## 6. PIE test plan

Driver: `Scripts/Editor/pie_transition_rules.py`, log prefix `[Transition]`, house style of `pie_a5_heal_punish.py`: `STEPS = [(delay, fn), ...]`, `check(name, ok, detail)`, final line `RESULT n/m passed`, `finish()` unregisters the tick callback and ends PIE. Run `pie_debug_overlay.py` once after an editor start first.

Modes from `Saved/transition_mode.txt` (default `main`): `main` (about 18 min), `quick` (3 trials everywhere, about 6 min), `death_transition`, `death_stagger`, `death_lethal` (the boss is destroyed about 3.5 s after death, so each death mode is its own PIE run, as in `pie_a2_interrupts.py`).

Helpers:
- `fresh()` (Freeze 35.1): `enc.reset_for_test()`, 0.5 s, `enc.wake()`, `enc.hold_for_test(True)`, `dbg.debug_refill_player()`, `tr.enter_combat()`, player `place()` as in `pie_riposte.py`.
- `check_trials(name, outcomes)`: one `check()` per scenario line, PASS only when every trial passed, detail "n/N trials, setup X, fps F" (Freeze 1333).
- Trial boundaries use the tracker montage position (`tr.get_position()`), not wall time, for A2, A4, A6 timings.
- Global invariants evaluated every tick for the whole run: INV1 never (`stg.is_staggered()` and `ph.is_in_transition()`) (Freeze 905); INV2 posture hold name matches the state (`Zero` when staggered, `Pinned` when transitioning, grace 0.15 s).
- Immunity is read with `boss.call_method("HasMatchingGameplayTag", args=(tag,))`, tag `Status.HitStunImmune` (as `pie_boss_stagger_edge.py:46`). Assumption: the effect grants this tag. S00 proves it first.

New UFUNCTION hooks the driver calls: Stagger `force_break_for_test()` (string), `try_break_for_test()`, `get_dropped_break_count(reason)`, `get_last_end_time()`, `get_cooldown_remaining()`; Phases `is_transition_queued()`, `get_last_transition_start_time()`, `get_queued_start_count()`; Posture `get_hold_name()`, `get_suppressed_drain_count()`. Existing: `debug_set_boss_health_fraction`, `debug_set_boss_posture`, `debug_drain_boss_posture`, `debug_kill_boss`, `debug_set_player_health`, `reset_for_test`, `start_move`, `play_move_montage_for_test`, `notify_heal_started_for_test`, `launch_for_test`, `is_blade_active`, `is_wave_active`, `build_lines`.

Scenarios of mode `main` (N = trials; "event" = the interruption; A0 = Attack attribute before; each trial also ends with `stg.is_staggered()` false and `ph.is_in_transition()` false within 6 s, "not stuck"):

| ID | Cells | Setup and action | Expected numbers | N | Checks |
|---|---|---|---|---|---|
| S00 | PH01 RS01 | Held awake boss. Health 0.55. Read the immune tag idle, at roar +0.3 s, at transition end +0.4 s. | idle False; roar True; after end False (before the change the tag stays up to about 2.2 s: this check fails on the old code) | 1 | 3 |
| S01 | BK09 PH10 HL01 | Health 0.55, wait for `is_in_transition`. At +0.3 s: `r = force_break_for_test()` and `notify_heal_started_for_test()`. Evaluate at +0.35 s and at transition end +0.3 s. | r == "transition"; stagger count +0; not staggered; `get_dropped_break_count("transition")` +1; roar still the current montage (name contains `Ability_R_Intro`) at +0.35 s; heal: accepted +0, discarded busy +1; end: phase two true, `get_phase_two_count()` +1, Attack within 0.6 of 1.25 x A0, `tr.is_neutral()` | 20 | 3 |
| S02 | BK08 RP01 PO01 | Player 110 cm in front, facing, in combat. Posture 30 (`debug_set_boss_posture(30)`). Health 0.55. Light Attack pressed (0.12 s) at roar +0.25, +0.75, +1.25 s. Sample every tick. | boss health lost >= 1 (a hit landed; precondition check); `is_staggered()` false at every sample; stagger count +0; posture at roar +1.6 s = 30 +/- 0.5; `get_suppressed_drain_count()` +1 or more; riposte accepted +0 and rejected +0; roar not interrupted before 1.4 s | 3 | 5 |
| S03 | PO03 | Posture 60, health 0.55. Sample posture after the transition ended (end = `FinishTransition`). | end +3.0 s: 60 +/- 0.5; end +6.5 s: 66.5 +/- 3; end +8.0 s: 86 +/- 3 | 1 | 3 |
| S04 | PH07 | `stagger_seconds = 0.6`. `force_break_for_test()` == "started". +0.3 s health 0.55. At +0.5 s: `is_transition_queued()` true, not in transition, count unchanged. Poll until the transition starts. | gap = `get_last_transition_start_time() - get_last_end_time()` in [0, 0.02] s (old code: uniform 0 to 0.1 s, so 20/20 fails); `get_phase_two_count()` +1; stagger count +1; `get_queued_start_count()` +1; `is_transition_queued()` false afterwards | 20 | 3 |
| S05 | PH08 RP02 | Default 2.5 s Down. Player 110 cm in front. Break. +0.2 s health 0.55. Light press at +0.5 s and at +1.3 s. Sample every tick. | riposte count +1; hit loss R of press 1 over loss L of press 2 in [2.2, 2.8]; never in transition while staggered; one transition starts after the stagger ended (count +1, gap <= 0.02 s) | 5 | 3 |
| S06 | PH09 | `stagger_seconds = 0.6`. Break. When `is_staggered()` and not `is_critical_window_open()` (GetUp) set health 0.55. | queued true; gap <= 0.02 s; count +1 | 3 | 1 |
| S07 | BK07 PH13 PO04 | One Python call: 5 x `force_break_for_test()` and health 0.55 (10 trials health first, 10 trials breaks first). | results == ["started", "staggered" x4]; stagger count +1; dropped "staggered" +4; no transition until the stagger ended (count +0 at +1.0 s), then +1 (stagger start time <= transition start time) | 20 | 2 |
| S08 | BK02 PH02 | Player 180 cm in front. `start_move("A2")`. Control: no event. Break at tracker position >= 1.95 s. Transition: health 0.55 at position >= 1.70 s (transition starts by about 1.80 s, before the 1.93 s window). Wait 1.5 s. | control: player health lost >= 30 (stand-in hit is 36); break and transition: player health lost == 0; tracker interrupted count +1; `get_current_move()` None within 0.3 s | 1 + 3 + 3 | 3 |
| S09 | BK03 PH03 | Player 250 cm at -70 degrees (left). `start_move("A4")`. Control: no event. Break at position >= 0.62 s; transition: health 0.55 at position >= 0.50 s. Wait 1.5 s. | control: lost == 20, `get_hit_count()` +1; break and transition: lost == 0; `is_blade_active()` false 0.1 s after the break and 0.25 s after the health set | 1 + 3 + 3 | 3 |
| S10 | BK04 PH04 HL03 | Player 700 cm, line of sight clear. `notify_heal_started_for_test()`. Event at +0.2 s (`stagger_seconds = 0.6` for the break). After the event ended: second heal. | `is_pending()` false 0.25 s after the event; released +0; javelins 0; `get_cancelled_count()` +1; `get_cooldown_remaining()` == 0; second heal accepted +1 and released +1 within 1.0 s | 3 + 3 | 3 |
| S11 | BK05 PH05 | Player 1000 cm. Heal hook. After the release (+0.3 s) event. Wait 2.5 s. | control: javelin hit +1 (1 trial); break and transition: javelin actors == 0 within 0.35 s, `get_javelin_hit_count()` +0, player health unchanged | 1 + 3 + 3 | 3 |
| S12 | BK06 PH06 | Player 700 cm. `launch_for_test()`. Event at +0.15 s (radius about 350 cm). Wait 1.5 s. | control: wave hit +1, health lost 48; break and transition: `is_wave_active()` false within 0.35 s, health lost == 0 | 1 + 3 + 3 | 3 |
| S13 | BK02 (A6) | Player 600 cm. `start_move("A6", True)`. Break at position >= 0.45 s. Sample the boss z every 0.1 s for 2 s. | wave launches +0; player health unchanged; boss z within 15 cm of the start z at +2.0 s (first run measures; a failure goes to KNOWN_ISSUES); after the stagger `tr.is_neutral()` | 3 | 2 |
| S14 | RS01 | Health 0.55. At roar +0.5 s `reset_for_test()`. Evaluate at +0.3 s, then wake and wait 2.5 s. | not in transition; phase one; Attack within 0.6 of A0; immune tag false; hold name "None" and posture >= 99.5; roar montage gone; generation +1; dormant; boss within 10 cm of home; `get_phase_two_count()` unchanged after wake | 5 | 3 |
| S15 | RS02 RS04 | `stagger_seconds = 2.5`. Break, +0.3 s health 0.55, +0.7 s `reset_for_test()`, wake, wait 4 s. | not staggered; `is_transition_queued()` false; phase two count unchanged; posture 100; `get_cooldown_remaining()` == 0 | 5 | 2 |
| S16 | RS03 BK12 PO04 | `cooldown_seconds = 5`, `stagger_seconds = 0.6`. `try_break_for_test()` "started". After the end: +1.0 s try; +5.2 s try. Then break again, reset 1 s after its end, wake, try. Overlay text. | +1.0 s: "cooldown", dropped "cooldown" +1; +5.2 s: "started"; after the reset: `get_cooldown_remaining()` == 0 and try == "started"; `build_lines()` contains "cooldown 1" | 3 | 4 |
| S17 | RS05 | Health 0.55. During the roar `reset_for_test()` twice 0.1 s apart. | generation +2; component class list equals the list before; phase one; Attack within 0.6 of A0; immune tag false; no transition after wake (2.5 s) | 10 | 2 |
| S18 | RS06 | Health 0.55. At roar +0.3 s `debug_set_player_health(0)`. Wait for the respawn (pawn name changes, 25 s limit) plus 2.5 s. | transition finished once (count +1, buffs once) before the respawn; after: dormant, phase one, generation +1, health full, immune tag false | 1 | 2 |
| S19 | PO02 | `stagger_seconds = 2.5`. Break. Posture at +0.2 s. `debug_drain_boss_posture(20)` at +0.5 and +1.0 s. Posture at +0.7, +1.2 s and at end +0.2 s. | 0 +/- 0.5 at +0.2, +0.7, +1.2; suppressed +2 or more; 100 +/- 0.5 at end +0.2 s | 3 | 3 |
| S20 | FPS | S01 (3 trials) and S04 (5 trials), each at `t.MaxFPS 30` and `t.MaxFPS 120`; restore `t.MaxFPS 0`. Detail logs the measured mean frame time. | same numbers as S01 and S04 | 16 | 4 |
| INV | all | INV1 and INV2 over the whole run | zero violations | - | 2 |
| LIVE | all | End of run: `tr.is_neutral()` within 6 s, no javelin, no wall, posture 100 after a reset | true | 1 | 1 |

Planned total: 63 checks in mode `main` (set `Min` in `RunDrivers.ps1` to the count the driver prints). Pre-change failures by reading (proof the checks are not vacuous): S00 (third check), S01, S02 (posture), S04, S07 order, S09 (blade 0.1 s), S11, S12, S14, S15, S16, S17, S19. Cells that already pass: S08, S10 core, S13 part.

Death modes (each one PIE run, one trial):
- `death_transition` (DT01): health 0.55, kill at roar +0.5 s. At kill +1.6 s: `is_in_transition()` false (not stuck); `get_phase_two_count()` == 1 and Attack == A0 within 0.6 (no buffs); boss tag `Status.Dead` true and hold name "None". 3 checks.
- `death_stagger` (DT02, RP03): break, health 0.55 at +0.2 s, riposte accepted at +0.5 s (precondition check), kill at +0.8 s. At +0.3 s after the kill: not staggered, `is_transition_queued()` false, immune tag false; at +2.0 s: `get_phase_two_count()` +0. 3 checks.
- `death_lethal` (PH11): in one call health 0.55 then `debug_kill_boss()`. At +1.0 s and +2.5 s: `get_phase_two_count()` +0 and not in transition. 2 checks.

Existing drivers that keep covering their cells (run as regression, not duplicated): `pie_phase_reset.py` (PH01, PH10, RS05, coarse queue), `pie_attack_rules.py` (L06 veto, B02), `pie_a5_heal_punish.py` (HL02, P07, P09), `pie_player_death_reset.py` (RS02, RS06 for stagger and riposte, DT03), `pie_a2_interrupts.py`, `pie_leap_wave.py`, `pie_a4_low_sweep.py`.

Automation test `OneBossFight.Boss.TransitionRules` (in `Tests/RPGAutomationTests.cpp`, pure): all 64 flag combinations of `ResolveBreak` (with and without `bIgnoreCooldown`) against the order Dead, Dormant, Transition, Staggered, Cooldown; `ResolveTransition` at (300, 500, 0.6) Start, (300.5, 500, 0.6) AboveThreshold, health 0 Dead, Max 0 NotReady, staggered below threshold QueuedBehindStagger, `bPhaseTwo` AlreadyDone; defaults: Stagger `CooldownSeconds` 0 and `StaggerSeconds` 2.5, Phases fraction 0.6 and `TransitionSeconds` 1.8, Posture 6 and 13.

## 7. Ordered implementation steps (each leaves the project building)

1. `RPGBossRules.h` plus the automation test. No behaviour change. `Scripts/Rebuild.ps1 -Tests`: 7 tests pass.
2. Test hooks with old behaviour: `ForceBreakForTest` returns a string, `TryBreakForTest`, getters (`GetLastEndTime`, `GetLastTransitionStartTime`, `GetQueuedStartCount`, `IsTransitionQueued`, `GetDroppedBreakCount` returning 0, `GetHoldName` returning "None", `GetSuppressedDrainCount` returning 0, `GetCooldownRemaining`). Write `pie_transition_rules.py`. Run `main` once on the old logic and record the failing list (section 6 prediction).
3. Posture hold (`BeginHold`, `EndHold`, counters). Unused yet. Build.
4. Cancel methods on LowSweep, Shockwave, Javelin, HealPunish plus `RPGBossInterrupt`. Unused yet. Build.
5. Stagger: `RequestBreak` gate and counters, `EndPackFlinch`, `CancelOffence` and posture hold in `StartStagger`, refill and `LastEndTime` in `EndStagger`, always-clearing `AbortStagger`, death clip stop. Build, run `pie_riposte.py`, `pie_boss_hud.py`, `pie_player_death_reset.py`, `pie_a5_heal_punish.py`.
6. Phases: rules in the tick, `TryStartQueuedTransition`, `IsTransitionQueued`, cancel and pin in `StartTransition`, immunity removal in `FinishTransition` and `ResetPhases`, tick prerequisite, warnings. Wire the hand-off in `EndStagger`. Build, run `pie_phase_reset.py`, `pie_attack_rules.py`, `pie_leap_wave.py`.
7. Overlay lines (4.8). Build.
8. Run `pie_transition_rules.py` in `main` and the three death modes; fix; then the full regression list of `MILESTONE_GATE2_CODE.md` plus `pie_posture_regen.py`, `pie_a2_interrupts.py`, `pie_boss_stagger_edge.py` (3 modes), `Scripts/Rebuild.ps1 -Tests`.
9. Docs (section 9) and the `RunDrivers.ps1` entry.

## 8. Risks and open questions

Risks:
- R1 Immunity facts unverified: duration 4 s is from DECISIONS.md:356, not re-read; that the effect grants `Status.HitStunImmune`; how a second application stacks. S00 checks the tag; if it fails the immunity checks become INFO and the tag name is corrected.
- R2 The pack gate refill at 0 is read from DECISIONS.md:231 and a node list, not from traced wiring. If the gate refills only when the stun can play, G3 shrinks but the pin stays correct.
- R3 One-frame race between the pack's damage and its hit stun activation (unverified). Residual, documented.
- R4 Skipping `ResumeBehaviour` at the hand-off relies on `StartTransition` holding with `bHeld = true`. S04 samples the boss position during the roar (drift under 5 cm) to prove the behaviour tree stayed stopped.
- R5 The 4 s effect barely covers a 3.9 s stagger; a hit in the last 0.1 s might replay a flinch. Out of scope; if seen, re-apply the effect when GetUp starts.
- R6 A6 broken in the air may leave the boss floating (pack leap, unverified). S13 measures it.
- R7 A stagger or transition cancelling a pack trace relies on montage replacement (A2-INT proves it for the stagger with the fall clip; the roar clip is the same mechanism but first proven by S08). M1 may add an explicit stop.
- R8 Posture held at 0 changes the HUD look (bar empty during the break, flash at the start).

Open questions for the owner (defaults in brackets):
- Q1 A javelin in flight when a break or a transition starts: cancel it [yes, Freeze 723] or let it fly (`bCancelJavelinsOnInterrupt`).
- Q2 Posture bar during a break: empty [yes] or full (`bHoldPostureAtZero`).
- Q3 Hits during the roar: pin posture and drop the break [yes] or queue a break for after the roar (`bPausePostureInTransition`).
- Q4 Freeze 766 and 771 speak of "transition protection" and "invulnerability". The project has hit stun immunity only (DECISIONS.md:380) and damage lands in the roar. Add damage immunity? [no, out of scope here; L08 needs death to stay possible].
- Q5 Queue behind the whole sequence including the 1.4 s get-up [yes] or start when the Down window expires.
- Q6 `CooldownSeconds` stays 0 (decision G0-5) against Freeze 1371 (5.0)? [stay 0].

Unverified (see also the list returned with this spec): effect duration and tag; gate wiring; real-path pack order of damage and hit stun; whether a pack hit stun can activate on a dead boss; engine end of notify states during blend-out (M1); A6 mid-air break; L05 (hammer) and L07 (lock-on and camera after the roar) are not part of M4.

## 9. Docs to update

- `TASKS.md`: rows G2-6 and G2-8 (done text), Done list entry.
- `MILESTONE_GATE2_CODE.md`: row M4 status and the driver line.
- `DECISIONS.md`: new section "Transition versus stance break (M4)": rules table 4.1, policy table 4.9, decisions drop-not-queue for a break in the roar, pin posture, cancel projectiles (Q1), queue behind GetUp (Q5).
- `KNOWN_ISSUES.md`: KI-071 immunity outlived the transition and a reset (fixed), KI-072 cooldown survived a reset (fixed), KI-073 javelin and wave not cancelled (fixed), further rows for R3, R5, R6 if they show up.
- `TEST_PLAN.md`: TRANS-01 (driver main), TRANS-02 (death modes), TRANS-03 (automation test), regression line.
- `DELTA_AUDIT.md`: rows PH-02, PH-04, POST-02, POST-03.
- `PROJECT_STATE.md` and `HANDOVER.md` section 4: the new driver in the regression list.
- `Scripts/RunDrivers.ps1`: entry `@{ N = 'pie_transition_rules'; K = 'R'; Min = 63 }` (main mode); the death modes are run by hand until the runner can write `Saved/transition_mode.txt`.

STATUS: COMPLETE
