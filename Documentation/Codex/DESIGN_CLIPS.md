# B9 — Authored Close Clips and Dormant/Wake Design

## Scope and Status

This is a read-only design for wiring the imported authored sequences without editing any pack asset or deleting an asset referenced by the pack. No editor inspection or runtime test was run for this document.

The available authored sequences are under `/Game/OneBossFight/Boss01/Animations`:

| Gameplay move | Authored sequence | Delivered duration | Required commit |
|---|---|---:|---:|
| A1 | `AN_Boss01_A1_QuickSlash` | 1.20 s | 0.33 s |
| A3a | `AN_Boss01_A3a_Combo1` | 0.80 s | 0.38 s |
| A3b | `AN_Boss01_A3b_Combo2` | 1.3333 s | 0.13 s |
| A2 | `AN_Boss01_A2_Raise`, `AN_Boss01_A2_ApexHold`, `AN_Boss01_A2_Slam` | three-stage | decide from authored contacts |
| dormant / wake | `AN_Boss01_DormantIdle`, `AN_Boss01_Wake` | 5.0 / 3.5 s | n/a |

`AN_Boss01_A1_QuickSlash.uasset`, `AN_Boss01_A3a_Combo1.uasset`, `AN_Boss01_A3b_Combo2.uasset`, `AN_Boss01_DormantIdle.uasset`, and `AN_Boss01_Wake.uasset` exist in that directory. They are `UAnimSequence` assets, not pack ability montages.

## Present Pack Path

1. The boss behaviour tree asset is `Content/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/BT_ExampleBoss.uasset`; its binary payload does not expose a trustworthy task class/name through static string extraction. The static dependency that selects the close ability is instead the combat style asset `.../ExampleGreatSwordBossCombatStyle.uasset`, which references `GA_GS_Boss_CloseAttack`.
2. `GA_GS_Boss_CloseAttack` owns the four montage references `GS_Attack01_Montage` through `GS_Attack04_Montage` (binary package strings in `Content/.../GA_GS_Boss_CloseAttack.uasset`). The known mapping is A1=`GS_Attack03_Montage`, A1b=`GS_Attack04_Montage`, A3a=`GS_Attack01_Montage`, A3b=`GS_Attack02_Montage` (`Source/OneBossFight/Player/RPGAttackTracker.cpp:40-60`).
3. The four pack montages contain `ANS_CollisionTrace`; `GS_Attack01_Montage` also has `AN_PerformFollowUp` (`Content/.../Animations/AI/GreatswordBoss/GS_Attack01_Montage.uasset`, static strings). This is why simply playing an authored sequence loses the pack trace and likely loses the A3 follow-up.
4. `URPGAttackTracker::StartMove(TEXT("Close"))` intentionally activates `Ability.Melee.Close` instead of playing an animation, because the ability supplies attack data for the damage trace (`Source/OneBossFight/Player/RPGAttackTracker.cpp:228-239`). The tracker presently observes the pack montages by name, adjusts their play rate for `rpg.CloseTelegraph`, and derives commit/active/recovery from its own `FRPGAttackTiming` rows (`:57-60`, `:275-303`).

### Required Owner Editor Read

Before implementing, use the editor bridge to dump `GA_GS_Boss_CloseAttack_C` functions/properties and inspect the `BT_ExampleBoss` close branch. Record: (a) the exact BT task/service which requests `Ability.Melee.Close`, (b) the concrete property type/name holding the four montages, (c) whether the ability selects by array index or by montage notify, and (d) every notify/state class, trigger time and duration on all four source montages. Static package strings prove the references and the two notifier class names above; they do **not** prove graph execution order or timings.

## Smallest Safe Close-Clip Integration

### Recommended: project-owned montage replacements on the live ability instance

1. Create four new **project-owned** montages in `/Game/OneBossFight/Boss01/Animations/Montages`, each using the same slot read by `RPGBossClips::SlotName()` from `GS_Attack01_Montage` (`Source/OneBossFight/Player/RPGBossClips.h:19-30`):
   - `AM_Boss01_A1` from `AN_Boss01_A1_QuickSlash`
   - `AM_Boss01_A3a` from `AN_Boss01_A3a_Combo1`
   - `AM_Boss01_A3b` from `AN_Boss01_A3b_Combo2`
   - retain the pack montage for A1b until an authored follow-up is delivered.
2. Add a small project component that locates the **created** `GA_GS_Boss_CloseAttack_C` ability via the existing reflection helpers, validates the exact montage-array property discovered in the editor read, and substitutes only the corresponding entries on that ability instance. It must restore the pack entries on `EndPlay`, reset, death, and any failed validation. It must never mutate `GA_GS_Boss_CloseAttack.uasset` or the pack montage assets.
3. Keep `URPGAttackTracker::StartMove(TEXT("Close"))` unchanged, so the behaviour tree still chooses range/branch state and the pack ability still owns attack-data selection, trace target creation, cancellation, and follow-up dispatch.
4. Extend the tracker mapping to recognize the three new montage names and set the A1/A3 timing rows from the authored notify timing, not from the current pack row. Turn off `rpg.CloseTelegraph` for a replacement clip if its authored windup already meets Freeze; otherwise the rate adjustment would double-stretch it.

