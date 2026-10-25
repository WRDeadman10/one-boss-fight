# AI and combo audit

## Proven inherited graph, with provenance limit

Saved/asset_text/GA_EnemyMeleeAttack.t3d exports /Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/AI/GA_EnemyMeleeAttack. It is a2026-10-19 export, not a fresh graph dump; current CDO/BT values remain U02/U03.

Graph connections inspected:

- **EventGraph:** ActivateAbility (K2Node_Event_3) -> CommitAbility (K2Node_CallFunction_20) -> EnterStateByTag (K2Node_CallFunction_16) -> K2_ClearTimer (K2Node_CallFunction_10) -> Get Ability Montage (K2Node_CallFunction_19). The returned F_AbilityMontage.AnimMontage feeds IsValid macro K2Node_MacroInstance_28. Valid -> PlayAbilityMontageAndWaitForEvent (K2Node_CallFunction_0) -> IncrementAttack (K2Node_CallFunction_4) -> index-vs-Array_LastIndex check -> ResetAttack on overflow. Invalid -> FailAbility (K2Node_CallFunction_27). [Export:227](C:/UnrealProject/OneBossFight/Saved/asset_text/GA_EnemyMeleeAttack.t3d:227), [Export:270](C:/UnrealProject/OneBossFight/Saved/asset_text/GA_EnemyMeleeAttack.t3d:270), [Export:373](C:/UnrealProject/OneBossFight/Saved/asset_text/GA_EnemyMeleeAttack.t3d:373), [Export:523](C:/UnrealProject/OneBossFight/Saved/asset_text/GA_EnemyMeleeAttack.t3d:523).
- **Can Activate Ability?:** BooleanAND receives IsCombatEnabled?, IsValid(GetFocusedCombatTarget), NOT IsAbilityActive(GetAnimatingAbility), and NOT IsCooldownActive?. [Export:575](C:/UnrealProject/OneBossFight/Saved/asset_text/GA_EnemyMeleeAttack.t3d:575). This establishes useful gates in the export; it does not prove team/life/arena/path validation inside callees.
- **Get Ability Montage:** RandomIntegerInRange(0, AttackMontages.LastIndex) -> L_RandomIndex. LastAttackIndex+1 wraps; equality of random and last chooses wrapped next instead. bRandomIndex selects between supplied Index and this random/no-immediate-repeat result. The selected index is bounded and passed to SetLastAttackIndex before returning the array entry. [Export:790](C:/UnrealProject/OneBossFight/Saved/asset_text/GA_EnemyMeleeAttack.t3d:790), [Export:901](C:/UnrealProject/OneBossFight/Saved/asset_text/GA_EnemyMeleeAttack.t3d:901), [Export:934](C:/UnrealProject/OneBossFight/Saved/asset_text/GA_EnemyMeleeAttack.t3d:934), [Export:871](C:/UnrealProject/OneBossFight/Saved/asset_text/GA_EnemyMeleeAttack.t3d:871).
- **OnAbilityEnd:** conditionally resets the state manager to default. ResetAttack event sets the attack index. [Export:317](C:/UnrealProject/OneBossFight/Saved/asset_text/GA_EnemyMeleeAttack.t3d:317), [Export:506](C:/UnrealProject/OneBossFight/Saved/asset_text/GA_EnemyMeleeAttack.t3d:506). Internals of CommitAbility, FailAbility, montage callback and follow-up event dispatcher are not exported here.

Thus some anti-repeat behavior exists in historical evidence. Calling the entire boss “uniform random with no memory” would be wrong. Calling it normalized utility/near-best seeded AI would also exceed the evidence.

## Ordinary selection and movement remain partly opaque

Package references identify BT_ExampleBoss, BB_Base, S_CalculateTargetValues, S_RotateCharacter, S_UpdateBehavior, S_UpdateTrackTarget, T_Strafing, T_TryActivateAbilitiesByTags, T_WaitAnimatingAbilityEnd and D_ChanceCondition. They do not reveal connected branches, thresholds, abort modes, cooldown decorators, intervals or probabilities. SM_Humanoid_CombatBehavior and BP_EnemyImpactDecision are referenced by boss info. These generic assets must be inspected, not dismissed as unused.

The style includes CloseAttack, CloseRare, LeapAttack, MidRangeAttack, SprintAttack, RetaliationAttack, Enter/ExitCombat and TurnInPlace. Tracker coverage is not proof the other abilities are disabled. U03 must export created abilities, actual chosen montages and start counts in an autonomous encounter.

## Native conditional combo layer

A1b/A3b are marked bBranchStage. At the first observed frame of that stage, BranchAllowedNow reads current player center distance and boss forward dot: within400cm and+/-60degrees. A denied montage stops with.15s blend, is remembered as DeniedMontage, and native phase returns None with instance counter decremented. [Tracker:172](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:172), [Tracker:411](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:411).

Strength: moving behind or away after the initial attack can change continuation. C-84 reports four real denials followed by7/7 front hits; this counters the old claim that denial inherently damages later poses.

Limits:

- This is a stage-start veto, not a pre-play authored gate transaction.
- No native graph-edge ID, combo ID, depth, hit-confirm, edge cooldown or pressure timer.
- Proximity permits continuation on whiff unless pack logic adds another rule.
- Denial does not itself author a minimum recovery.
- Current exact notify links and whether the first hit has closed before successor launch remain U06.

Recommend first documenting existing successor edges and a single-use event contract. Do not introduce a new full-pool selector inside combo windows.

## Reactions and attack availability

A5 observes an actual player montage, refuses while busy, validates400–1000cm/LOS/cooldown, and rechecks LOS at release. It is not an instantaneous damage counter: .45s tell plus flight allows evasion by design. However, montage-start reaction is immediate, legal starts are deterministic, and remaining heal recovery is not evaluated. Release-time target snapshot means the throw tracks before release, not during flight.

A4's mechanic is present but no native autonomous scheduler calls it; KI-067 records that the BT does not select it. A forced StartForTest is not selection coverage. Integrate only through the existing pack legal start boundary after U02, never by adding another competing per-tick planner.

## Recommended decision work

P0 export current BT/controller/abilities and log real distributions. P5 add an explainable gate-time context and reasons to the existing activation path, then connect A4 with range/angle/state/cooldown and bounded frequency. Only add family-history decay or utility terms if controlled long runs show a concrete problem. Preserve pack abilities, notify-driven damage and current spatial branch rule.

