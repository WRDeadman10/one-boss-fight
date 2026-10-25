# Existing Boss Audit Checklist

This is a future inspection plan only. It does **not** state that any listed asset or system exists in the current project, and this phase did not inspect the boss implementation.

## Evidence collection order

1. Inventory the boss pawn/controller, BT **or** StateTree, Blackboard, components, interfaces, GAS/attributes/tags if present, attack/phase/graph Data Assets, Montages, AnimBP, Notify classes, weapon sockets, collision profiles, arena/nav/EQS, player combat states, camera/UI/debug tools and tests.
2. Identify authority for selection, execution, motion, contact, damage, posture, phase, reset and telemetry. Record duplicate writers before judging behavior.
3. Extract every attack into a comparison sheet: gates, timing, tracking, motion, geometry, hit policy, defense policy, branches and recovery.
4. Inspect static assets/graphs first; then use deterministic runtime scenarios with fixed starts and seeds.
5. Record evidence as Present, Code-confirmed, Runtime-confirmed, Partially working, Missing or Blocked. A Blueprint node or C++ branch alone is not runtime proof.

## Requirement-by-requirement evidence

### Awareness and selection

| Requirement | Static evidence to inspect | Runtime/test evidence required |
|---|---|---|
| BOSS-AWR-001 | Target-validity functions, death interface, arena/leash actor and controller target-clear paths. | Target killed/destroyed/leaves arena; log shows reject/search/reset and no stale attack. |
| BOSS-AWR-002 | Context struct/builder and all neutral/combo/reaction call sites; timestamp field. | Change context around a gate; one coherent snapshot appears in decision log. |
| BOSS-AWR-003 | Per-attack range fields and distance helper implementation/debug labels. | Measured root/surface/origin placements match eligibility boundaries. |
| BOSS-AWR-004 | Signed-yaw helper, sector data and hysteresis variables. | 0/45/100/170-degree placements plus slow boundary crossing. |
| BOSS-AWR-005 | Z tolerance, floor/level checks and melee/AoE vertical filters. | Player on ledge/other floor receives no illegal melee/ground damage. |
| BOSS-AWR-006 | Player observable interface/tags, montage/ability state writers and AI readers; confirm no raw-input dependency. | Pre-commit cancel versus committed attack/heal produces appropriate reaction difference. |
| BOSS-AWR-007 | AI Perception setup, LOS trace, last-seen timestamp/position and reacquire policy. | Occlusion/heal/movement test proves no exact hidden tracking. |
| BOSS-AWR-008 | Pattern-memory storage, decay/cap formulas and utility integration. | Repeated behavior shifts scores, then returns toward baseline after decay. |
| BOSS-SEL-001 | Every selector invocation from BT/StateTree, executor and notifies. | Instrumented fight shows selection only at named gates. |
| BOSS-SEL-002 | Eligibility function and attack fields for every hard constraint. | Table-driven scenario toggles one constraint at a time and logs rejection. |
| BOSS-SEL-003 | Montage/socket/resource/path validation before selection/start. | Invalidate each dependency; move is rejected without stuck state. |
| BOSS-SEL-004 | Utility formula, curves/weights, normalization and debug trace fields. | Monotonic/boundary tests plus candidate term dump for fixed contexts. |
| BOSS-SEL-005 | RNG owner/seed, near-best threshold and sampling code. | Same-seed replay matches; many-seed histogram excludes weak moves. |
| BOSS-SEL-006 | Cooldown map/tags, write site and time-base definition. | Rejected/failed start preserves readiness; committed start consumes it once. |
| BOSS-SEL-007 | Attack/family history buffer and decay/min-spacing data. | Repeat score falls then recovers; signature spacing is enforced. |
| BOSS-SEL-008 | No-candidate branch in planner and bounded move/wait/reset tasks. | Force all moves invalid; no tight loop/stall and fallback completes. |
| BOSS-SEL-009 | Reaction-delay timers/tags, cooldown/budget and feasibility tests. | Boundary trials for latency, LOS, range and cooldown; reaction not guaranteed. |
| BOSS-SEL-010 | Structured log/schema and candidate rejection/score instrumentation. | One forced decision contains complete context, candidates, winner and seed. |

