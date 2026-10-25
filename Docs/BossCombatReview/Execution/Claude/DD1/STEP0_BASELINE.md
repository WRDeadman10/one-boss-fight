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
