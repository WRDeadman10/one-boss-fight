# BT-105: Trace G-06 Target Package Hash Drift Report

## Executive Summary

- **Task:** [BT-105](file:///c:/UnrealProject/OneBossFight/Documentation/TASKS.md) â€” Trace G-06 target package hash drift.
- **Investigator:** Antigravity (Implementer).
- **Core Finding:**
  1. **Zero on-disk file byte drift has occurred.** All four target package `.uasset` files on disk are bit-for-bit identical to their state when BT-100 and BT-103 were completed.
  2. **The root cause of the hash discrepancy was collation mismatch (ordinal vs culture-sensitive PowerShell `Sort-Object`):**
     - The hash `4CCFA3E08310B371FE4A10D052D957DD96A29743E83E742245898E1573BDB24B` (approved in [H-18]) was calculated using **ASCII/Ordinal collation** (where `.` ASCII 46 sorts before `_` ASCII 95).
     - The hash `5FC7C20C9733E6DE4AAA1D3DCF0B57AF0DA9FFA53C740471FD13663AC0FD17FF` is the actual, deterministic output of **PowerShell's default `Sort-Object`** in [run_probe_g06_roll_montages_locked.ps1](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/run_probe_g06_roll_montages_locked.ps1), where Windows linguistic word-sort collation orders `_` (underscore) before `.` (period).
  3. Before BT-106, the accepted runner invoked `($hashList | Sort-Object) -join "`n"`, and its runtime evaluation on these files was `5FC7C20C9733E6DE4AAA1D3DCF0B57AF0DA9FFA53C740471FD13663AC0FD17FF`.
  4. Lead Codex's preflight abort on BT-104 was entirely correct: running under the [H-18] approved hash `4CCFA3...` fails the runner's preflight check.
  5. BT-106 fixed the source by using explicit ordinal ordering. Current runner SHA256 is `479775D916340A7E277239A0F1CE50DFE15E93538D2C19A1F232314EF6A8C51D`; current aggregate asset hash is again `4CCFA3E08310B371FE4A10D052D957DD96A29743E83E742245898E1573BDB24B`, with unchanged package bytes.

---

## 1. Package Inventory & File-Level Hashes (Unchanged)

All four target packages defined in [run_probe_g06_roll_montages_locked.ps1](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/run_probe_g06_roll_montages_locked.ps1) and [probe_g06_roll_montages.py](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/probe_g06_roll_montages.py) have zero byte drift:

| # | Package Path | Disk File Path | Size (Bytes) | Last Modified (UTC) | Individual File SHA-256 |
|---|---|---|---|---|---|
| 1 | `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage` | `Content/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage.uasset` | 16,363 | 2025-12-12 17:33:33 | `7C4140900B1A32BEDAB53531B0C7FBE044A64948CEA28F5B6BC748928ED26542` |
| 2 | `/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage_Grey` | `Content/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage_Grey.uasset` | 18,256 | 2026-10-19 11:02:09 | `B851C8D0A17441A587E27D3312CA180C13CE81102BC29C916BB66B938F93BF27` |
| 3 | `/Game/OneBossFight/Player/Greystone/RootMotion/Montages/quick/Dodge_Small_Forward_Roll_Montage_Grey_RM` | `Content/OneBossFight/Player/Greystone/RootMotion/Montages/quick/Dodge_Small_Forward_Roll_Montage_Grey_RM.uasset` | 17,720 | 2026-11-18 05:42:12 | `87010FF5A2F5E1C4F96BE43739958271BF5581E5183D581B0D6C00C5128D74E0` |
| 4 | `/Game/OneBossFight/Player/Greystone/BP_GreystoneERPlayer` | `Content/OneBossFight/Player/Greystone/BP_GreystoneERPlayer.uasset` | 46,163 | 2026-11-13 19:21:06 | `527319C0B9FC35709D4D6DD3DBE3E7579BE4F7E439B68A521713E2C86B374824` |

---

## 2. Collation Analysis: Ordinal vs PowerShell Linguistic Sort

In [run_probe_g06_roll_montages_locked.ps1](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/run_probe_g06_roll_montages_locked.ps1), lines 107â€“122 implement:
```powershell
function Compute-DeterministicAssetHash {
    $hashList = [System.Collections.Generic.List[string]]::new()
    foreach ($pkg in $targetPackages) {
        $files = Get-AssetPackageFiles $pkg
        foreach ($file in ($files | Sort-Object Name)) {
            $h = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
            $hashList.Add($file.Name + '=' + $h)
        }
    }
    $combined = ($hashList | Sort-Object) -join "`n"
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($combined)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hashBytes = $sha.ComputeHash($bytes)
        return ([System.BitConverter]::ToString($hashBytes).Replace('-', '').ToUpperInvariant())
    } finally {
        $sha.Dispose()
    }
}
```

### 2.1 The Two Collation Behaviors

1. **Ordinal / ASCII Sort (Python `sorted()` / `[StringComparer]::Ordinal`):**
   - ASCII character code for `.` is 46; ASCII character code for `_` is 95.
   - Because $46 < 95$, `.uasset` sorts **before** `_Grey` and `_RM`.
   - Ordinal ordering:
     1. `BP_GreystoneERPlayer.uasset=527319C0...`
     2. `Dodge_Small_Forward_Roll_Montage.uasset=7C414090...`
     3. `Dodge_Small_Forward_Roll_Montage_Grey.uasset=B851C8D0...`
     4. `Dodge_Small_Forward_Roll_Montage_Grey_RM.uasset=87010FF5...`
   - SHA-256 of joined text:
     $$\text{Hash}_{\text{Ordinal}} = \texttt{4CCFA3E08310B371FE4A10D052D957DD96A29743E83E742245898E1573BDB24B}$$

2. **PowerShell `Sort-Object` (Windows Linguistic Word-Sort Collation):**
   - Windows default culture-sensitive string comparison treats `_` (symbol/connector) with lower sort weight than `.` (punctuation delimiter) in word-sort mode.
   - Consequently:
     - `Dodge_Small_Forward_Roll_Montage_Grey_RM...` has `_` at index 36 and index 41.
     - `Dodge_Small_Forward_Roll_Montage_Grey...` has `_` at index 36, followed by `.`.
     - `Dodge_Small_Forward_Roll_Montage...` has `.` at index 31.
   - Under Windows PowerShell `Sort-Object`:
     1. `BP_GreystoneERPlayer.uasset=527319C0...`
     2. `Dodge_Small_Forward_Roll_Montage_Grey_RM.uasset=87010FF5...`
     3. `Dodge_Small_Forward_Roll_Montage_Grey.uasset=B851C8D0...`
     4. `Dodge_Small_Forward_Roll_Montage.uasset=7C414090...`
   - SHA-256 of joined text:
     $$\text{Hash}_{\text{PowerShell}} = \texttt{5FC7C20C9733E6DE4AAA1D3DCF0B57AF0DA9FFA53C740471FD13663AC0FD17FF}$$

---

## 3. Discrepancy Attribution & Resolution

- **Why the mismatch occurred:** When the BT-103 deliverable was initially documented, the combined hash was reported from an ordinal/Python reference calculation (`4CCFA3...`), whereas the PowerShell runner script was authored using `$hashList | Sort-Object`, which uses PowerShell's culture-sensitive word sort (`5FC7C2...`).
- **Confirmation:** Executing `test_all_permutations.py` mathematically proved that among all $4! = 24$ permutations of the four target strings, exactly one permutation yields `5FC7C20C9733E6DE4AAA1D3DCF0B57AF0DA9FFA53C740471FD13663AC0FD17FF`: the exact linguistic word-sort ordering produced by PowerShell's `Sort-Object`.
- **Preflight Impact:** When Codex executed preflight in BT-104, the runner called `Compute-DeterministicAssetHash`, which evaluated via `Sort-Object` to `5FC7C20C...`. Comparing this against the approval request (which specified `4CCFA3...`) triggered the runner's preflight abort, exactly as designed.

---

## 4. Current Disposition after BT-106

BT-106 changed the runner to use explicit ordinal ordering; this fixes the locale-sensitive aggregate hash while preserving the Owner-approved `4CCFA3...` asset value. Because the runner source hash changed, the earlier source-hash envelope is stale. BT-104 must remain unexecuted until the Owner approves the refreshed exact source-hash envelope and Codex creates a fresh lead receipt. The current envelope is:
   - `runner`: `479775D916340A7E277239A0F1CE50DFE15E93538D2C19A1F232314EF6A8C51D`
   - `probe`: `412D99A00C2D19C5800D8CBB3539DC40249004793000443AF6D5A7B478A5B190`
   - `project`: `B9FE452589D2E13E096DFFCD364EA4F6C541C56670F55CF5317F2BC127C35818`
   - `editor_module`: `EDC6CB6C81B04E1203663B5F6270C82069A49376BC0EA3E290ADAA4573192E31`
   - `assets`: `4CCFA3E08310B371FE4A10D052D957DD96A29743E83E742245898E1573BDB24B`

---

## 5. Verification

- Mathematical permutation validation: [scratch/test_all_permutations.py](file:///c:/Users/Rushit%20Vaghela/.gemini/antigravity/brain/08607dc5-9f3b-4f98-a918-defe9349a048/scratch/test_all_permutations.py).
- PowerShell collation confirmation: [scratch/check_ps_sort.ps1](file:///c:/Users/Rushit%20Vaghela/.gemini/antigravity/brain/08607dc5-9f3b-4f98-a918-defe9349a048/scratch/check_ps_sort.ps1).
- Doc link check: `python c:/UnrealProject/OneBossFight/Scripts/Tools/check_doc_links.py` (`broken_links=0`).
