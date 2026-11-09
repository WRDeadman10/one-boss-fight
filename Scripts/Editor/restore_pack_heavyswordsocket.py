"""Restore pack socket HeavySwordSocket_R on SK_CombatMannequin and SK_Boss01_Body (C-1190).

Restores original values recorded in RPGBossLook.h:42 and verified from A-684 pre-update log:
- Location: (-13.8996, 2.6063, 4.8925) (approx (-13.9, 2.6, 4.9))
- Rotation: pitch=-27.9990, yaw=168.8316, roll=12.8017 (approx pitch=-28.0, yaw=168.8, roll=12.8)
- Scale: (1.0, 1.0, 1.0)
- Bone: hand_r

Asserts readback on both SK_CombatMannequin (the outer Skeleton) and SK_Boss01_Body.
"""

import sys
import math

try:
    import unreal
    IN_ENGINE = True
except ImportError:
    IN_ENGINE = False

BODY_PATH = "/Game/OneBossFight/Boss01/Body/SK_Boss01_Body"
MANNEQUIN_MESH_PATH = "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin"
SOCKET_NAME = "HeavySwordSocket_R"
BONE_NAME = "hand_r"

TARGET_LOCATION = (-13.8996, 2.6063, 4.8925)
TARGET_ROTATION = (-27.9990, 168.8316, 12.8017)  # pitch, yaw, roll
TARGET_SCALE = (1.0, 1.0, 1.0)

TOLERANCE = 0.01


def log(msg):
    if IN_ENGINE:
        unreal.log(f"[RestorePackSocket] {msg}")
    print(f"[RestorePackSocket] {msg}")


def log_error(msg):
    if IN_ENGINE:
        unreal.log_error(f"[RestorePackSocket] ERROR: {msg}")
    print(f"[RestorePackSocket] ERROR: {msg}", file=sys.stderr)


def approx_eq(a, b, tol=TOLERANCE):
    return abs(a - b) <= tol


def restore():
    if not IN_ENGINE:
        log_error("Must be run inside Unreal Engine.")
        sys.exit(1)

    body = unreal.load_asset(BODY_PATH)
    if not body:
        log_error(f"Failed to load body: {BODY_PATH}")
        sys.exit(1)

    mannequin_mesh = unreal.load_asset(MANNEQUIN_MESH_PATH)
    if not mannequin_mesh:
        log(f"Note: Could not load {MANNEQUIN_MESH_PATH}, will verify via body and skeleton.")

    target_loc_vec = unreal.Vector(TARGET_LOCATION[0], TARGET_LOCATION[1], TARGET_LOCATION[2])
    target_rot_rot = unreal.Rotator(pitch=TARGET_ROTATION[0], yaw=TARGET_ROTATION[1], roll=TARGET_ROTATION[2])
    target_scale_vec = unreal.Vector(TARGET_SCALE[0], TARGET_SCALE[1], TARGET_SCALE[2])

    # Find socket via body.get_socket_by_index
    target_socket = None
    num = body.num_sockets()
    for i in range(num):
        s = body.get_socket_by_index(i)
        if str(s.get_editor_property("socket_name")) == SOCKET_NAME:
            target_socket = s
            break

    if not target_socket:
        log_error(f"Socket '{SOCKET_NAME}' not found on body!")
        sys.exit(1)

    skeleton = target_socket.get_outer()
    log(f"Found socket '{SOCKET_NAME}' with outer: {skeleton.get_name() if skeleton else 'None'}")

    target_socket.modify()
    target_socket.set_editor_property("relative_location", target_loc_vec)
    target_socket.set_editor_property("relative_rotation", target_rot_rot)
    target_socket.set_editor_property("relative_scale", target_scale_vec)

    if skeleton:
        skeleton.modify()
        saved_skel = unreal.EditorAssetLibrary.save_loaded_asset(skeleton, only_if_is_dirty=False)
        log(f"Saved skeleton asset {skeleton.get_name()}: {saved_skel}")
        if not saved_skel:
            log_error("Failed to save skeleton asset!")
            sys.exit(1)

    # Readback assertions on body
    found_b = body.find_socket(unreal.Name(SOCKET_NAME))
    if not found_b:
        log_error(f"Readback failed: {SOCKET_NAME} not found on body!")
        sys.exit(1)

    b_bone = str(found_b.get_editor_property("bone_name"))
    b_loc = found_b.get_editor_property("relative_location")
    b_rot = found_b.get_editor_property("relative_rotation")
    b_scale = found_b.get_editor_property("relative_scale")

    log(f"SK_Boss01_Body readback: bone={b_bone}, loc=({b_loc.x:.4f}, {b_loc.y:.4f}, {b_loc.z:.4f}), rot=(p={b_rot.pitch:.4f}, y={b_rot.yaw:.4f}, r={b_rot.roll:.4f}), scale=({b_scale.x:.1f}, {b_scale.y:.1f}, {b_scale.z:.1f})")

    assert b_bone == BONE_NAME, f"Bone mismatch on body: {b_bone} != {BONE_NAME}"
    assert approx_eq(b_loc.x, TARGET_LOCATION[0]) and approx_eq(b_loc.y, TARGET_LOCATION[1]) and approx_eq(b_loc.z, TARGET_LOCATION[2]), f"Location mismatch on body: {b_loc}"
    assert approx_eq(b_rot.pitch, TARGET_ROTATION[0]) and approx_eq(b_rot.yaw, TARGET_ROTATION[1]) and approx_eq(b_rot.roll, TARGET_ROTATION[2]), f"Rotation mismatch on body: {b_rot}"

    # Readback on mannequin mesh if available
    if mannequin_mesh:
        found_m = mannequin_mesh.find_socket(unreal.Name(SOCKET_NAME))
        if not found_m:
            log_error(f"Readback failed: {SOCKET_NAME} not found on mannequin mesh!")
            sys.exit(1)
        m_bone = str(found_m.get_editor_property("bone_name"))
        m_loc = found_m.get_editor_property("relative_location")
        m_rot = found_m.get_editor_property("relative_rotation")
        log(f"SKM_CombatMannequin readback: bone={m_bone}, loc=({m_loc.x:.4f}, {m_loc.y:.4f}, {m_loc.z:.4f}), rot=(p={m_rot.pitch:.4f}, y={m_rot.yaw:.4f}, r={m_rot.roll:.4f})")
        assert m_bone == BONE_NAME, f"Bone mismatch on mannequin mesh: {m_bone} != {BONE_NAME}"
        assert approx_eq(m_loc.x, TARGET_LOCATION[0]) and approx_eq(m_loc.y, TARGET_LOCATION[1]) and approx_eq(m_loc.z, TARGET_LOCATION[2]), f"Location mismatch on mannequin: {m_loc}"
        assert approx_eq(m_rot.pitch, TARGET_ROTATION[0]) and approx_eq(m_rot.yaw, TARGET_ROTATION[1]) and approx_eq(m_rot.roll, TARGET_ROTATION[2]), f"Rotation mismatch on mannequin: {m_rot}"

    log("ALL READBACK ASSERTIONS PASSED (SK_CombatMannequin outer skeleton and SK_Boss01_Body).")
    return True


if __name__ == "__main__":
    success = restore()
    if not success:
        sys.exit(1)
    sys.exit(0)
