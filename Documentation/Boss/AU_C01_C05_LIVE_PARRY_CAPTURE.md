# AU-C01–C05 — full-fight live-parry capture

## Source finding

`Scripts/Editor/pie_full_fight.py` previously cycled light, strong, backstep, air light, air heavy and guard, with a bounded guard-counter path. It had no parry action. Its offline suite asserted that exact action cycle, so the full-fight capture could never show parry recoil or parry distortion. The separate `pie_tier2_parry.py` already demonstrates the required evidence boundary: press during an observed active A4 tracker window and count a result only when `RPGBossLowSweep.get_parried_count()` increases. `URPGPlayerParry.Press()` only opens a timing window; it does not prove contact.

## Change

Added one bounded `parry_watch` slot to the full-fight cycle. It watches the live `RPGAttackTracker`; it calls `RPGPlayerParry.press()` only when the current move is A4 and its active window is observed. It records each A4 attack instance once, distinguishes missing components, refused window, timeout, interrupted attempt, and real parry contact, and increments `parry_contact` only on a fresh low-sweep parry-count increase. The watcher ends after 3 game seconds without a live A4 or after the observed attempt resolves. It does not force-start an attack or inject a parry at a fixed wall-clock offset.

Offline tests were written first. The pre-fix run failed on the missing schedule slot, watcher method and timeout constant. After implementation, the focused suite passes 11/11; `py_compile` and `git diff --check` pass.

## Lead PIE still required

Run `pie_full_fight.py` on DATA-default. Return BUILD ID, map, same-run `[EncounterActivation] route=data`, script revision, A4 instance/position/window, parry `opened`, sweep parried-count before/after, boss montage, contact outcome, capture frame labels/paths/hashes and stop reason. A bounded no-A4 timeout is an inconclusive capture attempt, not a failed gameplay parry. Do not infer owner visual acceptance from this receipt.
