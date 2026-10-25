# D06B — gate and E-005 through E-008 independent review

Codex, 2026-10-25, C-98/3. Verdict: retain the measured symptoms with corrections below; **not P0 acceptance, not a proven A2 canceller or production adapter**. Section 0 owner decisions govern over obsolete requests elsewhere. Docs-only review; no new editor/probe/test execution.

## G1 — high: the gate still contains superseded instructions

DATA_DRIVEN_ARCHITECTURE_GATE.md:13-22, :56-58 and :66 retain proposed N/A exemptions and requests for G4/G5 approval, contrary to section0. Mark these sections explicitly historical/superseded; do not let agents remove affected required features under the old “if rejected, remove the step” rule. All 83 rows remain required; D05 supplies the eight-row costing. G4/G5 remain denied; unresolved causal or capture evidence is recorded honestly, not permission to add the denied tools.

G3 approval is a bounded scratch experiment, not proof the experiment succeeded. Gate:39 “G-3 proves (a)” must become “G-3 permits testing (a).” E-006:18-19 also needs its historical approval status updated. Specify a temporary PIE-instance EnemyInfoRef override, readbacks, cleanup and scratch paths before execution; do not persist a placed-level/map override under “new scratch assets only.” If a saved map change is indispensable, Claude must resolve that scope conflict with the owner first. Codex performs no such operation.

## E-005 — medium: distinguish nine pre-window cuts from ten pre-recovery terminations

The eleven tabulated events are nine Windup terminations, one Active termination at1.99 (window1.93-2.11), and one Recovery replacement at2.80. Thus **9/11 stopped before the tracked damaging window; 10/11 ended before reaching Recovery**. Do not call all ten “before the damage window.” Five of six first observed A2s were0.03-0.06; retain as a six-fight sample count, never a frequency estimate or future deterministic test ratio. The recovery case was “replaced by another attack,” not “montage stopped,” and2.80 is not the declared3.14 recovery endpoint. Correct the table's common stop-reason heading and “normal recovery end” wording (E-005:5-21; gate:28; STEP0 behavior table).

Independent raw confirmation: Saved/Logs/OneBossFight.log:20560/20595 (A2 defaults), :22245/:22355/:22464 (B warm), :23045/:23130 (T1), :26939/:27095 (T4), :28749 (T6), :38875 (T9). These recover all eleven rows. Saved log is mutable; Claude should freeze/hash the relevant slices rather than rely indefinitely on these line numbers. T1/T4/T6/T9 also have frozen exports. B warm's export explicitly arms wake0/telegraph0, unlike E-005:3's blanket wake1/telegraph0.4 header: label configuration per run, not all as defaults.

T4 frozen export:26 through its last first-instance trace at18.624 supports montage stopped/currentNone while CloseRare remains activated/animating; the first stopped tick is17.236. The directly observed persistence after that tick is about1.388s, roughly1.4s, not an established strictly greater-than1.4s lower bound (the longer1.448s includes initial playing ticks). Keep the ongoing-ability symptom and exact interval; do not infer exact end or next-selection delay from the trace limit. A no-hit outcome does not imply the full damage window never ran: a miss is possible.

E-005:29 “No native code ... can be the caller” exceeds the evidence. The inspected direct Montage_Stop sites and absence of their expected logs narrow candidates; they do not prove a causal caller, exclude indirect native-triggered Blueprint behavior or guarantee instrumentation coverage. Keep “no identified direct native caller in inspected sites.” CurrentState is a base-class object, not the state tag; neither a1s service nor equip blend is a proven cause. G4 stays denied. The symptom can be preserved by leaving the execution path untouched while DD-1 observes it; do not implement intentional early cancellation to force parity.

## E-006 — medium: quantified edge residue and parser contamination

All24 hashes listed in E-006 matched independently (19 BP exports,3 edge listings,2 scripts). This validates artifact identity, not graph correctness. Counted unresolved target endpoints in the actual edge listings:

| Listing | Total printed edges | Unresolved |
|---|---:|---:|
| EnemyMeleeAttack CanActivate |19|13|
| MeleeBase CanActivate |25|10|
| TryActivate Activate Abilities |26|11|
| Total |70|34|

This is34/70, not “about a quarter” (E-006:9). More seriously, the listed Activate Abilities FunctionEntry carries ReceiveAbortAI/ReceiveExecuteAI as well as its own title and several unrelated output pins. `bp_t3d_edges.py` resolves property blocks by the first node name across ALL graphs, retains stale node/current-graph state and resolves target only by pinID while ignoring the LinkedTo node reference. Reused K2Node names can merge graphs; this is a parser limitation in addition to duplicate bodies. Treat assembled chains as provisional until the specific edges are checked against graph-qualified raw object paths. No inference about exact activation success branch, abort path, ability ordering/filter or selector frequencies from this listing.

