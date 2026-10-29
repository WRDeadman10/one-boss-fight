@echo off

"C:\Program Files\Epic Games\UE_5.5\Engine\Build\BatchFiles\Build.bat" OneBossFightEditor Win64 Development "-Project=C:\UnrealProject\OneBossFight\OneBossFight.uproject" -WaitMutex > "C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\EngineRuns\DD30ChronologyBuild2\build_raw.log" 2>&1

exit /b %ERRORLEVEL%

