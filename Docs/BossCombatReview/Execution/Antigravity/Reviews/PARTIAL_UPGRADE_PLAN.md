# Partial Rows Upgrade Plan (v2.0)

> [!NOTE]
> **Status as of ledger version 3.14:** 13 of the 27 rows are now WITNESSED (`BOSS-AWR-001`, `BOSS-AWR-002`, `BOSS-AWR-005`, `BOSS-EXE-004`, `BOSS-EXE-007`, `BOSS-COM-002`, `BOSS-COM-003`, `BOSS-COM-005`, `BOSS-COM-007`, `BOSS-ANM-007`, `BOSS-HIT-005`, `BOSS-QA-003`, `BOSS-QA-004`); the table below is the ORIGINAL plan at commit `58352ae`; current PARTIAL ids: `BOSS-AWR-004`, `BOSS-SEL-008`, `BOSS-EXE-006`, `BOSS-COM-004`, `BOSS-ANM-002`, `BOSS-ANM-005`, `BOSS-HIT-008`, `BOSS-HIT-009`, `BOSS-MOV-001`, `BOSS-PAC-006`, `BOSS-PHS-004`, `BOSS-QA-001`, `BOSS-QA-002`, `BOSS-QA-005`.

## 1. Executive Summary

This document provides a concrete, grounded upgrade roadmap for all **27 canonical `PARTIAL` requirements** in `Docs/BossCombatReview/Execution/Antigravity/Ledger/witness_status_v3.json`.
Every row's title and ID are generated directly from the ledger to prevent title drift.
For each row, the ONE concrete missing observation needed beyond today's lines is specified relative to existing ledger notes and citations, and classified by execution authority:
- **Test-Only (Antigravity)**: 1 row (`BOSS-AWR-004`) can be graduated offline via pure C++ unit tests in `Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp`.
- **Engine Required (Claude)**: 26 rows require live Unreal Engine execution, PIE runs, level asset spawning, player pawn driver options, visual inspection, or GPU rendering.

## 2. Upgrade Matrix (27 PARTIAL Rows)

| ID | Title | Status | Missing Observation | Authority |
|---|---|---|---|---|
| `BOSS-AWR-001` | Target validity | PARTIAL | Live perception loop in boss character/controller detecting target death or despawn and halting offensive action in PIE. | Engine Required (Claude) |
| `BOSS-AWR-002` | Gate-time snapshot | PARTIAL | Live PIE run with lateral target displacement during windup proving trajectory commits strictly to gate snapshot angle. | Engine Required (Claude) |
| `BOSS-AWR-004` | Signed angle and hysteresis | PARTIAL | Hysteresis buffer implemented in `RPGBossMoveModel` and verified by unit test with yaw oscillating near cone boundary. | Test-Only (Antigravity) |
| `BOSS-AWR-005` | Vertical separation | PARTIAL | Live PIE run with target on an elevated platform witnessing selector refusal log: `[FrameworkProof] refusal ... reason=MoveModel.Vertical`. | Engine Required (Claude) |
| `BOSS-SEL-008` | No-candidate fallback | PARTIAL | Live PIE run witnessing boss execute purposeful neutral repositioning when selector returns `INDEX_NONE` without failing closed. | Engine Required (Claude) |
| `BOSS-EXE-004` | Stale event rejection | PARTIAL | Live executor log confirming rejection of late AnimNotify callbacks from an interrupted previous attack instance. | Engine Required (Claude) |
| `BOSS-EXE-006` | Idempotent abort | PARTIAL | Grab or AoE attack executor abort path implemented and verified with repeated abort producing clean recovery and zero duplicate events. | Engine Required (Claude) |
| `BOSS-EXE-007` | Watchdog | PARTIAL | Live executor telemetry logging watchdog timeout abort when montage end or notify end is suppressed. | Engine Required (Claude) |
| `BOSS-COM-002` | Gate after damage | PARTIAL | Live PIE proof witnessing combo branch gate opening during recovery window strictly after active hit window closes. | Engine Required (Claude) |
| `BOSS-COM-003` | Fresh branch context | PARTIAL | Live PIE proof with player shifted behind boss at branch gate, witnessing behind-the-boss branch selection. | Engine Required (Claude) |
| `BOSS-COM-004` | Explicit hit-confirm policy | PARTIAL | Live PIE telemetry observing Guarded and Parried branch selection (`outcome=Guarded` / `outcome=Parried`) during player defense. | Engine Required (Claude) |
| `BOSS-COM-005` | Single-use gate | PARTIAL | Live PIE proof injecting an anomalous duplicate gate trigger during active execution and logging its rejection. | Engine Required (Claude) |
| `BOSS-COM-007` | Default recovery | PARTIAL | Live PIE proof where target is within range but fails branch gate angle condition, witnessing clean transition to recovery. | Engine Required (Claude) |
| `BOSS-ANM-002` | Telegraph phases | PARTIAL | Live PIE log or anim notify probe formally asserting synchronized visual/audio telegraph cues during `[0, CommitSeconds]`. | Engine Required (Claude) |
| `BOSS-ANM-005` | Exclusive motion authority | PARTIAL | Explicit navigation velocity disablement lock in executor verified in PIE log during attack playback. | Engine Required (Claude) |
| `BOSS-ANM-007` | Notify-end independence | PARTIAL | Live PIE run with montage notify end intentionally omitted, proving attack finishes cleanly via fallback timer. | Engine Required (Claude) |
| `BOSS-HIT-005` | Query filtering | PARTIAL | Live PIE collision query telemetry explicitly logging filtered-out self capsule and dead target candidates during weapon sweep. | Engine Required (Claude) |
| `BOSS-HIT-008` | Central defense order | PARTIAL | Live PIE run with player in active shield block/parry stance, witnessing central resolver evaluate defense order before health damage. | Engine Required (Claude) |
| `BOSS-HIT-009` | Iframe completeness | PARTIAL | Live PIE sweep run with calibrated player dodge timing proving reproducible `RejectedInvulnerable` throughout iframe window. | Engine Required (Claude) |
| `BOSS-MOV-001` | Range-band policy | PARTIAL | Move card set authoring partitioning attacks across distinct range bands and live PIE validation logging appropriate band selection. | Engine Required (Claude) |
| `BOSS-PAC-006` | Neutral is purposeful | PARTIAL | Live PIE telemetry asserting zero active hitboxes (`activeHitboxes=0`) during neutral state intervals between attacks. | Engine Required (Claude) |
| `BOSS-PHS-004` | Fair heal punish | PARTIAL | Player flask drink perception reaction loop in boss character triggering heal-punish move selection in PIE. | Engine Required (Claude) |
| `BOSS-QA-001` | Runtime overlay | PARTIAL | Interactive or windowed PIE viewport screenshot capturing on-screen debug overlay rendering with non-black pixels. | Engine Required (Claude) |
| `BOSS-QA-002` | Structured event log | PARTIAL | Engine logging emitting production `[CARD_*]` tagged lines during combat execution in PIE. | Engine Required (Claude) |
| `BOSS-QA-003` | Reproducible scenarios | PARTIAL | Scripted replay harness executing fixed player inputs under fixed seed and asserting deterministic boss state progression across runs. | Engine Required (Claude) |
| `BOSS-QA-004` | FPS and time-scale parity | PARTIAL | Discrete PIE runs executed at fixed 30, 60, and 120 FPS witnessing invariant hit counts and damage totals. | Engine Required (Claude) |
| `BOSS-QA-005` | Performance bounds | PARTIAL | Packaged standalone build benchmark executed on RTX 2060 Super hardware recording frame time p99 <= 16.67 ms at 1080p. | Engine Required (Claude) |

