# Queue BQ Gate 1 — first C-1155 run

Date: 2026-11-13. Runner: `Scripts/Editor/run_B_GATE1_BQ_locked_build.ps1`.

## Result

- Evidence: `Docs/BossCombatReview/Execution/Codex/B_GATE1_BQ/Run_20261113_064920_db794e17/`.
- Development `OneBossFightEditor` build: exit 0.
- Full `Automation RunTests OneBossFight`, pinned to DD27j `cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec`: **573 started, 569 passed, 4 failed; suite exit 255**. Gate 1 is not accepted.
- Runner receipt: `RESULT=FAIL`, `STAGE=suite`, `COMPLETE=False`; both locks were released, no locks or temp files were kept. No PIE, package, asset, or map operation was run.

## Failures and hotfix

The four failing automation cases were:

1. `OneBossFight.Dodge.DecisionSeams`: NaN input-size classification.
2. `OneBossFight.Framework.Posture.DrainAmountFinite`: NaN regen arithmetic and raw-NaN assertions under the optimized Development build.
3. `OneBossFight.Framework.Runtime.ProfileDomains`: shared fixture retained `MaxAbortedAttacks=-1` between cases.
4. `OneBossFight.Parry.PackParryGuards`: `RequiredSeconds` was compared before finite/range validation.

Lead hotfix adds finite input checks before dodge comparison, rejects NaN regen operands before arithmetic, validates parry time arguments before comparing elapsed time, resets `MaxAbortedAttacks` in the shared profile fixture, and removes assertions that rely on raw NaN comparisons/arithmetic under UE's optimized floating-point assumptions. Antigravity accepted the hotfix at source/test review level (A-987); Claude acknowledged the file claim (C-1608). The `git diff --check` scoped to the hotfix files is clean.

During the lead's final source re-review, a second NaN edge was found in the regen overflow branch: after `IsFinite(Next)` returned false, the code compared `Next > 0` before distinguishing NaN from infinity. The branch now explicitly rejects `FMath::IsNaN(Next)` before the sign comparison, and the native test covers the `+inf * 0` NaN intermediate. Antigravity accepted this follow-up (A-988), and Claude acknowledged it (C-1609); it has not been compiled or run.

## Next gate

The hotfixes have **not yet been compiled or rerun**. The owner session was disconnected at preflight, both locks were absent, and no Unreal Editor process was running. C-1155 rerun is pending an active console session. Run the same approved locked runner with a fresh evidence directory; accept Gate 1 only if build and pinned suite both exit 0, every started test passes, and teardown releases all owned locks/temps.

## Hotfix rerun

- Evidence: `Docs/BossCombatReview/Execution/Codex/B_GATE1_BQ/Run_20261113_103554_41953579/`.
- The approved C-1155 locked runner completed from the active RDP session; the console-session precondition is for GPU benchmark sets, not this `-NullRHI` build/suite run.
- Development editor build exit 0. DD27j-pinned `Automation RunTests OneBossFight`: **573 started, 573 passed, 0 failed**; suite exit 0; `COMPLETE=True`.
- Teardown: 2 locks created, 2 released, none kept; no temps kept. No PIE, package, asset, or map operation.
- Gate 1 build-and-suite criteria pass. The editor is closed and the owner may open it with `-nosound` for a separate visual/playability check; that check is not part of this receipt.
