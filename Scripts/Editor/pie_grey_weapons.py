"""PIE check of weapon socket fit on Greystone: for each pack weapon actor, attach it to its own WeaponHandSocket then DisabledSocket (sheath) on Greystone's
mesh with the matching layer linked; frames tagged <weapon>_hand / <weapon>_sheath. Open L_SevarogArena first. Log prefix [GreyWeaponsPie]."""
import os
import unreal

log = lambda m: unreal.log("[GreyWeaponsPie] " + m)
FLAG = os.path.join(unreal.Paths.project_saved_dir(), "m7_flag.txt")
BASE = "/Game/OneBossFight/GreystonePack/"
W = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/"
LAYERS = BASE + "MeleeCombatSystem/Blueprints/Animation/AnimLayers/"
# name, actor Blueprint, layer, hand socket, sheath socket (the socket names come from the pack's item data assets: Items/Weapons/*, Items/Shields/*)
UNARMED = BASE + "Characters/Heroes/Mannequins/Animations/LinkedLayers/ABP_UnarmedLayer_Grey"
WEAPONS = [
    ("Polearm", W + "Polearms/BP_FengMaoWeapon", LAYERS + "ABP_2HandedSwordLayer_Grey", "FengMaoWeapon_Active", "FengMaoWeapon_Disabled"),
    ("Twinblade", W + "DualSwords/DualSwordInstances/BP_DualSteelSwords", LAYERS + "ABP_TwinbladeLayer_Grey", "Twinsword_R", "TwinbladeSheath_R"),
    ("Bow", "/Game/AdvancedARPGCombat/RangedCombatSystem/Blueprints/Weapons/Bow/BowInstances/BP_ElvenBow", UNARMED, "BowHandSocket", "BowAttachSocket"),
    ("Quiver", W + "Arrows/BP_PoisonArrows", UNARMED, "HuntingQuiverSocket", "HuntingQuiverSocket"),
    ("DualSwordL", W + "DualSwords/DualSwordInstances/BP_DualSteelSwords", LAYERS + "ABP_DualSwordLayer_Grey", "WeaponSocket_L", "DualSwordSheath_L"),
]
HAND, SHEATH = 2.0, 1.6
state = {"phase": "start", "t": 0.0, "i": -1, "sub": 99.0, "mode": "sheath", "actor": None}
handle = None


def flag(tag):
    if tag is None:
        if os.path.exists(FLAG):
            os.remove(FLAG)
    else:
        open(FLAG, "w").write(tag)


def finish(reason):
    global handle
    flag(None)
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("finished: " + reason)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish("error")


def attach(actor, mesh, socket):
    actor.get_editor_property("root_component").attach_to_component(mesh, socket, unreal.AttachmentRule.SNAP_TO_TARGET, unreal.AttachmentRule.SNAP_TO_TARGET, unreal.AttachmentRule.KEEP_WORLD, False)


def _tick(dt):
    s = state
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="wait", t=0.0)
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    if w is None:
        return
    pc = unreal.GameplayStatics.get_player_controller(w, 0)
    pawn = pc.get_controlled_pawn() if pc else None
    if pawn is None:
        return
    mesh = pawn.get_editor_property("mesh")
    if s["phase"] == "wait":
        if not s.get("listed"):
            s["listed"] = True
            for c in pawn.get_components_by_class(unreal.SkeletalMeshComponent):
                log("component %s mesh=%s WeaponSocket_R=%s ShieldSocket=%s" % (c.get_name(), c.get_editor_property("skeletal_mesh_asset").get_name() if c.get_editor_property("skeletal_mesh_asset") else None,
                    c.does_socket_exist("WeaponSocket_R"), c.does_socket_exist("ShieldSocket")))
        if s["t"] > 8.0:
            s["phase"] = "weapons"
        return
    s["sub"] += dt
    if s["sub"] < (HAND if s["mode"] == "hand" else SHEATH):
        return
    s["sub"] = 0.0
    if s["mode"] == "sheath" and s["i"] >= 0 and s.get("actor") is not None and not s.get("did_sheath"):
        pass
    if s["mode"] == "hand" and s["actor"] is not None:
        name = WEAPONS[s["i"]][0]
        socket = WEAPONS[s["i"]][4]
        attach(s["actor"], mesh, socket)
        flag("%s_sheath_%s" % (name, socket))
        s["mode"] = "sheath"
        return
    # next weapon
    if s["actor"] is not None:
        s["actor"].get_editor_property("root_component").detach_from_component(unreal.DetachmentRule.KEEP_WORLD, unreal.DetachmentRule.KEEP_WORLD, unreal.DetachmentRule.KEEP_WORLD)
        s["actor"].set_actor_location(unreal.Vector(0, 0, -5000), False, True)
        s["actor"] = None
    s["i"] += 1
    if s["i"] >= len(WEAPONS):
        finish("done")
        return
    name, path, layer, hand_socket, sheath_socket = WEAPONS[s["i"]]
    cls = unreal.load_object(None, path + "." + path.split("/")[-1] + "_C")
    lcls = unreal.load_object(None, layer + "." + layer.split("/")[-1] + "_C")
    if lcls:
        mesh.link_anim_class_layers(lcls)
    socket = hand_socket
    actor = next(iter(unreal.GameplayStatics.get_all_actors_of_class(w, cls)), None)  # pre-spawned in the editor world (PIE has no spawn from Python)
    attach(actor, mesh, socket)
    s["actor"] = actor
    s["mode"] = "hand"
    flag("%s_hand_%s" % (name, socket))
    log("%s attached to %s (socket exists: %s)" % (name, socket, mesh.does_socket_exist(socket)))


for name, path, layer, hand_socket, sheath_socket in WEAPONS:
    for old in unreal.EditorLevelLibrary.get_all_level_actors():
        if old.get_actor_label() == "GreyWeaponTest_" + name:
            old.destroy_actor()
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.load_object(None, path + "." + path.split("/")[-1] + "_C"), unreal.Vector(-1800, 0, 300))
    actor.set_actor_label("GreyWeaponTest_" + name)
handle = unreal.register_slate_post_tick_callback(tick)
log("registered")