## 3. Detailed Upgrade Requirements

### `BOSS-AWR-001`: Target validity

- **Ledger Status**: `PARTIAL`
- **Authority**: **Engine Required (Claude)**
- **Ledger Observable**: Boss AI halts attack execution or rejects candidate when player target is marked Dead, Destroyed, or off-arena.
- **Ledger Notes**: Unit playback guards test null target initialization refusal (runtime_tests:75) and resolver test rejects dead targets (auto_tests:173); full AI perception loop target validation and off-arena invalidation not yet wired.
- **ONE Missing Observation**: Live perception loop in boss character/controller detecting target death or despawn and halting offensive action in PIE.
- **Implementation & Evidence Plan**: Current citations (`Source/OneBossFight/Tests/RPGFrameworkRuntimeTests.cpp:79` and `Source/OneBossFight/Tests/RPGAutomationTests.cpp:173`) verify null target initialization refusal and damage resolver dead target rejection. Missing: live perception loop in `ARPGFrameworkBossCharacter` checking target validity on tick and aborting/rejecting attacks when target is killed or despawned in PIE.

### `BOSS-AWR-002`: Gate-time snapshot

- **Ledger Status**: `PARTIAL`
- **Authority**: **Engine Required (Claude)**
- **Ledger Observable**: AI state evaluator captures target distance/angle snapshot strictly at gate open, ignoring subsequent player repositioning during windup.
- **Ledger Notes**: Target range and angle are sampled into FRPGBossDecisionSnapshot at decision gate. In PIE shift proof (pie_shift2:1579, 1614, 1784), attack 1 runs against decision range 153.845 despite player pawn shift changing live range to 183.489; card execution executes without mid-action retargeting or trajectory abortion, and attack 2 samples the fresh range 183.489. Status is PARTIAL per C-543 honest limit: range snapshot isolation and absence of mid-action retargeting are witnessed live in PIE; angle snapshot isolation during execution is witnessed by construction / unit test.
- **ONE Missing Observation**: Live PIE run with lateral target displacement during windup proving trajectory commits strictly to gate snapshot angle.
- **Implementation & Evidence Plan**: Current citations (`Docs/BossCombatReview/Execution/Claude/B_SHIFT/pie_shift2/editor_raw.log:1579`, `Docs/BossCombatReview/Execution/Claude/B_SHIFT/pie_shift2/editor_raw.log:1614`, `Docs/BossCombatReview/Execution/Claude/B_SHIFT/pie_shift2/editor_raw.log:1784`, `Docs/BossCombatReview/Execution/Claude/B_SHIFT/pie_shift2/editor_raw.log:1858`) witness range snapshot isolation live in PIE. Missing: lateral target displacement during commit window proving boss heading angle snapshot isolation during execution without live retargeting.

