# Live batch (lead, Claude, 2026-11-04): COM-004 Parried with the approved phase hook, then SEL-008 geometry v3 content + arms.
$root = 'C:\UnrealProject\OneBossFight'
$f4 = "$root\Docs\BossCombatReview\Execution\Claude\F4\run_pie.ps1"
$ed = "$root\Docs\BossCombatReview\Execution\Claude\run_editor_script.ps1"
$out = "$root\Docs\BossCombatReview\Execution\Claude\B_LIVE_20261104b"
& $f4 -Map /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofComboOutcomeFAG23d -OutDir "$out\com004_parried_phase080" -Task F-AG3_COM004_parried_phase080 -Console 'rpg.BossProofPlayerGuard 2;rpg.BossProofPlayerGuardSeconds 15;rpg.BossProofPlayerGuardPhaseSeconds 0.08'
"com004 exit=$LASTEXITCODE"
$s = "$root\Docs\BossCombatReview\Execution\Codex\Proofs\make_strafe_stuck_static_blocker_sel008.py"
foreach ($m in 'blocker','control') {
    $env:SEL008_STRAFE_MODE = $m
    & $ed -Script $s -OutDir "$out\sel008_content_$m" -Task "SEL008c_content_$m" -NullRhi 0 -TimeoutSeconds 300
    "content $m exit=$LASTEXITCODE"
}
Remove-Item Env:SEL008_STRAFE_MODE
& $f4 -Map /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofStrafeBlockerSEL008c -OutDir "$out\sel008_blocker" -Task F-AG1_SEL008c_blocker
"sel008 blocker exit=$LASTEXITCODE"
& $f4 -Map /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofStrafeNoWallSEL008c -OutDir "$out\sel008_control" -Task F-AG1_SEL008c_control
"sel008 control exit=$LASTEXITCODE"
