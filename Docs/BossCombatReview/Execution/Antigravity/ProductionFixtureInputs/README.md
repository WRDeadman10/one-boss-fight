# Production Fixture Inputs (AG-CONTENT-01) - Corrected (X-260)

> **SCOPE:** `OFFLINE_INPUT_PACKET_NOT_RUNTIME_PROOF`  
> **TASK:** Prepared under Codex work order `[X-258]` (`AG-CONTENT-01`) and corrected under `[X-260]` for Claude's future positive production batch & animation-dependency test.  
> **SAFETY & INTEGRITY:** Zero engine, build, or automation processes executed. Zero pack edits. Zero Data Assets, levels, or encounter bindings created or activated.

---

## 1. Overview & Setup Context

Per `[X-258]` and `[X-260]`, this packet inventories the concrete production-fixture inputs needed for future positive production tests and animation-dependency fixtures.
The current fight setup uses the **Pack Mannequin / Ember Warden** configuration in `L_SevarogArena`:
- **Player:** `BP_CombatPlayerCharacter` (uses `SKM_CombatMannequin` on `SK_CombatMannequin`).
- **Boss:** `BP_ExampleGreatSwordBoss` (working name *The Ember Warden*), placed with `EnemyInfoRef = ExampleGreatSwordBoss`.
  - **Cosmetic Follower Body:** `SK_Boss01_Body` (restored 5 material slots per Report 08 / KI-064) driven via `SetLeaderPoseComponent`.
  - **Cosmetic Follower Pieces (3 Skeletal Meshes):** `SK_Boss01_Crown`, `SK_Boss01_Mantle`, `SK_Boss01_BrazierGauntlet` driven via `SetLeaderPoseComponent` (declared in `URPGBossLook::Pieces`, `RPGBossLook.h:37`).
  - **Cosmetic Weapon Attachment (1 Static Mesh):** `SM_Boss01_Greatsword` (`/Game/OneBossFight/Boss01/Weapons/SM_Boss01_Greatsword.SM_Boss01_Greatsword`, package `Content/OneBossFight/Boss01/Weapons/SM_Boss01_Greatsword.uasset`, sha256 `147629fb4c8df8b5d955f2c19622301bcd04d94b2ada27f7e07b7da79b0c8559`) attached to body socket `HeavySwordSocket_R` via `UStaticMeshComponent::AttachToComponent` (declared in `URPGBossLook::Sword`, `RPGBossLook.h:40`, constructor default `RPGBossLook.cpp:23`). **This is a static socket attachment, NOT a skeletal leader-pose follower.**
- **Exclusion:** Retired `GreystonePack` and `SevarogPack` assets are historical and **must not** be substituted.

---

## 2. Candidate Assignment Table for Production Tests

Every hash below is dynamically populated from exact disk preimages:

