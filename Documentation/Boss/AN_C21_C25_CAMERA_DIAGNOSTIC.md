# AN-C21–C25: Dynamic Melee Camera Diagnostic

Status: source map, Lead-only telemetry and offline checks complete. Camera behavior/collision remains unchanged pending owner choice. Lead owns both-route PIE under `ENGINE_LOCK`.

## Static source map

- `Source/OneBossFight/Player/RPGCameraRig.cpp:35-58`: obtains `CameraBoom` and `FollowCamera`, attaches the boom to the player capsule when configured, and enforces collision probing (`bDoCollisionTest`, probe size and `ECC_Camera` channel). It does not configure or query boss collision responses.
- `RPGCameraRig.cpp:105-147`: restores capsule attachment after pack ragdoll/death reattachment, re-enables spring-arm collision if another system disables it, and draws optional debug geometry. No boss look/follower is hidden based on camera position.
- `RPGCameraRig.h:26-36`: default probe size is 34 cm and channel is `ECC_Camera`; `RPGCameraRig.h:69-74` stores the boom and camera references.
- `Source/OneBossFight/Player/RPGBossLook.cpp:66-86`: creates skeletal follower components, explicitly disables their collision and overlap, attaches them to the pack mesh and copies the leader pose. This makes follower render bounds a different question from spring-arm primitive hits.
- `RPGBossLook.cpp:88-111`: hides the pack body and pack weapon mesh for presentation, keeps the pack mesh ticking, and creates body/piece followers. `RPGBossLook.cpp:124-138` creates the visible sword as a no-collision static mesh attached to the body socket. `RPGBossLook.cpp:149-178` tears down followers and restores pack visibility.
- `CAMERA_MELEE_OCCLUSION_PROPOSAL.md` records C-1044's open-ground samples (capsule `ECC_Camera=IGNORE`, no trace hit) and limits that evidence; C-1051's dynamic mantle/legs intrusion requires its own runtime baseline.

## Probe and acceptance boundary

`Scripts/Editor/probe_camera_inside_boss.py` provides a bounded per-tick dynamic sample and does not set actor locations, camera properties or collision. During its 30-second window the Lead must manually circle both directions at 150–250 cm and capture standing, attack recovery, dodge, aura and wall/floor cases on both routes. It reports actual camera/pivot, actual pivot-to-eye distance, target arm length, approximate sweep hit component, capsule channel response, and camera point inside any visible follower's axis-aligned world bounds.

The sweep endpoint omits spring-arm socket/target offsets because the current UE Python API does not expose the unfixed endpoint; AABB occupancy can overstate a skeletal mesh silhouette and is not pixel visibility. Failures to read bounds are explicit. Compare against the Lead video and retain existing `P_C1043_CAMERA` wall/floor evidence; neither the old static probe nor this offline-authored script proves the dynamic result.

The A/B/C trade-offs remain undecided. No camera Source change is appropriate until the owner chooses an option. After selection, retain wall/floor safety, compare identical orbit paths, and inspect silhouette/readability for attacks, dodge direction and phase-two aura.

## Offline validation

- `python -m unittest Scripts.Editor.test_probe_camera_inside_boss -v`: covers finite geometry, AABB inside/outside boundaries, required evidence markers and the no-option-selection contract.
- Codex did not launch Editor/PIE or alter camera Source/assets. Owner selection, dynamic live results and any implementation are pending.
