# Morgott, the Omen King — 82-Point Combat Engineering Reference

**Unreal Engine 5.5 / 5.5.4 • Evidence-led behavior study • Single-player boss • 30 October 2026**

> **Scope:** This report maps 82 requirements from the supplied 83-point boss audit checklist to Morgott’s visible/reported fight behavior and to a technically plausible Unreal implementation. `BOSS-QA-008` (multiplayer/network authority) is intentionally excluded. This is a design and reverse-observation guide, **not an extraction of FromSoftware source code**, and it is **not an audit status report on your own Unreal boss**.

## Executive summary

Morgott combines highly varied attack geometry, conditional follow-ups, strong positional pressure and rapidly changing fight tempo. His curved sword offers delayed committed strikes; conjured daggers check greedy proximity; spear throws and charges cover distance; hammer and spinning sword/hammer strings punish spacing mistakes; tail sweeps counter rear camping. Holy sword rain creates temporary lanes, and bloodflame attacks add lingering hazards and a true impaling grab. His range of choices is less important than how **player position at specific moments** changes which follow-up is threatening. [S1] [S2] [S4]

**Most transferable lesson:** do not implement 82 disconnected features. Build a coherent loop: observe player context → filter eligible moves → commit to a readable animation → deliver precisely timed geometry → evaluate legitimate follow-up conditions → expose measured recovery → reposition. Every branch is constrained by phase, animation authority, and counterplay.

### Evidence classification (not an implementation score)

| Marker | Meaning | Count |
|---|---|---:|
| **O** | Observable encounter mechanic | 12 |
| **R** | Documented community observation / pattern | 17 |
| **I** | Reasonable inference / engineering interpretation | 18 |
| **U** | Hidden internals not verified | 35 |

> An **O** or **R** judgment indicates evidence of an encounter behavior, **not proof** that Morgott uses the corresponding UE implementation pattern. All 82 Unreal-side suggestions below are recommendations for your game, not statements about Elden Ring source code. The original One Boss Fight audit statuses are intentionally not carried over as Morgott statuses.

## Fight-specific reference: what Morgott actually does

### Core behaviors

- **Attack identity is communicated through weapons:** conjured golden dagger, sword, spear and hammer are different threat families; the physical curved blade, tail and later bloodflame add additional combat grammar. [S1] [S2]
- **Spacing creates behavior:** player movement behind Morgott can invite tail or pivot-style pressure; close/midrange changes whether fast daggers, sword strings, spear charge or repositioning are feasible. [S1] [S4]
- **Combos are contextual rather than one fixed chain:** community breakdowns document different continuations depending on player front/rear position after moves such as spear charge. These are gameplay observations, not a published attack-selection algorithm. [S1]
- **Recovery must be judged spatially:** punish opportunities after helicopter finishers, spear charge whiffs, rain setup and certain bloodflame attacks depend on the player’s landing location and weapon startup. [S1] [S5]
- **Thresholds are more nuanced than just Phase 1/2:** deep community analysis reports an early holy rain unlock near 80% HP, cursed-blood transformation near 60% HP, and a later rapid-weapon string near 30% HP; animation interruption can shift timing. Other general guides summarize this more coarsely, so treat percentages as approximate observations. [S1] [S3]
- **Stance/parry pressure provides offensive counterplay:** Morgott is stance-breakable and requires three successful parries for a parry-induced critical opening per community reference. [S1] [S3]
- **Environment modifies attacks:** holy rain occupies fixed directional lanes; later random local geysers force awareness of ground position, but those geysers are not a uniform outward shockwave. [S1] [S4]

### Example move inventory (15 attack families)

| Attack family | Role / phase | Visible cue and behavior | Hit geometry | Player counterplay |
|---|---|---|---|---|
| Curved sword slash / delayed overhead | Melee front | Slash or downstroke with delayed weapon release; other sword follow-ups may occur. | Swept blade / narrow downward arc | Attack on actual release, not first lift; dodge flank; punish only confirmed finisher. |
| Holy dagger double slash | Close anti-greed | Quick conjured dagger attacks punish greedy proximity. | Two short narrow active windows | Move around flank and avoid immediate greedy extra attack. |
| Holy dagger throw | Medium / far pressure | Ranged spectral daggers can be a spacing or action-reaction threat. | Several narrow projectile lanes | Sidestep or dodge after projectile launch; keep approach option. |
| Holy spear throw | Ranged precision | Conjured long spear released along a forward lane; can lead to follow-up. | Fast narrow projectile / lane | Side dodge later in wind-up; avoid linear backward running. |
| Holy spear charge | Medium-to-long gap closer | Spear is presented then boss rushes; where player ends roll influences follow-up. | Moving thrust volume across root-motion path | Commit to lateral escape; dodge behind for flank punish. |
| Holy hammer overhead slam | Close/mid heavy follow-up | Large telegraphed conjured hammer slam; may lead to the helicopter-family ender. | Impact volume plus possible local shockwave | Dodge to side/back and identify whether ender follows. |
| Sword + hammer spin | Close area denial | Two-weapon spinning motion with broad arc and hammer end contact. | Sequential moving sweep volumes | Leave immediate radius or time successive dodges. |
| Helicopter: holy sword spin finisher | Melee combo finisher | Multi-hit spin after sword attack; recognizable grounded final hit and punish window. | Multiple blade arcs with separate windows | Stay outside repeated swings or evade around; retaliate after ender. |
| Rear tail sweep | Player behind | Rapid rear defense when player stays near back side. | Rear sweeping capsule / angular arc | Avoid persistent rear camping; jump/dodge with timing. |
| Holy swords rain | Arena zoning; scripted ~80% | Telegraphed floating blade pattern impacts and continues to constrain lanes for several seconds. | Initial circle + repeated falling sword hazard lanes | Identify lane pattern, move through safe spaces; exploit long setup cautiously. |
| Omen curse burst and geysers | Scripted ~60% transition | Boss plants sword, coughs and releases curse burst; water/geysers then change floor hazard conditions. | AOE burst + discrete localized eruptions | Disengage for burst; watch local geyser positions. |
| Bloodflame slam | Phase 2 | Sword-infused heavy ground impact can produce additional local geyser hazard. | Heavy impact + localized erupting AOE | Circle toward safe flank; retaliate after commitment if no geyser underfoot. |
| Bloodflame chase / two slashes | Phase 2 | Advancing slashes leave delayed explosive red bloodflame trails. | Two swept arcs + delayed hazard trail volumes | Avoid direct blade and delayed trail as distinct threats. |
| Bloodflame grab / skewer | Phase 2 | Forward impaling thrust leading to capture, lift and throw. | Narrow moving grab capsule + paired animation | Dodge at thrust release and take punish on whiff from side. |
| Rapid weapon-change barrage | Below ~30% unlock | Extended dagger → sword → hammer string, strong pressure but available only after late threshold. | Sequence of short weapon hits + broad heavy finisher | Survive string and identify true terminal recovery. |

The above list groups related animations into **families** for engineering purposes; it is not a claim that Morgott has precisely 15 internal attack entries. See [S1]–[S5] for observed moves and alternate naming.

## Engineering diagrams (original reconstructions)

**Figure 1 — proposed UE decision pipeline (not actual Morgott architecture)**

![Proposed decision pipeline](diagrams/01_decision_pipeline.png)

**Figure 2 — illustrative position-dependent combo branch**

![Combo branch](diagrams/02_combo_branches.png)

**Figure 3 — reported health-based moveset unlocks**

![Phase progression](diagrams/03_phases.png)

**Figure 4 — simplified hit geometry (top down; conceptual)**

![Damage geometry](diagrams/04_damage_geometry.png)

**Figure 5 — illustrative attack timeline (not actual Morgott frame timing)**

![Attack timeline](diagrams/05_attack_timeline.png)

## The 82 requirement-by-requirement mappings

For every ID, **Morgott reference** describes visible or community-reported behavior when possible, **Unreal implementation** describes a recommended translation to UE 5.5, and **Verification** gives a reproducible acceptance test. **Evidence O/R/I/U** describes the Morgott claim’s strength, not current project completion.

