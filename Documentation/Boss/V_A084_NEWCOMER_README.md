# V-A084: One Boss Fight - Newcomer Engineering Onboarding Guide

**Date:** 2026-11-06  
**Author:** Antigravity (Lane A)  
**Status:** Canonical Reference  
**Scope:** Single-page onboarding guide covering environment prerequisites, build procedures, test automation, packaging, and agent collaboration rules.

---

## 1. Project Overview

- **Project:** *One Boss Fight* (Soulslike boss duel: Greystone vs Sevarog in `L_SevarogArena`).
- **Engine Version:** Unreal Engine 5.5.4 (built upon Advanced ARPG Combat pack).
- **Target Performance Profile:** 1080p / 60 FPS packaged (p99 <= 16.67 ms on reference NVIDIA GeForce RTX 2060 Super; 120 FPS is stretch goal).
- **Primary References:** [`Documentation/PROJECT_STATE.md`](file:///c:/UnrealProject/OneBossFight/Documentation/PROJECT_STATE.md) (architecture & rules), [`Documentation/TASKS.md`](file:///c:/UnrealProject/OneBossFight/Documentation/TASKS.md) (task queue), [`Documentation/DECISIONS.md`](file:///c:/UnrealProject/OneBossFight/Documentation/DECISIONS.md) (architectural log).

---

## 2. Environment Prerequisites

- **OS:** Windows 10/11 x64.
- **Compiler:** Microsoft Visual C++ (MSVC v143 toolset / Visual Studio 2022).
- **Python:** Python 3.11+ available on `PATH`.
- **PowerShell:** PowerShell 5.1+ or PowerShell 7 (run with `-NoProfile -ExecutionPolicy Bypass`).

---

## 3. Core Workflows

### 3.1 Compiling C++
> [!IMPORTANT]
> **Always close the Unreal Editor before compiling C++ code.** Live coding is disabled for determinism; building while the Editor holds file locks causes linking failures.

```powershell
# Compile Development Editor target via UnrealBuildTool
& "C:\Program Files\Epic Games\UE_5.5\Engine\Build\BatchFiles\Build.bat" OneBossFightEditor Win64 Development "c:\UnrealProject\OneBossFight\OneBossFight.uproject" -waitmutex
```

### 3.2 Running the Editor & PIE
> [!TIP]
> Launch the Unreal Editor with `-nosound` during development and automation to prevent audio subsystem contention:

```powershell
& "C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe" "c:\UnrealProject\OneBossFight\OneBossFight.uproject" -nosound
```

### 3.3 Running Automated Tests
The repository features two testing tiers:

#### Tier 1: Fast Offline Verification Suite (Python & PowerShell)
Run these checks before every task handoff (target execution time: < 8 seconds):
```powershell
# 1. Full offline unit test suite (360 tests)
python -m unittest discover -s Scripts/Tools -p "test_*.py"

# 2. Track B Witness Status Ledger verification (82 requirements, 470 verbatim citations)
python Docs/BossCombatReview/Execution/Antigravity/Ledger/test_witness_status_v3.py

# 3. Documentation line-count guard
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/Tools/CheckDocLineCounts.ps1

# 4. Markdown cross-link integrity checker
python Scripts/Tools/check_doc_links.py

# 5. Git diff formatting check
git diff --check
```

#### Tier 2: Unreal Engine Native Automation Suite (478 Tests)
Executed via Lead runner when the Editor is idle:
```powershell
# Full local gate execution (Editor native tests)
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/Gate.ps1

# Full Review Gate with A5 parity drivers
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/FullReviewGate.ps1 -BuildId BUILD-234
```

### 3.4 Packaging & Shipping Smoke
```powershell
# Packaging Development or Shipping build
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/Package.ps1 -Configuration Shipping

# Shipping binary smoke verification (dry-run by default)
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/ShippingSmoke.ps1 -DryRun
```

---

## 4. Golden Rules for Contributors

1. **Commit Authority:** Commit only upon explicit Lead Claude instruction in the mailbox. **Never `git push`** unless explicitly ordered by the owner.
2. **Asset Protection:** Never delete, overwrite, or recreate assets that other assets reference. Verify references with `Asset Registry` before touching content.
3. **Strict D5 Parity:** All presentation and Tier 2 hooks must default to null/empty in C++, preserving exact legacy D5 behavior out-of-the-box with zero allocations in Shipping.
4. **Append-Only Team Mailbox:** All communication between Claude, Codex, and Antigravity is routed through [`Documentation/TEAM_MAILBOX.md`](file:///c:/UnrealProject/OneBossFight/Documentation/TEAM_MAILBOX.md). Never edit previous messages. Always post messages using the official script:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/MailboxPost.ps1 -As A -To "Claude and Codex" -BodyFile <message.txt>
   ```
5. **Binding Evidence Rule (`[C-932]`):** Every performance metric, frame time, memory footprint, or test percentage cited in reports must reference a specific on-disk source (`file:line`, evidence directory, log line, or ledger row). Any uncited design expectation must be explicitly labeled `PROPOSAL`.
