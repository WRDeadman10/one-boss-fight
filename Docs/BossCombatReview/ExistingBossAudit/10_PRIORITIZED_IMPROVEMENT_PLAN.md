# Prioritized improvement plan — proposal only

No work below is approved or implemented by this audit. Owner approval is required for the next development phase. Claude retains editor/build/performance ownership; handoff and file claims are required before any implementation. Preserve pack assets, existing user edits,3.2m roll distance and60FPS target.

Effort estimates are engineering complexity, not delivery promises: S<1day, M1–3days, L3–7days, XL>7days. Art and owner test availability are separate.

## P0 — Establish a current read-only runtime baseline

**Problem/evidence:** high-level choice, movement, current asset defaults and motion ownership are unverified (U01–U08); saved GA_EnemyMeleeAttack export is historical. Test switches differ from Shipping.

**Root cause:** incomplete current evidence, not demonstrated missing AI.

**Affected files/assets:** all exact U01–U08 packages in document11; existing export/probe tooling and current test reports. No gameplay edits.

**Approach:** editor owner reads placed boss info/controller/AnimBP, created abilities, BT edges/services/decorators/BB keys, effective montage arrays and notify tracks, trace/resolver graph. Record asset/build fingerprint, test mode and current independent capture.

**Improvement:** correct integration points and reproducible baseline; prevents duplicate planners or fixes for retired assets.

**Dependencies/risks:** editor-owner availability; graph loads must not compile/resave or alter PIE state unexpectedly. Baseline must identify harness switches.

**Tests/acceptance:** one connected route from map to chosen ability to montage to production trace to resolved damage; identify every live damaging action, including untracked pack abilities; no filename-derived behavior claims.

**Rollback:** no gameplay mutation; discard/revise inaccurate audit conclusions. Effort M, priority High.

## P1 — Make the special attacks visible and interval-safe

**Problem/evidence:** G01/G02; [Wave:73](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwave.cpp:73), [Wave:164](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwave.cpp:164), [Heal:255](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHealPunish.cpp:255), [Sweep:175](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossLowSweep.cpp:175).

**Root cause:** debug-only ring presentation; current-state rather than crossed-boundary detection; current-radius-only collision.

**Affected:** RPGBossShockwave.*, RPGBossHealPunish.*, RPGBossLowSweep.*, RPGAttackTracker.*; project-owned ring VFX/material; pie_leap_wave.py and special drivers.

**Approach:** production ring cue driven by actual origin/radius/lifetime; interval/event crossing that fires once only for a valid continuing attack; swept previous-to-current annulus; explicit floor/occlusion policy. Handle abort/reset before catch-up so skipped windows do not create late damage.

**Improvement:** readable, hardware-stable ground/throw mechanics.

**Dependencies/risks:** P0 confirms no existing ring renderer; P2-compatible identity. Risk: catch-up after interruption, duplicate release, incorrect jump crossing time, VFX performance.

**Tests:**30/60/120FPS,50–300ms hitches, rates, moving/airborne target, both active boundaries, reset/death before crossing; Shipping debug-off visuals.

**Acceptance:** one valid release/launch per accepted instance, no post-abort damage, same logical contacts under supported steps, ring visually matches damaging band and remains legible under reduced effects.

**Rollback:** revert only new geometry/event/VFX integration; preserve previous assets. Do not silently ship invisible damage as fallback—owner chooses release block/disable policy. Effort L, priority Critical.

## P2 — Tighten the existing execution boundary

**Problem/evidence:** G03/G05; [Tracker:105](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:105), [Tracker:234](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:234), [Tracker:389](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:389), [Tracker:251](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:251).

**Root cause:** observer ID after start, index-based recognition, shared fallback timing, distributed cleanup.

**Affected:** RPGAttackTracker.*, RPGBossCloseClipSwap.*, RPGBossInterrupt.*, RPGTraceGuard.*, relevant project-owned ability adapter after U03; current pack assets remain intact.

**Approach:** accepted-start reservation with unique ID before playback; effective timing chosen by actual montage; failed-start rollback; provenance for callbacks/windows; single idempotent finalize contract and bounded watchdog. Use pack's existing execution owner; do not add competing montage playback.

**Improvement:** no ambiguous early events, correct fallback commitment, safe restarts and cleanup.

**Dependencies/risks:** P0 exact pack callbacks/commit semantics. Risk to pack follow-ups, rate changes, phase/break priority and reflection compatibility.

