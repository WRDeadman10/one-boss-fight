# A6: Hardcoded Gameplay Numbers Audit

**Document Version:** 1.1.0 (Remediated per Tech Lead Review `[C-530]`)  
**Author:** Antigravity  
**Task Reference:** `[C-528]` Order 2, `[C-530]` Review Remediation  
**Status:** DELIVERED (Live Framework Scope vs Retired Reference Split, Strictly Verified on Disk, Pure CRLF)  
**Target Scope:** `Source/OneBossFight/Boss/**`, `Player/RPGFramework*`, `Player/RPGBoss*Rules`, `Player/RPGBossFrameworkProfile*`  

---

## 1. Executive Summary & Active Framework Risk Assessment

Per Tech Lead Claude's instructions in `[C-530]`, this audit strictly segregates **active framework code** from **retired legacy code** (`PROJECT_STATE.md:75-76`).
`ARPGSevarogDirector` is retired and unreferenced by the runtime framework, so its hardcoded numbers carry **zero active architectural risk** and are excluded from active risk counts.

### Active Live Framework Risk Breakdown:
- **Total Active Framework Entries:** 10
- **High Risk Parameters:** 0 (Zero live framework numbers directly compromise combat pacing or player reaction windows)
- **Medium Risk Parameters:** 1 (`RPGFrameworkMoveExecutor.cpp:127` - EarlyStop playback slack tolerance multiplier `1.5`)
- **Low Risk Parameters:** 9 (Navigation band midpoint `0.5`, viewport debug message durations `10.0s`, dormant wake clamp `0.15s`, and schema limit clamps)

### Retired Code Reference (Informational Only, Zero Active Risk):
- **Total Retired Entries:** 13 (All located in `RPGSevarogDirector.cpp`, including strike pending time `3.0s`, polling intervals, and fallback speeds; retained for legacy reference only).

---

## 2. Live Framework Code Audit (Active Architectural Risk)

All entries in this section are in active framework runtime files (`RPGFramework*`, `RPGBoss*Rules`, `RPGBossFrameworkProfile*`).

| File:Line | Value | Governed Gameplay Parameter | Proposed Profile Field Name | Risk | Engineering Rationale & Mitigation |
|:---|:---:|:---|:---|:---:|:---|
| `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:127` | `1.5` | Early playback termination slack tolerance multiplier on Delta * PlayRate. | `URPGBossFrameworkProfile::EarlyStopToleranceMultiplier` | **Medium** | High frame delta hitches combined with non-standard animation play rates could cause false EarlyStop playback failures or mask genuine stall bugs. |
| `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:445` | `10.f` | On-screen viewport error message display duration in seconds when framework character fails initialization. | `URPGBossFrameworkProfile::DebugMessageDurationSeconds` | Low | Telemetry display duration only; does not affect gameplay logic. |
| `Source/OneBossFight/Boss/RPGFrameworkBossController.cpp:17` | `.5f` | Midpoint factor (0.5) between BandMinCm and BandMaxCm for boss navigation goal projection. | `URPGBossFrameworkProfile::NavTargetBandRatio` | Low | Directly centers navigation approach between range thresholds; archetypes favoring perimeter combat cannot bias toward BandMax without code modification. |
| `Source/OneBossFight/Boss/RPGFrameworkProofFixture.cpp:76` | `.5f` | Midpoint factor (0.5) between BandMinCm and BandMaxCm for fixture initial projection. | `URPGBossFrameworkProfile::NavTargetBandRatio` | Low | Fixture setup mirrors controller midpoint calculation. |
| `Source/OneBossFight/Boss/RPGFrameworkProofFixture.cpp:97` | `10.f` | On-screen viewport error message display duration in seconds on fixture initialization failure. | `ARPGFrameworkProofFixture::ErrorDisplayDurationSeconds` | Low | Developer test harness feedback timing. |
| `Source/OneBossFight/Player/RPGBossDormantWakeRules.h:12` | `0.15f` | Safety clamp cap (150 ms) on minimum elapsed time before dormant boss can wake. | `FRPGBossDormantWakeConfig::MaxWakeSafetySeconds` | Low | Prevents premature wake transition during initial montage spawn frame. |
| `Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp:45` | `64` | Maximum substeps limit (64) for dynamic blade sweep temporal discretization. | `FRPGBossFrameworkProfileLimits::MaxSweepSubstepsLimit` | Low | Computational safety guard preventing runaway CPU sweep iteration. |
| `Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp:61` | `.5f` | Lower bound domain clamp (0.5s) on profile StaggerSeconds schema validation. | `FRPGBossFrameworkProfileLimits::MinStaggerSeconds` | Low | Defensive schema validator domain lower bound. |
| `Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp:61` | `60.f` | Upper bound domain clamp (60.0s) on profile StaggerSeconds schema validation. | `FRPGBossFrameworkProfileLimits::MaxStaggerSeconds` | Low | Defensive schema validator domain upper bound. |
| `Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp:100` | `8` | Maximum upper bound on RepeatMemory buffer and AttackCount sequence depth. | `FRPGBossFrameworkProfileLimits::MaxAttackSequenceDepth` | Low | Static array and history memory upper bound. |

---

## 3. Retired Code Reference (Legacy Director, Zero Active Risk)

Per `PROJECT_STATE.md:75-76`, `ARPGSevarogDirector` is retired and unused by the framework boss. These values are catalogued for historical context and are strictly excluded from active framework risk metrics.

