# BT-61: C-1619 route build runner extension

Date: 2026-11-16
Status: source implementation complete; awaiting lead review (`BT-61` -> `review`). Zero tests, build, Editor, PIE, or asset operations run per scope.

## Context

Following acceptance of BT-59 source implementation (`[X-2540]`, `[X-2541]`), which added the native `Production` profile identity branch to `Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp` and the `FFrameworkProductionProfile` automation test to `Source/OneBossFight/Tests/RPGFrameworkRuntimeTests.cpp`, Codex identified that the existing C-1155 build runner (`run_c1619_route_build_locked.ps1`) did not hash-bind these two new sources.

## Changes

1. **`Scripts/Editor/run_c1619_route_build_locked.ps1`**:
   - Added paths:
     - `$frameworkProfileCpp = Join-Path $root 'Source\OneBossFight\Player\RPGBossFrameworkProfile.cpp'`
     - `$frameworkRuntimeTestsCpp = Join-Path $root 'Source\OneBossFight\Tests\RPGFrameworkRuntimeTests.cpp'`
   - Added to `Get-SourceHashes`: `framework_profile_cpp`, `framework_runtime_tests_cpp`.
   - Added to pre-lock file existence check.
   - Added to pre-lock lead approval preflight check (`$approval.framework_profile_cpp_sha256`, `$approval.framework_runtime_tests_cpp_sha256`).
   - Added to post-lock recheck before build execution.
   - Added to post-build / post-suite recheck before lock release.
   - Included both hashes in emitted `status.json` and `route_lead_approval.json` receipts.

2. **`Scripts/Editor/run_sevarog_arena_route_acceptance.ps1`**:
   - Added paths and runtime hash computation for both `$frameworkProfileCpp` and `$frameworkRuntimeTestsCpp`.
   - Added to pre-flight existence, pre-lock approval validation, post-lock recheck, and post-run Editor exit verification.

3. **`Scripts/Tools/test_c1619_route_build_runner_contract.py`**:
   - Expanded from 17 to 20 contract checks, asserting that both runners hash-bind `framework_profile_cpp_sha256` and `framework_runtime_tests_cpp_sha256` across pre-lock, post-lock, post-build/post-run, and emitted receipts.

## Boundaries Preserved

- Strictly source-only; 0 tests executed per explicit directive; 0 Unreal processes running; 0 engine locks held; 0 asset writes/rebinds; 0 commits or pushes.
- Prepares for BT-64 locked Development build and complete DD27j suite.
