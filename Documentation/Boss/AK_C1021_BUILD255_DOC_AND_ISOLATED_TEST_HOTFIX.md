# C-1021 — BUILD-255 documentation and isolated test import

Lead reported that the owner approved the seven-clip reel and ordered implementation. BUILD-255 passed 484/484 after `URPGDodgeTiming` Source defaults were set to four `AM_ER` montage paths and the pack-wiring/native offline contracts were updated. The Lead holds `ENGINE_LOCK` for full-fight capture; Codex did not use the engine.

The offline suite timing test imported `Scripts.Tools.run_offline_suite_timed`, which fails when `python -I -m unittest discover -s Scripts/Tools` omits the repository root from `sys.path`. The test now accepts both package import and isolated discovery from `Scripts/Tools`. The focused five tests pass under both commands. No production Source changed.

Updated current status in `ER_PLAYER_CONTROLS_SPEC.md`, `GATE07_ANIMATION_REVIEW.md`, `AA_A08_NOTIFY_FRAMES_TABLE.md`, `CONTROLS_STATUS.md`, `PROJECT_STATE.md`, `DECISIONS.md`, `KNOWN_ISSUES.md` and `TEST_PLAN.md`. Historical C-975/C-1004 runtime-assigned evidence is labeled as such. The owner approval and Source default wiring are complete; fresh PIE and package proof of the default-wired game remain open. KI-193 stays open for those gates, and KI-194 remains resolved only for its pre-wiring tested routes. KI-196/KI-198 are unchanged pending their separate Lead evidence.

Validation: focused isolated and package-mode test imports passed 5/5 each; scoped `git diff --check` passed. No Unreal/PIE/build/commit by Codex.