**Tests:** zero-time notify, unavailable clip/socket, repeated same montage without empty frame, stale callback, duplicate abort, phase/break/death permutations, fallback authored-montage absence, paused montage timeout.

**Acceptance:** first event has correct ID; failed start consumes no live instance/resource; no neutral with old damage window; separate authored/fallback timings; timeout restores legal state.

**Rollback:** isolated adapter feature switch in Development plus revert scoped changes; retain original ability/montage references. Effort L, priority High.

## P3 — Correlate damage and declare defense policy

**Problem/evidence:** G04; [DamageH:25](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGDamageResolver.h:25), [Wave:106](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwave.cpp:106), [LeapTest:103](C:/UnrealProject/OneBossFight/Scripts/Editor/pie_leap_wave.py:103).

**Root cause:** separate pack/native outcomes; global health delta used as hit identity.

**Affected:** RPGDamageResolver.*, RPGBossDamage.h, RPGBossShockwave.*, trace outcome adapter, U05/U08 pack boundary; existing damage/leap/iframe drivers.

**Approach:** owner-approved per-move block/parry/iframe/reaction table; consume pack accepted-result events through adapter; key by encounter/attack/stage/victim; share direct/wave precedence. Preserve pack health/effects, avoid a second health write. Keep intentional un-blockable moves explicit.

**Improvement:** trustworthy defense and no unrelated-loss suppression.

**Dependencies/risks:** P0/P2; exact pack effect order. Risk: applying damage twice, changing balance, bypassing existing status effects.

**Tests:** direct before/after wave launch, healing between contacts, unrelated damage, duplicate body contacts, live iframe edges, guard/parry combinations, lethal and reset.

**Acceptance:** one documented outcome and attributed health change per contact; intended central priority independent of net HP history; no unintended posture/guard effects under iframe.

**Rollback:** revert adapter/policy integration together; restore original values, not assets. Effort L, priority High.

## P4 — Validate visible contact and effective animation cards

**Problem/evidence:** G07 and fallback/asset timing ambiguity; [Look:76](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossLook.cpp:76), [Log:3271](C:/UnrealProject/OneBossFight/Saved/Logs/OneBossFight.log:3271).

**Root cause:** visible follower weapon and hidden gameplay trace are independent; current end-to-end measurements incomplete.

**Affected:** project-owned montage/sequence/socket configuration only if measurements justify; RPGBossLook integration; trace overlays and existing capture drivers. No pack edits by default.

**Approach:** per-move cards for resolved animation, rates, root axes/displacement, sockets, notify/contact/commit/recovery/branch/cue times. Overlay actual production samples on blade; include pack fallbacks and untracked travel/retaliation moves. Adjust the smallest proven offset/shape problem, not arbitrary collision inflation.

**Improvement:** honest visible reach and dependable animation handoff.

**Dependencies/risks:** P0/P1/P2; artist and owner capture. Risk: grip changes affect every pose; wider trace can erase spatial defense.

**Tests/acceptance:** midblade/tip/base and angular placements, all supported rates/FPS, clear no-contact outside agreed visible tolerance; frame review approved by owner. Tolerance must be chosen before tuning.

**Rollback:** restore recorded project-owned socket/shape/timing values in place. Effort L, priority High.

## P5 — Expose decisions and integrate the missing natural move

**Problem/evidence:** G06, incomplete context/selection trace; [Issues:71](C:/UnrealProject/OneBossFight/Documentation/KNOWN_ISSUES.md:71), [Export:790](C:/UnrealProject/OneBossFight/Saved/asset_text/GA_EnemyMeleeAttack.t3d:790), [Heal:95](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHealPunish.cpp:95).

**Root cause:** A4 is isolated from natural scheduling; high-level rules not observable enough to tune.

**Affected:** existing BT activation boundary or project-owned adapter established by P0; LowSweep/HealPunish/CombatDebug; new project-owned tuning data only after approval.

**Approach:** log all candidates/gates/reasons and seed; connect A4 only when existing owner is free and range/angle/state/cooldown pass. Build atomic gate context. Preserve fixed combo successors. Decide explicit A5 latency/probability/remaining-heal policy; retain LOS and dodgeable flight. Add history/utility only if measured repetition warrants it.

**Improvement:** player naturally sees low-sweep jump lesson; explainable contextual selection.

