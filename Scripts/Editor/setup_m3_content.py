"""
M3 content setup for One Boss Fight. Idempotent: safe to re-run.

Run headless from the project root (editor closed):
  UnrealEditor-Cmd.exe OneBossFight.uproject -run=pythonscript -script=Scripts/Editor/setup_m3_content.py -unattended -nullrhi

Creates / configures:
  - IA_LightAttack, IA_HeavyAttack, IA_Dodge, IA_LockOn and their keys in IMC_Default (Jump moves to F)
  - AM_Greystone_* montages built from Greystone sequences, with RPG notify states placed from the
    sword bone's speed so the hit window matches the swing
  - DA_Weapon_GreystoneSword (URPGWeaponData)
  - BP_PlayerCharacter -> Greystone mesh, Greystone AnimBP, combat input, weapon and montages
  - BP_TrainingDummy, and two dummies placed in L_Greybox
"""

import unreal

INPUT_DIR = "/Game/OneBossFight/Input/"
CHARACTER_DIR = "/Game/OneBossFight/Characters"
GREYSTONE_DIR = "/Game/OneBossFight/Characters/Greystone"
WEAPON_DIR = "/Game/OneBossFight/Weapons"
LEVEL_PATH = "/Game/OneBossFight/Levels/L_Greybox"

PLAYER_BP = CHARACTER_DIR + "/BP_PlayerCharacter"
DUMMY_BP = CHARACTER_DIR + "/BP_TrainingDummy"
WEAPON_ASSET = WEAPON_DIR + "/DA_Weapon_GreystoneSword"

PACK = "/Game/ParagonGreystone"
ANIM_BP = PACK + "/Characters/Heroes/Greystone/Greystone_AnimBlueprint"
MESH_NAME = "Greystone"
DUMMY_MESH_NAME = "Greystone_Tough"

# Greystone's own skeleton has the sword as bones.
SWORD_BASE_BONE = "sword_bottom"
SWORD_TIP_BONE = "sword_top"

# (montage asset, source sequence, blend in/out seconds, damage, poise damage, stamina)
LIGHT_ATTACKS = [
    ("AM_Greystone_Light1", "Attack_A_Med", 28.0, 12.0, 18.0),
    ("AM_Greystone_Light2", "Attack_B_Med", 28.0, 12.0, 18.0),
    ("AM_Greystone_Light3", "Attack_C_Med", 32.0, 14.0, 20.0),
    ("AM_Greystone_Light4", "Attack_D_Med", 40.0, 18.0, 22.0),
]
HEAVY_ATTACK = ("AM_Greystone_Heavy", "Attack_RMB", 70.0, 40.0, 35.0)
HIT_REACT = ("AM_Greystone_HitReact", "HitReact_Front")
DEATH = ("AM_Greystone_Death", "Death")

# The Greystone AnimBP has a single Slot node "UpperBody"; its FullBody curve (carried by the attack animations)
# makes the AnimBP use that pose for the whole body when the character is not accelerating.
MONTAGE_SLOT = "UpperBody"

# Fallback fractions of the montage length when the bone path cannot be sampled.
FALLBACK_HIT = (0.35, 0.60)

# (asset, key names) - gamepad bindings follow Elden Ring conventions.
NEW_ACTIONS = {
    "IA_LightAttack": ["LeftMouseButton", "Gamepad_RightShoulder"],
    "IA_HeavyAttack": ["RightMouseButton", "Gamepad_RightTriggerAxis"],
    "IA_Dodge": ["SpaceBar", "Gamepad_FaceButton_Right"],
    "IA_LockOn": ["MiddleMouseButton", "Q", "Gamepad_RightThumbstick"],
}
JUMP_KEYS = ["F", "Gamepad_FaceButton_Bottom"]
OLD_JUMP_KEYS = ["SpaceBar"]


def log(msg):
    unreal.log("[M3Setup] " + msg)


def load(path):
    asset = unreal.load_asset(path)
    if asset is None:
        raise RuntimeError("Missing asset: " + path)
    return asset


def key(name):
    k = unreal.Key()
    k.set_editor_property("key_name", name)
    return k


