# Queue AP-C41–C45 — camera switch regression audit

**State:** offline audit complete; HideBossInside transition-log hotfix is ready for a fresh Lead build. No new build or PIE was run by Codex.

## C-1080/C-1081 feedback applied

- C-1080 accepted X-1507/X-1508 code review and BUILD-266 (487/487). Visual validation remained pending. Claude requested transition-only HideBossInside enter and exit/restore logs containing mesh component count and camera-to-boss distance.
- C-1081 supplied the BUILD-266 orbit result and requested an owner-proposal update. With options off: 0 camera-inside-boss-mesh AABB samples and 320 cm minimum spring arm on both routes. BossBlocks=1: 30/252 inside samples on legacy and 28/251 on data; arm length fell to 10–108 cm, snapping into the player and boss mesh. Lead recommends dropping A based on the tested orbit. HideBossInside=1: 0 inside samples and 320 cm minimum arm, but it did not trigger, so B remains unproven. The capsule was not entered in those runs; attack/lunge overlap is not tested. LockOnFraming's lead build, manual-input and feel run are pending.
- Added the requested `HideBossInside enter meshes=... camera_to_boss_cm=...` and `exit_or_restore` messages. The state flag gates them to transitions, not per-tick logs. The fresh build and a lunge-overlap run are pending.
- Updated `CAMERA_MELEE_OCCLUSION_PROPOSAL.md`, the AP option matrix, `TEST_PLAN.md` and `KNOWN_ISSUES.md` with exact route counts, limits, and open gates. The proposal now states the C-1078 source-experiment authorization and preserves the owner's unselected A/B/C question.

## Cross-option audit

All three CVars remain distinct, Development-only, and default 0. Their apply functions mutate only their named state, and cleanup handles disable, target/owner loss and EndPlay. The camera's existing wall/floor spring-arm sweep stays enabled. Hide uses local primitive list membership; BossBlocks saved-response restore and LockOnFraming original spring-arm mode are separate. No owner default is selected.

The per-switch values (5 cm bounds margins, 0.35 s manual grace, 120 deg/s turn cap) are documented as provisional. All runtime/feel assertions remain bounded by actual test coverage; the BossBlocks orbit regression is not generalized to lunge cases, B is not called successful absent a transition log, and C has no Lead result.

## Packaging caveat

All three switch declarations and behavior paths currently sit under `#if !UE_BUILD_SHIPPING`, so C-1080/BUILD-266 proves only Development compilation. If the owner selects a behavior, the selected code/config default must be moved out of the Development-only guard and package proof repeated under a separate reviewed change. No such code move is made or authorized by the current option-comparison order. The dynamic probe is Editor-only; the Development-package matrix has no executable driver.

Focused camera-source contracts pass 30/30 after adding the transition assertions; the passive camera-probe contract passes 4/4; the combined focused set passes 34/34. `py_compile` passes, doc links=0, and `git diff --check` has no whitespace errors (existing line-ending conversion notices only). No Codex C++ build, native suite, Editor, PIE, package or commit/push.
