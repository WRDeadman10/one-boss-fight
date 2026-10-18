"""
M4 content setup for One Boss Fight (boss and encounter). Idempotent: safe to re-run.

Run headless from the project root (editor closed):
  UnrealEditor-Cmd.exe OneBossFight.uproject -run=pythonscript -script=Scripts/Editor/setup_m4_content.py -unattended -nullrhi

Creates / configures:
  - AM_Sevarog_* montages from Sevarog sequences (slot FullBody), hit windows placed from the scythe tip speed
  - DA_Boss_* attack data assets and DA_Weapon_SevarogScythe
  - BP_SevarogBoss (RPGBossCharacter) with mesh, AnimBP, attacks, phases, entrance
  - L_Greybox: boss at the arena center, encounter trigger at the entrance (training dummies removed)
"""

import unreal

PACK = "/Game/ParagonSevarog"
BOSS_DIR = "/Game/OneBossFight/Boss"
CHARACTER_DIR = "/Game/OneBossFight/Characters"
WEAPON_DIR = "/Game/OneBossFight/Weapons"
LEVEL_PATH = "/Game/OneBossFight/Levels/L_Greybox"

BOSS_BP = CHARACTER_DIR + "/BP_SevarogBoss"
WEAPON_ASSET = WEAPON_DIR + "/DA_Weapon_SevarogScythe"
ANIM_BP = PACK + "/Characters/Heroes/Sevarog/Sevarog_AnimBlueprint"

SLOT = "FullBody"  # Sevarog's AnimBP has a FullBody slot node after the locomotion blend.
TIP_BONE = "root_weapon_end_r"
BASE_BONE = "weapon_r"

# name, sequence, hit-window mode ("motion" | "none"), radial (radius, forward offset, time fraction or None=peak) or None
MONTAGES = [
    ("AM_Sevarog_Sweep", "Swing1_Medium", "motion", None),
    ("AM_Sevarog_Backhand", "Swing2_Medium", "motion", None),
    ("AM_Sevarog_Overhead", "Swing3_Medium", "motion", None),
    ("AM_Sevarog_Lunge", "Swing_In_Air", "motion", None),
    ("AM_Sevarog_Shockwave", "Ultimate_Swing_120fps", "none", (500.0, 200.0, None)),
    ("AM_Sevarog_Lightning", "Cast", "none", (350.0, 600.0, 0.5)),
    ("AM_Sevarog_Entrance", "LevelStart", "none", None),
    ("AM_Sevarog_PhaseRoar", "Ultimate_Targeting", "none", None),
    ("AM_Sevarog_HitReact", "Hitreact_Front", "none", None),
    ("AM_Sevarog_Death", "Death_front", "none", None),
]

# asset, montage, kwargs for the attack data
ATTACKS = [
    ("DA_Boss_Sweep", "AM_Sevarog_Sweep", dict(
        attack_name="Sweep", min_range=0, max_range=380, max_angle=70, weight=3, cooldown=3, max_consecutive_repeats=1,
        tracking_turn_rate=120, recovery_pause=0.6), dict(damage=40, poise_damage=25)),
    ("DA_Boss_Backhand", "AM_Sevarog_Backhand", dict(
        attack_name="Backhand", min_range=0, max_range=380, max_angle=100, weight=3, cooldown=3, max_consecutive_repeats=1,
        tracking_turn_rate=120, recovery_pause=0.6), dict(damage=38, poise_damage=25)),
    ("DA_Boss_Overhead", "AM_Sevarog_Overhead", dict(
        attack_name="Overhead Slam", min_range=0, max_range=420, max_angle=50, weight=2, cooldown=5, max_consecutive_repeats=1,
        tracking_turn_rate=60, recovery_pause=0.9), dict(damage=60, poise_damage=40)),
    ("DA_Boss_Lunge", "AM_Sevarog_Lunge", dict(
        attack_name="Lunge", min_range=350, max_range=900, max_angle=40, weight=3, cooldown=6, max_consecutive_repeats=1,
        tracking_turn_rate=90, recovery_pause=0.9, lunge_speed=900), dict(damage=55, poise_damage=35)),
    ("DA_Boss_Shockwave", "AM_Sevarog_Shockwave", dict(
        attack_name="Shockwave", min_range=0, max_range=600, max_angle=180, weight=2, cooldown=10, max_consecutive_repeats=1,
        tracking_turn_rate=0, recovery_pause=1.0), dict(damage=70, poise_damage=45)),
    ("DA_Boss_Lightning", "AM_Sevarog_Lightning", dict(
        attack_name="Lightning (placeholder)", min_range=300, max_range=1500, max_angle=45, weight=3, cooldown=8,
        max_consecutive_repeats=1, min_phase=2, tracking_turn_rate=90, recovery_pause=1.0), dict(damage=45, poise_damage=30)),
]


