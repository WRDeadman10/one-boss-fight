"""Lead PIE driver (owner 2026-11-07): one full fight against the Ember Warden for a review video.

The bot walks to the boss and cycles through every Elden Ring move so the owner can judge the new clips
in play: R1 light, R2 strong, standing dodge (backstep), jump+R1 (air light), jump+R2 (air heavy),
L1 block (pack IA_Block) and an R2 guard counter when the counter window arms.

Honesty notes logged at start and in the summary:
- the player is refilled by the boss's RPGCombatDebug when below 35 HP, so the fight reaches the end;
- the boss keeps its real health and AI (no hold, no damage scaling).
Ends when the boss dies (actor destroyed or health <= 0) or after MAX_FIGHT_SECONDS.
Log prefix [FullFight]; stop marker "[FullFight] finished:".
"""
import math
import os
import unreal

FRAMES = os.environ.get("FIGHT_FRAMES", "D:/FightVideo/fight")
FRAME_FPS = 15.0

LOG = "[FullFight] "
MAX_FIGHT_SECONDS = float(os.environ.get("FIGHT_MAX", "480"))
BLOCK_ACTION = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_Block"
R1, R2, JUMP, DODGE = "Gamepad_RightShoulder", "Gamepad_RightTrigger", "Gamepad_FaceButton_Bottom", "Gamepad_FaceButton_Right"
# Each action: list of (time_s, key, down) plus the time the action lasts. "guard" is handled separately.
ACTIONS = {
    "light": ([(0.00, R1, True), (0.08, R1, False)], 1.0),
    "strong": ([(0.00, R2, True), (0.12, R2, False)], 1.5),
    "backstep": ([(0.00, DODGE, True), (0.10, DODGE, False)], 1.0),
    "air_light": ([(0.00, JUMP, True), (0.10, JUMP, False), (0.30, R1, True), (0.38, R1, False)], 1.6),
    "air_heavy": ([(0.00, JUMP, True), (0.10, JUMP, False), (0.30, R2, True), (0.42, R2, False)], 1.9),
}
CYCLE = ["light", "light", "strong", "backstep", "air_light", "guard", "light", "air_heavy", "backstep", "guard", "strong"]
S = {"phase": "start", "elapsed": 0.0, "fight_time": 0.0, "held": set(), "cycle": 0, "action": None,
     "action_t": 0.0, "event": 0, "beat": 0.0, "counts": {}, "refills": 0, "done": False, "boss_dead": False,
     "g_last": None, "frame": 0, "pending": None, "g_shot": -1.0}
HANDLE = None


def log(m):
    unreal.log(LOG + str(m))


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None) if actor else None


def attr(actor, tag_name, maximum=False):
    c = comp(actor, "BP_AttributesComponent_C")
    if not c:
        return None
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % tag_name)
    try:
        return float(c.call_method("GetMaxAttributeValue" if maximum else "Get Current Attribute Value", args=(t,)))
    except Exception:
        return None


def montage(actor):
    for mesh in actor.get_components_by_class(unreal.SkeletalMeshComponent) if actor else []:
        inst = mesh.get_anim_instance()
        m = inst.get_current_active_montage() if inst else None
        if m:
            return m.get_name()
    return "None"


def actors():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)
                 if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if world else None
    return world, pc, pawn, boss


def key(pc, k, down):
    unreal.RPGInputTestUtils.set_key_down(pc, k, down)
    (S["held"].add if down else S["held"].discard)(k)


def release_all(pc):
    for k in list(S["held"]):
        try:
            unreal.RPGInputTestUtils.set_key_down(pc, k, False)
        except Exception:
            pass
    S["held"].clear()


def face(pc, pawn, boss):
    a, b = pawn.get_actor_location(), boss.get_actor_location()
    yaw = math.degrees(math.atan2(b.y - a.y, b.x - a.x))
    pc.set_control_rotation(unreal.Rotator(0.0, 0.0, yaw))
    return math.hypot(b.x - a.x, b.y - a.y)


def capture(world):
    """One 960x540 in-engine frame per 1/15 s of game time; the next request waits for the previous PNG."""
    g = unreal.GameplayStatics.get_time_seconds(world)
    if S["pending"] is not None and not os.path.exists(S["pending"]):
        return
    if g - S["g_shot"] < 1.0 / FRAME_FPS:
        return
    S["g_shot"] = g
    S["pending"] = "%s/f_%05d.png" % (FRAMES, S["frame"])
    unreal.SystemLibrary.execute_console_command(world, "HighResShot 960x540 filename=%s" % S["pending"])
    log("FRAME %d g=%.3f action=%s" % (S["frame"], g, S["action"]))
    S["frame"] += 1


def finish(reason):
    global HANDLE
    if S["done"]:
        return
    S["done"] = True
    try:
        _, pc, _, _ = actors()
        if pc:
            release_all(pc)
    except Exception:
        pass
    if HANDLE is not None:
        unreal.unregister_slate_post_tick_callback(HANDLE)
        HANDLE = None
    log("SUMMARY fight_seconds=%.1f boss_dead=%s actions=%s player_refills=%d frames=%d" % (S["fight_time"], S["boss_dead"], S["counts"], S["refills"], S["frame"]))
    log("finished: " + reason)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("driver error: " + traceback.format_exc())
        finish("exception")


