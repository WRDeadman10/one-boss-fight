# BL-46..50: guard tests, batch 10 (PoiseRegen, Presentation; PunishLimiter false positive)

Assigned by X-2182 and X-2183 (lead Codex) to C (implementer), 2026-11-12. This is lane BL, batch 10 of 20.

**Two new test files only.** No production source edits, and no Unreal, build, PIE, commit or push.
- **Not compiled or run:** the engine-lock acceptance build is pending with the lead.
- **Checked by hand:** every assertion was traced against the header source.

## BL-48: PunishLimiter, an audit false positive (no test added)

The BL-01..05 census listed the `MaxUses` 100/101 boundary as untested. It is already asserted in `RPGBossQueueEBoundaryTests.cpp:111-121` (`FBossPunishLimiterMaximumAndOverflow`): `CanUse(S,100)` is true, `CanUse(S,101)` is false, and the `MAX_int32` counter refuses and cannot increment. Recorded as an **audit false positive**. No duplicate test was added.

## BL-49: re-verification and non-duplication (by hand)

| Header | Guard (line) | Gap tested | Existing tests, not repeated |
|---|---|---|---|
| `RPGBossPoiseRegenRules.h` | `:10-11` | `BasePerSecond` <0 or >1e6; negative `DelaySeconds`; `DelaySeconds` >1e6; `RampSeconds` >1e6; `MaxScale` <1 or >3; NaN in each of the 5 parameters; a negative elapsed time; `MaxScale` exactly 3 | `…PoiseRegen.Rules` (before the delay, the delay boundary, half ramp, the cap, monotonicity, **+Inf elapsed**); `ZeroRampMutation` (**zero ramp**); QueueE (MaxScale 1.5, 2 and 1; the ramp-end adjacent case). MaxScale 3 was not directly asserted anywhere, so it is added. |
| `RPGBossPresentationRules.h` | `:10` `bDead&&!bDeathAlreadyPlayed` | `ShouldPlayDeath(false,true)` is false | `…Presentation.Rules`: (true,false), (false,false), (true,true) |

## BL-46..47: tests

| Task | File | Automation test | Cases |
|---|---|---|---|
| BL-46 | `Source/OneBossFight/Tests/RPGBossPoiseRegenGuardTests.cpp` | `OneBossFight.Framework.PoiseRegen.Guards` | **Control:** a full ramp gives 15. `MaxScale` 3 gives 30 (exact acceptance). **Each of these gives 0** where the same valid call gives 15: base -1 or 1e6+1; delay -1; delay 1e6+1, with an elapsed time of 2e6 so the case discriminates; ramp 1e6+1; MaxScale 0.99 or 3.01; NaN in each of the 5 parameters. A negative elapsed time also gives 0, but that guard is **unobservable**: a negative elapsed time is always below a non-negative delay, which already returns 0. It is documented as an equivalent mutant. |
| BL-47 | `.../RPGBossPresentationGuardTests.cpp` | `OneBossFight.Framework.Presentation.Guards` | **Control:** (true, false) plays. (false, true) does not. |

## BL-50: status

- **Names:** the new names are unique; the existing tests are `…PoiseRegen.Rules`, `…Presentation.Rules` and `…Presentation.FlipbookRules`.
- **Batch 9 citation fix (A-886):** the PatternDetect cites in `BL_41_45_GUARD_TESTS_BATCH9.md` are now `:11/:12/:13`.
- **Defects:** none indicated.
- **Pending:** the engine-lock build.
