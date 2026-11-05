# F-AG1 SEL-008 strafe-stuck live pair (lead, Claude, 2026-11-04): authored static +Y wall vs no-wall control, same profile.
$f4 = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\F4\run_pie.ps1'
$out = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\B_SEL008_STUCK'
& $f4 -Map /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofStrafeBlockerSEL008b -OutDir "$out\blocker" -Task F-AG1_SEL008_blocker
"blocker exit=$LASTEXITCODE"
& $f4 -Map /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofStrafeNoWallSEL008 -OutDir "$out\control" -Task F-AG1_SEL008_control
"control exit=$LASTEXITCODE"
