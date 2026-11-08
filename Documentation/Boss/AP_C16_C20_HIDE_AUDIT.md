# Queue AP-C16–C20 — HideBossInside audit

**State:** offline audit/contract work complete; Lead build and both-route visual acceptance pending.

## API and behavior audit

The owner wording from C-1051 is preserved exactly in `CAMERA_MELEE_OCCLUSION_PROPOSAL.md`: “hide/dither the boss mesh when the camera is inside its bounds.” UE 5.5.4's `APlayerController::HiddenPrimitiveComponents` is documented in the engine header as a camera-local primitive visibility list. The hide switch uses that per-controller list, filtered to visible boss skeletal/static mesh primitives. This avoids global actor visibility changes and leaves collision and non-mesh Niagara/particle primitives untouched. The current single-player route is supported; two local viewers would need a separate run for each camera, while remote/network view behavior is not claimed.

`URPGBossLook` uses boss-owned skeletal followers for the body and static mesh sword, so the filter covers both primitive mesh types. Attached weapon geometry is hidden with the boss visuals; non-mesh aura/telegraph primitives stay rendered. An unreadable/nonfinite bound or camera position restores the entries this rig added. Existing hidden-list entries are not removed by this rig. The design has no damage, movement, trace, collision, input, or authored asset writes.

The enter test uses component bounds contracted by the proposed 5 cm margin; the exit test expands bounds by 5 cm. AABB comparisons are inclusive at each resulting boundary. These values aim to prevent flicker but are provisional and can hide slightly after the camera first enters the raw mesh bounds; visual timing and framing remain a Lead acceptance item. Do not present them as owner-approved tuning.

## Offline evidence and runtime gate

Combined BossBlocks and HideBossInside source contracts pass 15/15. Hide-specific cases cover the finite bounds and camera point, inclusive enter/exit math, separate margins, local-controller-only component list, mesh-only filtering, target/controller/EndPlay restoration, and absence of global visibility or collision/gameplay calls. `py_compile` passes for both contracts, repository doc links are clean, and `git diff --check` reports no whitespace errors apart from the existing LF/CRLF notices. These checks do not prove runtime rendering or the visual quality of the margins.

Lead's legacy/data run matrix is in `AP_C11_C15_HIDE_BOSS.md` and the corresponding `TEST_PLAN.md` entry. In addition to mesh visibility, record phase-two aura/telegraph visibility, hit feedback, player silhouette, wall/floor interactions, toggle-off while inside, and cleanup after reset and EndPlay. Keep KI-037 and KI-066 open until those observations are reviewed. No camera option is owner-selected.
