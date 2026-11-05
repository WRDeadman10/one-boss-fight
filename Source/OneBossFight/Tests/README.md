# Tests module

The C++ tests are Unreal automation registrations, usually named under `OneBossFight.*`. The test implementation is compiled under `WITH_DEV_AUTOMATION_TESTS`; reusable rule tests live beside the feature-specific test files in this folder.

## Inventory and naming

- Keep test names descriptive and stable; the macro registration name is the filter that Unreal automation runs.
- Test pure rules with table/boundary cases; stateful actor/component behavior uses automation fixtures and explicit `ForTest` APIs where appropriate.
- As of 2026-11-03, this folder contains 121 test `.cpp` files. `py Scripts/Tools/list_automation_tests.py --root .` prints every registration and source line; the current scan finds 332 unique registrations.
- `RPGAutomationTests.cpp` aggregates broad legacy/feature coverage; focused files such as `RPGBossMoveSelectorTests.cpp` and `RPGParryTests.cpp` keep isolated behavior checks near their domain.
- For world, UObject, global CVar, and async fixture ownership examples, see [`Documentation/Boss/TEST_FIXTURE_LIFECYCLE_S153.md`](../../../Documentation/Boss/TEST_FIXTURE_LIFECYCLE_S153.md).

## Running

The project build/test wrapper is `powershell -ExecutionPolicy Bypass -File Scripts\Rebuild.ps1 -Tests`; it closes Unreal before building and runs the automation suite. Only the current editor owner should launch a build/test cycle. A green source compile or unrun test addition is not a passing test: record the observed `automation tests: N finished, M passed` result and evidence in `Documentation/TEST_PLAN.md`. `Scripts/RunDrivers.ps1` is a separate PIE driver gate, not the C++ suite.
