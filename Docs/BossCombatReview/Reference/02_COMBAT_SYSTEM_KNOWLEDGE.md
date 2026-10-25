# Combat System Knowledge

## 1. Governing model

The package defines a boss as a closed, observable control loop:

`Observe -> build context -> choose at a legal gate -> commit -> animate -> test contact -> adjudicate defense/damage -> recover -> update encounter memory -> repeat`.

The key quality boundary is not “complex AI.” It is clean authority. Awareness describes the world; utility selects among legal options; one executor owns the live attack; animation supplies timing and motion; traces discover contact; one resolver decides the result. A boss becomes advanced when those systems retain their boundaries while responding to current player context.

## 2. Combat intelligence

### Purpose

Combat intelligence makes the boss responsive without granting psychic knowledge. It converts observable state into a timestamped `FCombatContext` and uses that snapshot only at authorized decision points.

### Required information

- Valid target, last-seen transform/time, arena membership and reachability.
- A declared distance convention, planar signed yaw, vertical separation and line of sight.
- Smoothed target velocity and visible committed activity: attack phases, heal/cast, dodge, guard, stagger and recovery.
- Boss phase, health, posture, cooldown/resource state, pressure budget and recent attack/family history.
- Arena safety data such as walls, hazards, navigation and legal warp destinations.

### Behavior

Hard gates remove impossible actions before scoring: wrong phase, state, range, angle, LOS, cooldown, resource, montage/socket or navigation requirement. Soft utility then compares range fit, angle fit, opportunity, spacing value, phase style and variety, minus repetition and risk. A deterministic maximum is useful during early debugging; production variety comes from seeded bounded noise or temperature-weighted sampling among near-best candidates. If no attack is eligible, the boss repositions, reorients, approaches or intentionally waits.

Reactions use visible commitment plus nonzero latency. A heal punish is legal only if the boss is free, sees the player, can physically reach them before the opportunity ends, is off cooldown and passes its selection rule. Memory is short-lived and capped; it biases choices rather than guaranteeing counters.

### Correctness and player effect

The player should be able to manipulate the boss by range, angle, timing and visible actions. Correct behavior produces contextual but explainable choices, logs rejected candidates, and never changes an in-flight attack because of a newly pressed input. Advanced behavior adds uncertainty, hysteresis, decaying memory, risk and spacing value while preserving legal gates and reproducibility.

## 3. Attack definitions and execution

### Purpose and data

An attack is a complete contract, not an animation name. Its data should describe identity/family, phase availability, range and yaw sectors, ideal distance, LOS/resource/cooldown gates, montage/sections, timing, tracking/warp policy, geometry, damage/posture/guard behavior, hit policy, cancel policy, follow-ups, recovery/punish class and audiovisual cues.

### Execution lifecycle

One executor owns `AttackInstanceID`, attack asset, section, state, start time, target snapshot and hit-victim sets. It validates neutral/gate legality, assigns the new ID before montage start, rolls back a failed montage, accepts only matching notifies, controls motion authority, closes every active hit window before unlocking, and uses blend-out/end delegates plus a watchdog as redundant cleanup paths.

Typical states are `Neutral`, `Positioning`, `Windup`, `Committed`, `Active`, `Recovery`, `Staggered`, `PhaseTransition` and `Dead`. A documented priority such as death over authorized phase transition over stance break over special reaction over combo gate over completion prevents same-frame event order from deciding gameplay accidentally.

### Advanced versus basic

A basic implementation plays a montage and enables a collider with delays. An advanced implementation has data-defined eligibility, instance-scoped notifies, explicit commit/cancel rules, authoritative recovery, interruption-safe cleanup, debug traces and distinct tactical roles. Every move should differ in at least two dimensions such as timing, reach, coverage, tracking, damage type, displacement, punish, activation position or branch options.

## 4. Conditional combo system

Fixed sequences always play the same ordered sections. Random sequences pick follow-ups without enough context. A conditional combo is a directed graph whose nodes are authored move stages and whose edges exist only at named animation gates.

At a combo gate, the executor first closes the ended hit window, builds fresh context, evaluates only outgoing edges, applies phase/range/yaw/action/hit-confirm/cooldown/depth rules, consumes the gate once, and either transitions with an authored blend or follows a default recovery. Hit confirmation and branch permission are separate policies: a move may continue on whiff, on contact, or on proximity, but the choice must be explicit.

Combo depth, edge cooldown/use counts and a maximum pressure duration prevent infinite offense. Advanced combos remain learnable: player positioning predicts which branches become legal. They do not branch arbitrarily during active damage.

## 5. Animation intelligence

### Motion authority

Neutral locomotion belongs to Character Movement and AI navigation. Committed attacks normally use authored root motion; selected gap closers may use Motion Warping during a named early window. `MoveTo`, per-tick actor translation/rotation, root motion and warping must not compete.

### Tracking and commitment

Each move defines a staged turn profile: high capped tracking in early wind-up, sharply reduced tracking in late wind-up, normally zero or very low tracking during active damage, and no snap during recovery. The warp target is sampled or refreshed only while authorized and freezes by commitment. This creates a spatial solution for dodging.

### Montage contract

Montages/sections carry commit, tracking, active-window, combo-gate, recovery, armor and completion events. Notify States open/close duration windows; point notifies signal atomic gates. Every callback validates live instance and state. Because notify ends can be skipped during blends or interruptions, the executor—not the notify—owns final cleanup.

Advanced animation integration measures real socket paths and contact frames, supports play-rate changes, records root axes/capsule displacement, and requires a MoveCard from animation production. It treats IK and layered blending as controlled polish, never as a second motion authority.

