# Mohg, Lord of Blood — 82-Point Combat Engineering Reference

**Unreal Engine 5.5 / 5.5.4 • Behavior-informed implementation guide • 30 October 2026**

> **Purpose:** Reuse exactly the original 83 BossCombatReview requirement IDs except `BOSS-QA-008` (network/multiplayer authority). Map each remaining requirement to Mohg’s encounter behavior, an original Unreal 5.5 implementation pattern, and a measurable QA check. This is **not** FromSoftware source-code reverse engineering; hidden implementation details are called out. This is **not** a status audit of your own Unreal project.

## Executive summary

**Yes, a Mohg-inspired implementation is feasible.** It should not be treated as simply 82 independent features or a Morgott-like moveset with blood-colored effects. Mohg’s identity is a slow, far-reaching trident cadence combined with delayed spells, **persistent spatial hazards**, multiple distinct hit timelines, a scripted **three-mark / three-pulse Bloodboon Ritual**, and a Phase 2 that adds flight plus bloodflame residue to physical strikes. [S1] [S2] [S3] [S4]

**Crucial engineering difference:** The active boss attack, the spell impact, and the residual flame pool must have *separate ownership and lifetime*. A melee Montage might finish while its spawned fire continues to damage the player. Ritual pulses are ordered scripted events; they must not be selected by ordinary random attack AI.

### Evidence classifications — NOT completion statuses

| Code | Interpretation | Count |
| --- | --- | --- |
| O | Observable/documented encounter behavior | 13 |
| R | Community-described pattern | 8 |
| I | Plausible engineering inference | 22 |
| U | Hidden implementation unverified | 39 |

**Important:** `O` and `R` describe encounter observations, not proof of matching UE architecture. Checklist QA and lifecycle requirements describe *your intended engineering quality*, not features demonstrably present in the Elden Ring executable.

## Core encounter differences vs Morgott

| Dimension | Morgott reference | Mohg reference |
| --- | --- | --- |
| Boss offense | High variation in conjured weapon type and position-dependent mix-ups | Slow trident attacks plus spell patterns, hazard overlap and aerial extensions |
| Damage geography | Sword rain and curse eruptions reshape local danger | Bloodboon fans/showers and persistent flame patches control floor occupancy |
| Phases | Weapon set and curse changes over health bands | Three prior curse marks → 3 scripted Nihil pulses → sustained aerial/bloodflame phase |
| Counterplay | Recognize enders, dodge through mixed geometry, punish opening | Time delayed release, avoid lingering patch, use ritual protection and position carefully |
| Engine emphasis | Authored combo graphs and movement commitment | Independent hazard manager, ritual controller, damage/status policy and phase state |

## Mohg attack-family catalogue (15 authored design cards)

These are useful **engineering groupings**, not a claim that Elden Ring has exactly 15 internal attack records. Every card has timing, hitbox coordinates, and numeric damage marked TBD; measure and author in your own assets.

| ID | Attack family | Phase | Damage geometry | Counterplay |
| --- | --- | --- | --- | --- |
| M01 | Trident wide horizontal sweep | P1 + P2 | Moving swept polearm volume | Sidestep or dodge through actual release; do not dodge on lift alone |
| M02 | Trident overhead smash | P1 + P2 | Vertical swept blade + localized impact | Leave landing line; punish committed ender when clean |
| M03 | Trident forward thrust | P1 + P2 | Narrow capsule swept forward | Lateral dodge near release; punish missed recovery |
| M04 | Bloodflame Talons | P1 + P2 | Hand-sweep cue plus delayed front explosion | Respect delayed burst, do not rush apparent end |
| M05 | Bloodboon narrow throw | P1 + P2 | Target-directed projectile / narrow fan plus pool | Move laterally and avoid landing fire |
| M06 | Bloodboon wide arc | P1 + P2 | Broad spray/fan with individual landings | Cross safe path through fan, then avoid residue |
| M07 | Bloodboon overhead shower | P1 + P2 | Overhead lob/pattern leaving nearby burning areas | Leave local shower or circle to back if safe |
| M08 | Bloodflame hand explosion | P1 + P2 | Local delayed frontal burst | Wait for explosion, then use recovery |
| M09 | Ritual mark countdown | P1 scripted | Target-bound mark, no direct initial damage | Recognize 3 stages; punish cast where safe |
| M10 | Nihil ritual: three pulses | Transition scripted | Three scheduled curse damage pulses + boss heal | Use appropriate mitigation; transition recovery |
| M11 | Phase-two trident bloodflame swing | P2 | Blade sweep followed by residual fire trail | Dodge direct weapon then reposition off fire |
| M12 | Phase-two bloodflame charge | P2 | Moving thrust/line plus ground residue | Dodge sideways and avoid trailing fire |
| M13 | Phase-two flying blood throw + dive | P2 | Airborne projectile fan then dive swept blade | Read wing posture and double-stage dodge |
| M14 | Phase-two winged trident slam | P2 | Aerial impact and explosion | Avoid impact and secondary blast |
| M15 | Phase-two trident ground detonation | P2 | Point impact + delayed AOE plus residue | Exit secondary radius rather than punishing inside flame |

## Original technical diagrams

**UE runtime components and separation of attack, hazard and ritual ownership.**

![UE runtime components and separation of attack, hazard and ritual ownership.](diagrams/01_ue_architecture.png)

**The legal gate and special-ritual priority used before scoring combat moves.**

![The legal gate and special-ritual priority used before scoring combat moves.](diagrams/02_decision_tree.png)

**Conditional trident and Talons follow-ups; delayed blast independent of combo path.**

![Conditional trident and Talons follow-ups; delayed blast independent of combo path.](diagrams/03_attack_combo_graph.png)

**Ordered three-mark / three-pulse transition; engineering sequence diagram.**

![Ordered three-mark / three-pulse transition; engineering sequence diagram.](diagrams/04_ritual_state_machine.png)

**Top-down damage families: trident, Talons, Bloodboon, ground fire and targeted Nihil.**

![Top-down damage families: trident, Talons, Bloodboon, ground fire and targeted Nihil.](diagrams/05_hit_geometry.png)

**Illustrative attack durations; NOT measured Mohg animation frames.**

![Illustrative attack durations; NOT measured Mohg animation frames.](diagrams/06_attack_timelines.png)

**Separated collision/temporary damage from persistent hazard lifetime.**

![Separated collision/temporary damage from persistent hazard lifetime.](diagrams/07_attack_hazard_ownership.png)

## The 82 requirement-by-requirement mappings

For each requirement: **Reference** is observed/reported Mohg behavior (or an explicit uncertainty), **Unreal** is a proposed way to implement a comparable mechanic, and **Acceptance** is a reproducible test. `R/I/U` do not mean the mechanic is missing from Mohg.

### Awareness and observable context

#### BOSS-AWR-001 — Target validity · Evidence I

**Original checklist requirement:** Every decision rejects dead, destroyed, invalid, out-of-arena or otherwise non-targetable actors.

**Mohg reference:** Mohg maintains an encounter target, but private invalid-target/leash logic is not documented. His arena contains obstructions and encounter boundaries. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Define target validity: alive, targetable, within arena/leash, not destruction-pending; validate at neutral, combo, cast and ritual gates. Guard locked-on curse target against despawn.

**Verification / acceptance:** Despawn/kill target during trident wind-up, Bloodboon cast and first Nihil pulse; no crash or orphaned curses.

#### BOSS-AWR-002 — Gate-time snapshot · Evidence U

**Original checklist requirement:** A timestamped combat context is rebuilt atomically at every neutral, combo or reaction gate.

**Mohg reference:** Mohg changes behavior with range and phase, but publicly available combat guides do not reveal his decision snapshot representation. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Capture immutable FCombatContext on each authorized gate: signed yaw, distance, verticality, LOS, action tags, phase, curse marks, hazard occupancy, timestamp.

