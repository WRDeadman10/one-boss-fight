# BT-91: Full-Mode Route Approval Receipt Diff & Source-Set Audit

**Author:** Antigravity (Implementer)
**Date:** 2026-11-17
**Scope:** Source-only preflight comparison of `Saved/C1619RouteBuild/Run_20261116_224348_b29aad4c/route_lead_approval.json` against current `run_sevarog_arena_route_acceptance.ps1` schema and the 9 bound runtime sources.
**Constraint:** Strict source-only preflight; 0 builds, 0 Unreal Editor launches, 0 PIE runs, 0 approval receipts created/altered, 0 asset/config mutations, 0 git commits/pushes.

---

## 1. Executive Summary

1. **Receipt Validity:**
   - All operational schema fields (`task`, `lead`, `approved`, `source_build_exit`, `suite_result`, `build_suite_run`, `dd27j_manifest_hash`, `locks_released`) remain 100% valid.
   - **8 of 9 source hashes match exactly.** All 7 compiled C++ source files and the Python acceptance driver match the approved BT-69 baseline byte-for-byte.
2. **Identified Stale Field:**
   - Exactly **1 source hash is stale**: `acceptance_runner_sha256`.
     * Receipt value: `94DD2FE8B0B98241EACE970C1A3115599996A871A827522EC4D49FAC1B7CE75E`
     * Current file on disk: `5DF121989AA43A6D07B42C9451EFE027155C0B12B0087F0C5890EEACB5E74A3E`
     * Root Cause: Updated in BT-72 to incorporate timeout bounding (`-FullTimeoutSeconds`), timestamp receipt validation, and graceful 30s `CloseMainWindow()` teardown.
3. **Compiled Source Stability:**
   - **Zero compiled C++ sources have changed.** The binaries produced by the BT-69 clean build/suite (`Run_20261116_224348_b29aad4c`) remain in complete alignment with the repository C++ source files.
4. **Minimum Safe Next Step:**
   - **Fresh Lead Approval Receipt Only (No Rebuild/Suite Needed).**
   - Because no compiled sources changed, a clean compilation / test suite re-execution is unnecessary. Codex (Lead) can safely issue an updated Lead Approval Receipt binding `acceptance_runner_sha256 = "5DF121989AA43A6D07B42C9451EFE027155C0B12B0087F0C5890EEACB5E74A3E"` while retaining the validated build/suite reference `Run_20261116_224348_b29aad4c`.

---

## 2. Detailed Field-by-Field Hash Comparison

The table below contrasts each field in `Saved/C1619RouteBuild/Run_20261116_224348_b29aad4c/route_lead_approval.json` with current disk state:

