"""Camera ground clipping test. Scenarios (log prefix [CamClip]):
  P  pitch sweep standing still on the arena floor: control pitch from -85 to +85 in steps, wait for the camera to settle, log camera height above the floor, arm length used and whether the camera is inside geometry.
  M  moving: the player runs (injected move) while the camera is swung from level to looking up and back, fast; the minimum clearance seen is logged.
A camera is "clipped" when its centre is closer than the probe radius to a surface it should be outside of: below the floor surface, or inside blocking geometry (sphere overlap on the camera channel).
Needs a warm-up PIE after an editor start (pie_debug_overlay.py)."""
import math
import unreal

log = lambda m: unreal.log("[CamClip] " + m)
PITCHES = [-85, -60, -30, 0, 15, 30, 45, 60, 75, 85]
S = {"phase": "start", "t": 0.0, "i": 0, "wait": 0.0, "rows": [], "mode": "P", "min_clear": 1e9, "run_t": 0.0, "clipped": 0, "samples": 0}
handle = None


def floor_z(w, x, y, z_hint):
    hit = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(x, y, z_hint + 400), unreal.Vector(x, y, z_hint - 2000), unreal.TraceTypeQuery.TRACE_TYPE_QUERY2, False, [], unreal.DrawDebugTrace.NONE, True)
    if hit is None:
        return None  # python returns None when nothing was hit
    t = hit.to_tuple()
    return t[5].z if t[0] else None


def inside_geometry(w, loc, radius):
    """True when a sphere of this radius at loc overlaps something the camera channel blocks."""
    hit = unreal.SystemLibrary.sphere_trace_single(w, loc, unreal.Vector(loc.x, loc.y, loc.z + 0.1), radius, unreal.TraceTypeQuery.TRACE_TYPE_QUERY2, False, [], unreal.DrawDebugTrace.NONE, True)
    if hit is None:
        return False
    t = hit.to_tuple()
    return bool(t[0] and t[1])


def sample(w, pc, pawn):
    cm = pc.player_camera_manager
    cam = cm.get_camera_location()
    pl = pawn.get_actor_location()
    arm = pawn.get_components_by_class(unreal.SpringArmComponent)[0]
    fz = floor_z(w, cam.x, cam.y, cam.z)
    clear = (cam.z - fz) if fz is not None else None
    inside = inside_geometry(w, cam, 12.0)
    dist = math.sqrt((cam.x - pl.x) ** 2 + (cam.y - pl.y) ** 2 + (cam.z - pl.z) ** 2)
    return cam, clear, inside, dist, arm


def _tick(dt):
    global handle
    s = S
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0)
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    if pawn is None or s["t"] < 9.0:
        return
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None)
    if boss is not None:
        # the boss must neither wake nor hurt the player: a dead player ragdolls and respawns, which pollutes the camera data
        next(c for c in boss.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == "RPGBossEncounter").hold_for_test(True)
        next(c for c in boss.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == "RPGCombatDebug").debug_refill_player()
    if s["mode"] == "P":
        if s["i"] == 0 and s["wait"] == 0.0:
            # a clear spot: the arena floor near its middle, facing north
            pawn.set_actor_location_and_rotation(unreal.Vector(900, 0, 120), unreal.Rotator(0, 0, 0), False, True)
            s["wait"] = s["t"] + 1.5
            return
        if s["t"] < s["wait"]:
            return
        if s["i"] < len(PITCHES):
            p = PITCHES[s["i"]]
            if s.get("set") != s["i"]:
                pc.set_control_rotation(unreal.Rotator(roll=0, pitch=p, yaw=0))
                s["set"] = s["i"]
                s["wait"] = s["t"] + 1.6
                return
            cam, clear, inside, dist, arm = sample(w, pc, pawn)
            cr = pc.player_camera_manager.get_camera_rotation()
            ctl = pc.get_control_rotation()
            ao = arm.get_world_location() if hasattr(arm, "get_world_location") else arm.get_component_location()
            log("pitch %+3d: control pitch %.0f camera pitch %.0f, arm origin z %.0f, camera z %.0f, above floor %s, distance to player %.0f, inside geometry %s" % (p, ctl.pitch if ctl.pitch < 180 else ctl.pitch - 360, cr.pitch, ao.z, cam.z, "%.0f" % clear if clear is not None else "n/a", dist, inside))
            s["rows"].append((p, clear, inside, dist))
            s["i"] += 1
            return
        # sweep finished
        bad = [r for r in s["rows"] if (r[1] is not None and r[1] < 12.0) or r[2]]
        log("SWEEP done: %d of %d pitches clipped %s" % (len(bad), len(s["rows"]), [r[0] for r in bad]))
        s.update(mode="M", t=0.0, wait=0.0, i=0)
        return
    if s["mode"] == "M":
        s["run_t"] += dt
        # run forward along +X (towards the arena middle) while the pitch swings between -20 and +80 twice per second
        pc.set_control_rotation(unreal.Rotator(roll=0, pitch=30 + 50 * math.sin(s["run_t"] * 6.0), yaw=(s["run_t"] * 90.0) % 360))
        unreal.RPGInputTestUtils.set_key_down(pc, "W", True)
        cam, clear, inside, dist, arm = sample(w, pc, pawn)
        s["samples"] += 1
        if clear is not None:
            s["min_clear"] = min(s["min_clear"], clear)
        if inside or (clear is not None and clear < 12.0):
            s["clipped"] += 1
        if s["run_t"] > 6.0:
            unreal.RPGInputTestUtils.set_key_down(pc, "W", False)
            log("MOVING done: %d samples, %d clipped, minimum height above the floor %.0f cm" % (s["samples"], s["clipped"], s["min_clear"]))
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