### Awareness and observable context

#### BOSS-AWR-001 — Target validity  ·  Evidence I

**Checklist requirement:** Every decision rejects dead, destroyed, invalid, out-of-arena or otherwise non-targetable actors.

**Morgott reference:** Morgott engages a valid opponent and stops offensive behavior at encounter termination. How his internal target-object validity and leash checks are encoded is unknown. [S1] [S2]

**Unreal Engine 5.5 translation:** Before every neutral or follow-up decision, reject dead/destroyed/non-targetable or off-arena targets; abandon an attack gracefully when a target becomes invalid.

**Verification / acceptance:** Kill/despawn the player, break encounter boundaries and interrupt a queued follow-up; expect safe reacquisition/reset.

#### BOSS-AWR-002 — Gate-time snapshot  ·  Evidence U

**Checklist requirement:** A timestamped combat context is rebuilt atomically at every neutral, combo or reaction gate.

**Morgott reference:** Morgott visibly changes follow-ups based on where the player finishes a dodge, suggesting fresh situation evaluation, but no public proof establishes atomic snapshots or timestamps.

**Unreal Engine 5.5 translation:** At every neutral, combo or reaction gate capture target location, action tags, facing, distance, LOS, boss phase and clock time in one immutable FCombatContext.

**Verification / acceptance:** Move behind Morgott during one combo; debug logs must show a fresh gate snapshot and the corresponding branch.

#### BOSS-AWR-003 — Distance convention  ·  Evidence I

**Checklist requirement:** Each attack declares whether range means root, capsule-surface or attack-origin distance.

**Morgott reference:** The spear has long reach, dagger pressure is strongest up close, and the sword/hammer cover different extents; exact range measurement convention is not published. [S1] [S2]

**Unreal Engine 5.5 translation:** Document root-to-root versus capsule edge versus attack-origin distance in each MoveData; avoid inconsistent range checks between selectors and traces.

**Verification / acceptance:** Place target on min/max range thresholds and repeat from different capsule sizes; compare eligibility with actual reach.

#### BOSS-AWR-004 — Signed angle and hysteresis  ·  Evidence R

**Checklist requirement:** Relative yaw is planar, boss-facing and stable near sector boundaries.

**Morgott reference:** Tail swipes answer positions behind him, and frontal or flank positioning changes certain sword/hammer continuations in detailed player observations. [S1] [S4]

**Unreal Engine 5.5 translation:** Compute signed planar target yaw relative to boss forward; add enter/leave thresholds around rear and side sectors to prevent flicker.

**Verification / acceptance:** Orbit across front/side/rear boundaries while an attack finishes; verify stable branch selection without oscillation.

#### BOSS-AWR-005 — Vertical separation  ·  Evidence U

**Checklist requirement:** Melee and ground actions enforce a documented Z tolerance.

**Morgott reference:** The fight mostly takes place on a relatively flat arena; no evidence establishes Morgott’s internal Z-difference gates.

**Unreal Engine 5.5 translation:** Apply vertical tolerance to sword, hammer, ground shockwaves and spear charge; define airborne exceptions for projectiles and leap attacks.

**Verification / acceptance:** Raise the player on test platforms; verify no ground sweep or melee attack hits vertically impossible targets.

#### BOSS-AWR-006 — Observable player activity  ·  Evidence R

**Checklist requirement:** Reactions use public committed action state, not raw future input.

**Morgott reference:** Players report Morgott responding to committed healing, long casts, and guard-break states; this should not be interpreted as knowledge of future button presses. [S1] [S4]

**Unreal Engine 5.5 translation:** Expose player action tags only after the animation/ability actually starts; gate reaction by commitment, LOS, feasible distance and reaction delay.

**Verification / acceptance:** Heal inside and outside reach; cancel during startup; ensure reaction never fires on input before an action is visible.

#### BOSS-AWR-007 — LOS and memory  ·  Evidence U

**Checklist requirement:** Precision reactions require current LOS; lost targets use timestamped last-seen state and reacquire.

**Morgott reference:** The arena is open and line-of-sight is generally unobstructed, but last-seen timers and LOS handling are not documented.

**Unreal Engine 5.5 translation:** Require current LOS for precision throws; store last-seen position/time and use a reacquire or search fallback after LOS loss.

**Verification / acceptance:** Introduce an occluding temporary wall and loss/reacquisition conditions; verify response is not omniscient.

#### BOSS-AWR-008 — Soft adaptation memory  ·  Evidence U

**Checklist requirement:** Pattern features decay, are capped and bias rather than force choices.

**Morgott reference:** Repeated-position pressure may result from fixed positional rules; evidence does not establish a decaying memory or player-pattern model.

**Unreal Engine 5.5 translation:** If adaptation is desired, track short-lived capped recent heal/roll/rear-camping metrics; bias preferences rather than guarantee a hard counter.

**Verification / acceptance:** Repeat backward rolls then vary behavior; ensure reactions shift probabilistically and decay after the pattern stops.

### Eligibility, utility and selection

#### BOSS-SEL-001 — Legal decision gates  ·  Evidence I

**Checklist requirement:** Full attack selection runs only in neutral or an explicitly authorized gate.

**Morgott reference:** Morgott’s attacks visibly commit and branch rather than instantly switching on every player movement; the exact internal selection-gate topology is unknown. [S1] [S2]

**Unreal Engine 5.5 translation:** Call selection in neutral or authored combo/reaction windows only; keep active committed motion under a single executor.

**Verification / acceptance:** Move player rapidly during active attack; ensure no illegal attack change until the next legal gate.

#### BOSS-SEL-002 — Hard-filter precedence  ·  Evidence I

**Checklist requirement:** Phase, state, range, angle, LOS, cooldown, resource, asset and path constraints reject before scoring.

**Morgott reference:** His weapon choices are context-sensitive: dagger at closer spacing, spear throws at range, tail response from behind, and health-gated moves. [S1] [S2]

**Unreal Engine 5.5 translation:** Hard-filter by phase, state, attack range, angle, LOS, cooldown and asset readiness; score only passing candidates.

**Verification / acceptance:** At each position/phase enumerate rejected candidates and reasons; no impossible move should be selected.

#### BOSS-SEL-003 — Executable asset gate  ·  Evidence U

**Checklist requirement:** A move with a missing montage/socket/required resource is never selected.

**Morgott reference:** The shipped boss of course has working animations; a data/asset validity gate inside FromSoftware’s runtime is not observable.

**Unreal Engine 5.5 translation:** Validate montage, sockets, curves, reaction ability and VFX references during content audit and at runtime before committing.

**Verification / acceptance:** Delete an attack montage reference in a dev copy; attack should be skipped with diagnostics, not leave boss frozen.

#### BOSS-SEL-004 — Normalized utility  ·  Evidence U

**Checklist requirement:** Eligible moves receive comparable documented range, angle, opportunity, spacing, phase and variety terms.

**Morgott reference:** Morgott creates the impression of contextual selection, but neither a utility-scoring equation nor its weights are established publicly.

**Unreal Engine 5.5 translation:** Use normalized scores for geometry, target commitment, phase, spacing, combo intent, variety and hazards; tune from recorded fights.

**Verification / acceptance:** Replay identical contexts with debug scoring; highest eligible utility should dominate without deterministic repetition.

#### BOSS-SEL-005 — Bounded randomness  ·  Evidence U

**Checklist requirement:** Variation is limited to near-best candidates, with deterministic seeded RNG.

**Morgott reference:** Different choices occur in comparable situations, but we cannot verify seeded RNG, near-best sampling, or exact randomness limits.

**Unreal Engine 5.5 translation:** Randomly choose among near-best legal attacks with reproducible local seed for tests; keep deterministic cooldown and rule enforcement.

**Verification / acceptance:** Run 1000 seeded neutral gates; confirm diversity, no invalid moves, and reproducible outputs.

#### BOSS-SEL-006 — Cooldown semantics  ·  Evidence R

