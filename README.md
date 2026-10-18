# One Boss Fight

Single-player, third-person Soulslike boss duel in Unreal Engine 5.5.4. See `Idea/IDEA.md` for the concept and `Idea/PROJECT_PLAN.md` for the execution plan.

## Requirements

- Unreal Engine 5.5.4 (launcher install)
- Visual Studio 2022 or newer with the "Game development with C++" workload
- Git + Git LFS (`git lfs install` once per machine)

## Build

```powershell
& "C:\Program Files\Epic Games\UE_5.5\Engine\Build\BatchFiles\Build.bat" OneBossFightEditor Win64 Development "-Project=<path>\OneBossFight.uproject" -WaitMutex
```

Then open `OneBossFight.uproject`. Close the editor before structural C++ changes (new modules/classes need a restart).

## Test

Headless automation tests (close the editor first or run alongside it):

```powershell
& "C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "<path>\OneBossFight.uproject" -ExecCmds="Automation RunTests OneBossFight; Quit" -nullrhi -unattended -nosplash -NoSound -testexit="Automation Test Queue Empty"
```

## Content setup and scripts

| Script | Purpose |
|---|---|
| `Scripts/Editor/setup_m1_content.py` | Idempotent headless setup of BP_PlayerCharacter, BP_RPGGameMode, L_Greybox, L_Benchmark. Run with `UnrealEditor-Cmd.exe <uproject> -run=pythonscript -script=<path> -unattended -nullrhi`. |
| `Scripts/Package.ps1` | Cook and stage a Development or Shipping build to `Saved/StagedBuilds`. |
| `Scripts/RunBenchmark.ps1 -Label <name>` | Run the packaged benchmark at 1920x1080 and print `summary.json` (avg FPS, p95/p99, frames over budget). |

## Docs

`Documentation/` holds decisions, performance log, asset licenses, test plan and known issues.
