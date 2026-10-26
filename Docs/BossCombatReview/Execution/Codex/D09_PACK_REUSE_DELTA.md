# WP-7 — pack reuse reassessment delta

2026-10-25, Codex; C110 addendum after WP6. DESIGN / EVIDENCE-LIMITED DELTA to D05 and D09_HIT-012/DEF-005/ANM-006/SEL-008. Original documents preserved. All83 requirements/proving tests unchanged. No pack edits, ability grants, asset writes, engine/export/build/PIE run by Codex. **AG12 inventory is not present at this review time**; no agent report is invented or awaited to finish the safe offline analysis. Reconcile it by exact revision/hash when available.

## Assumptions

Reuse is preferred where its actual semantics/compatibility can be proved on the Ember Warden. File presence or inherited CDO fields are not successful activation, complete capture/defense, or network safety. Default100% activation chance is not a desired success frequency. Reduce a subtrack estimate only conditionally; do not reduce required mechanic/test coverage. Reversal uses old complete project binding at startup, not stripping granted abilities from a live captured pair.

## Independently inspected evidence

Source file inventory confirms AI GA_AI_BlockGuard, GA_EnemyDodge, GA_EnemyGrabStart/Attack, GA_EnemyParried, GA_EnemyHeal; victim GA_GrabVictim; DefaultGrabAttackData; ParryFramesNS; player guard/parry/dodge; GA_DodgeBase and relevant animation assets. Existing frozen CDO exports provide stronger but still partial evidence:

- `CDO_GA_AI_BlockGuard.t3d`: Ability.Block, owned Status.Blocking, held2s, melee max350/ranged900, cooldown0, CostGameplayEffect=None, cancels Ability.Sprint. Therefore a finite hold candidate exists, but cost/reaction budget/directional/failure/guard-break semantics are NOT established.
- `CDO_GA_EnemyDodge.t3d`: Ability.Dodge, cooldown10, CostGameplayEffect=None, DodgeMontage empty, directional flag false. A base capability candidate exists; actual live arrays/direction/iframes/movement/safety are unknown and empty CDO alone cannot prove unusable (runtime setup may populate it).
- `CDO_GA_EnemyGrabAttack.t3d`: Ability.Grab.Attack and real DefaultGrabAttackData reference, reset/start position0, cost/cooldown absent. Does NOT establish capture eligibility, victim alignment/input/collision release, impact-once or abort safety.
- `CDO_GA_EnemyHeal.t3d`: Ability.Heal/cooldown15, HealGameplayEffect=None. Not an implemented useful heal, and not permission to add boss healing as fallback.
- `ExampleGreatSwordBossCombatStyle.t3d`:11 boss grants include melee/enter/exit/hitstun/turn/death, not these defense/grab/heal candidates. `ExampleGreatSwordBoss_info.t3d` binds this style and the pack boss BT. Thus reuse currently needs project-owned data/binding integration; it is not already active on this boss.
- Literal filename matches such as T_Explosion_WarpMask/SM_Impact_Warp are VFX, not evidence of motion warping. No usable motion-warp contract has been established by this search. Root-motion travel or actor relocation is not automatically ANM006-compliant early capped warping.

## Cost/design delta — no row is trimmed

| Row / D05 prior | What may be reused | Work remaining even if reuse succeeds | Conditional revised costing |
|---|---|---|---|
| HIT012 LARGE | Grab start/attack/victim abilities, attack-data schema and paired animations if discovered compatible | WP4 pre-play two-actor reservation, truthful target/impact identity, finite hold/release, handle-scoped input/collision/motion restoration, all interruption/death/reset/timeout/disconnect cases, authority and replication, visible tell/miss/recovery | Content/executor authoring may fall from large to medium; integration/paired lifecycle/network proof remains large-risk until raw graphs/live test. Overall **MEDIUM-LARGE candidate**, not accepted downgrade |
| DEF005 LARGE | AI guard/dodge plus parry-related notifies/reaction/player abilities | Guard cost/cooldown/direction/break; actual dodge montage/iframes/path; proactive AI parry distinct from being parried; all three fallible/readable/punishable; request adapter and P3 shared defense result, server authority | Guard/dodge implementation subtracks potentially medium. AI parry unresolved, therefore overall **MEDIUM-LARGE candidate** if all three reusable, otherwise LARGE |
| ANM006 MEDIUM-LARGE | Any discovered supported root-motion/warp window/target infrastructure | Actually perform early bounded warp, path/ledge/slope validation, target freeze before commitment, one movement owner and all cleanup/remote tests | **MEDIUM-LARGE unchanged pending evidence**. No “no warp” exception, no downgrade from visual Warp file names |
| SEL008 small incremental / medium integrated | Existing BT MoveTo/wait/reacquire and possibly reusable idle/turn clips | Shared explicit empty reason, finite query/retry/progress budgets, arbitration versus protected action, safe reset policy, target/generation cancellation, authoritative navigation | **SMALL incremental / MEDIUM integrated unchanged**; simple wait/reposition is sufficient when proved. Reused heal not required and not proposed as default |

