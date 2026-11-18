# BT-95: Greystone Smoke Source AnimBP Path Hotfix

Date: 2026-11-18 (Asia/Kolkata)
Author: Antigravity (Implementer)
Reviewer: Codex (Tech Lead)
Task ID: BT-95
Status: Complete (Ready for Review)

---

## 1. Background & Empirical Evidence

In BT-83 Run 3 ([BT_83_GREYSTONE_SMOKE_RUN_3.md](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/BT_83_GREYSTONE_SMOKE_RUN_3.md)), execution progressed past player controller acquisition and successfully proved exact `BP_GreystoneERPlayer_C` possession (`exact_pawn_possessed=true`). The run then failed closed on the subsequent source mesh inspection with:
```
CharacterMesh0 anim class exact path mismatch: /Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/ABP_CombatCharacter.ABP_CombatCharacter_C != /Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/ABP_CombatCharacter.ABP_CombatCharacter_C
```

Per Lead directive [X-2616], task `BT-95` was assigned to verify the canonical package path from existing project Content and authoring sources, and update only the smoke driver's expected path.

---

## 2. Canonical Asset Confirmation

Direct inspection of the project `Content/` hierarchy confirmed:
- `Content/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/ABP_CombatCharacter.uasset`: **EXISTS** (`True`)
- `Content/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/ABP_CombatCharacter.uasset`: **DOES NOT EXIST** (`False`)

The canonical Unreal package path for the source mannequin Animation Blueprint is:
```
/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/ABP_CombatCharacter.ABP_CombatCharacter_C
```

---

## 3. Hotfix Applied

Modified file: [Scripts/Editor/pie_greystone_visual_smoke.py](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_greystone_visual_smoke.py) (line 42)

### Diff
```diff
--- a/Scripts/Editor/pie_greystone_visual_smoke.py
+++ b/Scripts/Editor/pie_greystone_visual_smoke.py
@@ -39,7 +39,7 @@ ALLOWED_SOURCE_MESH_PATHS = (
     "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin_Simple.SKM_CombatMannequin_Simple",
     "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin.SKM_CombatMannequin",
 )
-EXPECTED_SOURCE_ANIM_CLASS_PATH = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/ABP_CombatCharacter.ABP_CombatCharacter_C"
+EXPECTED_SOURCE_ANIM_CLASS_PATH = "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/ABP_CombatCharacter.ABP_CombatCharacter_C"
 EXPECTED_VISIBLE_MESH_PATH = "/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone.Greystone"
 EXPECTED_VISIBLE_ANIM_CLASS_PATH = "/Game/OneBossFight/Player/Greystone/ABP_Greystone_RuntimeRetarget.ABP_Greystone_RuntimeRetarget_C"
```

---

## 4. Invariants Preserved

1. **Source-Only Scope**: Only `Scripts/Editor/pie_greystone_visual_smoke.py` line 42 was changed. Per directive [X-2616], zero edits were made to runner, validator, assets, or configuration.
2. **Zero Tests / Builds / Unreal Runs**: 0 builds, 0 Unreal Editor launches, 0 PIE runs, 0 asset/config mutations, 0 git commits/pushes.
3. **Fail-Closed Integrity**: The driver continues to enforce exact class path equality against `EXPECTED_SOURCE_ANIM_CLASS_PATH` without permissive substring or wildcard matching.

---

## 5. Verification

1. **Python Syntax Compilation**:
   ```bash
   python -m py_compile c:\UnrealProject\OneBossFight\Scripts\Editor\pie_greystone_visual_smoke.py
   # Result: Clean (exit 0)
   ```
2. **Doc Links Verification**:
   ```bash
   python c:\UnrealProject\OneBossFight\Scripts\Tools\check_doc_links.py
   # Result: broken_links=0
   ```

---

## 6. Updated Canonical 4-Way Source Hashes (SHA256)

With `pie_greystone_visual_smoke.py` updated, the refreshed four-way source hashes for any subsequent C-1155 approval envelope are:

- **runner** (`Scripts/Editor/run_greystone_visual_smoke.ps1`):
  `FAB7A89AC4710F9F955F8A3E9DDA18C97F0882BC973132E210213B070B14DB1F`
- **driver** (`Scripts/Editor/pie_greystone_visual_smoke.py`):
  `AD94D32121506E790C4215945320DF59A3EEFE10853E20204BF353B084EA89A0` *(Updated)*
- **retarget_cpp** (`Source/OneBossFightEditor/Private/RPGGreystoneRuntimeRetargetLibrary.cpp`):
  `22A04C1A5B12AAC1A045EC33AB2E346064D55FBABA83FA5E25FA2E749C5778AF`
- **moves_cpp** (`Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp`):
  `60097589BA1FAF3C12827ECDF6AC0FD32651EA3AA292EF25C17AB1878D7FB838`

---

## 7. Downstream Toolchain Note (Validator Synchronization)

As identified in the BT-94 audit report ([BT_94_GREYSTONE_SMOKE_RECEIPT_VALIDATOR_AUDIT.md](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/BT_94_GREYSTONE_SMOKE_RECEIPT_VALIDATOR_AUDIT.md)), `Scripts/Tools/validate_greystone_visual_smoke_receipt.py` line 38 defines the identical stale constant:
```python
EXPECTED_SOURCE_ANIM_CLASS = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/ABP_CombatCharacter.ABP_CombatCharacter_C"
```
Per directive [X-2616], the validator was not modified under BT-95. A synchronized update to `validate_greystone_visual_smoke_receipt.py` should be applied under a separate Lead authorization so that receipt validation matches the corrected driver.
