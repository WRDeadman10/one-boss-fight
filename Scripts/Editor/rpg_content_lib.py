"""
Shared helpers for the editor content scripts (used by setup_m5_content.py).
Import with:  sys.path.insert(0, <this folder>); import rpg_content_lib as lib
"""

import unreal


def log(msg):
    unreal.log("[ContentLib] " + msg)


def find_asset(root, class_name, name):
    """Find an asset by class and name anywhere under root (e.g. /Game/ParagonGreystone)."""
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    registry.scan_paths_synchronous([root], True)
    for data in registry.get_assets_by_path(root, recursive=True):
        if str(data.asset_class_path.asset_name) == class_name and str(data.asset_name) == name:
            return data.get_asset()
    raise RuntimeError("Missing %s '%s' under %s" % (class_name, name, root))


def recreate(path, asset_class, factory):
    """Create an asset, replacing any previous version so reruns are deterministic."""
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.delete_asset(path)
    folder, name = path.rsplit("/", 1)
    return unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, folder, asset_class, factory)


def sample_tip_speeds(sequence, tip_bone):
    """(times, speeds in cm/s) of a bone in component space across the sequence."""
    length = sequence.get_play_length()
    steps = max(8, int(length * 30))
    times = [length * i / steps for i in range(steps + 1)]
    chain = list(reversed(unreal.AnimationLibrary.find_bone_path_to_root(sequence, tip_bone)))
    points = []
    for t in times:
        component = unreal.Transform()
        for bone in chain:
            local = unreal.AnimationLibrary.get_bone_pose_for_time(sequence, bone, t, False)
            component = unreal.MathLibrary.compose_transforms(local, component)
        points.append(component.translation)
    speeds = [0.0] + [(points[i] - points[i - 1]).length() / (times[i] - times[i - 1]) for i in range(1, len(points))]
    return times, speeds


def motion_window(sequence, tip_bone, fallback=(0.35, 0.6)):
    """(start, end, peak_time, how): the run around the fastest movement, from 40 % of peak speed."""
    length = sequence.get_play_length()
    try:
        times, speeds = sample_tip_speeds(sequence, tip_bone)
    except Exception as exc:
        log("Tip sampling failed for %s: %s" % (sequence.get_name(), exc))
        return length * fallback[0], length * fallback[1], length * 0.5, "fallback"
    smooth = [sum(speeds[max(0, i - 1):i + 2]) / len(speeds[max(0, i - 1):i + 2]) for i in range(len(speeds))]
    peak = smooth.index(max(smooth))
    if smooth[peak] < 1.0:
        return length * fallback[0], length * fallback[1], length * 0.5, "fallback (no motion)"
    threshold = 0.4 * smooth[peak]
    start = peak
    while start > 0 and smooth[start - 1] >= threshold:
        start -= 1
    end = peak
    while end < len(smooth) - 1 and smooth[end + 1] >= threshold:
        end += 1
    return times[start], times[end], times[peak], "motion"


def make_attack_montage(folder, asset_name, pack_root, sequence_name, tip_bone, slot, combo=True):
    """Montage from a sequence, in the given slot, with hit/combo/cancel windows placed from the tip speed."""
    sequence = find_asset(pack_root, "AnimSequence", sequence_name)
    factory = unreal.AnimMontageFactory()
    factory.set_editor_property("source_animation", sequence)
    montage = recreate(folder + "/" + asset_name, unreal.AnimMontage, factory)
    unreal.RPGMontageUtils.set_montage_slot(montage, slot)

    length = montage.get_play_length()
    start, end, _, how = motion_window(sequence, tip_bone)
    track = "RPGCombat"
    unreal.AnimationLibrary.add_animation_notify_track(montage, track)
    unreal.AnimationLibrary.add_animation_notify_state_event(montage, track, start, max(end - start, 0.02), unreal.RPGANS_HitWindow)
    if combo:
        combo_start = min(end + 0.05, length - 0.2)
        unreal.AnimationLibrary.add_animation_notify_state_event(
            montage, track, combo_start, max(length - 0.05 - combo_start, 0.02), unreal.RPGANS_ComboWindow)
    cancel_start = min(end + 0.1, length - 0.1)
    unreal.AnimationLibrary.add_animation_notify_state_event(
        montage, track, cancel_start, max(length - cancel_start, 0.02), unreal.RPGANS_CancelWindow)

    unreal.EditorAssetLibrary.save_loaded_asset(montage)
    log("%s from %s: %.2fs, hit window %.2f-%.2fs (%s)" % (asset_name, sequence_name, length, start, end, how))
    return montage


def make_plain_montage(folder, asset_name, pack_root, sequence_name, slot):
    sequence = find_asset(pack_root, "AnimSequence", sequence_name)
    factory = unreal.AnimMontageFactory()
    factory.set_editor_property("source_animation", sequence)
    montage = recreate(folder + "/" + asset_name, unreal.AnimMontage, factory)
    unreal.RPGMontageUtils.set_montage_slot(montage, slot)
    unreal.EditorAssetLibrary.save_loaded_asset(montage)
    return montage


def attack_struct(montage, damage, poise, stamina, unblockable=False, play_rate=1.0):
    attack = unreal.RPGAttackData()
    attack.set_editor_property("montage", montage)
    attack.set_editor_property("damage", damage)
    attack.set_editor_property("poise_damage", poise)
    attack.set_editor_property("stamina_cost", stamina)
    attack.set_editor_property("unblockable", unblockable)
    attack.set_editor_property("play_rate", play_rate)
    return attack


def quit_editor_soon(ticks=90):
    """Quit a real editor a little after startup. Quitting inside the startup script crashes the level editor."""
    state = {"n": 0, "handle": None}

    def tick(_delta):
        state["n"] += 1
        if state["n"] >= ticks:
            unreal.unregister_slate_post_tick_callback(state["handle"])
            unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")

    state["handle"] = unreal.register_slate_post_tick_callback(tick)
