"""
PIE test of enemy poise: the player (kept alive) stands next to a sword enemy and fires the melee attack ability by tag
every 1.5 s. Logs the enemy's poise, health and hit-reaction montage with [PoiseEnemy].
"""
import unreal

log = lambda m: unreal.log("[PoiseEnemy] " + m)
POISE = unreal.GameplayTag(); POISE.import_text('(TagName="Attribute.Poise")')
HEALTH = unreal.GameplayTag(); HEALTH.import_text('(TagName="Attribute.Health")')
ATTACK = unreal.GameplayTagContainer()
state = {"phase": "start", "t": 0.0, "last": None, "next_attack": 0.0, "enemy": None}
handle = None


def world():
    try:
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    except Exception:
        return None


def comp(actor, class_name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == class_name), None)


def value(c, tag):
    try:
        return c.call_method("Get Current Attribute Value", args=(tag,))
    except Exception as e:
        return "ERR " + str(e)[:60]


def finish(reason):
    global handle
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
    p_attr = comp(pawn, "BP_AttributesComponent_C")
    asc = comp(pawn, "BP_AdvancedAbilitySystemComponent_C")
    if s["phase"] == "wait":
        if s["t"] > 20.0:
            enemies = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleSwordEnemy_C"]
            s["enemy"] = enemies[0]
            e = s["enemy"]
            tag = unreal.GameplayTag(); tag.import_text('(TagName="Ability.Attack")')
            ATTACK.import_text('(GameplayTags=((TagName="Ability.Attack")))')
            # stand 160 cm in front of the enemy, facing it
            loc = e.get_actor_location() + e.get_actor_forward_vector() * 160.0
            pawn.set_actor_location(loc, False, True)
            pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(loc, e.get_actor_location()))
            log("enemy %s poise %s health %s; player has ASC %s" % (e.get_name(), value(comp(e, "BP_AttributesComponent_C"), POISE), value(comp(e, "BP_AttributesComponent_C"), HEALTH), asc is not None))
            s.update(phase="fight", t=0.0, next_attack=0.5)
        return
    if s["phase"] == "fight":
        e = s["enemy"]
        e_attr = comp(e, "BP_AttributesComponent_C")
        p_attr.call_method("Set Current Attribute Value", args=(HEALTH, 100.0))  # keep the player alive
        if s["t"] >= s["next_attack"]:
            s["next_attack"] = s["t"] + 1.5
            try:
                asc.call_method("Try Activate Abilities By Tag", args=(ATTACK,))
            except Exception as ex:
                log("attack call failed: " + str(ex)[:160])
        mesh = e.get_components_by_class(unreal.SkeletalMeshComponent)[0]
        anim = mesh.get_anim_instance()
        montage = anim.get_current_active_montage() if anim else None
        snap = (value(e_attr, POISE), value(e_attr, HEALTH), montage.get_name() if montage else "-")
        if snap != s["last"]:
            log("t=%.1f enemy poise=%s health=%s montage=%s" % (s["t"], *snap))
            s["last"] = snap
        if s["t"] > 30.0:
            finish("30 s")


handle = unreal.register_slate_post_tick_callback(tick)
log("registered")
