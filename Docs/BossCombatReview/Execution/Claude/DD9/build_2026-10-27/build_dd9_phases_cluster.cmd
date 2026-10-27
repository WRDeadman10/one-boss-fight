@echo off
"C:\Program Files\Epic Games\UE_5.5\Engine\Build\BatchFiles\Build.bat" OneBossFightEditor Win64 Development "-Project=C:\UnrealProject\OneBossFight\OneBossFight.uproject" -WaitMutex > "Docs\BossCombatReview\Execution\Claude\DD9\build_2026-10-27\build_dd9_phases_cluster.log" 2>&1
exit /b %ERRORLEVEL%