This is smaller and safer than intercepting an already-playing montage: a post-start swap has already allowed the original `ANS_CollisionTrace` window to begin, can leave the ability waiting for the original montage, and cannot guarantee a clean A3 chain. It is also safer than replacing pack references: package changes would violate the project rule and risk every pack consumer.

### Rejected alternatives

- **Play a dynamic montage from `URPGAttackTracker`: reject.** `PlayClip` is appropriate for A4/A5 because those moves own their damage components, but the tracker explicitly documents that a bare close montage does not hurt (`RPGAttackTracker.cpp:230-235`).
- **Modify the pack montage or the pack ability CDO: reject.** It violates the no-pack-edit rule and would alter all instances.
- **Intercept after the tracker observes `GS_Attack*`: reject.** The observed montage can already be active/trace-enabled and the swap makes pack cancellation/follow-up order undefined.

## Authored Timing and Damage Windows

The authored sequences need project-owned montage authoring; animation duration alone does not establish gameplay damage.

1. Add an `ANS_CollisionTrace` notify state only if the owner verifies it is a reusable pack notify that accepts project-owned montage placement. Copy the pack source state’s settings after inspection; do not guess socket names, trace radius, attack-data source, or state duration.
2. Preserve `AN_PerformFollowUp` on the A3a montage only if inspection proves it is the mechanism that starts A3b. Otherwise the existing close ability must expose a project-owned, explicit branch handoff. A3b must retain `URPGAttackTracker::BranchAllowedNow()` semantics at its stage start (`RPGAttackTracker.cpp:396-413`).
3. Use authored contact frames to set `CommitTime`, `ActiveStartTime`, `ActiveEndTime`, and `RecoveryEndTime`. The delivered provisional commit points are A1 0.33, A3a 0.38, A3b 0.13; they are not active-window times. The Freeze requires montage-synchronized commitment, not an inferred interpolation value (`Documentation/Master_Design_Freeze_v1_2_AI_Implementation_Ready.md:563-581`).
4. `Scripts/Editor/make_death_montage.py:20-24` is the correct project precedent: create a montage in project content, copy the pack slot through `RPGMontageUtils`, then author project notifies. It is not permission to modify the source pack montage.

## Dormant and Wake

`URPGBossEncounter::Sleep()` only stops behaviour and marks the boss dormant (`Source/OneBossFight/Player/RPGBossEncounter.cpp:224-232`). `Wake()` clears dormancy and restarts behaviour immediately (`:256-266`). No dormant or wake sequence is currently played.

Recommended project-owned extension:

1. In `Sleep()`, play `AN_Boss01_DormantIdle` as a looping dynamic montage through `RPGBossClips::Play`; retain the returned montage pointer.
2. In `Wake()`, stop the dormant loop with a short blend-out, play `AN_Boss01_Wake` once, and defer `ResumeBehaviour()` until it ends. Maintain an explicit `Waking` flag that blocks `URPGAttackTracker` and all attack starts until the clip completes.
3. Every interrupt path—reset, death, phase transition, stance break, EndPlay—must stop both clips and clear `Waking`, then use the existing resume/reset owner. Do not let a dormant loop remain when the pack AI returns.
4. Do not make a new gameplay montage until the owner verifies the two sequence contact poses and whether the wake needs root motion. The existing boss clip wrapper provides the required slot and dynamic-montage mechanism (`Source/OneBossFight/Player/RPGBossClips.h:46-59`).

## Test Plan

Add the following after implementation; all need fresh PIE evidence.

| Driver / test | Evidence |
|---|---|
| `pie_authored_close_clips.py` | Force the pack close ability and observe A1/A3a/A3b montage identity, one commit, one trace window, health loss once per stage, no source pack montage, branch allow/deny on A3b, interruption/reset cleanup. |
| `pie_telegraph.py` extension | Measure authored commit-to-active windows at `rpg.CloseTelegraph 0` and default 0.4; prove no double-stretch and the Freeze 0.35 / 0.40 s tell. |
| `pie_attack_rules.py` extension | Track every authored stage, no duplicate launches, correct commit/active/recovery, and no attack during dormant/wake. |
| `pie_dormant_wake.py` | Sleep loop begins, gate wake plays once, AI starts only after wake completes, reset/death during wake leaves no montage or held brain. |
| automation | Pure mapping/timing validation for the authored rows; PackWiring-style load checks for three project montages and both idle/wake sequences. |

## Decision Required

Approve the live-instance montage replacement strategy only after the editor owner supplies the exact `GA_GS_Boss_CloseAttack_C` montage property and notify settings. If the close ability binds its damage to exact source montage assets rather than to notify/state data, do **not** wire replacements; choose a project-owned custom close-attack component instead and retain the pack close ability as a fallback.
