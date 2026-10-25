# D05 — Costing the eight now-required rows

2026-10-25. CI-P0-D-01 follow-up task1, C-96/C-98. Codex proposal for Claude/owner review. **All83 rows must end IMPLEMENTED with evidence; no N/A remains.** This supersedes D03's candidate-N/A/final-disposition language without editing Claude's register or historical audit. No implementation starts from this costing.

## Basis, scope and estimate convention

Binding direction: DATA_DRIVEN_ARCHITECTURE_GATE.md section0 G-2, C-96 and C-98. Exact requirements: Reference/06_REFERENCE_REQUIREMENTS.md and Reference/10_EXISTING_BOSS_AUDIT_CHECKLIST.md rows AWR-008, SEL-004/008, ANM-003/006, HIT-012, DEF-005, QA-008. The corresponding source chapters03/05/06/10/11/19 were read. Their illustrative coefficients, thresholds and timing examples are not approved balance values.

Small = bounded shared policy plus data and focused tests with no new actor lifecycle. Medium = shared state/selection/timeline capability and multiple boundary tests, modest content. Large = coupled actors/movement/defense or authority plus new content and substantial integrated tests. These are relative engineering/content/verification sizes, not calendar promises; pack extension feasibility, required animation quality, test tooling and networking experience remain unknown. Shared prerequisites are counted once, then incremental work per row is identified. “Smallest conforming” preserves every clause; no placeholder toggle, empty profile, never-selected move or conditional feature left disabled counts as implemented.

DD-1 only introduces behavior-identical storage/bindings/shadow data. Runtime fixes and new mechanics below belong to approved P1-P7 scopes, with final proof at P8. Adding fields during DD-1 must not activate them. The owner has approved direction/order; Claude brings these sizes and concrete scope to the owner, not a new request to waive any row.

## Summary

| Requirement | Size / main reason | Shared runtime mechanism | Content / authoring required | Principal stage |
|---|---|---|---|---|
| BOSS-QA-008 server authority | **Large, highest uncertainty**: end-to-end ownership and two-client synchronization cross every existing single-player path | Authority-gated request/decision/resolver/cooldown/posture/phase; replicated action state and events; target/member IDs; resync | Replication-ready participant profiles and test encounter; synchronized animation/cue bindings | Cross-cutting design now; P2/P3/P6/P7 integration; P8 network suite |
| BOSS-HIT-012 grab fail-safe | **Large**: two actors, controls, collision, safe placement and every exit | Shared capture/paired-action executor with authority, target reservation and idempotent release | Boss grab tell/capture/miss/paired damage/release clips and query/alignment/defense data | P2/P3/P4 core, P5 recovery, P8 proof |
| BOSS-ANM-003 bounded variable hold | **Medium**: section traversal, deterministic early choice, cues and clock semantics | Shared prechosen variant/hold controller and bounded watchdog | Short/long hold variants or bounded looping section with identifiable release cue | P1/P2/P5 and phase data P7 |
| BOSS-AWR-008 soft adaptive memory | **Medium**: observable event provenance, per-target history/decay and score integration | Bounded capped decaying feature accumulator feeding preferences | Per-boss observation/decay/cap/bias profile and ordinary-action floor | P6; phase/reset integration P7 |
| BOSS-SEL-004 normalized utility | **Medium–Large**: new legal-gate planner above pack executor, not editing three weights | Hard-filtered comparable feature scoring, deterministic near-best selection and trace | Per-move curves/weights/risk/opportunity/family/phase data | P2 request seam, P6 selector, P7 tuning |
| BOSS-SEL-008 empty-pool fallback | **Small incremental / Medium integrated**: safe bounded movement and retry depend on valid context/nav | Finite purposeful fallback task with timeout, backoff, completion and reset | Ordered fallback policy, desired range and retry/arena limits | P6 with P2/ANM motion handoff |
| BOSS-ANM-006 bounded Motion Warping | **Medium–Large**: real root-motion travel and collision/landing constraints | One shared early-window warp target owner, clamps/path checks/cancel cleanup | At least one actually used travel clip/window/target/cap/fallback profile | P2/P4/P6; P8 moving-target/network tests |
| BOSS-DEF-005 fair boss defenses | **Large**: three defense families, resource budget, reaction opportunity and counterplay | Shared guard/parry/dodge actions through same request/resolver/recovery gates | Directional guard, timed parry, dodge tells/animations/windows/cost/cooldown/recovery profiles | P3/P4/P5/P6, phase tuning P7 |

