# Queue J J026–J030 — parity capture map and repeat policy

## J026: five eligible standard-driver capture scopes

Registry rows below are the exact `RunDrivers.ps1` driver ID, mode, minimum check count and script evidence scope. The minimum is the registered validator threshold, not a captured pass count. These rows define what a future receipt may record; they are not receipts and contain no invented run measurements.

| Driver | Registry | Marker prefix / terminal | Observable fields the script actually samples |
|---|---|---|---|
| `pie_dormant_wake` | R / 11 | `[DormantWake]` / `RESULT n/n passed` | dormant/waking state, authored montage/stage, direct-start rejection during wake, reset/death wake cancellation and death state (`Scripts/Editor/pie_dormant_wake.py`) |
| `pie_telegraph` | R / 25 | `[Telegraph]` / `RESULT n/n passed` | close-telegraph CVar, sampled stage windup seconds, and telegraph-rate restoration (`Scripts/Editor/pie_telegraph.py`) |
| `pie_player_death_reset` | R / 25 | `[DeathReset]` / `RESULT n/n passed` | new pawn/generation, reset boss health/posture/state, player health, and absence/presence of damage outcomes across its authored scenarios (`Scripts/Editor/pie_player_death_reset.py`) |
| `pie_damage_path` | R / 17 | `[DamagePath]` / `RESULT n/n passed` | sampled health deltas, resolver outcomes, hit/invulnerability counters, and audit counters (`Scripts/Editor/pie_damage_path.py`) |
| `pie_boss_hud` | R / 29 | `[BossHud]` / `RESULT n/n passed` | HUD state, widget/banner/bar/prompt visibility, phase-two bar fraction, and victory count (`Scripts/Editor/pie_boss_hud.py`) |

The values above are source-declared probes only. To complete J026, Claude must run each registered driver, capture its actual terminal marker and observable values, and retain the paired control/data receipts, exact identity, and raw logs. The existing run harness does not yet emit trusted selected-route snapshots into receipts, so the data-route receipts remain blocked; no synthetic receipt is created here.

## J027: paired A4 control

The legacy A4 baseline and selected-data run must use the same declared map, binary/build, content/settings digests, seed, driver/arguments, and input digest, with unique run IDs and separate output directories. Preserve command/config capture, full raw log, receipt, and source-log hash for each run. The data run requires the J016–J020 authored definitions/manifest/selection and a trusted snapshot-to-driver bridge; until both exist, J027 is BLOCKED and no result is claimed.

## J028–J029: comparison and negative control

`Scripts/Tools/compare_encounter_parity.py` reports deterministic PASS/FAIL/INCONCLUSIVE, cites both receipt hashes and each observable's source-log/hash, and supports `--verify-source-logs` to hash retained bytes. A valid paired run with different `identity.input_sha256` must be FAIL. Fixtures for input-identity drift and source-log byte verification are authored in `Scripts/Tools/test_compare_encounter_parity.py`; they have not been run by Codex. The v2 builder remains a validator of supplied facts, not a proof that a driver measured them.

The comparator now refuses a report destination that aliases either receipt or any v2 observable's cited source log, so report generation cannot replace those evidence inputs. No source-log scraping is used to infer gameplay values.

## J030: repeat policy

1. Every trial gets a fresh run ID, output directory, raw log, and receipt. Within each control/data pair, all declared identity fields must match; run IDs must differ.
2. Repeats are paired by explicit `trial_id` and the same declared inputs. Never pair by filename order or nearest timestamp.
3. Deterministic observables (selection/manifest identity, generation transitions, refusal token, terminal marker, and exact scripted outcomes) must match within each pair. Preserve every mismatch; do not average it away.
4. Stochastic observables (timing, frame cost, or nondeterministic combat outcomes) are summarized across an agreed, predeclared number of pairs with the raw per-trial values retained. Do not compare them as exact-equality gameplay fields.
5. Missing trials, different identity, missing logs, or insufficient samples are INCONCLUSIVE. Do not silently discard an outlier or combine builds/content/settings across repeats.
6. The run owner supplies the sample count and hardware/method where relevant. This policy invents no performance budget or pass threshold.