The controller's raw EventGraph at BPX_BP_BaseAIController.t3d:2009-2054 independently links MasterAI -> GetEnemyInfo ReturnValue -> BehaviorTree self, then BehaviorTree output -> RunBehaviorTree.BTAsset. That narrow **tree-selection route** is supported without trusting the broken aggregate parser. It does not prove generic C++ tasks/ability invocation, veto-before-play, abort semantics or all competing selection entry points. Scratch proof must record actual selected info/tree/blackboard/controller, task entry/exit and no persistent mutation. A later accepted-action adapter still needs an entry-point closure inventory and a true pre-play proof; do not silently move its behavior into DD-1 hydration.

## E-007 — numeric release supported, visual pose still unverified

Independently found today's raw driver lines in Saved/Logs/OneBossFight.log:112092-112093 (one release/instance; commit and active0.47), :112096 (heading drift0), :147036 (31/31). Tracker source declares0.45; driver source accepts broad commit/active ranges rather than an exact0.47 invariant. Accept this sampled mechanism result with the stated configuration, not a new feel/capture pass.

E-007:5 and gate:30 should say “0.05s nominal /0.07s observed after sidecar's intended0.40 marker,” NOT after a measured visual hand-release pose. No synchronized pose capture exists. At20fps one frame is0.05s:0.05-0.07s is one to1.4 frames, not “smaller than one frame.” It establishes no perceptual defect or approved retiming. Freeze/hash today's successful log slice and config alongside the report; an older failed gate line elsewhere is a different run and not a refutation of this pass.

## E-008 — medium: bounds-derived endpoint, circular angles and disconnected dip samples

Read the complete v2 probe and raw sample export; v1 remains obsolete provenance. The probe's local_tip selects the furthest end of the longest local AABB axis. This is a **bounds-axis endpoint estimate**, not a measured socket or validated physical blade vertex. Origin(0,0,71), extent(31,3.8,92.3), scale1.5 and transform support the computed point(0,0,163.3); the six named socket checks were false. They do not enumerate every socket, prove the mesh has zero total sockets, or ban socket use on all other weapons. “No tested trace/tip sockets on this visible component” is the supported wording until an actual socket count is read back.

The12 active samples support planar reach74..312cm, height-103..208 relative to capsule-bottom proxy and query380cm/inner60/height40. The68cm difference is against the **largest sampled estimated endpoint**, not a proven global reach bound, a measured collision-overreach amount, or a test of every point along the blade/query. Preserve the discrepancy candidate; captures and production contact geometry are still needed before P4 conclusions.

Independently recomputed relative angular differences from rounded raw XY and yaw using shortest circular delta in[-180,180]: approximately -51.1,-51.0,-68.8,-88.0,-105.4,-113.8,+169.5,+146.4,-166.1,+173.5,+124.5,+83.0 degrees. Therefore sampled absolute shortest error is about51..174 degrees, not194. Circular wrapping changes the late maxima; it does not erase the large mismatch. At74cm the angle is sensitive, but not mathematically undefined (the vector is nonzero). State rounding/evaluation-order uncertainty.

Below-proxy active samples are0.730(-14),0.754(-103),0.807(-12); **0.782 is +20**, so0.730-0.807 is not a continuous observed below-floor interval. Recovery negatives0.903-1.001 end before1.025, which is+2. A sampled endpoint below capsule bottom is not a collision/floor surface measurement or pixels. Smaller capsule half-height raises the reference and makes the computed negative height MORE negative, not less (E-008:10). Do not claim actual floor penetration before validating the ground plane and visible pose. AG's armature-origin offline heights cannot independently settle engine floor penetration, timing or cause; they use a different reference frame.

Gate:29 / STEP0 table “only reachable from a test hook” is too strong: this forced run and inspected native/BT/style paths establish no natural route found, not absence of every Blueprint caller of the public StartMove function. CAP-03 remains open under G5 denied. No geometry, offsets, animation, release time or selection is changed by these corrections.

## Disposition

Claude should propagate these narrower statements to the gate/baseline/reconciliation, retain all raw provenance and unresolved classifications, and keep approved architecture distinct from unproved adapter execution. All83 required; D05 cost confirmation outstanding. DD-1 can be planned as a behavior-preserving foundation with explicit legacy-versus-animation shadow mismatches; this review does not accept P0 or authorize P1.
