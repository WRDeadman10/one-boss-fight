# BH-A11..BH-A15: SFX Batch `1–9` Asset Byte-Size & Option `A/B/C` Mapping Audit

**Authority:** [`QUEUE_BH_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BH_AG.md) Batch 3 (`BH-A11..BH-A15`)  
**Scope:** Strictly read-only disk byte & spec alignment verification (`0` commits, `0` pushes, `0` editor calls, `0` wiring mutations).

---

## 1. `BH-A11`: Active SFX & Sevarog Voice `.uasset` On-Disk Byte Summary

Every `/Game/` `SoundCue`, `SoundWave`, and `DialogueWave` referenced in [`BB_A11_A13_SEVAROG_CARD_SFX_SPEC.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BB_A11_A13_SEVAROG_CARD_SFX_SPEC.md), [`BB_A14_SEVAROG_VOICE_BARKS_SPEC.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BB_A14_SEVAROG_VOICE_BARKS_SPEC.md), [`BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md), [`SFX_03_AUDITION_MANIFEST.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/SFX_03_AUDITION_MANIFEST.md), and `SFX_05..SFX_12` resolves physically under `Content/`:

- **Verified unique `/Game/` audio assets:** `119 / 119` (`zero_or_missing = 0`)
- **Min `.uasset` byte size:** `2,281` bytes
- **Max `.uasset` byte size:** `2,312,702` bytes
- **Combined disk footprint:** `14,474,227` bytes (`~13.80 MiB`)

---

## 2. `BH-A12`: `BB_A05` vs `SFX_03` / `SFX_06` Option `A/B/C` Mapping & Regression Check

- Cross-checked [`BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md) against [`SFX_03_AUDITION_MANIFEST.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/SFX_03_AUDITION_MANIFEST.md) (`Gap 1..5` + `C-1186` Parry Addendum) and [`SFX_06_BATCH3_AUDITION_MANIFEST.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/SFX_06_BATCH3_AUDITION_MANIFEST.md) (`SFX-11..15` Option `A/B/C`).
- Every Option `A/B/C` entry in `SFX_03`, `SFX_05..SFX_12`, `BB_A11_A13`, and `BB_A14` resolves cleanly (`0` `SFX_02` shorthand regressions in any active spec; `SFX_01`, `SFX_02`, `SFX_04` remain archival historical notes only).

---

## 3. `BH-A13..BH-A15`: Contract Test, Owner Blockers & Batch 3 Manifest

- **`BH-A13` Contract Test:** [`Scripts/Tools/test_bh_a13_sfx_disk_bytes_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bh_a13_sfx_disk_bytes_contract.py) extracts all audio `/Game/` references across `BB_A05`, `BB_A11_A13`, `BB_A14`, `SFX_03`, and `SFX_05..SFX_12` and asserts `100%` on-disk `.uasset` existence with `st_size > 0` (`0` shorthand regressions).
- **`BH-A14` (`BLOCKED`):** Owner SFX audition picks (`Batch 1–9`) and `BB-A24` Phase-2 aura selection remain **`BLOCKED`** pending Owner reply.
- **`BH-A15` Batch 3 Owner-Ready Manifest (`0` commits, `0` media staged):**
  - [`Documentation/Boss/BH_A11_A15_SFX_DISK_AUDIT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BH_A11_A15_SFX_DISK_AUDIT.md)
  - [`Scripts/Tools/test_bh_a13_sfx_disk_bytes_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bh_a13_sfx_disk_bytes_contract.py)