**Dependencies/risks:** P0/P2/P4; risk of double planner, attack starvation or excessive counters.

**Tests/acceptance:** autonomous A4 selection in eligible scenarios, none while busy/illegal; reproducible seed/context; no failed-start cooldown consumption; no midcommit replacement; before/after distribution approved.

**Rollback:** disable only new candidate/weights/adapter, leaving original selector and mechanics intact. Effort M–L, priority High.

## P6 — Establish real recovery, finite combos and punish margins

**Problem/evidence:** G05; [Tracker:411](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:411), [Tracker:251](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:251); current punish margins unverified.

**Root cause:** successor-veto and descriptive recovery timestamps are not an authored end-to-end minimum lock.

**Affected:** validated ability/branch handoff, RPGAttackTracker, project montages if required, player/build test drivers.

**Approach:** map existing successor edges, once-per-instance gates and explicit whiff/hit policy; declare denied-edge/default recovery; measure earliest retaliation. Preserve guaranteed openings and publish usable margin by build/position. Add pressure cap only if current outer BT loops fail intended resets.

**Improvement:** learned follow-up reads and useful slow/fast-build counterattacks.

**Dependencies/risks:** P2/P4/P5; risks include slowing entire fight, cancelling pack ability incorrectly and trivializing phases.

**Tests/acceptance:** every edge+default, duplicated gate, target escape/death, bounded burst length; intended light/heavy punish succeeds at declared distances with agreed positive buffer; owner can recognize conditional opening.

**Rollback:** restore scoped recovery/edge values and callbacks; retain original assets. Effort L, priority High.

## P7 — Targeted positioning, terrain and phase refinement

**Problem/evidence:** U02/U09, [Issues:69](C:/UnrealProject/OneBossFight/Documentation/KNOWN_ISSUES.md:69); trace LOS does not validate leap landing.

**Root cause:** unproved movement/path policy, not a demonstrated need for EQS or Motion Warping.

**Affected:** existing movement/ability owner, arena checks, RPGBossPhases only where justified.

**Approach:** inspect first; add legal landing/path fallback or bounded leash where tests fail. Tune range bands to measured reach. Document boss armor/interruption and phase pressure/recovery profiles before adding new behavior.

**Improvement:** fewer wall traps, consistent spatial counterplay.

**Dependencies/risks:** P0/P4/P6; nav/collision/visual landing mismatch; do not make boss omniscient.

**Tests/acceptance:** corners, pillars, gate, unreachable/elevated/outside target; no clipping, bounded fallback, at least one legal readable defense per legal position; phase/break/death priority unchanged.

**Rollback:** restore own movement tuning/adapter, not level/pack replacement. Effort M–L after inspection, priority Medium; confirmed wall failures become High.

## P8 — Revalidate the complete release

**Problem/evidence:** G08; current-source quality and final shipping performance not proven; KI-085/106 harness/hand-test gaps.

**Root cause:** historical subsets, test-only wake bypass and variable benchmark conditions.

**Affected:** existing automation/drivers, packaged benchmark/capture, camera/feedback settings; performance changes remain Claude-owned.

**Approach:** record exact build/assets/settings/seed; run quick gates after each package, then full regression/soak and owner fights with Shipping-equivalent wake. Reproduce held-key riposte and setup discrepancy. Validate low-shake/effect cues. Interleave same-machine packaged baseline/profile runs; tune lights only from controlled data.

**Tests/acceptance:** no stale damage, duplicate starts, stuck input or reset regression; all required moves naturally reachable; owner approves telegraphs/punishes/camera/audio; packaged1080p60FPS average and p99<=16.67ms on accepted3060 proxy (label as proxy, not2060 measurement).120FPS remains stretch/parity, not a promised target.

**Rollback:** restore only newly approved tuning and retain benchmark baseline records; block release rather than claiming old test totals prove new code. Effort L, priority High.

## Order and stop gates

P0 -> P1/P2 -> P3/P4 -> P5 -> P6 -> P7 -> P8. P8's diagnostic/performance work can run alongside bounded combat work under separate ownership; each gameplay change still needs its own regression gate. Re-evaluate scope after P0: unverified features may already be adequate, reducing planned work.

Possible quick wins are inspection/measurement, fallback-row selection once timings are confirmed, and a controlled existing light-shadow experiment. None is a license to tune blindly or skip implementation approval.