QA008 remains cross-cutting LARGE; unused pack abilities may introduce additional replicated/callback dependencies rather than reduce networking risk. ANM003/AWR008/SEL004 are unaffected by names found. D09 structs and tests remain acceptance contracts; replace internal executor implementation with a shared adapter where reuse passes, not new per-boss code or a BP-name exemption.

## Project-owned grant/binding route

1. Prove G3 route(a) first: new scratch EnemyInfo + minimal BT, temporary PIE instance override, exact controller/tree/BB/task readback, restore on exit. G3 does not authorize saved map/style changes for production or editing the pack.
2. Later, under reviewed exact scope, create a project-owned combat-style instance with the pack style class. Preserve the existing11 ordered grants, anim-layer/enum/attribute/state/BB references, then add the chosen capability bindings only in a test/versioned candidate profile. Reference unchanged pack classes or shared project wrappers; no pack class/asset overwrite.
3. A project-owned EnemyInfo names that style and project BT. Explicit encounter binding chooses it before startup; do not patch a live ability list and infer grants worked. Pack startup may instantiate/copy defaults; read actual granted ability class/config/owning actor/tag/cooldown/montages after initialization and after reset.
4. Register every newly granted activation/branch/effect/abort path in WP4 closure. Route BT and native defense/grab requests through authority accepted-action reservation BEFORE pack playback. Internal grab victim activation, sprint/defense cancellation and combo events must propagate the same token or fail the proof. Wrapping only the initial task is insufficient.
5. Avoid double cost/cooldown/damage/iframe owners. Where pack already owns an operation, adapter declares that owner and records observed result; where it lacks a required budget/cleanup/authority contract, shared wrapper implements it under later phase scope. No global CancelAll or disabling old trace cleanup as a shortcut.

## Exact initial export jobs for Claude (read-only, not executed)

Use existing p0_export_text mechanism after the editor is free, NEW versioned filenames and hashes; never overwrite initial evidence. For each Blueprint below export BOTH full asset text/graph objects with graph-qualified LinkedTo endpoints AND generated-class CDO (class path is `asset_path + '.' + leaf + '_C'`). For data assets export live asset text; for every referenced montage/sequence export length, skeleton, slots/sections/segments, rate, blends/root-motion settings and all notify class/payload/times. A node inventory is not a resolved edge proof.

AI Blueprint assets (prefix `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/AI/`):

1. GA_AI_BlockGuard
2. GA_EnemyDodge
3. GA_EnemyGrabStart
4. GA_EnemyGrabAttack
5. GA_EnemyParried
6. GA_EnemyHeal
7. GA_EnemyTurnInPlace
8. HitReactions/GA_EnemyBlockReaction

Other exact assets:

9. `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/Shared/HitReactions/GA_GrabVictim`
10. `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/Shared/HitReactions/GA_BlockReaction`
11. `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/Player/GA_PlayerGuardBlock`
12. `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/Player/GA_PlayerParry`
13. `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/Player/GA_Player_Dodge`
14. `/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/Abilities/GA_DodgeBase`
15. `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Animation/AnimNotifies/ParryFramesNS`
16. `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/DataAssets/AttackData/DefaultGrabAttackData`
17. `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_DodgeCost`
18. `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/States/SM_BlockStanceEnemyImpactDecision`
19. `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/States/SM_BlockAttackEnemyImpactDecision`
20. `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/BT_ExampleBoss` (runtime task/decorator/service object tree)
21. `/Game/AdvancedARPGCombat/AdvancedCombatFramework/AbilitySystem/BP_AdvancedAbilitySystemComponent` (TryActivateByTags/by-class/separate/created filter, cancel/end/animating ownership)
22. `/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/BP_MasterEnemy` (info/style/ability initialization/grab/defense runtime events)

