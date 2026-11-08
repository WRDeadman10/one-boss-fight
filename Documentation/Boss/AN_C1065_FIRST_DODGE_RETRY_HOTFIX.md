# C-1065: First Dodge Activation Retry Hotfix

Status: BUILD-263 compiled and the full Lead suite passed 486/486. The retained `P_SHOWCASE/showcase_def4.log` shows the reproduced first standing press after draw entering the one-shot retry, `activated=1`, `active_after=1`, `buffer_consumed=1`, then `AM_ER_Backstep_Mixamo_V2` playing with root motion (83.9 cm total displacement by the end of rep 1); i-frames also activated. Reps 2 and 3 moved 80.2 cm and 98.8 cm. This validates the recovery on the retained showcase case, not the underlying pack InputBuffer/Enhanced Input/context cause, both-route/moving behavior, or absence of a delayed duplicate in all timing cases. KI-199 remains open. Evidence folder: `Docs/BossCombatReview/Execution/Claude/B_C1067_DODGERETRY/`.

## Evidence and bounded change

C-1065 BUILD-262 reports press 1 after draw with `GA_Player_Dodge_C active=0`, `CanActivate=1`, stamina 100, owned tags `{Player.Character, Equipped.Arrow}`, no blockers, and next-tick active still 0 / 0 cm. Presses 2/3 activate and move 96 cm. This rules out a CanActivate rejection in that sampled state; it does not distinguish an input-buffer swallow from Enhanced Input trigger/context reset.

On the actor's first dodge input only, `URPGDodgeTiming` now saves the reachable CanActivate result and press game time. After at least one later game tick, it checks whether the ability is still inactive. If and only if this was press 1, CanActivate was true, the ability is still inactive, and no fallback has already been attempted, it calls the pack ASC's `Try Activate Ability by Class` with the existing `GA_Player_Dodge` class and `bForceActivation=false`. The one-shot guard is set before the reflected call. If the activation succeeds (or the ability becomes active), it marks the buffered `InputTag.Dodge` press consumed using the same pack API already used by the roll path, to prevent a delayed duplicate. No second activation is issued when the ability became active naturally. Later presses, false/unreadable CanActivate results, and active abilities do not take this fallback.

Development log `first_dodge_activation_retry` reports the selected path, method/return reachability, activation result, post-call active state, buffer-consume result and `force=0`. Existing first-press traces retain all CreatedAbilities flags, owned tags and stamina. The original input-buffer path's own TryActivate return is still not directly exposed by the input callback.

## Test-first and validation

- Added `RPGDodgeActivationRules::ShouldRetryFirstPress` and native automation `OneBossFight.Dodge.FirstActivationRetry` for eligible, later-press, CanActivate-false, already-active and already-attempted cases.
- Added `Scripts/Tools/test_dodge_first_activation_retry_contract.py`; it failed before the rule/source existed, then passes 2/2 after the guarded retry and Development log were authored.
- Python syntax, focused contract, and `git diff --check` pass. No C++ compile/native run by Codex.

## Lead validation and remaining acceptance

BUILD-263 built successfully and the full native suite passed 486/486. The Lead showcase repro now passes the first standing case as summarized above. Still run `Scripts/Editor/probe_first_dodge_after_draw.py` fresh on legacy/data with `FIRST_DODGE_CASE=standing` and `moving`; require first moving quick-roll with press-time input/velocity and forward travel, repeated presses, and no buffered duplicate after the animation. Preserve logs and check the retry did not fire on an already-active ability. The underlying InputBuffer/trigger/context path remains unisolated. Keep KI-199 open until the broader route/case matrix and duplicate check pass.
