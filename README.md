# One Boss Fight

> A single-player Soulslike boss duel for Unreal Engine 5.5.4, built on the Advanced ARPG Combat pack: the pack's combat mannequin against the Ember Warden, a re-skinned great sword boss.

[SCREENSHOT: the player facing the Ember Warden in the arena]

## The Duel

One encounter, one boss, and no filler: wake the Ember Warden in `L_SevarogArena` (the level keeps its early working name), learn the attack sequence, manage stamina and posture, then create an opening for a frontal riposte. The fight changes at phase two and ends with a victory/retry flow rather than a menu transition.

[SCREENSHOT: phase-two roar or leap attack]

## Builds

| Build | Weapon identity | Combat focus |
|---|---|---|
| Starter | Pack sword | Baseline melee build. |
| Strength | Claymore | Higher posture damage, heavy stamina commitment, and authored hyperarmor windows. |
| Dexterity | Dual swords | Faster, lower-posture hits that build bleed. |

[SCREENSHOT: the three-build selection screen]

## Controls

The duel uses the supplied Advanced ARPG Combat input layout.

- Move, camera, lock-on, light attack, strong attack, dodge, and jump use that layout.
- Choose a build before waking the boss: press **B** for the in-game selector, or use `rpg.Build Starter|Strength|Dex`. Controller and menu playtesting remain owner validation items.
- After victory, the retry prompt reloads the encounter.

### Close-attack readability

`rpg.CloseTelegraph` stretches the short pack stand-in tells for close attacks. Its shipped default is `0.4`; set it to `0` to compare the pack's raw pacing. This is an interim readability aid while the authored close-attack clips remain art-blocked, and the owner feel test remains the final decision.

## Run A Packaged Build

1. Package the project with `Scripts/Package.ps1`.
2. Launch the staged `OneBossFight.exe` produced under `Saved/StagedBuilds/Windows`.
3. For a short launcher-and-log smoke check, use `Scripts/PackagedSmoke.ps1`.

The verified Shipping package has passed its binary debug-off check, staged-content manifest check, and launcher smoke check. A full packaged fight and win/retry hand check remain open.

## Verification Status

- `32/32` automation tests passed in the recorded current build.
- The latest PIE regression gate recorded `32/33` passing rows; the outstanding failure is the intermittent `pie_legend` trial tracked as KI-103.
- The Gate 4 soak completed `30` encounters with `213/213` checks.
- Current balance verification uses the 2,000-health boss, 3-percent bleed proc (60 damage), starter 0.39 multiplier, and the three build choices.

## Performance Target

The release target is a packaged 1920x1080 full encounter at at least 60 FPS average with a p99 frame time at or below 16.67 ms, on an RTX 2060 Super. The valid 60 FPS result is still pending: current packaged captures through Remote Desktop are invalid for this hardware decision. A console-session run whose benchmark summary names the NVIDIA GPU remains required.

[SCREENSHOT: benchmark or performance capture]

## Team Workflow

The owner directs design decisions and commits. Claude owns editor work, builds, PIE drivers, packaging, and runtime verification. Codex owns static engineering, tools, documentation, and code that Claude reviews before building. Antigravity supplies the Blender art and animation loop. The shared task tracker and mailbox retain evidence, open risks, and validation status instead of treating an unrun feature as complete.

## Project Status

Current progress per milestone is the dashboard at the top of `Documentation/TASKS.md`. The remaining high-weight work is balance verification, a valid packaged performance run, Shipping/package checks, presentation capture, owner hand tests, and the remaining art/audio integration.

## Build From Source

### Requirements

- Unreal Engine 5.5.4 (launcher install)
- Visual Studio 2022 or newer with the "Game development with C++" workload
- Git + Git LFS (`git lfs install` once per machine)

### Build

```powershell
& "C:\Program Files\Epic Games\UE_5.5\Engine\Build\BatchFiles\Build.bat" OneBossFightEditor Win64 Development "-Project=<path>\OneBossFight.uproject" -WaitMutex
```

Then open `OneBossFight.uproject`. Close the editor before structural C++ changes (new modules/classes need a restart).

### Test

Headless automation tests (close the editor first or run alongside it):

```powershell
& "C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "<path>\OneBossFight.uproject" -ExecCmds="Automation RunTests OneBossFight; Quit" -nullrhi -unattended -nosplash -NoSound -testexit="Automation Test Queue Empty"
```

### Content setup and scripts

| Script | Purpose |
|---|---|
| `Scripts/Editor/setup_m1_content.py` | Idempotent headless setup of BP_PlayerCharacter, BP_RPGGameMode, L_Greybox, L_Benchmark. Run with `UnrealEditor-Cmd.exe <uproject> -run=pythonscript -script=<path> -unattended -nullrhi`. |
| `Scripts/Package.ps1` | Cook and stage a Development or Shipping build to `Saved/StagedBuilds`. |
| `Scripts/RunBenchmark.ps1 -Label <name>` | Run the packaged benchmark at 1920x1080 and print `summary.json` (avg FPS, p95/p99, frames over budget). |

Decisions, performance log, test plan and known issues are in `Documentation/`.
