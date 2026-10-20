"""Where does the pack boss get its sword? Wakes the boss by proximity and logs its montage, state and weapon-like actors each second for 25 s. Log prefix [Arm]."""
import unreal

log = lambda m: unreal.log("[Arm] " + m)
state = {"t": 0.0, "phase": "start", "moved": False, "last": -1}
handle = None


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def montage(actor):
    mc = actor.get_components_by_class(unreal.SkeletalMeshComponent)
    inst = mc[0].get_anim_instance() if mc else None
    m = inst.get_current_active_montage() if inst else None
    return m.get_name() if m else None


def _tick(dt):
    global handle
    s = state
    s["t"] += dt
    if s["phase"] == "start" and s["t"] > 0.5:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
        s.update(phase="play", t=0.0)
        return
    if s["phase"] != "play":
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    if w is None:
        return
    pc = unreal.GameplayStatics.get_player_controller(w, 0)
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None)
    if pawn is None or boss is None:
        return
    t = s["t"]
    if not s["moved"] and t > 9.0:
        pawn.set_actor_location_and_rotation(unreal.Vector(boss.get_actor_location().x + 700, boss.get_actor_location().y, boss.get_actor_location().z), unreal.Rotator(0, 180, 0), False, True)
        s["moved"] = True
        s["t0"] = t
        log("player moved next to the boss")
    if s["moved"] and int((t - s["t0"]) * 1) != s["last"]:
        s["last"] = int(t - s["t0"])
        enc = comp(boss, "RPGBossEncounter")
        weapons = [(a.get_class().get_name(), str(a.get_attach_parent_actor().get_name()) if a.get_attach_parent_actor() else None) for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor)
                   if any(k in a.get_class().get_name() for k in ("Sword", "Weapon", "Kwang", "Great"))]
        log("t=%d dormant=%s montage=%s weapons=%s" % (s["last"], enc.is_dormant(), montage(boss), weapons))
        hdbg = comp(boss, "RPGCombatDebug")
        if hdbg:
            hdbg.debug_refill_player()
    if s["moved"] and t - s["t0"] > 26:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
        log("done")


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())


handle = unreal.register_slate_post_tick_callback(tick)
