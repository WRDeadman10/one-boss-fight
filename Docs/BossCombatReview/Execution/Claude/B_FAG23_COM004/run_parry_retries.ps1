# F-AG3 COM-004 Parried retries (lead, Claude, 2026-11-04): d_parried landed its only parry on leaf node B; parry timing is
# phase-dependent, so two more fresh runs on FAG23d: parry-only presses (mode 2) and block + parry taps (mode 5).
$f4 = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\F4\run_pie.ps1'
$out = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\B_FAG23_COM004'
$map = '/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofComboOutcomeFAG23d'
& $f4 -Map $map -OutDir "$out\d_parried_mode2" -Task F-AG3_COM004_parried_mode2 -Console 'rpg.BossProofPlayerGuard 2;rpg.BossProofPlayerGuardSeconds 15'
"mode2 exit=$LASTEXITCODE"
& $f4 -Map $map -OutDir "$out\d_parried_mode5b" -Task F-AG3_COM004_parried_mode5b -Console 'rpg.BossProofPlayerGuard 5;rpg.BossProofPlayerGuardSeconds 15'
"mode5b exit=$LASTEXITCODE"
