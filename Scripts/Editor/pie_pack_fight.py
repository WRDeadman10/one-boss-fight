"""
PIE check of the pack's own player (BP_CombatPlayerCharacter, mannequin) against the pack's great-sword boss (BP_ExampleGreatSwordBoss) in L_SevarogArena.
Logs once a second: pawn classes, distance, boss position, boss and player montage, boss and player health, boss blackboard. The player walks towards the
boss until WALK_UNTIL cm, then enters combat and swings (test driver). Open L_SevarogArena first, run via Scripts/run_in_editor.py. Log prefix [PackPie].
Ends play by itself after DURATION seconds.
"""
import unreal

log = lambda m: unreal.log("[PackPie] " + m)
DURATION = 45.0
WALK_UNTIL = 230.0  # cm: close enough for the pack's melee to reach
FIGHT = True
HEAL = True
state = {"phase": "start", "t": 0.0, "log_t": 99.0}
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
    if c is None:
        return None
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % tag)
    try:
        return c.call_method("Get Current Attribute Value", args=(t,))
    except Exception as e:
        return "ERR " + str(e)[:60]


def tags(*names):
    c = unreal.GameplayTagContainer()
    c.import_text("(GameplayTags=(%s))" % ",".join('(TagName="%s")' % n for n in names))
    return c


def montage_of(actor):
    mc = actor.get_components_by_class(unreal.SkeletalMeshComponent)
    inst = mc[0].get_anim_instance() if mc else None
    m = inst.get_current_active_montage() if inst else None
    return "%s@%.2f" % (m.get_name(), inst.montage_get_position(m)) if m else None


def bb_info(boss):
    try:
        ctrl = boss.get_controller()
        if ctrl is None:
            return "no controller"
        bbs = ctrl.get_components_by_class(unreal.BlackboardComponent)
        bb = bbs[0] if bbs else None
        if bb is None:
            return "no blackboard"
        return "ctrl=%s tgt=%s combat=%s dist=%s beh=%s" % (ctrl.get_class().get_name(), bb.get_value_as_object("TargetActor"), bb.get_value_as_bool("bCombatEnabled"),
                                                              bb.get_value_as_float("DistanceToTarget"), bb.get_value_as_name("CurrentBehaviorTag"))
    except Exception as e:
        return "bb err " + str(e)[:80]


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
    boss = next(iter(unreal.GameplayStatics.get_all_actors_of_class(w, unreal.load_class(None, "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss.BP_ExampleGreatSwordBoss_C"))), None)
    if pawn is None or boss is None:
        if s["t"] > 20.0:
            finish("no pawn or boss (pawn=%s boss=%s)" % (pawn, boss))
        return
    if s["phase"] == "wait":
        if s["t"] > 6.0:  # first PIE after an editor start renders black while shaders compile; the logic runs anyway
            mesh = pawn.get_components_by_class(unreal.SkeletalMeshComponent)[0]
            log("player=%s mesh=%s | boss=%s mesh=%s" % (pawn.get_class().get_name(), mesh.get_editor_property("skeletal_mesh_asset").get_name(), boss.get_class().get_name(),
                boss.get_components_by_class(unreal.SkeletalMeshComponent)[0].get_editor_property("skeletal_mesh_asset").get_name()))
            s.update(phase="watch", t=0.0, boss_start=boss.get_actor_location())
        return
    s["log_t"] += dt
    d = boss.get_actor_location() - pawn.get_actor_location()
    flat = unreal.Vector(d.x, d.y, 0)
    if s["log_t"] >= 1.0:
        s["log_t"] = 0.0
        log("t=%4.1f dist=%5.0f boss_at=(%.0f,%.0f) boss_montage=%s boss_hp=%s boss_poise=%s | player_montage=%s hp=%s | %s" % (
            s["t"], d.length(), boss.get_actor_location().x, boss.get_actor_location().y, montage_of(boss), attr(boss, "Attribute.Health"), attr(boss, "Attribute.Poise"),
            montage_of(pawn), attr(pawn, "Attribute.Health"), bb_info(boss)))
    s["heal_t"] = s.get("heal_t", 0.0) + dt
    if HEAL and s["heal_t"] > 1.0:  # keep the test player alive (not a bot worth shipping)
        s["heal_t"] = 0.0
        attrs = comp(pawn, "BP_AttributesComponent_C")
        t = unreal.GameplayTag()
        t.import_text('(TagName="Attribute.Health")')
        if attrs:
            attrs.call_method("Set Current Attribute Value", args=(t, 100.0))
    if flat.length() > WALK_UNTIL:
        pawn.add_movement_input(flat.normal(), 1.0, False)
    elif FIGHT:
        asc = comp(pawn, "BP_AdvancedAbilitySystemComponent_C")
        yaw = unreal.MathLibrary.make_rot_from_x(flat).yaw
        pawn.set_actor_rotation(unreal.Rotator(0, 0, yaw), False)
        s["swing_t"] = s.get("swing_t", 0.0) + dt
        if asc and not s.get("combat"):
            asc.call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))
            s["combat"] = True
        elif asc and s["swing_t"] > 1.6:
            s["swing_t"] = 0.0
            asc.call_method("Try Activate Abilities By Tag", args=(tags("Ability.Melee"),))
    if s["t"] > DURATION:
        moved = (boss.get_actor_location() - s["boss_start"]).length()
        finish("done, boss moved %.0f cm from its start" % moved)


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish("error")


assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name() == "L_SevarogArena", "open L_SevarogArena first"
handle = unreal.register_slate_post_tick_callback(tick)
