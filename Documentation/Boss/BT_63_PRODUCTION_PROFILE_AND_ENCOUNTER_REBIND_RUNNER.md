# BT-63: Production Framework Profile Asset Authoring and Encounter Rebind Runner

## Executive Summary
This document specifies the source-level runner, safety gates, backup/rollback mechanisms, and contract verification for **BT-63** (board task `BT-62`): authoring `DA_Boss_Sevarog_FrameworkProfile_Production` and rebinding `DA_Sevarog_Framework_Encounter` under C-1155 exclusive lock.

Following Tech Lead review **[X-2545]** and build gate completion (`Saved/C1619RouteBuild/Run_20261116_180407_2f383983`, 574/574 tests PASS, exit 0), this revision incorporates the strict C-1155 lock acquisition ordering and anti-drift verification:
1. **Lock Acquisition Preceding Backups & Post-Lock Recheck**:
   - Dual C-1155 locks (`ENGINE_LOCK.json` and `Docs/BossCombatReview/Execution/ENGINE_LOCK.json`) are acquired **before** any workspace directory creation, backup copy, or asset interaction.
   - Pre-lock baseline hashes of all 5 bound sources are captured.
   - Immediately post-lock, no Editor liveness is verified and all 5 hashes are recomputed and asserted equal to pre-lock baselines, eliminating any drift between preflight and the protected execution window.
   - BT-64 build gate and lead approval signature are revalidated under lock.
   - Backups (`DA_Sevarog_Framework_Encounter.uasset`, `DA_Boss_Sevarog_FrameworkProfile_Production.uasset`) and initial hashes are captured strictly under the active lock.
2. **Full BT-64 Gate Binding**:
   - Asserts pinned `dd27j_manifest_hash` (`cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec`) across both `status.json` and `route_lead_approval.json`.
   - Binds `acceptance_runner_sha256` and `acceptance_driver_sha256` to current repository files (`run_sevarog_arena_route_acceptance.ps1` and `pie_sevarog_arena_route_acceptance.py`).
   - Asserts `route_lead_approval.build_suite_run` resolves to the verified run directory.
3. **Lock Retention on Unreal Exit Failure**:
   - In `finally`, retains exclusive C-1155 locks if any `UnrealEditor` or `UnrealEditor-Cmd` process remains active after timeout or failed termination.
   - Reports exact held tokens and cleanup state (`locks_retained`).
   - Prevents missing `$run` directory from masking preflight refusals.
4. **Build Gate Bypass Restriction & DryRun Protection**:
   - Constrains `-SkipBuildGate` strictly to `-Mode DryRun`.
   - Enforces fail-closed `if dry_run: write = False` in authoring driver `main()` and `__main__`.
5. **Rollback Hash Verification**:
   - Asserts exact SHA256 equality when restoring a pre-existing profile asset, recording `profile_restored` and `profile_cleaned_up` evidence.

---

## 1. Architectural Components

### A. Locked Authoring Runner (`Scripts/Editor/run_author_production_framework_profile_locked.ps1`)
The PowerShell runner implements full C-1155 policy:
1. **TargetHealth Enforcement**: Fails closed unless `-TargetHealth` is exactly `800.0` HP.
2. **Preflight Checks**:
   - Asserts no `UnrealEditor` or `UnrealEditor-Cmd` processes are active.
   - Verifies existence of required files: Editor commandlet, project file, driver script, encounter asset, profile C++ implementation, framework tests, route runner, route driver, and `DefaultGame.ini`.
3. **Pre-Lock Hash Capture**:
   - Captures pre-lock baseline SHA256 hashes of driver, profile C++, test C++, route runner, and route driver.
4. **C-1155 Dual Exclusive Locks (Acquired First)**:
   - Acquires atomic locks at both `ENGINE_LOCK.json` and `Docs\BossCombatReview\Execution\ENGINE_LOCK.json`.
   - Records agent (`Antigravity`), party (`A`), task, command ID, PID, UTC timestamp, and unique owner token.
   - Verifies no Editor appeared during lock acquisition.
5. **Post-Lock Zero-Drift & Gate Revalidation**:
   - Recomputes all 5 source hashes under lock; aborts immediately if any file drifted.
   - Scans `Saved\C1619RouteBuild` runs for verified build output matching current source hashes (`framework_profile_cpp_sha256: 0CF583E9...`, `framework_runtime_tests_cpp_sha256: F0611B71...`, `acceptance_runner_sha256: 94DD2FE8...`, `acceptance_driver_sha256: 6896C2D3...`).
   - Verifies all fields: `result == 'PASS'`, `stage == 'done'`, `lead == 'Codex'`, `approved == true`, `source_build_exit == 0`, `suite_result == 'PASS'`, `suite_complete == true`, `failed == 0`, `passed >= 573`, `dd27j_manifest_hash == 'cd088e39...'`, `locks_released == 2`, `locks_kept == []`.
   - Validates `route_lead_approval.build_suite_run` resolves to the verified run directory.
   - Rejects `-SkipBuildGate` unless `-Mode DryRun` is selected.
6. **Protected Backups (Under Lock)**:
   - Creates isolated run folder: `Saved\BT63ProductionProfileAuthoring\Run_<timestamp>_<token>`.
   - Captures baseline hash and backs up `Content\OneBossFight\Data\Sevarog\DA_Sevarog_Framework_Encounter.uasset`. Validates backup SHA256.
   - Backs up pre-existing `DA_Boss_Sevarog_FrameworkProfile_Production.uasset` if present.
