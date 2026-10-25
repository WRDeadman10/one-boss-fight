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