**Checklist requirement:** Cooldown commits on an attack start, not on rejected or failed choice attempts.

**Morgott reference:** Community moveset analysis identifies attack-specific cooldown behavior, but not the engine’s precise commit semantics. [S1]

**Unreal Engine 5.5 translation:** Start cooldown only when the montage successfully enters the committed attack; failed selection or montage playback must not consume it.

**Verification / acceptance:** Force montage-start failure then retry; confirm cooldown was not consumed.

#### BOSS-SEL-007 — Anti-repeat memory  ·  Evidence U

**Checklist requirement:** Recent move and family repetition lower preference with time decay; hard spacing may protect signature moves.

**Morgott reference:** The moveset contains numerous attacks and reported cooldowns, but explicit anti-repeat memory and decay are not publicly verified.

**Unreal Engine 5.5 translation:** Add recent attack-family penalties and optional minimum separation for signature rain/hammer spins; store expiring history on committed starts.

**Verification / acceptance:** Fight at one fixed range for 5 minutes; histogram short-loop repeats and long-form variety.

#### BOSS-SEL-008 — No-candidate fallback  ·  Evidence I

**Checklist requirement:** Empty eligible sets choose purposeful wait, reorientation, approach/retreat, EQS positioning or reset.

**Morgott reference:** Morgott uses idle, approach, hops, and repositioning between attacks; no-candidate implementation is not disclosed. [S1] [S2]

**Unreal Engine 5.5 translation:** If no attack is eligible, intentionally face, approach, retreat, strafe, reset, or search, with bounded durations; never spin in a retry loop.

**Verification / acceptance:** Disable all valid attacks; watch boss choose visible purposeful neutral action without CPU spikes.

#### BOSS-SEL-009 — Reaction latency and budget  ·  Evidence I

**Checklist requirement:** Defensive/heal reactions require nonzero latency, cooldown/budget and ordinary feasibility.

**Morgott reference:** A flask or cast may invite quick projectiles and gap closing, but exact reaction latency or budget cannot be established by observation alone. [S1] [S4]

**Unreal Engine 5.5 translation:** Add nonzero reaction latency, cooldown, animation free-state, LOS and travel-time rules; never interrupt committed motion to cheat.

**Verification / acceptance:** Use healing at several ranges and just after attack commit; measure realistic response latency and valid interruptions.

#### BOSS-SEL-010 — Decision trace  ·  Evidence U

**Checklist requirement:** Each gate logs context, all candidate eligibility/reasons/scores, winner and RNG seed.

**Morgott reference:** No public view exposes Morgott’s internal attack scoring trace or seed values.

**Unreal Engine 5.5 translation:** Log gate ID, player state, all filtered candidates and reasons, selected move, RNG seed and phase in a development-only ring buffer.

**Verification / acceptance:** Recreate any test run from trace and seed; compare selected sequence to recorded animation events.

### Attack executor and state safety

#### BOSS-EXE-001 — Single execution authority  ·  Evidence U

**Checklist requirement:** One executor owns current attack, instance, section, state, target snapshot and victim sets.

**Morgott reference:** Only one coherent attack appears to own each active weapon/action, but internal executor ownership is unknown.

**Unreal Engine 5.5 translation:** Use one UBossAttackExecutorComponent as authority for attack instance, montage/section, phase, victim records, hit windows and cleanup.

**Verification / acceptance:** Trigger combo, stagger and phase transition on the same frame; one authoritative final state remains.

#### BOSS-EXE-002 — Instance before montage  ·  Evidence U

**Checklist requirement:** A unique ID and wind-up state are set before montage playback.

**Morgott reference:** There is no public evidence of Morgott’s internal attack instance creation order.

**Unreal Engine 5.5 translation:** Create unique FAttackInstanceId and set wind-up state before Montage_Play and Notify activation; carry ID through effects and damage.

**Verification / acceptance:** Add immediate startup notify and forced montage failure; verify events map to the correct instance.

#### BOSS-EXE-003 — Start rollback  ·  Evidence U

**Checklist requirement:** Montage play failure restores neutral/movement and does not consume a live attack.

**Morgott reference:** Montage startup rollback is a hidden engine implementation detail.

**Unreal Engine 5.5 translation:** Check playback handle; on failure atomically reset movement/rotation/temporary states and do not consume attack cooldown.

**Verification / acceptance:** Provide missing Montage in a test Data Asset; boss resumes neutral and chooses a fallback.

#### BOSS-EXE-004 — Stale event rejection  ·  Evidence U

**Checklist requirement:** Notify/callback instance, montage, section and expected state are validated.

**Morgott reference:** Stale animation callback rejection is not externally observable.

**Unreal Engine 5.5 translation:** Every callback validates instance ID, montage, section and expected state; reject old timelines after interruption or phase change.

**Verification / acceptance:** Interrupt and immediately start a new attack; late Notify must not damage or trigger an old branch.

#### BOSS-EXE-005 — Explicit priority  ·  Evidence I

**Checklist requirement:** Death, phase, stance, special, combo and completion conflicts follow a documented order.

**Morgott reference:** Morgott can be staggered and phase-transition mid-fight; these are visible priorities, though the exact arbitration table is unknown. [S1] [S2]

**Unreal Engine 5.5 translation:** Declare priority: death > forced phase > stance break > unavoidable transition > attack abort > legal combo > recovery, with design exceptions.

**Verification / acceptance:** Hit stance threshold as phase threshold is crossed; verify a single valid transition and no overlapping offense.

#### BOSS-EXE-006 — Idempotent abort  ·  Evidence U

**Checklist requirement:** Abort closes collision, warping, gates, armor and latent work, then restores motion once.

**Morgott reference:** Disappearing active attacks after stagger/death imply cleanup, but idempotent abort internals are hidden.

**Unreal Engine 5.5 translation:** Abort exactly once: stop traces, cancel spawned persistent actors when required, release warp, clear armor and reset gate state.

**Verification / acceptance:** Call Abort twice during active grab/AoE; expect no extra hit or leaked animation state.

#### BOSS-EXE-007 — Watchdog  ·  Evidence U

**Checklist requirement:** Every live attack has maximum expected duration plus margin and a safe timeout path.

**Morgott reference:** No public information documents an attack watchdog or duration margin.

**Unreal Engine 5.5 translation:** Track max expected montage duration plus bounded margin; if state is still live, close damage and transition to safe recovery.

**Verification / acceptance:** Suppress Montage End/Notify End in a controlled dev test; verify no permanent attack lock.

#### BOSS-EXE-008 — Cleanup-before-unlock  ·  Evidence U

**Checklist requirement:** Trace and temporary state are closed before any next selection can occur.

**Morgott reference:** It cannot be established whether hit volumes are torn down before the next selection gate internally.

**Unreal Engine 5.5 translation:** Close active attack collision and temporary invulnerability/warp state before clearing busy flag or choosing follow-up.

**Verification / acceptance:** Spam branching and interrupt at edge frames; no hit from a previous attack may land after next start.

### Conditional combos

#### BOSS-COM-001 — Authored graph  ·  Evidence R

**Checklist requirement:** Combo nodes and allowed outgoing edges are data-authored, not arbitrary full-pool selections.

**Morgott reference:** Community flowcharts document opening moves and restricted follow-up families: e.g. spear charge can lead to different sword/hammer continuations depending on position. [S1] [S2]

**Unreal Engine 5.5 translation:** Author move nodes, legal next-edge lists, gate timing, hit/guard/whiff prerequisites and cooldowns as Data Assets.

**Verification / acceptance:** Render attack graph from assets; all observed branches must appear; no unrelated attack may enter a combo gate.

#### BOSS-COM-002 — Gate after damage  ·  Evidence R

**Checklist requirement:** A branch gate occurs only at its authored time, normally after the prior hit window closes.

**Morgott reference:** Many follow-ups occur after a slash, charge or slam has reached a recognizable completed-hit stage; exact internal event marker is undisclosed. [S1]

