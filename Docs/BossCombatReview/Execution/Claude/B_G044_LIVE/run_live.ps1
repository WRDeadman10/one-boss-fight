# G044 live runs (lead, Claude, 2026-11-04): H019 driver in L_SevarogArena, legacy control then selected route
# (rpg.EncounterDefinition = the new DA_Sevarog_G044_Encounter). Each run: startup, player death, respawn, 6 s watch.
$h019 = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Codex\H019_ORDER\run_pie.ps1'
$out = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\B_G044_LIVE'
Remove-Item Env:H019_ENCOUNTER_DEFINITION -ErrorAction SilentlyContinue
& $h019 -OutDir "$out\control_legacy"
"control exit=$LASTEXITCODE"
$env:H019_ENCOUNTER_DEFINITION = '/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter'
& $h019 -OutDir "$out\selected"
"selected exit=$LASTEXITCODE"
Remove-Item Env:H019_ENCOUNTER_DEFINITION -ErrorAction SilentlyContinue
