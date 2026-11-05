# Queue V V-C031–V-C035: Optional Presentation Hooks

**State:** Codex implementation submitted for Lead build/review. All new visual fields preserve the existing native behavior when unset; no Content asset was modified or assigned to a game actor.

## V-C031 — A2 montage tracker plan

`/Game/OneBossFight/Boss01/Animations/AM_Boss01_A2.AM_Boss01_A2` is an optional tracker montage alias for the existing A2 row (`GS_ChargedAttack_Montage`). Antigravity's V-A013 review reports the authored montage's commit at 1.687 s, active interval 1.937–2.107 s, and blend end at 3.134 s against tracker 1.680 s / 1.930–2.110 s / 3.140 s. The full authored-windup montage must not receive the `rpg.CloseTelegraph` rate adjustment. The production ability remains the pack ability; the optional montage is played only by the explicit Development test-preview path, behind `rpg.AttackTracker.A2PreviewClip` (default 0). `StartMove("A2")` and the normal legacy/selected gameplay route remain unchanged.

### Lead-owned paired telegraph comparison

`pie_authored_close_clips.py` now includes the A2 row and accepts `A2_TRACKER_PREVIEW=0|1`, setting the Development CVar before PIE. Lead should run `pie_authored_close_clips` on both routes with preview 0, then again with preview 1, preserving all four original logs and matching game/build/route conditions. For A2, capture montage identity, tracker position at commit and active start, telegraph rate, active end and recovery/blend end, plus the source trace-notify checks. Require the default pair to remain on `GS_ChargedAttack_Montage`; require the preview pair to identify `AM_Boss01_A2`, keep rate 1.0, and stay within the measured V-A013 deltas. Compare gameplay observables, not the montage-name token. Any damage/hit-window or parity mismatch means disable the preview and keep the authored path unwired pending correction.

## V-C032 — A2 preview implementation

Added `OptionalTrackerMontagePath` to `FRPGAttackTiming`, assigned only on the native A2 row. `rpg.AttackTracker.A2PreviewClip` is a Development-only CVar defaulting to 0 and is consulted only in `PlayMoveMontageForTest`; it never replaces the pack ability in `StartMove`. The parity driver sets this CVar from `A2_TRACKER_PREVIEW` before PIE and captures the A2 commit/active timing checks. The tracker recognizes the optional montage by full object path and skips legacy telegraph rate scaling for it. No montage is loaded until the Development preview is explicitly requested.

## V-C033 — Parry slow-motion post-process hook

Added optional `ParryFeedbackCollection` / `ParryPulseParameter` fields to `URPGBossLegend` (collection defaults null). An accepted parry slow-motion request pulses the configured MPC scalar to 1 only with `rpg.Art.Tier2=1`. The Legend time-dilation scope resets it to 0 through the same restore path used on expiry, cancellation, encounter reset, and world teardown. Owner/Antigravity must supply the collection/material assignment; the existing `MPC_CombatFeedback` asset is not changed.

## V-C034 — Phase-two aura hook

Added optional soft Niagara aura and MPC scalar fields to `URPGSevarogDirector`; both default unset. With `rpg.Art.Tier2=1`, phase-two entry attaches the configured effect and sets the configured glow scalar. The director clears the effect/scalar on boss death, encounter reset, and component teardown. Existing phase-two threshold, roar, lightning and gameplay remain unchanged.

## V-C035 — Boss parry recoil hook

Added an optional `ParryRecoilMontage` to `URPGSevarogDirector` (default null). The existing confirmed parry callback asks the boss director to play it only while the Development Tier 2 switch is enabled. The current hit-stop request and parry result are untouched. The montage asset remains owner-gated and unassigned until Antigravity creates/imports it after owner approval.

## Verification boundary

Offline source-contract tests check the zero/null defaults, switch gates, scope cleanup, and that the normal A2 ability path remains the default. Codex did not build or run Unreal; Lead build/native automation, both-route A2 preview pair, and authored visual review remain pending. Cook coverage for any later assigned optional asset is a follow-up task (V-C038).
