"""P0 read-only geometry probe for CAP-02 (A4 low sweep: production query versus visible blade). Starts PIE, wakes and freezes the boss (existing test hooks used by pie_a4_low_sweep.py),
keeps the player far away (1500 cm) so nothing is hit, starts A4 through URPGBossLowSweep.StartForTest (FORCED start: a mechanism probe, not natural selection), and for every tick of the move logs:
montage-local time, the sweep's blade angle and active flag, the boss root, and the visible sword's world positions: the mesh origin, the local point (0,0,TIP_Z) (the greatsword's blade axis is +Z with its tip at +163.3 cm in
mesh space, Antigravity extraction) and the mesh sockets if they exist, each with its horizontal distance from the boss root and its height above the floor. It also logs the query numbers read from the component (Reach, InnerRadius,
BladeHeight, sweep angles) and the boss actor scale. Nothing is modified except the temporary PIE actors' state through the same hooks the existing drivers use. Log prefix [P0A4]. Ends by itself."""
import math
import unreal

log = lambda m: unreal.log("[P0A4] " + m)
TIP_Z = 163.3
SOCKETS = ("SOCKET_Weapon_Start", "SOCKET_Weapon_End", "SOCKET_BladeEnd", "BladeEnd", "BladeStart", "SOCKET_TrailEndSocket")
S = {"phase": "start", "t": 0.0, "t0": None, "ticks": 0, "done": False}
handle = None


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def find_boss(world):
    for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character):
        if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C":
            return a
    return None


def horiz(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def describe(label, v, root, floor):
    return "%s=(%.0f,%.0f,%.0f) d_h=%.0f h=%.0f" % (label, v.x, v.y, v.z, horiz(v, root), v.z - floor)


def local_tip(sw):
    """Tip of the visible sword in mesh space without assuming an axis: the end of the longest local-bounds axis that lies away from the mesh origin (the grip). Returns (Vector, axis_name, half_length)."""
    b = sw.get_editor_property("static_mesh").get_bounds()
    o, e = b.origin, b.box_extent
    ext = {"x": e.x, "y": e.y, "z": e.z}
    org = {"x": o.x, "y": o.y, "z": o.z}
    axis = max(ext, key=ext.get)
    sign = 1.0 if org[axis] >= 0 else -1.0
    v = {"x": o.x, "y": o.y, "z": o.z}
    v[axis] = org[axis] + sign * ext[axis]
    return unreal.Vector(v["x"], v["y"], v["z"]), "%s%s" % ("+" if sign > 0 else "-", axis), ext[axis]


def sword_of(boss):
    for c in boss.get_components_by_class(unreal.StaticMeshComponent):
        try:
            m = c.get_editor_property("static_mesh")
            if m and m.get_name() == "SM_Boss01_Greatsword":
                return c
        except Exception:
            pass
    return None


def _tick(dt):
    global handle
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    S["t"] += dt
    if S["phase"] == "start" and S["t"] > 0.5:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
        S.update(phase="play", t=0.0)
        return
    if world is None:
        return
    boss = find_boss(world)
    pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
    if boss is None or pawn is None:
        return
    enc = comp(boss, "RPGBossEncounter")
    sweep = comp(boss, "RPGBossLowSweep")
    tracker = comp(boss, "RPGAttackTracker")
    if S["phase"] == "play" and S["t"] > 6.0:
        enc.wake()
        enc.hold_for_test(True)
        loc = boss.get_actor_location()
        pawn.set_actor_location(unreal.Vector(loc.x + 1500, loc.y, loc.z), False, True)
        log("setup: boss scale %s, Reach %.0f, InnerRadius %.0f, BladeHeight %.0f, sweep %.0f -> %.0f deg, boss at (%.0f,%.0f,%.0f) yaw %.1f" % (
            boss.get_actor_scale3d(), sweep.get_editor_property("Reach"), sweep.get_editor_property("InnerRadius"), sweep.get_editor_property("BladeHeight"),
            sweep.get_editor_property("SweepFromDegrees"), sweep.get_editor_property("SweepToDegrees"), loc.x, loc.y, loc.z, boss.get_actor_rotation().yaw))
        sw = sword_of(boss)
        log("visible sword component: %s" % (sw.get_name() if sw else None))
        if sw:
            for sname in SOCKETS:
                try:
                    has = sw.does_socket_exist(sname)
                except Exception as e:
                    has = "ERR %s" % str(e)[:40]
                log("socket %s exists on the mesh: %s" % (sname, has))
        S.update(phase="settle", t=0.0)
        return
    if S["phase"] == "settle" and S["t"] > 1.5:
        ok = sweep.start_for_test(True)
        log("A4 forced start accepted: %s" % ok)
        S.update(phase="run", t=0.0, t0=unreal.GameplayStatics.get_time_seconds(world))
        return
    if S["phase"] == "run":
        now = unreal.GameplayStatics.get_time_seconds(world)
        pos = tracker.get_position()
        root = boss.get_actor_location()
        floor = root.z - boss.get_editor_property("capsule_component").get_scaled_capsule_half_height()
        sw = sword_of(boss)
        parts = ["t=%.3f montage_pos=%.3f phase=%s blade_active=%s blade_angle=%.1f" % (now - S["t0"], pos, tracker.get_phase_name(), sweep.is_blade_active(), sweep.get_blade_angle()), "root_yaw=%.1f" % boss.get_actor_rotation().yaw]
        if sw:
            tf = sw.get_world_transform()
            origin = tf.translation
            ltip, axis_name, half = local_tip(sw)
            tip = unreal.MathLibrary.transform_location(tf, ltip)
            if S["ticks"] == 0:
                b = sw.get_editor_property("static_mesh").get_bounds()
                log("sword mesh local bounds origin=(%.1f,%.1f,%.1f) extent=(%.1f,%.1f,%.1f); tip axis %s, local tip=(%.1f,%.1f,%.1f); component world scale=(%.3f,%.3f,%.3f)" % (
                    b.origin.x, b.origin.y, b.origin.z, b.box_extent.x, b.box_extent.y, b.box_extent.z, axis_name, ltip.x, ltip.y, ltip.z, tf.scale3d.x, tf.scale3d.y, tf.scale3d.z))
            parts.append(describe("mesh_origin", origin, root, floor))
            parts.append(describe("mesh_tip", tip, root, floor))
            for sname in ("SOCKET_Weapon_End",):
                try:
                    if sw.does_socket_exist(sname):
                        parts.append(describe(sname, sw.get_socket_location(sname), root, floor))
                except Exception:
                    pass
        log(" ".join(parts))
        S["ticks"] += 1
        if now - S["t0"] > 2.4:
            S["phase"] = "end"
            S["t"] = 0.0
        return
    if S["phase"] == "end" and S["t"] > 1.0:
        enc.hold_for_test(False)
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
        log("done, %d ticks logged" % S["ticks"])


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())


handle = unreal.register_slate_post_tick_callback(tick)
log("geometry probe registered")