**Unreal Engine 5.5 translation:** Place combo-gate Notifies after active hit window closes, unless move card explicitly allows overlapping multi-weapon hits.

**Verification / acceptance:** Slow animation to 0.25x; prove hitbox closes before branch gate for representative combos.

#### BOSS-COM-003 — Fresh branch context  ·  Evidence R

**Checklist requirement:** The gate evaluates current target state, not only the first move's snapshot.

**Morgott reference:** Changing position during a spear charge or dodge can alter whether a frontal sword continuation or an angled hammer response follows. [S1]

**Unreal Engine 5.5 translation:** At each gate resample player range/yaw/action; never reuse only the initiating attack snapshot.

**Verification / acceptance:** Dodge behind vs remain in front during spear charge; record two different eligible follow-up families.

#### BOSS-COM-004 — Explicit hit-confirm policy  ·  Evidence R

**Checklist requirement:** Each edge states whether contact, damage, guard or whiff is required.

**Morgott reference:** Reported guard-break interactions can change Morgott’s follow-up behavior; source notes some equipment-dependent exceptions. [S1]

**Unreal Engine 5.5 translation:** Every edge declares hit confirm / blocked / guard-broken / whiff / location conditions; separate confirmed hit from raw overlap.

**Verification / acceptance:** Compare clean whiff, guarded strike, parry and guard break; follow-up branches must match configured conditions.

#### BOSS-COM-005 — Single-use gate  ·  Evidence U

**Checklist requirement:** A gate is consumed once per matching instance.

**Morgott reference:** Repeated follow-up transition callbacks cannot be inspected externally.

**Unreal Engine 5.5 translation:** Consume a combo gate exactly once per attack instance and gate ID, even if Notify fires twice or the montage scrubs.

**Verification / acceptance:** Emit duplicate gate events and validate only one follow-up is committed.

#### BOSS-COM-006 — Finite pressure  ·  Evidence R

**Checklist requirement:** Combo depth, edge use/cooldown and maximum pressure duration enforce eventual recovery.

**Morgott reference:** He has long multi-weapon strings but also finishers such as the spinning sword/hammer sequence, allowing counterattacks after the sequence ends. [S1] [S5]

**Unreal Engine 5.5 translation:** Bound graph depth, number of repeat edges and pressure time; finishers always reach recovery unless special scripted phase behavior intervenes.

**Verification / acceptance:** Force max-depth combos in 100 fights; none should loop forever or prevent all offense from the player.

#### BOSS-COM-007 — Default recovery  ·  Evidence I

**Checklist requirement:** A missing/invalid target, edge or montage routes to declared recovery.

**Morgott reference:** When the player escapes range, Morgott may end a sequence, hop away, or reacquire rather than continuing every attack without a target. [S1] [S2]

**Unreal Engine 5.5 translation:** Missing edge/invalid target/failed Montage resolves to an authored recovery pose and intentional neutral movement.

**Verification / acceptance:** Remove target during gate; verify no frozen animation or instantaneous neutral bypass.

### Animation, tracking and motion

#### BOSS-ANM-001 — Montage timeline authority  ·  Evidence U

**Checklist requirement:** Commit, active, gate, armor and recovery derive from montage events/position rather than duplicate delays.

**Morgott reference:** Weapon release and impact visibly follow authored animation; exact animation-notify pipeline and engine event authority are not public.

**Unreal Engine 5.5 translation:** Drive attack hit windows, commit points, warp permissions and recovery transitions from Montage Notifies and montage-position checks; avoid unrelated timers.

**Verification / acceptance:** Play at 0.5x and during hitches; hit events should follow authored frame positions.

#### BOSS-ANM-002 — Telegraph phases  ·  Evidence O

**Checklist requirement:** Pose/direction/release cues precede damage and identify geometry.

**Morgott reference:** Morgott uses readable wind-ups, summoned holy weapon silhouettes, sword rain setup, and bloodflame infusion cues before distinctive attacks. [S1] [S2] [S4]

**Unreal Engine 5.5 translation:** Build attack telegraph design per move: pose, left/right weapon, floor cue, audio onset, release cue, camera framing and active hit shape.

**Verification / acceptance:** Blindplay tester identifies thrust/sweep/hammer/rain/grab from their cues without looking at debug labels.

#### BOSS-ANM-003 — Bounded holds  ·  Evidence R

**Checklist requirement:** Variable delay has declared min/max and is chosen before commitment with a reliable release cue.

**Morgott reference:** Delayed sword/hammer releases are perceptible, but precise variable random hold durations are not proven. [S1] [S5]

**Unreal Engine 5.5 translation:** If adding variable hold, define min/max chosen at wind-up start and make release animation readable; do not assume Morgott randomizes every hold.

**Verification / acceptance:** Record 30 repetitions; ensure no zero-warning release and all delays stay within authored bounds.

#### BOSS-ANM-004 — Staged rotation cap  ·  Evidence R

**Checklist requirement:** Early/late/active/recovery stages enforce per-move turn limits.

**Morgott reference:** Positioning can make a committed leap or spear charge pass the player, creating rear-flank punish windows; exact turn-rate curves remain unverified. [S1] [S4]

**Unreal Engine 5.5 translation:** Use explicit early/late wind-up tracking, release lock and limited recovery-turn rates on each move; never 180-degree auto-snap mid strike.

**Verification / acceptance:** Circle behind during wind-up and after commit; plot yaw per stage and test dodge consistency.

#### BOSS-ANM-005 — Exclusive motion authority  ·  Evidence U

**Checklist requirement:** Navigation/manual movement stops while root-motion/warp attack owns motion.

**Morgott reference:** Dashes, leaps and cartwheels are visible, but the game’s locomotion/root-motion ownership internals are unknown.

**Unreal Engine 5.5 translation:** Suspend AI MoveTo/CharacterMovement steering while an attack owns root motion or Motion Warping; restore cleanly at exit.

**Verification / acceptance:** Start a lunge while AI is chasing; detect no Nav/RootMotion tug-of-war or foot sliding.

#### BOSS-ANM-006 — Bounded Motion Warping  ·  Evidence U

**Checklist requirement:** Warp target updates only in an authorized early window and obeys translation/rotation/Z/path caps.

**Morgott reference:** Morgott changes displacement across leaps and charges; it is not established whether or how Souls game internals use a UE-style motion-warp system.

**Unreal Engine 5.5 translation:** For a UE imitation, restrict motion-warp target updates to early preparation, clamp reach and yaw and prevent collision crossing.

**Verification / acceptance:** Jump sideways after warp lock; attack should miss rather than unnaturally curve into target.

#### BOSS-ANM-007 — Notify-end independence  ·  Evidence U

**Checklist requirement:** Blend-out, interruption and watchdog all close any window even if Notify End is skipped.

**Morgott reference:** No external source establishes whether his hit windows rely on notify-end callbacks or fail-safe lifecycle logic.

**Unreal Engine 5.5 translation:** On Montage End, blend-out, interruption, phase transition and watchdog, always force all hit windows closed.

**Verification / acceptance:** Skip Notify End in a test asset or interrupt on active frame; verify trace stops immediately.

#### BOSS-ANM-008 — MoveCard handoff  ·  Evidence I

**Checklist requirement:** Every move records axes, scale/FPS, timing, displacement, sockets, warp, cues, cancels and branches.

**Morgott reference:** Morgott’s distinctive armament and geometry imply each move needs different animation specifications; his own studio asset documentation is private. [S1] [S2]

**Unreal Engine 5.5 translation:** Create MoveCard for each sword, dagger, hammer, spear, tail, rain and bloodflame action: FPS, startup, contacts, root motion, sockets, cues and branches.

**Verification / acceptance:** Content review rejects any active attack without its MoveCard and montage-based timing sheet.

### Hit detection and damage

#### BOSS-HIT-001 — Geometry fidelity  ·  Evidence O

**Checklist requirement:** Collision family and volume match the visible thrust, sweep, slam, ring, lane or grab.

