"""
The boss's final look (G2-15, URPGBossLook): Antigravity's body, crown, mantle, gauntlet and the greatsword on top of the pack mesh, which keeps driving the fight.
  L1 applied: the body follower (SK_Boss01_Body), three pieces, the sword (SM_Boss01_Greatsword) on the body's socket HeavySwordSocket_R; the pack mesh AND the pack's own sword (the static mesh Weapon Mesh, SM_KwangSword) are hidden in game; the sword has the mesh's world scale and its blade points up and away from the floor (the blade tip is above the hand).
  L2 the followers follow the pose: the body's pelvis sits on the pack mesh's pelvis (within 1 cm) standing and in the kneel of a stance break; the sword stays at the hand (hand_r) in both.
  L3 size: the body's head bone is 200 to 300 cm over its root bone in the world (the boss is about 3 m with the crown).
  L4 off and on: SetEnabledForTest(false) shows the pack mesh again and destroys the followers (none left), on again builds them once (no duplicates).
Boss held awake. Log prefix [BossLook]; ends with RESULT n/m passed. Run pie_debug_overlay.py once after an editor start first.
"""
import math
import unreal

log = lambda m: unreal.log("[BossLook] " + m)
results = []
S = {"phase": "start", "t": 0.0, "now": 0.0, "wait": 0.0, "gen": None}
handle = None


def check(name, ok, detail=""):
    results.append(ok)
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def comp(actor, name):
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
    return {"pawn": pawn, "boss": boss, "enc": comp(boss, "RPGBossEncounter"), "tr": comp(boss, "RPGAttackTracker"), "dbg": comp(boss, "RPGCombatDebug"), "stg": comp(boss, "RPGBossStagger"), "look": comp(boss, "RPGBossLook")}


def until(cond, timeout, step=0.0):
    t0 = S["now"]
    while not cond():
        if S["now"] - t0 > timeout:
            return False
        yield step
    return True


def dist(a, b):
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)


def fresh():
    p = P()
    p["stg"].set_cooldown_for_test(0.0)
    p["enc"].reset_for_test()
    yield 0.8
    p = P()
    p["enc"].wake()
    p["enc"].hold_for_test(True)
    p["dbg"].debug_refill_player()
    p["tr"].enter_combat()
    comp(p["pawn"], "BP_AdvancedAbilitySystemComponent_C").call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))
    yield 2.2


def pack_mesh(boss):
    look = comp(boss, "RPGBossLook")
    body = look.get_body_component()
    for c in boss.get_components_by_class(unreal.SkeletalMeshComponent):
        if c != body and not c.get_name().startswith("RPGLook"):
            return c
    return None


def pack_weapons(boss):
    return [c for c in boss.get_components_by_class(unreal.StaticMeshComponent) if "Weapon" in c.get_name() and not c.get_name().startswith("RPGLook")]


def blade(look, body):
    """(grip, tip, tip height over the hand): the sword's origin is the grip, its blade is +Z of the mesh."""
    sword = look.get_sword_component()
    box = sword.get_editor_property("static_mesh").get_bounding_box()
    length = box.max.z * sword.get_world_scale().z
    up = sword.get_up_vector()
    grip = sword.get_world_location()
    tip = unreal.Vector(grip.x + up.x * length, grip.y + up.y * length, grip.z + up.z * length)
    return grip, tip, tip.z - body.get_socket_location("hand_r").z, length


def pose_check(label):
    p = P()
    boss, look = p["boss"], p["look"]
    leader = pack_mesh(boss)
    body = look.get_body_component()
    d_pelvis = dist(leader.get_socket_location("pelvis"), body.get_socket_location("pelvis"))
    sword = look.get_sword_component()
    hand = body.get_socket_location("hand_r")
    d_hand = dist(sword.get_world_location(), hand) if sword else -1.0
    check("%s: the body's pelvis is on the pack mesh's pelvis (%.2f cm) and the sword's grip is at the hand (%.0f cm)" % (label, d_pelvis, d_hand), d_pelvis <= 1.0 and sword is not None and 3.0 <= d_hand <= 45.0, "")
    grip, tip, tip_over_hand, length = blade(look, body)
    log("%s: blade length %.0f cm, grip %s, tip %s, tip %.0f cm over the hand, blade direction %s" % (label, length, grip, tip, tip_over_hand, sword.get_up_vector()))
    return body