### `BOSS-AWR-004`: Signed angle and hysteresis

- **Ledger Status**: `PARTIAL`
- **Authority**: **Test-Only (Antigravity)**
- **Ledger Observable**: TestMoveModelSelectsBestMatchingCandidate evaluates FrontConeDegrees; signed yaw boundary hysteresis tested against threshold angles.
- **Ledger Notes**: MoveModel tests (model_tests:60) verify FrontConeDegrees evaluation with signed yaw at -60 and +60 deg; hysteresis buffer on cone boundary not yet implemented.
- **ONE Missing Observation**: Hysteresis buffer implemented in `RPGBossMoveModel` and verified by unit test with yaw oscillating near cone boundary.
- **Implementation & Evidence Plan**: Current citation (`Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp:60`) verifies `FrontConeDegrees` evaluation at +/-60 degrees. Missing: hysteresis buffer margin on cone boundary in `RPGBossMoveModel` with unit test asserting stable candidate selection without oscillation.

### `BOSS-AWR-005`: Vertical separation

- **Ledger Status**: `PARTIAL`
- **Authority**: **Engine Required (Claude)**
- **Ledger Observable**: Elevation separation delta Z > threshold invalidates horizontal ground sweep cards.
- **Ledger Notes**: MoveCardSpec defines MaxVerticalDeltaCm (0 = no limit); live boss character populates Snapshot.VerticalDeltaCm = |Target.Z - Boss.Z| (boss_character:148); MoveModel::IsEligible enforces vertical limit with named refusal MoveModel.Vertical and snapshot domain bounds (move_model:28, 38). VerticalSeparation automation test (model_tests:211-220) proves same floor eligible (Z=0), exact limit eligible (Z=50), just above refused (Z=50.01), far above refused (Z=400), unlimited card ignores Z separation, negative/NaN/inf delta Z refused with MoveModel.SnapshotDomain, and invalid card limits (-1, NaN, inf) refused compilation. Status is PARTIAL per C-537 honest limit: unit model evaluation is 100% verified, but no authored proof card in the test maps sets MaxVerticalDeltaCm > 0 and no PIE target stands on an elevated ledge, so runtime selector refusal in live PIE is unwitnessed.
- **ONE Missing Observation**: Live PIE run with target on an elevated platform witnessing selector refusal log: `[FrameworkProof] refusal ... reason=MoveModel.Vertical`.
- **Implementation & Evidence Plan**: Current citations (`Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp:211`, `Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp:220`, and `Docs/BossCombatReview/Execution/Claude/B_AWR005/reg_f5/editor_raw.log:1578`) verify unit model evaluation and baseline floor PIE. Missing: PIE run with target on elevated ledge and an authored card with `MaxVerticalDeltaCm > 0` witnessing runtime selector refusal.

### `BOSS-SEL-008`: No-candidate fallback

- **Ledger Status**: `PARTIAL`
- **Authority**: **Engine Required (Claude)**
- **Ledger Observable**: When 0 offensive move cards qualify, boss executes default neutral strafe / reset behavior rather than freezing.
- **Ledger Notes**: Selector policy test asserts that when 0 cards qualify, Select returns ChosenIndex=INDEX_NONE as a valid non-error answer with every refusal named (selector_tests:95-96); live character currently fails on INDEX_NONE (boss_char:96); Behavior Tree neutral strafe loop pending.
- **ONE Missing Observation**: Live PIE run witnessing boss execute purposeful neutral repositioning when selector returns `INDEX_NONE` without failing closed.
- **Implementation & Evidence Plan**: Current citations (`Source/OneBossFight/Tests/RPGBossMoveSelectorTests.cpp:95`, `Source/OneBossFight/Tests/RPGBossMoveSelectorTests.cpp:96`) assert selector returns `INDEX_NONE` with named refusals. Missing: live `ARPGFrameworkBossCharacter` handling `INDEX_NONE` via neutral repositioning/strafe loop instead of failing closed.

### `BOSS-EXE-004`: Stale event rejection

- **Ledger Status**: `PARTIAL`
- **Authority**: **Engine Required (Claude)**
- **Ledger Observable**: Interrupted attack ignores late AnimNotifies from previous montage.
- **Ledger Notes**: MoveModel assertions verify old callback cannot abort new attack (model_tests:147) and delayed old tick rejected (model_tests:151); interrupted attack late AnimNotify rejection in live executor path not yet fully logged.
- **ONE Missing Observation**: Live executor log confirming rejection of late AnimNotify callbacks from an interrupted previous attack instance.
- **Implementation & Evidence Plan**: Current citations (`Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp:147`, `Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp:151`) assert old callback cannot abort new attack. Missing: live executor telemetry logging rejection of stale anim notify tokens from interrupted previous attack.