**Morgott reference:** Morgott uses narrow sword/spear thrusts, broad spinning blade arcs, heavy hammer impacts, tail sweeps, falling blades, bloodflame trails and bloodflame grab. [S1] [S2] [S4]

**Unreal Engine 5.5 translation:** Use separate hit-volume families matching visible geometry: moving sword capsule, spear lane, sweep volumes, impact sphere, rain blades, persistent flame and grab capture.

**Verification / acceptance:** Capture synchronized weapon/hitbox overlays; each visible threat corresponds to a plausible collision volume.

#### BOSS-HIT-002 — Swept temporal sampling  ·  Evidence U

**Checklist requirement:** Weapon samples sweep previous-to-current positions during active windows.

**Morgott reference:** Visible blades move rapidly; exact Elden Ring collision sampling strategy is not publicly documented.

**Unreal Engine 5.5 translation:** During active animation frames sweep each weapon sample from previous to current world transform rather than relying only on instantaneous overlap.

**Verification / acceptance:** Test 30 FPS, 120 FPS and deliberate frame spikes; a blade passing through a target registers once.

#### BOSS-HIT-003 — Blade interior samples  ·  Evidence U

**Checklist requirement:** Long rotating weapons sample multiple points, not endpoints only.

**Morgott reference:** Long sweeping weapon arcs would benefit from interior sampling; public observation does not prove internal sample count.

**Unreal Engine 5.5 translation:** Add blade base, mid and tip samples (or contact segments) to the sword and spectral spear to cover interior trajectory.

**Verification / acceptance:** Put small test capsules at multiple places along blade; all should produce consistent contact.

#### BOSS-HIT-004 — Adaptive substeps  ·  Evidence U

**Checklist requirement:** Excessive sample translation/angular delta creates bounded substeps.

**Morgott reference:** Adaptive weapon trace subdivision is an engineering proposal, not a verified Morgott mechanic.

**Unreal Engine 5.5 translation:** If angular or positional delta between frames exceeds budget, subdivide swept segments with a strict maximum work cap.

**Verification / acceptance:** Inject 100 ms frame hitch into fast spin attack; compare missed hit count and CPU cost.

#### BOSS-HIT-005 — Query filtering  ·  Evidence U

**Checklist requirement:** Traces ignore owner/allies and use query-only channels with valid target/team checks.

**Morgott reference:** The boss attacks opponents rather than itself, but underlying object channels and filters are unavailable.

**Unreal Engine 5.5 translation:** Ignore attacker, attached weapon, friendly allied actors and non-targetables; use query-only physics channels and target classification.

**Verification / acceptance:** Spawn ally, summon and destructible prop between sword and target; verify correct candidates only.

#### BOSS-HIT-006 — Logical-victim dedupe  ·  Evidence U

**Checklist requirement:** Multiple components/bones of one actor count once according to hit policy.

**Morgott reference:** An ordinary sword swing should not multiply damage because it intersects multiple player bones; dedupe internals not visible.

**Unreal Engine 5.5 translation:** Key hit victims by logical actor/character and attack-window ID, not individual mesh primitive or bone.

**Verification / acceptance:** Hit multiple skeletal bodies with one sweep; exactly one configured contact is applied.

#### BOSS-HIT-007 — Explicit hit policy  ·  Evidence O

**Checklist requirement:** Once-per-attack, once-per-window, periodic and impact-plus-splash policies behave distinctly.

**Morgott reference:** Multi-weapon strings contain separate strikes; holy sword rain and bloodflame ground effects can produce distinct successive hazards. [S1] [S2]

**Unreal Engine 5.5 translation:** Define policy per attack window: once per strike, per impact, per projectile, periodic hazard, or separately flagged direct/splash.

**Verification / acceptance:** Stand in same AoE; verify hit frequency and knockback match each attack card.

#### BOSS-HIT-008 — Central defense order  ·  Evidence I

**Checklist requirement:** Validity/dedupe, iframe, parry, guard, posture/armor, health and feedback resolve in one documented order.

**Morgott reference:** Morgott’s fight supports dodge iframes, blocking, guard-break reactions and parryable physical sword attacks; internal resolution order is private. [S1] [S3]

**Unreal Engine 5.5 translation:** Centralize defense resolution: valid target -> dedupe -> iframe -> parry -> guard -> armor/stance -> health -> feedback, with per-attack exceptions.

**Verification / acceptance:** Use same target in sword/spear/hammer/rain trials while blocking, dodging and parrying; record consistent rule application.

#### BOSS-HIT-009 — Iframe completeness  ·  Evidence I

**Checklist requirement:** An invulnerable contact applies neither unintended health nor posture effects.

**Morgott reference:** Well-timed rolls can avoid sword, hammer, spear and many AoE hits; exact secondary posture handling requires engine-level inspection. [S1] [S2]

**Unreal Engine 5.5 translation:** When iframe succeeds, reject health, status and stance effects unless design explicitly says otherwise; handle undodgeable lingering mechanics separately.

**Verification / acceptance:** Roll through two contact windows and verify both direct and secondary effects behave per attack specification.

#### BOSS-HIT-010 — Direct/splash precedence  ·  Evidence I

**Checklist requirement:** Direct and AoE overlap cannot double-dip unless the data explicitly permits it.

**Morgott reference:** A hammer slam, bloodflame trail or geyser can overlap with its originating weapon impact; visible footage does not reveal dedupe policy. [S1] [S2]

**Unreal Engine 5.5 translation:** Tag direct strike and splash actor with one logical AttackID; designate direct-hit priority and explicitly permit independent secondary explosion only when intended.

**Verification / acceptance:** Stand at impact center vs nearby ring; verify no accidental direct+splash double damage.

#### BOSS-HIT-011 — Swept annulus  ·  Evidence I

**Checklist requirement:** Radial waves test the previous-to-current radius band and damage each victim once.

**Morgott reference:** Morgott’s phase transition spawns localized eruptions/geysers, and holy rain occupies targeted lanes; it is not one uniform continuously expanding ring. [S1] [S4]

**Unreal Engine 5.5 translation:** For the transition use timed geyser zones/overlap volumes; implement swept annulus only if a separate shockwave move explicitly needs an outward ring.

**Verification / acceptance:** Map impact zones and timing across the arena; ensure no invisible damage band or frame-step gap.

#### BOSS-HIT-012 — Grab fail-safe  ·  Evidence O

**Checklist requirement:** Grab capture, defense, alignment, control lock, damage and release are explicit and restore on interrupt/death.

**Morgott reference:** Phase-two Bloodflame Skewer/Grab impales a struck player, lifts them and throws them; it requires an authored capture/release lifecycle. [S1] [S2] [S4]

**Unreal Engine 5.5 translation:** Implement capture validity, iframe/guard behavior, paired attacker-victim Montages, motion alignment, damage event, interruption/death release and control restoration.

**Verification / acceptance:** Interrupt the grab at startup, after capture, during lift, and at death; player always regains control.

### Movement and arena

#### BOSS-MOV-001 — Range-band policy  ·  Evidence R

**Checklist requirement:** Close, ideal, approach and reacquire bands produce distinct movement/action preferences.

**Morgott reference:** Morgott alternates close sword pressure, midrange spear threat and long-range dagger/spear actions; the player can influence his available moves through spacing. [S1] [S4]

**Unreal Engine 5.5 translation:** Define close, ideal, chase and reacquire bands and choose movement based on the attack families available in each.

**Verification / acceptance:** Hold target at 1, 3, 7 and 12 meters; log qualitatively different movement and legal attack sets.

#### BOSS-MOV-002 — Combat positioning  ·  Evidence I

**Checklist requirement:** Candidate positions score reachability, distance, LOS, wall/hazard clearance, flank and variety.

**Morgott reference:** Morgott performs hops, sidesteps, cartwheels, approach and retreat; whether he uses numerical candidate-position scoring is unknown. [S1] [S2]

**Unreal Engine 5.5 translation:** For UE, evaluate few reachable strafe/reposition points for distance, visibility, wall clearance and follow-up opportunities.