**Verification / acceptance:** Show context ID at each select/branch; move player behind during a talon explosion and prove the next gate samples new location.

#### BOSS-AWR-003 — Distance convention · Evidence I

**Original checklist requirement:** Each attack declares whether range means root, capsule-surface or attack-origin distance.

**Mohg reference:** Trident sweeps have broad physical reach; hand-cast talons and bloodboon use different attack origins. Actual internal distance convention is unknown. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** MoveCard specifies root/capsule edge/weapon socket as distance origin; selector and contact validator agree about measurement.

**Verification / acceptance:** Test at 1.5m, 3m and sweep tip edge using different player capsule radii; no visually impossible legal attacks.

#### BOSS-AWR-004 — Signed angle and hysteresis · Evidence R

**Original checklist requirement:** Relative yaw is planar, boss-facing and stable near sector boundaries.

**Mohg reference:** Close frontal positions invite talons and trident exchanges; the shower variant of Bloodboon is associated with proximity. Exact angle sectors are unknown. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Calculate signed planar yaw with front/side/back hysteresis; allow Bloodboon variants and follow-ups to use sector constraints but never force tracking after commitment.

**Verification / acceptance:** Orbit at front/side boundary during a delayed trident swing; gate selection is stable and collision can miss.

#### BOSS-AWR-005 — Vertical separation · Evidence U

**Original checklist requirement:** Melee and ground actions enforce a documented Z tolerance.

**Mohg reference:** Winged attacks involve altitude changes, but exact internal height tolerances for ground strikes are not known. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Specify Z tolerances for sweeps, narrow thrown arcs and ground pools; flight attacks declare airborne origin and landing height limits.

**Verification / acceptance:** Move player onto a raised platform: ground fire must not damage a target far above it, while valid air attacks can acquire targets.

#### BOSS-AWR-006 — Observable player activity · Evidence I

**Original checklist requirement:** Reactions use public committed action state, not raw future input.

**Mohg reference:** Bloodboon ranged pressure and close punishes interact with what a player is doing; no credible source proves an exact heal-input-reading rule for Mohg. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Consume publicly observable player action tags only after animation commitment; reactions include LOS, range, delay, travel feasibility and executor-free gates.

**Verification / acceptance:** Heal/cast while Mohg is locked in trident release; he must not interrupt committed attack for an impossible instant response.

#### BOSS-AWR-007 — LOS and memory · Evidence U

**Original checklist requirement:** Precision reactions require current LOS; lost targets use timestamped last-seen state and reacquire.

**Mohg reference:** The mausoleum arena has gravestones and clear open sections; exact occlusion memory and target search rules are not published. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Make Bloodboon throws LOS-aware, store last seen target with age, and use reacquire behavior when target hides behind cover.

**Verification / acceptance:** Place solid obstacle between boss and player, verify ranged action eligibility and search fallback.

#### BOSS-AWR-008 — Soft adaptation memory · Evidence U

**Original checklist requirement:** Pattern features decay, are capped and bias rather than force choices.

**Mohg reference:** Mohg visibly creates positional pressure using lingering bloodflame, but adaptation to repeated player behavior is not demonstrated as a private memory algorithm. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Optional recent-action memory should bias attack-family selection while decaying; record repeated kiting or fire-patch avoidance without guaranteeing cheating counters.

**Verification / acceptance:** Script repeated backward rolls then lateral movement; log bounded adaptive weights and decay.

### Eligibility, utility and selection

#### BOSS-SEL-001 — Legal decision gates · Evidence I

**Original checklist requirement:** Full attack selection runs only in neutral or an explicitly authorized gate.

**Mohg reference:** Trident sequences finish with recoveries or optional continuations; ritual countdown/transition take over at special event gates. Internal AI schedule is unknown. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Select only at neutral, authored combo gates, reactive slots or threshold events; lock executor during active trident damage and each Nihil pulse.

**Verification / acceptance:** Spam player direction changes during active swipe; selection remains locked until a legal gate.

#### BOSS-SEL-002 — Hard-filter precedence · Evidence R

**Original checklist requirement:** Phase, state, range, angle, LOS, cooldown, resource, asset and path constraints reject before scoring.

**Mohg reference:** Close Talons, medium trident strikes, distant bloodboon throws and phase-two flight attacks have different practical ranges and phases. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Filter attack pool by phase, current curse state, range, angle, verticality, cooldown, hazard saturation and available montage before scoring.

**Verification / acceptance:** Enumerate eligible/rejected moves in near/mid/far and P1/P2 contexts; P2 flight cannot appear before wings.

#### BOSS-SEL-003 — Executable asset gate · Evidence U

**Original checklist requirement:** A move with a missing montage/socket/required resource is never selected.

**Mohg reference:** No public source shows Mohg’s ability/asset validation. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Prevalidate UAnimMontage, GameplayTag, effect blueprint, socket names, Niagara/Audio and hazard data; skip missing resources before commit.

**Verification / acceptance:** Break a trident montage reference in test profile and confirm safe fallback without draining cooldown.

#### BOSS-SEL-004 — Normalized utility · Evidence U

**Original checklist requirement:** Eligible moves receive comparable documented range, angle, opportunity, spacing, phase and variety terms.

**Mohg reference:** Mohg has diverse legal actions but no public evidence reveals utility weights, Behavior Tree topology or random draw algorithm. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Implement optional utility scoring for reach, player commitment, safe flame area, recent attacks, hazard density and phase intent. Distinguish hard eligibility from soft preference.

**Verification / acceptance:** Capture score table at each decision; compare narrow vs wide Bloodboon when player moves to the flank.

#### BOSS-SEL-005 — Bounded randomness · Evidence U

**Original checklist requirement:** Variation is limited to near-best candidates, with deterministic seeded RNG.

**Mohg reference:** Observed variation does not establish seeded randomness. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Choose weighted candidate from legal near-best options using seeded FRandomStream; preserve determinism for tests, allow authored special moves to override selection.

**Verification / acceptance:** Repeat same seed and player script 20 times; match committed move IDs and special-event ordering.

#### BOSS-SEL-006 — Cooldown semantics · Evidence U

**Original checklist requirement:** Cooldown commits on an attack start, not on rejected or failed choice attempts.

**Mohg reference:** Move-specific cooldown durations for Mohg are not reliably published. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Start cooldown only on confirmed attack commit; separate cooldown class for area hazard throws and winged entries to avoid spam.

**Verification / acceptance:** Force montage-start failure; cooldown remains available, but a successful Bloodboon cast consumes its own cooldown.

#### BOSS-SEL-007 — Anti-repeat memory · Evidence U

**Original checklist requirement:** Recent move and family repetition lower preference with time decay; hard spacing may protect signature moves.

**Mohg reference:** Slow trident combos and Bloodboon variants create variety, but no public evidence proves hidden anti-repeat history. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Keep short MoveFamilyHistory with recency penalties; exempt ritual, while limiting repetitive talons or identical puddle throws.

**Verification / acceptance:** Measure selection histograms from 1000 seeded decisions without violating legal phases.

#### BOSS-SEL-008 — No-candidate fallback · Evidence I

**Original checklist requirement:** Empty eligible sets choose purposeful wait, reorientation, approach/retreat, EQS positioning or reset.

**Mohg reference:** Mohg can pause, approach and reposition rather than execute nonstop attacks, especially as distant spells change spacing. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** When no move is legal, choose timed face/approach/strife/recenter/reacquire; factor current fire patches so movement does not intentionally self-block.

**Verification / acceptance:** Disable all eligible attacks; boss remains functional and does not spin or hang.

#### BOSS-SEL-009 — Reaction latency and budget · Evidence U

**Original checklist requirement:** Defensive/heal reactions require nonzero latency, cooldown/budget and ordinary feasibility.