| File:Line | Value | Governed Legacy Parameter | Legacy Context | Status |
|:---|:---:|:---|:---|:---:|
| `Source/OneBossFight/Boss/RPGSevarogDirector.cpp:29` | `0.1f` | Component polling tick interval in seconds (10 Hz) for combat director. | `PrimaryComponentTick.TickInterval = 0.1f;` | Retired (PROJECT_STATE.md:75-76) |
| `Source/OneBossFight/Boss/RPGSevarogDirector.cpp:67` | `-90.f` | Pitch rotation angle (-90 degrees) orienting projectile vertically downward toward strike point. | `Actor->SetActorLocationAndRotation(StrikeLocation + FVector(0.f, 0.f, StrikeHeight), FRotator(-90.f, 0.f, 0.f), false, nullptr, ETeleportType::TeleportPhysics);` | Retired (PROJECT_STATE.md:75-76) |
| `Source/OneBossFight/Boss/RPGSevarogDirector.cpp:69` | `2500.0` | Fallback projectile velocity (cm/s) when projectile movement component speed cannot be retrieved. | `double Speed = 2500.0;` | Retired (PROJECT_STATE.md:75-76) |
| `Source/OneBossFight/Boss/RPGSevarogDirector.cpp:75` | `0.1f` | Minimum landing delay clamp (0.1s) for lightning strike impact. | `const float Delay = FMath::Max(0.1f, StrikeHeight / static_cast<float>(FMath::Max(Speed, 100.0)));` | Retired (PROJECT_STATE.md:75-76) |
| `Source/OneBossFight/Boss/RPGSevarogDirector.cpp:75` | `100.0` | Minimum speed divisor floor (100.0 cm/s) preventing division by zero or negative speed in strike delay math. | `const float Delay = FMath::Max(0.1f, StrikeHeight / static_cast<float>(FMath::Max(Speed, 100.0)));` | Retired (PROJECT_STATE.md:75-76) |
| `Source/OneBossFight/Boss/RPGSevarogDirector.cpp:182` | `1.f` | Play rate multiplier (1.0) for Phase 2 roar transition montage. | `RoarLength = Anim->Montage_Play(PhaseRoarMontage, 1.f);` | Retired (PROJECT_STATE.md:75-76) |
| `Source/OneBossFight/Boss/RPGSevarogDirector.cpp:336` | `0.1f` | Montage blend-out duration in seconds (100 ms) when combat director resets. | `Anim->Montage_Stop(0.1f);` | Retired (PROJECT_STATE.md:75-76) |
| `Source/OneBossFight/Boss/RPGSevarogDirector.cpp:414` | `600.f` | Downward floor raycast distance (600 cm) from player actor location. | `StrikeLocation = GetWorld()->LineTraceSingleByChannel(Floor, Feet, Feet - FVector(0.f, 0.f, 600.f), ECC_Visibility) ? Floor.ImpactPoint : Feet - FVector(0.f, 0.f, 90.f);` | Retired (PROJECT_STATE.md:75-76) |
| `Source/OneBossFight/Boss/RPGSevarogDirector.cpp:414` | `90.f` | Fallback vertical Z offset (90 cm) subtracted from player actor location when floor raycast hits nothing. | `StrikeLocation = GetWorld()->LineTraceSingleByChannel(Floor, Feet, Feet - FVector(0.f, 0.f, 600.f), ECC_Visibility) ? Floor.ImpactPoint : Feet - FVector(0.f, 0.f, 90.f);` | Retired (PROJECT_STATE.md:75-76) |
| `Source/OneBossFight/Boss/RPGSevarogDirector.cpp:415` | `3.f` | Telegraph warning countdown in seconds (3.0s) between visual telegraph spawn and lightning impact. | `StrikePendingTime = 3.f;` | Retired (PROJECT_STATE.md:75-76) |
| `Source/OneBossFight/Boss/RPGSevarogDirector.cpp:418` | `5.f` | Vertical Z offset (5 cm) elevating Niagara telegraph decal slightly above floor mesh. | `UNiagaraFunctionLibrary::SpawnSystemAtLocation(GetWorld(), StrikeTelegraphEffect, StrikeLocation + FVector(0.f, 0.f, 5.f), FRotator::ZeroRotator, FVector(StrikeTelegraphScale));` | Retired (PROJECT_STATE.md:75-76) |
| `Source/OneBossFight/Boss/RPGSevarogDirector.cpp:483` | `0.25f` | Health check polling interval in seconds (4 Hz) for evaluating phase transitions. | `if (CheckTimer >= 0.25f)` | Retired (PROJECT_STATE.md:75-76) |
| `Source/OneBossFight/Boss/RPGSevarogDirector.cpp:507` | `0.5f` | Retry cooldown backoff in seconds (500 ms) when lightning strike conditions are not met. | `LightningTimer = FMath::Max(LightningTimer, 0.5f);` | Retired (PROJECT_STATE.md:75-76) |

---

## 4. Verification Protocol

Automated verification via `Docs/BossCombatReview/Execution/Antigravity/Reviews/test_a6_hardcoded_value_audit.py`:
1. Verifies that all 23 cited source file:line locations exist verbatim on disk.
2. Enforces that Section 2 (Live Framework Code) strictly contains zero citations of retired classes (`RPGSevarogDirector`).
3. Enforces pure CRLF line endings and zero tab characters.

