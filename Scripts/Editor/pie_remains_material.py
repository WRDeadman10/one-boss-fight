"""Look test of M_Boss01_Remains (log prefix [RemainsLook]): in PIE gives the corpse statue actor RemainsLook the three slot MIDs, and takes a shot at Dissolve 0.35, 0.6 and 1.0. Needs the scratch actor RemainsLook (Scripts/Editor/place_remains_look.py places it, remove_remains_look.py removes it)."""
import unreal

log = lambda m: unreal.log("[RemainsLook] " + m)
state = {"t": 0.0, "step": 0, "wait": 9.0, "phase": "start", "actor": None}
handle = None
SLOTS = {"M_Boss01_AshPlate": ((0.10, 0.095, 0.09), 0.0), "M_Boss01_EmberCore": ((0.9, 0.28, 0.04), 0.45), "M_Boss01_AncientSteel": ((0.05, 0.055, 0.065), 0.0)}
LEVELS = [0.6, 1.0]


def _tick(dt):
    global handle
    s = state
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0)
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    if pawn is None or s["t"] < s["wait"]:
        return
    mesh = unreal.load_asset("/Game/OneBossFight/Boss01/Remains/SM_Boss01_CorpseStatue")
    base = unreal.load_asset("/Game/OneBossFight/Boss01/Remains/M_Boss01_Remains")
    if s["actor"] is None:
        a = next((x for x in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.StaticMeshActor) if x.get_actor_label() == "RemainsLook"), None)
        if a is None:
            raise RuntimeError("no RemainsLook actor: place it first with Scripts/Editor/place_remains_look.py")
        comp = a.static_mesh_component
        mids = []
        for i, slot in enumerate(mesh.get_editor_property("static_materials")):
            tint, glow = SLOTS[str(slot.material_slot_name)]
            m = comp.create_dynamic_material_instance(i, base)
            m.set_vector_parameter_value("Tint", unreal.LinearColor(tint[0], tint[1], tint[2], 1.0))
            m.set_scalar_parameter_value("CoreGlow", glow)
            mids.append(m)
        s["actor"], s["mids"] = a, mids
        o, e = a.get_actor_bounds(False)
        p = unreal.Vector(o.x + 300.0, o.y - 270.0, 140.0)
        yaw = unreal.MathLibrary.find_look_at_rotation(p, unreal.Vector(o.x, o.y, o.z)).yaw
        pawn.set_actor_hidden_in_game(True)  # the third-person camera sits behind the pawn: it would stand in front of the statue
        pawn.set_actor_location_and_rotation(p, unreal.Rotator(0, 0, yaw), False, True)
        pc.set_control_rotation(unreal.Rotator(roll=0, pitch=-10, yaw=yaw))
        log("statue bounds origin (%.0f %.0f %.0f) extent (%.0f %.0f %.0f)" % (o.x, o.y, o.z, e.x, e.y, e.z))
        s["wait"] = s["t"] + 2.0
        return
    i = s["step"] // 2
    if i >= len(LEVELS):
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
        log("done")
        return
    if s["step"] % 2 == 0:
        for m in s["mids"]:
            m.set_scalar_parameter_value("Dissolve", LEVELS[i])
        s["wait"] = s["t"] + 1.5
    else:
        unreal.SystemLibrary.execute_console_command(w, "Shot ShowUI")
        log("shot Dissolve %.2f" % LEVELS[i])
        s["wait"] = s["t"] + 1.5
    s["step"] += 1


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())


handle = unreal.register_slate_post_tick_callback(tick)