### `BOSS-EXE-006`: Idempotent abort

- **Ledger Status**: `PARTIAL`
- **Authority**: **Engine Required (Claude)**
- **Ledger Observable**: Calling AbortAttack twice during grab or AoE produces identical clean recovery with zero duplicate hit events.
- **Ledger Notes**: MoveModel assertion (model_tests:130) verifies repeated model abort is idempotent and emits zero second events; grab/AoE executor abort path not yet implemented.
- **ONE Missing Observation**: Grab or AoE attack executor abort path implemented and verified with repeated abort producing clean recovery and zero duplicate events.
- **Implementation & Evidence Plan**: Current citation (`Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp:130`) verifies repeated model abort is idempotent. Missing: live grab/AoE executor abort implementation in character/executor verifying repeated abort produces clean recovery with zero duplicate hit events.

### `BOSS-EXE-007`: Watchdog

- **Ledger Status**: `PARTIAL`
- **Authority**: **Engine Required (Claude)**
- **Ledger Observable**: Suppressed MontageEnd / NotifyEnd automatically aborts card after Timeout = RecoveryEndSeconds + 0.5s.
- **Ledger Notes**: MoveModel tests exact Idle end boundary (model_tests:114); PIE fixture adopts BlendOut-span natural end (f4_run1:1649); explicit suppressed-event watchdog timeout (+0.5s) not logged.
- **ONE Missing Observation**: Live executor telemetry logging watchdog timeout abort when montage end or notify end is suppressed.
- **Implementation & Evidence Plan**: Current citations (`Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp:114` and `Docs/BossCombatReview/Execution/Claude/F4/final_f4_run1/editor_raw.log:1649`) test Idle end boundary and blend-out span end. Missing: live executor watchdog timer logging timeout abort after `RecoveryEndSeconds + 0.5s` when end notify is suppressed.

### `BOSS-COM-002`: Gate after damage

- **Ledger Status**: `PARTIAL`
- **Authority**: **Engine Required (Claude)**
- **Ledger Observable**: Hit window EndSeconds occurs strictly before combo branch decision gate opens.
- **Ledger Notes**: Card schema enforces timeline ordering (card_tests:108); PIE proof confirms attack 1 hit window Close event at localSeconds=0.4917 (f5_run1:1605) and finished cleanup (f5_run1:1656) strictly precede decision gate opening for attack 2 (f5_run1:1661).
- **ONE Missing Observation**: Live PIE proof witnessing combo branch gate opening during recovery window strictly after active hit window closes.
- **Implementation & Evidence Plan**: Current citations (`Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp:108` and `Docs/BossCombatReview/Execution/Claude/B_COMBO2/pie_run1/editor_raw.log:1605`, `Docs/BossCombatReview/Execution/Claude/B_COMBO2/pie_run1/editor_raw.log:1656`, `Docs/BossCombatReview/Execution/Claude/B_COMBO2/pie_run1/editor_raw.log:1661`) verify card schema timeline ordering and sequential attack cleanup. Missing: live multi-node combo chain where a mid-combo branch gate opens during recovery strictly after hit window closes.

### `BOSS-COM-003`: Fresh branch context

- **Ledger Status**: `PARTIAL`
- **Authority**: **Engine Required (Claude)**
- **Ledger Observable**: Branch decision evaluates target position at branch gate; if player rolled behind boss, combo branches to turn-around sweep rather than continuing forward chain.
- **Ledger Notes**: Branch decision evaluates fresh snapshot (FComboGate) at decision gate. Unit tests assert front continue vs behind recovery (combo_tests:69, 71); PIE proof confirms fresh range/yaw evaluation at gate 1 (pie_run1:1791). PARTIAL per C-542 honest limit: live target was always in front (yaw=0); behind-the-boss branch discrimination is unit-tested only.
- **ONE Missing Observation**: Live PIE proof with player shifted behind boss at branch gate, witnessing behind-the-boss branch selection.
- **Implementation & Evidence Plan**: Current citations (`Source/OneBossFight/Tests/RPGBossComboTests.cpp:69`, `Source/OneBossFight/Tests/RPGBossComboTests.cpp:71`, and `Docs/BossCombatReview/Execution/Claude/B_COMBO2/pie_run1/editor_raw.log:1791`) verify unit tests and frontal gate evaluation. Missing: live PIE run with player shifted behind boss (`|yaw| > 90`) at gate opening witnessing turn-around follow-up branch.

### `BOSS-COM-004`: Explicit hit-confirm policy

