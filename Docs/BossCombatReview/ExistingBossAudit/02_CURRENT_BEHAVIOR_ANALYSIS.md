# Current behavior analysis

## What can be stated from the inspected implementation

The ordinary fight is pack-driven, with native components adding constraints and bespoke moves. “Adaptive utility boss” is not established; neither is “purely random boss.” The saved inherited montage selector is random/index-based with last-index avoidance, while the high-level BT choosing the ability is still unverified.

| Behavior | Current evidence | Classification and quality limit |
|---|---|---|
| Engagement | Encounter sleeps until player center is within1200cm or later health loss is detected; wake clip holds behavior before resume | Source-confirmed. Health initialization is separately stabilized for first4s of dormancy. Not LOS-gated wake. [Encounter:65](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.cpp:65), [Encounter:136](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.cpp:136), [Encounter:254](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.cpp:254). |
| Targeting | Pack focused-target activation check in saved export; native tracking directly reads player0 | Mixed. Current perception, last-seen and targetability contract U02. [Export:639](C:/UnrealProject/OneBossFight/Saved/asset_text/GA_EnemyMeleeAttack.t3d:639), [Tracker:466](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:466). |
| Ordinary choice | Exported inherited montage selection supports supplied index or random index, avoids immediate random repeat | Historical graph-confirmed, not proof of current BT weights or all current CDO values. [Export:720](C:/UnrealProject/OneBossFight/Saved/asset_text/GA_EnemyMeleeAttack.t3d:720). |
| Heading | Windup native turn cap; commit yaw held until active end; release during recovery | Source-confirmed mechanism, not proof of final visible sword direction or exclusive rotation authority. [Tracker:450](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:450). |
| Combo | A1b/A3b only continue if observed-stage player within400cm and total120-degree cone | Fresh spatial response exists; check is after next montage starts. No native hit-confirm requirement. [Tracker:172](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:172), [Tracker:411](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:411). |
| Low sweep A4 | Analytic floor arc, jump/iframe/wall-aware | Mechanic exists but native production code does not schedule it; KI-067 says BT never picks it. Natural availability is not proved by a forced test. [Sweep:25](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossLowSweep.cpp:25), [Issues:71](C:/UnrealProject/OneBossFight/Documentation/KNOWN_ISSUES.md:71). |
| Heal reaction A5 | Drink montage rising edge; free/alive/range/LOS/cooldown checks; tell then snapshot-at-release projectile | Player-action-dependent, deterministic once all gates pass. No raw future-input read found. No explicit perception latency. [Heal:95](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHealPunish.cpp:95), [Heal:232](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHealPunish.cpp:232). |
| Phase2 | <=60% HP; ordinary offense interrupted; threshold queued behind break;1.8s roar; leap unlock; pack rate/damage and movement buffs | State/health/phase-dependent. It does more than recolor, but full phase-specific strategy is not established. [Phases:155](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPhases.cpp:155), [Phases:245](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPhases.cpp:245). |
| Posture | Weapon-row drain,100 pool,6s quiet then13/s; down/transition holds | Source-confirmed distinct resource. Current CooldownSeconds default is0, not older5s prose. [PostureH:31](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPosture.h:31), [StaggerH:134](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossStagger.h:134). |
| Riposte | Front/range/facing gate, one accepted execution per break; paired clips,100 impact at.8s, input/overlap restoration | Valuable implementation. Held sprint/guard release during DisableInput remains untested KI-085. [Stagger:497](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossStagger.cpp:497), [Stagger:553](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossStagger.cpp:553), [Stagger:730](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossStagger.cpp:730). |
| Reset/death | Player replacement triggers reset; generation invalidates specials; death-active boss refuses reset | Source-confirmed. Not equivalent to terrain leash. [Encounter:129](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.cpp:129), [Encounter:297](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.cpp:297). |

## Fixed versus contextual

Fixed: timing rows, range thresholds, arc/ring dimensions, posture rules, basic phase modifiers.

Random/index-based: inherited montage chooser in saved GA_EnemyMeleeAttack export. Current probability of a given ability depends on uninspected BT/decorators/state and defaults; no percentage is invented.

Distance/position-dependent: wake, A3/A1b continuation, heal-punish range, native precommit facing, contact geometry. Signed sector hysteresis and a complete spacing policy are not proved.

Player-action-dependent: A5 uses committed drink montage. Boss aggression response, guard/rear counters and target-attack reaction remain U02/U03, even though assets for retaliation/impact exist.

State/phase-dependent: dormancy/wake, break, transition, death and leap unlock; branch denial reacts to movement after the first attack started.

## What quality has and has not been demonstrated

Saved logs show live authored A1/A3a/A3b plus pack A1b trace windows, five sockets and50cm base radius ([Log:3223](C:/UnrealProject/OneBossFight/Saved/Logs/OneBossFight.log:3223), [Log:3271](C:/UnrealProject/OneBossFight/Saved/Logs/OneBossFight.log:3271)). This proves historical execution identity and trace opening, not honest visible geometry.

The project reports37/37 automation in mailbox C-84, a213/213 encounter soak, and prior balance wins around122–143s. These are existing reports, not reruns for this audit. Later close/wake changes mean old balance and soak totals are not a complete current-version acceptance gate.

KI-106/C-84 show real front attacks hitting after real branch denials; the older report's residual-pose root-cause claim is not sustained. Current uncertainty is setup dependence. Do not “fix” montage blending on that historical accusation.

Player-readable telegraphs, useful punish margins, current lock-on framing, controller feel, audio cues and natural attack distribution still require owner gameplay capture. A bot win or passing attribute assertion does not validate them.

