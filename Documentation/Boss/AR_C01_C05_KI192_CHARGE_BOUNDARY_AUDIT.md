# AR-C01–C05 — KI-192 charged R2 route boundary

**Scope:** static audit of the configured hold boundary, project callback, current tests, and C-971 legacy/data route observations. No threshold tuning, asset edit, Editor, build, or PIE was performed.

## Source map

- `Source/OneBossFight/Player/RPGDodgeTiming.h:137–151` documents the owner-approved Elden Ring context/actions and the intended input contract: R2 tap is strong, R2 hold is charged; the pack context remains available when this project context is empty.
- `RPGDodgeTiming.cpp:603–629` resolves the local player subsystem and adds the project mapping context at the configured priority. The actual R2 hold trigger configuration is in the referenced input assets (`IMC_EldenRing`, `IA_ER_HeavyTap`); it is not encoded as a numeric hold threshold in this C++ path.
- `RPGDodgeTiming.cpp:632–653` binds the HeavyTap action's `Triggered` event to `OnEldenRingHeavyTap`. `RPGDodgeTiming.cpp:666–679,702–733` injects the pack strong action and handles that trigger; this callback does not choose between `Ability_E_Anim_Montage` and `ChargedAttack_Montage` based on elapsed hold duration.
- `Documentation/Boss/AC_C26_C30_DLSS_AND_PERFORMANCE_GATES.md:21–23` and C-944/C-945 establish the intended 0.35 s input mapping while warning that callback timing is not the hold-threshold implementation.

## Retained C-971 boundary samples

The raw `probe_legacy_lines.txt` and `probe_data_lines.txt` files in `Docs/BossCombatReview/Execution/Claude/P_C971_ERLATENCY/` record:

| Requested R2 hold | Legacy montage / observation | Selected-data montage / observation |
|---|---|---|
| 0.34 s | Ability_E / 372.87 ms; tick 28.04 ms | Ability_E / 394.82 ms; tick 27.95 ms |
| 0.35 s | Ability_E / 400.54 ms; tick 29.58 ms | Ability_E / 392.63 ms; tick 27.29 ms |
| 0.36 s | ChargedAttack / 356.63 ms; tick 31.64 ms | Ability_E / 393.00 ms; tick 27.80 ms |
| 0.70 s | ChargedAttack / 382.08 ms; tick 27.97 ms | ChargedAttack / 367.22 ms; tick 26.29 ms |

These are one observed trial per requested hold and route in the retained C-971 probe. The 0.36 s split is an observed route difference; timing is game-tick-bounded, not physical controller latency. It does not identify whether the trigger asset, action phase, context precedence, frame sampling, or a later route-specific selection path caused the split. Do not change the 0.35 s setting from this sample alone.

## Coverage and next discriminating observation

The current source path establishes context registration, action binding, and pack-action injection. The C-971 probe schedules press/release cases at 0.34/0.35/0.36/0.70 s (`Scripts/Editor/pie_er_control_latency.py:23–31`), but its one sample per case cannot distinguish a repeatable configuration split from run/tick variation. Existing runtime evidence should remain as reported; the new receipt tool in AR-C06–C10 will enforce route/build/tick identity without asserting cause.

Next Lead run: on both routes and a fresh process per case, repeat each duration at least five times with effective context/action identity and hold-trigger events/readback retained. Preserve actual press/release game times, montage selected, observed delay, tick duration, and build/source identity. If the split persists, compare serialized trigger configuration and active mapping contexts before adjusting the hold threshold. If those fields cannot be read safely, report them unknown; do not infer from filenames or nominal duration.

**Disposition:** KI-192 remains open. No source fix is supported yet. This batch is independent of the owner camera/aura choice and the package bench; a future repeated PIE is Lead-owned.
