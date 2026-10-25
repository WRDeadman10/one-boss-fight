# Glossary and Design Principles

## Glossary

| Term | Definition in this reference |
|---|---|
| Active window | Exact animation interval during which a named collision mechanism may produce contact. |
| Aggression/pressure budget | Optional pacing resource spent by attacks and restored during neutral/recovery. |
| Anim Montage | Sectioned animation playback asset used for attack timing, blending, root motion and events. |
| Anim Notify | Atomic event at a montage time, such as commit or combo gate. |
| Anim Notify State | Begin/tick/end duration event, such as active trace, tracking or hyperarmor. |
| Attack family | Tactical grouping such as thrust, sweep, slam, gap closer, counter or special, used for variety memory. |
| Attack instance ID | Unique identity for one started move; protects against stale events and scopes hits. |
| Awareness/context | Timestamped observable world and combat state used for a decision. |
| Behavior Tree (BT) | High-level AI activity orchestration; not the owner of the active attack timeline. |
| Blackboard | Shared BT key/value state such as target, LOS, mode and movement goal. |
| Branch/Combo gate | Authored legal moment where only linked follow-ups may be evaluated. |
| Commit/lock | Point after which target/facing/motion changes become restricted by the move. |
| Combo ID | Identity linking several attack instances into one sequence for caps and telemetry. |
| Contact | Physical query result before iframe, parry, guard, posture and health adjudication. |
| Cooldown | Hard temporal unavailability, normally committed when an attack actually starts. |
| Damage resolver | Single policy owner that converts valid contact into defense, posture, health and feedback outcomes. |
| Decision gate | State/event at which a new action choice is legal. |
| Decision trace | Context, eligibility reasons, scores, seed and chosen action recorded for one gate. |
| EQS | Environment Query System used to generate/filter/score legal positioning points. |
| Follow-through | Motion after danger ends but before or overlapping recovery. |
| GAS | Gameplay Ability System; optional framework for abilities/effects/attributes, not required by the architecture. |
| Grab | Narrow capture contact followed by custom defense, paired alignment, control lock, damage and release. |
| Guard/block | Directional defensive adjudication that mitigates or redirects damage at a cost. |
| Hard gate | Binary feasibility constraint applied before utility scoring. |
| Hit confirm | Recorded contact/outcome used by an explicitly authored branch policy. |
| Hit policy | Rule for once-per-attack, once-per-window, periodic or impact-plus-splash damage. |
| Hitstop | Brief presentation freeze that must not duplicate traces or desynchronize timers. |
| Hurtbox | Collision representation accepted as a combat target. |
| Hyperarmor | Temporary resistance to specified interruptions; not general invulnerability. |
| I-frames | Explicit player state/window that rejects specified damage contacts. |
| Legal state | Executor/encounter state in which a given transition is authorized. |
| LOS | Line of sight required for specified perception and reaction rules. |
| Motion Warping | Bounded adjustment of authored root motion toward a named target during a notify window. |
| MoveCard | Animation handoff record of axes, scale, timing, displacement, sockets, cues, windows and policies. |
| Near-best sampling | Seeded weighted choice restricted to candidates close to the best score. |
| Neutral | State where new attack, movement or wait decisions may be made. |
| Parry/deflect | Short tagged defense window that produces a special attacker reaction. |
| Phase | Coherent rule set controlling moves, weights, pacing, movement, recovery and presentation. |
| Posture/stance | Accumulated break metric separate from health and immediate flinch. |
| Punish window | Usable player opportunity after travel, startup and safety are deducted from boss lock. |
| Recovery | Post-danger commitment during which most new boss actions remain locked. |
| Root motion | Translation/rotation authored on the animation root and applied to the character. |
| Signed yaw | Planar left/right target angle relative to boss facing. |
| Soft utility | Comparable desirability score among already legal choices. |
| StateTree | Alternative high-level hierarchical planner; should not compete with a BT for authority. |
| Swept annulus | Previous-to-current expanding ring band used for radial wave collision. |
| Swept weapon trace | Query from previous to current weapon sample positions, preventing tunneling. |
| Telegraph | Pose, motion, sound or effect that communicates attack identity and release. |
| Utility AI | Eligibility plus scoring plus bounded selection over possible actions. |
| Watchdog | Maximum-duration fallback that repairs a stale attack when expected animation events fail. |
| Whiff | Attack fails to contact; may have an authored recovery or branch policy. |
| Wind-up/anticipation | Pre-active animation communicating the incoming move and optionally tracking early. |

