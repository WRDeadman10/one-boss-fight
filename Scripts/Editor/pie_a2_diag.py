"""Diagnosis for the A2 scenarios: does the frozen boss have its sword in hand, does the forced move play, does the player lose health. Log prefix [A2D]."""
import unreal

log = lambda m: unreal.log("[A2D] " + m)
state = {"t": 0.0, "phase": "start", "step": 0}
handle = None


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def tags(*names):
    c = unreal.GameplayTagContainer()
    c.import_text("(GameplayTags=(%s))" % ",".join('(TagName="%s")' % n for n in names))
    return c


def hp(actor):
    c = comp(actor, "BP_AttributesComponent_C")
    t = unreal.GameplayTag()
    t.import_text('(TagName="Attribute.Health")')
    return c.call_method("Get Current Attribute Value", args=(t,))


def maxhp(actor):
    c = comp(actor, "BP_AttributesComponent_C")
    t = unreal.GameplayTag()
    t.import_text('(TagName="Attribute.Health")')
    try:
        return c.call_method("Get Max Attribute Value", args=(t,))
    except Exception as e:
        return "ERR"


def montage(actor):
    mc = actor.get_components_by_class(unreal.SkeletalMeshComponent)
    inst = mc[0].get_anim_instance() if mc else None
    m = inst.get_current_active_montage() if inst else None
    return "%s %.2f" % (m.get_name(), inst.montage_get_position(m)) if m else None


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
    if s["step"] == 0 and t > 9.0:
        enc = comp(boss, "RPGBossEncounter")
        enc.set_editor_property("test_freeze", True)
        asc = comp(boss, "BP_AdvancedAbilitySystemComponent_C")
        log("enter_combat -> %s" % comp(boss, "RPGAttackTracker").enter_combat())
        log("EnterCombat requested; player hp %s max %s" % (hp(pawn), maxhp(pawn)))
        s["step"] = 1
    if s["step"] == 1 and t > 14.0:
        for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor):
            n = a.get_class().get_name()
            if "Sword" in n or "Weapon" in n or "Kwang" in n:
                log("actor %s at %s parent %s" % (n, a.get_actor_location(), a.get_attach_parent_actor()))
        log("boss montage %s; attached actors: %s" % (montage(boss), [(a.get_name(), a.get_attach_parent_socket_name()) for a in boss.get_attached_actors()]))
        pawn.set_actor_location_and_rotation(unreal.Vector(boss.get_actor_location().x + 300, boss.get_actor_location().y, boss.get_actor_location().z), unreal.Rotator(0, 180, 0), False, True)
        boss.set_actor_rotation(unreal.Rotator(0, 0, 0), False)
        tr = comp(boss, "RPGAttackTracker")
        log("start_move -> %s" % tr.start_move("A2"))
        s["t1"] = t
        s["step"] = 2
    if s["step"] == 2:
        el = t - s["t1"]
        if int(el * 5) != s.get("last", -1):
            s["last"] = int(el * 5)
            log("t=%.1f boss montage %s player hp %s  dist %.0f" % (el, montage(boss), hp(pawn), (pawn.get_actor_location() - boss.get_actor_location()).length()))
        if el > 4.2:
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
