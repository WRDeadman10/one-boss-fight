# BH-A16..BH-A20: Paragon Greystone On-Disk Closure & Authored Asset SHA-256 Audit

**Authority:** [`QUEUE_BH_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BH_AG.md) Batch 4 (`BH-A16..BH-A20`)  
**Scope:** Strictly read-only disk, probe, and Git LFS pointer SHA-256 verification (`0` commits, `0` pushes, `0` editor calls, `0` third-party pack tracking).

---

## 1. `BH-A16`: Paragon Greystone Physical Disk Closure & Tracking Status

Cross-checked against [`BD_A03_A04_GREYSTONE_TEXTURES_RECONCILE.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BD_A03_A04_GREYSTONE_TEXTURES_RECONCILE.md) and `Saved/BossCombatReview/bb_a15_greystone_materials_probe.json`:

| Asset Bucket | Physical Path / Scope | Disk Count | Zero-Byte Files | `git ls-files` Count |
|---|---|---|---|---|
| **Hero Materials** | `Content/ParagonGreystone/Characters/Heroes/Greystone/Materials/` | `15` (`.uasset`) | `0` | `0` |
| **Resolved Global Textures** | `probe['child_bp']['unique_textures']` (`/Game/ParagonGreystone/Characters/Global/...`) | `26` (`.uasset` resolved; `182` total in `Global/`) | `0` | `0` |
| **Hero Armor Textures** | `Content/ParagonGreystone/Characters/Heroes/Greystone/Textures/` | `39` (`.uasset`) | `0` | `0` |

---

## 2. `BH-A17` & `BH-A18`: SHA-256 Parity (`B_C1280_GREYSTONE2` + `5` Authored Greystone `.uasset`s)

1. **`B_C1280_GREYSTONE2/evidence_sha256.txt`:** Note that `evidence_sha256.txt` records SHA-256 digests for the `34` capture/build logs inside `Docs/BossCombatReview/Execution/Claude/B_C1280_GREYSTONE2/` (`34/34` verified bit-exact against disk, `0` mismatches).
2. **Authored Project Greystone `.uasset`s (`Content/OneBossFight/Player/Greystone/*.uasset`):** Verified bit-exact `5/5` parity between live disk SHA-256 and committed Git LFS `HEAD` `oid sha256` pointers (`0` uncommitted changes):

| Authored Asset | Byte Size | Verified SHA-256 (`disk == HEAD LFS oid`) |
|---|---|---|
| `AM_ER_Attack_Air_Heavy_Plunge_Fit_Greystone.uasset` | `11,786` | `e02670a3920abd8963f0b0eea20aa708c328154931f7a2cea099d8a537142653` |
| `AM_ER_Attack_Air_Light_Fit_Greystone.uasset` | `9,458` | `45066e059081e262c82b6cb8640f90f678f2167a57d2f16e16a45c71ee45de82` |
| `AM_ER_Attack_GuardCounter_Fit_Greystone.uasset` | `19,486` | `2506b804e4e127e5016e4e3caacfb27d12c38b8143a48ba5ec4e78bdfe0133cb` |
| `AM_ER_Backstep_Mixamo_V2_Fit_Greystone.uasset` | `9,428` | `9d9046f5dbf704046b82dafefb36c2d4b8612b1d3777f4518df9be718bcb8cf4` |
| `BP_GreystoneERPlayer.uasset` | `37,840` | `91a4a63965c5ade63906221d404cdfb341028482c8be7dcc5fff43ca8e644373` |

Enforced offline by [`Scripts/Tools/test_bh_a18_greystone_sha256_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bh_a18_greystone_sha256_contract.py).

---

## 3. `BH-A19` & `BH-A20`: Lead Blockers & Batch 4 Owner-Ready Manifest

- **`BH-A19` (`BLOCKED`):** Lead `_RM` re-retarget (`ERFitRM_*.json` with `GLOBALLY_SCALED` on disk `.uasset`s), `RM4` controlled paired Mannequin/Greystone PIE capture, `KI-052`, and live `X26` Sevarog PIE remain **`BLOCKED`** awaiting Lead `[C-1286+]`. (Wait to re-baseline LFS hashes only when intentional Lead re-save occurs.)
- **`BH-A20` Batch 4 Owner-Ready Manifest (`0` commits, `0` media staged):**
  - [`Documentation/Boss/BH_A16_A20_PARAGON_GREYSTONE_SHA_AUDIT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BH_A16_A20_PARAGON_GREYSTONE_SHA_AUDIT.md)
  - [`Scripts/Tools/test_bh_a18_greystone_sha256_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bh_a18_greystone_sha256_contract.py)
