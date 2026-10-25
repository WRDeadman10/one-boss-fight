# 00 — Combat Design Goals, Fairness Contract, Definitions

## Desired experience

The Ashen Bellwarden should feel intelligent **because of contextual moves and believable commitment**, not because it cheats. The player should be able to infer patterns and then consciously manipulate range, angle, animation state, and recovery to generate openings.

### Design pillars

1. **Legible threat:** every dangerous active window has perceivable anticipation with a recognizable attack signature; deliberately difficult timing is allowed but invisible arbitrary damage is not.
2. **Committed moves:** targeting may update in neutral and early wind-up. Late wind-up and active damage have explicit rotation caps or hard lock.
3. **Player-responsive, not button-reading:** target selection may use committed visible player action states. Counter moves are gated by line-of-sight, distance, cost, and cooldown.
4. **Differentiated geometry:** thrust ≠ sweep ≠ localized impact ≠ radial expanding ring ≠ lingering hazard ≠ grab.
5. **Learnable uncertainty:** limited weighted variety across eligible attacks, with anti-repeat weighting; not pure uniform random selection.
6. **Recovery has value:** players who recognize the correct position can land a measurable punish; not every recovery guarantees a heavy hit.
7. **Production visibility:** every state transition, hit window, selected candidate, and branch is debuggable.
8. **Stable gameplay:** difficulty must survive 30/60/120 FPS tests and animation-rate/lag edge cases.

## Core definitions

- **Neutral:** boss is free to evaluate locomotion, reorientation or initiating an attack.
- **Wind-up:** early attack animation. Can include target tracking; usually still telegraphs move type.
- **Hold/delay:** distinctive pause before strike; may be purely authored or an explicitly bounded variable-time animation section. Must not pause indefinitely.
- **Commit/lock:** point after which movement or facing is intentionally constrained.
- **Active window:** exact interval in which one or more attack collision volumes can deal damage.
- **Follow-through:** weapon completes movement; sometimes collision has already ended.
- **Recovery:** time after active window while the boss is unable to initiate most actions.
- **Combo gate:** legal moment to choose a specified follow-up, evaluated against current context.
- **Punish window:** player-action opportunity computed from remaining boss lock minus travel, startup, and safety buffer.
- **Hit confirm:** evaluation whether an attack physically contacted a target (not to be confused with being allowed to branch).
- **Whiff:** attack misses; may have separate follow-up or recovery tuning if authored and fair.
- **Posture/stance:** accumulation that may cause stance break independently of health.
- **Hyperarmor:** interruption resistance on specified attacks or windows; not global invulnerability.
- **Telegraph:** audiovisual and movement cue that communicates an upcoming threat.

## Baseline scenario / non-goals

- First release: **single-player third-person melee**, 60 FPS target, keyboard/controller combat, 1 human boss opponent.
- A player prototype must support light attack, heavy attack, dodge i-frames, optional guard, heal, hurt/knockback, stamina, and death.
- Boss design is unusable without a functioning player defense/hit reaction system; implement a small test character first.
- First release deliberately excludes multiplayer, procedural generation, ML policy training, 50+ attacks, and complex animation-matching. Separate extension docs cover multiplayer.

## Observable fairness invariants (automatable)

- No hit outside an active window except persistent AoE with its own active state.
- A **single-hit** attack damages a particular victim no more than once per activation ID.
- Track lock never exceeds attack-specified angular velocity cap after commitment.
- Any attack's damage onset is after its minimum telegraph time (unless specifically classified as close-range quick punish with its own short cue).
- Every legal combat state has a timeout/fallback; no unending `Attack` state if a Montage interrupt event is missed.
- A phase transition may interrupt an attack only when its transition policy allows it.
- Player dodge invulnerability, block, posture and death states resolve **before** final health damage in a documented order.
- A blocked grab is not treated as a normal sword hit; it has custom guard interaction.

## What makes a move strategically different?

At least two of: (a) timing profile, (b) reach, (c) angular coverage, (d) tracking profile, (e) damage type, (f) punish option, (g) movement displacement, (h) guard/stance consequence, (i) position required for activation, (j) combo branch possibilities. Merely renaming animation clips does not add gameplay depth.

## Sample encounter loop

1. Boss neutral, at 450 cm distance from player.
2. Utility evaluator rejects close thrust and rear sweep, considers advancing lunge vs approach/strafe.
3. Lunge chosen, target point captured; early animation faces the player.
4. Commit event locks facing; authored root motion drives leap.
5. `ANS_AttackWindow` creates a continuous swept trace for the weapon.
6. Player dodges sideways; no hit is registered.
7. At an authored combo gate, if player is inside the lateral zone and branch cooldown passes, follow-up sweep occurs; otherwise recovery starts.
8. Boss is locked for 0.55s. Player reaches flank in 0.20s, light attack startup 0.24s: an approximately 0.11s margin remains — narrow but achievable.
9. Telemetry records the observed result for tuning; boss doesn't secretly read controller inputs.
