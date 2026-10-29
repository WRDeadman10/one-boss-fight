@echo off
"C:\Program Files\Epic Games\UE_5.5\Engine\Build\BatchFiles\Build.bat" OneBossFightEditor Win64 Development "-Project=C:\UnrealProject\OneBossFight\OneBossFight.uproject" -WaitMutex > "C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\DD13\run_2026-10-28\build_dd13.log" 2>&1
exit /b %ERRORLEVEL%