## 1. BOSS-QA-008 — Authority and multiplayer proof

Required clauses are not satisfied by declaring the game single-player. Reference checklist line131 asks server authority, replicated attack ID/start time/section/target/phase and montage sync; the source chapter19 also requires server-owned decisions, damage, posture and cooldown, per-victim hitsets, legal retarget gates, disconnect/death cleanup and listen/dedicated tests with packet simulation.

Smallest conforming design: one server-authoritative encounter/runtime works in standalone/listen/dedicated modes. Server allocates Actor/Encounter/Generation/Action/Stage/Effect identities, evaluates eligibility/choice/phase, confirms damage/posture/status and consumes cooldowns once. Clients receive selected Move/Variant, authoritative server start time, section/loop epoch, committed target/snapshot or warp transform, phase/transition and terminal/capture events. Reconcile presentation to server time without replaying authoritative damage; late relevance/join receives a coherent snapshot, not just a one-shot multicast. Clients cannot choose hit victims, redirect targets mid-active or authoritatively set HP.

Data additions: authority/replication policy reference, content/schema version/hash, stable participant IDs, network presentation timing tolerance, correction policy and supported clock bases. These configure shared code; data alone cannot supply networking safety. Local input/dodge feedback may be predicted, but defense outcomes must be reconciled with server timing/movement. Choose and document the defense reconciliation/lag policy before testing; do not introduce ad hoc client forgiveness.

Integration risk: current native GetPlayerPawn(...,0) callers in Tracker.cpp:175/447, HealPunish.cpp:99/154/232, Javelin.cpp:134, LowSweep.cpp:69, Shockwave.cpp:48/66 and resolver/player0 test wrappers are explicitly single-player. First-player/controller discovery and global time dilation/UI are similarly unsuitable as shared gameplay authority. Pack Blueprint ability/montage/attribute replication is not yet proven; immutable pack files may require project-owned adapters/subclasses and a server damage sink. If the pack has no safe authority hook, report a concrete adapter scope rather than claiming replicated metadata fixes the damage path. No host migration requirement is added unless supported/approved.

Proving test: listen server with two remote clients **and dedicated server with two clients**, baseline/80ms/150ms RTT and stated nonzero packet-loss/reordering conditions; document whether tool settings are RTT or one-way delays. Compare causal server/client traces, action/section/phase and visible commitment within an explicitly approved tolerance. Reject client-forged hit/retarget/start requests; simultaneous contacts/waves affect each victim once; death/reset/disconnect during windup/warp/grab/release clears locks and stale events; cooldown/phase/posture change only once on server; clients joining or regaining relevance reconstruct the current action without duplicate damage. Local Boss01/regression behavior remains unchanged in standalone.

Dependencies: participant bindings DD-1 step2, timeline/identity P2, shared resolution P3, warp/grab actor lifecycle, selector P6, phase P7. Design IDs/time domains **now** to avoid another migration; enable network behavior later through a specified gate. P8 requires actual runs, not replication property inspection alone. Largest unknowns: pack authority seams, root-motion/section sync, client dodge reconciliation, remote UI/input ownership, and dedicated-server execution. No shrinking to a server-side boolean or a two-local-pawn test.

## 2. BOSS-HIT-012 — Boss grab

A player-initiated riposte is useful reuse but is not a boss-initiated grab. Required lifecycle: target validity and directional capture query, defense/capture eligibility, paired alignment/animation, explicit input/motion restriction, once-only damage, safe release/throw and restoration at every interrupt/death/reset stage.

Smallest conforming design: add one readable boss grab as a data-driven move exercising a shared Capture/PairedAction executor. Pre-commit telegraph and capture volume permit declared counterplay; miss follows authored recovery. On eligible contact, atomically reserve one victim for the originating action/generation, validate facing/height/path, stop conflicting movement, save exact owned control/collision changes and start both animation variants. Damage is an identified marker/event and can occur only once for that capture. Release validates both actors and safe collision/navigation placement; failure takes a bounded safe fallback. Owner-approved defense policy specifies guard/parry/dodge immunity interactions. One boss grab is the minimum feature; multi-victim concurrency must still reject duplicate capture safely.

