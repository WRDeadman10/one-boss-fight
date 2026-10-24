# B10b — Authored Close Reach Discrepancy

## Cause

The prior control probe did not exercise the orientation reported in C7. `pie_close_reach.py` passed its requested yaw through `unreal.Rotator(0, yaw, 0)`, which places the value in the Python Rotator pitch slot. Its historical log records `TRIAL 1 dist 90 yaw -162.2 start (boss yaw now 180.0)` at `Saved/Logs/OneBossFight.log:4262`.

By contrast, C7's three authored misses were real actor yaw `-162.2`: `A3b` at `Saved/Logs/OneBossFight.log:4074`, `A1` at `:4087`, and `A3a` at `:4113`. Their trace windows recorded zero overlap and peak socket steps of 8, 10, and 10 cm at `:4079`, `:4092`, and `:4118`. The unchanged pack A1b at the same yaw recorded 14 overlaps and a 14 cm peak at `:4105`.

This disproves the claimed fresh-PIE comparison. C-78's later controlled bisect also shows that orientation is not the final cause: fresh authored attacks at actual `-162.2` and `180.0` both landed `10/10`, while the copied C1--C6 sequence left all later real attacks with only `8--13 cm` trace peaks. The unchanged pack A1b also fell to `14 cm` after that sequence (`Saved/Logs/OneBossFight.log:4105`), so the remaining defect is a post-interrupt pose or montage-state problem, not authored asset orientation.

## Fix

`pie_close_reach.py` now:

- sets actor yaw through `unreal.Rotator(0, 0, yaw)`;
- runs ten trials at `180.0` and `-162.2` degrees;
- logs requested yaw, actual yaw, and angular error before every trial.

The driver is a measurement probe, so it intentionally makes no pass/fail claim. Keep C7’s threshold relaxed until Claude runs the corrected orientation split. If the `-162.2` group still has weak authored traces while `180.0` does not, that is a product asset/root-orientation defect, not a stale tracker or branch-stop state.

`URPGCombatDebug::DebugBossMontageInstances()` now reports the boss mesh relative transform and every live montage instance's asset, weight, position, playing/stopped state, and root-motion disable count. `pie_close_attacks.py` logs this state after C6 and 0.15 s into the first C7 ability. This is the shortest runtime discriminator: a retained low-weight or stopped instance proves a slot/blend issue; a clean instance list with a moved mesh isolates residual root motion or mesh placement.

## Validation

Ran `python -I` AST parsing on `pie_close_reach.py` and `pie_close_attacks.py`: passed. No editor, build, PIE, package, or game run was performed.
