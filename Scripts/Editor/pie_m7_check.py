"""
PIE visual check for the M7 assets: roll montage, block/parry sparks, shockwave and lightning effects.

Writes Saved/m7_flag.txt with a tag while something worth photographing is on screen (slow motion, so a capture loop
outside the editor can grab frames: Scripts/CaptureLoop.ps1); the file is removed otherwise. Prefix [M7Drive].
Needs -unattended and the editor in the foreground.
"""
import os

import unreal

LOG = "[M7Drive] "
FLAG = os.path.join(unreal.Paths.project_saved_dir(), "m7_flag.txt")
TRIGGER_POINT = unreal.Vector(-1100.0, 0.0, 120.0)
state = {"phase": "start", "t": 0.0, "total": 0.0, "seen": set()}
handle = None


def log(msg):
    unreal.log(LOG + msg)
    with open(os.path.join(unreal.Paths.project_saved_dir(), "m7_trace.txt"), "a") as f:
        f.write(msg + chr(10))


def set_flag(tag):
    if tag is None:
        if os.path.exists(FLAG):
            os.remove(FLAG)
        return
    with open(FLAG, "w") as f:
        f.write(tag)


def world():
    try:
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    except Exception:
        return None


def finish(reason):
    log("finish called: " + reason)
    global handle
    set_flag(None)
    if handle is not None:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    try:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    except Exception:
        pass
    log("finished: " + reason)
    quit_state = {"n": 0, "h": None}

    def quit_tick(_dt):
        quit_state["n"] += 1
        if quit_state["n"] > 120:
            unreal.unregister_slate_post_tick_callback(quit_state["h"])
            unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")

    quit_state["h"] = unreal.register_slate_post_tick_callback(quit_tick)


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error: " + traceback.format_exc())
        finish("error")


def attack_name(brain, index):
    attacks = brain.get_editor_property("attacks")
    if 0 <= index < len(attacks):
        return str(attacks[index].get_editor_property("attack_name"))
    return ""


def _tick(dt):
    s = state
    s["t"] += dt
    s["total"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="wait", t=0.0)
        return
    w = world()
    if w is None:
        if s["phase"] != "wait":
            finish("PIE ended")
        return
    pc = unreal.GameplayStatics.get_player_controller(w, 0)
    pawn = pc.get_controlled_pawn() if pc else None
    bosses = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.RPGBossCharacter)
    if pawn is None or not bosses:
        return
    boss = bosses[0]
    brain = boss.get_components_by_class(unreal.RPGBossCombatComponent)[0]
    boss_attr = boss.get_components_by_class(unreal.RPGAttributeComponent)[0]
    p_attr = pawn.get_components_by_class(unreal.RPGAttributeComponent)[0]
    combat = pawn.get_components_by_class(unreal.RPGCombatComponent)[0]
    p_attr.heal(1000.0)  # keep the player alive: this is a visual check

    if s["phase"] == "wait":
        if s["t"] > 3.0:
            pawn.set_actor_location(TRIGGER_POINT, False, True)
            s.update(phase="engage", t=0.0)
        return
    if s["phase"] == "engage":
        if brain.get_boss_state() == unreal.RPGBossState.COMBAT and s["t"] > 1.0:
            pawn.set_actor_location_and_rotation(unreal.Vector(-700.0, 0.0, 120.0), unreal.Rotator(0.0, 0.0, 0.0), False, True)
            s.update(phase="roll_start", t=0.0)
        return
    if s["phase"] == "roll_start":
        if s["t"] > 0.3:
            log("dodge sideways: %s" % combat.request_dodge(unreal.Vector(0.0, 1.0, 0.0)))
            s.update(phase="roll_slow", t=0.0)
        return
    if s["phase"] == "roll_slow":
        if s["t"] > 0.06:
            unreal.GameplayStatics.set_global_time_dilation(w, 0.15)
            set_flag("roll_side")
            s.update(phase="roll_hold", t=0.0)
        return
    if s["phase"] in ("roll_hold", "back_hold"):
        mesh = pawn.get_components_by_class(unreal.SkeletalMeshComponent)[0]
        a = pawn.get_actor_location(); b = mesh.get_socket_location("pelvis")
        log("%s t=%.1f capsule=(%.0f,%.0f,%.0f) pelvis offset from capsule=(%.0f,%.0f,%.0f) state=%s" % (
            s["phase"], s["t"], a.x, a.y, a.z, b.x - a.x, b.y - a.y, b.z - a.z, combat.get_state()))
    if s["phase"] == "roll_hold":
        # Slate ticks are not time-dilated: t is real seconds, the roll (0.6 s of game time) takes 4 s at 0.15.
        if s["t"] > 4.5:
            unreal.GameplayStatics.set_global_time_dilation(w, 1.0)
            set_flag(None)
            s.update(phase="back", t=0.0)
        return
    if s["phase"] == "back":
        if s["t"] > 1.0 and combat.get_state() == unreal.RPGCombatState.LOCOMOTION:
            p_attr.reset_attributes()  # stamina back to full
            log("dodge back: %s" % combat.request_dodge(unreal.Vector(0.0, 0.0, 0.0)))
            s.update(phase="back_slow", t=0.0)
        return
    if s["phase"] == "back_slow":
        if s["t"] > 0.06:
            unreal.GameplayStatics.set_global_time_dilation(w, 0.15)
            set_flag("roll_back")
            s.update(phase="back_hold", t=0.0)
        return
    if s["phase"] == "back_hold":
        if s["t"] > 4.5:
            unreal.GameplayStatics.set_global_time_dilation(w, 1.0)
            set_flag(None)
            boss_attr.apply_damage(boss_attr.get_health() * 0.55)  # into phase 2 so the lightning is unlocked
            s.update(phase="fight", t=0.0)
        return
    if s["phase"] == "fight":
        # Stand in front of the boss and hold the guard so blocks and parries throw sparks.
        facing = (boss.get_actor_location() - pawn.get_actor_location())
        facing.z = 0.0
        if facing.length() > 450.0:
            pawn.set_actor_location_and_rotation(
                boss.get_actor_location() - facing.normal() * 330.0 + unreal.Vector(0.0, 0.0, 0.0), facing.rotator(), False, True)
        if combat.get_state() == unreal.RPGCombatState.LOCOMOTION:
            combat.start_block()
        index = brain.get_current_attack_index()
        name = attack_name(brain, index) if index >= 0 else ""
        want = name in ("Shockwave", "Lightning Strike") or "Combo" in name
        slow = want and s.get("slow_for", 0.0) < 3.0
        if want:
            s["slow_for"] = s.get("slow_for", 0.0) + dt / 0.12
        else:
            s["slow_for"] = 0.0
        unreal.GameplayStatics.set_global_time_dilation(w, 0.12 if slow else 1.0)
        set_flag(name.split(" ")[0] if slow else None)
        if name and name not in s["seen"]:
            s["seen"].add(name)
            log("attack seen: %s" % name)
        if s["t"] > 120.0 or {"Shockwave", "Lightning Strike"} <= s["seen"] and s["t"] > 90.0:
            unreal.GameplayStatics.set_global_time_dilation(w, 1.0)
            finish("done; saw %s" % sorted(s["seen"]))


handle = unreal.register_slate_post_tick_callback(tick)
log("driver registered")
