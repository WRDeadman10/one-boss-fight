# F-AG2/AG3 COM-004 live arms (lead, Claude, 2026-11-04; FAG23d = 8 attacks, outputs d_*): control, guarded (block hold), parried (block + parry taps).
$f4 = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\F4\run_pie.ps1'
$out = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\B_FAG23_COM004'
$map = '/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofComboOutcomeFAG23d'
& $f4 -Map $map -OutDir "$out\d_control" -Task F-AG23_COM004_control
"control exit=$LASTEXITCODE"
& $f4 -Map $map -OutDir "$out\d_guarded" -Task F-AG2_COM004_guarded -Console 'rpg.BossProofPlayerGuard 3;rpg.BossProofPlayerGuardSeconds 12'
"guarded exit=$LASTEXITCODE"
& $f4 -Map $map -OutDir "$out\d_parried" -Task F-AG3_COM004_parried -Console 'rpg.BossProofPlayerGuard 5;rpg.BossProofPlayerGuardSeconds 12'
"parried exit=$LASTEXITCODE"

