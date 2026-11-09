# SFX-04: Audio Integration & Wiring Plan (Plan-Only)

**Document Version:** 1.0  
**Authority:** Project Owner Order & Claude Directives `[C-1169]`, `[C-1181]`, `[C-1193]`  
**Owner:** Antigravity (`Art/Review/Audit`)  
**Status:** PROPOSED (Plan-only; NO apply or asset edits until Owner confirms sound choice)  

---

## 1. Architectural Principles

1. **Strict Opt-In Defaults (`nullptr` / Silent by Default):**
   - Every audio attachment is defined as an optional `TSoftObjectPtr<USoundBase>` or `USoundBase*` property on its owning C++ component or encounter data structure.
   - If unset, the component emits zero sound and preserves existing silent behavior with 0 overhead.
2. **Never Touch Pack Assets:**
   - No AnimNotify or property modifications shall ever be written to assets under `/Game/AdvancedARPGCombat/`.
   - All montages or components wired are either OneBossFight-native assets (`/Game/OneBossFight/`) or driven through project C++ classes (`URPGPlayerParry`, `URPGTier2BossPresentation`, `URPGBossStagger`).
3. **Deterministic Staged Rollout:**
   - Integration occurs under exclusive `ENGINE_LOCK.json`.
   - Each wired event must be preceded and followed by offline contract validation and diagnostic log markers (`[SFX_Trigger] event=<id> sound=<asset>`).

---

## 2. Event-to-Code Wiring Specifications

### GAP-01: Player Parry Success
- **Gameplay Event:** Greystone executes a successful parry against an incoming boss attack during the active parry window.
- **Owning Class:** `URPGPlayerParry` (`Source/OneBossFight/Player/RPGPlayerParry.h`)
- **Hook Point:** Inside `URPGPlayerParry::HandleSuccessfulParry(AActor* Attacker)` alongside hit-stop, camera impulse, and `NotifyParried`.
- **Property Schema:**
  ```cpp
  UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "RPG|Audio")
  TSoftObjectPtr<USoundBase> ParrySuccessSound = nullptr;
  ```
- **Execution Call:**
  ```cpp
  if (USoundBase* Sfx = ParrySuccessSound.LoadSynchronous())
  {
      UGameplayStatics::PlaySoundAtLocation(this, Sfx, GetOwner()->GetActorLocation(), 1.0f, 1.0f);
  }
  ```
- **Auditioned Candidates:**
  - `GAP01_Addendum_Opt2_SwordImpact1` (`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/SwordImpacts/SwordImpact1`) [0.35s, Sharp ping]
  - `GAP01_Addendum_Opt3_SwordImpact3` (`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/SwordImpacts/SwordImpact3`) [0.40s, Resonant clang]
  - `Sword_Sharpening_Fast_Speed_Cue` (`/Game/RealisticSwordSoundEffects/Sword_Sharpening_Fast_Speed_Cue`) [0.35s]

---

### GAP-02: Boss Parry Recoil
- **Gameplay Event:** Sevarog stumbles backwards upon having an attack deflected, playing `AM_Boss01_ParryRecoil` (duration 0.600s).
- **Owning Class / Asset:** `AM_Boss01_ParryRecoil` (`/Game/OneBossFight/Boss01/Animations/AM_Boss01_ParryRecoil`) OR `URPGBossStagger`
- **Hook Point:**
  - *Option 1 (AnimNotify):* `AnimNotify_PlaySound` placed at $t = 0.040\text{ s}$ on track `Audio` of `AM_Boss01_ParryRecoil`.
  - *Option 2 (Code):* `URPGBossStagger::PlayParryRecoil` via soft sound pointer.
- **Property Schema:**
  ```cpp
  UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "RPG|Audio")
  TSoftObjectPtr<USoundBase> ParryRecoilVocalSound = nullptr;
  ```
- **Auditioned Candidates:**
  - `Sevarog_Effort_Block` (`/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_Block`) [0.55s, deep vocal + whoosh]
  - `Sevarog_Effort_PainHeavy` (`/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_PainHeavy`) [0.60s, guttural gasp]

---

### GAP-03: Phase 2 Aura Ignite
- **Gameplay Event:** Boss health drops below threshold, triggering the Phase 2 transition sequence and spawning `NS_Boss_PhaseTwoAura`.
- **Owning Class:** `URPGTier2BossPresentation` (`Source/OneBossFight/Boss/RPGTier2BossPresentation.h`)
- **Hook Point:** Inside `URPGTier2BossPresentation::ActivatePhaseTwoPresentation()` at the exact moment the Niagara component is activated.
- **Property Schema:**
  ```cpp
  UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "RPG|Audio")
  TSoftObjectPtr<USoundBase> AuraIgniteSound = nullptr;
  ```
- **Auditioned Candidates:**
  - `SFX_Vefects_Shockwave_04_1s_Cue` (`/Game/Vefects/Easy_Shockwaves_VFX/Audio/SFX_Vefects_Shockwave_04_1s_Cue`) [1.00s, sub-bass + fire eruption]
  - `Explosion_Cue` (`/Game/StarterContent/Audio/Explosion_Cue`) [1.20s, concussive boom]

---

### GAP-04: Player Backstep Whoosh
- **Gameplay Event:** Greystone performs a defensive backstep with invulnerability frames.
- **Owning Class / Asset:** `Greystone_Dodge_B_Montage` (`/Game/ParagonGreystone/Characters/Heroes/Greystone/Animations/Greystone_Dodge_B_Montage`)
- **Hook Point:** `AnimNotify_PlaySound` on notify track at frame 0 / $t = 0.020\text{ s}$ of backstep hop.
- **Auditioned Candidates:**
  - `Swoosh_1_Cue` (`/Game/RealisticSwordSoundEffects/Swoosh_1_Cue`) [0.22s, swift evasion whoosh]
  - `Swoosh_3_Cue` (`/Game/RealisticSwordSoundEffects/Swoosh_3_Cue`) [0.18s, high air cut]

---

### GAP-05: Boss Stance Break / Posture Collapse
- **Gameplay Event:** Boss posture pool reaches 0; boss enters 3.0s vulnerable stagger state awaiting riposte.
- **Owning Class:** `URPGBossStagger` (`Source/OneBossFight/Player/RPGBossStagger.h`)
- **Hook Point:** Inside `URPGBossStagger::StartStagger()` before playing `AM_Boss01_Stagger`.
- **Property Schema:**
  ```cpp
  UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "RPG|Audio")
  TSoftObjectPtr<USoundBase> StanceBreakSound = nullptr;
  ```
- **Auditioned Candidates:**
  - `Collapse_Cue` (`/Game/StarterContent/Audio/Collapse_Cue`) [1.10s, heavy stone/armor collapse]
  - `A_Guardian_ImpactL_Cue` (`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue`) [0.85s, resounding bell chime]

---

## 3. Safety & Verification Gate

1. **No-Code / No-Asset State:**
   - This document is strictly design & schema preparation.
   - No `.uasset` or `.cpp` changes will be made until Owner selects preferred candidates from the audition pack (`SFX_Audition_Reel.mp4` & `Parry_Addendum_Reel.mp4`).
2. **Offline Contract:**
   - Validated by `Scripts/Editor/test_sfx_wiring_plan_contract.py` asserting all cited assets exist in project Content.
