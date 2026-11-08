# Queue AP-C06–C10 — BossBlocks audit and Lead run sheet

**State:** offline source audit and contracts complete; native build and PIE are Lead-owned and pending.

## Contract check

C-1051 option A says: “the boss capsule blocks ECC_Camera (the arm shortens instead of entering the mesh).” The implementation changes only the identified pack boss `UCapsuleComponent` response for `ECC_Camera`; the existing `USpringArmComponent` collision sweep remains enabled. The experiment does not change the boss mesh, player capsule, Visibility channel, authored spring-arm length, probe size, or wall/floor response. The reference 34 cm probe and camera-channel wall/floor behavior still need live verification.

While `rpg.Camera.BossBlocks` is enabled, the rig resolves the pack boss on each camera-rig tick. This covers replacement by a new actor even when the old weak pointer still refers to a live component. The iterator yields `APawn`, so the implementation explicitly casts the recognized pack boss to `ACharacter` before requesting its capsule. On target change it restores the old capsule's saved response before capturing the new one. On no target, switch-off, or EndPlay it restores where the capsule is still valid and still has the option's Block response. Weak object validity and owner-null logging avoid dereferencing destroyed objects. When disabled, the method returns before enumerating actors.

The current project helper recognizes the pack boss Blueprint class (`URPGPlayerMovesSubsystem::IsPackBoss`); it is not a generic “nearest enemy” rule. The passive probe reports each boss capsule's `ECC_Camera` response, actual camera and pivot positions, actual spring-arm length, approximate sweep component, and camera-in-mesh AABB. The approximate sweep is explicitly not authoritative due to omitted socket/target offsets in the current UE Python API. The probe does not move the player, enable the switch, or capture the full wall/floor/timing safety matrix by itself.

## Lead run matrix

Run on **legacy** and **data** with one fresh build identity per route. In each route, keep the passive probe running and manually circle left and right:

| Pass | CVar | Expected check |
|---|---:|---|
| Baseline | `rpg.Camera.BossBlocks 0` | Existing behavior; log camera AABB, arm actual/target, capsule response, wall/floor and player safety. |
| Experiment | `rpg.Camera.BossBlocks 1` | Boss capsule reports Block; arm shortens before the camera enters the mesh. Check 150–250 cm circling, 105 cm, recovery, attacks, dodge and aura. |
| Restore | `rpg.Camera.BossBlocks 0` | Original boss capsule response is restored and baseline behavior resumes. |

Repeat wall and floor approaches with the option both off and on. Capture the player's full body and boss silhouette around melee; record minimum camera/player separation, not only camera-inside state. Preserve logs, video/frame captures, route, build identity, and CVar commands in `Documentation/Boss/CAMERA_DYNAMIC_BASELINE_RECEIPT_TEMPLATE.md`. Stop/mark the case unreadable if the probe reports unreadable bounds or response; do not infer the hit component from its approximate sweep field alone.

## Offline contract results

`Scripts/Editor/test_camera_boss_blocks_contract.py` checks the switch guard and default, off-path early return, project-boss `ACharacter` capsule only, saved-response restore, and per-tick re-resolution instead of trusting a still-live cached target. The target-revalidation contract failed before the AP-C06–C10 change; the character-capsule contract then caught an invalid `APawn::GetCapsuleComponent()` call in the new path, which was corrected with the explicit character cast. All focused contracts pass afterward. These Python source contracts do not substitute for C++ compilation, Unreal collision evaluation, or Lead PIE evidence.
