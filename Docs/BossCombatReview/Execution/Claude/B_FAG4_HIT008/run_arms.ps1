# F-AG4 HIT-008 live pair (lead, Claude, 2026-11-04): existing GuardChip R7 map, control then block hold (guard mode 3).
$f4 = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\F4\run_pie.ps1'
$out = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\B_FAG4_HIT008'
$map = '/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofGuardChipR7'
& $f4 -Map $map -OutDir "$out\control" -Task F-AG4_HIT008_control
"control exit=$LASTEXITCODE"
& $f4 -Map $map -OutDir "$out\guarded" -Task F-AG4_HIT008_guarded -Console 'rpg.BossProofPlayerGuard 3;rpg.BossProofPlayerGuardSeconds 12'
"guarded exit=$LASTEXITCODE"
