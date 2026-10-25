# WP-4 — P2 request adapter and accepted-action transaction

2026-10-25, Codex. DESIGN ONLY. No P2 implementation/G4/G5 instrumentation or assets. Depends on accepted DD-1 and a proved pack entry route. Assumptions: one server/standalone authority per encounter; pack remains execution backbone, not permission for unmediated starts. Data selects declarative capabilities, never arbitrary per-boss code. Reverse by a complete encounter binding at a safe restart, not half migrating live actions.

## Entry-point closure inventory FIRST

Inventory of inspected active, potential and diagnostic starts; NOT a claim every Blueprint edge is resolved. Raw BPX paths are relative to Claude/Evidence/exports. Node names establish candidate calls; graph-qualified edges and runtime entry readback are needed before claiming a closed adapter.

| Entry / raw anchor | Current route | Required mediation / closure status |
|---|---|---|
| BT_ExampleBoss_tree.md:81/126-196/223+ | T_TryActivateAbilitiesByTags: EnterCombat, retaliation, CloseRare/Close, FarRare/Far, RangedRare/Ranged, mid/sprint attempts | Replace each start task in project-owned tree with RequestMove task, preserving attempt/fallthrough policy until separately changed. Enumerate every tag/ability candidate, including failed activation. Attempt chance is not success frequency |
| BPX_T_TryActivateAbilitiesByTags.t3d:402 | ASC Try Activate Ability called by Activate Abilities; bForceActivation passed | Wrapper must select exact ability candidate and reserve BEFORE invoking its play path. Existing success branch partly unresolved; no “LastSuccessfulAbility means success” assumption |
| BPX_BP_AdvancedAbilitySystemComponent.t3d:8096/8991+/9317+/9406+ | Try Activate Ability; separate-by-tags; by-class entry points | Inventory all callers and grant/set membership, not merely one BT task. Central adapter ABI needed or candidates remain bypass risks. No pack hook currently proven |
| BPX_GA_Attack.t3d:851; GA_MeleeBase:489; EnemyMeleeAttack:524 | PlayAbilityMontageAndWaitForEvent, ability selection/follow-up | Exact selected montage/section must be bound to accepted action. Follow-up jumps/next montage need child/branch authorization, not an unrecorded self-start |
| BPX_GA_EnemySprintAttack.t3d:737 | Sprint phase then follow-up montage | Reserve action for run-up, own movement handoff, authorize later follow-up only with current target/generation;37ms follow-up is NOT whole telegraph |
| Live GA_GS_Boss_CloseAttack/CloseRare/MidRangeAttack/SprintAttack/RetaliationAttack/LeapAttack and GS_Attack01-04/Charged/Mid01/SprintFollowUp/Retaliation/Leap | Actual abilities/montage variants in E002/CDOs/notifies | All damaging variants in definition/adapter map; three currently untracked moves cannot be excluded because Tracker has no stage |
| BPX_BP_BehaviorManagerComponent.t3d:2381/2441; StateManager/SM_Humanoid/UpdateBehavior exports | OnAbortCurrentBehaviorTask and state exit may terminate/reselect abilities | Abort and next-start paths need causal edge inventory. E00634/70 unresolved endpoints/parser contamination means callback order NOT established |
| RPGAttackTracker.cpp:234-248 / Pack/RPGBlueprintCall.h:271 | StartMove maps IDs to ability tags or dynamic PlayClip; bForce | Shared RequestAction; force may bypass availability only in existing authorized diagnostics, never death/generation/authority/safety. No new G5 start hook |
| RPGAttackTracker.cpp:148/189/209/230 | PlayClip, PlayMoveMontageForTest, direct Montage_Play, EnterCombatForTest | Diagnostic requests labeled with channel and source; production bypass forbidden. Shipping strips diagnostic entry semantics; direct animation-only observer does not produce accepted token |
| RPGBossLowSweep.cpp:25-31 | StartForTest -> Tracker StartMove A4 | Existing diagnostic channel only until separately approved natural selector. Shared planar executor owns contacts only under action token |
| RPGBossHealPunish.cpp:138/179/254 | Potion montage edge -> StartMove A5 -> poll active -> spawn javelin | Observable reaction snapshot -> authority RequestAction; release marker once under same token; projectile inherits generation/action/effect identity; no button-read reaction |
| RPGBossShockwave tick and A6 tracker active | Landing/wave starts after active observation; native damage plus pack center | Effect spawn under originating action; one central/wave resolution contract and explicit hit group, not HP-delta inference. P3 owns damage change |
| RPGBossPhases.cpp:309 | Direct phase roar montage replaces current montage; modifiers/fireballs | Lifecycle RequestAction (phase transition), precedence/queue policy, explicit cancel/finalize current move; not an attack selector bypass |
| RPGBossStagger.cpp:257/423/532/721/888/904; RiposteInput.cpp:65 | Stagger fall/down/reverse-getup, TryRiposte paired playback, lethal death activation | Shared lifecycle/paired request with both actor reservations; death/reset unconditional safety, break/riposte precedence explicit; no accidental immunity from protected attack window |
| RPGBossDormantWake/BossClips/BossDeath | Dynamic wake/idle/death/override montages and live ability arrays | Lifecycle playback binding includes owner/variant; death/reset invalidates offense regardless of montage completion |
| Boss/RPGSevarogDirector.cpp:182 | Retired direct roar/director path | Keep explicitly disabled/unbound and prove it cannot attach concurrently. If active, migrate it or fail closure; do not omit because named retired |
| Benchmark/RPGBenchmarkRunner.cpp:285-295 | Player EnterCombat/Dodge/Melee starts | Distinct player action channel; does not prove boss closure. Server validation when player-hit authority is integrated |
| RPGCombatDebug and shipped/test BlueprintCallable starts | Debug death/forced montage/action requests | Diagnostic inventory/capability gate, no new denied probe. Unknown Blueprint callers remain an explicit coverage hole until graph/asset caller scan/readback |

