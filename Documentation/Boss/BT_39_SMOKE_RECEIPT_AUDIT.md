# BT-39: C-1619 Smoke receipt and source-contract audit

Date: 2026-11-16
Run: `Saved/SevarogArenaRoute/Run_20261116_124914_d40365e8`

## Direct receipt and log observations

- `acceptance.json`: `result=FAILED`, `accepted=false`, `runtime_acceptance_status=BLOCKED`, failure `arena route refused: PlayerHealthTimeout`.
- Suppression was observed for `BP_ExampleGreatSwordBoss_C_3` before BeginPlay (`began_play=0`, `montage_active=0`). There was one local pack player and zero boss/competing-pack-boss actors at refusal.
- No framework binding, successful actor census, Boss HUD count, Sevarog max health, or selected production card was recorded. Boss death was not exercised in Smoke, and raw BehaviorTree ticks remain uninstrumented.
- The log contains 598 health-retry lines, retry 3 through 600, spanning frame 13 to 104 and timestamps `12:49:42.665` to `12:50:12.332` (about 29.667 seconds). Bursts share frames/timestamps, and source has multiple direct call sites in addition to the timer callback, so retry count alone is not a wall-clock measurement.
- The log's `health=hp=0` is the helper's extracted number; it does not prove the Blueprint's actual Health value. `RPGPack::ReadAttribute` calls `CallBlueprintFunction`; that returns true after `ProcessEvent` without validating the output schema. `ReadNumber` returns 0 if the named property is absent or nonnumeric (`Source/OneBossFight/Pack/RPGBlueprintCall.h:95-116,141-149,210-230`).
- No matching style/equipment initialization markers were found in the route log. This is absence of telemetry, not proof that initialization did not occur.
- Post-run source SHA-256 values still match the passing BT-40 receipt. The runner restored `DefaultGame.ini`, closed Editor, released both C-1155 locks, and saved no assets.

## Conclusion

The route remains blocked at the player-health gate. The audit cannot determine whether the actual health value stayed zero or whether output extraction defaulted to zero. Next action is a source-only runtime diagnostic that validates/logs the reflected getter's numeric output property and records player style/health evidence without weakening the gate. No playable package is available.
