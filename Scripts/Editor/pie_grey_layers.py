"""PIE check of every retargeted weapon layer on Greystone: links each layer class on the mesh, stands then runs, frames are tagged with the layer name
(CaptureLoop flag file). Open L_SevarogArena first (the boss sleeps behind his gate). Log prefix [GreyLayers]."""
import os
import unreal

log = lambda m: unreal.log("[GreyLayersPie] " + m)
FLAG = os.path.join(unreal.Paths.project_saved_dir(), "m7_flag.txt")
BASE = "/Game/OneBossFight/GreystonePack/"
LAYERS = [
    ("Unarmed", "Characters/Heroes/Mannequins/Animations/LinkedLayers/ABP_UnarmedLayer_Grey"),
    ("UnarmedShield", "Characters/Heroes/Mannequins/Animations/LinkedLayers/ABP_UnarmednShieldLayer_Grey"),
    ("Sword", "MeleeCombatSystem/Blueprints/Animation/AnimLayers/ABP_SwordLayer_Grey"),
    ("SwordShield", "MeleeCombatSystem/Blueprints/Animation/AnimLayers/ABP_SwordnShieldLayer_Grey"),
    ("2Handed", "MeleeCombatSystem/Blueprints/Animation/AnimLayers/ABP_2HandedSwordLayer_Grey"),
    ("DualSword", "MeleeCombatSystem/Blueprints/Animation/AnimLayers/ABP_DualSwordLayer_Grey"),
    ("Twinblade", "MeleeCombatSystem/Blueprints/Animation/AnimLayers/ABP_TwinbladeLayer_Grey"),
    ("MagicStaff", "MagicCombatSystem/Blueprints/Animation/ABP_MagicStaffLayer_Grey"),
]
STAND, RUN = 2.0, 1.6
state = {"phase": "start", "t": 0.0, "i": -1, "sub": 0.0, "mode": "stand"}
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
    mesh = pawn.get_components_by_class(unreal.SkeletalMeshComponent)[0]
    if s["phase"] == "wait":
        if s["t"] > 8.0:
            s.update(phase="layers", t=0.0, sub=99.0)
        return
    s["sub"] += dt
    limit = STAND if s["mode"] == "stand" else RUN
    if s["mode"] == "run":
        pawn.add_movement_input(pawn.get_actor_forward_vector(), 1.0, False)
    if s["sub"] > limit:
        s["sub"] = 0.0
        if s["mode"] == "stand" and s["i"] >= 0:
            s["mode"] = "run"
            flag("%s_run" % LAYERS[s["i"]][0])
            return
        s["mode"] = "stand"
        s["i"] += 1
        if s["i"] >= len(LAYERS):
            finish("done")
            return
        name, path = LAYERS[s["i"]]
        cls = unreal.load_object(None, BASE + path + "." + path.split("/")[-1] + "_C")
        log("layer %s class=%s" % (name, cls))
        if cls:
            mesh.link_anim_class_layers(cls)
        flag(name)


handle = unreal.register_slate_post_tick_callback(tick)
log("registered")