| Slot / ID | Role | Concrete Candidate Asset / Identity | Expected Type | Package File on Disk | SHA-256 (File Preimage) | Cook Configured |
|---|---|---|---|---|---|---|
| `PhaseRoarClip` | Boss | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_PhaseRoar.AN_Boss01_PhaseRoar` | `UAnimSequence` | `Content/OneBossFight/Boss01/Animations/AN_Boss01_PhaseRoar.uasset` | `0e19c86b2e68abd7b23b94f8b8d03ebb8059c762c11e9227a51d57c02b64479f` | N/A |
| `PhaseTransitionMontage` | Boss | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/Ability_R_Intro_Anim_Montage.Ability_R_Intro_Anim_Montage` | `UAnimMontage` | `Content/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/Ability_R_Intro_Anim_Montage.uasset` | `5e6a83e67d362b3dee896a78591e0e2056de96707e65189093fd87a8b2023356` | N/A |
| `PhaseImmunityEffect` | Boss | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C` | `UClass (derived from UGameplayEffect)` | `Content/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.uasset` | `f2fe720658b7503e1c7a75e43720e0117a3f8283338ae2ec15baa8198adf6fec` | N/A |
| `PhaseFireballAbility` | Boss | `/Game/AdvancedARPGCombat/MagicCombatSystem/Blueprints/AI/ExampleMagicEnemy/GA_Fireball_Enemy.GA_Fireball_Enemy_C` | `UClass (derived from UGameplayAbility)` | `Content/AdvancedARPGCombat/MagicCombatSystem/Blueprints/AI/ExampleMagicEnemy/GA_Fireball_Enemy.uasset` | `444e154c67fd10aa00102b85021d14124e34c1294a7450116cb2e9b3f9bcca0e` | N/A |
| `PhaseAttackAbilityPrefix` | Boss | `GA_GS_Boss_` (token) | `FString (naming prefix)` | N/A | N/A | N/A |
| `PhaseLeapAbilityTag` | Boss | `Ability.Melee.LeapAttack` (token) | `FName (FGameplayTag identity)` | N/A | N/A | N/A |
| `StaggerFallMontage` | Boss | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/KnockdownStart_Anim_Montage.KnockdownStart_Anim_Montage` | `UAnimMontage` | `Content/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/KnockdownStart_Anim_Montage.uasset` | `564973bab4afe57e0c7742cfc00a52303784e6b042ff3f62f0fde53f5c584fca` | N/A |
| `StaggerGetUpMontage` | Boss | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/Knockdown_Getup_Anim_Montage.Knockdown_Getup_Anim_Montage` | `UAnimMontage` | `Content/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/Knockdown_Getup_Anim_Montage.uasset` | `3156f085e06b80d518ad15db50aa61b63fbc83aa25502d84e800a031fa16b81b` | N/A |
| `StaggerFallClip` | Boss | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_StaggerFall.AN_Boss01_StaggerFall` | `UAnimSequence` | `Content/OneBossFight/Boss01/Animations/AN_Boss01_StaggerFall.uasset` | `46c550d8943ad84196cf42d7b51b33860c321d436c2da1eef87d15c4aee023e3` | N/A |
| `StaggerDownClip` | Boss | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_StaggerDown.AN_Boss01_StaggerDown` | `UAnimSequence` | `Content/OneBossFight/Boss01/Animations/AN_Boss01_StaggerDown.uasset` | `80702e46ccfe0556551169be8a14b805e7cdf88c60c60a72433998315187b7ae` | N/A |
| `StaggerRipostePlayerClip` | Player | `/Game/OneBossFight/Boss01/Animations/AN_Riposte_Player_Front.AN_Riposte_Player_Front` | `UAnimSequence` | `Content/OneBossFight/Boss01/Animations/AN_Riposte_Player_Front.uasset` | `c31727ff55c00bb53860de4c36fa147f16a34846fe64f99b486b9a8527df56fe` | N/A |
| `StaggerRiposteBossClip` | Boss | `/Game/OneBossFight/Boss01/Animations/AN_Riposte_Boss_Reaction.AN_Riposte_Boss_Reaction` | `UAnimSequence` | `Content/OneBossFight/Boss01/Animations/AN_Riposte_Boss_Reaction.uasset` | `767acccf1bd3414a3b46d9db7a37028cc72a8f9f5428f05289b7b89b2f0b8001` | N/A |
| `StaggerImmunityEffect` | Boss | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C` | `UClass (derived from UGameplayEffect)` | `Content/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.uasset` | `f2fe720658b7503e1c7a75e43720e0117a3f8283338ae2ec15baa8198adf6fec` | N/A |
| `StaggerHitStunAbilityClass` | Boss | `GA_GS_Boss_HitStun_C` (token)<br>`/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/GA_GS_Boss_HitStun.GA_GS_Boss_HitStun_C` (asset) | `UClass (derived from UGameplayAbility)` | `Content/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/GA_GS_Boss_HitStun.uasset` | `4ecf9d265995e2fcf9af8879477c8271abc08cedecb130fd403255125a897111` | N/A |
| `PlayerActorBlueprint` | Player | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.BP_CombatPlayerCharacter_C` | `UBlueprintGeneratedClass (derived from ACharacter)` | `Content/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.uasset` | `9662aaa364c56243180560b9121da7eadd8bfe43bfcd7f54bccd1752a07abc81` | N/A |
| `BossActorBlueprint` | Boss | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss.BP_ExampleGreatSwordBoss_C` | `UBlueprintGeneratedClass (derived from ACharacter)` | `Content/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss.uasset` | `a7dd5b156eb2bab555d16d12d9ef74ccecddd27990fd7c799873e24895f13217` | N/A |
| `SharedSkeleton` | Shared | `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin.SK_CombatMannequin` | `USkeleton` | `Content/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin.uasset` | `52677edcbfa4d78b49126481f7e3087c62231bdd76021055bba520c7c9de7e95` | Referenced |
| `PlayerMesh` | Player | `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin.SKM_CombatMannequin` | `USkeletalMesh` | `Content/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin.uasset` | `95fc213e7832602363eb213fb0de9b6826dead2ad4ec5ed01ab0651b3150112d` | Referenced |
| `BossMeshBody` | Boss | `/Game/OneBossFight/Boss01/Body/SK_Boss01_Body.SK_Boss01_Body` | `USkeletalMesh` | `Content/OneBossFight/Boss01/Body/SK_Boss01_Body.uasset` | `ee1f00924d99e8df84eb2325928ccd0a301dd58e7e220ae9ad4c5caf004969cd` | N/A |
| `BossFollowerCrown` | Boss | `/Game/OneBossFight/Boss01/Body/SK_Boss01_Crown.SK_Boss01_Crown` | `USkeletalMesh` | `Content/OneBossFight/Boss01/Body/SK_Boss01_Crown.uasset` | `46669e2f1c87471b5f0ed76c22f491f74179f722e0578af2c95093103592be5f` | N/A |
| `BossFollowerMantle` | Boss | `/Game/OneBossFight/Boss01/Body/SK_Boss01_Mantle.SK_Boss01_Mantle` | `USkeletalMesh` | `Content/OneBossFight/Boss01/Body/SK_Boss01_Mantle.uasset` | `d4b8b22527a9209556316a7264e2f6ff1a1cb7691ece1700877c5c0b9474f5de` | N/A |
| `BossFollowerBrazierGauntlet` | Boss | `/Game/OneBossFight/Boss01/Body/SK_Boss01_BrazierGauntlet.SK_Boss01_BrazierGauntlet` | `USkeletalMesh` | `Content/OneBossFight/Boss01/Body/SK_Boss01_BrazierGauntlet.uasset` | `405dcde80b40132aadee90b5135df7e4695b788fe406f13a6f13fa918d8d1d65` | N/A |
| `BossFollowerGreatsword` | Boss | `/Game/OneBossFight/Boss01/Weapons/SM_Boss01_Greatsword.SM_Boss01_Greatsword` | `UStaticMesh` | `Content/OneBossFight/Boss01/Weapons/SM_Boss01_Greatsword.uasset` | `147629fb4c8df8b5d955f2c19622301bcd04d94b2ada27f7e07b7da79b0c8559` | N/A |
| `ArenaLevel` | Shared | `/Game/OneBossFight/Levels/L_SevarogArena.L_SevarogArena` | `UWorld` | `Content/OneBossFight/Levels/L_SevarogArena.umap` | `095361fe5768accd59a0fe84a9f91ba3bfc8220dadea6d8c30f1ea3f1f3a77b5` | N/A |

