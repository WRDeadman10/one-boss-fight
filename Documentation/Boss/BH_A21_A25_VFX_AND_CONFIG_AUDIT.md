# BH-A21..BH-A25: Niagara VFX Disk Footprint & `DefaultEngine.ini` / `DefaultGame.ini` Graphics Audit

**Authority:** [`QUEUE_BH_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BH_AG.md) Batch 5 (`BH-A21..BH-A25`)  
**Scope:** Strictly read-only disk & config inspection (`0` commits, `0` pushes, `0` editor/VFX/config mutations).

---

## 1. `BH-A21`: `Content/OneBossFight/VFX/*.uasset` Inventory & `BB_A24` Cross-Check

All `6 / 6` Niagara assets in `Content/OneBossFight/VFX/` are tracked (`git ls-files = 6`) with non-zero byte sizes (`12,748,217` bytes total):

| Asset | Byte Size | Role / `BB_A24` Status |
|---|---|---|
| `NS_Boss_PhaseTwoAura.uasset` | `1,944,328` | Base Ember Phase-2 aura asset |
| `NS_Boss_PhaseTwoAura_Boost.uasset` | `1,948,492` | Historical review candidate (`C-1210` — excluded, do not reference) |
| `NS_Boss_PhaseTwoAura_BoostLite.uasset` | `1,948,552` | Historical review candidate (`C-1210` — excluded, do not reference) |
| `NS_Boss_PhaseTwoAura_BoostLite_Authored.uasset` | `2,184,059` | Active Ember Phase-2 aura / Cand C structural baseline in [`BB_A24_SEVAROG_PHASE2_AURA_CANDIDATES.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BB_A24_SEVAROG_PHASE2_AURA_CANDIDATES.md) |
| `NS_Boss_ShockwaveRing.uasset` | `2,164,027` | Shockwave ring VFX |
| `NS_Combat_ParrySpark.uasset` | `2,558,759` | Parry deflect spark VFX |

Cross-checked [`BB_A24_SEVAROG_PHASE2_AURA_CANDIDATES.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BB_A24_SEVAROG_PHASE2_AURA_CANDIDATES.md): `Content/ParagonSevarog/FX/Particles/` contains `35` legacy Cascade `UParticleSystem` `.uasset`s and `0` Niagara assets, matching `TSoftObjectPtr<UNiagaraSystem> PhaseTwoAuraEffect` spec (`<= 60` particles on Cand A, bounded fixed bounds per `C-1202`).

---

## 2. `BH-A22` & `BH-A23`: `DefaultEngine.ini` & `DefaultGame.ini` Graphics & Cook Root Audit

- **`Config/DefaultEngine.ini` (`[/Script/Engine.RendererSettings]`):**
  - Preserves UE 5.5 engine TSR default (`C-954`: no `r.AntiAliasingMethod` or forced `r.NGX.DLSS.*` debug CVars; `GameUserSettingsClassName=/Script/OneBossFight.RPGDLSSGameUserSettings` handles runtime opt-in).
  - Keeps `r.AllowStaticLighting=False`, `r.GenerateMeshDistanceFields=True`, `r.DynamicGlobalIlluminationMethod=1`, `r.ReflectionMethod=1`, `r.RayTracing=True`, `r.Shadow.Virtual.Enable=1`.
  - Default maps remain `/Game/OneBossFight/Levels/L_SevarogArena.L_SevarogArena`.
- **`Config/DefaultGame.ini` (`[/Script/UnrealEd.ProjectPackagingSettings]`):**
  - Preserves all project runtime cook directories including `/Game/OneBossFight/VFX`, `/Game/OneBossFight/Audio`, `/Game/OneBossFight/Data`, `/Game/OneBossFight/Poise`, `/Game/OneBossFight/UI`, `/Game/OneBossFight/Player/Greystone`, and `/Game/ParagonSevarog`.
  - Preserves `bDefaultToDataStartup=True` and `bTier2PresentationEnabled=True`.
- **Contract Test (`BH-A23`):** [`Scripts/Tools/test_bh_a23_graphics_config_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bh_a23_graphics_config_contract.py) asserts TSR default preservation, zero forced DLSS/debug CVars, required cook roots, and all `6` VFX `.uasset`s non-zero on disk.

---

## 3. `BH-A24` & `BH-A25`: Blockers & Batch 5 Owner-Ready Manifest

- **`BH-A24` (`BLOCKED`):** `NS_Sevarog_PhaseTwoAura_*` Niagara asset authoring remains **`BLOCKED`** awaiting Owner candidate pick (`BB_A24`) and Lead Unreal Editor slot (`[C-1286+]`).
- **`BH-A25` Batch 5 Owner-Ready Manifest (`0` commits, `0` media staged):**
  - [`Documentation/Boss/BH_A21_A25_VFX_AND_CONFIG_AUDIT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BH_A21_A25_VFX_AND_CONFIG_AUDIT.md)
  - [`Scripts/Tools/test_bh_a23_graphics_config_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bh_a23_graphics_config_contract.py)
