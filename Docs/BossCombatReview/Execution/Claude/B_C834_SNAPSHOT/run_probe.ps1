# C-834 live probe (lead, Claude, 2026-11-05): selected route in L_SevarogArena (startup map), fresh windowed editor, -nosound.
$here = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\B_C834_SNAPSHOT'
$env:H019_ENCOUNTER_DEFINITION = '/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter'
& 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\run_editor_script.ps1' `
    -Script "$here\probe_and_quit.py" -OutDir "$here\probe_selected" -Task 'C834-snapshot-probe' `
    -NullRhi 0 -PyCmd 1 -TimeoutSeconds 240
"probe exit=$LASTEXITCODE"
Remove-Item Env:H019_ENCOUNTER_DEFINITION -ErrorAction SilentlyContinue
Select-String "$here\probe_selected\editor_raw.log" -Pattern 'EncounterSnapshotProbe|HardError' | ForEach-Object { $_.Line }
