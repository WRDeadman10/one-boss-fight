# Known Issues

| ID | Area | Description | Workaround | Status |
|---|---|---|---|---|
| KI-001 | Toolchain | UBT warns "Visual Studio 2022 compiler is not a preferred version" (MSVC 14.51, VS 2026). Build succeeds. | Install MSVC 14.38 (17.8) if a later build fails | Open |
| KI-003 | Performance | Benchmark PC has an RTX 3060, not the target RTX 2060 Super; baselines are not target-hardware results | Re-measure on a 2060 Super if available | Open |
| KI-004 | Performance | Project defaults (Lumen, VSM) give 94-97 FPS avg and unstable p99 at 1080p in the empty arena | Use the `gi_off` settings via config in M6 | Open |
| KI-005 | Input | Look direction/sensitivity not yet playtested (`bEnableLegacyInputScales=False`, raw mouse, `LookSensitivity=1`) | Tune `LookSensitivity` or flip sign in IMC | Open |
| KI-006 | Content | Player used the engine tutorial mannequin as a placeholder | Replaced by Greystone in M3 | Closed (M3) |
| KI-002 | Build | ~68 C4996 deprecation warnings from engine headers (UE 5.5 API deprecations) | Ignore; not project code | Open |
| KI-007 | Animation | No dodge animation exists in any chosen pack. Dodge runs as a code-driven dash with timed i-frames (no montage); the character slides while the locomotion pose plays | Retarget or author a roll (M3 follow-up) | Open |
| KI-008 | Animation | Heavy attack uses `Attack_RMB`, a 3 s ability with a long wind-up; it feels too slow for a heavy swing. Light combo montages are 0.8-1.9 s | Pick another heavy source (`Attack_*_Slow`) or raise `PlayRate` in `DA_Weapon_GreystoneSword` | Open |
| KI-009 | Animation | Greystone's own AnimBP drives attacks through its Paragon character Blueprint (cast fails on our character). Montages play only through its `UpperBody` slot, and the whole body is used only while the animation's `FullBody` curve is active and the character is not accelerating | Own AnimBP in the polish milestone | Open |
| KI-010 | Input | Lock-on target switching uses a mouse flick (`SwitchFlickThreshold`, raw delta per frame). Gamepad stick switching is not implemented | Add a dedicated switch action | Open |
| KI-011 | Content | Paragon `GreystonePlayerCharacter` had a compile error (VR reset node) that made Play-In-Editor show a blocking dialog. The node was deleted in the (git-ignored) pack asset. A fresh Fab download restores it | Delete the node again, or delete the unused BP together with the pack | Workaround applied |
| KI-012 | Tooling | `Scripts/Editor/pie_combat_smoke.py` needs the editor window in the foreground and the editor started with `-unattended` (otherwise PIE stops on a modal dialog) | Run as documented in the script | Open |
| KI-013 | Boss | No 3-hit combo and no real lightning: Sevarog has no chained montage and no lightning VFX yet (`Lightning` is a radial hit using `Cast`; combo needs a multi-segment montage) | Add in M5 with VFX | Open |
| KI-014 | Boss | Boss walks by direct steering without a navmesh, so it can snag on arena pillars | Add NavMeshBoundsVolume and AI MoveTo if it happens in playtests | Open |
| KI-015 | Boss | Attack ranges, windows and damage are first-pass numbers; hit windows come from scythe tip speed | Tune in playtest | Open |
| KI-016 | Boss | Phase roar uses `Ultimate_Targeting` as a stand-in animation | Replace with a real roar if one is found | Open |
