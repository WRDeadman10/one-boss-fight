# Existing boss audit — executive summary

**Audit date:** October 25, 2026. **Scope:** read-only source, configuration, package dependencies, saved graph export and historical evidence against all 83 Phase 1 requirements. Only the twelve requested audit documents were created. No gameplay/asset/config edits, editor session, build, PIE, package, commit or push was performed.

## Verdict

Keep the existing architecture. The project already has a substantial working duel: pack-owned abilities/AI, native attack tracking and specials, posture/riposte, encounter reset, phase progression and useful tests. Its highest-value improvements are making existing damage readable and temporally reliable, tightening execution/damage ownership, and measuring actual punish opportunities—not replacing the boss with the reference example or merely adding animations.

This is **not a fresh playtest or certification of combat feel**. Binary dependencies were not treated as graphs. Unknown current Blueprint behavior remains explicitly unverified.

## Architecture

L_SevarogArena uses the Advanced ARPG Combat game mode/player and BP_ExampleGreatSwordBoss with the placed ExampleGreatSwordBoss info override. The dependency route includes BP_BaseAIController, BT_ExampleBoss, the humanoid behavior state machine, combat style and pack ability framework. This is the pack's custom Blueprint ability system, not Epic GAS.

RPGPlayerMovesSubsystem attaches project C++ extensions. Pack abilities own ordinary attacks and montage dispatch; RPGAttackTracker observes stages and controls commitment/heading. TraceGuard wraps pack trace safety. LowSweep, HealPunish/Javelin and Shockwave use a separate native damage resolver. Posture, Stagger, Encounter and Phases manage the larger encounter lifecycle. Retired Sevarog/Greystone implementations are not the active route.

See [architecture and evidence](C:/UnrealProject/OneBossFight/Docs/BossCombatReview/ExistingBossAudit/01_EXISTING_BOSS_ARCHITECTURE.md).

## Requirement results

| Classification | Count | Meaning |
|---|---:|---|
| IMPLEMENTED | 8 | Inspected implementation satisfies the scoped requirement; not a feel verdict |
| PARTIAL | 58 | A verified subset exists, but the full contract is incomplete or not established end-to-end |
| MISSING | 1 | A specific required behavior is positively absent from the native execution path |
| UNVERIFIED | 13 | Critical asset/runtime evidence is insufficient |
| NOT APPLICABLE | 3 | Outside the current approved design |

These counts are strict reference classifications, **not a project completion percentage**. See the [83-row evidence matrix](C:/UnrealProject/OneBossFight/Docs/BossCombatReview/ExistingBossAudit/03_REFERENCE_COMPARISON_MATRIX.md).

**Implemented:** observable committed heal reaction (AWR-006); deterministic conflict priority (EXE-005); fresh branch position check (COM-003); separate posture, explicit regeneration and bounded break/riposte (DEF-001–003); declared phase interruption policy and once-per-encounter progression (PHS-002–003).

**Partial:** targeting/context, ordinary selection eligibility and history safeguards, attack transactions/finalization, combo/default recovery, animation/contact contracts, damage geometry/defense integration, movement/pacing, phase profiles and diagnostics. “Partial” often means a meaningful native safeguard exists but the larger reference contract is not satisfied or fully established.

**Missing:** BOSS-EXE-002. Native attack identity is allocated when Tick observes a playing montage, rather than reserved before playback. This does not claim the pack has no internal ability identity; that identity is not established as the native attack provenance contract.

**Unverified:** adaptation (AWR-008); higher-level utility and empty-pool fallback (SEL-004/008); motion ownership and warp policy (ANM-005/006); production adaptive trace sampling (HIT-004); position scoring, stable movement goals and arena-wide defense (MOV-002/003/006); branch readability, measured punish margin and neutral presentation (PAC-004/005/006); boss defensive policy (DEF-005). Exact asset paths and inspections are in the [unverified register](C:/UnrealProject/OneBossFight/Docs/BossCombatReview/ExistingBossAudit/11_UNVERIFIED_ASSETS_AND_TESTS.md).

**Not applicable:** variable holds in the current fixed-delay catalogue (ANM-003), boss grabs (HIT-012), and multiplayer authority (QA-008). Re-audit if scope changes.

## Highest-impact gaps and causes