**Mohg reference:** Public guides discuss responding to player positions rather than publishing an exact reaction latency. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Require a configured positive minimum reaction delay and executable action state before punish selection; priority events never steal committed hit windows.

**Verification / acceptance:** Try heal during talons, after recovery and at long range; inspect actual valid reaction samples.

#### BOSS-SEL-010 — Decision trace · Evidence U

**Original checklist requirement:** Each gate logs context, all candidate eligibility/reasons/scores, winner and RNG seed.

**Mohg reference:** FromSoftware attack-decision telemetry is not publicly available. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Log candidate scores, range, yaw, phase, cooldown, curse marks, hazard count, chosen MoveID, AttackInstanceID, seed and rejection cause.

**Verification / acceptance:** Reconstruct an apparent repeated-talon case from one structured trace, including rejected alternatives.

### Attack executor and state safety

#### BOSS-EXE-001 — Single execution authority · Evidence U

**Original checklist requirement:** One executor owns current attack, instance, section, state, target snapshot and victim sets.

**Mohg reference:** Visible play presents one attack stream while multiple bloodflame pools remain damaging independently; no engine-level executor architecture is published. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Use one main BossAttackExecutor for current montage, with separate persistent HazardManager for detached pools; hazard damage may outlive owning attack without prolonging its active window.

**Verification / acceptance:** Finish Bloodboon and start a new trident swing while a pool remains; neither contaminates the other attack ID.

#### BOSS-EXE-002 — Instance before montage · Evidence U

**Original checklist requirement:** A unique ID and wind-up state are set before montage playback.

**Mohg reference:** Mohg’s internal instance identity is not observable. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Allocate FAttackInstanceId and commit state before Montage_Play; subevents carry unique ActionPulseID, TalonExplosionID or HazardID linked to parent attack.

**Verification / acceptance:** Immediate first-frame Notify and interrupted re-entry must never report unknown/previous attack.

#### BOSS-EXE-003 — Start rollback · Evidence U

**Original checklist requirement:** Montage play failure restores neutral/movement and does not consume a live attack.

**Mohg reference:** Startup rollback is engine-internal and not visible from encounter guides. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** If montage/ability does not start, restore locomotion, pending warp, target lock, temporary armor and cooldown reservation; do not leave curse/mana side-effects.

**Verification / acceptance:** Supply invalid Montage or blocked ability activation; boss returns neutral without leaked VFX or cooldown.

#### BOSS-EXE-004 — Stale event rejection · Evidence U

**Original checklist requirement:** Notify/callback instance, montage, section and expected state are validated.

**Mohg reference:** No public evidence confirms Mohg’s stale Notify filtering. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Reject callbacks whose instance/section/state mismatches; detached hazards maintain their own explicit lifetime independent of aborted boss attacks.

**Verification / acceptance:** Interrupt Talons before delayed explosion: use authored cancel policy, ensure no leaked callback or unexpected post-cancel blast.

#### BOSS-EXE-005 — Explicit priority · Evidence I

**Original checklist requirement:** Death, phase, stance, special, combo and completion conflicts follow a documented order.

**Mohg reference:** The ritual transition supersedes ordinary offense and stance-broken behavior; exact priority order is not disclosed. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Write priority table: Death > hard reset > legal protected ritual > stance break > attack interruption > authored combo gate > neutral selection. Decide explicit ritual defer/interrupt rule.

**Verification / acceptance:** Cross 50% during hit, death, stance break and shackle state; one deterministic legal outcome each time.

#### BOSS-EXE-006 — Idempotent abort · Evidence U

**Original checklist requirement:** Abort closes collision, warping, gates, armor and latent work, then restores motion once.

**Mohg reference:** The game resolves encounter end without permanent attack state, but internal abort logic is hidden. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Idempotent AbortAttack shuts melee hit windows, tracking, root-motion authority, warp, timers and active channels; environmental pools follow their declared persistence/removal policy.

**Verification / acceptance:** Interrupt/death/reset at every notify boundary; control and tracking restore exactly once.

#### BOSS-EXE-007 — Watchdog · Evidence U

**Original checklist requirement:** Every live attack has maximum expected duration plus margin and a safe timeout path.

**Mohg reference:** No publicly verified watchdog bound exists for Mohg. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Every montage and RitualController state has max duration plus fail-safe; watchdog releases stuck three-pulse transition without skipping its safety cleanup.

**Verification / acceptance:** Remove a pulse complete Notify in dev asset and inject hitch; encounter recovers or fails to safe state with diagnostic.

#### BOSS-EXE-008 — Cleanup-before-unlock · Evidence U

**Original checklist requirement:** Trace and temporary state are closed before any next selection can occur.

**Mohg reference:** Mohg’s cleanup order is not public. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Close contact traces and combo gates before unlocking next action; detach persistent hazard actors explicitly, never leave owning temporary trace enabled.

**Verification / acceptance:** Perform successive trident attacks inside active puddles; no previous weapon contact carries into the next move.

### Conditional combos

#### BOSS-COM-001 — Authored graph · Evidence R

**Original checklist requirement:** Combo nodes and allowed outgoing edges are data-authored, not arbitrary full-pool selections.

**Mohg reference:** The trident uses 2–3-hit strings that can end as a further sweep, thrust or overhead slam; Talons can precede melee follow-ups. Exact edge probabilities are unknown. [S2] [S3]

**Unreal Engine 5.5 / 5.5.4:** Build authored adjacency graph: TridentSwing1 -> Swing2 / Slam / End; Talons -> TridentFollowUp / End; WingThrow -> Dive / End. Each edge has constraints.

**Verification / acceptance:** Dump legal graph and play selected branches; no full-pool arbitrary jump directly out of active swing.

#### BOSS-COM-002 — Gate after damage · Evidence I

**Original checklist requirement:** A branch gate occurs only at its authored time, normally after the prior hit window closes.

**Mohg reference:** Talons has a delayed explosion and optional following attacks; the decision point must not make the attack unreadably overlap, though its private frame data are unknown. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Branch after relevant damage/hazard spawn gate and only when legal; decide if Talons delayed burst owns its own timer so a trident follow-up does not cancel it accidentally.

**Verification / acceptance:** Inspect montage timeline and player captures; next attack cannot begin during prohibited active interval.

#### BOSS-COM-003 — Fresh branch context · Evidence R

**Original checklist requirement:** The gate evaluates current target state, not only the first move's snapshot.

**Mohg reference:** Player position after the first trident swing changes safe responses to the possible follow-up; phase-two aerial follow-ups can reposition after the throw. [S2] [S3]

**Unreal Engine 5.5 / 5.5.4:** Refresh context at authored combo gates instead of selecting whole sequence at start; update yaw/range, player roll recovery and landing zone hazard.

**Verification / acceptance:** Move from front to side after Swing1, inspect gate snapshot and chosen follow-up eligibility.

#### BOSS-COM-004 — Explicit hit-confirm policy · Evidence U

**Original checklist requirement:** Each edge states whether contact, damage, guard or whiff is required.

**Mohg reference:** Guides document different combo endings but do not establish whether branching depends on hit, block or whiff. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Each combo edge explicitly declares any hit confirm, guard, miss or range requirement; avoid inventing confirmed Mohg hit-confirm internals.

**Verification / acceptance:** Script hit/whiff/block on same opener, compare resulting legal branches to your authored policy.

#### BOSS-COM-005 — Single-use gate · Evidence U

**Original checklist requirement:** A gate is consumed once per matching instance.

**Mohg reference:** Single-use internal branch handles are not publicly known. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Consume each ComboGateID once per AttackInstanceID, with atomic next-action reservation; duplicated Notifies cannot spawn two trident follow-ups.

**Verification / acceptance:** Double-fire branch event; exactly one child attack commits.

#### BOSS-COM-006 — Finite pressure · Evidence I

**Original checklist requirement:** Combo depth, edge use/cooldown and maximum pressure duration enforce eventual recovery.

