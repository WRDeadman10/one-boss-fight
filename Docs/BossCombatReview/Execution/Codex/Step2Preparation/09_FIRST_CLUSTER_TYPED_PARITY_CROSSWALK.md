# First adapter cluster: typed schema and parity crosswalk

Codex lead,2026-10-26. Read-only implementation preparation for Encounter/Posture/Phases/Stagger. This refines PacketD0; it does not release schemas, adapters, source changes, editor fixtures or gameplay tuning. Source defaults below are independently inspected declarations, not effective serialized/live actor values. Full83 coverage remains required beyond this deliberately bounded cluster.

## What the current scaffold actually proves

RPGEncounterBinding.h:17–35 defines four Stats scalars and a generic Phase array with identity/threshold/three multipliers. CompileParticipantImpl validates finite scalar ranges and each phase independently, then copies Stats/Phases. It does not implement native adapters, verify phase ordering or require a nonempty phase set. FRPGParityField strings are provenance transport; checking that a field name exists in RequiredFields does not compare its text Value with a typed scalar or actual component value, nor compute the caller-supplied manifest hash. These are product validation gaps, not a failure of the accepted inert2a scope.

RPGEncounterBindingTests.cpp:23–30 supplies four stats and one synthetic Stats.MaxHealth manifest field. The only component plan at:57–64 assigns BossMaxHealth and forces GateRadius0, using AActor hosts and synthetic config in standalone test worlds. It does not instantiate Posture, Phases or Stagger, does not test their BeginPlay reads, and does not exercise a live pack boss.45/45 previously reported automation successes cannot close those missing cases. No UE test was rerun here.

## Exact scalar mapping candidates

Existing input names are exact scaffold members; proposed destination means a future explicit typed assignment, not an existing production adapter. Source root for destinations is Source/OneBossFight/Player.

| Existing typed input | Native destination / inspected default | First meaningful read / independent witness requirement |
|---|---|---|
|Stats.MaxHealth|RPGBossEncounter.BossMaxHealth =2000|Encounter Tick waits for positive pack readings, applies and reads back maximum; sample initial attachment, post-pack initialization, and reset. Merely assigning before BeginPlay does not prove eventual2000/2000.|
|Stats.MaxPosture|RPGBossPosture.PostureMax =100|Posture.BeginPlay36–39 seeds current Posture; ResetPool140–145 and RefillAfterBreak148–156 seed again. Observe maximum and current pool separately, plus preserved hold behavior.|
|Stats.PostureRegenDelay|RPGBossPosture.RegenDelaySeconds =6|RegenStep call228; ResetPool sets last drain-1 while break refill sets current world time. Preserve both timelines; no serialization of LastDrainTime.|
|Stats.PostureRegenRate|RPGBossPosture.RegenPerSecond =13|RegenStep call228; preserve native0.05s component cadence and time domain. Compare actual progression after delay, not only a property getter.|
|Phases[selected].EntryHealthFraction|RPGBossPhases.PhaseTwoHealthFraction =0.6|ResolveNow uses health/max and native transition rules. Mapping selected phase is unresolved; do not silently choose index0/last or add arbitrary multiphase behavior.|
|Phases[selected].SpeedMultiplier|RPGBossPhases.MovementScale =1.2|BeginPlay samples BaseWalkSpeed but reset does NOT restore that cache: it divides CURRENT speed by CURRENT MovementScale. Transition and later pack writes need ordered observations. Earlier “reset restores” wording corrected by14_PHASE_REVERSAL_PARITY_CONTRACT.md; no runtime failure reproduced.|
|Phases[selected].RateMultiplier|RPGBossPhases.AttackRateScale =1.2|Actual granted ability montage-rate application/reversal; pack ABI and authored/fallback montage paths remain explicit. Scalar assignment alone is insufficient.|
|Phases[selected].AttackMultiplier|RPGBossPhases.DamageScale =1.25|Attribute.Attack application/reversal and reset; compare against pre-transition observed baseline, not a hardcoded generated expectation.|

## Inputs absent from those typed records

| Consumer group | Missing explicit schema boundary | Required decision/evidence before adapter acceptance |
|---|---|---|
|Encounter activation/reset|GateRadius1200; bResetOnPlayerRespawn; session-only bTestFreeze; startup compatibility enforcement4s|Separate encounter policy from boss stats and test overrides. Current fixture GateRadius0 is synthetic behavior, not Boss01 parity. HomeTransform/generation/health baseline remain runtime state.|
|Posture capability|bPinPackPoise=true; native pack-poise configuration writes StatRegenCoolDown1e9 and rates0|Trusted capability/compatibility policy, not a new author string-field API. ConfigureAttribute retries after pack extended attributes exist; verify actual target object/class and suppression without claiming a new posture feature.|
|Phase transition/presentation|TransitionSeconds1.8, bUseRoarClip, roar/fallback/immunity refs, bPausePostureInTransition, leap block/tag, ability prefix|Typed dependency and capability record, source-verified registration order and Stagger prerequisite. Loaded objects, phase flags, baseline speeds and transient immunity ownership remain state.|
|Disabled legacy fireball|bFireballEnabled=false, ability/cooldown/range fields|Migration must preserve disabled behavior and referenced dependencies. Do not enable it merely because a generic phase row exists.|
|Stagger and riposte|StaggerSeconds2.5, FreezeAtPosition1.55, CriticalMultiplier2.5, range/cones/arm, paired clips, alignment0.3, start gap150, impact0.8, base40, cooldown0 and other declared inputs|No corresponding typed config in scaffold. Use narrow Stagger/Riposte records, preserve critical hit40×2.5=100 and current fallback/abort rules; bCriticalOnEveryHit remains test policy. Full field inventory remains02/WP13, not just this selected list.|

