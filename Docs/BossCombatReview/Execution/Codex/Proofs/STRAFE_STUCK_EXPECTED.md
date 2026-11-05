# Neutral strafe stuck recovery live proof

## Setup

Run `make_strafe_stuck_arena_edge_profile.py` in the Unreal Editor. It duplicates the SEL008 profile, keeps neutral strafe enabled, disables cone hysteresis, moves the boss and target near the +Y edge of the existing floor/nav area, and saves a new map. It spawns no geometry and does not edit the source map. The intended setup leaves one tangent direction pointed toward the arena boundary; Claude must confirm the built map's actual nav bounds and live behavior. Codex does not launch Unreal.

## PASS

- The enabled run starts in neutral with no candidate and shows `strafe_start`, followed by `strafe_stuck flipped=1 movedRatio=<0.5` (`RPGFrameworkBossCharacter.cpp:489–505`). `movedRatio` is accumulated actual movement divided by expected arc over at least 0.3 seconds; do not infer a flip from an arena-edge location alone (`RPGBossStuckRules.h:13–47`).
- Exactly one stuck flip occurs in the uninterrupted strafe window. No stuck line may precede `strafe_start`, follow `strafe_end`, or occur while an attack is active. A restart after a gap over 0.5 seconds starts a new window (`RPGFrameworkBossCharacter.cpp:491–492`).
- Check the first `strafe_step` logged after the flip. From its `elapsed` value and the profile's `SelectorTieSeed`, compute the unflipped direction with `RPGBossStrafe::DirectionAt(seed, elapsed, 0.8, 1.6)` (`Player/RPGBossStrafeRules.h:39–57`). The logged `dir` must be the opposite; this accounts for a normal seeded direction boundary between the flip and the next 0.5-second telemetry sample.
- Continue the trace long enough to see the next direction state and verify the boss continues moving. A stuck event means `StrafeDirFlip` toggled once; it does not mean the strafe ended or that movement immediately reverses on the event's own already-computed step (`RPGFrameworkBossCharacter.cpp:495–505`).

## Control

Run the same opt-in profile in the interior of the nav area with room in both tangent directions and a candidate arranged to become eligible before the strafe budget expires. The normal-end control should show `strafe_start`, ordinary `strafe_step` movement, then `strafe_end reason=CandidateEligible`; it must show no `strafe_stuck` token. This distinguishes normal candidate recovery from the stuck-direction path.

## Validator

`python -I Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py <editor_raw.log>`

## FAIL

- No `strafe_start`, no stuck signal despite blocked movement across the full 0.3 s observation window, a ratio at/above 0.5 on the flip log, a subsequent logged direction that matches rather than opposes the seeded unflipped direction, or repeated flips without a reset.
- If the nav bounds extend beyond the floor, the boss does not approach the edge, or another condition explains movement, treat the run as invalid setup rather than a code pass/fail; adjust the spawn after inspecting the map bounds.
