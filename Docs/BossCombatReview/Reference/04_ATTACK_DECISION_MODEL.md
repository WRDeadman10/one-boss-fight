# Attack Decision Model

## Decision cadence

Attack selection is event/gate driven, never a per-frame opportunity to replace the current action.

Legal gates include:

- Neutral after recovery and cleanup.
- A named combo gate after the prior damaging window has closed.
- An explicitly budgeted defensive/reaction gate while otherwise free.
- A safe queued phase-transition gate.

Perception and context may refresh at a low rate between gates, but the selection snapshot is rebuilt atomically at the gate.

## Selection pipeline

```text
1. Validate encounter and target
   alive, visible/last-seen policy, inside arena, reachable, acceptable Z

2. Validate executor and priority
   neutral or expected combo gate, not dead/staggered/transitioning,
   queued higher-priority event handled first

3. Build fresh context
   distance convention, signed yaw, LOS, velocity, visible player action,
   player recovery, boss phase/health/posture, pressure, cooldowns, history,
   wall/nav/warp safety, timestamp

4. Hard-filter candidate set
   phase -> state/gate -> range/Z -> angle -> LOS -> cooldown/resource ->
   montage/sockets -> navigation/warp -> branch compatibility

5. If none remain
   choose reorient / approach / retreat / EQS position / purposeful wait / reset

6. Score eligible candidates
   range fit + angle fit + opportunity + spacing value + phase style + variety
   - repeat penalty - risk penalty + bounded contextual adaptation

7. Select
   deterministic max during diagnosis, or seeded weighted sample among near-best

8. Record trace
   context, candidate rejections/scores, selected ID, seed and gate

9. Start through executor
   assign instance ID, commit cooldown/history, freeze movement authority,
   play montage or roll back on failure
```

## Hard gates versus soft preferences

Hard gates express physical or state legality. A high score can never override them. Soft terms express desirability among moves that can genuinely execute. This separation is critical: range is both a legal interval and a preference curve, while a missing montage or wrong phase is only a rejection.

The package's proposed utility is:

```text
BaseWeight * (0.28 RangeFit + 0.20 AngleFit + 0.20 Opportunity
            + 0.12 SpacingValue + 0.10 PhaseStyle + 0.10 Variety)
- RepeatPenalty - RiskPenalty
```

Those coefficients are illustrative. The C++ sketch intentionally implements a simpler deterministic V0 (`0.50 range + 0.30 angle + 0.20 opportunity`) and omits production history, risk, spacing, phase-style and stochastic selection. The Python sandbox implements a closer, but still incomplete, seeded near-best model.

## Context-sensitive reactions

### Heal/cast punish

The player must have entered an observable committed action. After a minimum reaction latency, the boss may consider a punish only while free, with LOS, legal range, viable travel, cooldown/resource available and enough remaining player recovery. The punish is a normal candidate, not a guaranteed teleporting override.

### Aggression response

A nearby committed player attack can increase a block, dodge, riposte or counter score if that reaction has budget and startup. Defensive actions have cooldown and recovery and may fail to be selected. They are not perfect input-reading defenses.

### Position response

Close rear presence may make a rear hook eligible; repeated backward rolls may raise a lunge score; continuous guard may raise a guard-break score. These effects are capped, decay and operate only when the move's ordinary geometry and state rules pass.

## Conditional combo algorithm

At a named gate:

1. Verify the gate belongs to the current `AttackInstanceID` and has not been consumed.
2. Close the preceding hit window.
3. Build fresh context.
4. Read only outgoing edges from the current graph node.
5. Filter by distance, yaw, phase, target action, hit-confirm policy, cooldown, use count and combo depth.
6. Rank eligible edges by priority/weight with bounded variation.
7. Transition through an authored montage section or explicit montage blend.
8. If no edge is legal, enter the edge's declared normal/long recovery.
9. Log every edge rejection and the selected outcome.

Fixed sequences skip step 5 and always take their next edge. Random chains perform step 6 without meaningful step 5. Context-sensitive combos require both authored gate timing and current-world conditions.

## Commitment and cancellation

- Neutral and early wind-up may track or cancel only as the attack policy allows.
- Commitment freezes or sharply caps facing and target updates.
- Active damage cannot be replaced by an arbitrary newly chosen move.
- Combo decisions occur at their named gate, normally after active collision closes.
- Hyperarmor changes interruption eligibility, not attack selection legality or health immunity.
- Cancellation follows an explicit priority table; death is terminal, while phase/stagger behavior is policy driven.
- Every cancellation calls centralized cleanup and invalidates stale callbacks through the instance ID.

## Variety, cooldowns and pacing

- Cooldown begins on a committed attack start, not on every rejected selection attempt.
- Recent exact attacks and families receive decaying penalties.
- Signature moves have minimum spacing intervals.
- Near-best sampling excludes obviously poor candidates before randomness.
- The pressure budget limits continuous offense and guarantees recovery/neutral periods.
- Phase two may enlarge the pool, combo cap or pressure budget, but must retain openings.

## Correct observable behavior

- At fixed context and seed, selection is reproducible.
- A front-only move never starts on a rear target.
- Starting a heal after boss commitment does not replace the current move.
- Moving behind after commitment may evade the current strike and can influence only the next gate.
- The same move can repeat when context strongly justifies it, but does not dominate through unbounded weighting.
- When no attack is valid, the boss purposefully changes position or waits rather than looping the planner.
- Decision logs explain both the winner and every hard rejection.

## Verification strategy

Use a table-driven pure test for hard gates and deterministic seeds; then runtime tests at fixed distances, yaws, phases, cooldowns and player states. Force empty pools, missing assets, montage failure, target death, LOS loss, wall-adjacent warp and phase transition. For combos, test every outgoing edge and default recovery, gate duplication, max depth and interruption. Run long seeded encounters to measure move/family use rates, repeat rate, no-eligible frequency and pressure duration.