### Executor and combo graph

| Requirement | Static evidence to inspect | Runtime/test evidence required |
|---|---|---|
| BOSS-EXE-001 | All functions/nodes that set current attack, play attack montage or enable damage; ownership diagram. | Trace one attack and prove one live authoritative instance/writer. |
| BOSS-EXE-002 | Start sequence ordering around ID/state assignment and montage play. | Earliest notify carries correct new ID/state. |
| BOSS-EXE-003 | Montage-play return handling and rollback of movement/tags/cooldown/window. | Forced invalid montage returns safely to neutral. |
| BOSS-EXE-004 | Notify/event payloads and montage/section/instance/state checks. | Duplicate/delayed event injection is ignored and logged. |
| BOSS-EXE-005 | Central transition-priority table or equivalent guarded entry points. | Same-frame death/phase/break/gate pairs in reversed order yield same outcome. |
| BOSS-EXE-006 | `Abort/Finalize` implementation and every caller; idempotence guards. | Double abort at wind-up/active/recovery leaves clean identical state. |
| BOSS-EXE-007 | Max-duration data, watchdog timer/tick and timeout recovery. | Suppress completion/end and observe bounded recovery. |
| BOSS-EXE-008 | Cleanup and unlock ordering; trace/warp/armor queries. | Frame/event log proves old resources closed before neutral/new start. |
| BOSS-COM-001 | Attack-graph Data Asset/table, node/edge schema and gate lookup. | At a node, only declared outgoing edges ever start. |
| BOSS-COM-002 | Montage gate positions versus active-window end positions. | Timeline capture shows gate occurs after closure as authored. |
| BOSS-COM-003 | Context rebuild call inside combo gate. | Reposition after start changes branch according to gate-time state. |
| BOSS-COM-004 | Edge hit-confirm/whiff/guard/damage policy fields and outcome source. | Test all relevant prior outcomes and verify branches. |
| BOSS-COM-005 | Consumed-gate set/flag keyed by instance and gate. | Duplicate notify/callback cannot launch twice. |
| BOSS-COM-006 | Max depth, edge-use/cooldown and max-pressure controls; graph cycles. | Forced favorable branch conditions still terminate within cap. |
| BOSS-COM-007 | Default recovery edge, invalid-target/asset handling. | Remove target/follow-up at gate and observe declared recovery. |

### Animation and motion

| Requirement | Static evidence to inspect | Runtime/test evidence required |
|---|---|---|
| BOSS-ANM-001 | Montages/sections/notifies and any parallel timers for commit/active/recovery. | 0.75x/1.25x playback keeps gameplay events at montage positions. |
| BOSS-ANM-002 | MoveCards, animation poses, audio/VFX notify tracks and active times. | Gameplay-camera captures at tell/release/contact demonstrate readable geometry. |
| BOSS-ANM-003 | Hold section/variant logic, min/max and choice time. | Dodge inputs after choice cannot alter release; all variants stay bounded/cued. |
| BOSS-ANM-004 | Tracking-window notify/data, controller rotation flags and yaw-clamp code. | Per-frame yaw graph for crossing behind before/after commit. |
| BOSS-ANM-005 | AI MoveTo stop, movement mode, root-motion settings, Tick transforms and warp component. | Instrument all motion sources during attack; only declared owner changes transform. |
| BOSS-ANM-006 | Warp notify windows, target update sites, clamps and path/ledge fallback. | Moving-target, wall, stairs and off-nav trials verify cutoff/bounds. |
| BOSS-ANM-007 | Montage blend/end delegates, interrupt cleanup and Notify State end dependency. | Interrupt on every boundary; no window/armor/warp survives. |
| BOSS-ANM-008 | Per-move animation handoff/metadata, import settings, skeleton, axes, FPS and socket paths. | Compare card values with editor/runtime measurements at 30/60/120 FPS. |

### Contact and damage

