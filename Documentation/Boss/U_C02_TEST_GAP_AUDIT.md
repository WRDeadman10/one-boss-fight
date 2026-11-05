# U-C02 source-to-automation test gap audit

Inventory: 97 production `.cpp` translation units; 88 have at least one native automation source that names a primary same-header type. 0 declared primary-type candidates have no matching automation reference; 9 units lack a same-name declared type and require the helper/adapter caveat below.

This is a conservative static gap-finding heuristic, not proof of runtime coverage. It recognizes class/struct identifiers from the same-named header and searches `Source/OneBossFight/Tests/*.cpp` for those identifiers. It does not infer coverage from filename similarity, tests of collaborators, or indirect behavior. Risk is a review priority based on code location and is not a defect finding.

## Baseline gaps and test additions

The pre-test baseline found six primary class/type gaps. Manual review of the nine no-primary-header units found two additional callable surfaces without focused native coverage (`RPGPerf::FireRadiusScale` and `RPGBossInterrupt::CancelOffence`). U-C03/U-C04 added test-only coverage for all eight identified surfaces. The module entry point is not treated as a behavioral test target; helper/adapter units with existing dedicated adapter tests remain mapped in the manual section below.

| Baseline risk | Implementation surface | Added automation |
|---|---|---|
| High | `URPGPlayerParry` | `OneBossFight.Player.Parry.ComponentContract` |
| High | `URPGRiposteInput` | `OneBossFight.Player.RiposteInput.Defaults` |
| High | `RPGBossInterrupt::CancelOffence` | `OneBossFight.Combat.InterruptNoComponents` |
| Medium | `URPGFlaskHud` | `OneBossFight.UI.FlaskHud.InitialState` |
| Medium | `URPGCameraProbe` | `OneBossFight.Camera.Probe.WorldSupport` |
| Medium | `URPGHideBones` | `OneBossFight.Pack.HideBones.Defaults` |
| Low | `ARPGBenchmarkRunner` | `OneBossFight.Benchmark.RunnerNoWorld` |
| Medium | `RPGPerf::FireRadiusScale` | `OneBossFight.Performance.FireRadiusScaleClamp` |

## Candidate gaps (ranked by risk, then source path)

| Rank | Risk | Implementation file | Primary type(s) | Direct automation references |
|---:|---|---|---|---|

## Units requiring manual type mapping

These implementation files have no same-named header type detectable by the heuristic. They may implement free functions, adapters, or types declared in another header; the candidate-gap count above excludes them rather than claiming they are untested.

| Implementation file | Primary header |
|---|---|
| `Source/OneBossFight/Arena/RPGPerfSwitches.cpp` | Arena/RPGPerfSwitches.h |
| `Source/OneBossFight/OneBossFight.cpp` | OneBossFight.h |
| `Source/OneBossFight/Player/RPGBossAttackTrackerAdapters.cpp` | Player/RPGBossAttackTrackerAdapters.h |
| `Source/OneBossFight/Player/RPGBossCloseClipSwapAdapters.cpp` | Player/RPGBossCloseClipSwapAdapters.h |
| `Source/OneBossFight/Player/RPGBossDeathAdapters.cpp` | Player/RPGBossDeathAdapters.h |
| `Source/OneBossFight/Player/RPGBossInterrupt.cpp` | Player/RPGBossInterrupt.h |
| `Source/OneBossFight/Player/RPGBossLookAdapters.cpp` | Player/RPGBossLookAdapters.h |
| `Source/OneBossFight/Player/RPGBossLowSweepAdapters.cpp` | Player/RPGBossLowSweepAdapters.h |
| `Source/OneBossFight/Player/RPGBossShockwaveAdapters.cpp` | Player/RPGBossShockwaveAdapters.h |

Manual disposition: `RPGPerfSwitches.cpp` exposes free functions rather than a same-name class; U-C04 adds a CVar clamp/Shipping accessor automation. `RPGBossInterrupt.cpp` similarly exposes `CancelOffence`; U-C04 adds empty-component, repeat-call, and null-input coverage. `OneBossFight.cpp` is the Unreal module entry point without an independently callable gameplay surface. The adapter helper units are exercised through their focused `*AdaptersTests.cpp` fixtures; this heuristic lists them for human confirmation rather than counting their shared target types as direct proof.

## Reproduction

`python -I Scripts/Tools/audit_source_test_coverage.py`
