# C-1651 Sound-Enabled Package Preflight Specification

- **Date:** 2026-11-18
- **Directives:** [TEAM_MAILBOX.md](../TEAM_MAILBOX.md) `[X-2690]`, `[C-1650]`, `[C-1651]`, Task `BT-171`
- **Author:** Antigravity (Implementer)
- **Reviewer / Lead:** Codex (Technical Lead)
- **Status:** STATIC PREFLIGHT SPECIFICATION ONLY (Zero builds, cooks, or engine launches executed; strictly read-only source and script audit)

---

## 1. Executive Summary & Objective

Per Lead Codex directive `[X-2690]`, this document defines the static, source-verified preflight requirements, exact command lines, output paths, and log evidence criteria for executing a future **sound-enabled packaged build** of `OneBossFight`.

Prior packaged builds (such as C-1650 in [C1650_WINDOWS_DEVELOPMENT_PLAYTEST_PACKAGE.md](C1650_WINDOWS_DEVELOPMENT_PLAYTEST_PACKAGE.md)) and automated benchmark runs intentionally passed `-nosound` to prevent audio driver initialization and eliminate worker thread hangs during unattended headless execution. A sound-enabled package is required to validate live audio streaming, spatial attenuation, dynamic ducking, and voice concurrency in an actual packaged runtime environment.

---

## 2. Current Audio-Disabling Flags & Source Inventory

A rigorous audit of project configuration, automation scripts, and workflow documentation identified the exact sites where audio is currently suppressed:

| Component / Workflow | Location in Repository | Flag Passed | Mechanism & Purpose |
|---|---|---|---|
| **Automated Benchmark Runner** | `Scripts/RunBenchmark.ps1:44` | `-NoSound` | Injected into `$LaunchArgs`: suppresses audio engine initialization to maximize CPU headroom and eliminate audio driver variance during frame-time profiling. |
| **C-1650 Playtest Packaging** | `Documentation/Boss/C1650_WINDOWS_DEVELOPMENT_PLAYTEST_PACKAGE.md:10` | `-nosound` | Passed to `BuildCookRun` command line to prevent audio thread hangs during packaging. |
| **Automation & Editor Safety** | `AGENTS.md:10`, `Documentation/PROJECT_STATE.md` | `-nosound` | Mandated flag for all interactive and command-line Unreal Editor instances (`Launch the editor with -nosound`). |
| **Playable Dev Launcher** | `Scripts/PlayDevBuild.ps1:22` | *None* (**Sound ON**) | Launch arguments: `'-windowed', '-ResX=1920', '-ResY=1080', '-ForceRes', '-nosplash', '-log'`. Audio is **enabled by default** for interactive player testing. |

---

## 3. Sound-Enabled Packaging Command & Output Targets

