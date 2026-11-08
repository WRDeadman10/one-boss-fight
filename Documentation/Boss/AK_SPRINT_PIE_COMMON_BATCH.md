# AK-SPRINT batch — shared Lead PIE probe helpers

`Scripts/Editor/pie_lead_common.py` now centralizes component and boss lookup, boss-owned `RPGCombatDebug` player refill, player health read, `GameplayStatics` game time, active montage read, placement, `Ability.EnterCombat` activation, and the `SUMMARY finished` / PIE end marker. Its `unreal` import is lazy, so the helpers can be unit tested offline.

Four probes use the shared helpers:

1. `pie_er_control_latency.py`: boss lookup/refill, placement, combat entry, montage, finish.
2. `pie_er_air_restore.py`: the same shared operations.
3. `pie_er_guard_counter.py`: boss lookup/refill, placement, combat entry, montage, game time, finish.
4. `pie_er_air_hits.py`: a new canonical reach probe copied from the retained C-992 Lead evidence path, then ported to shared boss lookup/refill, placement, combat entry, health, montage, finish. The retained Lead evidence file was not changed. Corrected its copied setup label from 900 cm to the actual 160 cm.

The previous control, air-restore and air-hit probes looked for `RPGCombatDebug` on the player. The current runtime attaches it to the boss, so they now use the boss-owned component. Probe-specific event schedules, assertions, and result fields remain in each driver.

Offline validation: AST parsing of the helper and all four probes, plus three `unittest` cases for boss-owned refill and lookup, game time, combat entry, health, placement and finished marker. No Unreal/PIE/build/commit by Codex. Lead runtime validation remains open.
