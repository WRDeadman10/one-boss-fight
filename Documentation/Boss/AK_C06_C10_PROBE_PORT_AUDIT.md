# AK-C06–C10 — shared PIE probe port audit

This is an offline review of the AK-SPRINT helper port. No current Lead smoke result exists for the ported scripts.

| Task | Finding |
|---|---|
| C06 | `pie_lead_common.py` imports `unreal` lazily. Five offline `unittest` cases cover boss-owned debug lookup/refill, missing actors/components, game time, combat entry, health, placement, montage selection across meshes, and the finished marker. `python -m unittest test_pie_lead_common.py` passes 5/5 without Unreal. |
| C07 | The control-latency and air-restore case schedules, placement (900 cm), EnterCombat tag, and per-case result fields were retained. Shared setup changes the former player-side debug lookup to the actual boss owner. Montage lookup now searches all skeletal meshes instead of only the first, and the finish line is `SUMMARY finished:` rather than `finished:`; Lead smoke must verify the runner's marker and active montage. |
| C08 | Guard-counter cleanup releases held keys, clears boss hold when present, emits its detailed SUMMARY, and ends PIE. Synthetic warm-up is bounded to three R2 draws, then requires `RPGBuildLoadout.is_combat_enabled()` and no active montage before refill/arm. No array restoration is claimed from Python when `CreatedAbilities` is unavailable; C++ owns its own override timeout/EndPlay cleanup. |
| C09 | The canonical `pie_er_air_hits.py` copies the retained C-992 case schedule, trace line and boss-HP delta format. It uses shared lookup/health/placement/finish, moves the refill lookup to the boss, and corrects a copied setup label from 900 to the actual 160 cm. The retained Lead evidence file is unchanged. |
| C10 | AST parsing passed for the shared module and all four probes. Lead runtime import/route smoke is still required before treating any port as accepted. |

The shared helper deliberately has no fallback to player-owned `RPGCombatDebug`, because that component is attached to the boss in the current runtime. The probes still need to be run by the Lead under `ENGINE_LOCK` on the intended routes.
