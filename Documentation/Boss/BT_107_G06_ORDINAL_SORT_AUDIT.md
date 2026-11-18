# BT-107: Independent Audit of G-06 Ordinal Hash Hotfix

## Executive Summary

- **Task:** [BT-107](file:///c:/UnrealProject/OneBossFight/Documentation/TASKS.md) â€” Independently audit G-06 ordinal hash hotfix.
- **Auditor:** Antigravity (Independent Implementer/Auditor).
- **Audit Target:** BT-106 aggregate-hash ordering hotfix in [run_probe_g06_roll_montages_locked.ps1](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/run_probe_g06_roll_montages_locked.ps1) and corresponding documentation across [BT_103_G06_ROLL_MONTAGE_READBACK_RUNNER.md](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/BT_103_G06_ROLL_MONTAGE_READBACK_RUNNER.md), [BT_105_G06_TARGET_PACKAGE_HASH_DRIFT_REPORT.md](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/BT_105_G06_TARGET_PACKAGE_HASH_DRIFT_REPORT.md), and [TASKS.md](file:///c:/UnrealProject/OneBossFight/Documentation/TASKS.md).
- **Result:** **ALL 5 CRITERIA PASS (CLEAN).**

---

## Audit Checklist & Empirical Findings

### 1. Runner explicitly uses culture-invariant ordinal ordering: **PASS**
- Line 116 in [run_probe_g06_roll_montages_locked.ps1](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/run_probe_g06_roll_montages_locked.ps1) invokes:
  ```powershell
  $hashList.Sort([System.StringComparer]::Ordinal)
  ```
- This enforces strict byte-by-byte ordinal sort order, eliminating Windows culture/locale linguistic collation differences (where `_` was previously sorted ahead of `.` in word sort mode).

### 2. Target package discovery and file set is unchanged: **PASS**
- Target packages array remains identical:
  1. `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage`
  2. `/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage_Grey`
  3. `/Game/OneBossFight/Player/Greystone/RootMotion/Montages/quick/Dodge_Small_Forward_Roll_Montage_Grey_RM`
  4. `/Game/OneBossFight/Player/Greystone/BP_GreystoneERPlayer`
- Discovery mechanism (`Get-AssetPackageFiles`) continues to resolve exactly one `.uasset` file per package.

### 3. Same four current per-file hashes yield canonical `4CCFA3E0...`: **PASS**
- Individual file SHA-256 hashes on disk remain:
  - `BP_GreystoneERPlayer.uasset`: `527319C0B9FC35709D4D6DD3DBE3E7579BE4F7E439B68A521713E2C86B374824`
  - `Dodge_Small_Forward_Roll_Montage.uasset`: `7C4140900B1A32BEDAB53531B0C7FBE044A64948CEA28F5B6BC748928ED26542`
  - `Dodge_Small_Forward_Roll_Montage_Grey.uasset`: `B851C8D0A17441A587E27D3312CA180C13CE81102BC29C916BB66B938F93BF27`
  - `Dodge_Small_Forward_Roll_Montage_Grey_RM.uasset`: `87010FF5A2F5E1C4F96BE43739958271BF5581E5183D581B0D6C00C5128D74E0`
- Under `$hashList.Sort([System.StringComparer]::Ordinal)`, the sorted order is:
  1. `BP_GreystoneERPlayer.uasset=527319C0...`
  2. `Dodge_Small_Forward_Roll_Montage.uasset=7C414090...`
  3. `Dodge_Small_Forward_Roll_Montage_Grey.uasset=B851C8D0...`
  4. `Dodge_Small_Forward_Roll_Montage_Grey_RM.uasset=87010FF5...`
- Deterministic aggregate SHA-256:
  $$\text{Asset Hash} = \texttt{4CCFA3E08310B371FE4A10D052D957DD96A29743E83E742245898E1573BDB24B}$$
- Verified via live PowerShell execution: returns `True` against canonical `4CCFA3E0...`.

### 4. Runner SHA256 and pending approval language match across documents: **PASS**
- Live file hash of `run_probe_g06_roll_montages_locked.ps1`:
  $$\text{SHA256} = \texttt{479775D916340A7E277239A0F1CE50DFE15E93538D2C19A1F232314EF6A8C51D}$$
- Matches across:
  - [BT_103_G06_ROLL_MONTAGE_READBACK_RUNNER.md](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/BT_103_G06_ROLL_MONTAGE_READBACK_RUNNER.md) (Lines 83, 93)
  - [BT_105_G06_TARGET_PACKAGE_HASH_DRIFT_REPORT.md](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/BT_105_G06_TARGET_PACKAGE_HASH_DRIFT_REPORT.md) (Lines 14, 96)
  - [TASKS.md](file:///c:/UnrealProject/OneBossFight/Documentation/TASKS.md) (Lines 3668, 3674)
- All documents consistently state that BT-104 remains paused pending Owner authorization of the updated source-hash envelope.

### 5. No report implies runner/readback execution: **PASS**
- Reviewed all reports and task entries; all state clearly that the runner has not been invoked, no Unreal Editor process was launched, no C-1155 locks were acquired, and no asset/config changes were made.

---

## Disposition

- Audit Outcome: **APPROVED / CLEAN**.
- Task BT-107 is ready for movement to `review`.
- No documentation hotfixes required; alignment is complete.