Data: CaptureShape/Window, victim/attacker animation bindings and align transforms, victim bounds/skeleton constraints, allowed defenses, capture/align/release timeouts, damage marker, release displacement/path checks, miss/default recovery, interrupt matrix. Do not encode a victim-specific component class or arbitrary Blueprint per grab.

Proving test: valid capture, early/late/side/out-of-range miss, each declared defense, obstructed alignment/low ceiling/wall/ledge, victim dies/disconnects, attacker dies/reset/phase/break, interrupted either montage or missing marker at capture/alignment/damage/release. Both actors regain correct controls, movement/collision/input ownership, valid placement and no lingering damage; repeat capture and simultaneous competing grabs cannot duplicate or steal reservations. Use two-client tests once QA-008 is active. Capture/player-camera review must show tell and counterplay, and grab miss must be punishable.

Cost drivers: new paired content and victim compatibility, control/input-release safety (existing riposte risk), physics/placement, server reservation and authority. Implement core cancellation contracts before the grab, not a standalone per-boss class. Existing A1-A6 are preserved; adding this move changes the catalogue and needs an explicit move slot/frequency/presentation proposal in the later gate.

## 3. BOSS-ANM-003 — Bounded variable hold

Smallest conforming design: two authored short/long hold variants **selected at accepted windup start before commitment**, with declared minimum/maximum, a stable visible hold, reliable release cue and bounded release path. Random/weighted choice uses the action seed recorded at that instant; later player rolls cannot alter the chosen duration. A bounded looping section is acceptable if loop count/exit is chosen ahead and clock/section traversal is deterministic. A single fixed hold or an indefinite AI-controlled ApexHold does not satisfy the variable-delay clause.

Data: hold VariantId/section sequence, duration/loop bound and clock, selection/commit marker order, cue lead, exit seam, maximum action real duration and abort policy. Reuse animation-compiled timeline P2; do not run independent timers that drift from montage rate. Keep current fixed A2 legacy timing in DD-1; enabling new holds is a later behavior/content change.

Proving test: each variant at supported rates/FPS/time scales/hitches, inputs rolled before/after choice and throughout hold, target loss/section jump/early interrupt/death/reset. Same accepted seed/context yields same duration independent of post-choice input. Cue precedes actual damage on every variant; no stranded hold, duplicate release or hit after abort. Include marker loss/watchdog. Existing .60phase etc is unrelated and stays unchanged.

Cost medium: authoring seams/cues and timeline ordering are the work; no new effect executor is necessary after P2. Dependencies P1 readability, P2 event traversal/action identity, P5 recovery/punish, phase weighting inP7. No owner-approved specific hold times are invented here.

## 4. BOSS-AWR-008 — Capped decaying adaptation

Smallest conforming design: one bounded memory store **per encounter target/actor** for observable action/state events over a declared recent horizon (roll direction, committed heal, guard dwell/rear dwell/ranged activity as appropriate). Features decay with a documented clock/kernel, contributions and accumulated values are capped, and memory adjusts utility preferences rather than changing hard eligibility, an in-flight attack or committed geometry. Normal action/neutral opportunities retain a nonzero floor. Reset/reacquisition policy and phase carryover are explicit.

Data: observable feature/binding, accumulation/decay/cap, move/family bias weights, ordinary-choice floor, event dedup key, memory budget and reset policy. No raw future inputs, no machine-learning subsystem required; deterministic accumulators satisfy the full row when tested. This is distinct from repetition history of the boss's own moves (SEL-007).

Proving test: repeat each selected player behavior, export feature/bias curve and selected eligible candidates; stop behavior and verify decay toward baseline; saturate a feature to prove cap, duplicate an observation to verify dedupe, reset/switch target/two instances to show isolation, change phase under each carryover rule. Ineligible moves never become eligible and changing target behavior after commit cannot change current attack. Each main build retains legal counterplay/ordinary actions in integrated tests.

Cost medium: collection reliability and time-base/target provenance, coupling to normalized utility and fairness tests. Reuse P2 IDs/events and P6 snapshot/utility; P7 integrates phase. DD-1 carries inactive profile only, not activation or tuning.

