"""
Probe (M13, log prefix [HitProbe], no checks): why do the claymore's and the dual swords' light and strong swings land no hit in pie_builds.py (the swing tracker sees them, the hit intake sees none, only the claymore's charged attack hit)?
For each configuration (build, weapon slot lock on/off) the build is chosen while the boss sleeps, the fight starts (boss awake and held), and three swings of each kind are made from three distances in front of the boss; every swing logs
"PROBE build lock kind dist -> hits (boss health drop)". Compare: the sword explicitly chosen (control), the claymore without the lock, with the lock, the dual swords without the lock.
Needs the warm-up of RunDrivers.ps1 first. Ends with PROBE done.
"""
import math
import unreal

log = lambda m: unreal.log("[HitProbe] " + m)
IA = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/"
S = {"phase": "start", "t": 0.0, "now": 0.0, "wait": 0.0, "gen": None, "press_until": 0.0, "action": "IA_NormalAttack"}
handle = None
STYLE = {"Starter": "SwordCombatStyle", "Strength": "ClaymoreCombatStyle", "Dex": "DualSwordCombatStyle"}
CONFIGS = [("Starter", True), ("Strength", False), ("Strength", True), ("Dex", False), ("Dex", True)]
DISTANCES = [80.0, 110.0, 150.0]
KINDS = [("Light", "IA_NormalAttack", 0.12), ("Strong", "IA_StrongAttack", 0.12)]  # one swing each at 110 cm


def comp(actor, name):
    if actor is None:
        return None
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def tags(*names):
    c = unreal.GameplayTagContainer()
    c.import_text("(GameplayTags=(%s))" % ",".join('(TagName="%s")' % n for n in names))
    return c


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()


def actors():
    w = world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    return w, pc, pawn, boss


def P():
    w, pc, pawn, boss = actors()
    return {"w": w, "pc": pc, "pawn": pawn, "boss": boss, "enc": comp(boss, "RPGBossEncounter"), "tr": comp(boss, "RPGAttackTracker"), "dbg": comp(boss, "RPGCombatDebug"),
            "swing": comp(pawn, "RPGSwingTracker"), "intake": comp(pawn, "RPGHitIntake"), "ld": comp(pawn, "RPGBuildLoadout")}


def place(p, dist):
    boss, pawn = p["boss"], p["pawn"]
    bl = boss.get_actor_location()
    r = math.radians(boss.get_actor_rotation().yaw)
    q = unreal.Vector(bl.x + math.cos(r) * dist, bl.y + math.sin(r) * dist, bl.z + 20)
    look = unreal.MathLibrary.find_look_at_rotation(q, bl).yaw
    pawn.set_actor_location_and_rotation(q, unreal.Rotator(0, 0, look), False, True)
    p["pc"].set_control_rotation(unreal.Rotator(0, 0, look))
    p["dbg"].debug_set_boss_health_fraction(1.0)


def until(cond, timeout, step=0.0):
    t0 = S["now"]
    while not cond():
        if S["now"] - t0 > timeout:
            return False
        yield step
    return True


def press(action, seconds):
    S["action"] = action
    S["press_until"] = S["now"] + seconds


def player_idle():
    pawn = P()["pawn"]
    if pawn is None:
        return True
    inst = pawn.get_components_by_class(unreal.SkeletalMeshComponent)[0].get_anim_instance()
    return inst is None or inst.get_current_active_montage() is None


def style_of():
    return P()["ld"].get_actual_style_name()


def compact(text):
    import re
    text = re.sub(r"(Amount|Index|IsEquipped\?|Item|Guid)_\d+_[0-9A-F]+", r"", text)
    text = text.replace("/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/DataAssets/Items/", "").replace("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Items/Weapons/", "")
    return text[:900]


def script():
    # CONTROL on a fresh pawn: no build chosen, the pack's own slot; does an injected quickslot press cycle the weapon?
    ld = P()["ld"]
    log("DEFAULT SLOT: %s" % compact(ld.get_weapon_slot_report()))
    log("DEFAULT style %s, equipped %s" % (style_of(), ld.get_equipped_actor_class_name()))
    for action in ("IA_QuickSlotRight", "IA_QuickSlotRight", "IA_QuickSlotLeft", "IA_QuickSlotUp", "IA_QuickSlotDown"):
        before = style_of()
        press(action, 0.15)
        yield 2.5
        log("CONTROL %s: style %s -> %s, equipped %s" % (action, before, style_of(), P()["ld"].get_equipped_actor_class_name()))
    log("AFTER SLOT: %s" % compact(P()["ld"].get_weapon_slot_report()))


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    try:
        unreal.SystemLibrary.execute_console_command(world(), 'rpg.Build ""')
    except Exception:
        pass
    log("PROBE done")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def _tick(dt):
    s = S
    s["t"] += dt
    s["now"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.SystemLibrary.execute_console_command(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(), 'rpg.Build ""')
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0)
        return
    w, pc, pawn, boss = actors()
    if boss is None or pawn is None:
        return
    if s["now"] < s["press_until"]:
        unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset(IA + s["action"]), unreal.Vector(1, 0, 0))
    if s["wait"] > 0:
        s["wait"] -= dt
        return
    if s["gen"] is None:
        if s["t"] < 9.0:
            return
        s["gen"] = script()
    try:
        s["wait"] = float(next(s["gen"]))
    except StopIteration:
        finish()


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish()


handle = unreal.register_slate_post_tick_callback(tick)
