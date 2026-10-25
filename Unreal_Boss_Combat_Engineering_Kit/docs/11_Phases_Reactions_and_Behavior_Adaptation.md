# 11 — Phases, Heal Punishes, Adaptation, Anti-Cheese

## Phase transition is a rule-set change, not only more damage

Each phase owns allowed attack IDs, movement range profile, utility multipliers, combo-depth caps, recovery modifiers, pressure budget, special effects, and transition animation policy. A phase change should visibly alter combat and remain learnable.

### Phase proposal

| Property | Phase 1 (100%–55% HP) | Phase 2 (below 55%) |
|---|---|---|
| Common combos | up to 2 hit sections | up to 3 sections |
| Pressure budget max | 90 | 110 |
| Neutral pause | 0.35–0.85s | 0.25–0.70s |
| New geometry | Basic thrust/sweep/slam | Bell shockwave, delayed reverse sweep |
| Anti-heal | Conditional advancing lunge | Same, somewhat higher utility |
| Tracking | Stable at early telegraph | Select moves have slightly higher early tracking; no instant lock-breaking |
| Guaranteed punish | Heavy overhead/impact recoveries | Still present, maybe reposition-dependent |

HP thresholds are exemplary. Phase changes should avoid leaving boss permanently uninterruptible or eliminating all player openings.

## Transition policy

Choose one:
- **Deferred:** when HP threshold is crossed, queue phase transition after current combo/recovery. Very safe for consistency.
- **Interruptible transition:** threshold forces montage transition but reliably closes traces, cancels old timeline and provides a tell.
- **Cinematic transition:** dedicated scene with invulnerability; avoid collision and player-control traps.

The guide recommends **deferred** for the first version.

## Player action reaction decision gates

A boss can observe a heal and *prefer* a lunge if it is neutral, within sight, in reach and not on cooldown. It should not replace a committed swing midair to punish a heal. Use `ReactionLatency >= 0.20s` as a starting design value and tune it by move length. If using GAS tags, tag `Player.Action.HealingCommitted` and remove when action ends.

## Soft adaptation: limited, not omniscient

Adaptation can shift preferences based on the player's last 5–10 seconds:

- Excessive backward rolls: slightly increase advancing lunge weight.
- Constant shield guard: increase guard-break mixups.
- Close rear camping: increase rear sweep weight when rear condition is satisfied.
- Ranged spam: approach with intermittent cover/defensive responses.
- Repeated attacks during a bait animation: prefer quick counter when neutral.

Clamp each adaptation bonus; decay over time; provide minimum chance of neutral movement and ordinary attacks. A test should verify the boss is still beatable by each main player build.

## Player fairness safeguards

- Visible player action state, not raw input press, is the reactive trigger.
- Reaction must fit boss attack range, steering budget, cooldown and startup time.
- At a gate the boss may change **which attack starts next**, not rewrite which hit is currently in flight.
- Stale sightings cannot initiate pinpoint counters through walls.
- Defensive AI has reaction failures, opportunity costs and cooldown.

## Anti-exploit checklist

- Kiting boss beyond arena → leash reset rather than infinite projectile chase.
- Staying on boss rear axis → rear hook with cooldown, not omnidirectional invisible attack.
- Trapping boss in wall → safe reposition or reset via authored move (not teleport onto player mid-combat).
- Attacking during every recovery → differentiated guaranteed and conditional punish categories.
- Continuous guard → guard-break option that itself has clear punish on miss.
- Infinite parry → mix only explicitly unparryable attacks with clear different tells.
- Player unreachable on geometry → path validation and encounter reset.

## Phase regression cases

Cross threshold during wind-up, active hit, grab, stagger, death and AoE lifetime. Confirm no duplicated attack ID and no stale hitbox. All phase transitions emit one telemetry event and one change of allowed move set, not alternating between two phases due to HP healing.