| Requirement | Static evidence to inspect | Runtime/test evidence required |
|---|---|---|
| BOSS-HIT-001 | Attack geometry Data Assets/BPs, sockets, collision shapes and VFX bounds. | Debug overlay captured with visible weapon/effect at before/contact/end. |
| BOSS-HIT-002 | Previous/current transform cache and sweep calls inside active update. | Fast strike hits thin target once at 30/60/120 FPS. |
| BOSS-HIT-003 | Number/location of blade samples or swept capsule chain. | Mid-blade target hit when endpoint-only method would miss. |
| BOSS-HIT-004 | Travel/angular thresholds, substep loop and hard sample cap. | High rate/low FPS maintains hit while query count stays bounded. |
| BOSS-HIT-005 | Collision channel/profile, query params, ignore lists and team filtering. | Owner/ally/scenery/target line-up reaches resolver only for intended target. |
| BOSS-HIT-006 | Victim identity normalization and per-instance/window hit set. | Several body overlaps in one frame create one logical hit. |
| BOSS-HIT-007 | Hit-policy enum/data and reset/periodic counters. | Once-attack/window/periodic/impact+splash cases produce exact counts. |
| BOSS-HIT-008 | All damage entry points and central resolver order; prove no bypassing overlap damage. | Simultaneous iframe/parry/guard states resolve deterministically with reason. |
| BOSS-HIT-009 | Iframe state source and health/posture early-out. | Tests immediately before/inside/after window show zero effects only inside. |
| BOSS-HIT-010 | Direct/AoE precedence keying and double-dip option. | Victim in both regions receives authored event count/damage. |
| BOSS-HIT-011 | Ring actor/component radius history, band-width query and victim set. | Positions inside/at/outside moving band across FPS; no damage after pass. |
| BOSS-HIT-012 | Grab collider, eligibility, paired montage/warp, input/attachment/release cleanup. | Miss, wall, death/reset at each stage restores control and valid placement. |

### Movement, arena and pacing

| Requirement | Static evidence to inspect | Runtime/test evidence required |
|---|---|---|
| BOSS-MOV-001 | Range-band/phase movement data and planner branches. | Distance sweep shows intended tactic transitions with hysteresis. |
| BOSS-MOV-002 | EQS/query template tests and scoring weights; nav/hazard filters. | Visualize candidate scores and selected safe point in representative arena states. |
| BOSS-MOV-003 | Replan cadence/cooldown/minimum commitment and MoveTo task lifecycle. | Goal-change log shows no per-frame restart/jitter. |
| BOSS-MOV-004 | Root-motion path sweep, wall response and per-move fallback data. | Every travel attack from wall/corner/obstacle positions remains legal. |
| BOSS-MOV-005 | Leash/reset/search tasks and vertical/reachability checks. | Ledge/outside/unreachable cases terminate in bounded fallback. |
| BOSS-MOV-006 | Arena collision/nav map, effective dimensions, camera collision and each move's escape requirement. | Boundary/obstacle/stair/camera scenario matrix proves at least one legal response. |
| BOSS-PAC-001 | Montage markers and attack data for all timing segments. | Runtime event timeline matches asset positions for each move. |
| BOSS-PAC-002 | Pressure/aggression state, costs, regeneration and phase modifiers, or equivalent explicit pacing policy. | Long-run graph shows bounded bursts and reset intervals. |
| BOSS-PAC-003 | Attack recovery classifications and minimum lock implementation. | Script defined punish for each guaranteed-opening move. |
| BOSS-PAC-004 | Conditional edge timing, transition animation and cues. | Blind/recorded trials show branch outcome can be recognized before retaliation. |
| BOSS-PAC-005 | Player movement speeds/startups by build and punish instrumentation. | Compute/measure margin at specified distances for fast and slow attacks. |
| BOSS-PAC-006 | Neutral state actions, wait ranges and non-attack movement tasks. | State timeline/video shows purposeful but non-damaging neutral behavior. |

### Defense, posture and phase

