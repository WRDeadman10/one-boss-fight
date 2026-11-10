# BC-A03: Greystone Child Blueprint Material & Dependency Reconciliation

**Queue Lane:** `QUEUE_BC_AG` Task `BC-A03` (Antigravity)  
**Sources Inspected:**
- `Saved/BossCombatReview/bb_a15_greystone_materials_probe.json` (`[C-1282]` attempt 3, `materials3.log`)
- [`C1259_GREYSTONE_SOURCE_INVENTORY.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/C1259_GREYSTONE_SOURCE_INVENTORY.md)
- [`probe_greystone_materials_textures.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Editor/probe_greystone_materials_textures.py)

---

## 1. `BP_GreystoneERPlayer` vs `BP_GreystonePlayer` Probe Summary

- **Child Exists:** `true` (`/Game/OneBossFight/Player/Greystone/BP_GreystoneERPlayer`)
- **CDO Skeletal Mesh:** `/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone.Greystone` (identical to parent `/Game/OneBossFight/GreystonePack/BP_GreystonePlayer`; `override_materials = []`, `17` mesh slots -> `15` unique materials).
- **Hard Dependencies (`2`):** `/Game/OneBossFight/GreystonePack/BP_GreystonePlayer`, `/Script/OneBossFight`.
- **Soft Dependencies (`6`):** matches `C1259` Section 2 + 3.1 `1:1` (`Dodge_Small_Forward_Roll_Montage_Grey`, `Dodge_To_Idle_Montage_Grey`, plus the `4` authored `/Game/OneBossFight/Player/Greystone/AM_ER_*_Fit_Greystone` wrappers).
- **Texture Resolution Status:** `unique_textures = []` in attempt 3 because `MaterialEditingLibrary.get_used_textures` rejected `MaterialInstanceConstant`. Fixed in [`probe_greystone_materials_textures.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Editor/probe_greystone_materials_textures.py) (`_collect_used_textures` walks `parent` / `get_base_material()` to root `Material` + reads `texture_parameter_values` & `get_material_instance_texture_parameter_value`, offline-tested in `test_probe_greystone_materials_contract.py`); queued for Lead rerun in next free engine slot per `[C-1281]`/`[C-1282]`.

---

## 2. All `17` Mesh Slots (`15` Unique Materials) Reconciled Against `C1259` Section 6.2

`C1259_GREYSTONE_SOURCE_INVENTORY.md` Section 6.2 previously estimated `"15 material uassets under ParagonGreystone/.../Materials/"`. The live probe shows the exact count is indeed **`15` unique material assets**, split across **three subtrees under `/Game/ParagonGreystone/`**:

| Slot Index | Slot Name | Material Asset Path | Subtree Category vs `C1259` |
|---:|---|---|---|
| `0` | `M00_HeadTorso_skin00` | `/Game/ParagonGreystone/Characters/Heroes/Greystone/Materials/M_Greystone_Torso` | `Heroes/Greystone/Materials/` |
| `1` | `M01_ShoulderArms_skin01` | `/Game/ParagonGreystone/Characters/Heroes/Greystone/Materials/M_Greystone_arms` | `Heroes/Greystone/Materials/` |
| `2`, `7` | `M02_Legs_Cloth_skin02`, `M07_Cloth_skin07` | `/Game/ParagonGreystone/Characters/Heroes/Greystone/Materials/M_Greystone_legs` | `Heroes/Greystone/Materials/` *(shared `2x`)* |
| `3` | `M03_SwordShieldFur_skin03` | `/Game/ParagonGreystone/Characters/Heroes/Greystone/Materials/M_Greystone_shield` | `Heroes/Greystone/Materials/` |
| `4` | `M04_Flesh_Head_skin04` | `/Game/ParagonGreystone/Characters/Heroes/Greystone/Materials/M_Greystone_Flesh_head` | `Heroes/Greystone/Materials/` |
| `5` | `M05_Flesh_Arms_skin05` | `/Game/ParagonGreystone/Characters/Heroes/Greystone/Materials/M_Greystone_Flesh_Arms` | `Heroes/Greystone/Materials/` |
| `6`, `9` | `M06_HairFurBase_skin06`, `M09_Fur_skin09` | `/Game/ParagonGreystone/Characters/Heroes/Greystone/Materials/MIC_GreystoneFur` | `Heroes/Greystone/Materials/` *(shared `2x`)* |
| `8` | `M08_Hairsheets_skin08` | `/Game/ParagonGreystone/Characters/Heroes/Greystone/Materials/MIC_GreystoneHair` | `Heroes/Greystone/Materials/` |
| `10` | `M10_Lashes_skin10` | `/Game/ParagonGreystone/Characters/Global/Eyelash/M_EyelashMaster_Inst` | **Outside `Heroes/Greystone/`** -> `Characters/Global/Eyelash/` |
| `11` | `M11_InnerEye_skin11` | `/Game/ParagonGreystone/Characters/Heroes/Greystone/Skins/Dragonlord/Materials/M_Greystone_Dragonlord_EyeRefractive_Inst` | **Dragonlord Skin Subtree** -> `Skins/Dragonlord/Materials/` |
| `12` | `M12_Eyeshadow_skin12` | `/Game/ParagonGreystone/Characters/Global/Eyes/Materials/M_Eye_Occlusion` | **Outside `Heroes/Greystone/`** -> `Characters/Global/Eyes/Materials/` |
| `13` | `M13_Eyewet_skin13` | `/Game/ParagonGreystone/Characters/Heroes/Greystone/Materials/M_TearLine_Inst2` | `Heroes/Greystone/Materials/` |
| `14` | `M14_TeethAndTongue_skin14` | `/Game/ParagonGreystone/Characters/Global/Mouth/Materials/M_Mouth_MId_color` | **Outside `Heroes/Greystone/`** -> `Characters/Global/Mouth/Materials/` |
| `15` | `M15_Tearduct_skin15` | `/Game/ParagonGreystone/Characters/Heroes/Greystone/Materials/M_TearDuct_Darker` | `Heroes/Greystone/Materials/` |
| `16` | `M16_StonedMeshes_skin16` | `/Game/ParagonGreystone/Characters/Heroes/Greystone/Materials/M_Greystone_RockHair` | `Heroes/Greystone/Materials/` |

### Footprint & Packaging Disposition
- `11` materials sit in `Heroes/Greystone/Materials/`, `1` in `Skins/Dragonlord/Materials/`, and `3` in `Characters/Global/{Eyelash,Eyes,Mouth}/` (never prune those subtrees on any future minimal-pack pass).
- Expect `non_greystone_textures` on the upcoming fixed probe rerun to flag shared master/global textures referenced by slots `10`, `11`, `12`, and `14` (normal shared Paragon dependencies).