Closure record schema per entry: `entry_id, full_owner_class/graph/function/node/pin, raw_hash, authority_role, channel, accepted_key_location, exact_selected_variant, possible_downstream_start/cancel, bypass_policy, source/evidence_status, proof_test`. No inventory row is closed by a node count or post-start tracker observation. Search current project/pack caller graph for each public activation function, ability-tag event and montage helper before P2 acceptance. A missing export is UNVERIFIED, not proof no caller exists.

## Accepted transaction — identity BEFORE play

```cpp
struct FRPGActionKey { FGuid EncounterInstance; uint32 Generation; uint64 ServerSequence; };
struct FRPGActionRequest {
  FRPGParticipantKey Source, Target; FName MoveId, VariantId, EntrySection;
  ERPGRequestChannel Channel; TOptional<FRPGBranchPermit> Parent;
  FRPGObservedTrigger Trigger; FGuid ClientRequestNonce;
};
struct FRPGAcceptResult { EAccept Verdict; TOptional<FRPGActionKey> Key; FName Reason; };
class URPGCombatActionRuntime : public UActorComponent {
  FRPGAcceptResult Request(const FRPGActionRequest&);
  bool BindPlayback(FRPGActionKey, const FRPGPlaybackHandle&);
  void OnTraversal(FRPGActionKey, const FRPGPlaybackTraversal&);
  ECancelResult RequestCancel(FRPGActionKey, ECancelCause);
  void Finalize(FRPGActionKey, ETerminalReason);
};
class IRPGPackExecutionAdapter {
  FPlayResult StartExact(const FRPGReservedAction&);
  void StopOwned(FRPGActionKey, ECancelCause);
};
```

Authority sequence (single game-thread transaction, reentrancy guarded):

1. Deduplicate client/request nonce; resolve immutable content and source/target generation. Reject non-authority state mutation, stale world/actor/dead/untargetable/outside-arena target and invalid channel/branch.
2. Evaluate current phase, lifecycle priority, busy/recovery, resources, cooldown owner, range/cone/height/LOS, motion/path and trigger age from ONE current observation snapshot. Revalidate immediately at branch/release/contact where required; no future input knowledge.
3. Resolve exact ability/variant/section before reservation; unknown random downstream variant choice cannot be retrospectively labeled accepted. Reserve source action lane, optional paired target lane, bounded resource/cooldown reservation and allocate monotonic authoritative ActionKey BEFORE calling pack play. Publish an internal Starting state so reentrant notify/callback can resolve identity.
4. Adapter StartExact binds playback handle, montage instance/sections and token. On refusal/zero length/partial start, finalize FailedStart and refund only declared unconsumed reservations. On success transition Running and commit declared cooldown policy once. Never consume twice because pack also owns cooldown; adapter descriptor names one owner.
5. Crossed timeline executor emits effects/branches once per action/window/traversal. Hitsets keyed by action/effect/hit-group/target/generation. An accepted token is not a guaranteed hit or permission to ignore later death/stale/defense validation.
6. Terminal causes route through one idempotent finalizer; next selection only after configured recovery/lock conditions and all owned effects' declared terminal policy. Montage ended while ability remains active is not automatically successful cleanup.

States: Unreserved -> Starting -> Running (windup/commit/active/recovery substates) -> Finalizing -> Terminal. No resurrection after terminal; new traversal under same asset is not a new action without an accepted request. Reset bumps generation, invalidates tokens and finalizes all old owned resources; late notify/projectile cannot affect new generation. Replicated state contains key, identity/variant/section/start-clock/target/phase and terminal reason; clients render/interpolate, never own damage/cooldowns/phase.

## Cancellation/protected windows

Per-move data: `CancelPolicyId, protected Windows[], allowed Causes before/inside/after, partial-start refund, owned effect terminal modes, recovery release, max real duration, missing-notify deadline`. Protection blocks only declared ordinary cancels; death/reset/actor destruction/invalid generation remain unconditional safety. Stance break versus phase/riposte follows approved priority, not blanket poise immunity. Remote authority alone decides protected-window timing/cause. An external montage stop is observed and finalized with UnknownExternalStop unless evidence names the cause; do not fabricate an allowed canceller.