No selected typed phase row or missing schema should be manufactured from FRPGParityField.Value strings. Unknown mapping is a named compile/design gate. Generic Phase arrays require an explicit native capability contract that rejects unsupported arrangements, or a separately reviewed extension; this crosswalk approves neither a new phase count nor threshold tuning. Likewise positive-only Stats validation and native legacy health bypass/sentinel behavior are distinct policies; don't silently reinterpret a new data definition as legacy fallback.

## Staged parity witness matrix (NOT RUN)

1. Independently pin the actual legacy actor and dependencies before migration, including source hash, full actor/class/world/GI identities, startup cvars, selected catalog epoch and effective serialized/component values. Keep source-default and live-observation columns distinct. No fabricated values on missing hooks.
2. Observe configured unregistered instances and reject preexisting/begun consumers. Verify each typed assignment and provenance against an independent expected fixture. Deliberately change one input, omit one required field and mismatch a provenance text Value; ensure failures cannot be hidden by a shared expected/actual default helper.
3. Run real BeginPlay/pack initialization: health application and readback, Posture seeding, phase dependency loads and movement baseline, Stagger prerequisites. Record both attach triggers and duplicate suppression; reserve all participants before registering any cluster.
4. Exercise drain/hold/refill/reset and threshold-cross-with-break ordering. Compare before/after attributes and rates, exact generation owner, interruption/death cleanup, disabled fireball and test override restoration. Do not serialize mutable state to make parity pass.
5. Preserve failures and separate fixture arithmetic/property parity from real event-order/combat proof. Pair with08 cleanup requirements and07 retired-binding fences. Shipping configuration availability, two real duels and performance remain separate unclosed gates.

No new editor request to resting Claude: this is the replacement operator's future fixture contract, subject to resumed operator scheduling and scoped approval.

Follow-up15_HEALTH_APPLICATION_PARITY_CONTRACT.md details registration-ready versus actual pack-health application, >1 native override versus >0 compiler domain, startup restoration gates and reset reading current pack maximum. Synthetic GateRadius0 does not exercise normal initial dormancy restoration. No new delay/range policy or runtime failure is approved by that source audit.

14's Stagger-handoff source addendum now records refill-before-queued-phase pin, behavior hold transfer versus posture enum, reset's final ResetPool sentinel and next-drain timestamp replacement. Preserve source order in first-cluster integration; no new hold ownership policy or executed UE witness implied. Earlier source-document hashes retain their historical versions.

## Pinned current source (SHA256)

| Source/OneBossFight relative file | Hash |
|---|---|
|Player/RPGEncounterBinding.h|4330f8c416cd75284e829856b5d1cba7001c5ee62f40bdc7b1bf98a8dbf94a80|
|Player/RPGEncounterBinding.cpp|2fe63bcb78261b9bdd15be33607ea3c696ae33227989facc5b67e15cd91110dc|
|Player/RPGBossEncounter.h|4f3ab203562ef2d3a2d18828feaf5f437a5a7eaff1054e9b6ce60e9150cae9d6|
|Player/RPGBossPosture.h|bca70f5816a45733f0ea2d5550651da7192ba179a5e31d736eab90fd46cd3ff8|
|Player/RPGBossPosture.cpp|b26e184b0410e858d1c504e0b374dbc9e8f4c6b6399b05617559bb6909e88e41|
|Player/RPGBossPhases.h|0887f37564a28564261b81ad21a1baf2a4c6f6adae99a3a49c3c15622225a69a|
|Player/RPGBossStagger.h|7cfaaadbc33934d1dfe66560c0ff8c7fb47ac9e05399a5445b8c1e9a18c3695b|
|Tests/RPGEncounterBindingTests.cpp|bcdb3b2f40f1795bfd6187523cf98fc8ab2567cae46949065dd3a6908f2d66da|

Encounter/Phases/Stagger implementation pins remain in SOURCE_OBSERVATIONS.json and08 where recorded; refresh independently before implementation without overwriting the historical snapshot. A hash pin establishes bytes, not semantic coverage or runtime execution.