---

## 3. Unresolved-Check List (Blockers / Requirements for Future Live Fixture)

1. **Actual Actor Mesh & Skeleton Compatibility:**
   - On-disk presence of `SK_CombatMannequin`, `SK_Boss01_Body`, and the three skeletal follower pieces (`SK_Boss01_Crown`, `SK_Boss01_Mantle`, `SK_Boss01_BrazierGauntlet`) does not prove runtime skeletal hierarchy alignment or bone mapping in the current binary.
   - The body and pieces are cosmetic followers attached via `SetLeaderPoseComponent`. The underlying combat driver remains the hidden pack mesh on `BP_ExampleGreatSwordBoss`.
   - *Check needed in live fixture:* Confirm `SetLeaderPoseComponent` succeeds without bone-mismatch warnings and weapon sockets (`HeavySwordSocket_R`) resolve correctly.

2. **Paired Player/Boss Clip Compatibility & Root Motion Alignment:**
   - Historical authoring records (`Documentation/Archive/AG/REPORT_12.md:22`, sha256 `cadbecfa...`) document `AN_Riposte_Player_Front` (1.6s, 90cm root motion along +Y) and `AN_Riposte_Boss_Reaction` (2.0s) having impact frames at 0.80s (frame 24). Root motion is enabled on the player clip via `Scripts/Editor/set_riposte_root_motion.py`.
   - *Limitation:* These historical numbers are authoring evidence. In the current binary, they remain **uncorroborated runtime claims** until verified in a live execution fixture.
   - *Check needed in live fixture:* Verify root motion extraction on player character advances exactly 90cm from initial 150cm slide gap to 60cm contact distance without desync.

3. **HitStun Class Name Token vs Candidate Asset Distinction:**
   - `FRPGStaggerProfileConfig::HitStunAbilityClassName` expects the short `FName` token `GA_GS_Boss_HitStun_C`, NOT the full soft class path. Feeding the full package path will fail runtime matching.
   - The full soft class path `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/GA_GS_Boss_HitStun.GA_GS_Boss_HitStun_C` is the concrete package candidate on disk (`Content/.../GA_GS_Boss_HitStun.uasset`, sha256 `4ecf9d26...`).
   - *Check needed in live fixture:* Confirm that placed `BP_ExampleGreatSwordBoss` possesses this ability in its ASC and activates it on poise break.