**Verification / acceptance:** Test backpedaling and wall proximity; boss chooses reachable non-clipping approach/reposition destinations.

#### BOSS-MOV-003 — Movement commitment  ·  Evidence U

**Checklist requirement:** Strafe/approach choices have minimum duration and are not restarted every frame.

**Morgott reference:** Movement feels deliberate, but there is no evidence of internal minimum commitment timers.

**Unreal Engine 5.5 translation:** Give strafe/retreat choices minimum dwell time and interruption reasons, avoiding per-tick path change oscillation.

**Verification / acceptance:** Record move requests under moving target; no rapidly flipping left/right direction.

#### BOSS-MOV-004 — Wall-safe attacks  ·  Evidence I

**Checklist requirement:** Root-motion/warp paths predict walls and use correction, fallback or decline.

**Morgott reference:** Players report awkward fight patterns near the arena perimeter; leap and charge moves may be constrained by wall geometry. [S1]

**Unreal Engine 5.5 translation:** Predict root-motion path sweep; decline or adjust risky attacks near walls rather than letting the capsule clip into arena props.

**Verification / acceptance:** Bait spear charge against walls at all headings and review penetration and animation displacement.

#### BOSS-MOV-005 — Arena-valid responses  ·  Evidence U

**Checklist requirement:** Unreachable/elevated/outside targets cause reposition, search, leash or reset.

**Morgott reference:** The shipped encounter uses a bounded arena, but elevated/outside/leash target response policy is not known.

**Unreal Engine 5.5 translation:** If unreachable, fall back to seek, face, reacquire or reset; never throw a melee-only move at a target outside navmesh.

**Verification / acceptance:** Teleport test player beyond arena, above floor and behind blockers; boss exits invalid attack loop safely.

#### BOSS-MOV-006 — Arena/attack fit  ·  Evidence O

**Checklist requirement:** Escape requirements and camera visibility are valid from every legal arena position.

**Morgott reference:** The open Elden Throne arena supports lateral dodging and sightlines; holy swords rain creates lanes that constrain usable paths. [S1] [S2]

**Unreal Engine 5.5 translation:** Ensure every attack has dodge paths from legal arena positions and camera can show weapon release; avoid spawning impossible hazard overlaps.

**Verification / acceptance:** Spawn player at center and every edge point; capture dodge-space coverage for rain, hammer and geysers.

### Pacing and punishability

#### BOSS-PAC-001 — Explicit attack segments  ·  Evidence O

**Checklist requirement:** Every move declares anticipation, hold, commit, active, follow-through, recovery and neutral boundaries as applicable.

**Morgott reference:** Morgott shows dramatic anticipation, fast active slashes, chained follow-through and enders with identifiable recovery; exact timeline boundaries require frame study. [S1] [S5]

**Unreal Engine 5.5 translation:** For each MoveCard annotate anticipation, delayed hold, last tracking frame, active sub-windows, combo gate, recovery and neutral unlock.

**Verification / acceptance:** Export montage timeline for 12+ representative moves and compare to capture at slow playback.

#### BOSS-PAC-002 — Pressure variation  ·  Evidence O

**Checklist requirement:** Offense rises and falls; neutral/recovery periodically reset pressure.

**Morgott reference:** Sequences alternate explosive multi-hit offense, slow overhead anticipation, repositioning, and recognizable windows after specific enders. [S1] [S5]

**Unreal Engine 5.5 translation:** Manage combo-pressure budget, slow/heavy versus fast attacks, and neutral reset probabilities without forcing unnatural pauses.

**Verification / acceptance:** Chart 20 consecutive fights: longest unbroken pressure, waits and punish frequency must meet authored combat targets.

#### BOSS-PAC-003 — Guaranteed openings  ·  Evidence R

**Checklist requirement:** Some high-commitment moves have unconditionally meaningful recovery.

**Morgott reference:** Players can punish holy sword rain setup, helicopter finisher, missed spear charge and many bloodflame enders; safety depends on position and weapon speed. [S1] [S4] [S5]

**Unreal Engine 5.5 translation:** Mark actual guaranteed opening only after proving a chosen player weapon can start and exit safely from a defined position.

**Verification / acceptance:** For each claimed guaranteed opening, test light/heavy from close and flank distances with 30/60 FPS.

#### BOSS-PAC-004 — Conditional opening cues  ·  Evidence R

**Checklist requirement:** Follow-up-capable recoveries reveal the gate/outcome consistently.

**Morgott reference:** A hammer or sword continuation can be conditional on where the player rolls, so an apparent gap may not be a safe ender. [S1]

**Unreal Engine 5.5 translation:** Make potential follow-up readable via animation stance, armament spawn, pause or audible cue; separate conditional recovery from true ender.

**Verification / acceptance:** Test players blind: can they recognize whether the boss has a pending branch?

#### BOSS-PAC-005 — Punish-margin calculation  ·  Evidence I

**Checklist requirement:** Opening classification includes travel, player startup and safety buffer, not montage recovery alone.

**Morgott reference:** Morgott’s openings depend strongly on dodge destination and weapon speed; a single recovery-animation length cannot describe punish safety. [S1] [S5]

**Unreal Engine 5.5 translation:** Compute usable window = boss lock remaining − player approach − player attack startup − safety margin, for position/weapon variants.

**Verification / acceptance:** Measure actual travel/startup for light, heavy and flask; label guaranteed/conditional based on empirical margin.

#### BOSS-PAC-006 — Neutral is purposeful  ·  Evidence O

**Checklist requirement:** Non-attacking time may face, strafe, observe or reset without hidden damage pressure.

**Morgott reference:** Morgott may hop away, move, watch, or approach between strings; these intervals change positioning and open small decisions for the player. [S1]

**Unreal Engine 5.5 translation:** Create neutral states with visible facing/footwork and bounded pacing controls; never allow invisible damage during neutral.

**Verification / acceptance:** Measure idle durations and confirm no hidden active traces between attacks.

### Defense, posture and interruption

#### BOSS-DEF-001 — Separate health/reaction/posture  ·  Evidence O

**Checklist requirement:** Health, immediate flinch and posture accumulation have independent state and rules.

**Morgott reference:** Morgott has health, staggerable attacks, and a separate stance/critical-opening system; successful parries also build toward a critical opening. [S1] [S3]

**Unreal Engine 5.5 translation:** Separate health, one-hit reaction and cumulative stance resources; prevent incidental animation flinches from resetting stance unless authored.

**Verification / acceptance:** Compare chip damage, high-stagger attack and parry; confirm distinct health/reaction/posture outcomes.

#### BOSS-DEF-002 — Posture regeneration  ·  Evidence R

**Checklist requirement:** Regeneration starts only after a documented quiet delay and rate, then resets correctly.

**Morgott reference:** Community combat research reports a stance value of 80 and delayed reset behavior; exact patch-specific decay timing requires verification before treating it as a target. [S1] [S3]

**Unreal Engine 5.5 translation:** Expose posture maximum, quiet timer and regeneration curve in boss data; tune to desired fight pacing rather than copying unseen internals.

**Verification / acceptance:** After a controlled stance hit, wait different delays and log posture regeneration transition.

#### BOSS-DEF-003 — Single stance break  ·  Evidence O

**Checklist requirement:** Threshold produces one break, closes current offense and exposes a bounded critical window.

**Morgott reference:** Once stance is depleted Morgott can fall into a critical-hit opportunity; parry chains also lead to riposte availability. [S1] [S3]

**Unreal Engine 5.5 translation:** Fire stance break once at threshold, cancel offense, close active weapon windows and expose a timed critical socket state.

**Verification / acceptance:** Strike threshold during active combo and phase threshold; no duplicate breaks or stale active hit damage.

#### BOSS-DEF-004 — Windowed hyperarmor  ·  Evidence I

**Checklist requirement:** Interruption resistance exists only for named moves/windows; health/posture policy is explicit.

**Morgott reference:** Some moves are interruptible via stance pressure while others visibly continue through smaller hits; per-animation hyperarmor windows are not published. [S1] [S2]