- **Ledger Status**: `PARTIAL`
- **Authority**: **Engine Required (Claude)**
- **Ledger Observable**: Whiff, guard, and parry outcomes branch to distinct combo follow-ups (or force recovery reset).
- **Ledger Notes**: Unit tests prove outcome branching for Whiff -> C, Guarded -> D, and Parried -> DefaultRecovery (combo_tests:75-77). PIE proof confirms Hit -> Continue (pie_run1:1791) and Whiff -> Finished (pie_run1:1987). PARTIAL per C-542 honest limit: live telemetry only produces Hit and Whiff outcomes; Guarded and Parried branch edges are unit-tested only.
- **ONE Missing Observation**: Live PIE telemetry observing Guarded and Parried branch selection (`outcome=Guarded` / `outcome=Parried`) during player defense.
- **Implementation & Evidence Plan**: Current citations (`Source/OneBossFight/Tests/RPGBossComboTests.cpp:75`, `Source/OneBossFight/Tests/RPGBossComboTests.cpp:77`, and `Docs/BossCombatReview/Execution/Claude/B_COMBO2/pie_run1/editor_raw.log:1791`, `Docs/BossCombatReview/Execution/Claude/B_COMBO2/pie_run1/editor_raw.log:1987`) verify unit test outcome branching and live Hit/Whiff telemetry. Missing: live PIE telemetry observing Guarded and Parried outcome branch selection during active player shield defense.

### `BOSS-COM-005`: Single-use gate

- **Ledger Status**: `PARTIAL`
- **Authority**: **Engine Required (Claude)**
- **Ledger Observable**: Combo branch gate consumes trigger event; duplicate notifies within same window cannot trigger double branch.
- **Ledger Notes**: Unit test asserts duplicate GateId is ignored with EStep::Ignored (Combo.GateConsumed) leaving state untouched, and GateId 0 is refused (combo_tests:64, 65). PIE proof confirms monotonic gate generation (gate=1 at pie_run1:1791, gate=2 at pie_run1:1987). PARTIAL per C-542 honest limit: boss generates strictly monotonic GateIds so duplicate cannot occur live.
- **ONE Missing Observation**: Live PIE proof injecting an anomalous duplicate gate trigger during active execution and logging its rejection.
- **Implementation & Evidence Plan**: Current citations (`Source/OneBossFight/Tests/RPGBossComboTests.cpp:82` and `Docs/BossCombatReview/Execution/Claude/B_COMBO2/pie_run1/editor_raw.log:1791`, `Docs/BossCombatReview/Execution/Claude/B_COMBO2/pie_run1/editor_raw.log:1827`) verify unit test duplicate gate consumption and normal single gate evaluations. Missing: live PIE proof injecting an anomalous duplicate gate trigger during active attack execution and logging rejection (`result=Ignored`).

### `BOSS-COM-007`: Default recovery

- **Ledger Status**: `PARTIAL`
- **Authority**: **Engine Required (Claude)**
- **Ledger Observable**: Absence of branch input or out-of-range target at combo gate defaults cleanly to recovery blend without freeze.
- **Ledger Notes**: Unit tests assert out-of-range target (300cm > 250cm) and invalid target recover cleanly with Combo.DefaultRecovery (combo_tests:81, 82, 86). PIE proof confirms clean combo completion and attack loop continuation without freeze (RESULT outcome=CompletedWithDamage acceptedHits=2 attacks=3, pie_run1:2205). PARTIAL per C-542 honest limit: live run never triggered fallback recovery, witnessed via unit tests.
- **ONE Missing Observation**: Live PIE proof where target is within range but fails branch gate angle condition, witnessing clean transition to recovery.
- **Implementation & Evidence Plan**: Current citations (`Source/OneBossFight/Tests/RPGBossComboTests.cpp:87` and `Docs/BossCombatReview/Execution/Claude/B_COMBO2/pie_run1/editor_raw.log:1987`) verify unit test fallback recovery and live out-of-range recovery. Missing: live PIE proof where target is in range but fails angle condition, witnessing `result=Recover` and clean transition to recovery.

### `BOSS-ANM-002`: Telegraph phases

- **Ledger Status**: `PARTIAL`
- **Authority**: **Engine Required (Claude)**
- **Ledger Observable**: Every move card exhibits explicit CommitSeconds windup telegraph before active hit window.
- **Ledger Notes**: MoveCard schema rejects Commit >= ActiveStart (card_tests:107); PIE log (f4_run1:1571) logs windup telegraph before Open event at localSeconds=0.35; visual/audio telegraph cues not formally asserted in logs.
- **ONE Missing Observation**: Live PIE log or anim notify probe formally asserting synchronized visual/audio telegraph cues during `[0, CommitSeconds]`.
- **Implementation & Evidence Plan**: Current citations (`Source/OneBossFight/Tests/RPGBossMoveCardTests.cpp:107` and `Docs/BossCombatReview/Execution/Claude/F4/final_f4_run1/editor_raw.log:1571`) reject invalid commit timelines and log windup before Open event. Missing: formal assertion or probe in PIE log verifying synchronized visual/audio telegraph cues during windup.

### `BOSS-ANM-005`: Exclusive motion authority

