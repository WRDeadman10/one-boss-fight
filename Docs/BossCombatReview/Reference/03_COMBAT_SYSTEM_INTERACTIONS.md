# Combat System Interactions

## Connected runtime model

```text
Player-visible state + world geometry
        |
        v
Awareness/context -----> high-level mode and positioning
        |                         |
        v                         v
hard eligibility -----> utility ranking/seeded choice
        |                         |
        +-------------> attack executor <------------- phase/pressure/cooldowns
                              |
                       montage + motion owner
                         /            \
                hit-window notify    combo gate
                       |                 |
                 geometry query     fresh context + linked edges
                       |                 |
                 damage resolver <-------+
                       |
             health/posture/guard/stagger/death
                       |
          cleanup, recovery, telemetry and next legal gate
```

The essential dependency rule is one-way authority with explicit feedback. Awareness does not play animations; the BT does not toggle hitboxes; notifies do not select arbitrary attacks; collision does not decide combos; VFX does not apply damage. Feedback returns only through named events and fresh context.

## Interaction matrix

| Upstream system | Downstream effect | Required boundary | Failure if coupled incorrectly |
|---|---|---|---|
| Perception/awareness | Target validity, LOS, position, visible action | Timestamped context at legal gates | Psychic reactions, through-wall counters, stale targets. |
| Distance convention | Eligibility, range fit, movement and punish travel | One labeled convention per attack | Large-boss range mismatches and attacks chosen where they cannot connect. |
| Signed yaw/vertical delta | Front/side/rear attacks and floor validity | Boss-facing planar angle plus explicit Z tolerance | Rear hooks from the front; damage through floors. |
| Player action state | Heal/cast/attack reactions | Visible commitment plus reaction latency | Raw-input reading and instantaneous counters. |
| Cooldown/history | Variety and signature frequency | Committed starts update cooldown; history decays | Attempt spam, repetition or permanently banned moves. |
| Pressure budget | Attack eligibility and neutral rhythm | Long offense spends; reset/recovery replenishes | Endless combos or inert waiting. |
| Phase | Move set, utility, combo depth, movement and presentation | Transition once at a safe policy gate | Mid-swing rule swapping and duplicate transitions. |
| Utility decision | Executor start request | Select only eligible, executable assets | Chosen montage missing or illegal state replacement. |
| Executor state | Motion, montage, trace, combo and recovery | Single authoritative attack instance | BT/AnimBP/trace disagree about current attack. |
| Montage position/notifies | Commit, tracking, active, gate, armor and recovery timing | Validate instance/state; cleanup independent of notify end | Stale notifies, phantom hits, stuck armor. |
| Root motion/warping | Physical reach and facing | Exclusive movement authority; bounds and stop time | Sliding, wall penetration and post-commit homing. |
| Hit geometry | Contact candidates | Shape follows visible animation; swept sampling | Invisible wedges or tunneling misses. |
| Hit policy | Per-target eligibility | Instance/window-scoped dedupe | Multiple damage from multiple body overlaps. |
| Damage resolver | Iframes, parry, block, health and posture | Documented centralized order | Cosmetic hits differ from health; iframe still drains posture. |
| Posture/hyperarmor | Interruption and stance break | Explicit state/window matrix | Global invulnerability or inconsistent cancels. |
| Combo gate | Follow-up/recovery choice | Fresh context, outgoing edges only, gate consumed once | Arbitrary mid-swing switches and infinite chains. |
| Recovery/punish model | Player offense opportunity | Boss lock minus travel/startup/buffer | Fake openings and slow-build invalidation. |
| Arena/navigation | Legal starts, warp targets and reset | Reachability, wall/height/boundary checks | Attacks into walls or unreachable targets. |
| Debug/telemetry | Tuning and diagnosis | Stable IDs, reasons, timestamps and seeds | Unexplainable behavior and irreproducible bugs. |

## Critical causal chains

### Distance and position to attack choice

