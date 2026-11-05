# G1 — selected-route A7 benchmark expected sheet

Status: prep only; Claude owns package/build and live runs. No performance result is claimed.

## Capture method

Use the same capture contract as `Documentation/GATE4_RUNBOOK.md`: packaged 1920×1080 windowed fight on `/Game/OneBossFight/Levels/L_SevarogArena`, five-second discarded warmup, then sixty seconds of recorded frames. Repackage once before the matched set, keep configuration, cvars, build, driver, map and hardware fixed, and retain each raw `frames.csv` and `summary.json`. Summarize retained rows with `python -I Scripts/SummarizeBenchmark.py`.

Run one disposable warmup and three measured runs per arm. The legacy arm leaves `H019_ENCOUNTER_DEFINITION` unset. The selected arm sets it to the approved G044 object path for each child benchmark process. `Scripts/RunBenchmark.ps1` emits the `-H019EncounterDefinition=` argument only when the variable is nonempty; the runtime reads the command line only when `-RPGBenchmark` is present. That parsing and assignment are inside `#if !UE_BUILD_SHIPPING` in `RPGEncounterSelectionSubsystem.cpp` (Initialize, lines 58-67); the CVar fallback in ResolveSelectedDefinition is also non-Shipping-only (lines 127-129). The generic soft-path loader is shared, but the benchmark field remains empty in Shipping because its only assignment is compiled out. GATE4 uses a Development package, so this prepares its selected-route benchmark without opening a Shipping selector. With the variable unset, the argument list is unchanged. This benchmark hook does not decide the separate Blueprint setter policy in J049.

Example from the project root (substitute the actual staged executable folder if using a bench kit):

```powershell
Remove-Item Env:H019_ENCOUNTER_DEFINITION -ErrorAction SilentlyContinue
.\Scripts\RunBenchmark.ps1 -Label g1_legacy_warmup
.\Scripts\RunBenchmark.ps1 -Label g1_legacy_a
.\Scripts\RunBenchmark.ps1 -Label g1_legacy_b
.\Scripts\RunBenchmark.ps1 -Label g1_legacy_c

$env:H019_ENCOUNTER_DEFINITION = '/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter'
.\Scripts\RunBenchmark.ps1 -Label g1_selected_warmup
.\Scripts\RunBenchmark.ps1 -Label g1_selected_a
.\Scripts\RunBenchmark.ps1 -Label g1_selected_b
.\Scripts\RunBenchmark.ps1 -Label g1_selected_c
Remove-Item Env:H019_ENCOUNTER_DEFINITION -ErrorAction SilentlyContinue
```

## Acceptance and limitations

- Selected-arm average FPS is at least 60 and p99 frame time is at most 16.67 ms.
- Selected-arm p99 is no more than 0.5 ms slower than the matched legacy-arm p99.
- Each run's `gpu` must identify the expected NVIDIA adapter and `fight_started` must be true. A remote display or virtual adapter invalidates the run.
- This machine's RDP session may expose Microsoft Remote Display Adapter instead of the NVIDIA GPU. In that case Claude must hand the capture commands and this sheet to the owner to run in the active physical console session; no RDP result closes the hardware gate.
- This sheet is a run plan, not proof. Keep the legacy route available and follow the owner disposition for J049 separately.
