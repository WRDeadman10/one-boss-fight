# -*- coding: utf-8 -*-
cits = [
    ('Source/OneBossFight/Player/RPGAttackTracker.h', 22, 'FName MoveId;'),
    ('Source/OneBossFight/Player/RPGAttackTracker.h', 87, 'TArray<FRPGAttackTiming> Attacks;'),
    ('Source/OneBossFight/Player/RPGAttackTracker.cpp', 31, 'A2.MoveId = TEXT("A2");'),
    ('Source/OneBossFight/Player/RPGAttackTracker.cpp', 60, 'AddClose(TEXT("A1"), TEXT("AM_Boss01_A1")'),
    ('Source/OneBossFight/Player/RPGBossHealPunish.h', 44, 'float Cooldown = 4.f;'),
    ('Source/OneBossFight/Player/RPGBossPhases.h', 73, 'FVector2D FireballCooldown = FVector2D(6.f, 10.f);'),
    ('Source/OneBossFight/Player/RPGBossStagger.h', 134, 'float CooldownSeconds = 0.f;'),
    ('Source/OneBossFight/Boss/RPGSevarogDirector.h', 84, 'FVector2D LightningCooldown = FVector2D(6.f, 10.f);'),
]
for p, l, t in cits:
    lines = open(p, 'r', encoding='utf-8', errors='ignore').readlines()
    actual = lines[l-1].strip()
    assert t in actual, f'Mismatch at {p}:{l}: expected {t}, got {actual}'
    print(f'OK {p}:{l} -> {actual[:50]}')
print('All A-230 citations verified 100% against disk!')
