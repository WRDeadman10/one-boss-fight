# Production Fixture Inputs (AG-CONTENT-01)

> **SCOPE:** `OFFLINE_INPUT_PACKET_NOT_RUNTIME_PROOF`  
> **TASK:** Prepared under Codex work order `[X-258]` (`AG-CONTENT-01`) for Claude's future positive production batch & animation-dependency test.  
> **SAFETY & INTEGRITY:** Zero engine, build, or automation processes executed. Zero pack edits. Zero Data Assets, levels, or encounter bindings created or activated.

---

## 1. Overview & Setup Context

Per `[X-258]`, this packet inventories the concrete production-fixture inputs needed for future positive production tests and animation-dependency fixtures.
The current fight setup uses the **Pack Mannequin / Ember Warden** configuration in `L_SevarogArena`:
- **Player:** `BP_CombatPlayerCharacter` (uses `SKM_CombatMannequin` on `SK_CombatMannequin`).
- **Boss:** `BP_ExampleGreatSwordBoss` (working name *The Ember Warden*), placed with `EnemyInfoRef = ExampleGreatSwordBoss`, cosmetic follower body `SK_Boss01_Body` (restored 5 material slots per Report 08 / KI-064) on `SK_CombatMannequin`.
- **Exclusion:** Retired `GreystonePack` and `SevarogPack` assets are historical and **must not** be substituted.

---

## 2. Candidate Assignment Table for Production Tests

