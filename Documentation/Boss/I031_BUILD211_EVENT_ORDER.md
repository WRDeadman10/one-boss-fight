# I031 — BUILD-211 measured lifecycle order

## Evidence identity

- Run: Claude BUILD-211, H019-C804-live-order, legacy route in `L_SevarogArena`.
- Raw editor log: `Docs/BossCombatReview/Execution/Claude/B_H019_ORDER/editor_raw.log`
- SHA-256: `f44a189075d2414c27d88e01959bc66edc62209d71839f9468b11bee97536fc8`
- Result: `Docs/BossCombatReview/Execution/Claude/B_H019_ORDER/result.json`, exit code 0, not timed out.
- The distinct failed first attempt is retained separately as `B_H019_ORDER_FAIL_1_no_death`; it is not used for this ordering table.

## Observed event order

| Raw log time | Relative time | Token/event | Actor and generation evidence |
|---|---:|---|---|
| 08:05:21.256 | T+0 | `spawn_player` | New player actor ID 188409; generation 1, reset_count 0. |
| 08:05:21.768 | T+0.512362 s | `reset_detected` | Previous player ID 94425; new player ID 188409; generation 1, reset_count 0. |
| 08:05:21.769 | T+0.513253 s | `reset_broadcast` | Generation 2, reset_count 1. The boss log at the same engine timestamp records encounter reset 1. |

The boss actor is `BP_ExampleGreatSwordBoss_C_3` in the same log. The explicit lifecycle token order is spawn → tick-detected player replacement → reset broadcast. The spawned replacement existed for 0.512362 s before detection and 0.000891 s between detection and broadcast. These are calculations from the timestamps shown above.

## Absent tokens and limits

The raw log contains no `binding_released` or `rebind_activated` token; this was the legacy route and the probe only observes reset order. Absence here does not establish behavior of the selected data route. This event order supports the C-809 design trigger and does not prove selected-route rebind correctness, cleanup, or parity.
