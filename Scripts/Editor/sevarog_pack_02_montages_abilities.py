"""Sevarog on the pack, step 2: pack-format attack montages and the boss ability copies. Run in the open editor, after step 1.

Montages: built from the same Paragon sequences as the C++ boss montages (AM_Sevarog_*), with the hit window from the scythe tip speed
(same method as setup_m4_content.py), but carrying the pack's notifies instead of our RPG ones:
  ANS_DisableMovement (whole attack), ANS_SetDesiredRotation (wind-up, face target), ANS_CollisionTrace (hit window, target tag
  TargetType.MainWeapon, event GameplayEvent.AttackHit), AN_EndAnimatingAbility (near the end).
Abilities: copies of GA_GS_Boss_* with Sevarog montages in their F_AbilityMontage arrays.
"""
import unreal

log = lambda m: unreal.log("[SevPack2] " + m)
PACK = "/Game/ParagonSevarog"
OUT = "/Game/OneBossFight/SevarogPack"
MONT = OUT + "/Montages"
ABIL = OUT + "/Abilities"
A = "/Game/AdvancedARPGCombat/"
GS = A + "MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/"
SLOT = "FullBody"
TIP_BONE = "root_weapon_end_r"

ANS_COLLISION = A + "AdvancedCombatFramework/CollisionSystem/AnimNotifies/ANS_CollisionTrace.ANS_CollisionTrace_C"
ANS_DISABLE = A + "AdvancedCombatFramework/CoreCombatSystem/AnimNotifies/ANS_DisableMovement.ANS_DisableMovement_C"
ANS_ROTATE = A + "AdvancedCombatFramework/CoreCombatSystem/AnimNotifies/ANS_SetDesiredRotation.ANS_SetDesiredRotation_C"
AN_END = A + "AdvancedCombatFramework/AbilitySystem/AnimNotifes/AN_EndAnimatingAbility.AN_EndAnimatingAbility_C"
KNOCKDOWN_DATA = A + "MeleeCombatSystem/Blueprints/DataAssets/AttackData/MeleeKnockdownAttackData"

# montage name -> (sequence, attack data override or None, hit window mode)
ATTACKS = {
    "AM_SevPack_Sweep": ("Swing1_Medium", None),
    "AM_SevPack_Backhand": ("Swing2_Medium", None),
    "AM_SevPack_Overhead": ("Swing3_Medium", None),
    "AM_SevPack_Lunge": ("Swing_In_Air", KNOCKDOWN_DATA),
    "AM_SevPack_Shockwave": ("Ultimate_Swing_120fps", KNOCKDOWN_DATA),
}


def load_class(path):
    cls = unreal.load_object(None, path)
    if cls is None:
        raise RuntimeError("Missing class " + path)
    return cls


def find_pack_asset(class_name, name):
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    registry.scan_paths_synchronous([PACK], True)
    for data in registry.get_assets_by_path(PACK, recursive=True):
        if str(data.asset_class_path.asset_name) == class_name and str(data.asset_name) == name:
            return data.get_asset()
    raise RuntimeError("Missing %s '%s'" % (class_name, name))


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
    times, speeds = sample_tip(sequence)
    smooth = [sum(speeds[max(0, i - 1):i + 2]) / len(speeds[max(0, i - 1):i + 2]) for i in range(len(speeds))]
    peak = smooth.index(max(smooth))
    threshold = 0.4 * smooth[peak]
    start = peak
    while start > 0 and smooth[start - 1] >= threshold:
        start -= 1
    end = peak
    while end < len(smooth) - 1 and smooth[end + 1] >= threshold:
        end += 1
    return times[start], times[end]


def face_target_value():
    """E_DesiredRotation is a Blueprint enum, so take FACE_TARGET from the pack's own montage notify."""
    ref = unreal.load_asset(A + "MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_Attack01_Montage")
    for ev in unreal.AnimationLibrary.get_animation_notify_events(ref):
        o = ev.get_editor_property("notify_state_class")
        if o is not None and o.get_class().get_name() == "ANS_SetDesiredRotation_C":
            return o.get_editor_property("Desired Rotation Type")
    raise RuntimeError("no rotation notify in reference montage")


FACE_TARGET = face_target_value()


def tag(name):
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % name)
    return t


