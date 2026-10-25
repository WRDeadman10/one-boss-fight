# Architecture Understanding

This document describes how the reference architecture could be represented in Unreal Engine 5.5/5.5.4. It does not evaluate or prescribe changes to the current project.

## Conceptual Unreal topology

| Responsibility | Unreal representation | Contract |
|---|---|---|
| Boss body/life | `ACharacter` or existing boss pawn | Mesh, capsule, Character Movement, health/death and component host. |
| Target/perception | `AAIController` + `UAIPerceptionComponent` | Updates target candidates/last seen; never starts a montage directly. |
| High-level activity | Behavior Tree **or** StateTree | Chooses combat/search/reset/transition mode; not a second attack executor. |
| Awareness | Actor component or pure snapshot service | Produces timestamped `FCombatContext` from observable data. |
| Attack decision | C++/Blueprint component over Data Assets | Filters, scores and returns a trace; does not animate. |
| Attack executor | Authoritative actor component/state machine | Owns instance ID, montage lifecycle, motion handoff, gates, cleanup and watchdog. |
| Attack data | `UPrimaryDataAsset`/Data Assets | Designer-authored gates, timings, motion, geometry, damage, branches and recovery. |
| Combo graph | Data Asset of nodes/edges | Linked follow-ups evaluated only at named gates. |
| Animation timing | Anim Montages, sections, Anim Notify/Notify States | Emits commit/window/gate/recovery/armor events into executor. |
| Attack motion | Root-motion montage + selective Motion Warping | Owns committed displacement inside bounded windows. |
| Hit query | C++ component or focused BP component | Sweeps weapon samples or special volumes only while authorized. |
| Damage/defense | Custom resolver or existing GAS path | Central precedence for iframe/parry/guard/posture/health. |
| Posture/phase | Focused components or integrated ability/state modules | Own meters, transition policy and events; cannot bypass executor cleanup. |
| Position search | EQS/nav queries | Scores safe goals between committed actions. |
| Debug/replay | Gameplay Debugger, Visual Logger, Rewind/Animation/Unreal Insights, structured logs | Explains selection, timeline, motion, contact and outcome. |

## Suggested data boundaries

`BossConfig` owns global health, locomotion, posture and phase references. `BossPhase` owns allowed attacks and phase modifiers. `BossAttack` owns per-move selection, montage, timing, motion, hit and recovery data. `BossAttackGraph` owns branch topology and edge conditions. Runtime context and attack instances are never serialized back into design assets.

Gameplay Tags can express states/windows without requiring GAS. If GAS already exists, abilities/effects may carry execution, but one system must still own the attack timeline and instance identity.

## Event contract

```text
BT/StateTree task -> TryStartAttack(AttackId, Context)
Executor -> allocate instance, disable competing movement, play montage
AN_Commit -> executor locks/caps tracking
ANS_AttackWindow begin/tick/end -> executor/trace opens, samples, closes window
AN_ComboGate -> executor builds fresh context and chooses linked edge once
ANS_Armor -> executor applies/removes interruption rule
AN_RecoveryBegin -> executor applies minimum recovery lock
Montage blend/end or watchdog -> executor performs authoritative cleanup
Trace contact -> resolver -> defense/health/posture -> feedback/telemetry
Posture/death/phase/reset -> executor interrupt/queue according to priority
```

Callbacks include the attack instance and expected window/gate. An interruption can skip a Notify State end, so montage delegates and centralized abort are mandatory.

## Blueprint-first vertical slice

The reference proposes three differentiated attacks before a full catalogue: a thrust, sweep and overhead slam. Build the context/selector, executor, montage events, swept collision, one conditional branch, one guaranteed punish, posture/death and debug visualization. Exit criteria are behavior, not asset count: range/angle choice works; commitment prevents snap; collision matches the blade; duplicate hits do not occur; interruption cleans up.

## Hybrid production path

The recommended mature split is editor-authored Data Assets, montages, sections and notifies; C++ utility, executor, trace, resolver and telemetry; Blueprint/BT/StateTree for high-level composition. This retains iteration speed while keeping timing, identity and cleanup auditable.

## Diagram-by-diagram interpretation

### 01 — System architecture

Important nodes: Player, Awareness, High-Level AI, Movement, Utility Decision, Attack Executor, Anim Montage, Combo Gate, Hit Trace, Damage Resolver, Debug/Replay. Player visible state flows to awareness; context flows to AI; AI chooses positioning or asks utility for a combat action; utility returns a selected move to the executor; executor plays the montage; the montage opens hit windows and branch gates; hit contact reaches the resolver; resolved damage returns to the player. The combo gate requests fresh awareness context. Events/outcomes flow to debug/replay. The dependency is intentionally cyclic at the encounter level but acyclic inside one attack.