**Mohg reference:** Mohg’s trident strings appear bounded, leaving some identifiable finishes before new neutral choices. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Max combo depth/pressure budget; prioritize an explicit Recovery on terminal slam or aborted branch; no unbounded Talons->Swipe loop.

**Verification / acceptance:** Force chaseable player near range continuously; longest combo and total active pressure remain within authored cap.

#### BOSS-COM-007 — Default recovery · Evidence U

**Original checklist requirement:** A missing/invalid target, edge or montage routes to declared recovery.

**Mohg reference:** Exact error-recovery behavior for Mohg’s unavailable follow-ups is not published. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** When player is out of range, dead, invalid or required montage missing at branch, go to specified recovery rather than instant neutral or freeze.

**Verification / acceptance:** Despawn player at branch gate; recover safely with a measurable terminal window.

### Animation, tracking and motion

#### BOSS-ANM-001 — Montage timeline authority · Evidence I

**Original checklist requirement:** Commit, active, gate, armor and recovery derive from montage events/position rather than duplicate delays.

**Mohg reference:** Mohg’s delayed trident release, delayed talon explosion, and distinct triple Nihil thrusts are visibly timing-critical, but exact event source data are private. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Author animation sections and NotifyState windows for tracking/active blade/recovery; schedule talon explosion and each ritual pulse with event-time offsets tied to a single move clock.

**Verification / acceptance:** Capture montage position against damage and explosion event timestamps; mismatches are within chosen tolerance.

#### BOSS-ANM-002 — Telegraph phases · Evidence O

**Original checklist requirement:** Pose/direction/release cues precede damage and identify geometry.

**Mohg reference:** The raised trident, hand claw gesture, airborne posture and red ring curse are distinctive telegraphs for different collision families. [S1] [S2] [S3]

**Unreal Engine 5.5 / 5.5.4:** Give separate pose, sound and VFX release cues for stab, broad sweep, talon delayed detonation, ground pool and Nihil pulse.

**Verification / acceptance:** Blind footage tests distinguish immediate blade hit from delayed fire and arena curse.

#### BOSS-ANM-003 — Bounded holds · Evidence O

**Original checklist requirement:** Variable delay has declared min/max and is chosen before commitment with a reliable release cue.

**Mohg reference:** Mohg intentionally delays several trident releases and talon explosion relative to anticipation. No evidence proves randomized wind-up durations. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Record fixed authored holds; optional bounded variable holds only if your own design chooses them, selecting at start and preserving a readable final release cue.

**Verification / acceptance:** At 30/60/120 FPS verify release cue precedes hit and fixed test holds have consistent timing.

#### BOSS-ANM-004 — Staged rotation cap · Evidence I

**Original checklist requirement:** Early/late/active/recovery stages enforce per-move turn limits.

**Mohg reference:** Long trident windups can track target early; once he strikes, players can roll to the side. Exact rotation caps are not publicly verified. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Per-MoveCard yaw speed by stage: face early, slow late, lock at release; keep winged dive tracking commitment separate.

**Verification / acceptance:** Dash around boss during final 0.3s of charge and measure yaw drift after commitment.

#### BOSS-ANM-005 — Exclusive motion authority · Evidence U

**Original checklist requirement:** Navigation/manual movement stops while root-motion/warp attack owns motion.

**Mohg reference:** Mohg’s grounded trident lunges and phase-two flights demonstrate large authored displacement; ownership between path following and animation is unknown. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** At committed root-motion attack acquire exclusive movement authority, suspend NavMoveTo and manage exit transitions including death.

**Verification / acceptance:** Start MoveTo then immediately dive; path following does not fight root motion or snap boss.

#### BOSS-ANM-006 — Bounded Motion Warping · Evidence U

**Original checklist requirement:** Warp target updates only in an authorized early window and obeys translation/rotation/Z/path caps.

**Mohg reference:** No public proof identifies motion-warping algorithms used by Mohg. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** If using UE Motion Warping, capture bounded target before commit, forbid teleport-sized corrections or mid-active warps; handle bad arena edge destination.

**Verification / acceptance:** Player sprints behind during aerial descent; warp remains limited, readable and wall-safe.

#### BOSS-ANM-007 — Notify-end independence · Evidence U

**Original checklist requirement:** Blend-out, interruption and watchdog all close any window even if Notify End is skipped.

**Mohg reference:** Missed NotifyEnd behavior and montage blend-out handling cannot be inferred from fighting Mohg. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Use executor-managed cleanup on blend-out, interruption, death, phase override and timeout, not NotifyEnd alone; hazard lifespan independently tracked.

**Verification / acceptance:** Inject frame hitch and kill during weapon trace; no orphaned collision or pooled effect.

#### BOSS-ANM-008 — MoveCard handoff · Evidence I

**Original checklist requirement:** Every move records axes, scale/FPS, timing, displacement, sockets, warp, cues, cancels and branches.

**Mohg reference:** Mohg’s trident/hand/wing distinctions require different authored motion and hit geometry. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Each MoveCard records clip source FPS, scale, timecode, weapon socket paths, tracking/commit, phase, spawned hazards, pulse markers and authorized follow-ups.

**Verification / acceptance:** Review 12 authored MoveCards against actual Montage tracks and weapon render path.

### Hit detection and damage

#### BOSS-HIT-001 — Geometry fidelity · Evidence O

**Original checklist requirement:** Collision family and volume match the visible thrust, sweep, slam, ring, lane or grab.

**Mohg reference:** Trident sweeps are moving arcs, Talons is a delayed frontal burst, bloodboon leaves burning patches, and Nihil is a player-mark curse pulse. They do not share one spherical hitbox. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Separate SwordTrace/SweptSegment, targeted cast projectile or lobbed arc, delayed TalonVolume, PoolArea DOT, winged dive impact and targeted RitualPulse; no generic always-on AOE.

**Verification / acceptance:** Compare debug shape for each move with footage and expected legal dodge paths.

#### BOSS-HIT-002 — Swept temporal sampling · Evidence I

**Original checklist requirement:** Weapon samples sweep previous-to-current positions during active windows.

**Mohg reference:** Long, fast trident arcs are able to catch players across their spatial sweep. Exact collision sampling algorithm is unknown. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** On active NotifyState, sample previous/current weapon sockets and sweep capsule segments between them (query-only); no sword traces outside active stages.

**Verification / acceptance:** At 30 FPS and hitch, thin character crossed by tip still receives a single valid hit.

#### BOSS-HIT-003 — Blade interior samples · Evidence I

**Original checklist requirement:** Long rotating weapons sample multiple points, not endpoints only.

**Mohg reference:** A trident is long and wide; tip-only or origin-only traces would miss blade interior contact. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Use multiple sampled points along shaft and prongs (base/middle/tip), with logical actor dedupe and geometry-dependent blade section mask.

**Verification / acceptance:** Cross long weapon at middle in a controlled scene; hit once, not zero or three times.

#### BOSS-HIT-004 — Adaptive substeps · Evidence U

**Original checklist requirement:** Excessive sample translation/angular delta creates bounded substeps.

**Mohg reference:** Sampling frequency and collision substeps in Elden Ring cannot be verified externally. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Bounded substep interpolation when weapon movement exceeds configured world-space or angular threshold; cap trace cost per frame.

**Verification / acceptance:** Induce 120ms hitch during sweep and winged slash; compare hits to normal frame-rate path.

#### BOSS-HIT-005 — Query filtering · Evidence U

**Original checklist requirement:** Traces ignore owner/allies and use query-only channels with valid target/team checks.

**Mohg reference:** Exact collision channel filtering for Mohg is hidden. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Use dedicated combat query channels; ignore attacker, self-components, team members; trace supports cover and player target validity.

**Verification / acceptance:** Stand behind tomb obstacle, summon allied dummy and overlap boss weapon; no false damage.