def find_pack_asset(class_name, name):
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    registry.scan_paths_synchronous([PACK], True)
    for data in registry.get_assets_by_path(PACK, recursive=True):
        if str(data.asset_class_path.asset_name) == class_name and str(data.asset_name) == name:
            return data.get_asset()
    raise RuntimeError("Missing %s '%s' in %s" % (class_name, name, PACK))


def recreate(path, asset_class, factory):
    """Create an asset, replacing any previous version so reruns are deterministic."""
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.delete_asset(path)
    folder, name = path.rsplit("/", 1)
    return unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, folder, asset_class, factory)


# ---------------------------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------------------------

def setup_input():
    imc = load(INPUT_DIR + "IMC_Default")
    imc.modify()  # without this the package is not dirty and the save below is skipped
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    for action_name, keys in NEW_ACTIONS.items():
        path = INPUT_DIR + action_name
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            action = load(path)
        else:
            action = tools.create_asset(action_name, INPUT_DIR.rstrip("/"), unreal.InputAction, unreal.InputAction_Factory())
            action.set_editor_property("value_type", unreal.InputActionValueType.BOOLEAN)
            unreal.EditorAssetLibrary.save_loaded_asset(action)
        for key_name in keys:
            imc.unmap_key(action, key(key_name))  # avoid duplicates on rerun
            imc.map_key(action, key(key_name))
        log("%s mapped to %s" % (action_name, keys))

    jump = load(INPUT_DIR + "IA_Jump")
    for key_name in OLD_JUMP_KEYS:
        imc.unmap_key(jump, key(key_name))
    for key_name in JUMP_KEYS:
        imc.unmap_key(jump, key(key_name))
        imc.map_key(jump, key(key_name))
    # Gamepad B is the dodge button, so sprint moves to the left stick click.
    sprint = load(INPUT_DIR + "IA_Sprint")
    imc.unmap_key(sprint, key("Gamepad_FaceButton_Right"))
    imc.unmap_key(sprint, key("Gamepad_LeftThumbstick"))
    imc.map_key(sprint, key("Gamepad_LeftThumbstick"))
    unreal.EditorAssetLibrary.save_loaded_asset(imc, False)
    log("IMC_Default saved; jump now on %s" % JUMP_KEYS)


# ---------------------------------------------------------------------------------------------
# Montages
# ---------------------------------------------------------------------------------------------

def make_montage(asset_name, sequence):
    factory = unreal.AnimMontageFactory()
    factory.set_editor_property("source_animation", sequence)
    montage = recreate(GREYSTONE_DIR + "/" + asset_name, unreal.AnimMontage, factory)
    # The factory default "DefaultSlot" does not exist in Greystone's AnimBP.
    unreal.RPGMontageUtils.set_montage_slot(montage, MONTAGE_SLOT)
    return montage


def sample_sword_speed(sequence):
    """(times, speeds) of the sword tip in cm/s, or None if the pose API gives nothing useful."""
    length = sequence.get_play_length()
    steps = max(8, int(length * 30))
    times = [length * i / steps for i in range(steps + 1)]
    points = []
    try:
        # get_bone_pose_for_time is parent-relative; compose down the chain to get the component-space tip.
        chain = list(reversed(unreal.AnimationLibrary.find_bone_path_to_root(sequence, SWORD_TIP_BONE)))
        for t in times:
            component = unreal.Transform()
            for bone in chain:
                local = unreal.AnimationLibrary.get_bone_pose_for_time(sequence, bone, t, False)
                component = unreal.MathLibrary.compose_transforms(local, component)
            points.append(component.translation)
    except Exception as exc:
        log("Bone sampling failed for %s: %s" % (sequence.get_name(), exc))
        return None
    speeds = [0.0]
    for i in range(1, len(points)):
        dt = times[i] - times[i - 1]
        speeds.append((points[i] - points[i - 1]).length() / dt if dt > 0 else 0.0)
    return times, speeds, points