- **Ledger Status**: `PARTIAL`
- **Authority**: **Engine Required (Claude)**
- **Ledger Observable**: During attack card playback, AI navigation velocity translation is disabled; root motion / displacement authored explicitly.
- **Ledger Notes**: PIE fixture completes AI navigation walk (f4_run1:1506) before attack playback starts (f4_run1:1507); formal AI navigation translation disablement lock in executor not yet authored.
- **ONE Missing Observation**: Explicit navigation velocity disablement lock in executor verified in PIE log during attack playback.
- **Implementation & Evidence Plan**: Current citations (`Docs/BossCombatReview/Execution/Claude/F4/final_f4_run1/editor_raw.log:1506`, `Docs/BossCombatReview/Execution/Claude/F4/final_f4_run1/editor_raw.log:1507`) witness walk finish before attack start. Missing: explicit navigation translation disablement lock in executor asserting zero AI translation velocity interference during attack playback.

### `BOSS-ANM-007`: Notify-end independence

- **Ledger Status**: `PARTIAL`
- **Authority**: **Engine Required (Claude)**
- **Ledger Observable**: Attack state recovery and cleanup cannot stall if animation notify is dropped or montage interrupted prematurely.
- **Ledger Notes**: MoveModel asserts active abort closes hit window immediately and signals Aborted without waiting for montage end (model_tests:129); live PIE confirms MidAttack interruption cleans up model and stops owned montage at exact stance break tick (f8_pie1:1619, 1620). Status remains PARTIAL per C-530 because dropped notify end stall independence is not yet proven without notify.
- **ONE Missing Observation**: Live PIE run with montage notify end intentionally omitted, proving attack finishes cleanly via fallback timer.
- **Implementation & Evidence Plan**: Current citations (`Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp:129` and `Docs/BossCombatReview/Execution/Claude/F8/pie_run1/editor_raw.log:1619`, `Docs/BossCombatReview/Execution/Claude/F8/pie_run1/editor_raw.log:1620`) verify abort closing hit window and stance break cleanup. Missing: live PIE run with dropped montage notify end proving state cleanup occurs without stalling.

### `BOSS-HIT-005`: Query filtering

- **Ledger Status**: `PARTIAL`
- **Authority**: **Engine Required (Claude)**
- **Ledger Observable**: Trace queries filter out boss self-collision and dead bodies; only valid player combat capsule registers hit.
- **Ledger Notes**: Resolver asserts RejectedDead for dead bodies (auto_tests:173); PIE fixture registers hit exclusively on target capsule with zero self-hits (f4_run1:1593); ignored self/dead candidates not explicitly logged per C-405.
- **ONE Missing Observation**: Live PIE collision query telemetry explicitly logging filtered-out self capsule and dead target candidates during weapon sweep.
- **Implementation & Evidence Plan**: Current citations (`Source/OneBossFight/Tests/RPGAutomationTests.cpp:173` and `Docs/BossCombatReview/Execution/Claude/F4/final_f4_run1/editor_raw.log:1593`) verify resolver dead target rejection and live player target hit. Missing: live PIE sweep query telemetry explicitly logging filtered-out self capsule and dead candidates.

### `BOSS-HIT-008`: Central defense order

- **Ledger Status**: `PARTIAL`
- **Authority**: **Engine Required (Claude)**
- **Ledger Observable**: Central damage resolver checks player blocking/parrying state before applying health damage.
- **Ledger Notes**: Combat.DamageResolver.Decide (auto_tests:172) asserts decision hierarchy order; live player shield blocking/parrying stance integration not yet active in PIE.
- **ONE Missing Observation**: Live PIE run with player in active shield block/parry stance, witnessing central resolver evaluate defense order before health damage.
- **Implementation & Evidence Plan**: Current citation (`Source/OneBossFight/Tests/RPGAutomationTests.cpp:172`) asserts resolver decision hierarchy order. Missing: live player shield blocking/parrying stance integration in PIE witnessing defense evaluation order before health damage.

### `BOSS-HIT-009`: Iframe completeness

- **Ledger Status**: `PARTIAL`
- **Authority**: **Engine Required (Claude)**
- **Ledger Observable**: Player dodge iframe rejection verified against weapon sweeps.
- **Ledger Notes**: RPGDamageRules decides RejectedInvulnerable when target has invulnerable status (auto_tests:176); live PIE dodge sweep in KI-146 proves sweep rejected when iframe active (ki146_dodge:1642). However, per KI-146 and BUILD-94, pack IA_Dodge iframes activate ~0.3s after press (after blade window), and RejectedInvulnerable occurred in only 3 runs while most runs hit; window completeness is not witnessed, status remains PARTIAL per C-530.
- **ONE Missing Observation**: Live PIE sweep run with calibrated player dodge timing proving reproducible `RejectedInvulnerable` throughout iframe window.
- **Implementation & Evidence Plan**: Current citations (`Source/OneBossFight/Tests/RPGAutomationTests.cpp:176` and `Docs/BossCombatReview/Execution/Claude/KI146/dodge_0.15/editor_raw.log:1642`) verify resolver rule and isolated dodge rejection. Missing: live PIE sweep run with calibrated dodge timing proving 100% reproducible `RejectedInvulnerable` across complete iframe window without late hit leakage.

### `BOSS-MOV-001`: Range-band policy