#### BOSS-HIT-006 — Logical-victim dedupe · Evidence U

**Original checklist requirement:** Multiple components/bones of one actor count once according to hit policy.

**Mohg reference:** A player hit by the trident is not visibly damaged once per socket, but victim dedupe implementation is unknown. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** HitLedger keyed by ActorID + AttackInstanceID + HitWindowID; do not count multiple body components or overlapping prongs as multiple strikes.

**Verification / acceptance:** Overlap player capsule and 3 hit bones in same sweep; one direct strike resolves.

#### BOSS-HIT-007 — Explicit hit policy · Evidence O

**Original checklist requirement:** Once-per-attack, once-per-window, periodic and impact-plus-splash policies behave distinctly.

**Mohg reference:** Mohg combines direct weapon contact, repeated ritual pulses, delayed Talon burst, and persistent bloodflame damage over time. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Declare explicit OncePerWindow (blade), ScheduledThreePulses (Nihil), DelayedOnce (Talons), PeriodicDOT with tick interval (ground pool), ImpactPlusResidue (bloodflame weapon) policies.

**Verification / acceptance:** Record a complete phase-two combo; hit counts match distinct timing policies rather than accidental frame count.

#### BOSS-HIT-008 — Central defense order · Evidence I

**Original checklist requirement:** Validity/dedupe, iframe, parry, guard, posture/armor, health and feedback resolve in one documented order.

**Mohg reference:** Attacks can deal physical/fire damage and blood-loss buildup; status, health, guard and dodge effects have distinct gameplay results. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Central hit resolution order: target validity/ledger -> i-frame/guard -> damage type resistance -> HP/posture -> blood-loss buildup -> feedback; status proc has cooldown/threshold policy.

**Verification / acceptance:** For sweep, fire pool and Nihil, compare unguarded, iframe, resistant and protected-ritual targets.

#### BOSS-HIT-009 — Iframe completeness · Evidence I

**Original checklist requirement:** An invulnerable contact applies neither unintended health nor posture effects.

**Mohg reference:** Dodging is used to evade most weapon and explosion attacks, but periodic pools and scripted ritual require their own explicit mitigation rules. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Define iframe immunity for ordinary contact windows; explicitly specify whether persistent pools tick through roll state and mark Nihil as a special scripted curse with dedicated protection mechanic.

**Verification / acceptance:** Roll through blade and Talons, stand in pool while rolling, and use ritual protection; outcomes obey authored policy.

#### BOSS-HIT-010 — Direct/splash precedence · Evidence O

**Original checklist requirement:** Direct and AoE overlap cannot double-dip unless the data explicitly permits it.

**Mohg reference:** Phase-two trident impacts can create separate explosions or residual flames. Player may overlap direct weapon hit and subsequent environmental danger. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Use DirectHit and DelayedExplosion separate damage groups with explicit simultaneous dedupe rules and independent active times; retain separate hazard ID for later DOT.

**Verification / acceptance:** Stand at impact center and then in residual patch; only intended immediate and periodic hits occur.

#### BOSS-HIT-011 — Swept annulus · Evidence U

**Original checklist requirement:** Radial waves test the previous-to-current radius band and damage each victim once.

**Mohg reference:** Mohg does not have a documented continuously expanding annular shockwave as a signature move; his main persistent threats are Bloodboon patches and burst effects. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Do not falsely model Mohg’s bloodflame as a swept annulus. Retain annulus implementation in your generic boss toolkit only for an authored expanding-ring move, or mark Mohg-specific applicability N/A.

**Verification / acceptance:** Inspect Mohg attack mapping: all AoE volumes use correct shower, fan, impact or pool shape; annulus test remains generic.

#### BOSS-HIT-012 — Grab fail-safe · Evidence U

**Original checklist requirement:** Grab capture, defense, alignment, control lock, damage and release are explicit and restore on interrupt/death.

**Mohg reference:** The documented Mohg, Lord of Blood moveset centers on strikes, casts, flight and ritual; a player-capture grab is not established as a defining move. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Do not add a grab just to check a box. If the existing boss has a grab, maintain explicit start/capture/damage/release and abort safety, but mark Mohg-specific reference as not demonstrated.

**Verification / acceptance:** If no grab is authored, record N/A with rationale; if retained in your own boss, interrupt/die mid-grab and restore player control.

### Movement and arena

#### BOSS-MOV-001 — Range-band policy · Evidence R

**Original checklist requirement:** Close, ideal, approach and reacquire bands produce distinct movement/action preferences.

**Mohg reference:** The boss can use trident reach at midrange, Talons close, throws at range and winged movement in Phase 2. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Author near/mid/far bands and preferred distance with separate P1 grounded / P2 aerial policies; avoid fixed chase-to-zero-range.

**Verification / acceptance:** Place target at distances 2/5/10m and log movement/attack decisions in both phases.

#### BOSS-MOV-002 — Combat positioning · Evidence I

**Original checklist requirement:** Candidate positions score reachability, distance, LOS, wall/hazard clearance, flank and variety.

**Mohg reference:** Phase-two puddles constrain safe footwork; flying attacks let Mohg reposition over dangerous floor. Exact sampled waypoint algorithm is unknown. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Score nav destinations by reachability, range, arena walls, line-of-sight, safe landing area, player approach corridor and active hazards; treat flames as player hazards, not permanent NavMesh walls.

**Verification / acceptance:** Spawn many flame pools and force reposition; boss does not corner player with unavoidable overlapping damage.

#### BOSS-MOV-003 — Movement commitment · Evidence U

**Original checklist requirement:** Strafe/approach choices have minimum duration and are not restarted every frame.

**Mohg reference:** Mohg visibly commits to several steps/swing/flight trajectories, but movement hysteresis implementation is unpublished. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Minimum locomotion interval per approach/strafe/retreat action, with explicit stop conditions; transition authority to animation only when montage begins.

**Verification / acceptance:** Rapidly oscillate player distance; no pathfinding jitter or 60Hz replan spam.

#### BOSS-MOV-004 — Wall-safe attacks · Evidence I

**Original checklist requirement:** Root-motion/warp paths predict walls and use correction, fallback or decline.

**Mohg reference:** The wide arena has gravestones and boundaries that can interact with trident and winged charges. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Predict displacement and wall clearance for lunge/flight/dive; select shorter variant or reject when invalid; clamp warp target and avoid wall clip.

**Verification / acceptance:** Run charge/flight attacks from every perimeter quadrant near cover.

#### BOSS-MOV-005 — Arena-valid responses · Evidence U

**Original checklist requirement:** Unreachable/elevated/outside targets cause reposition, search, leash or reset.

**Mohg reference:** Internal behavior for unreachable/out-of-bounds players is not revealed. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Maintain arena-valid target/landing checks, safe reacquire, leash/reset and disconnected NavMesh handling for grounded actions.

**Verification / acceptance:** Teleport player beyond arena, up ledge or out of NavMesh: no attacks fired through walls and fight resets per design.

#### BOSS-MOV-006 — Arena/attack fit · Evidence O

**Original checklist requirement:** Escape requirements and camera visibility are valid from every legal arena position.

**Mohg reference:** Phase-two bloodflame can fill large floor areas, changing which dodge lanes remain available as new attacks arrive. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Enforce minimum safe-ground fraction, hazard lifetime/cap, landing-clearance radius and camera visibility when scheduling shower, charge and dive.

**Verification / acceptance:** Stress-spawn worst-case legal hazard combination at 8 arena locations; at least one counterplay route stays available.

### Pacing and punishability

#### BOSS-PAC-001 — Explicit attack segments · Evidence O

**Original checklist requirement:** Every move declares anticipation, hold, commit, active, follow-through, recovery and neutral boundaries as applicable.