## 5. BOSS-SEL-004 — Normalized utility

Smallest conforming design: one shared selector evaluated only at legal neutral/branch gates. Apply hard eligibility first; score eligible moves using documented comparable range, signed angle/tracking capability, opportunity, spacing, phase and variety features. Normalize each term and define weighted combination/penalties and score range; record all rejected reasons and feature/score totals. Choose deterministically among sufficiently good candidates with seeded bounded noise/weighted near-best draw; the exact reference coefficients are examples, not a requirement to copy.

Data: per-term curves/weights/normalization domain, preferred range/angle, phase/pacing/history/adaptation profile refs, near-best threshold/noise/temperature/seed policy, move family and risk. Existing ordered pack BT can remain the lifecycle/execution backbone, but a shared project request/selection task must own content-driven choice; a25percent decorator or moving its threshold into data does not implement normalized utility.

Proving test: fixed context sweeps at min/preferred/max range, yaw wrap/cone edges, height/LOS/resources/cooldown/phase; monotonicity and bound/finite checks for each term, missing/zero/negative weights and empty pools. Dump candidate terms and chosen seed, replay exact contexts, verify no scores for invalid candidates and no selection while committed. Statistically observe only the declared selection policy on repeated seeded trials without converting one bot fight into a frequency proof. Test boss-specific profile changes and a canary without code changes.

Cost medium–large: scoring math is bounded; snapshot provenance, pack request interception, diagnostics/replay and integration/fairness dominate. Dependencies P2 pre-play token, P5 legal recovery/branch gates, P6 context/movement, AWR-008 adaptation; P7 phase tuning. Shared foundations can reduce incremental cost, but no budget assumes all uninspected pack checks are already usable.

## 6. BOSS-SEL-008 — Purposeful no-candidate fallback

Smallest conforming design: when all moves fail eligibility, select a declared bounded action: safe reorientation/approach/retreat/spacing or purposeful wait with retry time; if target/path stays invalid beyond bound, controlled reacquisition/leash/reset. Record why no moves were legal, fallback goal/reason, timeout and completion. No per-frame tight retry, permanent wait, target teleport or fallback attack bypassing eligibility.

Data: ordered allowable fallback kinds, desired range/facing/LOS, nav/arena checks, maximum duration/displacement, retry/backoff and stable goal/hysteresis, reset policy. Shared finite task code is enough; EQS is optional implementation technology, not a waived behavior.

Proving test: all moves on cooldown, missing assets, exhausted resources, invalid phase, occluded/outside/vertical/unreachable target and zero-utility cases; assert bounded query/decision count, safe movement, timely return to legal gates or declared reset. Deny move start during fallback lock, interrupt with death/reset/phase, restore conditions mid-wait and verify legal re-entry without duplicate selection. Test a genuinely empty definition is rejected versus a temporarily empty eligible set that runs fallback.

Incremental size small after selector/nav ownership exists; integrated medium when those prerequisites/telemetry are absent. Depends on P2 cleanup/gates, P6 target/motion/nav context and SEL-004; P5/P7 pressure rules remain in force. Bounded fallback safety must not be cut as a cheaper “wait then try every tick” implementation.

## 7. BOSS-ANM-006 — Bounded Motion Warping

No N/A means an actual supported warp use must be exercised, not merely a profile set to Disabled. Smallest conforming design: one existing/new project-owned directional travel move with meaningful root motion and an authorized **early-only** warp window. Shared motion owner validates target transform/displacement/rotation/Z/path/landing bounds, samples/updates only within allowed gates, freezes by commitment and hands movement back on completion/abort. Invalid wall/stairs/ledge/off-nav target declines start or uses a declared safe bounded fallback. No homing/retargeting across active damage.

Data: animation/skeleton/root-motion binding, window/target role, one-shot or early-refresh rule, caps per axis/rotation, collision/nav/landing validation, warp strategy, fallback and cleanup. Do not require all duel clips to acquire root motion or replace the pack leap before its motion path is known. Shared UE capability integration availability/plugin settings and compatible root-motion extraction need Claude's inspection before choosing implementation; no engine setup claim is made by this design.

