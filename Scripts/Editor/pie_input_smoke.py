"""
PIE input smoke test: starts PIE, then presses real keys through the player controller's input pipeline
(so mappings and modifiers are exercised) and logs what the character did. Editor needs -unattended and focus.
Results: [InputDrive] lines in the Output Log.
"""
import unreal

LOG = "[InputDrive] "
state = {"phase": "start", "t": 0.0, "step": 0, "mark": None}
handle = None


def log(msg):
    unreal.log(LOG + msg)


def game_world():
    try:
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    except Exception:
        return None


def finish(reason):
    global handle
    if handle is not None:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    try:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    except Exception:
        pass
    log("finished: " + reason)


def action(name):
    return unreal.load_asset("/Game/OneBossFight/Input/" + name)


_subsystem = {}


def inject(pc, action_name, value=(1.0, 0.0, 0.0)):
    """Feeds an Enhanced Input action as if its mapped key were held this frame (bypasses key mapping)."""
    if "s" not in _subsystem:
        _subsystem["s"] = unreal.SubsystemBlueprintLibrary.get_local_player_subsystem(pc, unreal.EnhancedInputLocalPlayerSubsystem)
    ss = _subsystem["s"]
    ss.inject_input_vector_for_action(action(action_name), unreal.Vector(*value), [], [])


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error: " + traceback.format_exc())
        finish("error")


def _tick(dt):
    s = state
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="wait", t=0.0)
        return
    world = game_world()
    if world is None:
        if s["phase"] != "wait":
            finish("PIE ended")
        return
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    pawn = pc.get_controlled_pawn() if pc else None
    if pawn is None:
        if s["t"] > 20:
            finish("no pawn")
        return
    combat = pawn.get_components_by_class(unreal.RPGCombatComponent)[0]
    attr = pawn.get_components_by_class(unreal.RPGAttributeComponent)[0]

    # Script: (seconds from start of step, action)
    if s["phase"] == "wait":
        if s["t"] > 3.0:
            s.update(phase="run", t=0.0, step=0, mark=pawn.get_actor_location())
            log("start location %s yaw %.0f" % (pawn.get_actor_location(), pc.get_control_rotation().yaw))
        return

    # Each step injects the action every frame for `duration` seconds, then reports what the character did.
    steps = [
        ("move forward (IA_Move 0,1)", "IA_Move", (0.0, 1.0, 0.0), 1.0, False),
        ("move right (IA_Move 1,0)", "IA_Move", (1.0, 0.0, 0.0), 1.0, False),
        ("dodge (IA_Dodge) standing", "IA_Dodge", (1.0, 0.0, 0.0), 0.2, True),
        ("light attack (IA_LightAttack)", "IA_LightAttack", (1.0, 0.0, 0.0), 0.2, True),
        ("block (IA_Block) hold", "IA_Block", (1.0, 0.0, 0.0), 0.6, False),
    ]
    if s["step"] >= len(steps):
        finish("all steps done")
        return

    name, action_name, value, duration, once = steps[s["step"]]
    if s.get("started") != s["step"]:
        s["started"] = s["step"]
        s["t"] = 0.0
        s["mark"] = pawn.get_actor_location()
        s["states"] = set()
        s["stamina0"] = attr.get_stamina()
        s["fired"] = False
        return
    if s["t"] < 0:
        return
    if not (once and s["fired"]):
        inject(pc, action_name, value)
        s["fired"] = True
    s["states"].add(str(combat.get_state()).split(".")[-1].split(":")[0].strip("<> "))
    if s["t"] > duration:
        moved = pawn.get_actor_location() - s["mark"]
        log("%s: moved dx=%.0f dy=%.0f states=%s stamina %.0f -> %.0f" % (
            name, moved.x, moved.y, sorted(s["states"]), s["stamina0"], attr.get_stamina()))
        s["step"] += 1
        s["t"] = -1.2  # settle between steps


handle = unreal.register_slate_post_tick_callback(tick)
log("driver registered")