Ordinary branch request carries sourceActionKey+GateId+useOrdinal, bounded chain depth/time and current target/range/cone/LOS/resources. Once consumed cannot replay. Failed branch ends in declared recovery, not unbounded retry. Hold duration chosen/bounded before release per ANM003; no client input can extend a protected window forever.

Watchdog uses unscaled monotonic/explicit real-time source and a declared action budget, independent of frozen/slowed montage time; implementation must choose/test UE time API. Detects lost montage, orphaned animating ability, missing end notify, no progress/hold overrun, stale target and mismatched generation. It invokes Finalize, not a second damage/selection authority. Paused-game policy explicit. No arbitrary timeout inferred from a sampled1.388s trace.

Finalizer order: mark Finalizing/no new contacts -> invalidate branch/release permits -> close source-owned pack/native trace windows and queued effects -> cancel/retain already spawned projectiles per data policy -> end/reconcile owned pack ability -> restore only owned movement/rotation/input/camera/tag handles -> release/refund reservations once -> record Terminal and publish -> permit next action after recovery policy. Cleanup tracks handles/counts, never globally clears another system's tags/movement. Duplicate calls and callbacks at every boundary are no-ops after first ownership release.

RPGBossInterrupt::CancelOffence currently closes pack trace independently of native move id; retain that proven safeguard during migration. Do not describe untracked pack paths as lacking all cleanup. P2 adapter takes control only once compatible closure/cleanup is proved, not by disabling current safety first.

## Adapter options and G3 scratch proof

**(a) Project EnemyInfo + project BT/task:** E006 raw controller linkage proves only info->tree selection. Create new scratch assets only; temporary PIE EnemyInfoRef override with readback/cleanup, no saved map/pack mutation. Minimal task records entry, asks a diagnostic runtime reservation and calls an already permitted exact ability route; first prove task class compatibility and controller/BB setup. A second (separately approved P2) proof must cover exact chosen variant/section, pre-play identity, rejection without playback/cooldown, branch/internal sprint/follow-up/lifecycle starts and abort/terminal cleanup. A project BT cannot by itself intercept abilities started outside the tree; inventory those bridges explicitly. No G5 hook added to make coverage easy.

**(b) Pre-activation hook:** none found/proved; CanActivateAbility per-ability isn't a proven central veto. No pack edit authorized. If option(a) cannot close internal/direct starts, record missing hook/fact; propose a project-owned shared ability wrapper/controller route under a new exact reviewed scope. Never silently edit pack or claim post-play veto meets pre-play identity. G4 remains denied; causal A2 stack tracing isn't an adapter prerequisite unless a specific design depends on the caller.

Scratch must record before/after asset/map hashes, placed versus PIE info, actual controller/BT/BB/task class, gameplay readiness, callback order, acceptance allocation BEFORE montage start, reject case proving no side effects, cleanup and restoration. Missing readback is EDITOR NEEDED; design proceeds without inventing a result.

## A2 as transaction requirement, not bug-specific patch

E005 corrected:9 pre-window Windup terminations,1 Active1.99,1 Recovery replacement2.80;5/6 first samples0.03-.06, ongoing ability about1.388s observed, canceller unknown. P2 must demonstrate each accepted A2 has either supported traversal/recovery or bounded terminal cleanup, no stuck ability/selection lane, no damage after terminal and a known permitted/unknown external cancellation classification. Do NOT hardcode special A2 stop suppression, reproduce a10/11 ratio, or blame equip/service without evidence. Replay frozen samples into transaction tests, then fresh natural observations with config provenance; leave DD-1 execution untouched before P2 approval.

## Files/data and proving tests

Proposed new shared units: Player/RPGCombatActionRuntime.*, Pack/RPGPackExecutionAdapter.*, AI/RPGRequestMoveTask.*, Player/RPGCombatResources.*, Player/RPGCombatTimelineExecutor.* plus tests. Definitions gain cancellation/reservation/cooldown-owner/branch/terminal/watchdog/authority structs. Narrow migrations: TrackerStartMove/PlayClip, HealPunish/LowSweep/Shockwave, phase/stagger/riposte/death/wake request bridges and project BT binding. No per-MoveId executor class or new combat code per boss.

Automation: reentrant start, reject/no side effects, exact-variant bind mismatch, start failure after reservation, duplicate request/branch/release, same montage restart, forced diagnostic safety, every terminal cause twice, stale generation, crossed windows/lowFPS/rates, lost ability/montage and watchdog, two actors/shared definitions. PIE: all live pack/native/branch/lifecycle entry cases; accepted key exists at earliest effect callback, no double damage/motion owner, pack abort cleanup and next legal action after recovery. Network: server-only accept/HP/posture/cooldown/phase, two clients duplicate/out-of-order commands and80/150ms/packet loss with same action identity; no remote target homing. Performance/log caps measured, not guessed.

Evidence limit: raw source/call nodes inspected, E006 chains provisional; no closure/adapter/behavior/network proof executed. P2 remains gated by accepted DD-1 and reviewed exact scope. No owner decision invented; unresolved editor feasibility is documented, not awaited here. Continue WP5.
