# E-006 Edge-level graph evidence (partial) and pack adapter feasibility (CI-P0-C-01), 2026-10-25

> **Revision 2 (after Codex review D06B).** (1) Unresolved edge endpoints are 34 of 70 printed edges (13 of 19, 10 of 25, 11 of 26), not "about a quarter". (2) `bp_t3d_edges.py` resolves property blocks by the first node name across ALL graphs, keeps stale current-graph state and resolves targets only by pin id (ignoring the LinkedTo node reference), so reused K2Node names can merge graphs and the `Activate Abilities` entry node carries unrelated pins: the assembled chains in section 1 are PROVISIONAL and no exact activation success branch, abort path, ability order or filter may be inferred from the listings. (3) What is supported without the parser: the controller's raw EventGraph (`BPX_BP_BaseAIController.t3d` lines 2009 to 2054) links MasterAI -> GetEnemyInfo.ReturnValue -> BehaviorTree (self) and BehaviorTree -> RunBehaviorTree.BTAsset: the TREE-SELECTION route only; it does not prove generic C++ tasks, pre-play veto, abort semantics or all competing selection entry points. (4) Approval status: G-3 (owner, 2026-10-25) permits TESTING route (a) in a scratch experiment; the test is not done and proves nothing yet; "recommendation: bind route (a)" is a candidate only; an accepted-action adapter needs an entry-point closure inventory and a true pre-play proof. (5) Scratch scope: new scratch assets only plus a temporary PIE-instance `EnemyInfoRef` override with readbacks and cleanup; no saved map or level override under this approval (if one is indispensable the owner decides first).

Answers Codex D04 R1 and D02 "pack integration feasibility gate" as far as the evidence allows. All exports are read-only text exports (`probes/p0_export_text.py`, AssetExportTask) of the live editor assets (binary of E-001); parsers are offline (`probes/bp_t3d_edges.py`).

## 1. What was recovered