def log(msg):
    unreal.log("[M4Setup] " + msg)


def load(path):
    asset = unreal.load_asset(path)
    if asset is None:
        raise RuntimeError("Missing asset: " + path)
    return asset


def find_pack_asset(class_name, name):
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    registry.scan_paths_synchronous([PACK], True)
    for data in registry.get_assets_by_path(PACK, recursive=True):
        if str(data.asset_class_path.asset_name) == class_name and str(data.asset_name) == name:
            return data.get_asset()
    raise RuntimeError("Missing %s '%s' in %s" % (class_name, name, PACK))


def recreate(path, asset_class, factory):
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.delete_asset(path)
    folder, name = path.rsplit("/", 1)
    return unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, folder, asset_class, factory)


# ---------------------------------------------------------------------------------------------
# Hit window from motion
# ---------------------------------------------------------------------------------------------

def sample_tip(sequence):
    length = sequence.get_play_length()
    steps = max(8, int(length * 30))
    times = [length * i / steps for i in range(steps + 1)]
    chain = list(reversed(unreal.AnimationLibrary.find_bone_path_to_root(sequence, TIP_BONE)))
    points = []
    for t in times:
        component = unreal.Transform()
        for bone in chain:
            local = unreal.AnimationLibrary.get_bone_pose_for_time(sequence, bone, t, False)
            component = unreal.MathLibrary.compose_transforms(local, component)
        points.append(component.translation)
    speeds = [0.0] + [(points[i] - points[i - 1]).length() / (times[i] - times[i - 1]) for i in range(1, len(points))]
    return times, speeds


def motion_window(sequence):
    """(start, end, peak_time) around the fastest scythe movement, from 40 % of peak speed."""
    length = sequence.get_play_length()
    try:
        times, speeds = sample_tip(sequence)
    except Exception as exc:
        log("Tip sampling failed for %s: %s" % (sequence.get_name(), exc))
        return length * 0.35, length * 0.6, length * 0.5
    smooth = [sum(speeds[max(0, i - 1):i + 2]) / len(speeds[max(0, i - 1):i + 2]) for i in range(len(speeds))]
    peak = smooth.index(max(smooth))
    threshold = 0.4 * smooth[peak]
    start = peak
    while start > 0 and smooth[start - 1] >= threshold:
        start -= 1
    end = peak
    while end < len(smooth) - 1 and smooth[end + 1] >= threshold:
        end += 1
    return times[start], times[end], times[peak]


def build_montage(name, sequence_name, mode, radial):
    sequence = find_pack_asset("AnimSequence", sequence_name)
    factory = unreal.AnimMontageFactory()
    factory.set_editor_property("source_animation", sequence)
    montage = recreate(BOSS_DIR + "/" + name, unreal.AnimMontage, factory)
    unreal.RPGMontageUtils.set_montage_slot(montage, SLOT)

    length = montage.get_play_length()
    track = "RPGCombat"
    unreal.AnimationLibrary.add_animation_notify_track(montage, track)
    detail = ""

    if mode == "motion":
        start, end, _ = motion_window(sequence)
        unreal.AnimationLibrary.add_animation_notify_state_event(montage, track, start, max(end - start, 0.02), unreal.RPGANS_HitWindow)
        detail = "hit window %.2f-%.2fs" % (start, end)

    if radial is not None:
        radius, forward, fraction = radial
        if fraction is not None:
            when = length * fraction
        else:
            try:
                _, _, when = motion_window(sequence)
            except Exception:
                when = length * 0.55
        # add_animation_notify_event returns the notify object itself.
        notify = unreal.AnimationLibrary.add_animation_notify_event(montage, track, when, unreal.RPGAN_RadialHit)
        notify.set_editor_property("radius", radius)
        notify.set_editor_property("forward_offset", forward)
        detail += " radial %.0f cm at %.2fs" % (radius, when)

    unreal.EditorAssetLibrary.save_loaded_asset(montage)
    log("%s: %.2fs %s" % (name, length, detail))
    return montage


# ---------------------------------------------------------------------------------------------
# Data assets
# ---------------------------------------------------------------------------------------------

def build_attack(asset_name, montage, boss_fields, attack_fields):
    factory = unreal.DataAssetFactory()
    factory.set_editor_property("data_asset_class", unreal.RPGBossAttackData)
    data = recreate(BOSS_DIR + "/" + asset_name, unreal.RPGBossAttackData, factory)
    for key, value in boss_fields.items():
        data.set_editor_property(key, value)
    attack = unreal.RPGAttackData()
    attack.set_editor_property("montage", montage)
    for key, value in attack_fields.items():
        attack.set_editor_property(key, value)
    data.set_editor_property("attack", attack)
    unreal.EditorAssetLibrary.save_loaded_asset(data)
    return data