1. **Critical — wave readability:** the inspected A6 ring damage path renders its ring only outside Shipping; the existing issue record also reports missing wave visuals. Root cause: production presentation disconnected from the damaging radius. A debug-off Shipping capture must check for any independently wired current VFX before implementation.
2. **High — hitch-sensitive specials:** current-phase polling can skip an entire active interval; the expanding wave checks only its current band. Root cause: sampled-state logic without crossed-boundary or swept-radius handling. These mechanisms are source-confirmed; no new runtime reproduction was performed.
3. **High — incorrect fallback timing contract:** original pack and authored replacement montages share timing rows. Root cause: timing keyed to a move/name group rather than the resolved animation. Fallback preserves assets but not necessarily correct commitment/contact.
4. **High — split defense and hit provenance:** own special HP writes bypass pack defense/reaction processing; wave suppression infers a direct hit from net HP loss. Root cause: separate outcome authorities and no shared attributed contact key. Blockability must be an explicit design choice.
5. **High — incomplete lifecycle/recovery contract:** identity arrives after play, branch veto occurs after successor start, and RecoveryEndTime is descriptive rather than an enforced lock. Pack safeguards and actual earliest retaliation require inspection; a universal softlock or “fake recovery” is not proven.
6. **High — incomplete natural move integration:** A4 has animation/geometry and forced tests, but existing documentation says BT never chooses it and native autonomous scheduling was not found. Root cause: selection integration, not lack of content; confirm current BT overrides.
7. **High validation/release risks:** hidden production trace versus visible sword alignment, current punish readability and final Shipping performance remain open. Historical 28–29 FPS/~40 ms p99 on the accepted RTX 3060 proxy does not meet the 60 FPS/16.67 ms target; promising Development lighting experiments are not a Shipping pass.

Detailed evidence, caveats and tests: [ranked gaps](C:/UnrealProject/OneBossFight/Docs/BossCombatReview/ExistingBossAudit/04_CRITICAL_GAPS.md) and [root causes](C:/UnrealProject/OneBossFight/Docs/BossCombatReview/ExistingBossAudit/09_ROOT_CAUSE_ANALYSIS.md).

## Preserve

Preserve the pack character/controller/BT/ability backbone; native attachment and reflection facades; posture/riposte and priority rules; generation-based reset; monotonic phases and reversible buffs; live-instance clip swaps; immediate trace/interruption cleanup; player builds and measured dodge baseline; reusable authored/pack assets; existing tests and benchmark tools.

Extend narrow boundaries rather than replacing frameworks. Do not delete/recreate referenced assets, migrate to GAS/StateTree without demonstrated need, or retune the player's dodge to compensate for unreadable boss damage. See [preservation decisions](C:/UnrealProject/OneBossFight/Docs/BossCombatReview/ExistingBossAudit/08_SYSTEMS_TO_PRESERVE.md).

## Incremental roadmap — approval required

1. **P0:** obtain editor-owner handoff; inspect current graphs/defaults and capture a reproducible runtime baseline.
2. **P1:** provide a production wave cue and interval-safe release/launch/contact handling.
3. **P2:** establish pre-start identity, asset-specific fallback timing, rollback and idempotent finalization/watchdog at the existing execution boundary.
4. **P3:** correlate pack/native damage outcomes and document per-move defense/direct-wave precedence.
5. **P4:** measure visible blade versus production trace; create effective move cards including rates, root motion and recovery.
6. **P5:** expose eligibility/choice reasons; integrate existing A4 naturally and clarify heal-reaction policy without a competing planner.
7. **P6:** verify finite combos, explicit default recovery and usable punish margins for both builds.
8. **P7:** address only demonstrated movement, terrain, landing or phase-profile deficiencies.
9. **P8:** run fresh regression, owner feel tests and controlled packaged performance acceptance; Claude retains performance ownership.

P1/P2 precede dependent damage/measurement work; review scope after P0 because some unverified systems may already be adequate. Each package includes affected files/assets, risks, tests, acceptance and rollback in the [implementation proposal](C:/UnrealProject/OneBossFight/Docs/BossCombatReview/ExistingBossAudit/10_PRIORITIZED_IMPROVEMENT_PLAN.md).

## Evidence limitations and handoff

Historical successes include reported 37/37 automation, 11/11 dormant wake, trace/iframe checks and a 213-check soak, but they do not collectively certify the latest complete build or human combat quality. Older drivers bypass the wake clip; Shipping does not. C-84 supersedes the stale-montage/pose-damping explanation of KI-106; its remaining driver setup discrepancy is not a confirmed product defect.

**Audit complete. Stop here. No proposed improvement is implemented or approved.** The next development phase requires explicit owner approval and the applicable team/editor handoff.

