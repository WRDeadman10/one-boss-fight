# Report B7 — Boss Death Remains

## Decision

Implemented `ARPGBossRemains` as an actor rather than a component: the pack
destroys the boss actor after `URPGBossDeath` reaches `Dead`, while the remains
must outlive that actor until a reset or level teardown.

## Files

- `Source/OneBossFight/Player/RPGBossRemains.h/.cpp`: static-mesh actor,
  synchronous death-edge preload, per-slot named MID setup, dissolve rule,
  non-Shipping `rpg.RemainsFormSeconds`, and reset cleanup.
- `Source/OneBossFight/Player/RPGBossDeath.h/.cpp`: captures the boss mesh
  world transform (including scale), preloads at `BeginDeath`, and spawns only
  from `EndPlay(Destroyed)` after state `Dead` and outside teardown.
- `Source/OneBossFight/Player/RPGBossEncounter.cpp`: clears existing remains
  at `ResetEncounter` entry, including a reset that the existing death guard
  subsequently refuses.
- `Source/OneBossFight/Tests/RPGRemainsTests.cpp`: pure dissolve-rule
  automation test.
- `Scripts/Editor/pie_remains.py` and `Scripts/RunDrivers.ps1`: four-check
  production-path PIE driver and registered `pie_remains` row.
- `Documentation/TEST_PLAN.md`: `REMAINS-01` row required by the driver
  registry integrity check.

## Material Contract

All slots use `M_Boss01_Remains` then select tint/glow by source material slot
name: `M_Boss01_AshPlate` `(0.10, 0.095, 0.09) / 0`,
`M_Boss01_EmberCore` `(0.9, 0.28, 0.04) / 0.45`, and
`M_Boss01_AncientSteel` `(0.05, 0.055, 0.065) / 0`. The burst uses the existing
pre-cooked bleed `NS_BulletHit_Med` as a one-shot cover for the corpse-to-statue
swap; no new effect asset or pack asset is edited.

## Shipping

`rpg.RemainsFormSeconds` is declared only under `!UE_BUILD_SHIPPING`; Shipping
uses the same fixed 2.5-second duration without registering a cvar. No new
Shipping log is emitted. Test-facing UFUNCTION declarations remain unconditional.

## Symbol Review

- `UWorld::SpawnActorDeferred` / `AActor::FinishSpawning` —
  `Engine/World.h`, `GameFramework/Actor.h`.
- `UStaticMeshComponent::CreateDynamicMaterialInstance` —
  `Components/StaticMeshComponent.h`.
- `UMaterialInstanceDynamic::SetScalarParameterValue` and
  `SetVectorParameterValue` — `Materials/MaterialInstanceDynamic.h`.
- `UNiagaraFunctionLibrary::SpawnSystemAtLocation` —
  `NiagaraFunctionLibrary.h`.
- `URPGCombatDebug::DebugSetBossHealthFraction` / `DebugRefillPlayer` —
  `Source/OneBossFight/Player/RPGCombatDebug.h:60,75`.
- `URPGInputTestUtils::InjectAction` / `SetKeyDown` —
  `Source/OneBossFight/Combat/RPGInputTestUtils.h:25,30`.
- `ARPGBossRemains::GetDissolve`, `GetSlotCount`, and `IsFullyFormed` are
  unconditional UFUNCTIONs in `RPGBossRemains.h:45,48,51` for the PIE driver.

## Validation

- Re-read all changed C++ and driver files after editing.
- Ran Python AST parsing for `Scripts/Editor/pie_remains.py`; output:
  `pie_remains.py AST: OK`.
- Ran the PowerShell parser for `Scripts/RunDrivers.ps1`; output:
  `RunDrivers.ps1 parser: OK`.
- Ran `python -I Scripts/CheckDocs.py`; output:
  `No documentation integrity findings.`
- Did not compile, build, start the editor, run PIE, package, or run the game.
  Therefore the automation test and PIE driver are unverified at runtime.

## Review Focus

Please build-check `TActorIterator`, deferred actor spawning during the boss
component's `EndPlay`, and the pack's retry input route. The driver uses the
same finishing mechanism as `pie_real_kill.py`: health is lowered through
`DebugSetBossHealthFraction`, then a real Light Attack is injected; it does not
call `DebugKillBoss`.
