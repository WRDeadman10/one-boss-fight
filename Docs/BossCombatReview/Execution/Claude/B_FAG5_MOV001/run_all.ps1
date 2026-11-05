# F-AG5 MOV-001 live runs (lead, Claude, 2026-11-03): four NEW FAG5 maps, one F4 PIE run each, sequential.
$E = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\F4'
$Out = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\B_FAG5_MOV001'
foreach ($n in 'Melee100','Close250','Medium375','Gap700') {
    & "$E\run_pie.ps1" -Map "/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofFAG5_$n" -OutDir "$Out\$n" -Task "F-AG5_MOV001_$n"
    "$n exit=$LASTEXITCODE"
}