| Slot / ID | Role | Concrete Candidate Asset / Identity | Expected Type | Package File on Disk | SHA-256 (File Preimage) | Cook Configured |
|---|---|---|---|---|---|---|
| `PhaseRoarClip` | Boss | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_PhaseRoar` | `UAnimSequence` | `Content/OneBossFight/Boss01/Animations/AN_Boss01_PhaseRoar.uasset` | `0e19c86b2e68abd7b23b94f8b8d03ebb8059c762c11e9227a51d57c02b64479f` | Yes (`/Game/OneBossFight/Boss01`) |
| `PhaseTransitionMontage` | Boss | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/Ability_R_Intro_Anim_Montage` | `UAnimMontage` | `Content/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/Ability_R_Intro_Anim_Montage.uasset` | `5e6a83e67d362b3dee896a78591e0e2056de96707e65189093fd87a8b2023356` | Yes (`/Game/.../Animations`) |
| `PhaseImmunityEffect` | Boss | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C` | `UClass` (`UGameplayEffect`) | `Content/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.uasset` | `f2fe720658b7503e1c7a75e43720e0117a3f8283338ae2ec15baa8198adf6fec` | Yes (`/Game/.../Blueprints`) |
| `PhaseFireballAbility` | Boss | `/Game/AdvancedARPGCombat/MagicCombatSystem/Blueprints/AI/ExampleMagicEnemy/GA_Fireball_Enemy.GA_Fireball_Enemy_C` | `UClass` (`UGameplayAbility`) | `Content/AdvancedARPGCombat/MagicCombatSystem/Blueprints/AI/ExampleMagicEnemy/GA_Fireball_Enemy.uasset` | `444e154c67fd10aa00102b85021d14124e34c1294a7450116cb2e9b3f9bcca0e` | Yes (`/Game/.../ExampleMagicEnemy`) |
| `PhaseAttackAbilityPrefix` | Boss | `GA_GS_Boss_` | String Token | N/A | N/A | N/A |
| `PhaseLeapAbilityTag` | Boss | `Ability.Melee.LeapAttack` | `FName` Tag Token | N/A | N/A | N/A |
| `StaggerFallMontage` | Boss | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/KnockdownStart_Anim_Montage` | `UAnimMontage` | `Content/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/KnockdownStart_Anim_Montage.uasset` | `564973bab4afe57e0c7742cfc00a52303784e6b042ff3f62f0fde53f5c584fca` | Yes (`/Game/.../Animations`) |
| `StaggerGetUpMontage` | Boss | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/Knockdown_Getup_Anim_Montage` | `UAnimMontage` | `Content/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/Knockdown_Getup_Anim_Montage.uasset` | `3156f085e06b80d518ad15db50aa61b63fbc83aa25502d84e800a031fa16b81b` | Yes (`/Game/.../Animations`) |
| `StaggerFallClip` | Boss | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_StaggerFall` | `UAnimSequence` | `Content/OneBossFight/Boss01/Animations/AN_Boss01_StaggerFall.uasset` | `46c550d8943ad84196cf42d7b51b33860c321d436c2da1eef87d15c4aee023e3` | Yes (`/Game/OneBossFight/Boss01`) |
| `StaggerDownClip` | Boss | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_StaggerDown` | `UAnimSequence` | `Content/OneBossFight/Boss01/Animations/AN_Boss01_StaggerDown.uasset` | `80702e46ccfe0556551169be8a14b805e7cdf88c60c60a72433998315187b7ae` | Yes (`/Game/OneBossFight/Boss01`) |
| `StaggerRipostePlayerClip` | Player | `/Game/OneBossFight/Boss01/Animations/AN_Riposte_Player_Front` | `UAnimSequence` | `Content/OneBossFight/Boss01/Animations/AN_Riposte_Player_Front.uasset` | `c31727ff55c00bb53860de4c36fa147f16a34846fe64f99b486b9a8527df56fe` | Yes (`/Game/OneBossFight/Boss01`) |
| `StaggerRiposteBossClip` | Boss | `/Game/OneBossFight/Boss01/Animations/AN_Riposte_Boss_Reaction` | `UAnimSequence` | `Content/OneBossFight/Boss01/Animations/AN_Riposte_Boss_Reaction.uasset` | `767acccf1bd3414a3b46d9db7a37028cc72a8f9f5428f05289b7b89b2f0b8001` | Yes (`/Game/OneBossFight/Boss01`) |
| `StaggerImmunityEffect` | Boss | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C` | `UClass` (`UGameplayEffect`) | `Content/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.uasset` | `f2fe720658b7503e1c7a75e43720e0117a3f8283338ae2ec15baa8198adf6fec` | Yes (`/Game/.../Blueprints`) |
| `StaggerHitStunAbilityClass` | Boss | `GA_GS_Boss_HitStun_C` | `UClass` (`UGameplayAbility`) | `Content/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/GA_GS_Boss_HitStun.uasset` | `4ecf9d26451a55f9cfd54e4ae8b72e51928ebdb8e1db4b86e088ba96637b359f` | Yes (`/Game/.../Blueprints`) |
| `PlayerActorBlueprint` | Player | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter` | `UBlueprintGeneratedClass` | `Content/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.uasset` | `9662aaa3bb12c3f870a3165b6f047ff3a3df5cb89fbe9f7e5200388d754f91e3` | Yes (`/Game/.../Blueprints`) |
| `BossActorBlueprint` | Boss | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss` | `UBlueprintGeneratedClass` | `Content/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss.uasset` | `a7dd5b15beaa04791eeb00d0246a4eecf73449339e1a90c52bb1eeb96be34516` | Yes (`/Game/.../Blueprints`) |
| `SharedSkeleton` | Shared | `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin` | `USkeleton` | `Content/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin.uasset` | `52677edc466487ffaa79eec699df8d06bca1387693998b58a1491cf15a9a4b37` | Referenced |
| `PlayerMesh` | Player | `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin` | `USkeletalMesh` | `Content/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin.uasset` | `95fc213e4b7bdfd9aa17865f32eb4a9b5f541334860eb3a778fcbe23831835bc` | Referenced |
| `BossMeshBody` | Boss | `/Game/OneBossFight/Boss01/Body/SK_Boss01_Body` | `USkeletalMesh` | `Content/OneBossFight/Boss01/Body/SK_Boss01_Body.uasset` | `ee1f0092d6e3ae43906660fc07f7b3b42cb06d5ebbfdfc5eb29d6718cf30a3b8` | Yes (`/Game/OneBossFight/Boss01`) |
| `BossFollowerCrown` | Boss | `/Game/OneBossFight/Boss01/Body/SK_Boss01_Crown` | `USkeletalMesh` | `Content/OneBossFight/Boss01/Body/SK_Boss01_Crown.uasset` | `46669e2f476ca092c4bdf19293a55fb12c6a848c4cfbfbc359c3e98625ae7ef5` | Yes (`/Game/OneBossFight/Boss01`) |
| `BossFollowerMantle` | Boss | `/Game/OneBossFight/Boss01/Body/SK_Boss01_Mantle` | `USkeletalMesh` | `Content/OneBossFight/Boss01/Body/SK_Boss01_Mantle.uasset` | `d4b8b2257bf4b43c6b2ffad445d44ce9ce207a9b0c78a1bc25255476a6ce46fa` | Yes (`/Game/OneBossFight/Boss01`) |
| `BossFollowerBrazierGauntlet` | Boss | `/Game/OneBossFight/Boss01/Body/SK_Boss01_BrazierGauntlet` | `USkeletalMesh` | `Content/OneBossFight/Boss01/Body/SK_Boss01_BrazierGauntlet.uasset` | `405dcde8c6e2ca06ce91475c803caeb23439b8bc7370cae41a1cc1f13bcf3d42` | Yes (`/Game/OneBossFight/Boss01`) |
| `BossFollowerGreatsword` | Boss | `/Game/OneBossFight/Boss01/Body/SM_Boss01_Greatsword` | `UStaticMesh` | `Content/OneBossFight/Boss01/Body/SM_Boss01_Greatsword.uasset` | `37803719468e82aa8b0bb30fefca7a0e38a2dd0c6cf7b02db7bba539fe51dfd2` | Yes (`/Game/OneBossFight/Boss01`) |
| `ArenaLevel` | Shared | `/Game/OneBossFight/Levels/L_SevarogArena` | `UWorld` | `Content/OneBossFight/Levels/L_SevarogArena.umap` | `47f6cf67f4019a288bb409d6c291244e8bc1a42b10dc64f1c9cce0e88383a152` | Yes (`/Game/OneBossFight/Levels`) |