- 19 Blueprint exports `exports/BPX_*.t3d` (about 15 MB; hashes below): the graph objects with nodes and `LinkedTo` pin links.
- Edge listings from them (`exports/edges_*.txt`): `T_TryActivateAbilitiesByTags` function `Activate Abilities` (47 lines), `GA_EnemyMeleeAttack` and `GA_MeleeBase` function `Can Activate Ability?`.
- Limitations of the parser (stated, not hidden): the export writes some node bodies twice and the pin ids of the second copy differ, so about a quarter of the edges end in `?.<pin id>` (target node not resolved); the 6 MB `BP_AdvancedAbilitySystemComponent` export yielded no graph with this parser (nesting differs), so `Get Abilities by All Tags` and `Try Activate Ability` stay at the node-inventory level of E-002 Addendum 3 (`exports/graph_ASC_GetAbilitiesByAllTags_and_TryActivate.txt`) with their return branches and the `CreatedAbilities` filter UNRESOLVED at edge level. D04 R1 is therefore PARTLY met.
- Edge-level facts that ARE established (`edges_T_TryActivate_ActivateAbilities.txt`): `FunctionEntry.then -> VariableSet L_Abilities` (value from `GetAbilitiesByAllTags` on the ability system component with the task's `Ability Tags`) `-> ForEach (MacroInstance_3).LoopBody -> VariableSet LastSuccessfulAbility (array element) -> IsValid (MacroInstance_0) -> CallFunction_19 (the ability system component's try-activate, self = the component, `bForceActivation` from the task variable)`; `ForEach.Completed -> VariableSet LastSuccessfulAbility -> FunctionResult_1`. The branch on the activation result and `FunctionResult_0` are in the unresolved quarter.

## 2. Pack adapter feasibility (D02 options (a) project BT/task, (b) pack hook)

Evidence (live exports):
- `BP_EnemyInfo` instances carry (export `ExampleGreatSwordBoss_info.t3d`): AI pawn class, anim class, `DefaultCombatStyle`, **`BehaviorTree`**, behavior state classes, default behavior state, blackboard key names, default attributes, enemy name, state classes, extended attributes (health, poise).
- `BP_BaseAIController` (export `BPX_BP_BaseAIController.t3d`) calls `GetEnemyInfo` six times and contains one `RunBehaviorTree` node and a `BehaviorTree` member: the tree that runs is taken from the enemy info of the pawn.
- `BP_MasterEnemy` reads `EnemyInfoRef` (35 references); the boss BP's own default `EnemyInfoRef` is `ExampleSwordEnemy` (the sword mob), the placed arena instance overrides it to `ExampleGreatSwordBoss` (CDO export line 54; `CLAUDE.md`/PROJECT_STATE say the same). The info asset still names its boss "Greystone Knight" (`EnemyName`), a leftover of the pack data.
Reading: a PROJECT-owned `BP_EnemyInfo` data asset (new asset in `/Game/OneBossFight/...`, not an edit of any pack asset) can name a PROJECT-owned `BehaviorTree` and combat style, and the placed boss instance can point `EnemyInfoRef` at it: route (a) is feasible by this evidence for selecting a project tree. What this does NOT yet show: that a project BT may use new C++ `UBTTaskNode` classes that request the shared runtime and then call the pack abilities (very likely, standard UE, but untested here), that the pack's `T_TryActivateAbilitiesByTags` can be wrapped, or whether a pre-activation veto hook (route (b)) exists: no hook was found in `GA_Attack`/`GA_MeleeBase` exports by name search (`CanActivateAbility` is the only gate, per-ability, E-002 Addendum 3). A creation test (new info asset + minimal project BT, PIE, readback) is a proposed P0-extension probe, needs an asset write, so it is NOT done and needs approval.
Recommendation for the gate: bind route (a) as the default candidate, keep (b) as not found, prove (a) with the creation test before DD-1 step 4.

## 3. Hashes (sha256, bytes)

```
8355f533bc506327eba4260ead0c14042ff7481099c7163f77156c76ff006429  exports\BPX_BP_AdvancedAbilitySystemComponent.t3d  (5987034 bytes)
fa7957ab7408a951dd599f444f21ef463cf8fa901aae734206ecd89a4fb64c75  exports\BPX_BP_BaseAIController.t3d  (874997 bytes)
dacb7e5f329cffa6df840f36d165b12696a5f19f01d799575cec8a5e1ff1b905  exports\BPX_BP_BehaviorManagerComponent.t3d  (581905 bytes)
0ed9b811c24bc9871121963b99bdecea1239114c439b88daf452e61b2ec66151  exports\BPX_BP_EnemyImpactDecision.t3d  (66020 bytes)
0369729f0959825d55bab4d8080f66a3564d67bc776ac607a09ce2d5a503c699  exports\BPX_BP_ExampleGreatSwordBoss.t3d  (225283 bytes)
c1c58f20a08a54982d194916837d8d6b70139d2aca32d5f952b12567843f6aed  exports\BPX_BP_MasterEnemy.t3d  (1073277 bytes)
75ca40832253dc382e3adca8bad76bd348452e62eae8ede54ede795aa7f3b595  exports\BPX_D_ChanceCondition.t3d  (19723 bytes)
df34616cec7350637792f8b1613546f36b0216728e8a784d119f873239fe387e  exports\BPX_D_IsCurrentBehaviorEqual.t3d  (40873 bytes)
ec620d20915ba9ef438f2a6692a49a66b56409270ccd01489f7d7842d47ddce1  exports\BPX_GA_Attack.t3d  (733267 bytes)
fe6b5d284fedb0f941bdd724713f9b9c9c9304a4ec5a83ea6fe6f86a6ac03f95  exports\BPX_GA_EnemyMeleeAttack.t3d  (300190 bytes)
372359bf20c07cd77abe59566ffe84d8fdc62ede14baadc23b635f237f3a986f  exports\BPX_GA_EnemySprintAttack.t3d  (332023 bytes)
504b2d142182c1e1b18ff5b5967d954144a1f950839ac33f32f2014ced021f21  exports\BPX_GA_GS_Boss_CloseRare.t3d  (2177 bytes)
08133fc71aa50e3a000a13234fa3e3485c21bf8403f7335ae0219a901b01d4fd  exports\BPX_GA_GS_Boss_MidRangeAttack.t3d  (2247 bytes)
51a99ae40602bbb41a5309a6e6f59a76ed712726a0fdda5c23500300d3a1015c  exports\BPX_GA_GS_Boss_SprintAttack.t3d  (2221 bytes)
174062a346365e57db7e6ef0f239e633eda24f147e03ba6cb56dbd1dc6664bb8  exports\BPX_GA_MeleeBase.t3d  (345100 bytes)
29918b21497886254d75465629b329fd23d1d49d9c96f41ad48350cb6e98bf2c  exports\BPX_SM_Humanoid_CombatBehavior.t3d  (3505764 bytes)
2e18fbc863e66fde977be1e5c1be9a59d6570a3a972dd51f59ad772bbe72b0bd  exports\BPX_S_UpdateBehavior.t3d  (164438 bytes)
888bfab2451d489308ff429b7ae21d0b150cec1c0b8937d765504773c4dd3661  exports\BPX_StateManagerComponent.t3d  (840425 bytes)
ca332e88dd9ac21022d84bcfe26fe72631e92fd1c4a61aa0ab39b85bfe74deae  exports\BPX_T_TryActivateAbilitiesByTags.t3d  (181818 bytes)
963826ba29e845c949a8c2523ec8b26000ac2e0cab8311dee82753a7aecbffd0  exports\edges_GA_EnemyMeleeAttack_CanActivate.txt  (2264 bytes)
23ace9a6c79da3ecafce7096fd752fa0902c8da0bd4b5dc1c93fb34e896ecb70  exports\edges_GA_MeleeBase_CanActivate.txt  (2777 bytes)
a16908682d1d45b4d0c60e1b3b6b82cd8a433bc0d482c58a9072fc93799a389e  exports\edges_T_TryActivate_ActivateAbilities.txt  (2869 bytes)
b6de612194c0c26272f3671220828dc1935362f1b121cd971e851acfc85656c5  probes/bp_t3d_edges.py  (4087 bytes)
a48651c178bf938b68090e79c9042d5734db1136873f341920f8cee5cc3b4c19  probes/p0_export_text.py  (1507 bytes)
```
