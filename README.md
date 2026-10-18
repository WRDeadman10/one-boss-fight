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

## Docs

`Documentation/` holds decisions, performance log, asset licenses, test plan and known issues.
