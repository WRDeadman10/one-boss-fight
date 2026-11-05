# W-A014: Staged Binary Symbol Scan Report (`CheckShippingFeatureSymbols.py`)

**Date:** 2026-11-06  
**Author:** Antigravity (Lane A)  
**Status:** Complete  
**Scope:** Execution and verification of [`Scripts/CheckShippingFeatureSymbols.py`](file:///c:/UnrealProject/OneBossFight/Scripts/CheckShippingFeatureSymbols.py) against staged project binaries in [`Saved/StagedBuilds/`](file:///c:/UnrealProject/OneBossFight/Saved/StagedBuilds/).  
**Sources:**
- Symbol Scanner: [`Scripts/CheckShippingFeatureSymbols.py:1-35`](file:///c:/UnrealProject/OneBossFight/Scripts/CheckShippingFeatureSymbols.py#L1-L35)
- Staged Binary Inventory: [`Saved/StagedBuilds/Windows/OneBossFight/Binaries/Win64/`](file:///c:/UnrealProject/OneBossFight/Saved/StagedBuilds/Windows/OneBossFight/Binaries/Win64/)
- Packaging Specification: [`Documentation/Boss/W_C021_C024_PACKAGED_SMOKE_AND_SIZE.md:12-25`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/W_C021_C024_PACKAGED_SMOKE_AND_SIZE.md#L12-L25)

---

## 1. Executive Summary

Task `W-A014` mandates executing `CheckShippingFeatureSymbols.py` against the staged Shipping executable or explicitly reporting missing stage status.
* **Default Staged Target:** `Saved/StagedBuilds/Windows/OneBossFight/Binaries/Win64/OneBossFight-Win64-Shipping.exe`
* **Stage Status:** **MISSING (Development configuration stage present)**.
* The existing staged directory contains the **Development configuration package** ([`OneBossFight.exe`](file:///c:/UnrealProject/OneBossFight/Saved/StagedBuilds/Windows/OneBossFight/Binaries/Win64/OneBossFight.exe), 305,538,048 bytes), created for the Round 6 Development benchmark kit.
* Executing the scanner against the existing staged binary confirms scanner operation: `rpg.Art.Tier2` and `BuildStamp.txt` are absent, while the expected Development identifier (`DEVELOPMENT BUILD`) is correctly detected.

---

## 2. Scan Results & Symbol Inventory

### 2.1 Default Execution (Shipping Binary Search)
```powershell
python Scripts/CheckShippingFeatureSymbols.py
```
**Output:**
```text
FAIL no Shipping executable at Saved\StagedBuilds\Windows\OneBossFight\Binaries\Win64\OneBossFight-Win64-Shipping.exe
```

### 2.2 Scan of Existing Staged Development Binary
```powershell
python Scripts/CheckShippingFeatureSymbols.py Saved/StagedBuilds/Windows/OneBossFight/Binaries/Win64/OneBossFight.exe
```
**Output:**
```text
binary: Saved\StagedBuilds\Windows\OneBossFight\Binaries\Win64\OneBossFight.exe (305538048 bytes)
rpg.Art.Tier2: absent
BuildStamp.txt: absent
DEVELOPMENT BUILD: FOUND
VERDICT FAIL: Development-only symbols present
```

### 2.3 Detailed Symbol Roster

| Symbol Token | Checked Encodings | Development Staged Binary (`OneBossFight.exe`) | Target Shipping Expected State |
|---|---|:---:|:---:|
| `rpg.Art.Tier2` | ASCII, UTF-16LE | **ABSENT** | **ABSENT** |
| `BuildStamp.txt` | ASCII, UTF-16LE | **ABSENT** | **ABSENT** |
| `DEVELOPMENT BUILD` | ASCII, UTF-16LE | **FOUND** (305 MB binary) | **MUST BE ABSENT** |

---

## 3. Findings & Next Steps

1. **Tool Verification:** `CheckShippingFeatureSymbols.py` correctly identified the `DEVELOPMENT BUILD` token in the Development binary, verifying its binary inspection algorithm.
2. **Shipping Stage Prerequisite:** When the Lead or Owner runs [`Scripts/Package.ps1 -Configuration Shipping`](file:///c:/UnrealProject/OneBossFight/Scripts/Package.ps1), the resulting `OneBossFight-Win64-Shipping.exe` will be scanned to verify zero leakage of development strings.