**Mohg reference:** Trident attacks include prominent wind-up/slow hold, active strike and recovery; Talons has a visibly delayed blast. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Every MoveCard separates anticipate, hold, track-lock, commit, blade active, residual spawn, follow-up gate, recovery and neutral unlock; pulses have their own timeline.

**Verification / acceptance:** Export timing chart for all attack families with 30/60/120fps event logs.

#### BOSS-PAC-002 — Pressure variation · Evidence R

**Original checklist requirement:** Offense rises and falls; neutral/recovery periodically reset pressure.

**Mohg reference:** The fight alternates slow trident strings, blood throws, cast set-ups and later aggressive winged pressure; ground fire adds passive pressure between attacks. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Track active direct pressure and persistent hazard pressure separately; introduce offense budget, neutral intervals, phase-specific behavior and hazard saturation penalties.

**Verification / acceptance:** Graph 20 fight runs; demonstrate both high-pressure sequences and real no-threat opportunities.

#### BOSS-PAC-003 — Guaranteed openings · Evidence R

**Original checklist requirement:** Some high-commitment moves have unconditionally meaningful recovery.

**Mohg reference:** An overhead trident finisher and certain spell animations can offer attack opportunities, though safe return depends on flame left behind. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Mark true guaranteed recovery only when player at a declared position can land and exit without remaining in a blood pool.

**Verification / acceptance:** Test quick/heavy player attacks after overhead slam and after Bloodboon cast from left and rear positions.

#### BOSS-PAC-004 — Conditional opening cues · Evidence R

**Original checklist requirement:** Follow-up-capable recoveries reveal the gate/outcome consistently.

**Mohg reference:** Talons can precede a trident continuation, so the apparent end of the claw animation is not always the true punish window. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Expose continuation telegraph and do not cancel expected delayed blast when combo gate chooses a follow-up. Distinguish possible branch from terminal Recovery.

**Verification / acceptance:** During Talons, test player waiting/attacking at several ranges; identify an honest branch tell before follow-up.

#### BOSS-PAC-005 — Punish-margin calculation · Evidence I

**Original checklist requirement:** Opening classification includes travel, player startup and safety buffer, not montage recovery alone.

**Mohg reference:** A player who dodges a trident may still be in lingering bloodflame, reducing practical punish margin despite apparent boss recovery. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Measure usable opening = recovery remaining - approach - startup - safety, then discount duration spent crossing active hazard; classify by starting position and weapon.

**Verification / acceptance:** Compare fast and heavy punishes after trident slam in clean floor versus pool-covered floor.

#### BOSS-PAC-006 — Neutral is purposeful · Evidence I

**Original checklist requirement:** Non-attacking time may face, strafe, observe or reset without hidden damage pressure.

**Mohg reference:** Mohg may briefly face, close, reposition or use a ritual-countdown cast rather than relentless direct swings. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Neutral is a purposeful decision state; avoid background damage except separately tracked existing hazards with explicit expiry.

**Verification / acceptance:** Watch neutral AI as last hazard expires; no phantom weapon damage and no indefinite inert loop.

### Defense, posture and interruption

#### BOSS-DEF-001 — Separate health/reaction/posture · Evidence O

**Original checklist requirement:** Health, immediate flinch and posture accumulation have independent state and rules.

**Mohg reference:** Mohg can take ordinary health damage while also being staggered/stance-broken, and blood-loss interactions are separate from his attack states. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Separate boss health, immediate hit reaction, posture, status buildup and per-move interruption policy.

**Verification / acceptance:** Hit with small/large/posture attacks across cast and flight; verify independent state changes.

#### BOSS-DEF-002 — Posture regeneration · Evidence U

**Original checklist requirement:** Regeneration starts only after a documented quiet delay and rate, then resets correctly.

**Mohg reference:** The exact posture-regeneration timing/curve of the fight is not established by the selected public strategy sources. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Expose posture regen delay/rate; postpone recovery appropriately during sustained damage and reset cleanly on phase transition or encounter reset.

**Verification / acceptance:** Apply hit, wait multiple intervals, inspect posture trend and one-shot regen start.

#### BOSS-DEF-003 — Single stance break · Evidence O

**Original checklist requirement:** Threshold produces one break, closes current offense and exposes a bounded critical window.

**Mohg reference:** The fight permits stagger and critical opportunities, while Mohg’s Shackle can temporarily restrain him in the first phase. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Stance break closes attack and exposes bounded riposte state; shackle is separate capped, P1-only restraint with authored immunity rules and no player-control grab.

**Verification / acceptance:** Break stance during trident window; use shackle twice in P1 and once in P2; verify cap and transitions.

#### BOSS-DEF-004 — Windowed hyperarmor · Evidence I

**Original checklist requirement:** Interruption resistance exists only for named moves/windows; health/posture policy is explicit.

**Mohg reference:** Certain trident and ritual animations appear to continue through smaller incoming hits; precise hyperarmor windows are private. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Author named startup/active/ritual armor windows; distinguish interruption resistance from posture/health immunity and decide whether threshold event is deferred.

**Verification / acceptance:** Apply same stagger load at early windup, during active slash and during ritual pulse; record authorized interruptions.

#### BOSS-DEF-005 — Fair boss defense · Evidence U

**Original checklist requirement:** Boss block/parry/dodge has facing/timing, startup, cooldown, cost and recovery constraints.

**Mohg reference:** Mohg is not characteristically a shield-blocking or parrying duelist. Defensive power comes from spacing, body/weapon coverage, spells and pressure. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Treat direct boss block/parry AI as optional, not a Mohg requirement. If your design includes it, enforce facing, timing, startup, cooldown and recovery.

**Verification / acceptance:** Mark Mohg analog optional; any added defense is predictable and never instantaneous.

### Phases and anti-cheese reactions

#### BOSS-PHS-001 — Phase rule set · Evidence O

**Original checklist requirement:** A phase defines move pool, utility modifiers, combo cap, movement, pressure, recovery and presentation.

**Mohg reference:** The three curse-countdown marks precede a triple Nihil transition; after it Mohg gains wings, bloodflame-coated weapon trails, blood pools and airborne entries. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Use data-driven phase policy plus dedicated RitualController; P1 set tags for mark application, P2 add flying move pool and detaching bloodflame hazards rather than simply raising damage.

**Verification / acceptance:** At phase change, log new abilities and verify phase-two weapon contact spawns correctly attributed pools.

#### BOSS-PHS-002 — Safe transition policy · Evidence O

**Original checklist requirement:** Threshold queues/delegates interruption according to one declared policy; first version should defer to a safe gate.

**Mohg reference:** The approximately half-health transition is the scripted three-pulse ritual; countdown actions are introduced during earlier health decline. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Queue ordered three mark events and one transition, with non-reentrant RitualState machine. Explicit policy for burst DPS skipping thresholds, stagger, shackle and death.

**Verification / acceptance:** Drop HP from 100% to below threshold in one scripted hit; no duplicate/out-of-order marks and ritual has defined interrupt or skip behavior.

#### BOSS-PHS-003 — Phase monotonicity · Evidence I

**Original checklist requirement:** Healing and repeated threshold events do not oscillate or duplicate the transition.

**Mohg reference:** After the transition wings and bloodflame-enabled moves persist; healing from Nihil does not cause Mohg to revert to first phase. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Store monotonic phase flag and independently count applied marks and executed pulses; boss HP healing never rewinds ritual phase or rearms marks.

**Verification / acceptance:** Drive health below 50, finish pulses, heal above 50; no repeated count or second transformation.

#### BOSS-PHS-004 — Fair heal punish · Evidence U

**Original checklist requirement:** Heal reaction requires committed heal, latency, LOS, range, travel feasibility, cooldown and free executor.

**Mohg reference:** Specific reaction policy to healing is not established by supplied Mohg moveset evidence. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** If heal punishment is desired, permit only after visible player healing commitment, range/LOS/travel gates, cooldown and executor vacancy; do not make ritual pulses player-input reactions.

