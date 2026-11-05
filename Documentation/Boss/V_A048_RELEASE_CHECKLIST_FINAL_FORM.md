# V-A048: Final Release Gate Checklist

**Author:** Antigravity (Offline Quality, Audit & Asset Lane)  
**Date:** 2026-11-06  
**Scope:** Authoritative release gate criteria for packaging and shipping *One Boss Fight*.
**Sources:** Documentation/TEST_PLAN.md:1500-1525, Documentation/PROJECT_STATE.md:259

---

## 1. Executive Summary

- **Target Build:** Packaged Windows 64-bit Shipping build (`OneBossFight-Shipping.exe`).
- **Target Performance:** 1080p / 60 FPS, \(p99 \le 16.67\text{ ms}\) on RTX 2060 Super.
- **Contract:** Zero runtime drift against the D5 parity contract, zero broken assets, 100% native test pass.

---

## 2. Gate Verification Matrix

| Gate ID | Gate Dimension | Verification Mechanism | Acceptance Threshold | Responsible Lane |
| :--- | :--- | :--- | :--- | :--- |
| **`GATE-01`** | **Native Automation Suite** | `UnrealEditor-Cmd.exe -ExecCmds="Automation RunTests OneBossFight"` | **476 / 476 PASS**, 0 warnings, 0 failures | Lead Claude |
| **`GATE-02`** | **Cook Coverage** | `OneBossFight.Content.CookCoverage` native test | **PASS** (100% Source path literals registered in `DefaultGame.ini`) | Lead Claude |
| **`GATE-03`** | **D5 Parity Preservation** | `bUseLegacyStartup=True` in `DefaultGame.ini`, all soft refs default null | **PASS** (Zero allocations/spawns in Shipping baseline) | Codex & Antigravity |
| **`GATE-04`** | **Packaged Performance** | Staged Shipping Benchmark (`RunPerfExperiments.ps1`) | **\(p99 \le 16.67\text{ ms}\)** (60 FPS) across 3-minute duel | Lead Claude / Owner |
| **`GATE-05`** | **Asset Reference Integrity** | `check_doc_links.py` and redirector scan | **`broken_links=0`**, 0 project redirectors | Antigravity |
| **`GATE-06`** | **Git LFS Compliance** | `git lfs status` and `git lfs fsck` | Zero large binaries in packfiles; 100% uassets LFS tracked | Antigravity |
| **`GATE-07`** | **Look-Changing Art Approval**| Owner sign-off on Tier 2 Art Brief (`TIER2_ART_OWNER_BRIEF.md`) | Explicit Owner approval documented in mailbox | Owner |
| **`GATE-08`** | **Offline Quality Suite** | `python -m unittest discover -s Scripts/Tools -p "test_*.py"` | **320+ PASS**, 0 failures, 0 errors | Antigravity |
| **`GATE-09`** | **Documentation Integrity** | `Scripts/Tools/CheckDocLineCounts.ps1` | **ALL PASS** (no files shrank below baseline) | Antigravity |

---

## 3. Shipping Packaging Checklist

1. [ ] Rebuild clean Shipping binaries with editor closed (`Scripts/Rebuild.ps1 -Shipping`).
2. [ ] Stage build into `Saved/StagedBuilds/Windows/`.
3. [ ] Confirm `nvngx_dlss.dll` bundled in `OneBossFight/Plugins/Marketplace/DLSS/Binaries/ThirdParty/Win64/`.
4. [ ] Run 3 consecutive test duels without crash or VSM page-pool overflow.
5. [ ] Verify player victory sequence triggers corpse statue dissolve and HUD victory banner.