### 02 — Attack decision tree

Start is a legal gate. Target validity failure routes to search/leash/reset. An unavailable executor routes to “wait for legal gate.” A pending phase transition takes precedence. Otherwise context is rebuilt, all attacks are hard-filtered by phase/range/yaw/cooldown/LOS, and an empty set routes to EQS/reorient/approach/wait. Eligible moves are scored, near-best sampled with stored seed/reasons, then passed to `START ATTACK`, which freezes movement authority. The diagram makes hard-gate ordering a control-flow property, not a scoring suggestion.

### 03 — Attack graph

Neutral enters A02 Crescent Sweep, which progresses wind-up -> active -> gate. After active closes, current context selects A07 for phase-two close/front, A05 for behind plus cooldown, long recovery when the player escaped, or normal recovery on no edge. All routes reach recovery complete and return neutral. The graph demonstrates conditional, learnable branches and a guaranteed default.

### 04 — Combat state machine

Neutral can position when no move is valid, then returns when range is ready. A chosen move enters wind-up; commit notify enters committed; hit-window begin enters active; finish/no branch enters recovery; unlock returns neutral. A legal combo gate returns to wind-up for a follow-up. Wind-up/committed can enter stagger only when their interruption rules allow. Recovery can enter a queued phase transition and return when ready. Death is reachable as a terminal priority from combat states. The diagram implies that exact phase/stagger/death conflicts still require an explicit priority table.

### 05 — Attack timing

The illustrative A03 bar separates anticipation, hold, active hit and recovery on a single montage clock. A tracking-lock marker precedes the first possible contact at 0.98 seconds. The engineering implication is that telegraph, commitment, collision and punish are one timing contract; the numeric times are not generic requirements.

### 06 — Hit geometry

Six top-down shapes distinguish a narrow thrust, broad swept arc, localized slam impact, annular radial wave, forward lane and tight grab cone. These are not interchangeable broad overlaps. Each geometry implies a different safe response and query implementation, so geometry belongs in attack data and QA.

### 07 — Tracking and commit

The step plot allows high early tracking, drops to a low late-wind-up cap, then zero through commit and recovery, and restores neutral turn authority at the end. The abrupt stage changes are conceptual; each move owns its actual caps. The player experience is a credible early aim followed by a dodgeable committed line.

### 08 — Pressure rhythm

Pressure rises through a combo, falls into a quiet interval, rises higher for a phase-two burst, falls through an explicit reset, and rises to a smaller later sequence. It illustrates a shaped rhythm rather than permanent maximum aggression. A budget/tokens system is one implementation, not the only valid one.

### 09 — Arena and spacing

Concentric regions around the boss identify close-punish, ideal polearm exchange and approach/lunge space inside an illustrative 1500 cm boundary. The player is shown in the exchange region. The diagram connects weapon design to arena dimensions, but explicitly says it is not to scale.

### 10 — Damage pipeline

An active notify authorizes a swept weapon/wave query. Contact must be a valid enemy and live instance, then pass hit-policy dedupe. Iframes and parry route to no health damage with a reason. Guard routes either to blocked/reduced application or unblocked application. Health/posture application and no-health outcomes both end in feedback plus a logged result. The chart's compressed guard arrow means mitigation values still require explicit design.

### 11 — Utility scoring

An example ranking shows A04 0.82, A02 0.73, A03 0.65 and A01 0.47; A05 rear hook and A08 false mercy are rejected rather than assigned competitive scores. This reinforces eligibility-before-utility. The two rejection labels overlap visibly in the PNG/SVG rendering, so the exact label placement is defective even though the intended model is clear from the documents/data.

### Ashen Bellwarden concept sheet

The concept shows an armored bell-bearing polearm boss, front/back silhouette, and thumbnails for narrow thrust, broad sweep, impact slam and concentric radial wave. It supports attack readability and geometry differentiation; it is not evidence of an implemented asset or a requirement to copy this character.

## Architecture acceptance principles

- Exactly one authority for selection execution and exactly one authority for final damage.
- No competing high-level planners or competing committed-motion sources.
- All temporary state is instance-scoped and cleaned on every exit.
- Data values are measurable against the actual montage and arena.
- Debugging exists before complexity is added.
- Optional systems—GAS, StateTree, EQS, Motion Warping and multiplayer—are adopted only where they solve a real requirement and do not create duplicate authority.
