"""
PIE check of poise scaling by attack power (GA_BaseHitReaction gate): the pack player walks up to the pack boss and presses IA_NormalAttack (light) and then
IA_StrongAttack (heavy) as real input; every change of the boss's Attribute.Poise is logged with the move that caused it. Expected: light 20, heavy 50
(boss poise 100, regenerates 2 per 0.1 s after 4 s without a hit, so the check lets it refill between moves). Log prefix [PoisePie].
Open L_SevarogArena first; run with Scripts/run_in_editor.py. TARGET picks the victim: "boss" (pack great-sword boss, never staggers in the pack's design, so its
poise stays 100) or "sword" (a pack sword enemy, poise 30: light 30 -> 10, heavy breaks it and plays a hit reaction). The "sword" target is a temporary actor in
the editor level labelled PoiseTestEnemy; run with REMOVE_ONLY = True afterwards to delete it.
"""
import unreal

log = lambda m: unreal.log("[PoisePie] " + m)
ACTIONS = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/"
# (name, input action, seconds to wait before the move)
PLAN = [("light", "IA_NormalAttack"), ("heavy", "IA_StrongAttack"), ("light", "IA_NormalAttack"), ("heavy", "IA_StrongAttack")]
TARGET = "sword"
REMOVE_ONLY = False
SWORD = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleSwordEnemy/BP_ExampleSwordEnemy"
BOSS = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss"
state = {"phase": "start", "t": 0.0, "step": 0, "press_until": -1.0, "wait_until": 0.0, "last_poise": None, "label": "-"}
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


def tags(*names):
    c = unreal.GameplayTagContainer()
    c.import_text("(GameplayTags=(%s))" % ",".join('(TagName="%s")' % n for n in names))
    return c


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
    if s["t"] > 130.0:  # checked first: later branches return early
        finish("timeout")
        return
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="wait", t=0.0)
        return
    w = world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next(iter(unreal.GameplayStatics.get_all_actors_of_class(w, unreal.load_class(None, (SWORD if TARGET == "sword" else BOSS) + (".BP_ExampleSwordEnemy_C" if TARGET == "sword" else ".BP_ExampleGreatSwordBoss_C")))), None) if w else None
    if pawn is None or boss is None:
        if s["t"] > 25:
            finish("no pawn or boss")
        return
    d = boss.get_actor_location() - pawn.get_actor_location()
    flat = unreal.Vector(d.x, d.y, 0)
    # keep the test player alive and facing the boss
    s["heal_t"] = s.get("heal_t", 0.0) + dt
    if s["heal_t"] > 0.5:
        s["heal_t"] = 0.0
        t = unreal.GameplayTag()
        t.import_text('(TagName="Attribute.Health")')
        comp(pawn, "BP_AttributesComponent_C").call_method("Set Current Attribute Value", args=(t, 100.0))
    poise = attr(boss, "Attribute.Poise")
    if s["last_poise"] is not None and poise != s["last_poise"] and poise < s["last_poise"]:
        log("boss poise %.0f -> %.0f (drop %.0f) during %s step, boss hp %s, player montage %s" % (s["last_poise"], poise, s["last_poise"] - poise, s["label"], attr(boss, "Attribute.Health"), montage_of(pawn)))
    s["last_poise"] = poise
    pp = attr(pawn, "Attribute.Poise")
    if s.get("last_pp") is not None and pp != s["last_pp"] and pp < s["last_pp"]:
        log("PLAYER poise %.0f -> %.0f (drop %.0f) from boss montage %s" % (s["last_pp"], pp, s["last_pp"] - pp, montage_of(boss)))
    s["last_pp"] = pp
    hp = attr(boss, "Attribute.Health")
    if s.get("last_hp") is not None and hp != s["last_hp"]:
        log("boss hp %.0f -> %.0f during %s step (poise %.0f, boss montage %s)" % (s["last_hp"], hp, s["label"], poise, montage_of(boss)))
    s["last_hp"] = hp
    if s["phase"] == "wait":
        if s["t"] > 6.0:
            comp(pawn, "BP_AdvancedAbilitySystemComponent_C").call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))
            s.update(phase="fight", t=0.0, wait_until=2.0)
        return
    if flat.length() > 200.0:
        pawn.add_movement_input(flat.normal(), 1.0, False)
    elif s["t"] > s["wait_until"] and s["press_until"] < s["t"] and s["step"] < len(PLAN):
        yaw = unreal.MathLibrary.make_rot_from_x(flat).yaw
        pawn.set_actor_rotation(unreal.Rotator(0, 0, yaw), False)
        name, action = PLAN[s["step"]]
        if poise is not None and poise < s.setdefault("max_poise", poise) - 0.5:
            return  # let poise refill between moves
        s["label"] = name
        s["press_until"] = s["t"] + 0.2
        s["wait_until"] = s["t"] + 2.5
        s["step"] += 1
        log("press %s (target poise %.0f, distance %.0f, player montage %s, target montage %s)" % (name, poise, flat.length(), montage_of(pawn), montage_of(boss)))
    if s.get("press_until", -1) - 0.15 < s["t"] < s.get("press_until", -1) + 0.45 and int(s["t"] * 10) != s.get("pm_t", -1):
        s["pm_t"] = int(s["t"] * 10)
        log("   player montage %s, target hp %s poise %s montage %s" % (montage_of(pawn), attr(boss, "Attribute.Health"), poise, montage_of(boss)))
    if s["t"] < s["press_until"]:
        pc_action = unreal.load_asset(ACTIONS + PLAN[s["step"] - 1][1])
        unreal.RPGInputTestUtils.inject_action(pc, pc_action, unreal.Vector(1, 0, 0))
    if s["step"] >= len(PLAN) and s["t"] > s["wait_until"] + 25.0:  # keep fighting a while: the boss hits the player too
        finish("done")
    if s["t"] > 120.0:
        finish("timeout")


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish("error")


assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name() == "L_SevarogArena", "open L_SevarogArena first"
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in eas.get_all_level_actors():
    if a.get_actor_label() == "PoiseTestEnemy":
        eas.destroy_actor(a)
if REMOVE_ONLY:
    log("temporary enemy removed")
else:
    if TARGET == "sword":
        enemy = eas.spawn_actor_from_class(unreal.load_class(None, SWORD + ".BP_ExampleSwordEnemy_C"), unreal.Vector(-1500, 0, 100), unreal.Rotator(0, 0, 180))
        enemy.set_actor_label("PoiseTestEnemy")
        log("temporary sword enemy placed")
    handle = unreal.register_slate_post_tick_callback(tick)