def recreate(path, asset_class, factory):
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.delete_asset(path)
    folder, name = path.rsplit("/", 1)
    return unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, folder, asset_class, factory)


def build_montage(name, sequence_name, attack_data_path):
    sequence = find_pack_asset("AnimSequence", sequence_name)
    factory = unreal.AnimMontageFactory()
    factory.set_editor_property("source_animation", sequence)
    montage = recreate(MONT + "/" + name, unreal.AnimMontage, factory)
    unreal.RPGMontageUtils.set_montage_slot(montage, SLOT)
    length = montage.get_play_length()
    start, end = motion_window(sequence)
    track = "PackCombat"
    lib = unreal.AnimationLibrary
    lib.add_animation_notify_track(montage, track)
    lib.add_animation_notify_state_event(montage, track, 0.0, length * 0.9, load_class(ANS_DISABLE))
    rot = lib.add_animation_notify_state_event(montage, track, 0.0, max(start * 0.9, 0.1), load_class(ANS_ROTATE))
    rot.set_editor_property("RotationInterpSpeed", 520.0)
    rot.set_editor_property("Desired Rotation Type", FACE_TARGET)
    trace = lib.add_animation_notify_state_event(montage, track, start, max(end - start, 0.05), load_class(ANS_COLLISION))
    trace.set_editor_property("Collision Target Tag", tag("TargetType.MainWeapon"))
    trace.set_editor_property("EventTag", tag("GameplayEvent.AttackHit"))
    trace.set_editor_property("TraceRadiusModifier", 0.0)
    if attack_data_path:
        trace.set_editor_property("AttackData", unreal.load_asset(attack_data_path))
    end_notify = lib.add_animation_notify_event(montage, track, length * 0.9, load_class(AN_END))
    unreal.EditorAssetLibrary.save_loaded_asset(montage)
    try:
        root = sequence.get_editor_property("enable_root_motion")
    except Exception:
        root = "?"
    log("%s: %.2fs window %.2f-%.2f root_motion_in_sequence=%s" % (name, length, start, end, root))
    return montage


def ability_montage(template_struct, montage, end_type_text=None):
    """A copy of an F_AbilityMontage struct with another montage object."""
    text = template_struct.export_text()
    import re
    text = re.sub(r'AnimMontage_5_[0-9A-F]+="[^"]*"', lambda m: 'AnimMontage_5_2620D50C4D110CA156B1A28F49A30836="%s"' % ("/Script/Engine.AnimMontage'%s'" % montage.get_path_name()), text)
    text = re.sub(r"AbilityEndType_32_[0-9A-F]+=NewEnumerator\d", "AbilityEndType_32_951260D64E59D4A64784A3872E20F496=NewEnumerator0", text)
    template_struct.import_text(text)
    return template_struct


def duplicate(src, dst):
    if unreal.EditorAssetLibrary.does_asset_exist(dst):
        unreal.EditorAssetLibrary.delete_asset(dst)
    asset = unreal.EditorAssetLibrary.duplicate_asset(src, dst)
    if asset is None:
        raise RuntimeError("duplicate failed %s -> %s" % (src, dst))
    return asset


def set_attack_montages(ga_name, montages, prop="AttackMontages"):
    asset = unreal.load_asset(ABIL + "/" + ga_name)
    cdo = unreal.get_default_object(asset.generated_class())
    template = cdo.get_editor_property(prop)[0]
    new = []
    for m in montages:
        s = cdo.get_editor_property(prop)[0]
        new.append(ability_montage(s, m))
    cdo.set_editor_property(prop, new)
    asset.modify()  # without this a CDO-only edit is not written by the save
    unreal.BlueprintEditorLibrary.compile_blueprint(asset)
    unreal.EditorAssetLibrary.save_loaded_asset(asset, False)
    log("%s.%s = %s" % (ga_name, prop, [m.get_name() for m in montages]))


def set_single_montage(ga_name, prop, montage):
    asset = unreal.load_asset(ABIL + "/" + ga_name)
    cdo = unreal.get_default_object(asset.generated_class())
    cdo.set_editor_property(prop, ability_montage(cdo.get_editor_property(prop), montage))
    asset.modify()  # without this a CDO-only edit is not written by the save
    unreal.BlueprintEditorLibrary.compile_blueprint(asset)
    unreal.EditorAssetLibrary.save_loaded_asset(asset, False)
    log("%s.%s = %s" % (ga_name, prop, montage.get_name()))