**Verification / acceptance:** Heal with/without LOS during P1 and P2, and mid-ritual; only authored eligible reactions occur.

#### BOSS-PHS-005 — Anti-cheese with counterplay · Evidence O

**Original checklist requirement:** Kiting, rear camping, guard, terrain and wall traps receive bounded readable responses or reset.

**Mohg reference:** Ranged Bloodboon counters kiting; flame residue limits repeated backward dodges; aerial moves can cross long distance, but all need readable escapes. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Use position-dependent but bounded counters, hazard-cap and visible flight tell; avoid target-following invisible pools or guaranteed roll-catches.

**Verification / acceptance:** Repeat kiting, rear camping and dodging backward; every counter has playable lateral/through-dodge response.

### Debugging, QA, presentation and optional networking

#### BOSS-QA-001 — Runtime overlay · Evidence U

**Original checklist requirement:** Debug view exposes phase/state/instance/context/attack/montage/tracking/window/gate/cooldown/pressure.

**Mohg reference:** Mohg’s fight does not publicly expose internal AI debug values. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Developer HUD displays target distance/angle, phase, marks 0..3, ritual pulse 0..3, attack ID, active weapon/hazard count, combo gate, cooldown and current hazard coverage.

**Verification / acceptance:** Match overlay with ground-truth actor/trace state over full transition.

#### BOSS-QA-002 — Structured event log · Evidence U

**Original checklist requirement:** Decisions, commits, windows, contacts, defenses, branches, interrupts and transitions use stable IDs/times.

**Mohg reference:** No public structured combat event stream exists for Mohg. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Log stable IDs for mark applied, countdown spoken, ritual start/pulse/protection/heal, bloodflame spawn/tick/expire, attack branches and interruption; include monotonic time.

**Verification / acceptance:** Reconstruct three pulse ritual and simultaneous blood pool from log without ambiguous event ownership.

#### BOSS-QA-003 — Reproducible scenarios · Evidence U

**Original checklist requirement:** Seed, starts, player script, time, phase and IDs are recorded.

**Mohg reference:** No publicly available reproducible seeded AI test suite is supplied with Mohg. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Seed local RNG, script player movement/healing, record initial marks/phase/hazard map and deterministic outcomes; archive version/config hashes.

**Verification / acceptance:** Replay phase transition in same seeded start twice; pulse and attack IDs match.

#### BOSS-QA-004 — FPS and time-scale parity · Evidence U

**Original checklist requirement:** 30/60/120 FPS and supported time scales do not change hit count, cleanup or legal decisions.

**Mohg reference:** Exact FromSoftware engine FPS and time-scale invariance cannot be established from guide footage. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** At 30/60/120 FPS and hitches, sweep temporal traces, schedule triple pulses against clock, hazard DOT accumulators and clean up.

**Verification / acceptance:** Compare hit and pulse counts across frame caps and 150ms hitch; no skipped third Nihil or duplicate pool ticks.

#### BOSS-QA-005 — Performance bounds · Evidence U

**Original checklist requirement:** Utility is gate-driven; traces run only while active with bounded samples; packaged frame cost is profiled.

**Mohg reference:** Actual CPU/GPU cost of Mohg’s decision logic and flame effects is not public. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Event-driven utility, bounded collision substeps, pooling of Niagara/hazard actors, capped active flame patch count, profiler markers by system; measure packaged fight.

**Verification / acceptance:** Run worst-case P2 flame saturation and winged combo with Unreal Insights; meet your project budget.

#### BOSS-QA-006 — Camera/readability · Evidence O

**Original checklist requirement:** Boss target point, camera collision and framing keep release cues/weapon threats visible.

**Mohg reference:** Winged and ground AoEs are large; camera framing can become harder near boss body and arena edges. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Use dedicated lock-on target, camera collision, upper-body visibility and ground danger projections for flying attacks and ritual; suppress excessive shakes.

**Verification / acceptance:** Capture all 8 arena compass points during winged dive, Bloodboon fan and triple ritual; main cue remains readable.

#### BOSS-QA-007 — Accessible feedback · Evidence I

**Original checklist requirement:** Shake/effect reduction and non-color-only audiovisual cues preserve attack distinctions.

**Mohg reference:** Telegraphs in the public fight rely heavily on red visual effects plus distinct motion/audio; game-level accessibility settings are not inferred. [S1] [S2]

**Unreal Engine 5.5 / 5.5.4:** Differentiate geometry by pose, sound rhythm and VFX shape, not red tint alone; optional motion/shake and flash reduction without removing warning.

**Verification / acceptance:** Run low effects, grayscale, no sound and shake-off tests; distinguish flying throw, talon explosion, ritual and puddle.

## Implementation model: concrete Unreal ownership pattern

The recommended design works as **modular additions to an existing framework**. If your current project uses a marketplace combat pack or GAS, adapt these responsibilities instead of replacing functional systems.

```text
ABossCharacter
  ├── AIController / BehaviorTree or StateTree (high-level neutral decisions)
  ├── UBossCombatContextComponent (target + hazard snapshot at gates)
  ├── UBossAttackSelectorComponent (hard filters / weighted choice)
  ├── UBossAttackExecutorComponent (single attack instance + montage)
  ├── UBossComboGraphComponent (allowed next attacks / gates)
  ├── UBossRitualComponent (3 marks -> 3 pulses -> phase 2)
  ├── UBossHazardManagerComponent (independent fire patch lifetimes + cap)
  ├── UBossHitResolverComponent (iframe/guard/status/poise/HP)
  ├── UBossPhaseComponent (monotonic flags and move pools)
  └── UBossCombatDebugComponent (IDs/log/overlay/seed replay)

UPrimaryDataAsset: DA_BossCombatProfile, DA_BossMoveCard[M01..M15],
DA_BossComboGraph, DA_BossRitualRules, DA_BloodflameHazardRules
AnimMontages / NotifyStates: Track / Commit / BladeActive / CastSpawn / ComboGate / Recovery
Actors: ABloodflamePoolActor, ABloodboonProjectileActor, ABossAttackCueActor (if necessary)
```

### Concrete class/API suggestions (pseudocode, not compiled UE source)

```cpp
// Adapt to your actual UE combat framework; this is an interface sketch, not drop-in code.
struct FAttackInstance { FGuid Id; FGameplayTag MoveTag; double StartSeconds; };
struct FBossCombatContext { TObjectPtr<AActor> Target; float Distance; float SignedYaw; bool bLOS; int32 Phase; uint8 Marks; int32 FirePatches; };

// BossAttackExecutor::TryStart
// 1. Validate context, move asset, montage/phase/cooldown and executor availability.
// 2. Reserve instance ID BEFORE playing montage; set state=Windup.
// 3. Montage_Play and validate success; rollback if invalid.
// 4. NotifyStates open/close hit windows and tracking/commit rules.
// 5. ComboGate reads fresh context and selects only from authored outgoing edges.
// 6. On End/Interrupt/Death/Reset close trace and restore movement.
// 7. Spawned fire is owned by HazardManager and follows separate lifetime rules.

// RitualController::TryScheduleMarkAtThreshold
// Mark ordinal is monotonic (0 -> 1 -> 2 -> 3). No duplicate casts.
// At legal phase-transition gate, execute Pulse(1), Pulse(2), Pulse(3).
// Each pulse: apply documented protection to target damage; apply boss heal independently.
// Finishing pulse 3 permanently sets Phase2, wings and P2 move pool.
// Interrupt policy (death/stance/shackle/invalid target) must be authored and tested.
```

### Attack data card fields