| Requirement | Static evidence to inspect | Runtime/test evidence required |
|---|---|---|
| BOSS-DEF-001 | Attribute/component ownership for health, hit reaction and posture; hit-class table. | Same attacks demonstrate independently varying damage/flinch/posture. |
| BOSS-DEF-002 | Posture max, last-hit timestamp, delay/rate and reset paths. | Drain/wait/re-drain timing verifies delay, rate and restart. |
| BOSS-DEF-003 | Threshold crossing guard, break entry, critical window and offense cleanup. | Simultaneous hits trigger one break; active attack cannot damage afterward. |
| BOSS-DEF-004 | Hyperarmor Notify States/tags and interruption matrix. | Each hit class just outside/inside window matches policy; death always wins. |
| BOSS-DEF-005 | Boss guard/parry/dodge selection, facing/timing/cost/cooldown/recovery. | Repeated varied attacks prove defense is fallible, directional and punishable. |
| BOSS-PHS-001 | Phase Data Assets/config and code applying pool/weights/combo/movement/pressure/recovery/presentation. | Before/after dump shows one coherent rule-set switch. |
| BOSS-PHS-002 | Threshold listener, pending transition state and safe-gate/interrupt policy. | Cross threshold in wind-up/active/recovery/stagger/grab/death/AoE cases. |
| BOSS-PHS-003 | One-shot/phase-monotonic flags and reset behavior. | Cross/heal/cross and duplicate callbacks produce one transition per encounter. |
| BOSS-PHS-004 | Player heal-state source, reaction listener/gate, latency, LOS/range/travel/cooldown checks. | Matrix varies each condition; heal after boss commit never swaps current attack. |
| BOSS-PHS-005 | Rear/guard/kite/terrain/wall response definitions, cues, cooldowns and reset rules. | Long scripted exploit cases show bounded readable response and counterplay. |

### Debug, QA, camera and optional networking

| Requirement | Static evidence to inspect | Runtime/test evidence required |
|---|---|---|
| BOSS-QA-001 | Debug component/UI/console toggles and data providers. | One forced move shows phase/state/instance/context/montage/tracking/window/gate/cooldown/pressure live. |
| BOSS-QA-002 | Event structs/schema, log category/sink and stable IDs for every major event. | Parse a full encounter and verify causal ordering/required fields. |
| BOSS-QA-003 | Seed control, deterministic setup script and captured starts/player actions. | Repeat the same scenario and compare decisions/outcomes. |
| BOSS-QA-004 | Fixed-FPS/time-dilation controls and automation/runtime drivers. | Compare 30/60/120 and supported time scales for hits, cleanup, branches and transforms. |
| BOSS-QA-005 | Tick settings, selector cadence, trace sample counters, pooling and profile markers. | Packaged Unreal/Animation Insights capture meets an agreed frame-time/query budget. |
| BOSS-QA-006 | Spring arm/camera/lock-on target, collision settings and move visibility assumptions. | Capture close, wall, overhead, long-sweep and giant-boss cases; cues remain visible. |
| BOSS-QA-007 | Shake/effects/accessibility settings and alternative color/audio cues. | Review all moves with reduced shake/effects and color alternatives; identity/timing remains legible. |
| BOSS-QA-008 | Only if networking exists: server-authority code, replicated attack ID/start time/section/target/phase and montage sync. | Listen/dedicated two-client tests at 80/150 ms and packet loss; no duplicate hits or illegal retarget. |

## Cross-cutting artifacts to request

- One attack catalogue exported from the real Data Assets with every eligibility, timing, motion, geometry, defense, branch and recovery field.
- One event log and synchronized video/debug capture for each forced attack.
- Blackboard/BT or StateTree diagrams and task/service call sites.
- AnimBP slot graph, Montage section/notify dumps and root-motion settings.
- Weapon skeleton/mesh sockets and collision profile definitions.
- Damage entry-point call graph proving centralized adjudication.
- Posture/hyperarmor/phase priority matrix.
- Arena dimensions, navmesh/EQS debug and wall/vertical test map.
- Player action-state, iframe, guard, startup and movement-speed evidence for every supported build.
- Deterministic automation/PIE test table, multi-FPS results and packaged performance capture.

## Stop condition for the future audit

Do not recommend implementation changes until each requirement has at least static evidence or is marked Missing/Blocked, and runtime-sensitive claims are distinguished from code presence. Findings should cite exact asset paths, Blueprint nodes/functions, C++ symbols, log events or captured frames.