ONLY_TOGGLE = globals().get('ONLY_TOGGLE', False)  # set True to rebuild just the entrance / exit montages (keeps the ability assets)
if not ONLY_TOGGLE:
    unreal.EditorAssetLibrary.make_directory(MONT)
    unreal.EditorAssetLibrary.make_directory(ABIL)

    montages = {name: build_montage(name, seq, data) for name, (seq, data) in ATTACKS.items()}
    entrance = unreal.load_asset("/Game/OneBossFight/Boss/AM_Sevarog_Entrance")
    roar = unreal.load_asset("/Game/OneBossFight/Boss/AM_Sevarog_PhaseRoar")
    hitreact = unreal.load_asset("/Game/OneBossFight/Boss/AM_Sevarog_HitReact")

    for ga in ("CloseAttack", "CloseRare", "EnterCombat", "ExitCombat", "HitStun", "LeapAttack", "MidRangeAttack", "RetaliationAttack", "SprintAttack"):
        duplicate(GS + "GA_GS_Boss_" + ga, ABIL + "/GA_Sev_" + ga)

    set_attack_montages("GA_Sev_CloseAttack", [montages["AM_SevPack_Sweep"], montages["AM_SevPack_Backhand"], montages["AM_SevPack_Overhead"]])
    set_attack_montages("GA_Sev_CloseRare", [montages["AM_SevPack_Shockwave"]])
    set_attack_montages("GA_Sev_MidRangeAttack", [montages["AM_SevPack_Overhead"]])
    set_attack_montages("GA_Sev_LeapAttack", [montages["AM_SevPack_Lunge"]])
    set_attack_montages("GA_Sev_SprintAttack", [montages["AM_SevPack_Overhead"]])
    set_attack_montages("GA_Sev_RetaliationAttack", [montages["AM_SevPack_Backhand"]])
    set_single_montage("GA_Sev_EnterCombat", "Enter Combat Montage", entrance)
    set_single_montage("GA_Sev_ExitCombat", "ExitCombatMontage", roar)

    # Hit stun: the same Sevarog reaction for every direction.
    hs = unreal.load_asset(ABIL + "/GA_Sev_HitStun")
    cdo = unreal.get_default_object(hs.generated_class())
    react = cdo.get_editor_property("Hit React Montages")
    for key in list(react.keys()):
        react[key] = ability_montage(react[key], hitreact)
    cdo.set_editor_property("Hit React Montages", react)
    hs.modify()
unreal.BlueprintEditorLibrary.compile_blueprint(hs)
    unreal.EditorAssetLibrary.save_loaded_asset(hs, False)
    log("GA_Sev_HitStun directions = %d -> AM_Sevarog_HitReact" % len(list(react.keys())))


# ---- entrance / exit combat montages: copies carrying the pack's combat toggle and ability end notifies -------------------------
AN_TOGGLE = A + "AdvancedCombatFramework/CoreCombatSystem/AnimNotifies/AN_ToggleCombat.AN_ToggleCombat_C"


def toggle_copy(src_path, name, toggle_at, end_at):
    dst = MONT + "/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(dst):
        unreal.EditorAssetLibrary.delete_asset(dst)
    src = unreal.load_asset(src_path)
    m = unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset(name, MONT, src)
    lib = unreal.AnimationLibrary
    lib.add_animation_notify_track(m, "PackCombat")
    lib.add_animation_notify_event(m, "PackCombat", toggle_at, load_class(AN_TOGGLE))
    lib.add_animation_notify_event(m, "PackCombat", end_at, load_class(AN_END))
    unreal.EditorAssetLibrary.save_loaded_asset(m)
    log("%s: %.2fs toggle %.2f end %.2f" % (name, m.get_play_length(), toggle_at, end_at))
    return m


ent = toggle_copy("/Game/OneBossFight/Boss/AM_Sevarog_Entrance", "AM_SevPack_Entrance", 3.5, 3.9)
ext = toggle_copy("/Game/OneBossFight/Boss/AM_Sevarog_PhaseRoar", "AM_SevPack_Exit", 0.3, 0.6)
set_single_montage("GA_Sev_EnterCombat", "Enter Combat Montage", ent)
set_single_montage("GA_Sev_ExitCombat", "ExitCombatMontage", ext)