**Unreal Engine 5.5 translation:** Author hyperarmor windows per Montage section; specify effects on flinch and stance damage separately.

**Verification / acceptance:** Apply same stagger attack at startup, active and recovery for hammer, spear and bloodflame attacks.

#### BOSS-DEF-005 — Fair boss defense  ·  Evidence U

**Checklist requirement:** Boss block/parry/dodge has facing/timing, startup, cooldown, cost and recovery constraints.

**Morgott reference:** Morgott is not typically depicted using a shield-block/parry/dodge system like a humanoid duelist; his defensive repertoire is mainly repositioning, mobility and retaliatory threats.

**Unreal Engine 5.5 translation:** Treat active boss block/parry as optional, not as a required copy of Morgott; if implemented, impose startup, angle, cooldown and recovery.

**Verification / acceptance:** Never claim this is a documented Morgott feature; prove fair reaction timings for any added defensive action.

### Phases and anti-cheese reactions

#### BOSS-PHS-001 — Phase rule set  ·  Evidence O

**Checklist requirement:** A phase defines move pool, utility modifiers, combo cap, movement, pressure, recovery and presentation.

**Morgott reference:** Detailed moveset analysis describes an early sword-rain unlock around 80% HP, a dramatic cursed-blood transition around 60%, and an additional rapid armament barrage becoming eligible around 30%. [S1] [S3]

**Unreal Engine 5.5 translation:** Represent threshold unlocks as data-driven event/phase flags; change attack pool, geyser hazard rule, pressure and follow-up families, not merely HP damage scale.

**Verification / acceptance:** Reduce HP slowly across thresholds; record first-time events, legal attacks before/after and late-fight move availability.

#### BOSS-PHS-002 — Safe transition policy  ·  Evidence R

**Checklist requirement:** Threshold queues/delegates interruption according to one declared policy; first version should defer to a safe gate.

**Morgott reference:** The transition visibly interrupts or supersedes current combat with sword-plant/cough and curse eruption; community analysis notes stagger can shift its actual activation point. [S1] [S3]

**Unreal Engine 5.5 translation:** Queue one protected phase action at a documented safe/preemptive gate, cancel stale attack traces and do not transition into an invalid state.

**Verification / acceptance:** Cross threshold while staggered, grabbing and during combo branch; transition occurs once without stray damage.

#### BOSS-PHS-003 — Phase monotonicity  ·  Evidence I

**Checklist requirement:** Healing and repeated threshold events do not oscillate or duplicate the transition.

**Morgott reference:** Morgott does not visibly revert to an earlier move set after entering cursed-blood phase, and threshold events are one-time. [S1] [S2]

**Unreal Engine 5.5 translation:** Monotonic phase state and one-shot transition flags; heals cannot rearm 80/60/30% unlock events.

**Verification / acceptance:** Artificially heal boss above a prior threshold; verify no duplicated sword-rain intro or phase transition.

#### BOSS-PHS-004 — Fair heal punish  ·  Evidence R

**Checklist requirement:** Heal reaction requires committed heal, latency, LOS, range, travel feasibility, cooldown and free executor.

**Morgott reference:** Healing or lengthy casts at vulnerable distances can provoke fast ranged or advancing pressure, but he is not guaranteed to react every time. [S1] [S4]

**Unreal Engine 5.5 translation:** Only consider committed flask/cast after observable startup; add positive latency, LOS, range, travel and cooldown, and defer until executor free.

**Verification / acceptance:** Test instant/long heal at each range with and without LOS and while boss is mid-combo; report probabilities.

#### BOSS-PHS-005 — Anti-cheese with counterplay  ·  Evidence R

**Checklist requirement:** Kiting, rear camping, guard, terrain and wall traps receive bounded readable responses or reset.

**Morgott reference:** Tail whip addresses rear positioning; spears/daggers address distance; rain and geysers reshape arena movement, giving counterplay for overly safe habits. [S1] [S4]

**Unreal Engine 5.5 translation:** Use bounded, telegraphed counters to rear camping, kiting, repeated guard and terrain abuse; never auto-correct strike trajectory into player.

**Verification / acceptance:** Repeat each exploit attempt 20 times; counters must be visible, avoidable and not force an infinite punish chain.

### Debugging, QA, presentation and optional networking

#### BOSS-QA-001 — Runtime overlay  ·  Evidence U

**Checklist requirement:** Debug view exposes phase/state/instance/context/attack/montage/tracking/window/gate/cooldown/pressure.

**Morgott reference:** Morgott’s actual game does not expose a developer overlay of combat state to players.

**Unreal Engine 5.5 translation:** Add optional debug HUD of target distance, sector, phase flags, attack instance, montage, active hit windows, cooldowns and recovery.

**Verification / acceptance:** During fights compare HUD values against ground truth traces and events.

#### BOSS-QA-002 — Structured event log  ·  Evidence U

**Checklist requirement:** Decisions, commits, windows, contacts, defenses, branches, interrupts and transitions use stable IDs/times.

**Morgott reference:** No public structured runtime event log reveals private AI state.

**Unreal Engine 5.5 translation:** Emit event logs keyed by encounter/attack/branch ID with monotonic timestamps, contextual inputs, collision hits and aborts.

**Verification / acceptance:** Correlate a single multi-hit string from selection to attack end across serverless runtime logs.

#### BOSS-QA-003 — Reproducible scenarios  ·  Evidence U

**Checklist requirement:** Seed, starts, player script, time, phase and IDs are recorded.

**Morgott reference:** Player recordings can show repeated fight patterns, but they are not deterministic seeds of FromSoftware AI.

**Unreal Engine 5.5 translation:** Record seeded decision RNG, player replay scripts, starting phase/position, cooldowns and version; support deterministic automation trials.

**Verification / acceptance:** Replay same scripted player trajectory twice and compare selected action sequence.

#### BOSS-QA-004 — FPS and time-scale parity  ·  Evidence U

**Checklist requirement:** 30/60/120 FPS and supported time scales do not change hit count, cleanup or legal decisions.

**Morgott reference:** No reliable public test proves Morgott’s internal 30/60/120 FPS parity or time-dilation safety.

**Unreal Engine 5.5 translation:** Run frame-rate capped automated cases for charge, sweep, grab, rain, phase transition and stance break; compare hit counts and decision legality.

**Verification / acceptance:** Execute 30/60/120 FPS plus induced hitch; no unjustified duplicate/missed damage or orphaned state.

#### BOSS-QA-005 — Performance bounds  ·  Evidence U

**Checklist requirement:** Utility is gate-driven; traces run only while active with bounded samples; packaged frame cost is profiled.

**Morgott reference:** Exact CPU cost of Morgott’s combat decision evaluator and collision system is not public.

**Unreal Engine 5.5 translation:** Evaluate utility at events, not every tick; trace only while hit active; bounded substeps and pooled projectile/hazard effects.

**Verification / acceptance:** Unreal Insights packaged runs across low/high frame settings and demanding Phase 2 hazards.

#### BOSS-QA-006 — Camera/readability  ·  Evidence O

**Checklist requirement:** Boss target point, camera collision and framing keep release cues/weapon threats visible.

**Morgott reference:** Long weapon swings and overhead attacks require readable camera framing; even this polished encounter can sometimes crowd the camera at close range. [S1] [S4]

**Unreal Engine 5.5 translation:** Ensure lock-on point, camera collision and arena edge positioning keep release cues in frame; adjust own boss scale and effects as needed.

**Verification / acceptance:** Capture camera from 8 compass bearings at near/far distances during huge hammer and bloodflame effects.

#### BOSS-QA-007 — Accessible feedback  ·  Evidence U

**Checklist requirement:** Shake/effect reduction and non-color-only audiovisual cues preserve attack distinctions.

**Morgott reference:** Accessibility settings and non-color-only cue completeness cannot be inferred from Morgott gameplay guides alone.

**Unreal Engine 5.5 translation:** Provide distinctive poses/audio/shape cues separate from holy-gold vs blood-red colors, with optional camera-shake/effect reductions.

