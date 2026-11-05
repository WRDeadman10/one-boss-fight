# Queue S21 — typed gameplay values from parity checks

Date: 2026-11-05. `write_a4_parity_receipt.py` now promotes explicit health, posture, and damage values in each registered driver's PASS/FAIL check message into a `gameplay-check-NNNN` typed observable. The value names the source check, retains its status/message, and uses exact comparison. Health transitions and current/maximum pairs receive distinct field names. The extractor deliberately does not calculate deltas or infer values from unlabelled numbers.

The registration covers all 31 drivers in `DRIVERS`. A scan of the available `B_C835_PARITY` historical logs found labeled gameplay values in the following subset; the remaining stored logs had no check message matching these field labels. Future captures use the same extractor across all 31 drivers.

| Driver | Historical logs scanned | Check messages with typed fields | Fields found |
|---|---:|---:|---|
| `pie_a4_low_sweep` | 12 | 0 | — |
| `pie_dormant_wake` | 6 | 0 | — |
| `pie_damage_path` | 6 | 15 | health |
| `pie_player_death_reset` | 8 | 64 | health, health_current, health_maximum |
| `pie_telegraph` | 8 | 0 | — |
| `pie_boss_hud` | 8 | 0 | — |
| `pie_phase_reset` | 2 | 2 | posture |
| `pie_boss_death` | 4 | 0 | — |
| `pie_boss_death_states` | 2 | 0 | — |
| `pie_victory_lock` | 2 | 0 | — |
| `pie_transition_rules` | 2 | 10 | damage |
| `pie_a5_heal_punish` | 4 | 4 | health_before, health_after |
| `pie_bleed` | 2 | 6 | health_before, health_after, damage |
| `pie_leap_wave` | 2 | 8 | health, health_before, health_after, damage |
| `pie_posture_hits` | 2 | 32 | posture |
| `pie_hyperarmor` | 2 | 2 | posture |
| `pie_close_attacks` | 2 | 12 | health_before, health_after |
| `pie_authored_close_clips` | 2 | 0 | — |
| `pie_boss_clips` | 2 | 0 | — |
| `pie_attack_rules` | 2 | 0 | — |
| `pie_boss_look` | 2 | 0 | — |
| `pie_riposte` | 6 | 0 | — |
| `pie_riposte_exec` | 2 | 4 | health_before, health_after, health, damage |
| `pie_riposte_lethal` | 2 | 2 | health_before, health_after |
| `pie_trace_audit` | 2 | 0 | — |
| `pie_hit_intake` | 2 | 20 | posture |
| `pie_iframes` | 2 | 0 | — |
| `pie_fog_gate` | 2 | 0 | — |
| `pie_remains` | 2 | 0 | — |
| `pie_soak` | 2 | 0 | — |
| `pie_legend` | 2 | 0 | — |

Tests cover health transitions, maximum/current health, lethal transitions, posture and damage labels, and registration-wide extraction across all 31 driver prefixes (`test_a5_parity_driver_registration.py`: 15/15). S22 regenerated all 31 available `_d5`/`_t1` pairs from their existing raw logs into a temporary directory and reran the comparator: 31 PASS, 0 FAIL, 0 INCONCLUSIVE. The two arms had matching typed-field sets and values for every pair (62 typed observables per arm across the 31 pairs). No source receipt or raw log was modified; this is receipt regeneration, not a new live run.

Temporary receipts and reports: `%TEMP%\s22-parity-zckb3ur7` on the Lead machine used for this run.

| Pair | Result | Typed gameplay observables (legacy/data) |
|---|---|---:|
| `pie_a4_low_sweep_t1` | PASS | 0/0 |
| `pie_a5_heal_punish_d5` | PASS | 1/1 |
| `pie_a5_heal_punish_t1` | PASS | 1/1 |
| `pie_attack_rules_d5` | PASS | 0/0 |
| `pie_authored_close_clips_d5` | PASS | 0/0 |
| `pie_bleed_d5` | PASS | 3/3 |
| `pie_boss_clips_d5` | PASS | 0/0 |
| `pie_boss_death_d5` | PASS | 0/0 |
| `pie_boss_death_states_d5` | PASS | 0/0 |
| `pie_boss_hud_d5` | PASS | 0/0 |
| `pie_boss_look_d5` | PASS | 0/0 |
| `pie_close_attacks_d5` | PASS | 6/6 |
| `pie_damage_path_t1` | PASS | 3/3 |
| `pie_dormant_wake_t1` | PASS | 0/0 |
| `pie_fog_gate_d5` | PASS | 0/0 |
| `pie_hit_intake_d5` | PASS | 10/10 |
| `pie_hyperarmor_d5` | PASS | 1/1 |
| `pie_leap_wave_d5` | PASS | 4/4 |
| `pie_legend_d5` | PASS | 0/0 |
| `pie_phase_reset_d5` | PASS | 1/1 |
| `pie_player_death_reset_t1` | PASS | 8/8 |
| `pie_posture_hits_d5` | PASS | 16/16 |
| `pie_remains_d5` | PASS | 0/0 |
| `pie_riposte_d5` | PASS | 0/0 |
| `pie_riposte_exec_d5` | PASS | 2/2 |
| `pie_riposte_lethal_d5` | PASS | 1/1 |
| `pie_soak_d5` | PASS | 0/0 |
| `pie_telegraph_d5` | PASS | 0/0 |
| `pie_trace_audit_d5` | PASS | 0/0 |
| `pie_transition_rules_d5` | PASS | 5/5 |
| `pie_victory_lock_d5` | PASS | 0/0 |
