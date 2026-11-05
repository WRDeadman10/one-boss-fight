# Automation determinism audit (Queue D83)

Static source scan of test random, clock, and ordering inputs. No test/build/Editor run.

## Random inputs

Every `FRandomStream` construction found in `Source/OneBossFight/Tests` uses a literal seed:

| Test source | Seed |
|---|---:|
| `RPGBleedRulesPropertyTests.cpp` | `0xB1EED` |
| `RPGAutomationTests.cpp` | `7` |
| `RPGBossAimHysteresisTests.cpp` | `0x97A11` |
| `RPGBossApproachTests.cpp` | `0x94A11` |
| `RPGBossComboPropertyTests.cpp` | `0x51A7` |
| `RPGBossMoveCardTests.cpp` | `0x92A11` |
| `RPGBossMoveSelectorTests.cpp` | `0x86A11` |
| `RPGBossMoveModelTests.cpp` | `0x87A11` |
| `RPGBossStrafeTests.cpp` | `0x90A11` |
| `RPGBossYawProbeTests.cpp` | `0x96A11` |
| `RPGFrameworkRuntimeTests.cpp` | `0x91A11` |
| `RPGParryTests.cpp` | `0x89A11` |

`FGuid::NewGuid()` appears in world/registry/preflight fixtures. Those tests use generated IDs as unique opaque identities and assert separation, invalidation, or mismatched identity behavior; they do not assert a particular GUID value. The identity values are intentionally nondeterministic, while the expected test outcomes are invariant to them.

## Time and ordering

The targeted scan found no use of `FPlatformTime`, wall-clock date/time, process sleep, `FMath::Rand`, timers, or tickers in test sources. Pure-model time cases use explicit numeric clocks. World-driven fixtures manually tick or synchronize with futures where asynchronous work is involved; ThreadPool scheduling can vary, but the inspected tests synchronize results with future completion and assert outcome/state invariants rather than a specific worker order. This source review does not prove all indirect helpers or engine scheduling are deterministic.

## Disposition

No unseeded random-number generator or wall-clock dependency was found by the source searches. The fixed-seed fuzz/property cases are reproducible from their test code. Generated GUIDs remain nondeterministic test inputs but are not golden outputs. No code changes were made.