4. **Gameplay Effect Class Kind & CDO Verification:**
   - `GE_HitStunImmune.GE_HitStunImmune_C` is verified present on disk (sha256 `f2fe7206...`).
   - *Check needed in live fixture:* Verify that synchronous load produces a valid `UGameplayEffect` derived class and that ASC application grants immunity tags without leaking state on encounter reset.

5. **Load & Cook Availability vs Runtime Memory:**
   - Static cook configuration (`Config/DefaultGame.ini`, sha256 `9827ff8e...`) covers `/Game/OneBossFight/Boss01`, `/Game/AdvancedARPGCombat/MeleeCombatSystem/...`, etc.
   - *Limitation:* Static cook config proves configured coverage only, NOT packaged proof.
   - *Check needed in live fixture:* A positive production test must verify that `LoadSynchronous()` succeeds in an isolated environment without pre-loaded package artifacts.

---

## 4. Pinned Source, Config, and Evidence Dependencies

The table below documents the exact observed preimages of all sources, configs, reports, and scripts referenced by this packet. Note that `Source/OneBossFight/Player/RPGEncounterBinding.h` and `.cpp` are observed while **concurrently evolving under Claude's DD11 implementation (`X-259`)**, and no claim of frozen DD10 acceptance is made.

| Dependency File | Relative Path | SHA-256 | Size |
|---|---|---|---|
| `RPGEncounterBinding.h` | `Source/OneBossFight/Player/RPGEncounterBinding.h` | `ce0a7da73e833a22aef8ad69e3ed42984b39b04131997d78f055f4a4070d9c92` | 17193 B |
| `RPGEncounterBinding.cpp` | `Source/OneBossFight/Player/RPGEncounterBinding.cpp` | `c7255051e5f6be46db5b5caa0351cf45e50c3c07c4c0a8085fd3d71b633df828` | 17034 B |
| `RPGBossPhases.h` | `Source/OneBossFight/Player/RPGBossPhases.h` | `0887f37564a28564261b81ad21a1baf2a4c6f6adae99a3a49c3c15622225a69a` | 8607 B |
| `RPGBossPhases.cpp` | `Source/OneBossFight/Player/RPGBossPhases.cpp` | `c43615412e1f345d6ed75cc6d6a6b0d9ece6acaaac612e545b42cc24087f7a06` | 21965 B |
| `RPGBossStagger.h` | `Source/OneBossFight/Player/RPGBossStagger.h` | `7cfaaadbc33934d1dfe66560c0ff8c7fb47ac9e05399a5445b8c1e9a18c3695b` | 17803 B |
| `RPGBossStagger.cpp` | `Source/OneBossFight/Player/RPGBossStagger.cpp` | `c711d766b4fecb6999c638cf5d8720ca422ba758223f941ea437ebac5b474c98` | 36358 B |
| `RPGBossLook.h` | `Source/OneBossFight/Player/RPGBossLook.h` | `a9176a475a77c24f6c521e4ad251e9b050955ad05d0925483c6468831c7d6a97` | 4041 B |
| `RPGBossLook.cpp` | `Source/OneBossFight/Player/RPGBossLook.cpp` | `eb02ea8b1abe7ebc00039f3b5d265826064c6fe02d45e429ff02dc266ea6aa21` | 7561 B |
| `DefaultGame.ini` | `Config/DefaultGame.ini` | `9827ff8e632354cb7d3013955f1c1891ca16eac037abf8cd64369e5aa8886be3` | 3366 B |
| `REPORT_08.md` | `Documentation/Archive/AG/REPORT_08.md` | `71742a2ba6b3effdcce8cfb9bfe1acd70ae4d7023d5d59fe4def26240f3fdde9` | 16785 B |
| `REPORT_12.md` | `Documentation/Archive/AG/REPORT_12.md` | `cadbecfa63c27117944ad9f1a0b7a955845096506aa4005d1a33f57271c913a7` | 27859 B |
| `REPORT_13.md` | `Documentation/AG/REPORT_13.md` | `10d9b33895c227d141912cd9ef3807d4c1713a3a889c98058d346fc5f7a2464f` | 14977 B |
| `set_riposte_root_motion.py` | `Scripts/Editor/set_riposte_root_motion.py` | `0e6be54f61e178e173217519136964362027f0e5bd0e1fb7356164a1dcb7cd45` | 1044 B |