Exact known animation candidates to export now:

23. `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/Defend/Deflect_InPlace_AI_Montage`
24. `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/Defend/Ability_AI_Block2_Montage`
25. `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/Defend/BlockLoop`
26. `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle_Montage`
27. `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage`

Then dependency closure, not a guessed fixed montage list: enumerate all montage/sequence/curve/notify/GE/style references in jobs1-22 INCLUDING inherited and runtime-set arrays; emit the full resolved object path, class, hash and referencing property/function for each; export those referenced animations/notifies. Explicitly mark empty CDO arrays versus runtime-populated arrays. Query for actual MotionWarping component/target/modifier references in this closure and installed project/plugin settings; no ability/clip named Warp was established by file search. Capture live weapon/item/skeleton/capsule/mesh scale and actor role for a candidate test on the boss only after approved binding.

Graph questions to resolve: guard angle/resource drain/block-break/end; dodge iframe begin/end/motion direction/path; grab target/victim selection/alignment/impact/release and every abort; parry caller/actor eligibility/finite window and defense results; ASC ownership/cooldown/cancel replication; any player input dependency or player0 assumption; target/generation and timeout behavior. Exporting a parent CDO alone is not the answer.

## Editor-needed test gate and evidence limits

Claude's sequence (baseline/automation -> step1 build/witnesses -> scratch route -> exports) is respected; no probe is run now. After export review, test the reusable capability on the boss under a project-owned candidate binding, then apply the SAME D09 per-row automation/PIE/two-client evidence. Include rejection/no-start, reset/death/phase/stagger, missing-notify/timeout, stale target and disconnect, not just a successful montage. Do not call the row IMPLEMENTED until all material clauses pass. Bring AG12 into this delta by evidence IDs when delivered; its file-name inventory can reduce search, not prove semantics.

Current conclusion: credible reuse candidates for grab/guard/dodge, possible parry infrastructure and existing locomotion; **unknown completeness and warping**. D05 estimates become conditional branch estimates above, not falsely settled cheaper sizes. No new owner decision required for this reassessment; actual readbacks remain EDITOR NEEDED and do not stop offline delivery.

## WP16 / X-T5 graph answers, 2026-10-26

Read PR2/3 raw exports and a new graph-qualified node/pin edge index (`WP6Support/pack_graph_review.mjs`, generated `pack_graphs.json`, each file SHA256 included). Identity uses asset/graph/node + pin GUID, never first node with matching short name. Compiled MERGED/ExecuteUbergraph and authoring EventGraph copies are distinct representations, not multiple runtime calls. Linked input-pin DefaultValue is **not** its effective value. Zero unresolved links in the indexed guard, block reaction, victim and actor-sync graphs; GrabStart4 and PlayerParry2 unresolved endpoints remain, and macros/inherited implementations still require explicit inspection. Resolved edge count is not end-to-end behavioral proof.

### Guard direction, drain, break, end

