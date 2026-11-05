# D143 — paired-control run identity audit

Date: 2026-11-03  
Scope: compare the expected-sheet pairing contracts with the current log/report utilities. Static source and documentation audit only; no run or test executed.

## Pair contracts found in the expected sheets

| Pair protocol | Shared fields / allowed difference | Current evidence boundary |
|---|---|---|
| Aggro switch (`Docs/BossCombatReview/Execution/Codex/Proofs/AGGRO_SWITCH_EXPECTED.md`) | Same map, neutral distance band, range hold, dodge schedule/timing, selector inputs; only `bAggroEnabled` changes. | Retained enabled run switches at 153.517 cm before the first scheduled dodge and observes only two of three scheduled dodges. It is not a valid threshold positive; control silence alone cannot rescue it. |
| Yaw cone hysteresis (`YAW_PROBE_HYSTERESIS_EXPECTED.md` and `YAW_PROBE_NO_HYSTERESIS_EXPECTED.md`) | Same map/environment, candidate identity, card cone, range, target, phase, seed, probe amplitude/sample order; only `ConeHysteresisDegrees` changes (0 vs 6). | Current R6A8 evidence does not bind the same candidate's eligibility/memory across both arms; the expected sheet explicitly says the hysteresis relation is unproven. |
| Telegraph scale (`TELEGRAPH_SCALE_EXPECTED.md`) | Same copied map/profile/card and authored rate; enabled feature is the intended difference. Compare control playback rate, enabled scaled rate and later restore to the same authored baseline. | The sheet requires this numeric equality explicitly; token-presence-only comparison is insufficient. |
| Anti-cheese (`Documentation/Boss/ANTICHEESE_PROOF_EXPECTED_S119.md`) | Same selector snapshot, range, cooldown/repeat history, card set and seed; gate/pattern factor is the intended difference. | Existing sequences 2 and 3 differ in state/range, so the current observed crossover is not a strict same-snapshot A/B. The sheet calls for a fixed-snapshot pair. |
| Arena leash (`ARENA_LEASH_EXPECTED_S115.md`) | Same map/profile and captured target origin; compare inside/boundary/outside target positions, preserving the same baseline and card behavior. | Existing outside-to-inside run lacks an inside-only negative control and exact 250 cm boundary check; the shared driver also reads mutable map/shift inputs. |
| Pack arena parry (`PACK_ARENA_PARRY_EXPECTED_D32.md`) | Same real arena, actual pack boss/player/style, profile and attack/contact conditions across damaging no-parry and parried arms; only the real parry route differs. | Run IDs, map, actor, style, profile and hooks remain pending/UNKNOWN; no framework-boss substitute can validate the pair. |

The intended common rule is: compare the same scenario and controlled inputs, allow only the named feature toggle or treatment to differ, and retain separate unique run identities for both arms. A different map/profile/seed/source/build/driver, actor, start state, or uncontrolled input invalidates the pair unless that field is explicitly declared the treatment. Missing identity is UNKNOWN and cannot be interpreted as a match.

## What current tooling enforces

- `Scripts/Tools/proof_report.py` accepts a positive log and optional `--control-log`. When paired control identity flags are supplied (`--control-expect-map`, `--control-expect-profile`, `--control-expect-source`), it requires those fields in the control and compares each requested value with the positive log. Map/profile/source mismatches or missing fields fail identity checks; one treatment field remains intentionally outside this shared-identity comparison. Control token checks still run independently.
- Expected positive identity fields now fail closed when absent. Source aliases are normalized from `source`, `source_hash`, and `source_id`.
- The optional `--manifest` freshness/hash path in `proof_report.py:41-70,146-158` is applied to `args.log`; it does not bind the control log, command, seed, source manifest, build, map, profile, or a shared pair ID. `Scripts/Tools/evidence_pack.py` copies a selected raw log and optional pre/post state files with hashes but its manifest schema contains file labels/names/bytes/hashes, not pair metadata (`:40-78`).
- `Scripts/Tools/compare_parry_runs.py:14-31` compares RESULT rows, hit outcomes and token-count deltas from two paths; it has no identity or setup compatibility check. `detect_duplicate_pie_runs.py` only finds identical chunks within one concatenated file and does not establish that two files are distinct, paired runs.

Therefore a mismatched pair cannot be certified by current tooling alone. A caller can supply a control from a different map/profile/seed or an old overwritten log and still receive token-presence results. Treat the comparison as unpaired/incomplete unless the reviewer independently confirms the shared identities and the declared treatment delta from retained per-arm evidence.

## Minimum pair-identity record for a valid comparison

Record per arm and bind both records to a shared `pair_id`:

1. Unique `run_id`, arm role (`positive` / `control`), UTC start/end, and immutable raw-log path plus SHA-256.
2. Project/build identity: engine version, executable/DLL or build ID, compiled Source manifest hash, relevant content/profile asset hashes, and driver/command hash.
3. Map package, profile asset, actor/class identity, seed, target/start transforms, game mode, CVar/input state, test hooks and scenario schedule.
4. An explicit allowlist naming the sole treatment difference (or a list of all planned differences) with actual readbacks from both arms.
5. Fail closed when a required field is absent, different outside the allowlist, or linked to a reused log path without a preserved per-attempt copy/hash. Keep manual geometry, contact, and gameplay observations separate from structured telemetry.

This audit's proof-report identity gap was addressed under C-763. `Scripts/Tools/test_queue_c_tools.py` now covers absent expected identity, matching paired identities, each of map/profile/source mismatches, and missing control fields. Full offline tool suite: 48 tests run, 47 passed, 1 skipped. These checks cover only the fields requested by the caller; they do not establish build, actor, seed, run-ID, or treatment readback equivalence, and do not certify any retained pair.