## 6. Hit detection and damage

### Geometry families

- Thrust: a narrow tip sphere/capsule swept through its path.
- Sweep: multiple samples along the blade swept between previous and current transforms.
- Slam: direct weapon contact plus a separately specified impact volume.
- Radial wave: a moving annular band swept from previous to current radius, not a permanently damaging disk.
- Lane/beam: a forward box/capsule/trace, with explicit periodic policy if persistent.
- Grab: a narrow capture volume followed by defense checks, alignment and paired-animation state.

### Contact and adjudication

Fast weapons require spatial sweeps between frames and interior blade samples; endpoint-only tests can miss a rotating blade. Adaptive substeps are triggered by excessive sample travel or angular change. Contact records attack, instance, window, victim, point, normal, bone, instigator, damage type, posture and time.

Hit policy is explicit: once per attack, once per window, periodic with a cap, or direct-impact-plus-splash with defined precedence. Multiple target bodies map to one logical victim. Contact is not damage. A centralized resolver validates actor/team/instance, deduplicates, then applies the documented defense order: invulnerability/dodge, parry/deflect, guard/block, armor/posture, health/elemental damage, stagger/knockback and feedback. An iframe-protected contact can be logged while applying no health or posture.

Correctness requires collision to match the visible weapon or effect at 30/60/120 FPS, no damage outside active windows, no accidental double-dip, Z/LOS rules for floor effects, and guaranteed shutdown on every abnormal exit.

## 7. Movement intelligence and arena use

Navigation handles long travel; combat locomotion handles committed strafes, pivots, retreats and attack transitions. Range bands map space to meaningful options: danger-close response, ideal weapon exchange, approach/lunge and reacquisition. EQS or equivalent position search scores reachability, desired distance, LOS, wall clearance, hazards, flank value and variety, then commits briefly to one destination instead of re-querying every frame.

The arena is part of combat balance. Attack reach, required escape distance, camera clearance, obstacles, stairs, vertical layers and boundary size must be measured together. Root-motion attacks need path validation and a wall-safe fallback. Unreachable or out-of-arena targets cause search/leash/reset rather than damage through floors or endless projectile spam.

## 8. Combat pacing and punish windows

Every attack is segmented into anticipation, optional bounded hold, commit, active contact, follow-through, recovery and neutral. Delayed releases are fair when their variant is selected before commitment, min/max duration is bounded and the release has a consistent cue.

Pressure should rise and fall. Neutral can contain purposeful movement, facing and observation. An optional pressure budget makes attacks spend aggression and neutral/recovery replenish it, guaranteeing resets even in a more aggressive phase.

A punish window is not simply montage recovery:

`usable punish = guaranteed boss lock - player travel - player attack startup - safety buffer`.

Openings may be guaranteed, conditional, spacing-created or resource-created. Correct tuning tests fast and slow player builds from multiple positions. Advanced pacing varies rhythms and conditional follow-ups while retaining some unmistakable high-commitment openings.

## 9. Defensive and reactive behavior

Boss defense must have the same fairness constraints as offense. Blocks need a facing cone, stamina/posture cost and recovery. Parries apply only to tagged moves during short windows. Boss dodges have reaction startup, failure chance/opportunity cost, cooldown and recovery; they cannot perfectly evade every hit. Rear counters and guard breaks are conditional moves with tells and cooldowns, not invisible omnidirectional immunity.

The player-side resolver must distinguish dodge, guard, parry, grab and ordinary damage. Grabs need capture eligibility, paired alignment, wall/edge handling, damage/release events and a fail-safe that always restores input and attachment state.

## 10. Posture, stagger, hyperarmor and phases

Health, immediate hit reaction and posture are separate. Posture accumulates independently, regenerates only after a quiet delay and triggers exactly one stance-break transition at threshold. Hyperarmor suppresses specified interruption classes during explicit windows but does not imply invulnerability; whether posture can break through armor must be a documented matrix rule.

A stance break closes traces, clears warping/combo state, plays a dedicated reaction and exposes a bounded critical window. It cannot leave the executor or movement locked. Death always terminates cleanly.

A phase is a rule-set asset: allowed attacks, utility modifiers, movement profile, combo depth, pressure, recovery and presentation. The recommended first policy queues a threshold crossing until a safe gate. It applies once, cannot oscillate with healing, and is regression-tested when crossed during wind-up, active, grab, stagger, death and persistent AoE.

## 11. Debugging, validation and production quality

The minimum debug view exposes phase/state/instance, target context, chosen/rejected candidates, montage position, tracking cap, hit window/victims, next gate, cooldown/pressure and defense result. Events carry encounter/seed/time so runs are reproducible. Trace paths, AoE radius, warp targets, range bands and arena safety must be drawable.

Correct implementation is demonstrated by deterministic logic tests plus scripted runtime scenarios at multiple frame rates, animation rates and interruption points. Balance evidence includes use/hit rates, repeats, rotation overshoot, fake-opening deaths, tunneling, wall clips and punish margins. Performance is protected by gate-time scoring, active-window-only bounded traces, pooled cosmetics and packaged profiling.

VFX, sound and camera are functional communication channels: they must identify geometry and release timing without obscuring threats. Accessibility includes reduced shake/effects, non-color-only cues and usable lock-on/camera behavior.

## 12. Status of the Ashen Bellwarden example

The Bellwarden, its twelve attacks, all timings, weights, dimensions, health/posture and phase values are illustrative design proposals. They demonstrate system coverage—thrust, sweep, slam, lunge, rear counter, defensive counter, combo, delayed attack, multi-hit spin, annulus, lane and grab—but are not requirements for another boss and are not claims about Elden Ring internals.