- `exports/PR2_SM_BlockStanceEnemyImpactDecision.t3d:464-485`: WasAttackBlocked reads Blackboard.Key.AngleToTarget into InRange[-45,+45], inclusive; result joins BooleanAND alongside CanAttackBeBlocked at447-453. This is a **90-degree target-angle condition**, not measured incoming-weapon direction or arbitrary spherical block coverage. Do not transplant as the final D09 attack-source directional test without checking its blackboard authority/freshness.
- `PR2_GA_AI_BlockGuard.t3d:2370-2377`: obtains Stamina extended attribute; linked data feeds Modify Regen Percent at2360-2367 (100 on this end path). Presence of a stamina reference/regen modification does not establish per-hit drain. Cost GE is None in CDO:26; no inference of free blocks universally because damage can charge stamina elsewhere.
- `PR2_GA_EnemyBlockReaction.t3d:2515-2559`: current Attribute.HitCount compared >= max Attribute.HitCount, feeding BooleanAND. IncrementHitCount graph2392-2447 reads, increments and writes HitCount. CDO:4 bHitStunImmuneOnMaxHitCount=False. Therefore hit-count infrastructure exists; not demonstrated stamina-zero guard-break contract or reset lifetime. Parent impact decision / damage effect owns missing semantics.
- `PR2_GA_AI_BlockGuard.t3d:2422-2437`: nonlooping timer StopBlocking (input Time pin0.15 must be traced if connected); OnAbilityEnd calls parent then branch2228-2246 and montage stop path exists. HeldTime2s remains CDO6, not evidence that every terminal route restores all regen/state tokens. No product cost/break policy certified.

**EDITOR NEEDED exact closure:** `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/States/SM_ImpactDecision.SM_ImpactDecision` (CanAttackBeBlocked and directional/defense result implementation), `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/States/BP_EnemyImpactDecision.BP_EnemyImpactDecision`, `/Game/AdvancedARPGCombat/AdvancedCombatFramework/AttributesSystem/Objects/BP_BaseExtendedAttribute.BP_BaseExtendedAttribute` (Modify Regen Percent semantics), plus the actual damage GE(s) returned by the runtime block decision. Export referenced full paths rather than guessing a guard-break GE name. Read current/max HitCount and stamina before/after blocked hits/end/reset on the approved test binding; no new capability grants implied.

### Dodge iframe and path

- `PR2_GA_EnemyDodge.t3d:348-357`: Get Ability Montage returns the exact struct consumed by Play Ability Montage134-146. It is not hard-bound in this graph to the exported Dodge_To_Idle candidate. CDO DodgeMontage empty remains an unresolved binding, not proof no implementation exists.
- `PR2_Dodge_To_Idle_Montage.t3d:46`: candidate iframe state duration0.699774 starting at zero local time;48 movement-cancel1.706624..2.333334;49 length2.333333 and50 RateScale2. These are montage-local endpoints, **not real elapsed windows**. Nominal if no other modifiers: length1.1666665s and iframe0.349887s. Effective montage/segment/ability rate and phase modifiers must be observed.
- `PR3_ANS_iFrames.t3d:242-250,287-295`: notify end removes Status.Invulnerable and begin adds it to receiving character. This proves tag routes, not overlapping-window token safety or cleanup after lost end.
- No path/ledge/slope safety proof from this graph. Query full montage-selected sequence root-motion data and parent DodgeBase/playback implementation; a candidate roll clip is not a validated safe boss evade.

**EDITOR NEEDED:** actual GA_EnemyDodge instance DodgeMontage array and selected full montage/sequence/section/rate, root-motion settings and path collision during an approved candidate test; export `/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/Abilities/GA_DodgeBase.GA_DodgeBase` inherited movement/selection routes and `/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AnimNotifies/ANS_MovementCancel.ANS_MovementCancel` cleanup. Existing PR2 DodgeBase export can answer static subsets; runtime path remains required.

### Grab selection, WHERE montages come from, alignment and release

