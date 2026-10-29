# DD30 Chronology Build 2 (Release C-350) Run Report

**Agent:** Antigravity  
**Task:** C-350 / DD30ChronologyBuild2 (DD30 Chronology Promotion + ONE Build)  
**Date:** 2026-10-29  
**Status:** SUCCESS (Exit Code 0, Zero Errors, New DLL Produced)  

---

## 1. Execution Summary
- **Release ID:** `C-350`
- **Execution Directory:** `Docs/BossCombatReview/Execution/Antigravity/EngineRuns/DD30ChronologyBuild2/`
- **Build Command Line:**
  `"C:\Program Files\Epic Games\UE_5.5\Engine\Build\BatchFiles\Build.bat" OneBossFightEditor Win64 Development "-Project=C:\UnrealProject\OneBossFight\OneBossFight.uproject" -WaitMutex`
- **Build Start:** `2026-10-29T23:45:11.1700046+05:30`
- **Build End:** `2026-10-29T23:45:20.0104888+05:30`
- **Build Duration:** `8.84` seconds
- **Exit Code:** `0` (Success)
- **Engine Lock:** Acquired atomically via `engine_lock.py acquire`, released after evidence freeze via `engine_lock.py release`.

---

## 2. Promoted Files & Source Count
- **Total Source Files:** 219 (exact parity with baseline, 0 drift)
- **Promoted 3 Include-Order Fixed `.cpp` Files:**
  * `Source/OneBossFight/Player/RPGBossEncounter.cpp`:
    - Before (preimage): `3f3b62d834486c375ec9c2de1ef3423ad719fa81a81477149450d3ae542ee3be`
    - After (promoted): `bce27a9dd7c280423301eca600edb29263250c807b3d9bc3f4be962b7bede080`
  * `Source/OneBossFight/Player/RPGDodgeTiming.cpp`:
    - Before (preimage): `367bb788df0ab17eefd194aef0d1296cf62ad33f8befe91d60b9dcb50c634f36`
    - After (promoted): `acafc4a8ceb4f7dbe297e3688fe88722186311c863c29073c2dcac1ec9aedbee`
  * `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp`:
    - Before (preimage): `5d0f0be233e6bb6f054c47c96d07244758227b46c9739a04bf1d6236d3a0c703`
    - After (promoted): `dd279aa717633b3f5f523df62de72ca5d8af0e0ad18c57fe3f646fe855bd6f67`

---

## 3. Diagnostics (Errors & Warnings)
- **Compiler / UBT Errors:** **EXACTLY ZERO** (0).
  * The three include-order compilation diagnostics from run_C346 (`Expected RPGBossEncounter.h to be first header included`, etc.) are completely resolved.
- **Compiler Warnings:** **EXACTLY ONE** (1) known MSVC toolchain warning:
  * `Warning: Visual Studio 2022 compiler is not a preferred version`
  * Niagara plugin warnings did not re-trigger because plugin metadata was already cached.

---

## 4. Binary Outputs & Hashes
- `Binaries/Win64/UnrealEditor-OneBossFight.dll`:
  * Size: `738,304` bytes
  * SHA256: `332afd497b68c01b556be9fd73682574e97c31ed868f46a382ee0cb301bdaacf`
  * Baseline (C-346 failed build): `99baecdb4fb324e07f4ad488a34f76c798ec991c47f5cd73d05a66b0bdd5e875`
- `Binaries/Win64/UnrealEditor-OneBossFight.pdb`:
  * Size: `18,874,368` bytes
  * SHA256: `e27ab3814e895a305f07c01e47dc3d916f77e066566de14063fe97a28c05fdb6`
- `Binaries/Win64/OneBossFight.exe`:
  * Size: `550,400` bytes (unchanged)
  * SHA256: `5495fb88c31c1546a01329165d4bbe697671176dd263ee46f57ff2e3c9c34b65`

---

## 5. State Diff & Pin Preservation
- `content`: 0 added, 0 removed, 0 changed (11,755 files, 19 Data hashes).
- `config`: 0 added, 0 removed, 0 changed.
- `saved`: 0 added, 0 removed, 0 changed.
- `source`: 0 added, 0 removed, 0 changed (all 219 files match `promoted_source_manifest_sha256.txt`).
- `toolkit`: 0 added, 0 removed, 0 changed.
- `binary`: only `UnrealEditor-OneBossFight.dll` and `.pdb` updated.
- `saved_assets_unchanged.json`: all 3 saved draft assets (`DA_Boss_AbyssalRevenant_Draft`, `DA_Boss_EmberWarden_Draft`, `DA_Player_Hero_Draft`) bit-identical.
- `git status`: HEAD `605c2dd81d4092e8f84aa7608651ed19d566423a`.

---

## 6. Evidence Receipt (`receipt_sha256.txt`)
Receipt manifest contains 18 frozen files under `DD30ChronologyBuild2/` totaling all build artifacts, diffs, logs, and state snapshots.
