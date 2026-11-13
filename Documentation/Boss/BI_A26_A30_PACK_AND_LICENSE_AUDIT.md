# BI-A26..BI-A30: Third-Party Content Packs vs `ASSET_LICENSES.md` & `.gitignore` Audit

**Authority:** [`QUEUE_BI_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BI_AG.md) Batch 6 (`BI-A26..BI-A30`)  
**Contract Gate:** [`Scripts/Tools/test_bi_a29_pack_ignore_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bi_a29_pack_ignore_contract.py)  
**Scope:** Strictly read-only disk, `.gitignore`, `git ls-files`, & license register audit (`0` edits to packs, `0` commits).

---

## 1. `BI-A26..BI-A27`: Third-Party `Content/` Pack Inventory & Git Isolation (`0` Tracked, `0` Dirty)

Every third-party directory under `Content/` (`dirty_content_count = 0`) is strictly isolated from git tracking via `.gitignore`:

| Pack Directory (`Content/<Dir>`) | On-Disk Files | Total Bytes | `git ls-files` Count | `ASSET_LICENSES.md` Entry |
|---|---:|---:|---:|---|
| `ParagonGreystone` | `1,735` | `2,280,171,217` | `0` | Listed (Fab Standard) |
| `ParagonGrux` | `1,406` | `3,110,644,727` | `0` | Listed (Fab Standard) |
| `ParagonSevarog` | `1,071` | `1,448,859,480` | `0` | Listed (Fab Standard) |
| `ParagonSteel` | `1,585` | `2,276,310,858` | `0` | Listed (Fab Standard) |
| `AdvancedARPGCombat` | `2,557` | `3,058,405,345` | `0` | Listed (creator/URL to fill) |
| `MS` / `MSPresets` / `CustomAssets` / `Smart` / `Materials` / `Blueprints` / `Effects` / `Textures` | `736` | `10,644,869,865` | `0` | Listed (Dark Ruins Megascans sample) |
| `Deadly_Ruins` / `Free_Spells` / `Mage` / `BeamPack` / `BloodPack` / `RealisticSwordSoundEffects` | `725` | `1,620,613,183` | `0` | Listed (creator/URL to fill) |
| **`Essential_Foosteps_SK`** | `521` | `49,509,275` | `0` | **MISSING from `ASSET_LICENSES.md`** *(cooked in `DefaultGame.ini`)* |
| **`Vefects`** | `295` | `170,221,086` | `0` | **MISSING from `ASSET_LICENSES.md`** *(used by SFX Batch 1 & 3)* |
| **`UnrealClaude`** | `207` | `42,890` | `0` | **MISSING from `ASSET_LICENSES.md`** *(local editor plugin workspace)* |

*(Note: `StarterContent` holds `264` historically tracked sample files of `267` on disk, and `ThirdParty` holds `5` historical tracked files of `10`.)*

---

## 2. `BI-A28..BI-A30`: Shipping License Gaps & Regression Contract

- **Actionable Shipping Gap for Owner / Lead:** [`Documentation/ASSET_LICENSES.md`](file:///C:/UnrealProject/OneBossFight/Documentation/ASSET_LICENSES.md) must add entries + creator/listing URLs for `Essential_Foosteps_SK` and `Vefects` (plus fill the `"to be filled"` creator/URL entries on `AdvancedARPGCombat`, `RealisticSwordSoundEffects`, `Free_Spells`, `Mage`, `BeamPack`, `BloodPack`, `Deadly_Ruins`, and `DarkRuinsMegascansSample`) before any public/commercial Shipping distribution.
- **Contract Test (`BI-A29`):** [`test_bi_a29_pack_ignore_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bi_a29_pack_ignore_contract.py) asserts `0` tracked or modified files across all third-party packs (`Paragon*`, `AdvancedARPGCombat`, `MS*`, `Deadly_Ruins`, `Free_Spells`, `Mage`, `BeamPack`, `BloodPack`, `RealisticSwordSoundEffects`, `Essential_Foosteps_SK`, `Vefects`).
