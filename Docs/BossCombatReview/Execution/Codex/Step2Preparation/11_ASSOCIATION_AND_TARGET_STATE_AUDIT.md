# Associated-target migration: lookup and state ownership

Codex lead,2026-10-27. Static source/design review only. No live changes, engine test, new gameplay policy or integration release. Refines PacketF/G; PacketB must preserve current behavior and must NOT absorb these changes into legacy extraction. Partial targeted audit, not an exhaustive project/Blueprint caller inventory or evidence that two live duels were run.

## Actual call-site distinctions

| Source under Source/OneBossFight/Player | Inspected behavior | Future bound-context requirement |
|---|---|---|
|RPGHitIntake.cpp198–228|TrackBossHealth caches first IsPackBoss character found by iterator, searches on0.5s retry when missing; does not scan on every hit|Resolve associated boss explicitly; invalidate cache and health baseline/scaler on key/target/generation change. Preserve existing unbound single-boss compatibility route under its own policy.|
|RPGHitIntake.cpp397–419|HandlePackHit obtains HitResult actor directly, filters IsPackBoss, defers finalize next tick|Validate event target against current associated participant and capture immutable identity/generation with queued record. Do not replace a direct event target with first-boss lookup. There is no iterator in this function.|
|RPGHitIntake.cpp422 onward|FinalizePending deduplicates using SeenMontages only; OnHit scaler is one intake-owned state, while TrackBossHealth calls that scaler for the cached boss|Target/generation/action identity must accompany pending correction/merge state, or a reviewed one-target-per-intake invariant must reject cross-target input before it enters shared state. Different targets sharing montage name must not silently merge. Same montage asset can restart: identity is not just a name.|
|RPGRiposteInput.cpp51–74|OnLightAttack iterates all pack-boss pawns and tries eligible Stagger components; does not stop at first success|Bound input goes only to approved associated boss. Tests must check unrelated staggered boss is untouched, not merely that one riposte accepted. Preserve ordinary unbound behavior unless separately approved.|
|RPGBossEncounter.cpp126–151|Player0 drives respawn identity detection, activation distance and reset|Associated player's replacement must be distinguished from unrelated player0 changes. Reset remains one encounter-generation authority; no duplicate reset when lookup cache refreshes.|
|RPGBossPhases.cpp155–164|Phase transition waits on player0 HitIntake pending records|Wait on associated player's actual pending intake. Otherwise another encounter's pending hit can suppress a transition, or the correct pending hit can be missed. Phases458 also uses player0 for legacy fireball; that feature remains disabled, not enabled by migration.|
|RPGBossHealPunish.cpp99/154/232|Player0 participates in heal detection, eligibility and launch|Capture associated target and launch key; a later target/pawn switch cannot silently redirect an already pending punish. Preserve approved timing and eligibility policy.|
|RPGBossShockwave.cpp48/66|HealthAtLaunch samples player0, Resolve later queries player0|Use the same associated target identity across launch/sample/resolve; central-hit priority baseline cannot be borrowed from another pawn. Retain annulus/timing semantics during migration; no swept collision fix hidden here.|
|RPGTraceGuard.cpp167|Player0 is temporarily seeded into hit set for blocked line-of-sight|Choose associated target and preserve exact owned seed removal/window identity; no unrelated target exclusions.|
|RPGIFrameMonitor.cpp24–27|Static Find(WorldContext) resolves player0 monitor|Callers need actor-scoped lookup to inspect the intended victim's i-frame state. A world-context parameter alone does not encode participant association.|
|RPGDamageResolver.cpp201–215|GetPlayerPawn occurs in ResolveForTest under non-Shipping guard|Do not report this as production Resolve target selection. Production Resolve already accepts a victim; validate that caller supplies the correct bound victim and generation. Test helper selection is a separate fixture concern.|

## Why a resolver swap is insufficient

