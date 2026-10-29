# -*- coding: utf-8 -*-
citations = [
    ('Source/OneBossFight/Player/RPGBossHealPunish.h', 44, 'float Cooldown = 4.f;'),
    ('Source/OneBossFight/Player/RPGBossHealPunish.cpp', 132, 'if (GetCooldownRemaining() > 0.f)'),
    ('Source/OneBossFight/Player/RPGBossPhases.h', 73, 'FVector2D FireballCooldown = FVector2D(6.f, 10.f);'),
    ('Source/OneBossFight/Player/RPGBossPhases.cpp', 345, 'NextFireball = Now + FMath::RandRange(FireballCooldown.X, FMath::Max(FireballCooldown.X, FireballCooldown.Y));'),
    ('Source/OneBossFight/Player/RPGBossStagger.h', 134, 'float CooldownSeconds = 0.f;'),
    ('Source/OneBossFight/Player/RPGBossStagger.cpp', 331, 'Flags.bCooldown = Now < CooldownEnd;'),
    ('Source/OneBossFight/Player/RPGBossStagger.cpp', 443, 'CooldownEnd = bClearCooldown ? 0.0 : Now + CooldownSeconds;'),
    ('Source/OneBossFight/Boss/RPGSevarogDirector.h', 84, 'FVector2D LightningCooldown = FVector2D(6.f, 10.f);'),
    ('Source/OneBossFight/Boss/RPGSevarogDirector.cpp', 388, 'LightningTimer = FMath::RandRange(LightningCooldown.X, FMath::Max(LightningCooldown.X, LightningCooldown.Y));'),
    ('Source/OneBossFight/Audio/RPGFootsteps.h', 81, 'float Cooldown = 0.f;'),
    ('Source/OneBossFight/Audio/RPGFootsteps.cpp', 121, 'if (Movement->IsMovingOnGround() && Speed > 40.f && Foot.Cooldown <= 0.f)'),
    ('Source/OneBossFight/Player/RPGAttackTracker.h', 53, 'float RecoveryEndTime = 0.f;'),
    ('Source/OneBossFight/Player/RPGAttackTracker.cpp', 36, 'A2.RecoveryEndTime = 3.14f;'),
    ('Source/OneBossFight/Player/RPGAttackTracker.cpp', 60, 'AddClose(TEXT("A1"), TEXT("AM_Boss01_A1"), TEXT("GS_Attack03_Montage"), TEXT("/Game/OneBossFight/Boss01/Animations/AM_Boss01_A1.AM_Boss01_A1"), 0.33f, 0.35f, 0.50f, 1.20f, false, true);'),
    ('Source/OneBossFight/Player/RPGAttackTracker.cpp', 62, 'AddClose(TEXT("A3a"), TEXT("AM_Boss01_A3a"), TEXT("GS_Attack01_Montage"), TEXT("/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3a.AM_Boss01_A3a"), 0.38f, 0.40f, 0.60f, 0.80f, false, true);'),
    ('Source/OneBossFight/Player/RPGAttackTracker.cpp', 63, 'AddClose(TEXT("A3b"), TEXT("AM_Boss01_A3b"), TEXT("GS_Attack02_Montage"), TEXT("/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3b.AM_Boss01_A3b"), 0.13f, 0.15f, 0.40f, 1.3333f, true, true);'),
    ('Source/OneBossFight/Player/RPGAttackTracker.cpp', 74, 'A6.RecoveryEndTime = 1.80f;'),
    ('Source/OneBossFight/Player/RPGAttackTracker.cpp', 255, 'if (Timing && Position < Timing->RecoveryEndTime - 0.1f)')
]

for p, l, t in citations:
    lines = open(p, 'r', encoding='utf-8', errors='ignore').readlines()
    assert l <= len(lines), f"{p} has only {len(lines)} lines, cited {l}"
    actual = lines[l-1].strip()
    assert t in actual, f"Mismatch at {p}:{l}! Expected '{t}', got '{actual}'"
    print(f"OK {p}:{l} -> {actual[:55]}")

print(f"PASS: All {len(citations)} citations verified 100% against disk.")