Distance first acts as a hard feasibility gate, then as a soft preference around an ideal reach. Angle and vertical separation further restrict geometry. If no attack is legal, movement is selected to create a legal future context. This prevents utility weights from rescuing an impossible move. Near a wall, arena safety can veto an otherwise good lunge; at the rear, a cooldown-limited backhook can enter the pool while frontal moves leave it.

### Position to conditional combo

The first move commits to its authored path. Only after the active window closes does a named combo gate sample the player's new position. The graph may select a close/front follow-up, a rear counter, a long recovery when the player escaped, or default recovery. Thus movement during the attack changes the next legal edge, not the strike already in flight.

### Tracking to dodge and punish

Early tracking makes the attack credible against ordinary strafing. Reduced late tracking and commitment create a point after which lateral/rear movement wins. Root motion and Motion Warping must stop updating at that boundary. The resulting whiff location plus recovery determines whether the player can travel and attack before the boss unlocks.

### Animation timing to collision timing

The animation pose communicates threat; Notify States authorize collision; swept socket paths determine the actual contact time. A global “damage moment” is insufficient for a long sweep because different target positions intersect at different frames. Play-rate, low-FPS and hitstop tests must prove that the notify interval, sampled path and visual weapon still agree.

### Combo continuation to punish windows

A conditional recovery is not safely punishable until the player confirms that no branch remains legal. The branch gate and follow-up cue therefore determine when the apparent opening becomes real. Heavy committed finishers should still provide some unconditional long openings so the fight does not reduce to guessing.

### Movement AI to attack eligibility

Movement deliberately changes future distance, angle and wall-clearance inputs. EQS or equivalent selects a short committed position goal; it must stop before root-motion execution. After a whiff, recovery or failed eligibility set, the boss can reorient/approach rather than repeatedly retry an invalid attack.

### Healing to decision-making

Healing enters awareness only after a visible committed state. At the next legal reaction gate, a heal-punish move competes with other eligible actions. LOS, range, travel time, reaction latency, cooldown and probability/utility can all prevent it. A boss already committed to another attack cannot retroactively switch.

### Cooldowns, history and unpredictability

Cooldowns impose hard temporal spacing; recent move/family history applies a decaying soft penalty; near-best seeded sampling supplies bounded variation. Together they avoid both repetition and uniform randomness. Because seed, candidate scores and rejection reasons are logged, the variability remains reproducible.

### Stagger to animation execution

Damage resolution changes posture. If the threshold is reached and current hyperarmor/priority rules allow a break, the executor aborts the current attack, closes traces, clears warping and gates, removes temporary armor and enters a dedicated stagger state. If a break is deferred by policy, that pending event needs a visible, deterministic release rule. Death supersedes all of it.

### Phase to combat intelligence

A phase change modifies the allowed pool and scoring/movement/pacing parameters. The health threshold merely queues the change; the chosen transition policy decides when it becomes authoritative. Old instance callbacks and persistent hazards need provenance so they cannot mutate the new phase or encounter after reset.

### Geometry to defense

The collision mechanism discovers contact, but the resolver supplies meaning. A ring wave, grab and sword hit can share the resolver while defining different dodge, guard and parry policies. Deduplication happens before health change, and visual feedback follows the adjudicated result. This makes “hit,” “blocked,” “parried,” “iframe” and “damaged” distinct telemetry outcomes.

## What makes the whole system advanced

Advanced behavior emerges from composition, not from a single clever selector:

1. Context is rich but constrained to observable information.
2. Every decision happens at an authored legal gate.
3. Every move has distinct geometry, motion, timing and risk.
4. Player positioning affects eligibility, branches and punish value.
5. Randomness operates only among strong legal choices and is reproducible.
6. Animation, motion and collision share one timeline and attack identity.
7. Exceptional exits restore every temporary state.
8. Phase/aggression changes alter pressure without deleting counterplay.
9. Telemetry explains both selection and damage outcomes.
10. Tests cover timing boundaries, low FPS, arena edges, interrupts and player-build differences.
