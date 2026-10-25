# DD-1 step 0: baseline (CI-DD-1, Claude), 2026-10-25

Status: manifest generated; regression baseline RUNNING (detached full gate, started 16:34 local, about 100 minutes, result file `Saved/rundrivers_dd1_step0_baseline.txt`; its table is copied here when it ends). This is the pin that DD-1 steps 1 to 3 must keep behaviour-identical to. No source, config, asset or pack file was changed for it.

## What is pinned (`STEP0_MANIFEST.json`, generator `dd1_step0_manifest.py`, read-only)

- git HEAD `5500600d0310aac874928aa8aacc8338e6d5535d`, branch main; dirty list (20 entries, the owner's and my uncommitted work, never touched by agents' resets): map `L_SevarogArena.umap`, perf docs/scripts (`BENCHKIT_README.md`, `PERFORMANCE_LOG.md`, `KNOWN_ISSUES.md`, `RunBenchmark.ps1`, `RunPerfExperiments.ps1`, `MakeBenchKit.ps1`, `BenchKit_Collect.ps1`), driver scripts (`pie_close_attacks.py`, `pie_close_reach.py`, `pie_dormant_wake.py`, `RunDrivers.ps1`, new `wake_clip_off.py`), perf C++ (`RPGFireSource.cpp`, `RPGPerfSwitches.*`), `RPGBossDormantWake.cpp`; untracked `Docs/` and `Unreal_Boss_Combat_Engineering_Kit/`.
- 136 source files (`.cpp/.h/.cs`), 5 config files, 605 project content assets (`Content/OneBossFight`, `.uasset/.umap`, 275 MB), 330 PIE driver scripts, the editor module DLL (`UnrealEditor-OneBossFight.dll`, built 2026-10-25 00:57, sha in E-001), each with sha256. Combined digest of source + config + project assets: `6c2102992482aded3935f85054bbc85256a1dfd162dcb6a2c0abc57b05d16adc`.
- Test registry: 39 gate rows in `RunDrivers.ps1` (plus 3 balance rows `pie_build_fight_*`, not part of the gate) and 37 automation tests in 8 files (`RPGAutomationTests`, `RPGBossCloseClipSwapTests`, `RPGBossDormantWakeTests`, `RPGBuildTests`, `RPGCodexTests`, `RPGFlaskHudTests`, `RPGFlipbookEffectTests`, `RPGRemainsTests`).
- Pack assets are outside this manifest (git-ignored; `Content/AdvancedARPGCombat` is the owner's imported pack, 92 files differ on purpose per PROJECT_STATE); DD-1 does not edit any of them.

## Behaviours DD-1 must reproduce (measured in P0, not endorsed)

| Behaviour | Evidence | Rule for DD-1 |
|---|---|---|
| A2 slam stopped early (10 of 11 instances; first slam at 0.03 to 0.06 s in 5 of 6 fights), ability left active over 1.4 s | E-005 | reproduce; shadow comparison must show the same stops; a fix is a P2 change with its own approval |
| Mid01, sprint follow-up and retaliation run through the pack path, not through tracker stages | E-002, E-002-10 | reproduce; they enter the data model as pack-owned moves with their measured notify timings |
| A4 only starts from the test hook; its query is a planar arc (reach 380, inner 60, height 40, 90 to -90 degrees) unrelated to the visible blade | E-002, E-008 | reproduce |
| A5 released at the tracker's active window (montage 0.45 s, seen at 0.47) on the player's potion montage | E-007 | reproduce |
| Wake clip off in the driver harness (`rpg.WakeClip 0`), `rpg.CloseTelegraph` 0.4 default, legend off in drivers | E-001, E-004 | the harness switches stay as `RunDrivers.ps1` sets them; both configurations are recorded |
| Window must be restored; minimized editor = about 3 fps = invalid timing runs | E-004 | check before every run |

## Step 0 acceptance (checklist)

1. Manifest committed to the evidence tree: DONE (`STEP0_MANIFEST.json`, 216 KB).
2. Baseline gate table on the current binary: PENDING (running; any failing row is recorded as a known flake or a defect before step 1, never hidden; a row that fails here cannot be used as a parity witness).
3. Automation tests on the current binary: PENDING (needs the editor closed, so they run after the gate; last recorded 37 of 37 in C-84).
4. Codex review of this baseline and of the step 1 specification: PENDING.
Step 1 does not start before 2 to 4 are done.

## Supplement 1 (2026-10-25 19:20, after Codex D06 R5 and the first gate run)

- The manifest `STEP0_MANIFEST.json` is preserved unchanged as the pin; its generator (`dd1_step0_manifest.py`, sha256 recorded in the supplement manifest below) is never rerun over it. Supplements are new files: `STEP0_SUPPLEMENT1.json` (to be written when the clean run ends) will add: the hash of `RunDrivers.ps1` (Codex read CDEDAD68...9535 independently), its rows with K/T/Setup, the presets and wrappers (`run_in_editor.py`, `mcp_call.py`, the warm-up scripts), the actual invocation, effective cvars at the run start and end, window state, tick cadence, engine/plugin identity, result and log hashes, file-list additions/removals since the pin.
- First gate run (started 16:34, ended 18:05 local, result `Saved/rundrivers_dd1_step0_baseline_CONTAMINATED_run1.txt`): 35 of 39 rows passed; FAIL `pie_telegraph` (T0: default 0.4 read as 0.000), `pie_soak` (189/213, "reset start state" checks), `pie_player_death_reset` (21/25, boss "not staggered, no montage left" checks), `pie_damage_path` (15/17, A5 javelin trials 0/5). CLASSIFICATION: HARNESS CONTAMINATION BY MY OWN DIAGNOSTICS, not a product finding. Before the run I left two process-wide settings changed in the editor: `rpg.CloseTelegraph 0` (the A5 and A4 probe runs set it; `pie_telegraph` T0 expects the default 0.4) and the log verbosity `Log LogAnimMontage VeryVerbose` (set for the A2 montage-stop search; it grew the log to 310 MB and slowed every PIE, which breaks the timing-sensitive rows `pie_soak`, `pie_player_death_reset`, `pie_damage_path`). The 35 passing rows are not parity witnesses either, because they ran in that contaminated state. Lesson recorded: every probe that changes a console variable or a log verbosity must restore it in the same script, and a gate run starts only from a freshly started editor.
- Remediation: the editor was closed and restarted through `Scripts/Rebuild.ps1 -Tests` (automation tests on the current binary, result `Saved/rebuild_dd1_step0.txt`), then the full gate was started again from the fresh editor (`Saved/rundrivers_dd1_step0_baseline_clean.txt`, started about 19:05 local, about 95 minutes). Only the clean run counts as the step 0 baseline. The first run is retained, labelled contaminated, with its failing rows.
- Corrections to the behaviour table above (Codex D06B): A2: nine Windup stops, one Active stop (1.99 s, window 1.93 to 2.11), one Recovery replacement (2.80 s): mechanism and sampled outcomes are preserved, NOT a statistical 10 of 11 invariant; A4: "no natural route found in the inspected native/BT/style evidence" (not "only from a test hook"); the A4 geometry row is a one-run forced measurement with a bounds-axis tip estimate; A5: 0.45 s nominal, 0.47 s observed, after an INTENDED 0.40 s marker. DD-1 observes these symptoms through the shadow comparison and never reproduces them by implementing cancellation.