def build_weapon():
    factory = unreal.DataAssetFactory()
    factory.set_editor_property("data_asset_class", unreal.RPGWeaponData)
    unreal.EditorAssetLibrary.make_directory(WEAPON_DIR)
    weapon = recreate(WEAPON_ASSET, unreal.RPGWeaponData, factory)
    weapon.set_editor_property("display_name", unreal.Text("Sevarog Scythe"))
    weapon.set_editor_property("trace_base_socket", BASE_BONE)
    weapon.set_editor_property("trace_tip_socket", TIP_BONE)
    weapon.set_editor_property("trace_radius", 45.0)
    weapon.set_editor_property("trace_samples", 6)
    unreal.EditorAssetLibrary.save_loaded_asset(weapon)
    return weapon


# ---------------------------------------------------------------------------------------------
# Blueprint and level
# ---------------------------------------------------------------------------------------------

def configure_boss(montages, attacks, weapon):
    if unreal.EditorAssetLibrary.does_asset_exist(BOSS_BP):
        bp = load(BOSS_BP)
    else:
        factory = unreal.BlueprintFactory()
        factory.set_editor_property("parent_class", unreal.load_class(None, "/Script/OneBossFight.RPGBossCharacter"))
        bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset("BP_SevarogBoss", CHARACTER_DIR, unreal.Blueprint, factory)

    cdo = unreal.get_default_object(bp.generated_class())

    # Sevarog is ~311 cm tall.
    capsule = cdo.get_editor_property("capsule_component")
    capsule.set_editor_property("capsule_half_height", 155.0)
    capsule.set_editor_property("capsule_radius", 90.0)

    mesh_component = cdo.get_editor_property("mesh")
    mesh_component.set_editor_property("skeletal_mesh_asset", find_pack_asset("SkeletalMesh", "Sevarog"))
    mesh_component.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, -155.0))
    mesh_component.set_editor_property("relative_rotation", unreal.Rotator(roll=0.0, pitch=0.0, yaw=-90.0))
    mesh_component.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
    mesh_component.set_editor_property("anim_class", load(ANIM_BP).generated_class())

    cdo.set_editor_property("hit_react_montage", montages["AM_Sevarog_HitReact"])
    cdo.set_editor_property("death_montage", montages["AM_Sevarog_Death"])
    cdo.set_editor_property("boss_name", unreal.Text("Sevarog"))

    combat = cdo.get_components_by_class(unreal.RPGCombatComponent)[0]
    combat.set_editor_property("weapon", weapon)

    brain = cdo.get_components_by_class(unreal.RPGBossCombatComponent)[0]
    brain.set_editor_property("attacks", attacks)
    brain.set_editor_property("entrance_montage", montages["AM_Sevarog_Entrance"])
    brain.set_editor_property("phase_transition_montage", montages["AM_Sevarog_PhaseRoar"])
    brain.set_editor_property("phase_health_thresholds", [0.5])

    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_loaded_asset(bp)
    log("BP_SevarogBoss configured with %d attacks." % len(attacks))
    return bp


def build_level(boss_bp):
    unreal.EditorLevelLibrary.load_level(LEVEL_PATH)
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        label = actor.get_actor_label()
        if label.startswith("TrainingDummy") or label.startswith("SevarogBoss") or label.startswith("EncounterTrigger"):
            actor.destroy_actor()

    boss = unreal.EditorLevelLibrary.spawn_actor_from_class(
        boss_bp.generated_class(), unreal.Vector(0.0, 0.0, 160.0), unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0))
    boss.set_actor_label("SevarogBoss")

    trigger = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.load_class(None, "/Script/OneBossFight.RPGEncounterTrigger"),
        unreal.Vector(-1100.0, 0.0, 200.0), unreal.Rotator(0.0, 0.0, 0.0))
    trigger.set_actor_label("EncounterTrigger")
    try:
        volume = trigger.get_editor_property("volume")
        volume.set_editor_property("box_extent", unreal.Vector(120.0, 1500.0, 300.0))
    except Exception as exc:
        log("Trigger extent not set (default used): %s" % exc)

    unreal.EditorLevelLibrary.save_current_level()
    log("L_Greybox: boss and encounter trigger placed.")


def main():
    unreal.EditorAssetLibrary.make_directory(BOSS_DIR)
    montages = {}
    for name, sequence, mode, radial in MONTAGES:
        montages[name] = build_montage(name, sequence, mode, radial)

    attacks = [build_attack(asset, montages[montage], boss_fields, attack_fields)
               for asset, montage, boss_fields, attack_fields in ATTACKS]
    weapon = build_weapon()
    boss_bp = configure_boss(montages, attacks, weapon)
    build_level(boss_bp)
    log("M4 content setup complete.")


main()
