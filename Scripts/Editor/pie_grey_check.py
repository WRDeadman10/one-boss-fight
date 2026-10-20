"""
PIE visual check of the Greystone player on the Advanced ARPG framework. Run via execute_script with the pack demo level open and
Scripts/CaptureLoop.ps1 running. Phases: idle, enter combat, three attacks, dodge. Frames are tagged through Saved/m7_flag.txt.
Log prefix [GreyCheck].
"""
import os
import unreal

log = lambda m: unreal.log("[GreyCheck] " + m)
FLAG = os.path.join(unreal.Paths.project_saved_dir(), "m7_flag.txt")


def flag(tag):
    if tag is None:
        if os.path.exists(FLAG):
            os.remove(FLAG)
    else:
        open(FLAG, "w").write(tag)


def tags(*names):
    c = unreal.GameplayTagContainer()
    c.import_text("(GameplayTags=(%s))" % ",".join('(TagName="%s")' % n for n in names))
    return c


STEPS = [
    ("idle", None, 3.0),
    ("combat", "Ability.EnterCombat", 3.0),
    ("attack1", "Ability.Melee", 1.6),
    ("attack2", "Ability.Melee", 1.6),
    ("attack3", "Ability.Melee", 1.6),
    ("dodge", "Ability.Dodge", 2.0),
    ("idle2", None, 1.5),
]
state = {"phase": "start", "t": 0.0, "step": -1, "step_t": 0.0}
handle = None


def world():
    try:
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    except Exception:
        return None


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


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
    w = world()
    if w is None:
        return
    pc = unreal.GameplayStatics.get_player_controller(w, 0)
    pawn = pc.get_controlled_pawn() if pc else None
    if pawn is None:
        return
    if s["phase"] == "wait":
        if s["t"] > 25.0:
            log("pawn %s mesh %s" % (pawn.get_class().get_name(), pawn.get_components_by_class(unreal.SkeletalMeshComponent)[0].get_editor_property("skeletal_mesh_asset").get_name()))
            # clear the area: move to an open spot of the demo level facing the wall text
            s.update(phase="steps", t=0.0, step=-1, step_t=99.0)
        return
    if s["phase"] == "steps":
        s["step_t"] += dt
        step = STEPS[s["step"]] if s["step"] >= 0 else None
        if step is None or s["step_t"] > step[2]:
            s["step"] += 1
            if s["step"] >= len(STEPS):
                finish("steps done")
                return
            name, tag, _ = STEPS[s["step"]]
            s["step_t"] = 0.0
            flag(name)
            if tag:
                asc = comp(pawn, "BP_AdvancedAbilitySystemComponent_C")
                try:
                    r = asc.call_method("Try Activate Abilities By Tag", args=(tags(tag),))
                except Exception as e:
                    r = "ERR " + str(e)[:100]
                log("step %s (%s) -> %s" % (name, tag, r))
            else:
                log("step %s" % name)


handle = unreal.register_slate_post_tick_callback(tick)
log("registered")