def hit_window_from_motion(sequence):
    """Start/end seconds where the sword tip moves fast; falls back to fixed fractions."""
    length = sequence.get_play_length()
    sampled = sample_sword_speed(sequence)
    if sampled is None:
        return length * FALLBACK_HIT[0], length * FALLBACK_HIT[1], "fallback"

    times, speeds, points = sampled
    peak = max(speeds)
    if peak < 1.0:
        return length * FALLBACK_HIT[0], length * FALLBACK_HIT[1], "fallback (no motion)"

    # Smooth over 3 samples, then take the contiguous run around the peak above 40 % of it.
    smooth = [sum(speeds[max(0, i - 1):i + 2]) / len(speeds[max(0, i - 1):i + 2]) for i in range(len(speeds))]
    peak_index = smooth.index(max(smooth))
    threshold = 0.4 * smooth[peak_index]
    start = peak_index
    while start > 0 and smooth[start - 1] >= threshold:
        start -= 1
    end = peak_index
    while end < len(smooth) - 1 and smooth[end + 1] >= threshold:
        end += 1
    log("%s: sword peak %.0f cm/s at %.2fs, tip x/y/z at peak %s" % (
        sequence.get_name(), smooth[peak_index], times[peak_index], points[peak_index]))
    return times[start], times[end], "motion"


def add_notify_state(montage, track, start, end, state_class):
    duration = max(end - start, 0.02)
    unreal.AnimationLibrary.add_animation_notify_state_event(montage, track, start, duration, state_class)


def build_attack_montage(asset_name, sequence_name, is_heavy):
    sequence = find_pack_asset("AnimSequence", sequence_name)
    montage = make_montage(asset_name, sequence)
    length = montage.get_play_length()
    hit_start, hit_end, how = hit_window_from_motion(sequence)

    track = "RPGCombat"
    unreal.AnimationLibrary.add_animation_notify_track(montage, track)
    add_notify_state(montage, track, hit_start, hit_end, unreal.RPGANS_HitWindow)

    if not is_heavy:
        # Next attack may be queued from the end of the swing until shortly before the animation ends.
        combo_start = min(hit_end + 0.05, length - 0.2)
        add_notify_state(montage, track, combo_start, length - 0.05, unreal.RPGANS_ComboWindow)
    # Recovery can be dodge-cancelled once the swing is over.
    add_notify_state(montage, track, min(hit_end + 0.1, length - 0.1), length, unreal.RPGANS_CancelWindow)

    unreal.EditorAssetLibrary.save_loaded_asset(montage)
    log("%s: length %.2fs, hit window %.2f-%.2fs (%s)" % (asset_name, length, hit_start, hit_end, how))
    return montage


def build_plain_montage(asset_name, sequence_name):
    montage = make_montage(asset_name, find_pack_asset("AnimSequence", sequence_name))
    unreal.EditorAssetLibrary.save_loaded_asset(montage)
    log("%s: length %.2fs" % (asset_name, montage.get_play_length()))
    return montage


# ---------------------------------------------------------------------------------------------
# Weapon data
# ---------------------------------------------------------------------------------------------

def attack_struct(montage, damage, poise, stamina):
    attack = unreal.RPGAttackData()
    attack.set_editor_property("montage", montage)
    attack.set_editor_property("damage", damage)
    attack.set_editor_property("poise_damage", poise)
    attack.set_editor_property("stamina_cost", stamina)
    return attack


def build_weapon(light_montages, heavy_montage):
    factory = unreal.DataAssetFactory()
    factory.set_editor_property("data_asset_class", unreal.RPGWeaponData)
    unreal.EditorAssetLibrary.make_directory(WEAPON_DIR)
    weapon = recreate(WEAPON_ASSET, unreal.RPGWeaponData, factory)

    weapon.set_editor_property("display_name", unreal.Text("Greystone Sword"))
    weapon.set_editor_property("light_combo", [
        attack_struct(m, LIGHT_ATTACKS[i][2], LIGHT_ATTACKS[i][3], LIGHT_ATTACKS[i][4])
        for i, m in enumerate(light_montages)])
    weapon.set_editor_property("heavy_attack", attack_struct(
        heavy_montage, HEAVY_ATTACK[2], HEAVY_ATTACK[3], HEAVY_ATTACK[4]))
    weapon.set_editor_property("trace_base_socket", SWORD_BASE_BONE)
    weapon.set_editor_property("trace_tip_socket", SWORD_TIP_BONE)
    weapon.set_editor_property("trace_radius", 18.0)
    weapon.set_editor_property("trace_samples", 4)
    unreal.EditorAssetLibrary.save_loaded_asset(weapon)
    log("Weapon asset saved.")
    return weapon