7. **Execution Stages**:
   - **Stage 1 (DryRun)**: Executes commandlet in dry-run mode. Verifies exit code 0, emits `dry_run_receipt.json`, and confirms encounter asset on disk was not modified.
   - **Stage 2 (Write)**: Executes commandlet with write and rebind flags. Verifies exit code 0, emits `write_receipt.json`, verifies production profile asset was created on disk with positive byte count, and verifies encounter asset hash changed.
   - **Stage 3 (Readback)**: Launches a fresh commandlet process to independently load both assets from disk. Verifies exact property readback, C++ validation bridge result `PASS`, and deterministic encounter manifest hash.
8. **Rollback & Lock Retention**:
   - On any failure or process timeout (4 minutes per stage), terminates launched editor processes.
   - Restores `DA_Sevarog_Framework_Encounter.uasset` from backup and verifies SHA256 restoration (`encounter_restored`).
   - If profile asset pre-existed, restores from backup and verifies restored SHA256 matches `initialProfileHash` (`profile_restored`).
   - If profile asset was newly created, removes it and verifies deletion (`profile_cleaned_up`).
   - In `finally` block, retains locks if any Unreal process remains active (`locks_retained`), otherwise cleanly removes owned atomic locks and emits `status.json`. Preflight failures before run creation do not mask errors.

---

## 2. Encounter Rebinding Contract (`author_production_framework_profile.py`)

The authoring driver incorporates canonical encounter payload generation, deterministic hashing, and readback assertions:

### A. Canonical Encounter Selection Payload
```json
{
  "schema": 1,
  "boss_slot": "Boss",
  "player_slot": "Player",
  "initial_boss_phase": "Phase_1",
  "boss_definition": "/Game/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_Draft",
  "player_definition": "/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Player_Hero_Draft_V3",
  "use_framework_boss": true,
  "framework_boss_profile": "/Game/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_FrameworkProfile_Production"
}
```

### B. Deterministic Encounter Manifest Hash
- Canonical JSON UTF-8 serialization with sorted keys and no whitespace separators.
- **Encounter Manifest SHA256**: `62ecc592e0c2ad57ec0b5d70afd56ba7ea1dc7f9d0fd1dc7a3fc1b625ac6d305`.

### C. Fail-Closed Dry-Run Protection
- `if dry_run: write = False` strictly enforced in driver `main()`.
- `is_write = (...) and not is_dry_run` enforced in `__main__`.
- Guarantees zero asset writes or property mutations under dry-run mode.

### D. Reflected Float32 Tolerance Matching (Consistent with C-1623)
- Uses `approved_float_matches(actual, expected, tol=1e-4)` across reflected Unreal float32 properties (`blend_in_seconds`, `blend_out_seconds`, card cooldowns/weights, transform vectors/rotators, combo edge ranges).
- Fails closed on non-finite, NaN, inf, or out-of-tolerance values (`abs(actual - expected) <= 1e-4`).
- Preserves discrete identifiers, names, and boolean properties under exact equality.

---

## 3. Static Contract Coverage

- `Scripts/Tools/test_author_production_framework_profile_contract.py`:
  - Verified mandatory TargetHealth 800.0 enforcement.
  - Verified exact O1 stats (1500 HP, 100 Posture, 60% Phase 2) and approved posture values (`PlayerPostureHitAmount = 60.0`, `StaggerSeconds = 2.5`).
  - Verified 7 production card specs, exact transform component checks, and combo graph readback.
  - Verified `approved_float_matches` finite tolerance comparator (<= 1e-4, rejecting non-finite, NaN, and out-of-tolerance).
  - Verified encounter payload generation, deterministic SHA256 `62ecc592...`, and encounter readback assertions.
  - Verified deferred receipt emission strictly after successful operation stages.
- `Scripts/Tools/test_author_production_profile_runner_contract.py`:
  - Verified runner parameters, C-1155 dual lock acquisition, preflight process checks.
  - Verified dual lock acquisition precedes backups and post-lock source drift check.
  - Verified build gate schema binding (`source_build_exit`, `suite_result`, `suite_complete`, `dd27j_manifest_hash`, `acceptance_runner_sha256`, `acceptance_driver_sha256`, `locks_released = 2`, `build_suite_run`).
  - Verified `-SkipBuildGate` restriction to `-Mode DryRun`.
  - Verified backup and hash-verified rollback for both encounter and profile assets.
  - Verified lock retention on exit failure, exit shutdown wait, and preflight mask prevention.
  - Verified three-stage execution and receipt schema (including 60.0 hit amount and 2.5s stagger assertions).
  - Verified fail-closed log scanning rejecting Python errors even if editor exit code is 0.

---

## 4. Verified File Hashes
- `Scripts/Editor/run_author_production_framework_profile_locked.ps1`: `13357A67D09199DF8AE4531D31A892FCA3936CFC3DE5FDE997719C4A9BB2184A`
- `Scripts/Editor/author_production_framework_profile.py`: `70B8B9B5C63AC7B6B17B2C899CA89095CB749EF358B00E0ED8913DC8AEDB2F9F`
- `Scripts/Tools/test_author_production_framework_profile_contract.py`: `1769CD886BD08FF5123DF054F77BA257C01E2E7E34EFFCEE21499C301D8D54AF`
- `Scripts/Tools/test_author_production_profile_runner_contract.py`: `35F25ABFD1A87872157AB28B546C2FDB2D5BA318D695E9FFE953764E4F9D5954`
- `Documentation/Boss/BT_63_PRODUCTION_PROFILE_AND_ENCOUNTER_REBIND_RUNNER.md`: self-referential markdown documentation
