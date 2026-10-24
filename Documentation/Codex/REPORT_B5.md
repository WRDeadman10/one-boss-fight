# B5 - Shipping benchmark readiness audit

## Blocking finding

### B5-1 — High: fight mode cannot resolve the arena boss

- `Source/OneBossFight/Benchmark/RPGBenchmarkRunner.cpp:178` accepts only class names beginning `BP_SevarogBossPack`.
- The shipped arena contains `BP_ExampleGreatSwordBoss_C`: its serialized actor entry is visible in `Content/OneBossFight/Levels/L_SevarogArena.umap`, and project runtime logs identify the same actor (`Saved/Logs/OneBossFight-backup-2026.10.23-20.42.40.log:32796`, `BP_ExampleGreatSwordBoss_C_3: awake, the fight begins`).
- When lookup fails, `TickFight` returns at `RPGBenchmarkRunner.cpp:185-190`; it never walks the player, calls `Ability.EnterCombat`, drives melee/dodge, or pushes phase two. The outer runner still records frames and writes a `fight_mode: true` summary.
- **Fix before benchmarking:** resolve the real arena boss class (for example, the current `BP_ExampleGreatSwordBoss` prefix, or preferably the attached `RPGBossEncounter` component) and add a completed-run assertion/log field that says whether `bFightStarted` became true. `bFightStarted` is currently assigned at line 192 but never consumed.

## Ready by static inspection

- Packaged command-line startup is compiled gameplay code: `FParse::Param("RPGBenchmark")` at `RPGBenchmarkRunner.cpp:45`, fight switch at `:68`, label at `:76`, quit at `:286`.
- The actor is placed in the arena: `Content/OneBossFight/Levels/L_SevarogArena.umap` contains `RPGBenchmarkRunner_0`.
- The runner owns output generation: `FPaths::ProjectSavedDir()/Benchmark/<label>_<timestamp>` at `RPGBenchmarkRunner.cpp:294-296`, with `frames.csv` at `:307` and `summary.json` at `:369`. In the staged build this is the script path `Saved/StagedBuilds/Windows/OneBossFight/Saved/Benchmark`, matching `Scripts/RunBenchmark.ps1:43-48`.
- `summary.json` includes GPU brand, driver, CPU, RAM, OS, resolution, build configuration, FPS/percentiles, per-thread p99 fields, and target verdict at `RPGBenchmarkRunner.cpp:323-364`. `gpu` comes from `FPlatformMisc::GetPrimaryGPUBrand()` at `:310`, not an editor-only API.
- `Scripts/SummarizeBenchmark.py:39-76` reads those fields and exits nonzero for `Remote Display` or `Virtual` GPU names.
- The runner disables/restores `t.MaxFPS`, `r.VSync`, smooth frame rate, and fixed frame rate in ordinary runtime code (`RPGBenchmarkRunner.cpp:374-423`); there is no `WITH_EDITOR`/`UE_BUILD_SHIPPING` guard around benchmark operation.
- The pack bot calls direct reflection paths, not Shipping-neutral test hooks: `RPGPack::TryActivateByTag` for enter-combat/dodge/melee at `:245`, `:250`, `:255`; direct `ReadAttribute`/`WriteAttribute` at `:200-223`. A direct runner scan found no `ForTest`, `Debug`, `RPGCombatDebug`, `RPGTraceAudit`, or `RPGInputTestUtils` call.
- Q16/Q17 guards therefore do not statically affect the runner path. Guarded test/debug utilities still exist in their own source, but are not benchmark dependencies.

## Doubts to verify in the first real Shipping run

1. **GPU name validity:** `GetPrimaryGPUBrand()` is available in the Shipping source path, but only the run can prove it reports the physical NVIDIA card rather than a remote adapter. Check `summary.json` before retaining each run, as `GATE4_RUNBOOK.md:7-10` requires.
2. **Shipping log visibility:** benchmark progress uses `UE_LOG` (`RPGBenchmarkRunner.cpp:106`, `:280-282`, `:371`). Results do not depend on logs because files are written directly, but runbook smoke text correctly notes Shipping logging may be compiled out (`GATE4_RUNBOOK.md:185-196`). Inspect `summary.json`, not logs, for completion.
3. **Fight wake after the resolver fix:** the runner has no explicit encounter `Wake()` call. It relies on player movement to 190-420 cm (`RPGBenchmarkRunner.cpp:228-255`) and the encounter proximity gate. Confirm `fight_started`/boss-awake behaviour in the first run.
4. **No existing staged summaries were found during this read-only audit**, so the output schema and physical packaged path are code-derived, not observed in a completed Shipping benchmark.

## Check-first order for Claude

1. Fix B5-1 and build/package.
2. Run one console-session Shipping warm-up with `-RPGBenchmarkFight`; verify a `summary.json` exists and names the NVIDIA GPU.
3. Confirm the summary/log says the fight began and phase two was forced; only then collect the runbook's three recorded 1080p runs.
4. Run `python -I Scripts/SummarizeBenchmark.py`; reject Remote Display/Virtual rows before comparing FPS.

No editor, build, package, benchmark, or game was run for this audit.
