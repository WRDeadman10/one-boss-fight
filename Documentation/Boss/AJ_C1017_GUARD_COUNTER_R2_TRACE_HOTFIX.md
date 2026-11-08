# C-1017 — guard-counter R2 trace hotfix

Claude accepted the C-1016 source change after BUILD-254 (484/484), but the synthetic PIE run reported an accepted guard counter with no swing or boss damage. This patch changes only `Scripts/Editor/pie_er_guard_counter.py`; it does not assert a runtime fix.

- Replaced all four invalid `world.get_time_seconds()` calls with `unreal.GameplayStatics.get_time_seconds(world)` through a helper.
- Initialized `guard_window` in synthetic mode before its result line.
- Logged R2 press and release game times. The probe continues to press and release `Gamepad_RightTrigger` through `RPGInputTestUtils.set_key_down`, whose C++ implementation forwards `IE_Pressed` and `IE_Released` to `PlayerController::InputKey`. The pack strong action fires on release; the observed ER strong count now distinguishes a missing ER tap from a later pack attack failure.
- From press through 1.5 seconds after release, logged each tick's player montage, world position, boss distance, armed state, and ER strong count. The existing 2-second observation still captures hit count and boss HP.
- Snapshotted runtime `CreatedAbilities.StrongAttackMontages` before R2 and logged array changes and a return to the baseline. If UE Python cannot expose these Blueprint properties, the log marks the array state unavailable and does not claim restoration.

Lead rerun: use the same synthetic route and environment as C-1016 on both encounter routes. Inspect `COUNTER_R2_PRESS`, `COUNTER_R2_RELEASE`, `COUNTER_TICK`, `STRONG_ARRAY_CHANGE`, `OVERRIDE_ARRAYS_RESTORED`, the existing accepted-counter source line, and `RESULT`. The ER count should rise after release. If it rises but no attack montage starts, inspect the pack strong ability's release path; if the override returns to baseline before that release path executes, the trace identifies the timing fault. No new C++ source was changed pending this evidence.

Validation: Python AST parse and scoped whitespace check. Codex did not run UE, PIE, build, or commit.

## C-1020 synthetic draw gate

The Lead's r2 trace showed the R2 tap reached the ER handler on both routes, but the player was still sheathed: the legacy route played `DrawSword_Montage` after the counter tap, while the data route played no attack montage. The synthetic probe now repeats its existing 0.70 s R2 draw warm-up up to three times until `RPGBuildLoadout.is_combat_enabled()` is true, waits for the active player montage to end, and only then refills, calls `DebugArmGuardCounter()`, and taps R2. It fails explicitly if the weapon never draws or a montage persists past 8 s. No production source changed. The Blueprint `created_abilities` array is unavailable to Python in the Lead run, so the array observer remains explicitly unavailable; no native getter was added because the draw-state trace already identified the immediate probe fault.