```json
{
  "MoveId": "M04_Talons",
  "AllowedPhaseTags": ["Phase1", "Phase2"],
  "RangeMinCm": "TBD",
  "RangeMaxCm": "TBD",
  "AngleSectorDeg": "TBD",
  "Montage": "TBD asset reference",
  "AnimationEvents": ["Telegraph", "TalonCast", "ExplosionSpawn", "ComboGate", "RecoveryEnd"],
  "TrackingLockEvent": "TBD",
  "Geometry": "FrontalClawWithDelayedExplosion",
  "DamagePolicy": "DelayedOncePerTarget",
  "DetonationDelay": "TBD from animation",
  "NextMoveIds": ["M01_TridentSweep", "Recovery"],
  "FireHazardPolicy": "OptionalSeparateLifetime",
  "Cooldown": "TBD",
  "AcceptanceTestId": "T03"
}
```

### Two separate concepts must never be conflated

**Animation / active hit window:** owned by current attack instance; e.g. trident shaft trace only while a specific Montage NotifyState is active.

**Detached persistent hazard:** its own object/ID, start time, expiry time, periodic damage and area shape. It can continue after the owning animation ends, and obeys separate cleanup policy for boss death, encounter reset and arena boundaries.

### Ritual and phase-transition special handling

The curse countdown should be a **scripted high-priority event queue**, not three random attacks that must happen to be chosen. The final ritual should fire one unique pulse event at each authored marker. Define protection as a *modifier to player damage*; boss healing is a separate operation. Use monotonic `MarkCount`, `RitualPulseIndex`, `bRitualComplete`, `PhaseIndex`; log all transitions. The original game triggers the ritual around mid-health, but exact threshold behavior under extreme burst damage and interrupts should be treated as a design decision for your implementation. [S1] [S2] [S4]

## Focused P0–P8 adoption roadmap

| Stage | Title | Concrete goal |
| --- | --- | --- |
| P0 | Establish baseline | Inspect current UE boss, phase markers, montage timing, cast hazards, actual damage and QA evidence. No changes. |
| P1 | Telegraph correctness | Create visible matching cues for delayed Talons, weapon sweeps, fire patch and ritual pulse; verify Shipping. |
| P2 | Event and identity safety | Attack IDs before montage, reliable pulse/Notify delivery, cancel and timeout cleanup. |
| P3 | Damage pipeline | Unify sword, fire DOT, projectile, blood loss, protections and ritual heal order. |
| P4 | Geometry and coverage | Trace trident shaft/prongs, position fan/shower pools and verify all move families are reachable. |
| P5 | Combo and recovery | Branch authored trident/Talons graph at correct windows; measure punish with hazardous floor. |
| P6 | AI and movement | Range/phase/hazard-aware weighted scoring, movement, winged positioning and fair reactions. |
| P7 | Ritual and pacing | Implement/count three marks, safe 3-pulse Nihil and monotonic P2 switch; tune hazard saturation and pressure. |
| P8 | Final validation | Packaged QA at 30/60/120 FPS, hitch injection, edge-case transitions, runtime captures and user gameplay sign-off. |

## Test catalogue

| Test | Scenario | Action | Expected outcome |
| --- | --- | --- | --- |
| T01 | Delayed trident | Player rolls at initial lift vs release | Only release-timed dodge succeeds; laterally escaped player avoids committed swing |
| T02 | Sweep tracking | Player crosses behind during last wind-up | After tracking lock, weapon does not snap 180 degrees |
| T03 | Talons double timeline | Dodge claw, immediately return to front | Explosion still triggers at authored time; not duplicated by follow-up |
| T04 | Combo termination | Escape range after first trident swing | Next edge invalidates and boss enters documented recovery |
| T05 | Bloodboon variants | Stand near, side and long distance | Legal fan/shower/throw selection matches spatial constraints |
| T06 | Fire patch persistence | Stand on residue after original attack ends | Only periodic pool DOT persists, not old melee trace |
| T07 | Hazard cap | Force repeated P2 bloodflame at arena edge | Dodgeable lane remains; old pools expire, no infinite fill |
| T08 | Three marks | Slowly lower HP through mark thresholds | Exactly 3 ordered marks, target VFX and matching log entries |
| T09 | Burst HP threshold | Drop HP sharply across multiple mark triggers | No skipped required countdown/state deadlock; documented fallback policy |
| T10 | Three Nihil pulses | Allow ritual with/without protection | Exactly 3 pulse events, unique IDs, boss healing independent of protection |
| T11 | Nihil interruption | Trigger stance break/death/reset during transition | Correct cancel/defer policy, no duplicate ritual, player controls survive |
| T12 | Healing monotonicity | Heal boss over 50% after ritual | P2 remains active; marks/pulses do not restart |
| T13 | Shackle restraint | Activate in P1 repeatedly then P2 | Bounded P1-only effect by authored count; no illegal P2 stun |
| T14 | Aerial throw + dive | Player changes position after projectile release | Dive tracks only allowed early period, never teleports through wall |
| T15 | Impact plus fire | Player touches both sword and resulting pool | Distinct direct/explosion/DOT policies, no duplicate same-window hit |
| T16 | Defense order | Use iframe, guard, fire protection and status resist | Health/poise/status outcomes follow authored matrix |
| T17 | 30/60/120 + hitch | Inject 150ms hitch on sweep and ritual | No missed pulses, duplicate damage, or orphan collision |
| T18 | Performance | Saturate max legal P2 flame patches in Shipping | Meet project CPU/GPU budget and maintain readable VFX |

## Misconceptions, evidence limits and implementation risks

- The 82-point checklist is a **quality specification**. It is not evidence that Elden Ring uses Utility AI, Unreal-style Animation Notifies, arbitrary instance GUIDs or a specific C++ component design.

- Do not copy Morgott’s prior project audit statuses into this Mohg guide. Those statuses evaluate your current UE boss and are not a completion metric for Mohg.

- Bloodboon ground fire is **not automatically an expanding annular shockwave**. Use explicit fan/cone, falling drops, trail, local burst and persistent pool shapes. `BOSS-HIT-011` remains a useful generic check but not a documented Mohg-specific move.

- Public move lists do not firmly document a Mohg-specific cinematic grab. `BOSS-HIT-012` may legitimately be marked *not applicable for this reference boss*, while still required by your own game if it includes grabs.

- The three marks and three Nihil pulses are encounter-established; exact animation-frame markers, private interrupt priority and underlying threshold scheduling are not.

- A Purifying Crystal Tear-like protection reduces ritual **player damage** but should not be implemented as canceling independent **boss healing**.

- Phase 2 is not just a speed multiplier; it changes **the geometry of the floor**, meaning a dodge can succeed against the blade yet leave the player standing in fire.

- All sample timing diagrams and Unreal pseudo interfaces are illustrations, not extracted FromSoftware values or ready-to-compile code.

- Many decisions about blood loss, stun, environmental persistence and counterplay must be authored to fit your original game rather than copying copyrighted animations, model assets, or exact presentation.


## References

- **[S1]** Eldenpedia (wiki.gg) — Mohg, Lord of Blood moveset, phase transition, arena, bloodflame. https://eldenring.wiki.gg/wiki/Mohg%2C_the_Omen

- **[S2]** Gamer Guides — Mohg, Lord of Blood attack families, 2–3-hit combos, explosion, winged phase and punish opportunities. https://www.gamerguides.com/elden-ring/guide/mohgwyn-palace/bosses/mohg-lord-of-blood-boss-guide

- **[S3]** EIP Gaming — phase-two ground flames, Talons variants, aerial delayed slam and practical counterplay. https://eip.gg/elden-ring/guides/how-to-beat-mohg-lord-of-blood/

- **[S4]** Windows Central — ritual mitigation, shackle use, winged attack distinctions and phase-two behavior. https://www.windowscentral.com/elden-ring-how-beat-mohg-lord-blood

- **[S5]** Original user-provided 83-point BossCombatReview checklist, minus BOSS-QA-008. Boss_83_Combat_Requirements_Audit.md


*All diagrams and engineering examples in this package are new conceptual illustrations; no game mesh, texture, animation or extracted code is embedded.*
