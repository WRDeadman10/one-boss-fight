# Queue AM C01–C05: melee camera diagnostic

C-1030 Lead and A-628 describe an extreme close-up at about 105 cm player-to-boss distance in the BUILD-255 full-fight video. A-628 saw a cleaner backstep at 212 cm (`FIGHT_VIDEO_REVIEW_AG.md:13,24`). The observation does not identify a blocking collision primitive. `RPGCameraRig.cpp:50–52` enables the spring-arm camera probe at its configured size/channel (native defaults 34 cm, `ECC_Camera`), and `RPGBossLook.cpp:74,123` disables collision on the displayed follower body/mantle/sword. The boss capsule or camera sightline remains a live hypothesis, not a proven cause.

`Scripts/Editor/pie_camera_melee_occlusion.py` is a Lead-only read-only probe. It places the player at nominal 105, 200 and 300 cm on the boss-facing axis, waits for the camera to settle, then logs actual horizontal separation, spring-arm target/probe properties, pivot and camera locations, actual pivot-camera distance, boss capsule Camera response, candidate sphere-trace hit, and PlayerCameraManager pose. It uses `pie_lead_common`. If UE Python does not expose the spring arm's unfixed camera position, the probe labels a no-offset approximation; a property or trace read error is logged instead of silently claiming no hit. No collision setting changes.

Offline verification: `python -m unittest Scripts.Editor.test_pie_camera_melee_occlusion_offline` passes 3/3 (horizontal geometry, 105 cm placement facing, explicit finished marker); `python -m py_compile Scripts/Editor/pie_camera_melee_occlusion.py` passes. `RunLeadPie.ps1` two-route `-DryRun` printed both `-nosound` commands, route selection and stop marker, with no Editor/lock/output mutation.

Lead command from the project root (when ENGINE_LOCK is free):

```powershell
& .\Scripts\RunLeadPie.ps1 -Script Scripts/Editor/pie_camera_melee_occlusion.py -Routes @('legacy','data') -OutputDir Docs/BossCombatReview/Execution/Claude/P_AM_CAMERA -StopMarker '[MeleeCamera] finished:'
```

Review each `SAMPLE`, `BOSS_CAPSULE`, `PROBE` and `CAMERA_MANAGER` line at 105/200/300 cm. If `PROBE` is unreadable, add a scoped C++ Development debug hit log before selecting the production change. Only a trace-supported result can choose capsule Camera-ignore versus close-distance framing. The arena wall/floor collision test remains mandatory after any camera Source fix.
