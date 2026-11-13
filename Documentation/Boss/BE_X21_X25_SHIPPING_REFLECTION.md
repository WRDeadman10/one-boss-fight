# Queue BE Batch 5 — Shipping reflection boundary

Date: 2026-11-10  
Status: source/contract/checklist READY; no Shipping target was built, so reflection absence is not claimed as runtime-proven.

## Reflection policy

| Class | Reflected functions | Shipping policy |
|---|---|---|
| `URPGDamageResolver` | `ResolveForTest`, `NoteOverlapForTest` | UFUNCTION metadata is compiled only with `WITH_EDITORONLY_DATA`; ordinary C++ declarations/definitions remain available so Shipping compiles, while existing bodies fail closed/no-op under `UE_BUILD_SHIPPING`. Production audit readers, `ClearAudit`, and `BuildSummaryLine` stay reflected for runtime diagnostics. |
| `ARPGFrameworkBossCharacter` | `InitializeWithProfileForTest`, `StartCardForTest`, `StartSelectedCardForTest`, `GetOutcomeForTest`, `GetNavigationResultForTest`, `StartComboForTest`, `SpawnFrameworkBossForTest` | All seven test-bridge UFUNCTION declarations are `WITH_EDITORONLY_DATA` guarded. Their C++ definitions retain Shipping refusal/unavailable branches. Production selected-encounter initialization is unchanged. |
| `URPGDodgeTiming` | `IsGuardCounterArmed`, `DebugArmGuardCounter`, `DescribeGuardState` | Development/synthetic guard-counter nodes are editor-data-only reflected. Read-only input/dodge counters and stage diagnostics remain reflected because they support existing runtime diagnostics and capture receipts. |
| `URPGIFrameMonitor` | `DebugForceOwned` | Synthetic stale-watchdog hook is editor-data-only reflected. Read-only record/source/lifecycle counters remain reflected for diagnostics. |
| `URPGPlayerParry` | No test-only UFUNCTION found | `Press`, `IsWindowOpen`, and count/visual accessors remain reflected as production input or runtime diagnostic APIs. |

## Offline contract and verification

`Scripts/Tools/test_be_x21_x25_shipping_reflection_contract.py` asserts guarded declaration parity for every listed test hook, checks the retained C++ definitions, and pins selected production/debug APIs as intentionally reflected. It is source-level evidence only: UnrealHeaderTool's Shipping preprocessing and the cooked Shipping class function tables still need Lead verification.

## Lead Shipping/UHT proof checklist

For one named build, record:

1. Git HEAD/source hash, Unreal version, `.uproject`, target name, `Shipping` configuration, platform and build command/exit code.
2. UHT log path and completion; exact warnings/errors for `RPGDamageResolver`, `RPGFrameworkBossCharacter`, `RPGDodgeTiming`, `RPGIFrameMonitor`, and `RPGPlayerParry`.
3. A runtime or cooked-package reflection dump for those five classes showing each test hook above absent (`FindFunctionByName` returns null / not in `UClass` function list) and the listed production calls/readers present.
4. If Blueprint assets reference any hidden hook, report their asset paths and compile/load result; do not silently rewrite assets in this gate.
5. Packaged or Shipping smoke outcome, log path, and whether any test node/function was callable. Development UHT/build output alone does not satisfy this gate.

## Validation

- `test_be_x21_x25_shipping_reflection_contract.py`: 4/4 passed.
- `test_check_shipping_guards.py`: 4/4 passed.
- C-1155 Development build exit 0; DD27j-pinned suite 509/509 started / passed, 0 failed, complete; no assets; both locks released.
- Receipt: `Docs/BossCombatReview/Execution/Codex/BE_X21_X25_SHIPPING_REFLECTION/Run_20261110_181101/`.

No local Shipping build, package, reflection dump, or asset mutation was performed in this batch.
