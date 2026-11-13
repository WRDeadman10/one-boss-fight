# BL-71..75: guard tests, batch 15 (WarpCurve, YawProbe, DLSSPlayerSettings)

Assigned by X-2193 (lead Codex) to C (implementer), 2026-11-12. This is lane BL, batch 15 of 20.

**Three new test files only.** No production source edits, and no Unreal, build, PIE, commit or push.
- **Not compiled or run:** the engine-lock acceptance build is pending with the lead.
- **Checked by hand:** every assertion was traced against the header source.

## BL-74: re-verification and observability (by hand)

| Header | Gap tested | Existing coverage, not repeated | Discriminates? |
|---|---|---|---|
| `RPGBossWarpCurveRules.h:11-19` | NaN or +Inf `T01`; NaN, +Inf or negative `OvershootAmount`; exact bounds 0 and 0.5 accepted; an invalid `ECurve` → 0 | `…WarpCurve.Rules`: endpoints, midpoints, finite clamp, amount 1.0 (above 0.5), overshoot shape | **Yes, all:** without a guard, `Clamp(NaN or Inf)` becomes 1, and the Linear curve with a bad amount returns 0.5 |
| `RPGBossYawProbeRules.h:11-15` | NaN or Inf `CenterDeg` and `AmplitudeDeg`; `Period` 0 or negative → 0 | extrema boundary; positive and negative overflow witnesses | **Only a negative `Period`:** it would give `10+5·sin(-π/2)=5`. The NaN/Inf input guards and `Period==0` are **equivalent mutants**: the final `IsFinite(Result) ? Result : 0` already returns 0, since `Inf·sin` gives NaN or Inf and `x/0` phases give NaN. The tests label them. |
| `RPGDLSSPlayerSettingsRules.h:13-25` | an unknown `EPlayerMode` → TSR, with and without support | `RPGDLSSPlayerSettingsRulesTests.cpp`: all declared modes, supported and unsupported, plus Off | yes: the `default:` branch is reached only for an unknown value when supported |

**False positives:** none. Every audit item tested here was unasserted. The WarpCurve "amount above 0.5" case is already covered (amount 1.0), so it is not repeated.

## BL-71..73: tests

| Task | File | Automation test | Cases |
|---|---|---|---|
| BL-71 | `Source/OneBossFight/Tests/RPGBossWarpCurveGuardTests.cpp` | `OneBossFight.Framework.WarpCurve.Guards` | **Control:** linear 0.5. NaN or +Inf `T01` gives 0; a NaN, +Inf or -0.01 amount gives 0. Amounts of 0 and 0.5 end at 1, and 0.5 overshoots mid-way (1.5). `static_cast<ECurve>(99)` gives 0. |
| BL-72 | `.../RPGBossYawProbeGuardTests.cpp` | `OneBossFight.Framework.BossYawProbe.Guards` | **Control:** sample 1 of period 4 is 15. Period -4 gives 0 (**discriminates**). Period 0, NaN or +Inf centre, and NaN or +Inf amplitude give 0 (**equivalent**, documented). |
| BL-73 | `.../RPGDLSSPlayerSettingsGuardTests.cpp` | `OneBossFight.Player.DLSSPlayerSettingsGuards` | **Control:** supported Quality gives Quality. An unknown mode (99) gives TSR, supported or not. |

## BL-75: status

- **Names:** the new names are unique; the existing tests are `…WarpCurve.Rules`, `…BossYawProbe.Rules`, the extrema boundary, the overflow witnesses and `…Player.DLSSPlayerSettingsRules`.
- **Defects:** none indicated.
- **Pending:** the engine-lock build.