- **Ledger Status**: `PARTIAL`
- **Authority**: **Engine Required (Claude)**
- **Ledger Observable**: Attack cards partitioned across distinct range bands: Melee (0-220), Close (150-350), Medium (200-400), Gap-Closer (400-950).
- **Ledger Notes**: Range band [150, 180] cm observed in walk fixture (f4_run1:1506); full 15-family range-band partitioning awaits F5 authoring (calibrating to measured reach per KI-145).
- **ONE Missing Observation**: Move card set authoring partitioning attacks across distinct range bands and live PIE validation logging appropriate band selection.
- **Implementation & Evidence Plan**: Current citation (`Docs/BossCombatReview/Execution/Claude/F4/final_f4_run1/editor_raw.log:1506`) observes single range band in walk fixture. Missing: authoring full move cards partitioned across distinct range bands (Melee, Close, Medium, Gap-Closer) and live PIE run logging appropriate family selection.

### `BOSS-PAC-006`: Neutral is purposeful

- **Ledger Status**: `PARTIAL`
- **Authority**: **Engine Required (Claude)**
- **Ledger Observable**: Neutral state has zero active hitboxes, zero root motion drift, and clear idle posture.
- **Ledger Notes**: MoveModel asserts finished Idle (model_tests:73); PIE fixture verifies cleanups with modelIdle=1 and ownedMontageStopped=1 between attacks (f5_run1:1656, 1690); zero root motion drift confirmed across attack decisions with range held constant at exactly 169.602 cm (f5_run1:1510, 1661).
- **ONE Missing Observation**: Live PIE telemetry asserting zero active hitboxes (`activeHitboxes=0`) during neutral state intervals between attacks.
- **Implementation & Evidence Plan**: Current citations (`Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp:73` and `Docs/BossCombatReview/Execution/Claude/F5/pie_run1/editor_raw.log:1510`, `Docs/BossCombatReview/Execution/Claude/F5/pie_run1/editor_raw.log:1656`, `Docs/BossCombatReview/Execution/Claude/F5/pie_run1/editor_raw.log:1661`, `Docs/BossCombatReview/Execution/Claude/F5/pie_run1/editor_raw.log:1690`) verify model idle and zero root motion drift in neutral. Missing: formal telemetry assertion confirming zero active hitboxes during neutral intervals between attacks.

### `BOSS-PHS-004`: Fair heal punish

- **Ledger Status**: `PARTIAL`
- **Authority**: **Engine Required (Claude)**
- **Ledger Observable**: Heal punish move (MC-03/MC-05) triggers only when player initiates flask drink within reachable band.
- **Ledger Notes**: Legacy context only for adapters (OneBossFight.Binding.HealPunish.*); player flask drinking perception reaction loop in framework boss not yet active.
- **ONE Missing Observation**: Player flask drink perception reaction loop in boss character triggering heal-punish move selection in PIE.
- **Implementation & Evidence Plan**: Current status PARTIAL (legacy adapters exist). Missing: perception reaction loop in `ARPGFrameworkBossCharacter` detecting player flask drinking and triggering heal-punish card selection in PIE.

### `BOSS-QA-001`: Runtime overlay

- **Ledger Status**: `PARTIAL`
- **Authority**: **Engine Required (Claude)**
- **Ledger Observable**: On-screen debug overlay displays active MoveCard, Phase, Range, Cone, HitWindow state, and Posture.
- **Ledger Notes**: Runtime debug overlay implemented in RPGBossOverlayRules.h (rpg.BossOverlay CVar 1 on-screen, 2 logged). Live PIE proof on L_SevarogFrameworkProofF8 (B_QA001 pie2) verifies 16 telemetry lines, capturing idle (line 1577), HeavySlam committed (line 1588), live Window=Open during active swing (line 1642), stance break stagger with Posture=0/100 and Stagger=1 (line 1720), and Phase 2 live Window=Open swings (lines 1757, 1914). Unit test BossOverlayFormat (runtime_tests:376, 378, 380) verifies exact formatting and non-finite NaN/inf safe fallback to 'n/a'. Status remains PARTIAL per C-534/C-535: string construction and live logging are fully witnessed, but on-screen viewport pixel drawing has not yet been captured via screenshot (headless/unattended PIE GPU backbuffer readback returned black). Only the on-screen screenshot is required to graduate to WITNESSED.
- **ONE Missing Observation**: Interactive or windowed PIE viewport screenshot capturing on-screen debug overlay rendering with non-black pixels.
- **Implementation & Evidence Plan**: Current citations (`Source/OneBossFight/Tests/RPGFrameworkRuntimeTests.cpp:415`, `Source/OneBossFight/Tests/RPGFrameworkRuntimeTests.cpp:417`, `Source/OneBossFight/Tests/RPGFrameworkRuntimeTests.cpp:419` and `Docs/BossCombatReview/Execution/Claude/B_QA001/pie2/editor_raw.log:1577`, `Docs/BossCombatReview/Execution/Claude/B_QA001/pie2/editor_raw.log:1914`) verify overlay string formatting and live telemetry lines. Missing: viewport screenshot capturing on-screen debug overlay rendering with non-black pixels.

