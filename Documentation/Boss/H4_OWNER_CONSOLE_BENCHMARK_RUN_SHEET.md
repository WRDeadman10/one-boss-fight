# H4 — owner console selected-route benchmark

**Run only in the active physical console session** on the RTX 2060 Super.
RDP/virtual GPU captures do not close the target-hardware gate. Use the
Development package because the benchmark selector is deliberately
non-Shipping. Keep the staged project, cvars, map, resolution and hardware fixed.

From the project root, package once:

```powershell
.\Scripts\Package.ps1 -Configuration Development
```

Run one warm-up and three measured captures per arm, retaining each reported
directory with its `frames.csv` and `summary.json`:

```powershell
Remove-Item Env:H019_ENCOUNTER_DEFINITION -ErrorAction SilentlyContinue
.\Scripts\RunBenchmark.ps1 -Label h4_legacy_warmup
.\Scripts\RunBenchmark.ps1 -Label h4_legacy_a
.\Scripts\RunBenchmark.ps1 -Label h4_legacy_b
.\Scripts\RunBenchmark.ps1 -Label h4_legacy_c

$env:H019_ENCOUNTER_DEFINITION = '/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter'
.\Scripts\RunBenchmark.ps1 -Label h4_selected_warmup
.\Scripts\RunBenchmark.ps1 -Label h4_selected_a
.\Scripts\RunBenchmark.ps1 -Label h4_selected_b
.\Scripts\RunBenchmark.ps1 -Label h4_selected_c
Remove-Item Env:H019_ENCOUNTER_DEFINITION -ErrorAction SilentlyContinue
python -I .\Scripts\SummarizeBenchmark.py
```

Check every run's `gpu` identifies the RTX 2060 Super and `fight_started` is
true. The selected arm must average at least 60 FPS, have p99 at most 16.67 ms,
and be no more than 0.5 ms slower at p99 than the matched legacy arm. A failed
or invalid run does not count; preserve it and report the error rather than
silently replacing it.

Send Claude the build/config identity, console/GPU identity, all eight labels'
result directories, every `frames.csv` and `summary.json`, the summarizer table,
and any invalid/failed-run details. Do not claim the target gate from an RDP or
virtual adapter capture.