**Verification / acceptance:** Test color-blind filters, low VFX, no audio and constrained camera; moves remain distinguishable.

## P0–P8 application roadmap for your existing boss

| Phase | Goal | What Astra should request from Claude / Antigravity |
|---|---|---|
| **P0** | Evidence capture and active system audit | Claude: inspect active C++/BT/Blueprint execution, real Montage gates, attack data and damage paths. Antigravity: visual timing, silhouettes and animation-hit alignment. Astra: reconcile observed behavior with requirements; mark hidden internals unverified. |
| **P1** | Telegraph and hazard readability | Prioritize visible shockwaves/ground hazards, readable thrust-versus-sweep cues, material visibility and packaged build evidence. |
| **P2** | Attack lifetime and event reliability | Unique instance assigned before Montage play; validated Notify lifecycle; hitch, cancel, death and timeout tests. |
| **P3** | Damage defense consistency | Separate strike, sweep, burst, persistent hazard and grab policies with consistent iframe, guard, posture and dedupe rules. |
| **P4** | Attack geometry and coverage | Validate true weapon trajectory, interior traces, projectile lanes, stagger opportunities and attack eligibility. |
| **P5** | Contextual combos and punish windows | Codify legal branches and gates, locked strike direction, whiff/follow-up recovery and testable safe counterattacks. |
| **P6** | Movement and smart selection | Improve range bands, action awareness, anti-repeat, reaction latency, purposeful spacing and no-candidate fallback. |
| **P7** | Pressure and threshold escalation | Use purposeful late-fight unlocks, active hazard management and readable aggression changes, while preserving the project design freeze. |
| **P8** | Package/build/runtime QA | Validate 30/60/120 fps behavior, recorded fight scripts, camera/readability, packaged performance and owner gameplay evaluation. |

## Targeted encounter test cases (minimum)

| ID | Setup | Observation | Pass criterion |
|---|---|---|---|
| T01 | Frontal close attack | Player remains close in front after sword opener | Frontal legal follow-ups only; log gate and valid choices. |
| T02 | Rear escape during charge | Player rolls behind during spear charge | Committed charge does not curve unnaturally; rear branch/recovery chosen at gate. |
| T03 | Heal punish feasibility | Start flask in front at near/mid/far | Reaction only after action visibly commits, with delay and feasible follow-up. |
| T04 | Dagger anti-greed | Stand close and repeatedly attack | Dagger can appear when eligible, but does not guarantee an unfair instant counter. |
| T05 | Tail anti-rear-camping | Remain behind for multiple sword loops | Tail/reorient counters occur with readable cues and real recoveries. |
| T06 | Hammer finisher | Bait overhead hammer then dodge side | After known ender player can land an intended punish, no hidden cancel. |
| T07 | Swords rain lanes | Cross ~80% threshold; move between falling lanes | Fixed lane cue is consistent with the damage volumes and remaining safe ground. |
| T08 | Blood transition | Cross ~60% while staggered or in combo | One legal phase transition; no overlapping hits or repeat transition. |
| T09 | Geyser locality | Trigger ground impacts in phase two | Local eruptions only damage their displayed areas, cleanup after finish. |
| T10 | Bloodflame grab release | Be caught then interrupt with death/reset | Player regains controls; capture identity and damage are consistent. |
| T11 | Late rapid string | Cross ~30% threshold and run long seeded fights | Late attack becomes eligible but does not need to fire immediately. |
| T12 | Stance-break authority | Break posture at active hit window | Attack traces close, one stance break, valid critical window. |
| T13 | Frame-time hitch | Inject 100ms hitch during multi-hit spin | No skipped required hits, duplicate contacts, stale Notify callbacks. |
| T14 | No-candidate fallback | Disable all attack candidates or move player off NavMesh | Purposeful face/approach/reacquire/reset, no infinite reevaluation. |
| T15 | Camera readability | Fight at arena border during hammer/sword rain | Attack release remains visible enough to support dodge choice. |
| T16 | Recovery vs weapon speed | Time punish with fast and heavy player weapons | Document actual valid punish window by starting distance and startup. |

## Recommended UE asset / component layout

```text
Boss/
  Data/DA_BossCombatProfile, DA_Moves/, DA_ComboGraph, DA_PhaseRules
  AI/BP_BossAIController, BT_Boss, BB_Boss, UtilitySelection
  Components/BossContext, BossDecision, BossAttackExecutor, BossHitResolver
  Components/BossMovement, BossPosture, BossPhase, BossDebug
  Animation/ABP_Boss, Montages/, Notifies/, MoveCards/
  Effects/HolyWeapons/, Bloodflame/, RainZones/, Geysers/
  Tests/Automation/, GameplayCapture/, Baselines/
```

These are **proposed module boundaries**, not an instruction to replace a functioning project implementation. Preserve existing framework ownership and map responsibilities onto current classes wherever practical.

## Known uncertainty and important non-equivalences

- The checklist describes **82 ideal design, engineering, and QA requirements**, not 82 capabilities proven to exist in FromSoftware’s game engine. A number of requirements are your engineering standards (atomic context snapshot, seeded RNG, idempotent abort, trace substeps, observability); none can honestly be reverse-asserted from normal gameplay footage.
- **Do not copy the old project audit statuses** (Implemented/Partial/etc.) into Morgott. Those ratings were assigned to your own Unreal boss and do not describe Morgott’s implementation.
- **Grab is applicable to Morgott**. Although the original current-project audit marked `BOSS-HIT-012` N/A, Morgott’s bloodflame skewer is an actual capture attack. Any Morgott-inspired boss should consider a robust grab life cycle if one is included.
- **Variable randomized delay is unverified.** A deliberate delayed strike is observable; RNG selecting hold duration is not established.
- **Phase thresholds are reported approximate unlocks.** Detailed fan research identifies ~80/~60/~30% HP but other general sources simplify phase two to 50%; interruptions and stagger affect when a threshold transition visibly occurs. Test reference footage before using frame-perfect thresholds.
- **Geometric shockwave vs geysers differs.** Morgott’s post-transition geysers are local bursts/hazards; do not misrepresent them as the continuous annulus requirement unless you are intentionally adding a different attack to your own boss.
- **Boss block/parry AI is not a documented signature Morgott mechanic.** He can be parried by the player, which is different from Morgott parrying player attacks.
- **Exact animation FPS, frame markers, hitbox coordinates, AI scores, cooldown clocks and internal system structure are unverified.** Community-reported timings are encounter observations; this guide deliberately avoids inventing exact frames.

## Source notes

- **[S1]** Recycle, “Morgott – The Omen King | A Comprehensive Guide” (Steam Community, detailed community combat observations, updated 2026). https://steamcommunity.com/sharedfiles/filedetails/?id=2982878937
- **[S2]** Eldenpedia / wiki.gg, “Morgott, the Omen King” (community moveset, phases, arena). https://eldenring.wiki.gg/wiki/Morgott,_the_Omen_King
- **[S3]** tarnished.app, “Morgott, the Omen King” (combat stats, parries, stagger, thresholds). https://tarnished.app/enemies/morgott--the-omen-king
- **[S4]** Neoseeker, “Morgott, the Omen King – Elden Ring Walkthrough” (moves, counterplay, phase two). https://www.neoseeker.com/elden-ring/Bosses/Morgott_the_Omen_King
- **[S5]** EIP Gaming, “How to Beat Morgott, the Omen King” (move lists and punishability examples). https://eip.gg/elden-ring/guides/how-to-beat-morgott-the-omen-king/
- **[S6]** Original project checklist: Boss_83_Combat_Requirements_Audit.md (user-provided; source for the 83 IDs and criteria, network omitted). Boss_83_Combat_Requirements_Audit.md

**Reproduction guidance:** Original conceptual diagrams are included in the `diagrams/` directory. This document paraphrases source gameplay observations and does not reproduce proprietary Elden Ring meshes, textures, animations or code. Use your own boss art and animations when implementing.
