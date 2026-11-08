# C-1065: First Dodge Activation Retry Hotfix

Status: workaround proven in PIE on both routes, standing and moving; root cause not isolated; package open. BUILD-263 compiled and the full Lead suite passed 486/486. Lead's both-route first-dodge probe reports the first standing dodge after draw moves about 84 cm, the moving first dodge rolls 215.8/219.7 cm with backstep_count=0, repeats work, and the non-forced one-shot retry fires once with no duplicate. The retained `P_SHOWCASE/showcase_def4.log` confirms the first standing press's retry returned `activated=1`, `active_after=1`, `buffer_consumed=1`, then `AM_ER_Backstep_Mixamo_V2` played with root motion (83.9 cm total displacement by the end of rep 1); i-frames also activated. Package proof remains open. The source pack InputBuffer/Enhanced Input/context mechanism was not independently isolated. Evidence folder: `Docs/BossCombatReview/Execution/Claude/B_C1067_DODGERETRY/`.

## Evidence and bounded change

C-1065 BUILD-262 reports press 1 after draw with `GA_Player_Dodge_C active=0`, `CanActivate=1`, stamina 100, owned tags `{Player.Character, Equipped.Arrow}`, no blockers, and next-tick active still 0 / 0 cm. Presses 2/3 activate and move 96 cm. This rules out a CanActivate rejection in that sampled state; it does not distinguish an input-buffer swallow from Enhanced Input trigger/context reset.

On the actor's first dodge input only, `URPGDodgeTiming` now saves the reachable CanActivate result and press game time. After at least one later game tick, it checks whether the ability is still inactive. If and only if this was press 1, CanActivate was true, the ability is still inactive, and no fallback has already been attempted, it calls the pack ASC's `Try Activate Ability by Class` with the existing `GA_Player_Dodge` class and `bForceActivation=false`. The one-shot guard is set before the reflected call. If the activation succeeds (or the ability becomes active), it marks the buffered `InputTag.Dodge` press consumed using the same pack API already used by the roll path, to prevent a delayed duplicate. No second activation is issued when the ability became active naturally. Later presses, false/unreadable CanActivate results, and active abilities do not take this fallback.

Development log `first_dodge_activation_retry` reports the selected path, method/return reachability, activation result, post-call active state, buffer-consume result and `force=0`. Existing first-press traces retain all CreatedAbilities flags, owned tags and stamina. The original input-buffer path's own TryActivate return is still not directly exposed by the input callback.

## Test-first and validation

- Added `RPGDodgeActivationRules::ShouldRetryFirstPress` and native automation `OneBossFight.Dodge.FirstActivationRetry` for eligible, later-press, CanActivate-false, already-active and already-attempted cases.
- Added `Scripts/Tools/test_dodge_first_activation_retry_contract.py`; it failed before the rule/source existed, then passes 2/2 after the guarded retry and Development log were authored.
- Python syntax, focused contract, and `git diff --check` pass. No C++ compile/native run by Codex.

## Lead validation and remaining acceptance

BUILD-263 built successfully and the full native suite passed 486/486. Lead C-1067 reports the fresh both-route standing/moving first-use matrix passed, repeats were normal, and there was no duplicate activation. KI-199 is closed for PIE. Keep package proof open, and reopen the issue if a first-use failure or delayed duplicate recurs; the original InputBuffer/trigger/context mechanism remains unisolated.

## AO-C21–C25 diagnostic follow-through

No new Lead root-cause readback has arrived. Codex's offline diagnostic handoff adds only `Get Buffered Input Tag` and current montage-position observations to the existing no-assignment probe. It does not expose the notify state's live InputBuffer window, both Enhanced Input trigger phases, or active mapping-context changes. It adds no new action binding, activation call, context mutation, montage assignment, or input delay; KI-199 remains unchanged. See `AO_C21_C25_FIRST_DODGE_DIAGNOSTIC_HANDOFF.md`.