## Design principles

1. **Responsiveness is gated, not continuous.** Read current context at neutral, authored combo and limited reaction gates; never rewrite a committed hit.
2. **Player-visible commitment is the fairness contract.** A strong early aim is acceptable when the move later locks enough to create a spatial or temporal answer.
3. **Hard legality precedes preference.** Phase, state, range, angle, LOS, cooldown, resource, asset and path checks are never outweighed by utility.
4. **Uncertainty must remain learnable.** Use cooldowns, history and bounded seeded choice among near-best options, not uniform randomness or hidden perfect counters.
5. **One system owns each truth.** Executor owns attack state; montage owns authored timing; trace owns contact discovery; resolver owns defense/damage; phase/posture own their state.
6. **Animation and collision form one contract.** Visible weapon/effect path, notify windows, swept geometry and contact timing must agree across frame rates.
7. **Contact is not damage.** Iframes, parry, guard, armor, posture and health are centrally ordered outcomes of a valid contact.
8. **Motion authority changes explicitly.** Navigation, root motion, Motion Warping and manual transforms never compete during commitment.
9. **Every temporary state has an exit.** Normal end, blend-out, interrupt, death, phase, reset, destruction and watchdog all close collision and restore control.
10. **Combos are authored graphs.** Branch only at named gates, only to linked edges, from fresh context, with finite depth and reliable recovery.
11. **Punishment is positional math.** Judge openings after travel, player startup and safety; test multiple weapons and response distances.
12. **Pressure must breathe.** Neutral, recovery and resets are part of challenging combat, not evidence of weak AI.
13. **Arena geometry is combat data.** Walls, vertical layers, boundary, camera and escape distance constrain move viability.
14. **Defense has costs and tells.** Boss parry, block, dodge, rear counter and guard break need startup, cooldown, failure and recovery.
15. **Phases change rules coherently.** Transition safely and once; do not merely add damage or delete all openings.
16. **Debuggability is a feature.** Log why a move was chosen and why a contact did or did not damage before trying to balance it.
17. **Measure actual assets.** Illustrative spreadsheet times never override imported montage/contact measurements.
18. **Tune root causes in order.** Fix camera and hitbox mismatch, then tracking, then defensive timing, recovery, attack frequency, damage and utility weights.
19. **Presentation communicates mechanics.** VFX, sound and camera identify geometry/timing; they do not hide a mismatch.
20. **Accuracy claims stay bounded.** This package proposes original systems and values; it does not document proprietary Elden Ring internals.

## Basic versus advanced implementation

| Basic | Advanced |
|---|---|
| Random montage from a list | Hard gates, explainable utility, history and seeded bounded variation. |
| Per-tick face target | Per-move staged rotation cap and commit snapshot. |
| Delay opens a broad collider | Montage Notify State authorizes swept, geometry-specific traces. |
| Overlap directly subtracts health | Central contact record and defense/damage resolver. |
| Fixed combo array | Data-authored graph with context-sensitive gates and default recovery. |
| One global stagger boolean | Health, hit reaction, posture and hyperarmor matrix. |
| Phase = faster animations | New rule set with safe one-shot transition and preserved counterplay. |
| Recovery judged by eye | Instrumented punish margin for several player builds/positions. |
| End notify is the only cleanup | Instance validation, blend/end delegates, idempotent abort and watchdog. |
| “Feels unfair” debugging | Reproducible seed, context/decision/contact logs and frame-rate matrix. |
