# SEL-008 static blocker and no-wall control

## Setup

The authored proof uses `/Game/OneBossFight/FrameworkProof/DA_Sevarog_NeutralStrafe_SEL008` without modifying or duplicating it. Run `make_strafe_stuck_static_blocker_sel008.py` in Unreal Editor with `SEL008_STRAFE_MODE=blocker`; it creates the fresh map `L_SevarogFrameworkProofStrafeBlockerSEL008c`. The boss starts at X=500 and the PlayerStart at X=850, so the start separation is 350 cm. The source profile band is 110–140 cm; 350 cm is 210 cm beyond its maximum, satisfying the required 80 cm outside-band start. The fixture's startup walk approaches the band along Y=0.

The setup script reads `capsule_radius_cm` from the exact SEL-008 profile before creating a map. Current profile evidence records a 60 cm boss capsule; the live F4 run also records a 35 cm Recast nav-agent radius. The script refuses if the profile radius differs from 60 cm, then asserts the authored wall face remains at least 15 cm beyond both radii from the Y=0 approach lane. The face is at Y=75 cm: capsule clearance is 15 cm; nav-agent clearance is 40 cm. The initial seeded `dir=-1` tangent moves toward +Y, so the boss capsule contacts the wall after 15 cm of tangent travel. At 180 cm/s this is within the first 0.3 s stuck-observation window (54 cm maximum expected travel). The wall is 160 x 20 x 300 cm, Static, and BlockAll, centered over the band-arrival X; this is wider than the capsule diameter but localized to that arrival. It is authored in and saved with the new map before PIE; the driver does not spawn geometry. All radius, approach-clearance, and contact-window assertions run before `new_level`.

Create the matched no-wall control with the same script and positions by setting `SEL008_STRAFE_MODE=control`; it writes `L_SevarogFrameworkProofStrafeNoWallSEL008c`. Both modes refuse an existing destination. Run each map through the Lead-owned F4 driver, writing separate output folders. Never load a map with `unreal.load_asset`; the run driver loads the package through its existing map-load path. The GameMode assertion reads the class name with `get_name()`, and profile object identity compares `get_path_name().split('.')[0]` to the package path. This script uses no UENUM values.

## PASS

- In the blocker run, record ordinary `strafe_start`, then `[FrameworkProof] strafe_stuck flipped=1 movedRatio=<0.5` after at least the 0.3 s observation window. The ratio must be under 0.5; the raw event is the recovery/direction-flip signal. There must be exactly one such event in the uninterrupted strafe window.
- After the flip, inspect the next `[FrameworkProof] strafe_step elapsed=... dir=... movedCm=...`. Compute the unflipped seeded direction with `RPGBossStrafe::DirectionAt(SelectorTieSeed, elapsed, 0.8, 1.6)`; the logged direction must be its opposite. Later steps must show movement continuing away from the wall. `strafe_stuck` and the following `strafe_step` are the existing recovery/flip and resume evidence; no separate recovery token is emitted by the runtime.
- The matched control uses the same profile, boss/target positions, floor, nav bounds, and driver but no wall. It should show `strafe_start`, positive ordinary `strafe_step` movement, and `strafe_end reason=CandidateEligible`, with no `strafe_stuck` token. A direction change without `strafe_stuck` is the normal seeded schedule, not recovery.
- Keep map path, profile band, `walk start` range, `strafe_start`, `strafe_stuck`, following `strafe_step`, and control tokens in the raw log. The Lead records the run result and manually confirms the authored wall is present only in the blocker map.

## Control

The control is the `SEL008_STRAFE_MODE=control` map generated from the same script. Compare the blocker and control logs under the same build, F4 driver, and duration. The control must not emit `strafe_stuck`; it establishes ordinary neutral-strafe movement with this same 350 cm initial separation and walk-in.

## FAIL

- No `strafe_start`, no `strafe_stuck` despite a manually confirmed blocking contact lasting through the observation window, `movedRatio` at or above 0.5, more than one stuck flip in one uninterrupted window, or no resumed movement after the direction flip.
- If the wall blocks the startup walk, the nav projection differs, or the actual capsule does not contact the wall, mark the setup invalid and adjust the authored geometry before interpreting behavior. The setup receipt must report `capsuleRadius=60`, `navAgentRadius=35`, `wallFaceY=75`, `walkCapsuleClearance=15`, `walkNavClearance=40`, and `strafeContactTravel=15`; a profile or engine setting change requires recalculating and reviewing the geometry. A code-level `strafe_stuck` test does not substitute for PIE evidence.
- The control emitting `strafe_stuck`, or either run failing to reach the intended band, invalidates the pair. Keep run evidence and setup snapshots; do not infer success from the map layout alone.

## Verification

Claude owns Unreal Editor execution and review. Run the linter on this sheet with `py Scripts/Tools/lint_expected_sheets.py Docs/BossCombatReview/Execution/Codex/Proofs/STRAFE_STUCK_STATIC_BLOCKER_SEL008_EXPECTED.md --root .`. Run blocker and control with the existing `Docs/BossCombatReview/Execution/Claude/F4/run_pie.ps1`; the required positive tokens are `strafe_start`, `strafe_stuck`, and `strafe_step`, and the control requires `no strafe_stuck`.