# ---------------------------------------------------------------------------------------------
# Blueprints
# ---------------------------------------------------------------------------------------------

def get_component(cdo, name, component_class):
    try:
        return cdo.get_editor_property(name)
    except Exception:
        comps = cdo.get_components_by_class(component_class)
        if not comps:
            raise RuntimeError("Component %s not found on %s" % (name, cdo.get_name()))
        return comps[0]


def style_character(cdo, mesh_name, hit_react, death, weapon):
    """Greystone is ~206 cm tall: resize the capsule and sit the mesh on its bottom."""
    capsule = cdo.get_editor_property("capsule_component")
    capsule.set_editor_property("capsule_half_height", 103.0)
    capsule.set_editor_property("capsule_radius", 42.0)

    mesh_component = cdo.get_editor_property("mesh")
    mesh_component.set_editor_property("skeletal_mesh_asset", find_pack_asset("SkeletalMesh", mesh_name))
    mesh_component.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, -103.0))
    mesh_component.set_editor_property("relative_rotation", unreal.Rotator(roll=0.0, pitch=0.0, yaw=-90.0))
    mesh_component.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
    mesh_component.set_editor_property("anim_class", load(ANIM_BP).generated_class())

    cdo.set_editor_property("hit_react_montage", hit_react)
    cdo.set_editor_property("death_montage", death)

    if weapon is not None:
        combat = get_component(cdo, "combat", unreal.RPGCombatComponent)
        combat.set_editor_property("weapon", weapon)


def configure_player(hit_react, death, weapon):
    bp = load(PLAYER_BP)
    cdo = unreal.get_default_object(bp.generated_class())
    cdo.set_editor_property("light_attack_action", load(INPUT_DIR + "IA_LightAttack"))
    cdo.set_editor_property("heavy_attack_action", load(INPUT_DIR + "IA_HeavyAttack"))
    cdo.set_editor_property("dodge_action", load(INPUT_DIR + "IA_Dodge"))
    cdo.set_editor_property("lock_on_action", load(INPUT_DIR + "IA_LockOn"))
    style_character(cdo, MESH_NAME, hit_react, death, weapon)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_loaded_asset(bp)
    log("BP_PlayerCharacter now Greystone with combat input.")


def ensure_dummy_blueprint(hit_react, death):
    if unreal.EditorAssetLibrary.does_asset_exist(DUMMY_BP):
        bp = load(DUMMY_BP)
    else:
        factory = unreal.BlueprintFactory()
        factory.set_editor_property("parent_class", unreal.load_class(None, "/Script/OneBossFight.RPGTrainingDummy"))
        bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset("BP_TrainingDummy", CHARACTER_DIR, unreal.Blueprint, factory)
    cdo = unreal.get_default_object(bp.generated_class())
    style_character(cdo, DUMMY_MESH_NAME, hit_react, death, None)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_loaded_asset(bp)
    log("BP_TrainingDummy ready.")
    return bp


def place_dummies(dummy_bp):
    unreal.EditorLevelLibrary.load_level(LEVEL_PATH)
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_actor_label().startswith("TrainingDummy"):
            actor.destroy_actor()
    # They face the player start at (-1800, 0).
    for index, (x, y) in enumerate([(-1100.0, 0.0), (-1100.0, 500.0)]):
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            dummy_bp.generated_class(), unreal.Vector(x, y, 105.0), unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0))
        actor.set_actor_label("TrainingDummy_%d" % (index + 1))
    unreal.EditorLevelLibrary.save_current_level()
    log("Dummies placed in L_Greybox.")


def main():
    unreal.EditorAssetLibrary.make_directory(GREYSTONE_DIR)
    setup_input()

    lights = [build_attack_montage(name, seq, is_heavy=False) for name, seq, *_ in LIGHT_ATTACKS]
    heavy = build_attack_montage(HEAVY_ATTACK[0], HEAVY_ATTACK[1], is_heavy=True)
    hit_react = build_plain_montage(*HIT_REACT)
    death = build_plain_montage(*DEATH)

    weapon = build_weapon(lights, heavy)
    configure_player(hit_react, death, weapon)
    dummy_bp = ensure_dummy_blueprint(hit_react, death)
    place_dummies(dummy_bp)
    log("M3 content setup complete.")


main()