---

## 3. Unresolved-Check List (Blockers / Requirements for Future Live Fixture)

1. **Actual Actor Mesh & Skeleton Compatibility:**
   - On-disk presence of `SK_CombatMannequin` and `SK_Boss01_Body` does not prove runtime skeletal hierarchy alignment or bone mapping in the current binary.
   - `SK_Boss01_Body` is driven as a cosmetic follower via `URPGBossLook::SetLeaderPoseComponent`. The underlying combat driver remains the hidden pack mesh on `BP_ExampleGreatSwordBoss`.
   - *Check needed in live fixture:* Confirm `SetLeaderPoseComponent` succeeds without bone-mismatch warnings and weapon sockets (`HeavySwordSocket_R`) resolve correctly.

2. **Paired Player/Boss Clip Compatibility & Root Motion Alignment:**
   - `AN_Riposte_Player_Front` (1.6s, 90cm root motion) and `AN_Riposte_Boss_Reaction` (2.0s) have matching impact frames at 0.8s.
   - *Check needed in live fixture:* Verify root motion extraction on player character advances exactly 90cm from initial 150cm slide gap to 60cm contact distance, and that anim notify `RPGBossClips` handles playback without clipping or desync.

3. **Gameplay Effect Class Kind & CDO Verification:**
   - `GE_HitStunImmune.GE_HitStunImmune_C` is verified as present on disk.
   - *Check needed in live fixture:* Verify that synchronous load produces a valid `UGameplayEffect` derived class and that ASC application grants immunity tags without crashing or leaking state on encounter reset.

4. **Load & Cook Availability vs Runtime Memory:**
   - Static cook configuration (`DefaultGame.ini` `+DirectoriesToAlwaysCook`) covers `/Game/OneBossFight/Boss01`, `/Game/AdvancedARPGCombat/MeleeCombatSystem/...`, etc.
   - *Limitation:* Static cook config proves configured coverage only, NOT packaged proof.
   - *Check needed in live fixture:* A positive production test must verify that `LoadSynchronous()` succeeds in an isolated environment without pre-loaded package artifacts.

5. **Timings & Attack Prefix Resolution:**
   - `AttackAbilityPrefix = "GA_GS_Boss_"` and `LeapAbilityTag = "Ability.Melee.LeapAttack"` are string/name tokens.
   - *Check needed in live fixture:* Verify that placed/spawned `BP_ExampleGreatSwordBoss` actually possesses abilities matching `GA_GS_Boss_*` and that `Ability.Melee.LeapAttack` exists in the `UGameplayTagsManager` registry.

---

## 4. Source Declaration Preimages

Any change to these source files invalidates this witness packet:

| Source File | Project Relative Path | SHA-256 |
|---|---|---|
| `RPGEncounterBinding.h` | `Source/OneBossFight/Player/RPGEncounterBinding.h` | `48d875f75e7a9e334a17950c024d2ea5230058b8d4f09a9ea11dfae10a625ca5` |
| `RPGBossPhases.h` | `Source/OneBossFight/Player/RPGBossPhases.h` | `d720b0051e5f8f8b3df9bb3bfce5db80590c102a2815124b898be28d82d4775d` |
| `RPGBossPhases.cpp` | `Source/OneBossFight/Player/RPGBossPhases.cpp` | `8929d81d248bfb36f75f71e62ff187513361eef35c3c0ca6bb9a4441c888d3e8` |
| `RPGBossStagger.h` | `Source/OneBossFight/Player/RPGBossStagger.h` | `2643a6d7131fe186e8a0026e95c1a7a03fb4d2eeff0a08e64c760dcfe7f0709b` |
| `RPGBossStagger.cpp` | `Source/OneBossFight/Player/RPGBossStagger.cpp` | `d2c3df426c11702f2dc574b5b7b99c855a805f4bf88414fa9cf5cfb4b8a25c15` |
