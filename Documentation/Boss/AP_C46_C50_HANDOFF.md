# Queue AP-C46–C50 — final offline handoff

**Offline queue:** complete. **Lead build/runtime:** BUILD-268 passed the B retreat case; BUILD-269 passed C lock-on framing in PIE on both routes. **Owner choice:** pending; B and C individually ready for review, B+C not tested together.

## Queue and implementation census

`QUEUE_AP.md` contains exactly 50 unique ordered task IDs, AP-C01 through AP-C50, arranged as ten five-task batches. The source adds three independent `#if !UE_BUILD_SHIPPING` cvars, all default `0`: `rpg.Camera.BossBlocks`, `rpg.Camera.HideBossInside`, and `rpg.Camera.LockOnFraming`. Their helpers and restoration state are separate. The existing camera safety path remains in place. No final camera default or owner selection is claimed.

Source/tests: `Source/OneBossFight/Player/RPGCameraRig.cpp`, `RPGCameraRig.h`; passive probe `Scripts/Editor/probe_camera_inside_boss.py`; five focused contracts: `test_camera_boss_blocks_contract.py`, `test_camera_hide_boss_contract.py`, `test_camera_lock_on_framing_contract.py`, `test_camera_options_independence.py`, and `test_probe_camera_inside_boss.py`.

## Offline checks

- Combined camera-source contracts: 30/30.
- Passive probe contracts: 4/4.
- Combined focused tests: 34/34.
- `py_compile`: passed for the probe and five supporting test files.
- `check_doc_links.py .`: `broken_links=0`.
- `git diff --check`: no whitespace errors; Git reports existing LF/CRLF conversion notices.
- Queue census: 50 IDs, 50 unique, ordered 1–50.

These checks do not replace C++ compilation or visual, input, collision, package, or owner acceptance.

## Lead evidence

- C-1080: prior HideBossInside implementation accepted after BUILD-266 GREEN 487/487; visual check pending.
- C-1081: awake-boss 30-second orbit, 115–280 cm player distance, 60 deg/s camera yaw, both routes. OFF: 0 inside-AABB samples, arm minimum 320 cm. BossBlocks: legacy 30/252 and data 28/251 inside samples, arm 10–108 cm; Lead recommends dropping A for this tested orbit. HideBossInside: 0 inside samples, arm minimum 320 cm, but no trigger was observed, so B remains unproven. The boss capsule was never entered; attack/lunge overlap remains required. LockOnFraming has no Lead result.
- C-1082 directed BUILD-267 after the worktree settled; Claude then reported BUILD-267 GREEN 487/487 in C-1083 and ran both-route 30-second away/fixed PIE. HideBossInside logged 14 legacy and 25 data enter/exit pairs but triggered too often because the component AABBs include large mantle/sword bounds. LockOnFraming kept the boss aligned to the boom (5–6 degree average last-10 yaw error versus 74–78 off), but boom yaw diverged up to 165 degrees from ControlRotation.
- C-1083 accepted the code and requested two behavior changes. Codex now uses the boss capsule grown by 5 cm to enter and 10 cm to exit, with a 0.35-second minimum local hide duration. Transition-only enter/exit logs remain. LockOnFraming now applies rate-limited yaw to PlayerController ControlRotation at 120 degrees/second after the existing 0.35-second manual-input grace; the spring arm remains on `bUsePawnControlRotation`, so movement and view share yaw. All new values/behavior require fresh Lead validation.

## C-1083 hotfix verification boundary

- Test-first source contracts were updated for capsule geometry, wider exit hysteresis, minimum hide duration, controller-yaw ownership, and spring-arm mode restore. The two focused contracts plus cross-option independence pass 25/25; all five camera/probe files pass 36/36.
- Codex did not run native build, Unreal, PIE, or package verification. C-1083 requests BUILD-268 then the away/fixed rerun on both routes.

## C-1085 lock-on input follow-up

- C-1085 reports BUILD-268 GREEN 487/487. HideBossInside passes both routes: the new retreat scenario generated 18/24 capsule-overlap samples with options off; B entered only at 20–58 cm from the boss center and produced 11/13 hides per 30 seconds, each 0.35–0.43 s, with no distant false triggers or blinking. B is ready for owner review.
- C-1086 corrected the earlier diagnosis: ControlRotation stayed at 150° for the full 30 seconds, with no other writer. The measured 45° per 0.2 s boss-bearing swing came from the driver's 180°/s sprint orbit at 185 cm radius; the old 120°/s cap could not keep up.
- Source search found no per-tick player camera yaw writer or AddControllerYawInput/AddYawInput call. The only unrelated production `SetControlRotation` is riposte alignment in `RPGBossStagger.cpp`; `RPGCameraProbe.cpp` contains a synthetic test write. Lead's asset readback identified `BP_CameraModeComponent_C`, `BP_TargetingComponent_C`, and `BP_AdvancedPlayerController_C`; none changed control in that run.
- Codex's C-1085 fix reads the pack's `IA_Look` Axis2D action value from `UEnhancedPlayerInput`; magnitude above 0.25 keeps a 0.35 s manual grace. Missing action/input fails open to the authored camera. C-1086 replaces the 120°/s ceiling with error-proportional `FixedTurn` speed `clamp(abs(yaw error) * 6, 60, 360)` degrees/second (270°/s at 45° error), preserving shortest-path bumpless follow. Its five focused camera/probe files passed 39/39 after the orbit contract was added. BUILD-269 status below supersedes the pending runtime state recorded in the initial C-1086 handoff.
- C-1088 reports BUILD-269 GREEN 487/487 and C passing PIE on both routes. View-to-boss error: median 14° walk / 27° sprint, p90 25–37°; off median 82–90°, p90 154–164°. A 1 s injected IA_Look moves control 35° with C on, same as off; after that input, error reacquired from 63–114° to 14–24° in about 2 s. C-1090 later tested B+C in one attack-mode case on both routes: 9 A4/A6 starts and zero refusals per run; 0 intrusion samples and 36–37° view-to-boss median. Broader combined scenarios and package behavior remain open. Owner choice remains pending. The owner-facing comparison and no-code production promotion plan are in `CAMERA_MELEE_OCCLUSION_PROPOSAL.md`; no source changes to `RPGCameraRig` until the owner picks.

## Remaining gates

1. Claude builds the C-1083 hotfix as BUILD-268 and reruns away/fixed on both routes, validating capsule margins, minimum duration, enter/exit logs, and reduced toggles.
2. Claude reviews LockOnFraming manual input, pitch, movement/dodge alignment, target-loss and feel behavior in PIE; confirm no snap when manual grace ends.
3. Keep the BossBlocks orbit regression in the report; it is not evidence for attack/lunge behavior.
4. Owner selects the final camera behavior. All options are presently under `!UE_BUILD_SHIPPING`; selected behavior/configuration must leave that guard and receive separate package proof before any Shipping claim. No code move is included in Queue AP.

The proposal and test matrix contain the exact C-1081/C-1083 measurements and current follow-up. No build, Editor, PIE, package, commit, or push was run by Codex.
