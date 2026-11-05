# Queue G — RunDrivers parity inventory

Source of the active standard gate: `Scripts/RunDrivers.ps1` lines 17–56. Its current registry has **40** standard drivers (the older roadmap says 31 and is stale). Every registered driver script contains a reference to the pack boss/player actor class or the framework fixture class. Current source includes an opt-in selected data route in `URPGPlayerMovesSubsystem::OnWorldBeginPlay` (`Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:57-113`); with no selection the original legacy Attach path remains, and the late-spawn route currently fails closed (`:155-179`). The registered drivers have not been migrated to or run through the data route, so they remain legacy-path baselines. Future parity must preserve the legacy baseline as an explicit control and prove the data route separately. The earlier statement that no startup caller exists is stale after C-800 implementation.

`R` drivers require a final `RESULT passed/total passed` with zero failures and at least `Min` checks; `S` drivers require final `SUMMARY total checks, 0 failed` and at least `Min` checks. A driver-specific `T` overrides the runner's default 420-second timeout. The command runs serially in one open Editor and includes warm-up actions; do not run two chains concurrently.

| # | Script / registered driver | Current route | Final marker | Min | Timeout s |
|---:|---|---|---|---:|---:|
| 1 | `pie_a4_low_sweep.py` | Legacy pack path | R | 14 | 420 |
| 2 | `pie_hit_intake.py` | Legacy pack path | R | 36 | 600 |
| 3 | `pie_posture_hits.py` | Legacy pack path | R | 25 | 1100 |
| 4 | `pie_stamina_cost.py` | Legacy pack path | R | 17 | 900 |
| 5 | `pie_hyperarmor.py` | Legacy pack path | R | 23 | 900 |
| 6 | `pie_bleed.py` | Legacy pack path | R | 19 | 900 |
| 7 | `pie_boss_clips.py` | Legacy pack path | R | 14 | 600 |
| 8 | `pie_riposte_exec.py` | Legacy pack path | R | 15 | 700 |
| 9 | `pie_riposte_lethal.py` | Legacy pack path | R | 3 | 300 |
| 10 | `pie_boss_look.py` | Legacy pack path | R | 14 | 300 |
| 11 | `pie_boss_death.py` | Legacy pack path | R | 11 | 300 |
| 12 | `pie_boss_death_states.py` | Legacy pack path | R | 28 | 600 |
| 13 | `pie_remains.py` | Legacy pack path | R | 4 | 600 |
| 14 | `pie_flipbooks.py` | Legacy pack path | R | 7 | 300 |
| 15 | `pie_builds.py` | Legacy pack path | R | 103 | 1500 |
| 16 | `pie_combat_catalog.py` | Legacy pack path | R | 91 | 300 |
| 17 | `pie_build_hyperarmor.py` | Legacy pack path | R | 20 | 900 |
| 18 | `pie_build_hud.py` | Legacy pack path | R | 8 | 600 |
| 19 | `pie_build_select.py` | Legacy pack path | R | 18 | 600 |
| 20 | `pie_flask_hud.py` | Legacy pack path | R | 7 | 600 |
| 21 | `pie_dormant_wake.py` | Legacy pack path | R | 11 | 600 |
| 22 | `pie_telegraph.py` | Legacy pack path | R | 25 | 600 |
| 23 | `pie_authored_close_clips.py` | Legacy pack path | R | 14 | 600 |
| 24 | `pie_soak.py` | Legacy pack path | R | 213 | 900 |
| 25 | `pie_a5_heal_punish.py` | Legacy pack path | R | 31 | 420 |
| 26 | `pie_player_death_reset.py` | Legacy pack path | R | 25 | 420 |
| 27 | `pie_damage_path.py` | Legacy pack path | R | 17 | 900 |
| 28 | `pie_iframes.py` | Legacy pack path | R | 19 | 1500 |
| 29 | `pie_trace_audit.py` | Legacy pack path | R | 30 | 1500 |
| 30 | `pie_legend.py` | Legacy pack path | R | 25 | 900 |
| 31 | `pie_close_attacks.py` | Legacy pack path | R | 55 | 420 |
| 32 | `pie_leap_wave.py` | Legacy pack path | R | 17 | 420 |
| 33 | `pie_attack_rules.py` | Legacy pack path | R | 13 | 420 |
| 34 | `pie_boss_hud.py` | Legacy pack path | R | 29 | 420 |
| 35 | `pie_victory_lock.py` | Legacy pack path | R | 9 | 420 |
| 36 | `pie_camera_scenarios.py` | Legacy pack path | R | 6 | 420 |
| 37 | `pie_phase_reset.py` | Legacy pack path | S | 14 | 420 |
| 38 | `pie_riposte.py` | Legacy pack path | S | 5 | 420 |
| 39 | `pie_fog_gate.py` | Legacy pack path | S | 6 | 420 |
| 40 | `pie_transition_rules.py` | Legacy pack path | R | 28 | 900 |

Additional modes are outside the 40-row standard gate: `-Full` appends `pie_dodge_trials` and requires 180 trials; the balance table adds three `pie_build_fight` rows (Starter/Strength/Dex), each with 10 checks and 1000-second timeout. Their output is not included in a standard 40-driver parity denominator unless explicitly run and reported.

## Paired-run acceptance

For each eligible standard driver, hold constant map, build/binary identity, content snapshot, settings, seed, player start, input sequence, and command-line arguments. Capture a legacy-control receipt first and the data-path receipt separately; give each a fresh output directory and retain both raw logs plus command JSON. Require the same registered final-marker contract/minimum, compare the driver-declared gameplay observables and terminal result, and record every changed component/selection/activation token. Missing identity, expected marker, clean terminal state, or matching input makes the pair inconclusive. This inventory does not claim any data-path execution or parity result; current source contains only the legacy startup route.

## Receipt comparator contract

`Scripts/Tools/compare_encounter_parity.py CONTROL.json DATA.json` consumes explicit driver receipts with schema `onebossfight.encounter-parity/v1`; it never infers behavior by scanning source. Required fields: `route` (`legacy` or `data`), distinct nonempty `run_id`, `identity` (`map`, `build_id`, `content_sha256`, `settings_sha256`, `seed`, `driver`, ordered `driver_args`, `input_sha256`), `final_marker`, `checks` (`passed` and positive `minimum`), `terminal.clean=true`, `activation.outcome`, `components` census, and nonempty named `observables`. Missing/malformed identity or terminal evidence is INCONCLUSIVE (exit 2); mismatched paired identity, marker, terminal state, or observable values FAIL (exit 1); otherwise PASS (exit 0). The activation receipt and component census are printed side by side because the route is expected to change them; they are not forced equal. Optional `--report-json PATH` writes deterministic `onebossfight.encounter-parity-report/v1` via same-directory atomic replacement; inputs remain read-only. This is only a comparison contract: no current driver emits this receipt, no data-route runtime parity has been established.