### `BOSS-QA-002`: Structured event log

- **Ledger Status**: `PARTIAL`
- **Authority**: **Engine Required (Claude)**
- **Ledger Observable**: Structured log output emits tagged lines: [CARD_VALIDATE], [CARD_PLAN], [CARD_APPLY], [CARD_DECISION], [CARD_HIT].
- **Ledger Notes**: PIE fixture emits structured [FrameworkProof] telemetry tokens (target_health_init, walk, hit, invariant); production [CARD_*] prefix reserved for QA Block.
- **ONE Missing Observation**: Engine logging emitting production `[CARD_*]` tagged lines during combat execution in PIE.
- **Implementation & Evidence Plan**: Current citations (`Docs/BossCombatReview/Execution/Claude/F4/final_f4_run1/editor_raw.log:1439`, `Docs/BossCombatReview/Execution/Claude/F4/final_f4_run1/editor_raw.log:1506`, `Docs/BossCombatReview/Execution/Claude/F4/final_f4_run1/editor_raw.log:1593`, `Docs/BossCombatReview/Execution/Claude/F4/final_f4_run1/editor_raw.log:1651`) verify `[FrameworkProof]` telemetry tokens. Missing: engine logger emitting production `[CARD_*]` prefix lines (`[CARD_VALIDATE]`, `[CARD_PLAN]`, `[CARD_APPLY]`, `[CARD_DECISION]`, `[CARD_HIT]`) during PIE.

### `BOSS-QA-003`: Reproducible scenarios

- **Ledger Status**: `PARTIAL`
- **Authority**: **Engine Required (Claude)**
- **Ledger Observable**: Scripted replay driver executes fixed player inputs and asserts deterministic boss state progression under fixed seed.
- **Ledger Notes**: PIE driver drive_pie.py produces consistent invariant outcomes across 3 runs, but a fixed-input replay harness asserting full state progression under fixed seed is not yet authored per C-405.
- **ONE Missing Observation**: Scripted replay harness executing fixed player inputs under fixed seed and asserting deterministic boss state progression across runs.
- **Implementation & Evidence Plan**: Current citations (`Docs/BossCombatReview/Execution/Claude/F4/final_f4_run1/editor_raw.log:1651`, `Docs/BossCombatReview/Execution/Claude/F4/final_f4_run2/editor_raw.log:1643`, `Docs/BossCombatReview/Execution/Claude/F4/final_f4_run3/editor_raw.log:1653`) verify invariant outcomes across runs. Missing: fixed-input replay harness asserting deterministic boss state progression under fixed seed across repeated runs.

### `BOSS-QA-004`: FPS and time-scale parity

- **Ledger Status**: `PARTIAL`
- **Authority**: **Engine Required (Claude)**
- **Ledger Observable**: Combat execution at 30, 60, and 120 FPS yields identical hit counts and damage totals.
- **Ledger Notes**: MoveModel assertion (model_tests:91) tests variable step invariance; swept capsule substeps adapt to velocity (f4_run1:1578); discrete 30/60/120 FPS PIE runs not logged.
- **ONE Missing Observation**: Discrete PIE runs executed at fixed 30, 60, and 120 FPS witnessing invariant hit counts and damage totals.
- **Implementation & Evidence Plan**: Current citations (`Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp:91` and `Docs/BossCombatReview/Execution/Claude/F4/final_f4_run1/editor_raw.log:1578`) verify variable step model invariance and adaptive swept capsule substeps. Missing: discrete PIE runs at fixed 30, 60, and 120 FPS verifying invariant hit counts and damage totals.

### `BOSS-QA-005`: Performance bounds

- **Ledger Status**: `PARTIAL`
- **Authority**: **Engine Required (Claude)**
- **Ledger Observable**: Packaged build 1080p 60 FPS verified with frame time p99 <= 16.67 ms on RTX 2060 Super baseline.
- **Ledger Notes**: Legacy benchmark tests pass in editor, but packaged build benchmark on target RTX 2060 Super GPU is parked (owner 2026-10-29).
- **ONE Missing Observation**: Packaged standalone build benchmark executed on RTX 2060 Super hardware recording frame time p99 <= 16.67 ms at 1080p.
- **Implementation & Evidence Plan**: Current status PARTIAL (in-editor benchmarks pass). Missing: packaged standalone benchmark run on target RTX 2060 Super hardware recording p99 frame time <= 16.67 ms at 1080p 60 FPS.

## 4. Verification & Consistency Safeguards

1. **Title Parity**: All 27 titles match `Docs/BossCombatReview/Execution/Antigravity/Ledger/witness_status_v3.json` exactly.
2. **Ledger Consistency**: All 27 rows are confirmed `PARTIAL` in the ledger census.
3. **Verbatim Symbol & Path Integrity**: Every backticked identifier referencing code or disk artifacts exists in `Source/` or `Docs/`.
4. **Line Endings**: Pure LF (`\n`) formatting across all documentation.

