# D141 — expected-sheet stale-token audit

Date: 2026-11-03  
Scope: static comparison of active expected sheets with the FrameworkProof schema registry and source literals; no log validator, Editor, or runtime run.

## Result

Scanned 17 active expected sheets: the 13 files in `Docs/BossCombatReview/Execution/Codex/Proofs/` matching `*EXPECTED*.md` (including `LOS_MEMORY_EXPECTED_S117.md`), plus `ANTICHEESE_PROOF_EXPECTED_S119.md`, `ARENA_LEASH_EXPECTED_S115.md`, `PACK_ARENA_PARRY_EXPECTED_D32.md`, and `TIE_BAND_SEED_PROOF_EXPECTED_S120.md`. The author guide, linter negative-fixture description, and this D141 audit report are support documents, not active proof sheets.

The registry at `Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py` contains 138 schema keys. Across active sheets, 40 distinct schema-key names appear in inline trace examples or exact `[FrameworkProof] <token>` notation; all 40 are registered and have a literal `[FrameworkProof] <token>` occurrence in `Source/OneBossFight`. No stale, unknown, or schema-missing token reference was found in the active sheets. No expected sheet refers to an active schema key lacking a source literal emitter. This is a static name comparison, not proof that a branch emits the line at runtime.

## Per-sheet token references and limits

| Active sheet | Registered token references found | Non-token evidence still required or explicitly limited |
|---|---|---|
| `AGGRO_SWITCH_EXPECTED.md` | `aggro_switch`, `dodge_observed`, `player_dodge_started`, `player_dodges_scheduled` | Retained enabled run is range-confounded and has only two observed dodges for three scheduled; it explicitly cannot prove the dodge-rate threshold. |
| `FATIGUE_EXPECTED.md` | `event`, `fatigue`, `guard_state`, `hit`, `sweep` | Per-instance open/close whiff confirmation is explicitly manual; a fatigue trace alone is not a whiff proof. |
| `GUARD_CHIP_EXPECTED.md` | `guard_chip` | The numeric incoming/applied relationship must be compared against the intended guarded-hit condition. |
| `LOS_MEMORY_EXPECTED_S117.md` | `los_lost`, `los_regained`, `los_resume`, `los_search_start`, `los_search_timeout`, `playback_start`, `target_shift_injected`, `walk` | A labeled observation/video must show actual movement to last-known position; request telemetry does not prove movement. |
| `OVERLAY_PARRY_EXPECTED.md` | `overlay` | Screen presentation is a visual criterion; token presence only establishes the optional log path. |
| `PARRY_RECOVERY_EXPECTED.md` | `decision`, `parry_recovery` | Compare engine timestamps and `extra`; token presence alone does not prove the delay gate. |
| `PARRY_STAMINA_EXPECTED.md` | `parry_stamina`, `parry_tag` | Insufficient-stamina refusal remains explicitly unproven live; compare stamina values and tag cleanup. |
| `STRAFE_STUCK_EXPECTED.md` | `strafe_end`, `strafe_start`, `strafe_step`, `strafe_stuck` | Physical blocked movement/nav setup and the measured ratio remain manual; the retained R3c log is explicitly not a successful stuck proof (author guide S152). |
| `TELEGRAPH_SCALE_EXPECTED.md` | `playback_start`, `telegraph_restore`, `telegraph_scale` | Compare effective/restored rates with the authored card rate; registered lines do not validate the authored asset value. |
| `WARP_EASE_EXPECTED.md` | `warp_blocked`, `warp_ease`, `warp_step`, `warp_summary` | Compare movement amounts and matching conditions across arms; the tokens alone do not establish the numeric relation. |
| `YAW_CONE_EXPECTED.md` | `yaw_probe` | Probe samples must span both sides of the cone edge in both runs; this sheet does not convert samples into candidate eligibility. |
| `YAW_PROBE_HYSTERESIS_EXPECTED.md` | `cone_hysteresis` | Current logs lack candidate-specific paired A/B evidence; the sheet explicitly says the hysteresis relation is not proven. |
| `YAW_PROBE_NO_HYSTERESIS_EXPECTED.md` | `yaw_probe` | Candidate identity and the negative control must be tied to the same controlled snapshot; token presence is insufficient. |
| `ANTICHEESE_PROOF_EXPECTED_S119.md` | `anticheese` | Calculate scores from the same snapshot and compare selected card; the structured lines do not establish the arithmetic by themselves. |
| `ARENA_LEASH_EXPECTED_S115.md` | `arena_leash`, `cleanup`, `event`, `playback_start`, `target_shift_injected`, `walk` | Retained run does not prove exact-boundary behavior or an inside-only negative control; driver inputs are mutable and need preservation for replay identity. |
| `PACK_ARENA_PARRY_EXPECTED_D32.md` | None specified in inline token notation | Actor/map/style/profile/run identity fields remain pending or UNKNOWN; the sheet forbids substituting the framework proof boss for the actual pack boss. |
| `TIE_BAND_SEED_PROOF_EXPECTED_S120.md` | None specified in inline token notation | Seed, candidate ordering, and paired selection observations must be preserved as run evidence; the sheet is a run protocol for existing unit tests. |

The names above are registry references in backticks or `[FrameworkProof]` syntax, not claims that every line is present in a retained run. `EXPECTED_SHEET_AUTHOR_GUIDE_S152.md` separates measured evidence from manual observation and unknown state. `EXPECTED_SHEET_LINTER_NEGATIVE_FIXTURES_D65.md` intentionally contains the unregistered `typo_token` solely as a negative test fixture; it is not an active proof sheet and must stay classified as intentionally unknown.

## Separate linter structure finding

The linter source `Scripts/Tools/lint_expected_sheets.py` requires exact level-two headings `Setup`, `Control`, `PASS`, and `FAIL` and only recognizes tokens written as `[FrameworkProof] <name>`. The corrected scan excludes this audit report, the author guide, and negative-fixture description: 9 of the 17 active sheets had missing exact headings, and the other eight already had them. C-762 requested a documentation-only repair; those nine sheets now have the four headings. The explicit rerun passed all 17/17 sheets (X-904). This heading repair does not change the manual/UNKNOWN proof boundaries.

## Method and limits

Parsed the Python AST for the `SCHEMAS` dictionary to count registry keys; scanned active sheet inline trace examples and exact `[FrameworkProof]` tags; checked each referenced key for both registry membership and a literal source tag. The comparison does not evaluate payload patterns, interpolated/dynamic emitters, retained logs, schema semantics, or physical setup. The pre-existing linter description's unknown token was excluded from the active set by role, not treated as a source token.