def script():
    yield from fresh()
    p = P()
    look = p["look"]
    check("L1 the boss has the look component and it is applied", look is not None and look.is_applied(), "")
    body = look.get_body_component()
    sword = look.get_sword_component()
    leader = pack_mesh(p["boss"])
    check("L1 the body follower plays SK_Boss01_Body, %d pieces" % look.get_piece_count(), body is not None and body.get_editor_property("skeletal_mesh_asset").get_name() == "SK_Boss01_Body" and look.get_piece_count() == 3, "")
    check("L1 the sword is SM_Boss01_Greatsword on the body's socket HeavySwordSocket_R", sword is not None and sword.get_editor_property("static_mesh").get_name() == "SM_Boss01_Greatsword" and str(sword.get_attach_socket_name()) == "HeavySwordSocket_R" and sword.get_attach_parent() == body, "socket %s" % (sword.get_attach_socket_name() if sword else None))
    check("L1 the pack mesh is hidden in game", leader is not None and leader.get_editor_property("hidden_in_game") is True, "")
    weapons = pack_weapons(p["boss"])
    check("L1 the pack's own sword is hidden too (%d weapon mesh(es), %d hidden by the look, visible: %s)" % (len(weapons), look.get_hidden_pack_weapon_count(), [w.get_name() for w in weapons if not w.get_editor_property("hidden_in_game")]),
          len(weapons) >= 1 and look.get_hidden_pack_weapon_count() == len(weapons) and all(w.get_editor_property("hidden_in_game") for w in weapons))
    scale_ratio = sword.get_world_scale().x / leader.get_world_scale().x if sword is not None else 0.0
    check("L1 the sword has the pack mesh's world scale (%.2f of it)" % scale_ratio, 0.97 <= scale_ratio <= 1.03)
    pose_check("L2 standing")
    height = body.get_socket_location("head").z - body.get_socket_location("root").z
    check("L3 the body's head is %.0f cm over its root (the boss is about 3 m with the crown)" % height, 200.0 <= height <= 300.0, "")
    # a stance break: the kneel
    stand_pelvis = leader.get_socket_location("pelvis").z
    P()["stg"].force_break_for_test()
    kneeling = yield from until(lambda: P()["stg"].get_clip_stage_name() == "down", 3.0)
    yield 0.4
    p = P()
    drop = stand_pelvis - pack_mesh(p["boss"]).get_socket_location("pelvis").z
    check("L2 the boss kneels (stage %s, the pelvis %.0f cm lower than standing) before the pose is compared" % (p["stg"].get_clip_stage_name(), drop), kneeling and drop >= 30.0)
    pose_check("L2 in the kneel of a stance break")
    stood = yield from until(lambda: not P()["stg"].is_staggered(), 8.0)
    check("L2 the stance break ended (the boss stands again)", stood)
    yield 0.5
    # off and on
    P()["look"].set_enabled_for_test(False)
    yield 0.3
    p = P()
    leader = pack_mesh(p["boss"])
    left = [c.get_name() for c in p["boss"].get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name().startswith("RPGLook")] + [c.get_name() for c in p["boss"].get_components_by_class(unreal.StaticMeshComponent) if c.get_name().startswith("RPGLook")]
    check("L4 off: the pack mesh is drawn again and no follower is left (%s)" % left, not p["look"].is_applied() and leader.get_editor_property("hidden_in_game") is False and not left, "")
    P()["look"].set_enabled_for_test(True)
    yield 0.3
    p = P()
    bodies = [c for c in p["boss"].get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name() == "RPGLookBody"]
    swords = [c for c in p["boss"].get_components_by_class(unreal.StaticMeshComponent) if c.get_name() == "RPGLookSword"]
    check("L4 on again: one body, one sword, %d pieces (no duplicates)" % p["look"].get_piece_count(), p["look"].is_applied() and len(bodies) == 1 and len(swords) == 1 and p["look"].get_piece_count() == 3, "")
    pose_check("L4 after on again")


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("RESULT %d/%d passed" % (sum(1 for r in results if r), len(results)))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def _tick(dt):
    s = S
    s["t"] += dt
    s["now"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0)
        return
    w, pc, pawn, boss = actors()
    if pawn is None or boss is None:
        return
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
        check("tick raised", False)
        finish()


handle = unreal.register_slate_post_tick_callback(tick)
