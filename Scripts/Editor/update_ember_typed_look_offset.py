"""Update only the live-referenced Ember typed definition's sword look data.

Run by the Lead in Unreal Editor under ENGINE_LOCK.json. The operation refuses
every package except the exact project-owned draft and never touches pack data.
"""
import math

import unreal

if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import ue_editor_values


TARGET_PACKAGE_PATH = (
    "/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/"
    "BossDrafts/DA_Boss_EmberWarden_Draft"
)
TARGET_ASSET_NAME = "DA_Boss_EmberWarden_Draft"
TARGET_OBJECT_PATH = TARGET_PACKAGE_PATH + "." + TARGET_ASSET_NAME
PACK_ROOT = "/Game/AdvancedARPGCombat"
OLD_SOCKET = "HeavySwordSocket_R"
NEW_SOCKET = "hand_r"
TARGET_PITCH = 19.84
TARGET_YAW = -1.84
TARGET_ROLL = -10.48
TOLERANCE = 1.0e-4


def require(condition, message):
    if not condition:
        raise RuntimeError("[EmberTypedLook] REFUSED: " + message)


def assert_safe_target_path(package_path):
    normalized = str(package_path).replace("\\", "/").rstrip("/")
    require(not normalized.startswith(PACK_ROOT + "/") and normalized != PACK_ROOT,
            "pack asset path is forbidden: " + normalized)
    require(normalized == TARGET_PACKAGE_PATH,
            "only the exact Ember typed definition may be saved: " + normalized)


def vector_values(value):
    return float(value.x), float(value.y), float(value.z)


def rotation_values(value):
    # Unreal exposes FTransform.rotation as FQuat in Python; convert it to the
    # Euler Rotator only for comparing the serialized authoring values.
    to_rotator = getattr(value, "rotator", None)
    if callable(to_rotator):
        value = to_rotator()
    return float(value.pitch), float(value.yaw), float(value.roll)


def close(actual, expected):
    return math.isfinite(float(actual)) and math.isclose(
        float(actual), float(expected), rel_tol=0.0, abs_tol=TOLERANCE)


def offset_matches(offset, expected_rotation, expected_location=(0.0, 0.0, 0.0)):
    location = vector_values(offset.translation)
    rotation = rotation_values(offset.rotation)
    scale = vector_values(offset.scale3d)
    return (
        all(close(a, e) for a, e in zip(location, expected_location))
        and all(close(a, e) for a, e in zip(rotation, expected_rotation))
        and all(close(a, 1.0) for a in scale)
    )


def preserved_look_state(look):
    return {
        "enabled": look.get_editor_property("enabled"),
        "body": ue_editor_values.stable_value(
            look.get_editor_property("body"), unreal, "Look.Body"),
        "pieces": ue_editor_values.stable_value(
            look.get_editor_property("pieces"), unreal, "Look.Pieces"),
        "sword": ue_editor_values.stable_value(
            look.get_editor_property("sword"), unreal, "Look.Sword"),
    }


def assert_preserved(before, look):
    require(preserved_look_state(look) == before,
            "Look enabled/body/pieces/sword changed; refusing to save unrelated values")


def assert_target_values(look):
    require(str(look.get_editor_property("sword_socket")) == NEW_SOCKET,
            "SwordSocket readback is not hand_r")
    offset = look.get_editor_property("sword_attach_offset")
    require(offset_matches(offset, (TARGET_PITCH, TARGET_YAW, TARGET_ROLL)),
            "SwordAttachOffset readback does not match the requested transform")


def current_state_is_supported(look):
    socket = str(look.get_editor_property("sword_socket"))
    offset = look.get_editor_property("sword_attach_offset")
    if socket == NEW_SOCKET and offset_matches(
            offset, (TARGET_PITCH, TARGET_YAW, TARGET_ROLL)):
        return "already-configured"
    if socket == OLD_SOCKET and offset_matches(offset, (0.0, 0.0, 0.0)):
        return "legacy-default"
    return "unexpected"


def main():
    # Check the hard-coded destination before any load or mutation.
    assert_safe_target_path(TARGET_PACKAGE_PATH)
    require(TARGET_OBJECT_PATH == TARGET_PACKAGE_PATH + "." + TARGET_ASSET_NAME,
            "target object/package identity is inconsistent")

    eal = unreal.EditorAssetLibrary
    require(eal.does_asset_exist(TARGET_PACKAGE_PATH),
            "typed Ember definition is missing: " + TARGET_PACKAGE_PATH)
    asset = eal.load_asset(TARGET_PACKAGE_PATH)
    require(asset is not None, "typed Ember definition failed to load")
    assert_safe_target_path(asset.get_outermost().get_name())
    require(asset.get_path_name() == TARGET_OBJECT_PATH,
            "loaded object path differs from the allow-listed target")

    definition_class = unreal.load_class(None, "/Script/OneBossFight.RPGBossDefinition")
    require(definition_class is not None
            and ue_editor_values.is_expected_class(asset, definition_class),
            "target is not a URPGBossDefinition")

    look = asset.get_editor_property("look")
    before = preserved_look_state(look)
    state = current_state_is_supported(look)
    require(state != "unexpected",
            "Look socket/offset is neither the expected legacy default nor requested value")
    if state == "already-configured":
        assert_preserved(before, look)
        unreal.log("[EmberTypedLook] PASS already configured; no save needed")
        return

    # Edit only the nested look struct. Keep its existing enabled/body/pieces/sword values.
    look.set_editor_property("sword_socket", NEW_SOCKET)
    look.set_editor_property(
        "sword_attach_offset",
        unreal.Transform(
            unreal.Vector(0.0, 0.0, 0.0),
            unreal.Rotator(pitch=TARGET_PITCH, yaw=TARGET_YAW, roll=TARGET_ROLL),
            unreal.Vector(1.0, 1.0, 1.0),
        ),
    )
    asset.set_editor_property("look", look)

    # Assert the in-memory result and preserved fields before the only save call.
    assert_safe_target_path(asset.get_outermost().get_name())
    staged_look = asset.get_editor_property("look")
    assert_target_values(staged_look)
    assert_preserved(before, staged_look)

    require(eal.save_loaded_asset(asset), "save failed for allow-listed Ember definition")

    # Reload from the saved package, then assert target identity and all changed values.
    reloaded = eal.load_asset(TARGET_PACKAGE_PATH)
    require(reloaded is not None, "saved Ember definition failed to reload")
    assert_safe_target_path(reloaded.get_outermost().get_name())
    require(reloaded.get_path_name() == TARGET_OBJECT_PATH
            and ue_editor_values.is_expected_class(reloaded, definition_class),
            "reloaded object is not the allow-listed Ember typed definition")
    readback = reloaded.get_editor_property("look")
    assert_target_values(readback)
    assert_preserved(before, readback)
    unreal.log(
        "[EmberTypedLook] PASS saved only the allow-listed definition; "
        "socket=hand_r location=(0,0,0) rotation=(19.84,-1.84,-10.48)"
    )


if __name__ == "__main__":
    main()
