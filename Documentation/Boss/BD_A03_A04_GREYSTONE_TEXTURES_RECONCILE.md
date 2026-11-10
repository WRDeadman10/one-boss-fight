# BD-A03..A04: Greystone Refreshed Texture Probe Reconciliation

**Queue Lane:** `QUEUE_BD_AG` Tasks `BD-A03`..`BD-A04` (Unblocked by `[C-1284]` `materials4.log`)  
**Sources Inspected:**
- `Saved/BossCombatReview/bb_a15_greystone_materials_probe.json` (`[C-1284]` rerun with `5280f67d` fix)
- [`BC_A03_GREYSTONE_MATERIALS_RECONCILE.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BC_A03_GREYSTONE_MATERIALS_RECONCILE.md)
- [`C1259_GREYSTONE_SOURCE_INVENTORY.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/C1259_GREYSTONE_SOURCE_INVENTORY.md)

---

## 1. Texture Probe Delta (`0 -> 28` Unique Textures Resolved)

- Both `child_bp` (`BP_GreystoneERPlayer`) and `parent_bp` (`BP_GreystonePlayer`) now resolve **`28` unique textures** identically (`[C-1284]` `child_textures=28 parent_textures=28`):
  - **`2` Engine Shared Resources (`/Engine/...`):**
    - `/Engine/EditorMaterials/Cascade/CASC_Solo_On.CASC_Solo_On`
    - `/Engine/EngineResources/Black.Black`
  - **`26` Shared Paragon Greystone Global Textures (`/Game/ParagonGreystone/Characters/Global/...`):**
    - `Eyelash/`: `T_Universal_Eyelashes_D`
    - `Eyes/Textures/`: `Example/T_EyeIrisBaseColor_Example_5`, `Example/T_EyeScleraBaseColor_Example_3`, `Example/T_Eye_Wet_Normal`, `T_EpicQuadPanorama_CC`
    - `Hair/`: `SharedHairContent/AnimalHairSet01/T_AnimalHairSet01_{Depth,ID,Opacity,Root}`, `SharedHairContent/AnimalHairSet01/T_Greystone_Rabbit_HairColor`, `SharedHairContent/FemaleHairSet02/T_FemaleHairSet02_{Depth,ID,Opacity,Roots}`, `T_Caustics_2`, `T_Fire_Tiled_D`, `T_GreystoneHair_Flow`, `TestContent/T_HairClump02_{Depth,DyeMask}`
    - `MaterialFunctions/Textures/Noise/`: `T_AtmosphericCloudNoise03`
    - `Mouth/Textures/`: `T_Master_Mouth_1_{COLOR,N,RGB}`, `T_TeethAndTongue_{D2,N}`
    - `Global/`: `T_Black_Linear`

---

## 2. Reconciliation Against `C1259` Section 6.2 Footprint (`BD-A04`)

1. **`non_greystone_textures` (`28`) Explanation:** `probe_greystone_materials_textures.py` checks prefix `/Game/ParagonGreystone/Characters/Heroes/Greystone/`, so all `26` `/Game/ParagonGreystone/Characters/Global/` textures + `2` `/Engine/` defaults classify into `non_greystone_textures` by prefix rule even though those `26` textures belong to the Paragon Greystone character pack's shared global shader masters (`M_EyelashMaster_Inst`, `M_Eye_Occlusion`, `M_Mouth_MId_color`, `MIC_GreystoneFur`, `MIC_GreystoneHair`, `M_TearLine_Inst2`, `M_TearDuct_Darker`, `M_Greystone_Dragonlord_EyeRefractive_Inst`). Zero foreign non-Paragon-Greystone project/pack textures leaked in.
2. **Hero Armor Textures (`C1259` `39` Files in `Heroes/Greystone/Textures/`):** Not emitted by `MaterialEditingLibrary.get_used_textures` on the `11` hero `MaterialInstanceConstant` / material slots in `materials4.log` (either static-switch / virtual / AssetRegistry hard dependencies vs `Material` parameter reflection); nevertheless, `Heroes/Greystone/Textures/` (`275.83 MB`) AND `Characters/Global/` (`26` resolved textures) MUST BOTH remain on disk in any local footprint minimization pass.
3. **Final Keep-List Update to `C1259` Section 6.2:** Minimal local Paragon Greystone runtime closure = `Meshes/` (`3`) + `Heroes/Greystone/Materials/` (`11`) + `Skins/Dragonlord/Materials/` (`1`) + `Characters/Global/{Eyelash,Eyes,Hair,MaterialFunctions,Mouth}/` (`3` materials + `26` textures) + `Heroes/Greystone/Textures/` (`39` disk assets).
