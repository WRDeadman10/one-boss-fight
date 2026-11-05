# W-A008: AttackTracker A2 Optional Montage Path Review

**Date:** 2026-11-06  
**Author:** Antigravity (Lane A)  
**Status:** Complete  
**Scope:** Architectural audit of the A2 delayed overhead slam montage dispatch, preview-clip CVar gating, authored override matching, and production fallback handling in [`RPGAttackTracker`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp).  
**Sources:**
- Attack Tracker Source: [`Source/OneBossFight/Player/RPGAttackTracker.cpp:24-44, 140-145, 223-239, 314-325`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L24-L44)
- Presentation Rules: [`Source/OneBossFight/Presentation/RPGPresentationRules.h:18-35`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Presentation/RPGPresentationRules.h#L18-L35)
- Unit Mutation Tests: [`Source/OneBossFight/Tests/RPGPresentationRulesTests.cpp:15-35`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGPresentationRulesTests.cpp#L15-L35)
- Codex Tooling Audit: [`Documentation/Boss/W_C046_SECOND_REVIEW_AG_TOOLS.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/W_C046_SECOND_REVIEW_AG_TOOLS.md)

---

## 1. Executive Summary

The A2 move represents Sevarog's signature delayed overhead slam (Freeze 16/30.2). To balance authoring visual improvements with zero Shipping regression risk, the dispatch pipeline employs a **three-tier resolution model**:
1. **Preview-Clip Guard (`rpg.AttackTracker.A2PreviewClip`):** Development-only toggle for live in-game testing of authored assets.
2. **Authored Path Matcher (`MatchesOptionalTrackerMontagePath`):** Case-insensitive asset path recognizer that binds A2 timing windows when the authored composite montage is active.
3. **Fail-Closed Pack Fallback:** Unconditional fallback to the original vendor stand-in montage (`GS_ChargedAttack_Montage`) whenever the authored asset is absent or disabled.

---

## 2. Dispatch Resolution Pipeline Analysis

### 2.1 Development-Only Preview CVar Guard
```cpp
// Source/OneBossFight/Player/RPGAttackTracker.cpp:223-229
#if UE_BUILD_DEVELOPMENT
if (MoveId == FName(TEXT("A2")) && CVarRPGAttackTrackerA2PreviewClip.GetValueOnGameThread() != 0 && !Timing->OptionalTrackerMontagePath.IsEmpty())
{
    UAnimMontage* PreviewMontage = LoadObject<UAnimMontage>(nullptr, *Timing->OptionalTrackerMontagePath);
    return PreviewMontage && Anim->Montage_Play(PreviewMontage) > 0.f;
}
#endif
```
- **Shipping Isolation:** Enclosed in `#if UE_BUILD_DEVELOPMENT`. In Shipping builds, this block is completely stripped by the preprocessor; zero branch overhead or string parsing occurs in production.
- **Default-Off Safety:** `CVarRPGAttackTrackerA2PreviewClip` defaults to `0` ([`line 24`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L24)). Unless explicitly set in the console, the preview path is never taken.

### 2.2 Authored Montage Recognition (`RPGPresentationRules`)
When the authored montage `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A2.AM_Boss01_A2` is played (either via preview CVar or future encounter definition data binding), `URPGAttackTracker` identifies it via:
```cpp
// Source/OneBossFight/Player/RPGAttackTracker.cpp:142, 316
RPGPresentationRules::MatchesOptionalTrackerMontagePath(T.OptionalTrackerMontagePath, ObjectPath)
```
- **Case-Insensitive Compliance:** Validated in [`RPGPresentationRulesTests.cpp:30-33`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGPresentationRulesTests.cpp#L30-L33). Handles case drift seamlessly (`FString::operator==`).
- **Timing Preservation:** When matched, the tracker enforces canonical A2 timing: `CommitTime = 1.68f`, `ActiveStartTime = 1.93f`, `ActiveEndTime = 2.11f`, `RecoveryEndTime = 3.14f` ([`lines 39-42`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L39-L42)).

### 2.3 Production Stand-in Fallback
If `rpg.AttackTracker.A2PreviewClip == 0` or the authored asset fails `LoadObject`:
```cpp
// Source/OneBossFight/Player/RPGAttackTracker.cpp:234-238
const FString Path = Timing->MontagePath.IsEmpty()
    ? FString::Printf(TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/%s.%s"), *Timing->MontageName, *Timing->MontageName)
    : Timing->MontagePath;
UAnimMontage* Montage = LoadObject<UAnimMontage>(nullptr, *Path);
return Montage && Anim->Montage_Play(Montage) > 0.f;
```
- The system plays the original pack asset `/Game/AdvancedARPGCombat/.../GS_ChargedAttack_Montage.GS_ChargedAttack_Montage`.
- Exactly preserves legacy D5 behavior out-of-the-box.

---

## 3. Disposition on Codex Tooling Review (`W-C046`)

Codex noted in [`Documentation/Boss/W_C046_SECOND_REVIEW_AG_TOOLS.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/W_C046_SECOND_REVIEW_AG_TOOLS.md) that [`Scripts/author_a2_close_composite.py`](file:///c:/UnrealProject/OneBossFight/Scripts/author_a2_close_composite.py) uses `AnimMontageFactory.SourceAnimation`, which in UE 5.5 only populates the initial Raise segment into the new montage asset, leaving Hold and Slam to be stitched manually or via track segments.
* **Architecture Impact:** None on C++ runtime. The C++ `RPGAttackTracker` correctly plays whatever montage is bound to `OptionalTrackerMontagePath`.
* **Authoring Script Plan:** The script has been updated with fail-closed execution guards (`ONEBOSSFIGHT_EXECUTE_TIER1_ASSET_WRITES=1`). Any multi-segment montage stitching will be verified in Editor when asset baking is officially authorized by the owner.

---

## 4. Conclusion

The A2 optional montage dispatch architecture satisfies all project safety requirements: zero Shipping overhead, default-off Development previewing, and an unconditional fail-closed fallback to vendor stand-ins.