Current intake stores a target weak pointer in the hit record but also owns mutable health correction state independently of that record. A weak pointer establishes object lifetime, not encounter identity/current generation. A pending next-tick record can survive a reset while its actor remains valid. Health sampling baseline, queued multiplier correction, montage merge key, pending record finalization and target association must agree on one immutable lifetime token.

This is a source-derived requirement for future multiple-context acceptance, not a reproduced wrong-damage event in current single-boss play. Do not claim that every simultaneous-target case is reachable in the current fixture. Actual Blueprint dispatch/event ordering and possible cross-target inputs still need reviewed engine evidence. A design can constrain unsupported input, but cannot claim general associated-context isolation while silently using first-world actors internally.

## Required staged/engine witnesses before PacketF acceptance

### Cancellation follow-up,2026-10-27

Additional actual source inspection confirms existing protection that migration must preserve: HealPunish.cpp218–223 detects encounter generation change, clears pending requests and resets cooldown; native Javelin.Launch60–69 captures generation/attack instance, and Tick101–115 cancels when source boss is gone/dead or the source encounter generation differs. Do not describe all delayed native effects as unguarded or replace these safeguards with a second generation owner. This remains static source evidence, not a newly executed cancellation test.

Intake differs: HandlePackHit schedules a next-tick UObject delegate; its current record has a target weak pointer but no captured participant generation in the inspected record/queue path. EndPlay171–175 unbinds the pack event; ResetCounters537 onward clears Pending and scaler, but the inspected Encounter reset implementation has no intake ResetCounters/OnGenerationChanged call. This targeted source search does not prove no indirect Blueprint caller exists. A UObject-bound timer may become invalid on destruction; that is different from an encounter reset while the same actor/component survives. Do not claim a reproduced stale hit or timer after destruction. Future fixture must reset between queue and finalize, retain living objects, and observe whether old-generation health/posture/bleed effects are rejected; no engine run authorized or performed here.

Use two independently associated player/boss pairs. Hit B while A is first in iterator order; verify B's health/posture/bleed attribution, no A state change and no A correction baseline. Reset A with B holding a pending hit; verify only A's old key/state expires. Queue same montage-name records for different target identities, repeated playback instances and legitimate same-target dual-blade hits; distinguish rejection/merge policy explicitly. Replace one pawn without destroying its old weak target yet; verify old-generation records/pending punish/wave cannot redirect. Press riposte while unrelated boss is staggered; no unrelated action.

Tests must preserve current single-duel compatibility, row multipliers, central priority and exact cleanup ownership. These witnesses are NOT RUN here. No new natural-frequency, geometry, performance, or packed-runtime claim. Hot-path lookup complexity still needs actual measurement after approved implementation; reducing iterators structurally is not p99 proof.

## Independently observed byte pins

| Source/OneBossFight/Player relative source | SHA256 |
|---|---|
|RPGHitIntake.cpp|f2d0bd281924c4d29509214c1344234e1a8b2f476a77e51e00a045e73ae4a3db|
|RPGRiposteInput.cpp|8443ebb9380a25c349f40e7e635d0eb8cade3656cbee1e3fc83dc2f3d50ab277|
|RPGIFrameMonitor.cpp|46c694c8841dbcfca3f85239e6a356d418a3ff08e3966edee431c7b669ce6c11|
|RPGTraceGuard.cpp|24db190a15fafda4f4dd266506b199f2cc609d17cbd7c3fc3b638ca915bea472|
|RPGDamageResolver.cpp|82da0dd3400a049d92bd96409f90db58a319fd7db73e44f7b46b766e938a6bca|
|RPGBossHealPunish.cpp|1e63046d9c215fd0d7a5f894ee1b4539d64ddbefd9c80812cecbbae89c476906|
|RPGBossJavelin.cpp|6438e6bb76122fae5193bff9a1d55c88211dfb1edf90c4704236c1500a744bdb|

Other cited consumer pins already in SOURCE_OBSERVATIONS.json/08; recheck before implementation, preserve historical evidence. No scanner snapshot regenerated or source defaults changed.
