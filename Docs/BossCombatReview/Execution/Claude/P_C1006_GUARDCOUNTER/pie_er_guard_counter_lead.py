"""Lead-run ER guard-counter probe for C-1004.

Starts L_SevarogArena PIE on the selected route, positions the player in the
Ember Warden's forward attack lane, holds real Gamepad_LeftShoulder (L1) while
the boss AI is active, and taps real Gamepad_RightTrigger (R2) only after the
engine log reports a successful guarded contact. It reports the actual player
hit-intake kind/data and boss HP delta. It never writes asset properties.

Run once per route. For data route set H019_ENCOUNTER_DEFINITION before editor
startup; leave unset for legacy. Inspect the paired LogRPGDodge successful
guard line and this probe's [ERGuardCounter] output. Owner clip review and
saved asset assignment remain separate gates. Log prefix: [ERGuardCounter].
"""
import os
from pathlib import Path
import unreal

LOG = "[ERGuardCounter] "
GUARD_CONFIRM = "successful guarded contact armed guard counter window"
COUNTER_ACCEPT = "guard counter accepted after successful block"
GUARD_KEY = "Gamepad_LeftShoulder"  # L1
COUNTER_KEY = "Gamepad_RightTrigger"  # R2
MAX_GUARD_SECONDS = 30.0
COUNTER_HOLD_SECONDS = 0.12
POST_COUNTER_SECONDS = 2.0

S = {"phase": "start", "elapsed": 0.0, "held": set(), "log_offsets": {},
     "guard_confirmed": False, "hp_before": None, "hp_after": None,
     "counter_accept_logged": False, "record_count_before": None,
     "record_count_after": None, "done": False}
HANDLE = None


def log(message):
    unreal.log(LOG + str(message))


def comp(actor, class_name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent)
                 if c.get_class().get_name() == class_name), None)


def attr(actor, tag_name):
    component = comp(actor, "BP_AttributesComponent_C")
    if not component:
        return None
    tag = unreal.GameplayTag()
    tag.import_text('(TagName="%s")' % tag_name)
    try:
        return float(component.call_method("Get Current Attribute Value", args=(tag,)))
    except Exception as exc:
        return "error:%s" % exc


def montage_name(actor):
    for mesh in actor.get_components_by_class(unreal.SkeletalMeshComponent):
        instance = mesh.get_anim_instance()
        montage = instance.get_current_active_montage() if instance else None
        if montage:
            return montage.get_name()
    return "None"


def actors():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)
                 if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if world else None
    return world, pc, pawn, boss


def set_key(pc, key, down):
    if not pc:
        raise RuntimeError("player controller unavailable while changing " + key)
    ok = unreal.RPGInputTestUtils.set_key_down(pc, key, down)
    if down:
        S["held"].add(key)
    else:
        S["held"].discard(key)
    if not ok:
        raise RuntimeError("RPGInputTestUtils.set_key_down failed: " + key)
    log("input key=%s down=%s delivered=%s" % (key, down, ok))


def release_all(pc=None):
    pc = pc or S.get("last_pc")
    for key in list(S["held"]):
        try:
            if pc:
                unreal.RPGInputTestUtils.set_key_down(pc, key, False)
        except Exception:
            pass
        S["held"].discard(key)


