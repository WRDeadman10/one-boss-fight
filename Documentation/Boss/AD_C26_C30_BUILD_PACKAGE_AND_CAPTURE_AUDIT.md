# Queue AD-C26–C30 — build identity, cook, smoke, and capture provenance

Date: 2026-11-07. Source/config/document audit only. No staged build was created or launched.

## AD-C26 — BUILD_INFO producer/consumer crosswalk

| Stage | Producer / consumer | Fields or checks | Limit |
|---|---|---|---|
| Package build | `Scripts/Package.ps1` runs UAT BuildCookRun, then writes `Saved/StagedBuilds/Windows/OneBossFight/Saved/BuildStamp.txt` as `OBF-{SHIPPING|DEVELOPMENT}-{UTC timestamp}-{8 hex}` and prints `[PACKAGE_BUILD_ID]`. | ID is generated after BuildCookRun; Shipping also receives the staged text file. | No source revision, executable hash, UFS manifest hash, UAT log hash, or package content digest is recorded here. |
| Bench kit | `Scripts/MakeBenchKit.ps1` reads the selected stage's `BuildStamp.txt`, hashes the staged inner executable, and emits `BUILD_INFO.txt`: Package build ID, configuration, executable SHA-256, executable time/size, and stage-included booleans. | Hash is computed over the copied inner game executable, not the launcher. If no stamp exists, it writes `UNSTAMPED`. | It does not emit source revision, engine version, cooked-manifest identity, or UAT/run-log linkage. It labels configuration from script flags, without verifying that the stamp prefix agrees. |
| Kit validator | `Scripts/Tools/check_bench_kit.py` requires the documented files/manifests, rejects empty required files and PDBs, checks ID syntax and a 64-character lowercase executable-hash shape. | It does not recompute the executable hash or compare the ID's configuration with `Package configuration`. It is a shape/presence check. |
| Benchmark/run intake | `PackagedRunLog.psm1` uses staged `BuildStamp.txt` to group log paths; Round 6 intake pins one expected Development ID. The normalized G044 manifest separately requires build ID, configuration, roots, packages, and source-manifest SHA-256. | These consumers check the run/manifest's declared values. | No generic checker binds BUILD_INFO, staged executable hash, UFS manifest hash, UAT log, and run receipt together. |

The retained `B_C947_R6KIT/BUILD_INFO.txt` demonstrates those five fields in a real transfer-kit record. This is a schema example, not evidence of a current staged build. Earlier R6 kit audits found that its BUILD_INFO was not identity-bound to UFS manifests/UAT or a source revision; see `Y016_Y020_A7_COOK_MANIFEST_RECONCILIATION.md` and `Y046_Y049_RELEASE_READINESS_RECHECK.md`.

## AD-C27 — CookCoverage paths and soft-reference boundary

`OneBossFight.Content.CookCoverage` in `Source/OneBossFight/Tests/RPGAutomationTests.cpp` scans literal `/Game/...` strings in Source `.cpp`/`.h`, compares each path to a `DirectoriesToAlwaysCook` prefix from `Config/DefaultGame.ini`, and fails for uncovered literals. It does not inspect the Asset Registry dependency closure or prove an actual cook/stage contains a package. Constructed paths and references assigned only in Blueprint/default assets are outside its literal scan.

The relevant configured project roots are `/Game/OneBossFight/Player/Animations`, `/Game/OneBossFight/VFX`, `/Game/OneBossFight/Boss01`, `/Game/OneBossFight/Boss`, `/Game/OneBossFight/Effects`, and `/Game/OneBossFight/Data` (plus other project roots listed in `DefaultGame.ini`). The first two cover the current optional ER player animation location and Tier 2 aura; Boss01/Effects cover the recoil montage and parry-distortion material locations. However, optional montage/MPC/PPM/Niagara soft references assigned in Blueprint assets are not independently enumerated by this source-literal test. Root configuration means eligible assets under those roots are configured for cook; it is not proof those exact packages were saved, assigned, staged, or loaded in a packaged run. BUILD-246 CookCoverage predates current optional content and is not a current package witness.

## AD-C28 — Shipping smoke false-positive boundary

