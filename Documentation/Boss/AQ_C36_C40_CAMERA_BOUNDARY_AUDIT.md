# AQ-C36–C40: camera probe and option boundaries

**Scope:** static source and document audit for the maintained PIE probe and the proposed camera options. No Editor, PIE, build, or package run was performed for this audit. Runtime evidence cited below is Lead-reported in C-1088–C-1091; it is not independently reproduced here.

## C36 — what the probe measures

- `Scripts/Editor/pie_camera_engage.py:103–118` checks visible boss `SkeletalMeshComponent` world AABBs through `SystemLibrary.get_component_bounds`; it does not inspect rendered pixels, depth, transparency, or perceptual visibility. An AABB hit is a bounds-occupancy proxy.
- `Scripts/Editor/pie_camera_engage.py:121–125` checks a camera point against an upright radius/half-height capsule approximation without the C++ option's enter/exit margins. `RPGCameraRig.cpp:51–66, 212–213, 252–253` uses an oriented capsule segment and hysteresis margins instead. The probe's capsule metric is not a direct reproduction of B's production predicate.
- `Documentation/Boss/CAMERA_MELEE_OCCLUSION_PROPOSAL.md:34–36` defines the earlier bounds telemetry as approximate and explicitly says it is not a rendered-pixel verdict. The newer maintained probe adds AABB/capsule sample counts; neither establishes actual occlusion or game-view readability.
- `pie_camera_engage.py:164–252, 271–300` is an active PIE driver, not a passive observation-only tool: it starts PIE, changes camera CVars, moves/places the pawn, changes control rotation for modes, and can inject `IA_Look` or start tracker moves. Its telemetry helpers (`attack_band_metrics`, `mesh_inside`, `capsule_inside`, `sample`) only collect/aggregate observations; this distinction is now covered by the C37 AST contract.
- C-1090's results apply to the exact BUILD-269 attack-mode A4/A6 case on both routes reported in C-1090. The matrix records default `CAM_SPEED=1.0`, no look injection, and pending nonmatching rows in `AQ_C11_C15_BC_MATRIX.md:26–49`. Tracker starts and zero sampled geometry-proxy intrusions do not prove contact, damage, full-frame visibility, or every attack/lunge timing.

## C37 — telemetry side-effect contract

`Scripts/Editor/test_pie_camera_engage_contract.py:test_telemetry_helpers_do_not_mutate_world_assets_or_global_camera_state` parses the maintained probe and rejects world/control/input/attack/save/CVar mutation calls inside its four telemetry/aggregation helpers. Existing whole-file checks also reject editor-property and asset-save APIs. The test intentionally does **not** assert that `drive` or `tick` are side-effect-free; those functions must configure and run the Lead-owned PIE scenario.

## C38 — B hide scope

- `Source/OneBossFight/Player/RPGCameraRig.cpp:179–185` requires a valid local `APlayerController`; lines 285–290 add eligible boss mesh primitives to that controller's `HiddenPrimitiveComponents`, and lines 307–315 remove only entries this rig added.
- The implementation filters to registered, visible `USkeletalMeshComponent` or `UStaticMeshComponent` primitives (`RPGCameraRig.cpp:236–250`). This is local-viewer mesh hiding. It does not establish Niagara/aura/telegraph visibility, replicated or multiplayer behavior, nor visibility on another player's view. Those checks remain open in `CAMERA_MELEE_OCCLUSION_PROPOSAL.md:14,18`.

## C39 — C angle definitions and windows

- In `pie_camera_engage.py:136–155`, `yaw_gap` is the wrapped absolute difference between camera world yaw and controller control yaw. `boss_off` is the wrapped absolute difference between camera world yaw and the horizontal player-to-boss bearing. These are yaw-only angular proxies; they are not full 3D view direction or a targetability/readability score.
- The runner schedules sampling when game time reaches `next_sample`, then advances that deadline by 0.1 game seconds (`pie_camera_engage.py:246–251`). This is a game-time sampling target, not a guarantee of exact wall-clock cadence.
- The summary field `boss_off_last10_avg` averages only the final ten recorded `boss_off` samples (`pie_camera_engage.py:263–267`); it is not a run-wide median or p90. The C-1088 medians/p90 and C-1090 median are separate Lead-reported run statistics, not values computed by this summary field.
- C-1088's C-only route/speed/look-input runs and C-1090's single tested B+C attack-mode case are distinct evidence. C-1090 reports the combined case's 36–37° view-to-boss **median** on both routes; all other matrix rows, broader scenarios, and package behavior remain unverified (`AQ_C11_C15_BC_MATRIX.md:26–49`).

## C40 — disposition and limits

The current source and proposal support only a Development PIE experiment with explicit local geometry and yaw proxies. Option choice remains with the owner; no selected shipped default, Shipping inclusion, package proof, aura/telegraph readability finding, or multiplayer claim follows from this audit. Lead owns live PIE and packaged validation. No runtime/source or asset files were changed by this batch.