def tail_guard_confirmations():
    """Read only the active project's UE log; confirmation is the source log line."""
    log_dir = Path(unreal.Paths.project_saved_dir()) / "Logs"
    try:
        paths = sorted(log_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not paths:
            return 0
        path = paths[0]
        size = path.stat().st_size
        # Existing logs were baselined before PIE. A log created/rotated after
        # that point has no saved offset and must be scanned from byte zero.
        offset = S["log_offsets"].get(str(path), 0)
        if size < offset:  # log rotated/truncated
            offset = 0
        with path.open("r", encoding="utf-8", errors="replace") as stream:
            stream.seek(offset)
            text = stream.read()
            S["log_offsets"][str(path)] = stream.tell()
        matches = [line.strip() for line in text.splitlines()
                   if GUARD_CONFIRM in line or COUNTER_ACCEPT in line]
        for line in matches:
            if GUARD_CONFIRM in line:
                S["guard_confirmed"] = True
                log("GUARD_CONTACT_CONFIRMED source_log=%s line=%s" % (path.name, line[-400:]))
            if COUNTER_ACCEPT in line:
                S["counter_accept_logged"] = True
                log("COUNTER_ACCEPT_CONFIRMED source_log=%s line=%s" % (path.name, line[-400:]))
        return len(matches)
    except Exception as exc:
        log("guard_log_tail_unavailable=%s" % exc)
        return 0


def records(intake):
    if not intake:
        return None
    try:
        value = intake.call_method("GetRecordLines")
        return [str(row) for row in value]
    except Exception as exc:
        return ["record_read_error:%s" % exc]


def finish(reason):
    global HANDLE
    if S["done"]:
        return
    S["done"] = True
    if HANDLE is not None:
        unreal.unregister_slate_post_tick_callback(HANDLE)
        HANDLE = None
    try:
        _, pc, _, boss = actors()
        release_all(pc)
        encounter = comp(boss, "RPGBossEncounter") if boss else None
        if encounter:
            encounter.hold_for_test(False)
    except Exception:
        pass
    log("SUMMARY reason=%s guarded_contact_confirmed=%s counter_sent=%s counter_accept_logged=%s hp_before=%s hp_after=%s boss_hp_delta=%s record_count_before=%s record_count_after=%s" %
        (reason, S["guard_confirmed"], S.get("counter_sent", False), S["counter_accept_logged"],
         S["hp_before"], S["hp_after"],
         (S["hp_after"] - S["hp_before"] if isinstance(S["hp_before"], (float, int)) and
          isinstance(S["hp_after"], (float, int)) else "unknown"),
         S["record_count_before"], S["record_count_after"]))
    log("GUARD_COUNTER_EVIDENCE_BEGIN")
    for row in (S.get("records_after") or [])[-8:]:
        log("HIT_RECORD " + row)
    log("GUARD_COUNTER_EVIDENCE_END")
    if not S["guard_confirmed"]:
        log("LIMIT no successful-guard source log was observed; no counter-window acceptance may be claimed")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("ERROR " + traceback.format_exc())
        finish("tick exception")


def _tick(dt):
    S["elapsed"] += dt
    if S["phase"] == "start":
        if S["elapsed"] > 0.5:
            route = os.environ.get("H019_ENCOUNTER_DEFINITION", "").strip()
            if route:
                unreal.SystemLibrary.execute_console_command(None, "rpg.EncounterDefinition " + route)
                log("route=data selection=%s" % route)
            else:
                log("route=legacy H019_ENCOUNTER_DEFINITION=unset")
            try:
                log_dir = Path(unreal.Paths.project_saved_dir()) / "Logs"
                for path in log_dir.glob("*.log"):
                    S["log_offsets"][str(path)] = path.stat().st_size
            except Exception as exc:
                log("initial_log_offset_unavailable=%s" % exc)
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            S.update(phase="setup", elapsed=0.0)
        return

    world, pc, pawn, boss = actors()
    if not world or not pc or not pawn or not boss:
        if S["elapsed"] > 30.0:
            finish("world/player/Ember Warden unavailable")
        return

    S["last_pc"] = pc
    debug = comp(pawn, "RPGCombatDebug")
    if debug:
        debug.debug_refill_player()
    dodge = comp(pawn, "RPGDodgeTiming")
    intake = comp(pawn, "RPGHitIntake")
    if not dodge or not intake:
        finish("RPGDodgeTiming or RPGHitIntake missing")
        return

    if S["phase"] == "setup":
        if S["elapsed"] < 8.0:
            return
        encounter = comp(boss, "RPGBossEncounter")
        if not encounter:
            finish("RPGBossEncounter missing")
            return
        framework_executor = comp(boss, "RPGFrameworkMoveExecutor")
        encounter.hold_for_test(False)  # the boss must execute real AI swings
        location = boss.get_actor_location()
        forward = boss.get_actor_forward_vector()
        player_location = unreal.Vector(location.x + forward.x * 220.0,
                                        location.y + forward.y * 220.0, location.z)
        facing = unreal.MathLibrary.find_look_at_rotation(player_location, location)
        yaw = unreal.Rotator(0.0, facing.yaw, 0.0)
        pawn.set_actor_location_and_rotation(player_location, yaw, False, True)
        pc.set_control_rotation(yaw)
        set_key(pc, "R", True)  # Lead fix: stray indent in Codex original (no enclosing if)
        S.update(phase="toggle_release", elapsed=0.0)
        gc = unreal.load_asset("/Game/OneBossFight/Player/Animations/AM_ER_Attack_GuardCounter")
        dodge.guard_counter_montage = gc
        log("lead runtime assignment guard_counter=%s" % (gc.get_name() if gc else None))
        log("setup boss_held=False player_distance_cm=220 combat_toggle_key=R framework_executor_present=%s" %
            bool(framework_executor))
        return

    if S["phase"] == "toggle_release":
        if S["elapsed"] >= 0.15:
            set_key(pc, "R", False)
            if not dodge.is_elden_ring_input_active():
                finish("Elden Ring input context is inactive; cannot claim the mapped L1/R2 guard-counter route")
                return
            try:
                window = float(dodge.get_editor_property("guard_counter_window_seconds"))
            except Exception as exc:
                finish("cannot read GuardCounterWindowSeconds: %s" % exc)
                return
            if window <= 0.0:
                finish("GuardCounterWindowSeconds is not positive")
                return
            S.update(phase="guard", elapsed=0.0, hp_start=attr(boss, "Attribute.Health"),
                     hp_before=attr(boss, "Attribute.Health"), records_before=records(intake),
                     record_count_before=intake.get_boss_hit_count(), last_boss_montage="",
                     guard_window=window)
            log("armed hold L1 while boss AI swings; source guard contact triggers immediate R2 inside configured window=%.2fs" % window)
            set_key(pc, GUARD_KEY, True)
        return

    if S["phase"] == "guard":
        tail_guard_confirmations()
        current_boss_montage = montage_name(boss)
        if current_boss_montage != S.get("last_boss_montage"):
            S["last_boss_montage"] = current_boss_montage
            if current_boss_montage != "None":
                log("boss_montage=%s player_montage=%s player_hp=%s boss_hp=%s" %
                    (current_boss_montage, montage_name(pawn), attr(pawn, "Attribute.Health"),
                     attr(boss, "Attribute.Health")))
        if S["guard_confirmed"] and not S.get("counter_sent", False):
            S["guard_confirm_game_time"] = world.get_time_seconds()
            S["hp_before"] = attr(boss, "Attribute.Health")
            S["record_count_before"] = intake.get_boss_hit_count()
            S["records_before"] = records(intake)
            set_key(pc, GUARD_KEY, False)
            set_key(pc, COUNTER_KEY, True)
            S.update(phase="counter_release", elapsed=0.0, counter_sent=True,
                     guard_game_time=world.get_time_seconds())
            log("COUNTER_TAP same_editor_tick_as_guard_log game_time=%.3f configured_window=%.2fs source_acceptance_log_required=True boss_hp_before=%s" %
                (S["guard_game_time"], S["guard_window"], S["hp_before"]))
            return
        if S["elapsed"] >= MAX_GUARD_SECONDS:
            S["hp_after"] = attr(boss, "Attribute.Health")
            S["record_count_after"] = intake.get_boss_hit_count()
            S["records_after"] = records(intake)
            finish("timed out waiting for source-confirmed guarded contact")
        return

    if S["phase"] == "counter_release":
        tail_guard_confirmations()
        if S["elapsed"] >= COUNTER_HOLD_SECONDS:
            set_key(pc, COUNTER_KEY, False)
            S.update(phase="observe", elapsed=0.0)
            log("counter key released; sampling result for %.2fs" % POST_COUNTER_SECONDS)
        return

    if S["phase"] == "observe":
        tail_guard_confirmations()
        if S["elapsed"] >= POST_COUNTER_SECONDS:
            S["hp_after"] = attr(boss, "Attribute.Health")
            S["record_count_after"] = intake.get_boss_hit_count()
            S["records_after"] = records(intake)
            log("RESULT guard_contact_confirmed=%s counter_accept_logged=%s same_tick_as_guard_log=True configured_window=%.3fs player_montage=%s boss_hp_before=%s boss_hp_after=%s boss_hp_delta=%s hit_count_before=%s hit_count_after=%s" %
                (S["guard_confirmed"], S["counter_accept_logged"], S["guard_window"],
                 montage_name(pawn), S["hp_before"], S["hp_after"],
                 (S["hp_after"] - S["hp_before"] if isinstance(S["hp_before"], (float, int)) and
                  isinstance(S["hp_after"], (float, int)) else "unknown"),
                 S["record_count_before"], S["record_count_after"]))
            finish("counter result sampled")


HANDLE = unreal.register_slate_post_tick_callback(tick)
log("driver registered; L1 stays held until the source emits successful guarded contact, then R2 is tapped immediately")
