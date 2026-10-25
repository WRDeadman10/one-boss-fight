# Movement, recovery and pacing

## Current movement knowledge

Native encounter/wake/phase/stagger code holds or resumes the pack behavior manager and stops CharacterMovement for major transitions. Ordinary chase, strafe, retreat, combat spacing and attack displacement remain pack-owned. BT dependency names establish where to inspect, not what movement actually does.

Tracker rotates the actor toward player0 before commitment (120/180/240/360deg/s depending on move), then writes committed yaw each tick through active end. It does not explicitly stop navigation on every attack or bound recovery yaw. Root-motion modes, slot layering, S_RotateCharacter interaction and travel ability displacement need U02/U04/U06. No active Motion Warping system is proved; adding one is not an audit recommendation by default.

Wall suppression in RPGTraceGuard prevents certain blade damage through blockers; it does not validate where a leap lands. A4 uses a low LOS line, A5 uses world sweeps with near-hand penetration grace, and A6 has no native wall/path query. Arena boundary/leash behavior cannot be inferred from the respawn reset.

## Recovery is not a number in a row

[Tracker:251](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:251) uses RecoveryEndTime to count an early end. It does not keep a recovery deadline or hold selection until that timestamp. [Tracker:465](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:465) enters Recovery at active end and releases heading. [Tracker:134](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:134) only regards no tracked move/no montage/no special state as neutral for own move starts. Pack ability/BT gates may provide stronger lockout, but that remains unverified.

Consequences:

- An authored1.20s end timestamp is not proof of a.70s usable opening after A1 active end.
- A3a's.60→.80 interval may be transition to A3b, not an opening.
- Branch-denied montage stop may expose a different gap than the original row implies.
- A5 recovery ends before its projectile necessarily arrives; a neutral boss is not automatically a safe player punish state.
- Phase2 play-rate scaling changes real-time margins even when montage-local markers stay aligned.

Do not retune damage or add long idle delays to conceal an unmeasured recovery contract.

## Punish calculation to measure

For each intended opening:

usable margin = earliest legal boss retaliation time - player decision time - travel time - player attack startup - agreed safety buffer.

Use actual first possible damaging contact of the player's chosen swing, not full animation duration. Record starting center/surface distance and build. Test Starter light/strong, Strength jumping heavy, and Dex light/strong at contact,1m and2m away; include stamina availability and whether movement/attack startup overlap. Averages from bot fight lengths do not establish this.

Current source exposes posture/stamina/build distinctions, but no complete current per-move/build/position margin table was located. This is UNVERIFIED, not proof that every move is unpunishable. Preserve already successful fight loops while collecting it.

## Pressure and phase

Fixed arrays and finite observed chains are some pressure bounds; they do not limit repeated outer BT activations. No native pressure-budget component exists in the inspected active layer. The pack may provide waits/aggression rules; U02 must establish them before a new system is proposed.

Phase2 adds leap plus pack montage/movement/damage scaling. It intentionally interrupts ordinary attacks at threshold and waits behind an earned break/riposte. That is an explicit project policy, allowed by the reference's configurable transition model; it is not an automatic “unsafe phase” defect. Extend its tests to hitches, failed clips and persistent special damage.

The visible blade/ground-wave cue is higher priority than pressure sophistication. Once contact honesty and timing are reliable, measure long-run attack bursts, repeated families, time spent chasing, time in guaranteed recovery, and heal response rate. Add a budget only if existing waits cannot guarantee intended breathing room.

## Arena and camera acceptance

The current arena is flat; do not invent a stairs requirement for a nonexistent legal route. Test every actually legal boundary/entrance/prop position, then include out-of-bounds/elevated cases as abuse tests. A valid response must be possible without clipping or losing release cues. Camera floor/pitch/probe safeguards already exist; current lock-on, near-boss overhead and controller readability are still owner tests (KI-066).

Performance is part of pacing: the last reported Shipping baseline is28–29FPS with p99~40ms on the accepted3060 proxy. Development lighting experiments are promising but variable. Preserve the60FPS/p99<=16.67ms target;120FPS remains parity testing/stretch telemetry, not the release performance gate.

