# B8 — Combat Flipbook Effects

## Status

Implemented; not compiled or run. Claude owns the build and PIE validation.

## Implementation

- Added `ARPGFlipbookEffect` in `Source/OneBossFight/Player/RPGFlipbookEffect.h` and `.cpp`: one non-colliding engine plane, one dynamic material instance, camera-facing tick, 8 by 8 row-major `Frame` scalar, terminal frame 63, then a 0.05 s lifetime grace for one render frame.
- Uses Claude's C-66 instances exactly: blood `MI_Boss01_FB_BloodBurst` for 0.60 s at 140 cm, additive spark `MI_Boss01_FB_HitSpark` for 0.25 s at 90 cm, and dust `MI_Boss01_FB_DodgeDust` for 0.80 s at 220 cm wide / 110 cm high and lifted 55 cm.
- `URPGBossBleed::BeginPlay` preloads blood and `DoProc` spawns it beside the existing Niagara call (`Source/OneBossFight/Player/RPGBossBleed.cpp:34-37`, `:107-113`).
- `URPGHitIntake::BeginPlay` preloads spark; the deferred, accepted first record retains the pack `FHitResult.ImpactPoint` and spawns it only after same-frame blade merges (`Source/OneBossFight/Player/RPGHitIntake.cpp:418-435`, `:527`).
- `URPGDodgeTiming` preloads dust and starts it on the observed dodge-ability active edge. The edge now runs independently of `bBackwardWithoutInput`; only the pre-existing backward turn remains conditional (`Source/OneBossFight/Player/RPGDodgeTiming.cpp:54-70`, `:76-87`).
- Added pure frame-rule automation source `Source/OneBossFight/Tests/RPGFlipbookEffectTests.cpp`, PIE driver `Scripts/Editor/pie_flipbooks.py`, `pie_flipbooks` row (minimum 7) and `FLIPBOOK-01` in `Documentation/TEST_PLAN.md`.

## Required Validation

1. Build and run all automation tests, including `OneBossFight.Presentation.FlipbookRules`.
2. Warm the editor, then run `Scripts/RunDrivers.ps1 -Only pie_flipbooks`; expected `RESULT 7/7 passed`.
3. Visually inspect blood at the proc point, spark at the weapon impact and dust at the feet. Confirm all planes face the active camera, the spark retains additive blending, and no first-use hitch occurs.
4. Confirm the three material paths are cooked in Shipping. They appear as literal paths in `RPGFlipbookEffect.cpp`, so the existing content coverage scan should discover them; this was not built or packaged here.

## Static Validation Run

- `python -I -c "... ast.parse('Scripts/Editor/pie_flipbooks.py') ..."` printed `pie_flipbooks.py: syntax OK`.
- PowerShell parser on `Scripts/RunDrivers.ps1` printed `RunDrivers.ps1: syntax OK`.
- `python -I Scripts/CheckDocs.py` printed `No documentation integrity findings.`
- Public project Python calls were checked in headers: `URPGInputTestUtils::InjectAction` / `SetKeyDown` (`Combat/RPGInputTestUtils.h:25,30`), `URPGBossEncounter::HoldForTest` / `Wake` (`Player/RPGBossEncounter.h:67,75`), `URPGCombatDebug::DebugRefillPlayer` (`Player/RPGCombatDebug.h:75`), and the three new `ARPGFlipbookEffect` getters (`Player/RPGFlipbookEffect.h:54-61`).

No editor, build, PIE, package, game, commit, or push was run.