Proving test: target strafes/perpendicularly crosses behind/moves beyond cap, wall/corner/ceiling/stairs/ledge/off-nav/invalid landing, target loss/death and section jump/slowmo/hitch/cancel/reset. Capture committed target and actual actor trajectory; translation/rotation/Z stay bounded, no post-commit updates, one motion owner and no movement through blockers. Validate tick/animation synchronization and server/client target/time alignment under QA-008.

Cost medium–large: reusable target/window math plus animation/root-motion content, physics and pack/character-movement seams; visual foot/sliding/silhouette review required. Depends on participant data DD-1step2, timeline/window IDs P2, geometry P4, motion ownership/nav P6. P8 canary should use the shared capability in data, not a hand-coded one-boss implementation.

## 8. BOSS-DEF-005 — Fair guard/parry/dodge

Do not reduce “block/parry/dodge” to permanently enabling one invulnerability tag or a perfect counter. Smallest conservative conforming design supports **all three defense families** as data-driven actions with actual exercised content: directional guard with resource/chip/guard-break rules; timed parry against explicitly parryable contacts; dodge with startup, finite protected interval, travel/clearance and recovery. If Claude believes the reference's slash denotes alternatives, obtain an explicit owner interpretation rather than silently shrinking the costing. This estimate includes all three.

Shared runtime uses observed player commitment and reaction latency/budget/cooldown/availability, never raw input prediction; actions go through legal request and cancellation/recovery gates. Facing/timing/resource checks run at resolution, failed/late/rear/insufficient-resource defenses can be punished. Death/reset always clear window ownership; posture/HP remain independent and an armor window cannot erase intended break semantics.

Data: defense family, facing cone, startup/active/recovery, stamina/other cost, cooldown, allowed hit/move tags, chip/guard-break/parry response, dodge motion/iframe window, reaction delay/weight/failure budget, punish recovery and presentation. No exact new timing/cost value is approved by this estimate.

Proving test: repeat player light/heavy/jump/charged attacks from front/flank/rear at early/on-time/late timings, resource depletion/cooldown/busy states and each declared parryable/unparryable policy. Confirm successes and deliberate failure cases, resource accounting once, finite immunity, visible tell and a reachable punish after failure; multiple body contacts/pack-native-special damage paths give consistent outcomes. Interrupt/phase/reset/death while guarding/parrying/dodging, two targets/clients and path blockage cannot strand tags/input/motion. Main-build counterplay and no perpetual-defense loops require integrated P8 trials.

Cost large: selector reactions, shared resolution, new defense presentation/animations, meaningful failure/punish and player attack classification are coupled. Dependencies P2, P3 damage/defense, P4 geometry/motion, P5 recovery, P6 reaction budgeting, P7 phase. Pack has defense assets/classes but their availability is not proof these semantics already work for this boss.

## Sequencing and owner-facing size conclusion

1. DD-1 preserves storage/API behavior only. Add IDs/versions/context boundaries with future authority in mind; no feature enablement.
2. P2 establishes pre-play transaction, section/window/gate identities, declared cancellers, cleanup and watchdog. ANM-003 can reuse this; paired/grab and network action state consume it.
3. P3/P4 unify per-victim outcomes/defense/query/motion safety. Add bounded warp and capture core only with approved move/content specs.
4. P5 recovery/punish gates precede new defenses and combo/hold tuning.
5. P6 context + eligibility + utility + bounded fallback + adaptive memory share one snapshot/history/event contract. P7 changes profiles/phase, not the shared algorithm.
6. QA-008 is cross-cutting: implement/verify authority seams alongside each relevant stage, then P8 runs listen/dedicated two-client latency/loss plus existing standalone suite. Delaying all networking design until P8 risks reworking every earlier owner.
7. P8 proves all eight and all remaining75; no vacuous disabled-mode or schema-only IMPLEMENTED disposition.

The added scope is **not eight small data rows**: networking and paired capture/defenses are new integrated capabilities/content/test tracks. No summed effort/day estimate is defensible before pack authority and adapter feasibility are known. Claude should present this full size, dependency/risk and conservative all-three-defense interpretation for owner re-confirmation while retaining the no-N/A target. No row or test is removed to lower cost.

Validation: requirement/reference text and present single-player/native seams inspected; estimates are engineering judgments, not tests run. No Source/Config/asset/script/pack edits, build, engine/PIE/network test or commit/push by Codex.

