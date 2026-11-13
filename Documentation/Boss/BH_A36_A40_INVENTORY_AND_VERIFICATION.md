# BH-A36..BH-A40: `Content/OneBossFight/` Inventory, Queue `BC..BH` Cross-Links & Offline Suite Sweep

**Authority:** [`QUEUE_BH_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BH_AG.md) Batch 8 (`BH-A36..BH-A40`)  
**Scope:** Strictly read-only disk inventory, link audit, & offline unittest execution (`0` commits, `0` pushes, `0` editor calls).

---

## 1. `BH-A36`: `Content/OneBossFight/` Asset Inventory vs `.gitignore`

| Subfolder | `.uasset`/`.umap` Count | Tracked (`git ls-files`) | Byte Size | `.gitignore` Rule Alignment |
|---|---|---|---|---|
| `Data/` | `32` | `32` (`100%`) | `275,333` | Tracked project DataAssets (`AlwaysCook`) |
| `Player/` | `41` | `41` (`100%`) | `10,096,735` | Tracked incl. `5` Greystone `.uasset`s (`AlwaysCook`) |
| `VFX/` | `6` | `6` (`100%`) | `12,748,217` | Tracked Niagara VFX (`AlwaysCook`) |
| `Audio/` | `2` | `2` (`100%`) | `55,926,203` | Tracked project audio (`AlwaysCook`) |
| `Poise/` | `1` | `1` (`100%`) | `6,757` | Tracked poise asset (`AlwaysCook`) |
| `UI/` | `7` | `7` (`100%`) | `190,471` | Tracked UI assets (`AlwaysCook`) |
| `Boss/` + `Boss01/` + `Effects/` + `Environment/` + `Input/` + `Levels/` + `ReviewFixtures/` + `Scratch/` | `123` | `123` (`100%`) | `46,093,502` | Tracked project content |
| `Characters/` | `44` | `38` | `80,245,819` | `6` untracked under `Characters/Greystone/` ignored by `.gitignore` |
| `FrameworkProof/` | `193` | `179` | `2,619,372` | `14` test/scratch proof assets explicitly ignored by `.gitignore` |
| `GreystonePack/` + `SevarogPack/` | `393` + `32` | `0` + `0` | `103,125,890` + `863,514` | Retarget/copy packs explicitly ignored by `.gitignore` |

---

## 2. `BH-A37`: Queue `BC..BH` Cross-Link & Orphan Audit

- Audited all `92` docs matching `^(B[C-H]_|QUEUE_B[C-H])*.md` in `Documentation/Boss/` (`67` referenced by peer docs; earlier `BC_A01_A05_STATUS.md` + new `BH_*` batch docs were unlinked from peer indexes, while the remaining `18` `B[C-F]_X*`/`QUEUE_BE_PRE_C1274_SUPERSEDED` belong to Codex's lane).
- Cross-linking all `BH` batch deliverables & [`BC_A01_A05_STATUS.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BC_A01_A05_STATUS.md) here and in [`QUEUE_BH_AG_CLOSEOUT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BH_AG_CLOSEOUT.md) leaves **`0` orphaned Antigravity Queue `BC..BH` documents**:
  - [`BH_A01_A05_MEDIA_ARCHIVE_AUDIT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BH_A01_A05_MEDIA_ARCHIVE_AUDIT.md)
  - [`BH_A06_A10_SIGNATURE_ANCHORS.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BH_A06_A10_SIGNATURE_ANCHORS.md)
  - [`BH_A11_A15_SFX_DISK_AUDIT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BH_A11_A15_SFX_DISK_AUDIT.md)
  - [`BH_A16_A20_PARAGON_GREYSTONE_SHA_AUDIT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BH_A16_A20_PARAGON_GREYSTONE_SHA_AUDIT.md)
  - [`BH_A21_A25_VFX_AND_CONFIG_AUDIT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BH_A21_A25_VFX_AND_CONFIG_AUDIT.md)
  - [`BH_A26_A30_OVERSIZED_LOG_AND_INDEX_AUDIT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BH_A26_A30_OVERSIZED_LOG_AND_INDEX_AUDIT.md)
  - [`BH_A31_UNBLOCK_SEQUENCE_BRIEF.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BH_A31_UNBLOCK_SEQUENCE_BRIEF.md)
  - [`BH_A41_A45_FINAL_CONSOLIDATED_MANIFEST.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BH_A41_A45_FINAL_CONSOLIDATED_MANIFEST.md)

---

## 3. `BH-A38..BH-A40`: Offline Verification Sweep & Batch 8 Manifest (`0` Commits)

| Check / Suite | Scope | Result |
|---|---|---|
| `test_check_shipping_guards.py` (`BH-A38`) | Latest `Source/` C++ guards | **`4/4 PASS`** |
| `test_bh_*.py` | `BH-A03`, `BH-A08`, `BH-A13`, `BH-A18`, `BH-A23`, `BH-A28` | **`12/12 PASS`** |
| `test_bg_*.py` / `test_bf_*.py` / `test_be_*.py` / `test_bd_*.py` | Active queues `BD..BG` (`test_b*_contract.py` `88/88`) | **`1/1` / `14/14` / `33/33` / `10/10` PASS** |
| Contract tests (`test_c1285`, `test_pie_warmup`, `test_probe`, `test_c1276`, `test_c1278`, `test_validate_queue_batches`) | Root chain, warmup, probe, Sevarog S6–S8, X26, Queue schema | **`18/18 PASS`** |
| `check_doc_links.py` | Full workspace markdown link check | **`broken_links=0`** |

- **`BH-A40` Batch 8 Owner-Ready Manifest (`0` commits, `0` media staged):** [`BH_A36_A40_INVENTORY_AND_VERIFICATION.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BH_A36_A40_INVENTORY_AND_VERIFICATION.md).