`Scripts/PackagedSmoke.ps1` launches the specified staged launcher with `-nosound -log` for a bounded interval and checks that it stays alive. Development then checks a runtime log for configured blocking categories; Shipping skips the log check because Shipping logging is compiled out and calls `CheckShippingBinary.py`, which scans the inner binary for only `rpg.Debug` and `LogRPGDebug` (ASCII/UTF-16). Its Shipping verdict therefore means **process alive plus those two names absent**; it does not prove no cook omissions, correct route, player input, attacks, boss damage/death, or visual acceptance.

`Scripts/ShippingSmoke.ps1` is broader: package Shipping, run the benchmark wrapper, then scan three Development-only feature strings (`rpg.Art.Tier2`, `BuildStamp.txt`, `DEVELOPMENT BUILD`). `RunBenchmark.ps1` runs the automated `-RPGBenchmarkFight` scenario, writes frame summary/CSV and requires process exit 0 plus results. That is a packaged benchmark exercise, not player-controlled gameplay acceptance or proof of every feature path. Keep smoke, benchmark, route/interaction captures, and owner visual approval as separate evidence.

## AD-C29 — Package.ps1 output/stale-stage audit

`Scripts/Package.ps1` writes both Development and Shipping builds to the same `$ProjectRoot/Saved/StagedBuilds` directory, then stamps `Windows/OneBossFight/Saved/BuildStamp.txt`; it contains no stage deletion/isolation step and does not pass UAT `-clean`. `MakeBenchKit.ps1` documentation/defaults expect Shipping at `Saved/StagedBuilds_Shipping/Windows` with a fallback to `Saved/StagedBuilds/Windows`, while its default Development source is also `Saved/StagedBuilds/Windows`. `ShippingSmoke.ps1`, `RunBenchmark.ps1`, and the default Shipping binary checker also target `Saved/StagedBuilds/Windows`.

This is a stage-identity/collision risk: configuration runs can target the same output tree, and the bench-kit defaults can read the same tree for both configurations when no separate Shipping tree exists. The script has no internal evidence that UAT removed all stale files. A future implementation should select a configuration-specific stage root consistently across package, smoke, benchmark, and kit scripts, and must establish clean-output behavior before any deletion/cleanup is introduced. This audit makes no destructive change and no claim that a particular current stage is contaminated.

## AD-C30 — packaged gameplay capture manifest template

For each capture, copy this record beside immutable raw outputs and fill every field from the run; use `null` where a value cannot be witnessed. A completed template is not acceptance until the raw file hashes and run IDs are populated.

```json
{
  "schema": "onebossfight.packaged-gameplay-capture/v1",
  "capture_id": "",
  "captured_at_utc": "",
  "source": {
    "branch": "",
    "commit": "",
    "working_tree_clean": null,
    "change_summary_or_diff_sha256": null,
    "engine_version": ""
  },
  "package": {
    "build_id": "",
    "configuration": "Shipping",
    "launcher_path": "",
    "launcher_sha256": "",
    "inner_executable_path": "",
    "inner_executable_sha256": "",
    "build_info_path": "",
    "build_info_sha256": "",
    "cook_manifest_path": "",
    "cook_manifest_sha256": "",
    "uat_log_path": "",
    "uat_log_sha256": ""
  },
  "run": {
    "map": "/Game/OneBossFight/Levels/L_SevarogArena",
    "route": "",
    "encounter_definition": "",
    "resolution": {"width": 1920, "height": 1080},
    "display_mode": "",
    "frame_cap_or_vsync": "",
    "launch_arguments": [],
    "input_device": "",
    "controls_profile": "",
    "hardware_gpu": "",
    "gpu_driver": "",
    "test_case_ids": []
  },
  "evidence": {
    "video_path": "",
    "video_sha256": "",
    "game_log_path": "",
    "game_log_sha256": "",
    "summary_path": null,
    "summary_sha256": null,
    "frames_path": null,
    "frames_sha256": null,
    "screenshots": [],
    "result": "",
    "observations": [],
    "limitations": []
  }
}
```

Template fields are capture requirements, not measured project results. For gameplay approval include player-controlled steps and observable outcomes; benchmark-only data must be labeled as benchmark data.