def _tick(dt):
    S["elapsed"] += dt
    if S["phase"] == "start":
        if S["elapsed"] > 0.5:
            sel = os.environ.get("H019_ENCOUNTER_DEFINITION", "").strip()
            if sel:
                unreal.SystemLibrary.execute_console_command(None, "rpg.EncounterDefinition " + sel)
            log("route=%s; player refilled below 35 HP by the boss RPGCombatDebug; boss health and AI untouched" % ("data " + sel if sel else "legacy"))
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            S.update(phase="wait", elapsed=0.0)
        return
    world, pc, pawn, boss = actors()
    if S["phase"] == "wait":
        if pawn and boss and S["elapsed"] > 6.0:
            asc = comp(pawn, "BP_AdvancedAbilitySystemComponent_C")
            t = unreal.GameplayTagContainer()
            t.import_text('(GameplayTags=((TagName="Ability.EnterCombat")))')
            asc.call_method("Try Activate Abilities By Tag", args=(t,))
            bl = boss.get_actor_location()
            pawn.set_actor_location_and_rotation(unreal.Vector(bl.x + 700, bl.y, bl.z), unreal.Rotator(0, 0, 180), False, True)
            log("setup boss_hp=%s/%s player_hp=%s/%s" % (attr(boss, "Attribute.Health"), attr(boss, "Attribute.Health", True), attr(pawn, "Attribute.Health"), attr(pawn, "Attribute.Health", True)))
            S.update(phase="draw", elapsed=0.0)
        elif S["elapsed"] > 30.0:
            finish("no player/boss within 30 s")
        return
    if S["phase"] == "draw":
        if 0.3 <= S["elapsed"] and R2 not in S["held"] and S["elapsed"] < 0.4:
            key(pc, R2, True)
        if S["elapsed"] >= 1.0 and R2 in S["held"]:
            key(pc, R2, False)
        if S["elapsed"] >= 3.5:
            unreal.SystemLibrary.execute_console_command(world, "slomo 0.5")
            log("FIGHT_START slomo=0.5 frames=%s fps=%.0f" % (FRAMES, FRAME_FPS))
            S.update(phase="fight", elapsed=0.0)
        return
    # fight: all timing below uses GAME time (capture stalls real time)
    g = unreal.GameplayStatics.get_time_seconds(world)
    gdt = 0.0 if S["g_last"] is None else max(0.0, g - S["g_last"])
    S["g_last"] = g
    dt = gdt
    S["fight_time"] += dt
    capture(world)
    if boss is None or (attr(boss, "Attribute.Health") is not None and attr(boss, "Attribute.Health") <= 0.0):
        if not S["boss_dead"]:
            S["boss_dead"] = True
            S["dead_at"] = S["fight_time"]
            log("BOSS_DEAD at %.1f s" % S["fight_time"])
        if S["fight_time"] - S["dead_at"] > 5.0:
            finish("boss dead")
        return
    if S["fight_time"] > MAX_FIGHT_SECONDS:
        finish("time limit")
        return
    if pawn is None:
        return
    hp, hpmax = attr(pawn, "Attribute.Health"), attr(pawn, "Attribute.Health", True)
    # The pack reports a 1e6 max for the player; the playable bar is 100-120, so refill below 35 HP.
    if hp is not None and hp < 35.0:
        dbg = comp(boss, "RPGCombatDebug")
        if dbg:
            dbg.debug_refill_player()
            S["refills"] += 1
    S["beat"] += dt
    if S["beat"] >= 2.0:
        S["beat"] = 0.0
        log("BEAT t=%.1f boss_hp=%s player_hp=%s boss_montage=%s player_montage=%s action=%s" % (
            S["fight_time"], attr(boss, "Attribute.Health"), hp, montage(boss), montage(pawn), S["action"]))
    dist = face(pc, pawn, boss)
    if S["action"] is None:
        if dist > 260.0:
            pawn.add_movement_input(pawn.get_actor_forward_vector(), 1.0, True)
            return
        name = CYCLE[S["cycle"] % len(CYCLE)]
        S["cycle"] += 1
        S.update(action=name, action_t=0.0, event=0, guard_armed_at=None)
        S["counts"][name] = S["counts"].get(name, 0) + 1
        log("ACTION %s t=%.2f dist=%.0f" % (name, S["fight_time"], dist))
        return
    S["action_t"] += dt
    name = S["action"]
    if name == "guard":
        action = unreal.load_asset(BLOCK_ACTION)
        dodge = comp(pawn, "RPGDodgeTiming")
        if S.get("guard_armed_at") is None:
            unreal.RPGInputTestUtils.inject_action(pc, action, unreal.Vector(1.0, 0.0, 0.0))
            if dodge and dodge.is_guard_counter_armed():
                S["guard_armed_at"] = S["action_t"]
                key(pc, R2, True)
                S["counts"]["counter"] = S["counts"].get("counter", 0) + 1
                log("COUNTER t=%.2f" % S["fight_time"])
            elif S["action_t"] > 2.5:
                S["action"] = None
        else:
            if R2 in S["held"] and S["action_t"] - S["guard_armed_at"] >= 0.12:
                key(pc, R2, False)
            if S["action_t"] - S["guard_armed_at"] >= 1.6:
                S["action"] = None
        return
    events, length = ACTIONS[name]
    while S["event"] < len(events) and S["action_t"] >= events[S["event"]][0]:
        _, k, down = events[S["event"]]
        key(pc, k, down)
        S["event"] += 1
    if S["action_t"] >= length:
        release_all(pc)
        S["action"] = None


HANDLE = unreal.register_slate_post_tick_callback(tick)
log("driver registered")