### 3.1. Standard Development Packaging Command
To produce a sound-enabled Development package, execute `Scripts/Package.ps1` without passing `-nosound` to the underlying UAT invocation:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Scripts\Package.ps1 -Configuration Development
```

### 3.2. Underlying UAT Command Line
As defined in `Scripts/Package.ps1:66-74`, the wrapper invokes `RunUAT.bat BuildCookRun` with:
- `-project=C:\UnrealProject\OneBossFight\OneBossFight.uproject`
- `-platform=Win64`
- `-clientconfig=Development`
- `-build -cook -stage -pak`
- `-map=/Game/OneBossFight/Maps/L_SevarogArena`
- `-stagingdirectory=C:\UnrealProject\OneBossFight\Saved\StagedBuilds`
- `-NoP4 -utf8output`

*(Note: `Scripts/Package.ps1` does not pass `-nosound` by default; sound suppression in prior runs occurred when callers manually passed `-nosound` to UAT or benchmark runners).*

### 3.3. Expected Packaged Artifacts & Paths
Upon successful cook and stage, the following directory structure and artifacts are produced:
- **Staged Root:** `Saved\StagedBuilds\Windows\`
- **Game Executable:** `Saved\StagedBuilds\Windows\OneBossFight.exe`
- **Packaged Content Container:** `Saved\StagedBuilds\Windows\OneBossFight\Content\Paks\OneBossFight-Windows.pak` (along with `.ucas` and `.utoc` IoStore containers)
- **Build Stamp Receipt:** `Saved\StagedBuilds\Windows\OneBossFight\Saved\BuildStamp.txt` (stamped format: `OBF-DEVELOPMENT-YYYYMMDDTHHmmssZ-<hash>`)
- **Staged Log Directory:** `Saved\StagedBuilds\Windows\OneBossFight\Saved\Logs\`

---

## 4. Mandatory Prerequisites Before Packaging

Before a sound-enabled package run is authorized, the following gating milestones must be satisfied:

1. **Owner Tone Selection Recorded:**
   - Project Owner must submit selections from [C1651_OWNER_SFX_AUDITION_PICK_SHEET.md](C1651_OWNER_SFX_AUDITION_PICK_SHEET.md) for Batch 1 (SFX-10) and Batch 2 (SFX-11..15) in [Documentation/TEAM_MAILBOX.md](../TEAM_MAILBOX.md).
2. **Discrete Runtime Cue Wiring Completed:**
   - Lead Codex must author, review, and approve discrete wiring tasks mapping chosen Sound Cues to verified trigger sites:
     * `Audio/RPGArenaAmbience.cpp` (`Wind` sound reference)
     * `Audio/RPGFootsteps.cpp` (Footstep / land SoundBase)
     * `Player/RPGLegend.cpp` (`ParrySlowMotionSoundMix` assignment)
     * Boss attack montages (`AM_Boss01_A1`, `A2`, `A3`, `Mid01`, `Sprint`) anim notify cue assignments.
3. **Static Preflight Verification:**
   - `python c:/UnrealProject/OneBossFight/Scripts/Tools/check_doc_links.py` must report `broken_links=0`.
   - `python -m unittest discover -s c:/UnrealProject/OneBossFight/Scripts/Tools -p "test_sevarog_sfx_cue_plan.py"` must pass cleanly (4/4 tests OK).
4. **Editor & Workspace Pre-Flight:**
   - Pre-flight check confirms zero running `UnrealEditor.exe` or `OneBossFight.exe` instances.
   - Project locks in `Saved/` must be clear.

---

## 5. Post-Package Playback Checks & Log Evidence

Following packaging, the build must be executed in sound-enabled mode via `Scripts/PlayDevBuild.ps1`. The resulting log (`Saved\StagedBuilds\Windows\OneBossFight\Saved\Logs\OneBossFight.log`) must be inspected for concrete runtime evidence:

### 5.1. Log Signatures to Confirm (Pass Criteria)
- **Audio Device Initialization:**
  ```text
  LogAudio: Display: Creating Audio Device: ...
  LogAudio: Display: Initializing Audio Device '...' with [channels] at [sample_rate] Hz
  LogAudio: Display: Audio Device Output: Format=..., Channels=..., SampleRate=...
  LogAudio: Display: Initialized AudioDevice: ...
  ```
- **Clean Sound Loading:**
  - Selected Sound Cues and Waves must log successful streaming/instantiation without missing asset warnings.

### 5.2. Log Signatures to Reject (Failure Criteria)
- **Missing Asset Warnings:**
  `LogAudio: Warning: Failed to load sound ...` or `LogAudio: Warning: SoundCue ... contains missing sound wave`.
- **Audio Device Failure:**
  `LogAudio: Error: Failed to initialize audio device` or fallback to `DummyAudioDevice`.
- **Voice Starvation / Buffer Underruns:**
  `LogAudio: Warning: Voice starvation detected` or buffer underrun errors during heavy multi-track combat sequences.

### 5.3. Audible Human Verification Checklist
- **Arena Ambience:** Low-level desolate wind whistling is audible immediately upon level load.
- **Boss Attack Telegraphs:** High-speed blade swooshes and hammer air displacement are clearly audible and directional during boss swings.
- **Stance Break Stinger:** Heavy stone masonry collapse / crunch triggers sharply at the exact moment of boss posture breaking.
- **No Sample Clock Drift:** Playback pitch and duration match the audition reels exactly (zero 44.1 kHz / 48.0 kHz demux stretching).

---

## 6. Recovery & Failure Handling Procedures

1. **Packaging Hang / Audio Driver Deadlock:**
   - If UAT hangs indefinitely during cook: do not use wildcard process killing (such as `.bat` or blanket `UnrealEditor-Cmd.exe` kills). Instead, identify and terminate only the specific captured PID / process tree spawned for the UAT run (e.g. `Stop-Process -Id $Process.Id -Force` or `taskkill /PID $UatPid /T /F`). If the PID is unknown, do not force-terminate running editor processes indiscriminately.
   - Inspect UAT log in `Saved/Logs/` to determine the stalling thread.
2. **Packaged Run Crash on Launch:**
   - If `OneBossFight.exe` crashes on startup: inspect `Saved\StagedBuilds\Windows\OneBossFight\Saved\Crashes\` and the latest log in `Saved\Logs\`.
   - If audio device initialization caused an access violation: test with `-nosound` to isolate whether the crash is audio-driver specific.
3. **Artifact Preservation & Stage Isolation:**
   - Never execute indiscriminate recursive deletions of `Saved\StagedBuilds\Windows` (to prevent wiping existing valid playtest packages).
   - If an isolated sound-enabled test package is desired without overwriting the default Development stage, supply a dedicated staging directory via the `-StageDir` parameter (e.g. `.\Scripts\Package.ps1 -Configuration Development -StageDir Saved\StagedBuilds_SoundTest`).
   - Never commit staged packaged binaries or `.pak` files to git (`Saved/StagedBuilds*` directories are git-ignored).

---

## 7. Strict Discipline Confirmation

- **Zero Unreal Editor Launches:** 0 editor instances launched.
- **Zero Builds or Cooks Run:** 0 UAT commands executed.
- **Zero Asset / Script Edits:** `Scripts/Package.ps1` and `Scripts/PlayDevBuild.ps1` remain untouched.
- **Zero Git Commits or Pushes:** No commits or pushes performed.
