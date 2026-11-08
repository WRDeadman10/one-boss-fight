# Queue AM C41–C45: melee camera decision

## C41: collision branch closed by Lead trace

Lead C-1044 ran `pie_camera_melee_occlusion.py` on legacy/data. `P_C1043_CAMERA/probe_legacy_lines.txt:1-12` and its data counterpart show nominal 105, 200, 300 cm samples with target arm 370 cm, pivot-to-camera ~375 cm, `sphere_trace=None`, and boss capsule `ECC_Camera=IGNORE`. The probe's desired endpoint is an explicitly labeled no-offset approximation, and the capsule `collision_enabled` property was unreadable. The actual full arm and capsule channel response support Lead's conclusion: boss collision does not retract the camera on this open-ground lane. The conditional boss collision Source fix is not applicable; Lead ordered no camera production change.

## C42: retained floor/wall safety contract

`RPGCameraRig.cpp:48-53` keeps `bDoCollisionTest=true`, `ProbeSize=34` cm and `ECC_Camera`. `:117-124` restores the test/size if pack logic changes them. `RPGCameraRig.h:32-49` sets the camera probe and pitch limits; `RPGAutomationTests.cpp:1294-1297` asserts probe >=25 cm and pitch bounds. `OneBossFight.Arena.Collision` checks floor, pillar, and boundary wall via `ECC_Visibility`, which is not direct `ECC_Camera` evidence. `pie_camera_clip.py` has a separate floor/movement camera safety scenario; no new run was made for this batch. This audit retains the existing safety trace without claiming wall/floor Camera-channel verification from the open-ground C-1044 result.

## C43–C45: status and gate

`CAMERA_MELEE_OCCLUSION_PROPOSAL.md` records the ruled-out boss-capsule branch and Lead's no-change decision. The BUILD-255 fight video still has wall/pillar close-ups and boss fill; an optional composition pull-back or lock-on adjustment requires owner direction and 105 cm, wall, floor, dodge, phase-two visual checks. KI-037 framing and KI-066 broader camera coverage stay open. No Source change, build, PIE, or owner visual acceptance is claimed by Codex in this batch.
