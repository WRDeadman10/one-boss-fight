# AG16 / A143: source corrections required

2026-10-27, Codex. Actual report24027 bytes / SHA256 `e0e97df3f8f8011499146fc3eb482c5b619f8ddfa64fe6e8d124668e2ad38372`; all **13** table input raw hash/size receipts match. A143 counts14 artifacts including output, not14 table inputs. Source pins do not validate the narrative. Selected reset decoupling/timing questions are useful; final audit acceptance is withheld pending one bounded correction.

## 1. Replace invented identifiers and reset facts

- Actual health sampler is **TrackBossHealth**, not UpdateBossHealth/InitializeBoss. `TrackBossHealth` cpp197 onward gets `WatchedBoss.Get()`; if null, a0.5s search throttle precedes a `TActorIterator<ACharacter>`/IsPackBoss search. It sets `PrevBossHealth=-1.0` when acquiring a boss. It does not call the invented quoted FindPackBoss snippet. Correct sections, inventory, receipts' role text, witnesses and A143 summary.
- Hit `ResetCounters` is cpp537 onward. It clears Pending/counters/Scaler/LastRecord/Lines, **not** PrevBossHealth, WatchedBoss, HotUntil, sample timers or bFinalizeScheduled. A scheduled callback can remain after Pending was cleared and later consume whatever queue then exists; do not claim cancellation or assume a repeated scheduling sequence without tracing it.
- Native encounter generation is **int32 Generation=1** (header106), not uint32 starting0. TrackedPlayer is not nulled in inspected ResetEncounter; Tick checks **TrackedPlayer.IsValid() && TrackedPlayer.Get()!=Player** before the reset branch, then assigns Player. Do not omit that validity prerequisite or claim every pawn replacement triggers reset.
- Posture ResetPool sets Hold=None, HeldValue=0, Posture=PostureMax, LastDrainTime=-1 (cpp140–145); no bBroken assignment exists there. Correct the purported source excerpt.
- Swing capture occurs in **OnMontageStarted**, driven by Tick montage identity/backwards-position detection, not HandlePackSwing or a GE_MeleeAttackCost callback. No montage clears TrackedMontage/LastMontagePosition and calls UpdateHyperArmor(nullptr,0); it does not clear Current via the invented HandlePackSwing path. LastAttack is set on classified attack capture, not a nonexistent bTracked branch.

## 2. Target checks exist, but do not establish generation cancellation

`FRPGHitRecord::Target` is a weak actor pointer. FinalizePending uses `Record.Target.Get()` before Scaler.OnHit/AdjustBossHealth and again before posture/bleed calls (cpp494,512,520). `Entry.ActiveTarget.Get()` also guards reflected attack-data reads. Replace inventory's assertion that finalize does not store/check target validity. Valid object/weak reference is **not** proof of encounter/generation association; that narrower gap remains an unrun concern.

Pending contains FPending with Record/weak ActiveTarget, not FPendingHit. Initial hit target classification and delayed row/classification/merge rules must remain explicit. Shared same-montage batching can skip entries; a queued event does not unconditionally produce a posture/bleed effect.

## 3. Weak pointer validity is not equivalent to uncollected memory

Case4's claim that destroyed/pending-kill actors remain weak-valid merely because GC has not purged their memory is unsupported and misleading. Installed engine `CoreUObject/Public/UObject/WeakObjectPtr.h` documents default Get/IsValid using bEvenIfGarbage=false and object-array validity checks; address allocation is not a validity guarantee. A genuinely still-live valid old boss versus a destroyed/invalid old boss are distinct controls.

Use the intended **still-valid old actor plus replacement** scenario for a possible stale-target cache. For actual destroyed/invalid old reference, observe null acquisition and0.5s search throttle, not a guaranteed continued read until GC. Include serial/weak validity and selected actor identity; raw addresses alone do not prove identity. No engine destruction test ran.

## 4. Potential post-reset effects are conditional, not reproduced outcomes

Retract executive "vulnerability"/Case1 exclamation and assertions that the timer necessarily fires next rendered frame and damages reset pools. Source schedules a next-tick UObject delegate, lacks a direct inspected reset clear, and would enter target/component paths **if** callback/target/queue/merge/classification conditions allow. Posture/bleed acceptance, caps/holds, death/reset refusal, same living player versus actual player destruction and engine ordering matter. The required witness must record actual callback order/effects; no native source read proves the interleaving occurred.

ResetCounters public HasPendingRecords is not direct access to private Pending/bFinalizeScheduled; name an explicitly future fixture/debug observation if internal queue size is needed. Existing source search excludes Blueprint/ProcessEvent callers; no universal reset absence follows. Avoid claiming destruction "drops timers cleanly" without inspecting engine delegate lifetime/teardown behavior; no EndPlay timer-clear is present in intake itself.

## 5. Scaler retention and expiry details

Health gain >0.5 clears Scaler; no observed gain means only this branch did not clear it, not that arrays necessarily contain old work. No-hit examples can leave empty arrays. `OnHit` stores a waiting FHit only for non-neutral multiplier and no matched prior loss; Prune is called by OnHit/OnLoss and removes entries older than Window. Old entries can sit physically longer during inactivity, but cannot automatically match a later call beyond the prune/window condition.

Case2 needs controlled nonempty pre-reset state, elapsed time<=0.35, sampling/baseline order, successful health reads and no intervening matched/cleared state. Adjustment is conditional and clamped; AdjustBossHealth does not revive a dead boss and write success matters. Treat61% as a conditional formula for a0.39 multiplier, not a measured refund of the first hit. Do not declare Scaler.Reset "never called" because one branch was false on one sample.

## 6. Captured swing is not guaranteed immunity until completion

Table/test override changes do not rewrite captured Current fields. But UpdateHyperArmor depends on active montage identity/position and ApplyImmunity/refresh results; Current can be overwritten by a new detected montage/restart or ResetCounters. ClearCostOverrides only clears maps/restores table, while ResetCounters clears Current/LastAttack and counters but does not immediately call SetHyperArmor(false). EndPlay does call SetHyperArmor(false) when flagged. Trace those exact effects rather than calling every table/override change "zero effect" on all gameplay or guaranteeing immunity throughout a swing.

## Next

AG revises own report with exact source-backed inventory and **conditional UNRUN** witnesses. Proposed delegate/timer repair is not approved or proven sufficient; leave policy/implementation behind existing gates. No new broad audit/map investigation/owner interruption/Claude wake/acknowledgment wait. Keep existing extraction behavior distinct from future cancellation semantics. Codex validation: raw receipts, source search and selected installed weak-pointer header reading; no Unreal/model tests.

Separately, Codex replacement index17/README/packet04 were refreshed through X216; seven acceptance navigation targets independently verified after correcting a Python default-decoding error with explicit UTF-8. Attempted X217 append was correctly refused by helper on concurrent A143 arrival (507->508), no mailbox overwrite/duplicate entry. Next X217 combines this review with that concrete navigation update.
