# C-1043 Lead probe script hotfix

Status: both Python failures corrected offline; Lead rerun pending.

- A4 guard counter: C-1043's first run reached the weapon draw style change but failed the fixed 2.5-second readiness assertion. `pie_er_a4_guard_counter.py` now polls until both `RPGBuildLoadout.is_combat_enabled()` and no active player montage hold, with a five-real-second window and up to three R2 draw attempts. It logs readiness per attempt. No synthetic guard arm or runtime montage assignment was added. The underlying real A4 IA_Block/R2/montage/HP gate is unchanged.
- Camera: C-1043's first run raised on `get_component_location`. `pie_camera_melee_occlusion.py` now reads `get_world_location()` from the named `CameraBoom` and `FollowCamera`, as the existing `pie_camera_scenarios.py` and `pie_cam_probe.py` already do. Camera-manager readback is explicitly labeled `UNREADABLE` if unavailable. The sphere trace and camera-manager getters are used in existing camera probes; the desired arm endpoint is explicitly approximate from control yaw and target length because the unfixed getter is not exposed. Capsule collision-response calls stay caught and labeled, so they cannot crash the snapshot.
- Validation: focused fake-Unreal tests 5/5 (including draw readiness and named camera world-location selection); both scripts compile; both two-route RunLeadPie dry runs use `-nosound` and valid stop markers. Codex did not run Editor, PIE, build or package.

```powershell
& ./Scripts/RunLeadPie.ps1 -Script Scripts/Editor/pie_camera_melee_occlusion.py -Routes @('legacy','data') -OutputDir Docs/BossCombatReview/Execution/Claude/P_C1043_CAMERA_R2 -StopMarker '[MeleeCamera] finished:'
& ./Scripts/RunLeadPie.ps1 -Script Scripts/Editor/pie_er_a4_guard_counter.py -Routes @('legacy','data') -OutputDir Docs/BossCombatReview/Execution/Claude/P_C1043_A4COUNTER_R2
```

The first C-1043 run remains a script-level failure, not a gameplay verdict. KI-198 and the camera collision diagnosis remain open until raw rerun evidence is reviewed.