| Receipt Key | Bound Path | Approved Hash (BT-69 Receipt) | Current Disk Hash (SHA256) | Match Status |
| :--- | :--- | :--- | :--- | :--- |
| `subsystem_cpp_sha256` | `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp` | `60097589BA1FAF3C12827ECDF6AC0FD32651EA3AA292EF25C17AB1878D7FB838` | `60097589BA1FAF3C12827ECDF6AC0FD32651EA3AA292EF25C17AB1878D7FB838` | **MATCH (VALID)** |
| `subsystem_h_sha256` | `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.h` | `DA259E1A75E078350E06CFDFC1FE1AEDCD2F5872B62D00DA557975A98F6D82B6` | `DA259E1A75E078350E06CFDFC1FE1AEDCD2F5872B62D00DA557975A98F6D82B6` | **MATCH (VALID)** |
| `boss_cpp_sha256` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` | `168DC2D1EFF48F90414B120FA5E5512633126023CC4863D618ED39CB291A2213` | `168DC2D1EFF48F90414B120FA5E5512633126023CC4863D618ED39CB291A2213` | **MATCH (VALID)** |
| `boss_h_sha256` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.h` | `6F8D7D4F400EEF6E000C791C1B77CE5D5B92FF689B8D814B3035B060A3FC37ED` | `6F8D7D4F400EEF6E000C791C1B77CE5D5B92FF689B8D814B3035B060A3FC37ED` | **MATCH (VALID)** |
| `blueprint_call_h_sha256` | `Source/OneBossFight/Pack/RPGBlueprintCall.h` | `49B414970CEFD4ADDACE2C6D48DE2E4B63CA14CBD235EFA83565A25B4DB8328A` | `49B414970CEFD4ADDACE2C6D48DE2E4B63CA14CBD235EFA83565A25B4DB8328A` | **MATCH (VALID)** |
| `framework_profile_cpp_sha256` | `Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp` | `0CF583E9BB0ACEADEFF5D24B645F4DF1077911A891BF6F1DE6D8FEECBC406264` | `0CF583E9BB0ACEADEFF5D24B645F4DF1077911A891BF6F1DE6D8FEECBC406264` | **MATCH (VALID)** |
| `framework_runtime_tests_cpp_sha256` | `Source/OneBossFight/Tests/RPGFrameworkRuntimeTests.cpp` | `F0611B71CAFC2B32647C221316B2DB07A05DEDC45675B012D87246AA71F201F7` | `F0611B71CAFC2B32647C221316B2DB07A05DEDC45675B012D87246AA71F201F7` | **MATCH (VALID)** |
| `acceptance_runner_sha256` | `Scripts/Editor/run_sevarog_arena_route_acceptance.ps1` | `94DD2FE8B0B98241EACE970C1A3115599996A871A827522EC4D49FAC1B7CE75E` | `5DF121989AA43A6D07B42C9451EFE027155C0B12B0087F0C5890EEACB5E74A3E` | **MISMATCH (STALE)** |
| `acceptance_driver_sha256` | `Scripts/Editor/pie_sevarog_arena_route_acceptance.py` | `6759E8296D56D0BAC1FFF9B97BAC7ED82FC8099C801F52A2EF52FDF9D55C50F6` | `6759E8296D56D0BAC1FFF9B97BAC7ED82FC8099C801F52A2EF52FDF9D55C50F6` | **MATCH (VALID)** |

---

## 3. Runner Preflight Enforcement Behavior

In `Scripts/Editor/run_sevarog_arena_route_acceptance.ps1`:
- **Preflight Check (Lines 100-110):**
  ```powershell
  if ($approval.subsystem_cpp_sha256 -cne $initialHashes.subsystem_cpp -or
      $approval.subsystem_h_sha256 -cne $initialHashes.subsystem_h -or
      $approval.boss_cpp_sha256 -cne $initialHashes.boss_cpp -or
      $approval.boss_h_sha256 -cne $initialHashes.boss_h -or
      $approval.blueprint_call_h_sha256 -cne $initialHashes.blueprint_call_h -or
      $approval.framework_profile_cpp_sha256 -cne $initialHashes.framework_profile_cpp -or
      $approval.framework_runtime_tests_cpp_sha256 -cne $initialHashes.framework_runtime_tests_cpp -or
      $approval.acceptance_runner_sha256 -cne $initialHashes.acceptance_runner -or
      $approval.acceptance_driver_sha256 -cne $initialHashes.acceptance_driver) {
      throw 'ABORT: approved subsystem and boss character source hashes do not match the current files'
  }
  ```
- **Consequence:** Because `approval.acceptance_runner_sha256` (`94DD2FE8...`) does not equal `initialHashes.acceptance_runner` (`5DF12198...`), line 107 triggers immediate fail-closed preflight abort before any locks are acquired, config is modified, or Editor is launched.

---

## 4. Minimum Safe Next Step Recommendation

1. **Rebuild / Suite Need:** **NONE.**
   All 7 C++ source files that participate in the engine binary are completely unaltered since the passing build and test suite run `Run_20261116_224348_b29aad4c` (574/574 tests passed). Rebuilding would introduce unnecessary churn without any binary differences.
2. **Fresh Lead Approval Receipt:** **REQUIRED.**
   Codex (Lead) should issue a fresh Lead Approval Receipt with the identical payload as BT-69, updating only:
   ```json
   "acceptance_runner_sha256": "5DF121989AA43A6D07B42C9451EFE027155C0B12B0087F0C5890EEACB5E74A3E"
   ```
3. **Execution Readiness:**
   Once the updated approval receipt is emitted, `run_sevarog_arena_route_acceptance.ps1` will pass preflight without friction, clearing the path for the Owner-operated BT-71 Full-mode playtest.
