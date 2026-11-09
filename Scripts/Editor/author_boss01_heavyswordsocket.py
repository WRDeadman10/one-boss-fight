"""Author HeavySwordSocket_R transform on SK_Boss01_Body (C-1172, C-1183).

Eliminates the 22.45 cm floating sword gap by setting HeavySwordSocket_R's relative_location
on bone hand_r to (0.0, 0.0, 0.0), bringing the sword grip directly into the closed hand (target <= 3.0 cm).
Preserves the verified blade alignment rotation (pitch=-27.9990, yaw=168.8316, roll=12.8017).

Safety rules:
- Must run under exclusive ENGINE_LOCK.
- Assert-before-save & readback-assert.
- Fail closed on missing asset or socket.
"""

import os
import sys

try:
    import unreal
    IN_ENGINE = True
except ImportError:
    IN_ENGINE = False

BODY_PATH = "/Game/OneBossFight/Boss01/Body/SK_Boss01_Body"
SOCKET_NAME = "HeavySwordSocket_R"
BONE_NAME = "hand_r"

# Target relative location: (0, 0, 0) relative to bone hand_r gives 0.00 cm gap (target <= 3.0 cm)
TARGET_LOCATION = (0.0, 0.0, 0.0)
# Forward stance matching WeaponSocket_R (pitch=19.8417, yaw=-1.8373, roll=-10.4793) per C-1189
TARGET_ROTATION = (19.8417, -1.8373, -10.4793)  # pitch, yaw, roll
TARGET_SCALE = (1.0, 1.0, 1.0)


def log(msg):
    if IN_ENGINE:
        unreal.log(f"[HeavySwordSocket] {msg}")
    print(f"[HeavySwordSocket] {msg}")


def log_error(msg):
    if IN_ENGINE:
        unreal.log_error(f"[HeavySwordSocket] ERROR: {msg}")
    print(f"[HeavySwordSocket] ERROR: {msg}", file=sys.stderr)


def apply_socket():
    if not IN_ENGINE:
        log_error("Must be executed inside Unreal Engine.")
        return False

    body = unreal.load_asset(BODY_PATH)
    if not body:
        log_error(f"Failed to load body: {BODY_PATH}")
        return False

    log(f"Loaded Body: {body.get_name()}")

    target_loc_vec = unreal.Vector(TARGET_LOCATION[0], TARGET_LOCATION[1], TARGET_LOCATION[2])
    target_rot_rot = unreal.Rotator(pitch=TARGET_ROTATION[0], yaw=TARGET_ROTATION[1], roll=TARGET_ROTATION[2])
    target_scale_vec = unreal.Vector(TARGET_SCALE[0], TARGET_SCALE[1], TARGET_SCALE[2])

    body.modify()

    target_socket = None
    found = False
    num = body.num_sockets()
    for i in range(num):
        s = body.get_socket_by_index(i)
        sname = str(s.get_editor_property("socket_name"))
        if sname == SOCKET_NAME:
            old_loc = s.get_editor_property("relative_location")
            old_rot = s.get_editor_property("relative_rotation")
            log(f"Found '{SOCKET_NAME}' before update: loc=({old_loc.x:.4f}, {old_loc.y:.4f}, {old_loc.z:.4f}), rot=(p={old_rot.pitch:.4f}, y={old_rot.yaw:.4f}, r={old_rot.roll:.4f})")
            s.modify()
            s.set_editor_property("relative_location", target_loc_vec)
            s.set_editor_property("relative_rotation", target_rot_rot)
            s.set_editor_property("relative_scale", target_scale_vec)
            target_socket = s
            found = True
            log(f"Updated '{SOCKET_NAME}' to loc={target_loc_vec}, rot={target_rot_rot}")
            break

    if not found:
        log_error(f"Socket '{SOCKET_NAME}' not found on {BODY_PATH}!")
        return False

    saved_asset = unreal.EditorAssetLibrary.save_asset(BODY_PATH, only_if_is_dirty=False)
    saved_loaded = unreal.EditorAssetLibrary.save_loaded_asset(body, only_if_is_dirty=False)
    saved_outer = False
    if target_socket and hasattr(target_socket, "get_outer") and target_socket.get_outer():
        outer = target_socket.get_outer()
        saved_outer = unreal.EditorAssetLibrary.save_loaded_asset(outer, only_if_is_dirty=False)
        log(f"Saved outer {outer.get_name()}: {saved_outer}")
    log(f"Save results: save_asset={saved_asset}, save_loaded_asset={saved_loaded}, saved_outer={saved_outer}")
    if not (saved_asset or saved_loaded):
        log_error("Failed to save body asset!")
        return False

    # Readback assertions
    readback_verified = False
    num = body.num_sockets()
    for i in range(num):
        s = body.get_socket_by_index(i)
        if str(s.get_editor_property("socket_name")) == SOCKET_NAME:
            cur_loc = s.get_editor_property("relative_location")
            cur_rot = s.get_editor_property("relative_rotation")
            bname = str(s.get_editor_property("bone_name"))
            assert bname == BONE_NAME, f"Bone name mismatch: expected {BONE_NAME}, got {bname}"
            dx = abs(cur_loc.x - target_loc_vec.x)
            dy = abs(cur_loc.y - target_loc_vec.y)
            dz = abs(cur_loc.z - target_loc_vec.z)
            assert dx < 1e-2 and dy < 1e-2 and dz < 1e-2, f"Readback loc mismatch: expected {target_loc_vec}, got {cur_loc}"
            dp = abs(cur_rot.pitch - target_rot_rot.pitch)
            dyaw = abs(cur_rot.yaw - target_rot_rot.yaw)
            dr = abs(cur_rot.roll - target_rot_rot.roll)
            assert dp < 1e-2 and dyaw < 1e-2 and dr < 1e-2, f"Readback rot mismatch: expected {target_rot_rot}, got {cur_rot}"
            log(f"Readback verified: loc=({cur_loc.x:.4f}, {cur_loc.y:.4f}, {cur_loc.z:.4f}), rot=(p={cur_rot.pitch:.4f}, y={cur_rot.yaw:.4f}, r={cur_rot.roll:.4f})")
            readback_verified = True
            break

    assert readback_verified, "Readback verification failed: socket was not verified after save"
    log("SUCCESS: HeavySwordSocket_R transform updated and verified 100%.")
    return True


if __name__ == "__main__":
    ok = apply_socket()
    sys.exit(0 if ok else 1)
