"""
PIE check of the audio components: the player walks and runs forward (add_movement_input) and its footstep component must count steps; the boss stays dormant
(no music) until the player enters its gate, then the boss music must start; after a health reset to 0 for the boss the music must stop.
Log prefix [AudioPie]. Open L_SevarogArena first; run with Scripts/run_in_editor.py (editor throttling off).
"""
import unreal

log = lambda m: unreal.log("[AudioPie] " + m)
state = {"phase": "start", "t": 0.0, "stage": "idle", "t0": 0.0, "steps0": 0, "events": []}
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
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("finished: " + reason)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def check(name, ok, detail=""):
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))
    state["events"].append((name, ok))


def _tick(dt):
    s = state
    s["t"] += dt
    if s["t"] > 90.0:
        finish("timeout")
        return
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0)
        return
    w = world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next(iter([a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"]), None) if w else None
    if pawn is None or boss is None:
        return
    steps, music, enc = comp(pawn, "RPGFootsteps"), comp(boss, "RPGBossMusic"), comp(boss, "RPGBossEncounter")
    boss_steps = comp(boss, "RPGFootsteps")
    if steps is None or music is None or enc is None or boss_steps is None:
        check("components attached", False, "(player steps %s, boss steps %s, music %s, encounter %s)" % (steps, boss_steps, music, enc))
        finish("missing components")
        return
    el = s["t"] - s["t0"]
    if s["stage"] == "idle" and s["t"] > 6.0:
        check("boss music silent while the boss sleeps", enc.is_dormant() and not music.is_playing())
        s["steps0"] = steps.get_step_count()
        s.update(stage="walk", t0=s["t"])
    elif s["stage"] == "walk":
        pawn.add_movement_input(unreal.Vector(0, 1 if int(el / 2.0) % 2 == 0 else -1, 0), 0.5)  # walk speed, sideways back and forth (stays out of the boss gate)
        s["dbg"] = s.get("dbg", 0.0) + dt
        if s["dbg"] > 0.7:
            s["dbg"] = 0.0
            m = pawn.get_components_by_class(unreal.SkeletalMeshComponent)[0]
            v = pawn.get_velocity()
            log("   speed %.0f at %.0f,%.0f z %.0f foot_l z %.1f foot_r z %.1f steps %d" % (v.length(), pawn.get_actor_location().x, pawn.get_actor_location().y, pawn.get_actor_location().z, m.get_socket_location("foot_l").z, m.get_socket_location("foot_r").z, steps.get_step_count()))
        if el > 8.0:
            n = steps.get_step_count() - s["steps0"]
            check("walking makes footsteps", n >= 5, "(%d steps in 8 s)" % n)
            s["steps0"] = steps.get_step_count()
            s.update(stage="run", t0=s["t"])
    elif s["stage"] == "run":
        pawn.add_movement_input(unreal.Vector(0, 1 if int(el / 1.0) % 2 == 0 else -1, 0), 1.0)
        if el > 2.5:
            n = steps.get_step_count() - s["steps0"]
            check("running makes more footsteps than walking", n >= 4, "(%d steps in 2.5 s)" % n)
            s.update(stage="gate", t0=s["t"])
            pawn.set_actor_location(unreal.Vector(-900, 0, 110), False, True)
    elif s["stage"] == "gate":
        if el > 3.5:
            check("music starts once the boss wakes", (not enc.is_dormant()) and music.is_playing(), "(dormant %s, playing %s)" % (enc.is_dormant(), music.is_playing()))
            c = comp(boss, "BP_AttributesComponent_C")
            t = unreal.GameplayTag()
            t.import_text('(TagName="Attribute.Health")')
            c.call_method("Set Current Attribute Value", args=(t, 0.0))
            s.update(stage="death", t0=s["t"])
    elif s["stage"] == "death":
        if el > 2.0:
            check("music stops when the boss dies", not music.is_playing())
            fails = [n for n, ok in s["events"] if not ok]
            finish("%d checks, %d failed %s" % (len(s["events"]), len(fails), fails))


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish("error")


assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name() == "L_SevarogArena", "open L_SevarogArena first"
handle = unreal.register_slate_post_tick_callback(tick)
