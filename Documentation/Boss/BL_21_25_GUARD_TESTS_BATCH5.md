# BL-21..25: guard tests, batch 5 (CueJitter, Cue, Defense)

Assigned by X-2169 and X-2171 (lead Codex) to C (implementer), 2026-11-12. This is lane BL, batch 5 of 20. The scope is **limited to the lead's gap list** (X-2171).

**Three new test files only.** No production source edits, and no Unreal, build, PIE, commit or push.
- **Not compiled or run:** the engine-lock acceptance build is pending with the lead.
- **Checked by hand:** every assertion was traced against the header source, and each file has a positive control.

## BL-24: re-verification (by hand)

| Header | Guard (line) | Gap tested | Existing tests, not repeated |
|---|---|---|---|
| `RPGBossCueJitterRules.h` | `:10-11` `CueIndex<0…JitterSeconds<0…SafeMax<SafeMin` and `IsFinite(SafeMin/SafeMax)` | `CueIndex<0`, `JitterSeconds<0`, reversed bounds, non-finite bounds → 0 | `…CueJitter.Rules`, seed/index variation, exact safe clamps |
| `RPGBossCueRules.h` | `:27` `MaxSeconds>3.f` and `IsFinite(MaxSeconds)` | `MaxSeconds==3` accepted; `+Inf` gives -1 | `…Cue.Rules`, `…Cue.Sweep` |
| `RPGBossDefenseRules.h` | `:18` `PlayRate>0`; `:20` `BackstepCm>0`; `:21` `IsFinite(Cooldown)` | a negative play rate; a negative backstep; a `+Inf` cooldown | `…Defense.Rules`, `…Defense.Sweep`, the cooldown adjacent boundary |

## BL-21..23: tests

| Task | File | Automation test | Cases |
|---|---|---|---|
| BL-21 | `Source/OneBossFight/Tests/RPGBossCueJitterGuardTests.cpp` | `OneBossFight.Framework.CueJitter.Guards` | **Control:** zero jitter returns the base time exactly (1.0). Each of these gives 0: cue index -1; jitter -0.1; bounds (2, 1.5); NaN `SafeMin`; NaN `SafeMax`; +Inf `SafeMax`; -Inf `SafeMin`. |
| BL-22 | `.../RPGBossCueGuardTests.cpp` | `OneBossFight.Framework.Cue.Guards` | `HoldSeconds(1, 3, 42, i)` stays in [1, 3] for 8 indices, so a max of exactly 3 is accepted. A max of `+Inf` gives -1. |
| BL-23 | `.../RPGBossDefenseGuardTests.cpp` | `OneBossFight.Framework.Defense.Guards` | **Controls:** `TelegraphOk(.5, 1)`, `BackstepDistanceOk(100)`, `CooldownOk(3)`. A play rate of -1 is refused, including `(-.5, -1)`, whose ratio alone (0.5 ≥ 0.25) would pass, so only the `PlayRate>0` guard refuses it. A backstep of -10 is refused. A `+Inf` cooldown is refused. |

## BL-25: status

- **Names:** the new names are unique; the existing tests are named `.Rules`, `.Sweep` and adjacent-boundary.
- **Defects:** none indicated.
- **Pending:** the engine-lock build.
