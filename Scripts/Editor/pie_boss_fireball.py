"""
PIE probe: can the pack great-sword boss be given the pack magic enemy's fireball ability (GA_Fireball_Enemy) at runtime and fire it at the player? The player stands
900 cm away; the boss is woken, given the ability (Give Ability) and made to activate it (Try Activate Ability by Class). Logs the boss's montages, any new actors
whose class name suggests a projectile or effect, and the player's health. Log prefix [FirePie]. Open L_SevarogArena first; run with Scripts/run_in_editor.py.
"""
import unreal

log = lambda m: unreal.log("[FirePie] " + m)
ABILITY = "/Game/AdvancedARPGCombat/MagicCombatSystem/Blueprints/AI/ExampleMagicEnemy/GA_Fireball_Enemy.GA_Fireball_Enemy_C"
state = {"phase": "start", "t": 0.0, "stage": 0, "t0": 0.0, "last_m": None, "seen": set(), "hp0": None}
handle = None


def world():
    try:
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    except Exception:
        return None


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def attr(actor, tag):
    c = comp(actor, "BP_AttributesComponent_C")
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % tag)
    return c.call_method("Get Current Attribute Value", args=(t,)) if c else None


def montage_of(actor):
    mc = actor.get_components_by_class(unreal.SkeletalMeshComponent)
    inst = mc[0].get_anim_instance() if mc else None
    m = inst.get_current_active_montage() if inst else None
    return m.get_name() if m else None


def finish(reason):
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("finished: " + reason)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def _tick(dt):
    s = state
    s["t"] += dt
    if s["t"] > 60:
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
    enc = comp(boss, "RPGBossEncounter")
    asc = comp(boss, "BP_AdvancedAbilitySystemComponent_C")
    m = montage_of(boss)
    if m != s["last_m"]:
        s["last_m"] = m
        log("   boss montage -> %s" % m)
    for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor):
        n = a.get_class().get_name()
        if n not in s["seen"] and any(k in n for k in ("Fire", "Projectile", "Ball", "Cue", "Impact", "Niagara")):
            s["seen"].add(n)
            log("   new actor %s at %s" % (n, a.get_actor_location().to_tuple() if hasattr(a.get_actor_location(), "to_tuple") else a.get_actor_location()))
    el = s["t"] - s["t0"]
    if s["stage"] == 0 and s["t"] > 7.0:
        s["hp0"] = attr(pawn, "Attribute.Health")
        enc.wake()
        s.update(stage=1, t0=s["t"])
        pawn.set_actor_location_and_rotation(unreal.Vector(-900, 0, 110), unreal.Rotator(0, 0, 0), False, True)
        log("== woke the boss, player at 900 cm")
    elif s["stage"] == 1 and el > 2.5:
        cls = unreal.load_object(None, ABILITY)
        log("ability class: %s" % cls)
        try:
            given = asc.call_method("Give Ability", args=(cls, 1))
            log("Give Ability -> %s" % str(given)[:120])
        except Exception as e:
            log("Give Ability failed: %s" % str(e)[:160])
        try:
            ok = asc.call_method("Try Activate Ability by Class", args=(cls, True))
            log("Try Activate Ability by Class -> %s" % ok)
        except Exception as e:
            log("Try Activate failed: %s" % str(e)[:160])
        s.update(stage=2, t0=s["t"])
    elif s["stage"] == 2 and el > 6.0:
        log("player health %s -> %s" % (s["hp0"], attr(pawn, "Attribute.Health")))
        finish("done")


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish("error")


assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name() == "L_SevarogArena", "open L_SevarogArena first"
handle = unreal.register_slate_post_tick_callback(tick)
