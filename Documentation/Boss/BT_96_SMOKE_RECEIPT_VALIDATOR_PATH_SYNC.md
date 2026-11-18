# BT-96: Smoke Receipt Validator Path Synchronization

Date: 2026-11-18 (Asia/Kolkata)
Author: Antigravity (Implementer)
Reviewer: Codex (Tech Lead)
Task ID: BT-96
Status: Complete (Ready for Review)

---

## 1. Objective & Scope

Per Lead directive [X-2618], task `BT-96` synchronizes the offline receipt and log marker validator ([validate_greystone_visual_smoke_receipt.py](file:///c:/UnrealProject/OneBossFight/Scripts/Tools/validate_greystone_visual_smoke_receipt.py)) with the canonical source mannequin Animation Blueprint package path confirmed under `BT-95` and empirically recorded during `BT-83 Run 3` ([BT_83_GREYSTONE_SMOKE_RUN_3.md](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/BT_83_GREYSTONE_SMOKE_RUN_3.md)).

Scope is strictly source-only: no modifications to runner, driver, C++ sources, assets, or configuration; no tests or engine runs; no commits or pushes.

---

## 2. Exact Code Diff

Modified file: [Scripts/Tools/validate_greystone_visual_smoke_receipt.py](file:///c:/UnrealProject/OneBossFight/Scripts/Tools/validate_greystone_visual_smoke_receipt.py) (line 38)

```diff
--- a/Scripts/Tools/validate_greystone_visual_smoke_receipt.py
+++ b/Scripts/Tools/validate_greystone_visual_smoke_receipt.py
@@ -35,7 +35,7 @@ ALLOWED_SOURCE_MESH_PATHS = (
     "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin_Simple.SKM_CombatMannequin_Simple",
     "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin.SKM_CombatMannequin",
 )
-EXPECTED_SOURCE_ANIM_CLASS = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/ABP_CombatCharacter.ABP_CombatCharacter_C"
+EXPECTED_SOURCE_ANIM_CLASS = "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/ABP_CombatCharacter.ABP_CombatCharacter_C"
 EXPECTED_VISIBLE_MESH = "/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone.Greystone"
 EXPECTED_VISIBLE_ANIM_CLASS = "/Game/OneBossFight/Player/Greystone/ABP_Greystone_RuntimeRetarget.ABP_Greystone_RuntimeRetarget_C"
```

---

## 3. Invariants Preserved

1. **Exact Alignment with Driver**: The constant `EXPECTED_SOURCE_ANIM_CLASS` in `validate_greystone_visual_smoke_receipt.py` now matches byte-for-byte with `EXPECTED_SOURCE_ANIM_CLASS_PATH` in `pie_greystone_visual_smoke.py` line 42.
2. **Fail-Closed Verification Retained**: Both receipt observations (line 211) and log marker assertions (line 372) continue to enforce exact equality against `EXPECTED_SOURCE_ANIM_CLASS`.
3. **No Runner/Driver Modifications**: Neither `run_greystone_visual_smoke.ps1` nor `pie_greystone_visual_smoke.py` was touched.
4. **Zero Asset/Config Changes**: No `.uasset`, `.umap`, or `.ini` files were modified.

---

## 4. Verification

1. **Python Syntax Compilation**:
   ```bash
   python -m py_compile c:\UnrealProject\OneBossFight\Scripts\Tools\validate_greystone_visual_smoke_receipt.py
   # Result: Clean (exit 0)
   ```
2. **Doc Links Verification**:
   ```bash
   python c:\UnrealProject\OneBossFight\Scripts\Tools\check_doc_links.py
   # Result: broken_links=0
   ```

---

## 5. Hashes Baseline

### Validator Hash:
- `Scripts/Tools/validate_greystone_visual_smoke_receipt.py`:
  `4584523C0E7B8C179E6ECCDE26382576237117AEEC829A6F85040F616F2BB708`

### Canonical Four-Way Source Hashes (Unchanged from BT-95):
- **runner** (`Scripts/Editor/run_greystone_visual_smoke.ps1`):
  `FAB7A89AC4710F9F955F8A3E9DDA18C97F0882BC973132E210213B070B14DB1F`
- **driver** (`Scripts/Editor/pie_greystone_visual_smoke.py`):
  `AD94D32121506E790C4215945320DF59A3EEFE10853E20204BF353B084EA89A0`
- **retarget_cpp** (`Source/OneBossFightEditor/Private/RPGGreystoneRuntimeRetargetLibrary.cpp`):
  `22A04C1A5B12AAC1A045EC33AB2E346064D55FBABA83FA5E25FA2E749C5778AF`
- **moves_cpp** (`Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp`):
  `60097589BA1FAF3C12827ECDF6AC0FD32651EA3AA292EF25C17AB1878D7FB838`

---

## 6. Readiness for BT-83 Run 4

With both driver (`BT-95`) and validator (`BT-96`) synchronized to the canonical source AnimBP path, downstream receipt validation is fully unblocked for Lead Codex to execute Run 4 under H-17.