- Attacker source is the ability's **inherited AttackMontages**, not DefaultGrabAttackData. `PR2_GA_EnemyGrabAttack.t3d:933` delegates Get Ability Montage to parent. `PR3_GA_EnemyMeleeAttack.t3d:722-732,1005-1025` selects from AttackMontages, with index/random inputs; EventGraph279-288 feeds returned struct to PlayAbilityMontageAndWaitForEvent. GrabAttack3206-3210 reads same array for index limits. Exported CDO omitting this array is not proof of a populated binding or of no possible inherited default. Source of actual populated value is **still unresolved**.
- Victim source is **GrabMontages map keyed by attacker's combat-style enum**, with index/random selection: `PR2_GA_GrabVictim.t3d:4190-4274`; GetGrabMontage4932-4943 yields selected struct, then GrabMontage assignment. CDO8 is empty map and9 has null montage/sync-task; no pair is proved for Boss01.
- Target/activation route: GrabAttack Perform Grab Victim1384-1427 gets focused combat target; SetGrabData2960-2971 precedes Try Activate Ability through exec pin2965. Args include attacker style, grab index, current montage position and reuse-position flag. Do not equate default pin literals with linked runtime inputs.
- Victim alignment: CreateTask4767-4775 then Start Sync4704-4716 takes selected profile distance/rotation/speed/facing; `PR3_BP_ActorSyncTask.t3d:1923-1934` derives target transform, interpolation path reaches actor location setter. Compiled copy1220-1231 has **bSweep=false** on SetActorLocation. This is real alignment infrastructure, not a collision-safe capped MotionWarping guarantee. Missing wall/ledge/size limits are material for HIT012/ANM006.
- Victim OnAbilityEnd4464 and Cancelable reset4454/4474, state reset4498/4623, montage stop4562 and EndAbility4865 show cleanup fragments. They do not prove both actors release input/collision/movement exactly once on death/reset/missing notify/disconnect; sync task lifetime and ownership must be inspected end-to-end. No claim that every abort route is complete.

**EDITOR NEEDED exact readback:** attacker GA_EnemyGrabStart/GA_EnemyGrabAttack instance AttackMontages with source property owner (CDO/inherited/runtime setter) and victim GA_GrabVictim instance GrabMontages + selected full pair/sync-task class. Export those returned montages/sequences and all referenced notify payloads plus `/Game/AdvancedARPGCombat/AdvancedCombatFramework/AbilitySystem/Abilities/BP_AdvancedGameplayAbility.BP_AdvancedGameplayAbility` parent end/cancel/timer logic. Export a subclass only if runtime class identifies one. No guessed unarmed montage path and no "0% code reuse" conclusion.

### Parry windows and results

- `PR2_ParryFramesNS.t3d:654-672,743-761`: notify begin sets bParryFrames and Status.ParryActive; end clears both. Window duration is authored by the actually selected montage, not this class. `PR2_GA_PlayerParry.t3d:2041-2053` waits for GameplayEvent.Parry; CanActivate1713-1721 checks Status.ActionCommitted. Player-class ability names do not by themselves prove all logic is player-only, nor show proactive AI parry.
- Current index leaves2 PlayerParry exec endpoints unresolved; cannot certify event->parried-reaction result/counter graph by member-name list alone. GA_EnemyParried is victim reaction, not a selector for an AI's anticipatory parry.

**EDITOR NEEDED:** actual selected ParryMontages array, corresponding montage notify start/end, source of GameplayEvent.Parry and impact decision result routing; export missing linked nodes as graph-qualified full object/pin identities and parent SM_ImpactDecision. Then distinguish successful counter, whiff, late/early, unblockable and interruption. DEF005 remains all three defenses required, not waived because two are reusable.

### E010 run4 repeated tree: narrower corrected explanation

Scratch tasks return Failed/Succeeded synchronously (`Source/OneBossFight/Scratch/RPGScratchRouteA.cpp:80`), no latent wait or stop-tree task. Local UE5.5 source `Engine/Source/Runtime/AIModule/Private/AIController.cpp:1013` explicitly calls StartTree(..., **EBTExecutionMode::Looped**); BehaviorTreeComponent.h:137 default is also Looped. Thus a second root pass is expected-capable without any special controller restart, and raw run4 ids3/4 are consistent with ordinary looping. `BPX_BP_BaseAIController.t3d:2477` also contains RestartLogic, but a static node plus repeated entries DOES NOT establish it fired in this run. E010 wording "the controller restarts the tree" is too specific.

**EDITOR NEEDED only to distinguish actual cause:** trace RunBehaviorTree/RestartLogic callsites plus tree start/stop/root-pass timestamps for scratch controller and task entries, or a separately authorized single-run-tree fixture. Feasibility remains proved. Exactly-once execution remains unproved; no live fix authorized by this review.

## WP16 disposition

Each requested subject now has concrete graph anchors or an exact readback/export request. Static review delivered, editor-complete reuse acceptance OPEN. Costings remain conditional. No pack asset changed, no Codex editor/build, no defense/grab/warp implementation or P1/P2 start implied.
