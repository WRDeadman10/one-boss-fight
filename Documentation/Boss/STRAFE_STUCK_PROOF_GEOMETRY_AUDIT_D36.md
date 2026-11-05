# Strafe-stuck proof geometry audit (Queue D36)

Scope: inspect the existing R3c arena-edge procedure and source geometry needed for a valid stuck-recovery witness. Source/docs/evidence review only; no driver or Editor run.

## Intended geometry and observed result

- R3c derives an approximate +Y floor edge from the SEL008 floor scaled 40x40 around `(250,0)`, places the boss at `(500,1900,170)` and target at `(653.5,1900,100)`, yaw 180°, expecting one tangent direction to approach the boundary (`Docs/BossCombatReview/Execution/Claude/B_STRAFE_STUCK/make_strafe_stuck_arena_edge_profile.py:7-13,26-39`). These are script-intended coordinates, not reflected map or collision proof.
- In the boss, neutral strafe computes a direction, sweeps `SetActorLocation(..., true)`, compares actual planar displacement to expected `WalkSpeed * Delta`, and flips only when the rolling ratio is below 0.5 for at least 0.3 s (`Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:498-505`; `Source/OneBossFight/Player/RPGBossStuckRules.h:18-45`). A direction flip without the `strafe_stuck` token is not evidence of this branch.
- Retained R3c completed as a process (`result.json` exit 0; raw log hash recorded) but the expected sheet/retained log reports three starts, zero `strafe_stuck`, and three normal ends. The second window ended `CandidateEligible`; boss moved normally at Y=1900 (`Documentation/Boss/EXPECTED_SHEET_AUTHOR_GUIDE_S152.md:21-29`; `Docs/BossCombatReview/Execution/Claude/B_STRAFE_STUCK/pie_r3c_run1/editor_raw.log:1783,1955,2045`). Thus the run does not prove blocked geometry or stuck recovery.
- R3b used a four-wall collision cage and its content-run attempts crashed while creating walls (`make_strafe_stuck_profile_r3b.py:56-78`; retained failed content runs under `B_STRAFE_STUCK`). The cage is an artificial movement trap, not evidence of a natural arena edge, and the failed attempts remain failures.

## Valid geometry constraints and unknowns

Use an open, ordinary floor/nav-edge setup with no walls/cage, place the boss capsule just inside a verified boundary, and orient the target so the seeded tangent sequence includes an outward component. The expected sheet requires the same interior control to show ordinary movement and the edge setup to block movement for the rule's full threshold. Record map/profile/run identity, actual boss capsule and floor/nav bounds, contact/step positions, seeded direction, expected and actual displacement, elapsed blocked interval, ratio, flip token, and post-flip direction. Physical bounds, navmesh, collision response, capsule dimensions, and swept movement must be reflected/visually verified in the actual authored map; the script's approximate coordinates and log parser cannot establish them.

Disposition: R3c is an invalid/inconclusive positive geometry attempt, not a code failure or pass; reuse the no-cage geometry idea only after live bounds/collision inspection. Do not run either retained content creator as part of this audit.
