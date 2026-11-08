# Queue AP-C11–C15 — local HideBossInside option

**State:** source and offline contracts complete; Lead native build and legacy/data PIE pending.

## C-1051 option B scope

C-1051's exact owner option is “hide/dither the boss mesh when the camera is inside its bounds.” The implementation uses `rpg.Camera.HideBossInside`, guarded outside Shipping and default `0`. It checks the active FollowCamera location against finite bounds for visible boss skeletal/static mesh components. Unreadable or nonfinite bounds fail safe by restoring the rig's local hide entries. Entry begins 5 cm inside the bounds and exit occurs 5 cm outside; these are proposed anti-flicker margins for Lead validation, not owner-approved camera tuning.

The engine's `APlayerController::HiddenPrimitiveComponents` list is explicitly per-controller. The rig adds only visible boss skeletal/static mesh primitives missing from that list, tracks those additions with weak pointers, and removes one matching entry per addition on switch-off, target/controller replacement, unreadable geometry, leaving the bounds, or EndPlay. Existing entries owned by other systems are not claimed or removed. It does not call `SetActorHiddenInGame`, `SetHiddenInGame`, or alter collision. Particle, Niagara, aura, and other non-mesh primitives are excluded. Both camera switches can be independently enabled; the default remains off.

## Test-first evidence

`Scripts/Editor/test_camera_hide_boss_contract.py` was written first and failed all five contracts before source changes. It now checks default-off/non-Shipping, controller-local primitive hiding, no global hide calls, finite bounds with distinct margins, off/unreadable cleanup, and tracking/restoration on EndPlay or target change. Further audit added inclusive boundary, mesh-only filtering, no gameplay/collision side effects, and independent-switch cleanup coverage. Combined BossBlocks and HideBossInside source contracts pass 15/15. This does not establish how the engine renders the local hidden list in PIE or prove the chosen margins are visually adequate.

## Lead acceptance

On legacy and data, capture baseline with `rpg.Camera.HideBossInside 0`, then enable `1` while circling at 150–250 cm in both directions. Cover close contact at 105 cm, standing, recovery, dodge, attacks, phase-two aura, wall and floor. Confirm the boss mesh becomes invisible only in the local camera when the camera enters the bounds, and returns after exiting; verify aura/telegraphs, hit feedback, collision, other actors, player framing and both route modes remain intact. Toggle `1 -> 0` while inside, replace/reset the boss while hidden if possible, and end PIE; ensure all rig-added component entries are removed. Record route/build, samples, screenshots/video, unreadable-bound cases, and CVar commands in the camera receipt template. C-1081's orbit-only run recorded 0 inside-AABB samples with HideBossInside enabled, so the option did not trigger and remains unproven. C-1080 accepted its prior code/build review; the transition-log hotfix below needs a fresh Lead build and runtime trigger. KI-037/KI-066 stay open.

## C-1080/C-1081 transition-log hotfix

Added one `HideBossInside enter` log when the local mesh hide state first becomes active and one `exit_or_restore` log when that state ends. Both lines include mesh component count and camera-to-boss distance. A state flag gates the logs to transitions, so per-tick update does not spam. Lead BUILD-266 accepted the prior code (487/487) but found that the orbit probe did not trigger hide; rebuild and an attack/lunge-overlap PIE capture are required before B can be considered exercised.
