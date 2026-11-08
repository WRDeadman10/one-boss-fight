"""Lead-run ER guard-counter probe for C-1004.

Starts L_SevarogArena PIE on the selected route, positions the player in the
Ember Warden's forward attack lane, injects pack IA_Block every frame while
the boss AI is active, and taps real Gamepad_RightTrigger (R2) only after the
engine log reports a successful guarded contact. It reports the actual player
hit-intake kind/data and boss HP delta. It never writes asset properties.

Run once per route. For data route set H019_ENCOUNTER_DEFINITION before editor
startup; leave unset for legacy. Inspect the paired LogRPGDodge successful
guard line and this probe's [ERGuardCounter] output. Owner clip review and
saved asset assignment remain separate gates. Log prefix: [ERGuardCounter].
"""
import os
import math
from pathlib import Path
import unreal

LOG = "[ERGuardCounter] "
GUARD_CONFIRM = "successful guarded contact armed guard counter window"
COUNTER_ACCEPT = "guard counter accepted after successful block"
COUNTER_KEY = "Gamepad_RightTrigger"  # R2
GUARD_ACTION_PATH = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_Block"
MAX_GUARD_SECONDS = 25.0
COUNTER_HOLD_SECONDS = 0.12
POST_COUNTER_SECONDS = 2.0

S = {"phase": "start", "elapsed": 0.0, "held": set(), "log_offsets": {},
     "guard_confirmed": False, "hp_before": None, "hp_after": None,
     "guard_source_log_seen": False, "guard_armed_api_seen": False,
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


def max_attr(actor, tag_name):
    component = comp(actor, "BP_AttributesComponent_C")
    if not component:
        raise RuntimeError("BP_AttributesComponent_C missing while reading max " + tag_name)
    tag = unreal.GameplayTag()
    tag.import_text('(TagName="%s")' % tag_name)
    return float(component.call_method("GetMaxAttributeValue", args=(tag,)))


def set_attr(actor, tag_name, value):
    component = comp(actor, "BP_AttributesComponent_C")
    if not component:
        raise RuntimeError("BP_AttributesComponent_C missing while setting " + tag_name)
    tag = unreal.GameplayTag()
    tag.import_text('(TagName="%s")' % tag_name)
    component.call_method("Set Current Attribute Value", args=(tag, float(value)))


def distance_cm(first, second):
    a = first.get_actor_location()
    b = second.get_actor_location()
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)


def montage_name(actor):
    for mesh in actor.get_components_by_class(unreal.SkeletalMeshComponent):
        instance = mesh.get_anim_instance()
        montage = instance.get_current_active_montage() if instance else None
        if montage:
            return montage.get_name()
    return "None"


def enter_combat_tag():
    tags = unreal.GameplayTagContainer()
    tags.import_text('(GameplayTags=((TagName="Ability.EnterCombat")))')
    return tags


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


def inject_guard_action(pc):
    if not pc:
        raise RuntimeError("player controller unavailable while injecting IA_Block")
    action = unreal.load_asset(GUARD_ACTION_PATH)
    if not action:
        raise RuntimeError("pack IA_Block asset could not be loaded")
    ok = unreal.RPGInputTestUtils.inject_action(pc, action, unreal.Vector(1.0, 0.0, 0.0))
    if not ok:
        raise RuntimeError("RPGInputTestUtils.inject_action failed for IA_Block")


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
                S["guard_source_log_seen"] = True
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
    log("SUMMARY reason=%s guarded_contact_confirmed=%s guard_armed_api_seen=%s guard_source_log_seen=%s counter_sent=%s counter_accept_logged=%s player_hp_before=%s player_hp_after=%s hp_before=%s hp_after=%s boss_hp_delta=%s record_count_before=%s record_count_after=%s" %
        (reason, S["guard_confirmed"], S["guard_armed_api_seen"], S["guard_source_log_seen"],
         S.get("counter_sent", False), S["counter_accept_logged"],
         S.get("player_hp_before"), S.get("player_hp_after"),
         S["hp_before"], S["hp_after"],
         (S["hp_after"] - S["hp_before"] if isinstance(S["hp_before"], (float, int)) and
          isinstance(S["hp_after"], (float, int)) else "unknown"),
         S["record_count_before"], S["record_count_after"]))
    log("GUARD_COUNTER_EVIDENCE_BEGIN")
    for row in (S.get("records_after") or [])[-8:]:
        log("HIT_RECORD " + row)
    log("GUARD_COUNTER_EVIDENCE_END")
    if not S["guard_armed_api_seen"]:
        log("LIMIT IsGuardCounterArmed never became true; no counter input was sent")
    if not S["guard_source_log_seen"]:
        log("NOTE successful-guard source log was not found in project Saved/Logs; armed-state polling is authoritative for probe input")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("ERROR " + traceback.format_exc())
        finish("tick exception")


def begin_guard_phase(pc, pawn, boss, dodge, intake):
    if os.environ.get("ER_GC_ASSIGN", "").strip() == "1":
        montage = unreal.load_asset("/Game/OneBossFight/Player/Animations/AM_ER_Attack_GuardCounter")
        if not montage:
            finish("ER_GC_ASSIGN=1 but GuardCounter montage asset could not be loaded")
            return
        try:
            dodge.guard_counter_montage = montage
        except Exception as exc:
            finish("ER_GC_ASSIGN=1 transient GuardCounterMontage assignment failed: %s" % exc)
            return
        log("runtime_guard_counter_montage_assigned=%s saved=False" % montage.get_name())
    try:
        window = float(dodge.get_editor_property("guard_counter_window_seconds"))
    except Exception as exc:
        finish("cannot read GuardCounterWindowSeconds: %s" % exc)
        return
    if window <= 0.0:
        finish("GuardCounterWindowSeconds is not positive")
        return
    debug = comp(boss, "RPGCombatDebug") if boss else None
    if not debug:
        finish("RPGCombatDebug missing on boss; cannot keep the guard probe alive")
        return
    debug.debug_refill_player()
    player_hp_at_guard_start = attr(pawn, "Attribute.Health")
    player_hp_max = max_attr(pawn, "Attribute.Health")
    if (not isinstance(player_hp_at_guard_start, (float, int)) or
            not math.isfinite(player_hp_at_guard_start) or
            abs(player_hp_at_guard_start - player_hp_max) > 0.5):
        finish("player health refill did not read back at max: current=%s max=%s" %
               (player_hp_at_guard_start, player_hp_max))
        return
    S.update(phase="guard", elapsed=0.0, hp_start=attr(boss, "Attribute.Health"),
             hp_before=attr(boss, "Attribute.Health"), records_before=records(intake),
             record_count_before=intake.get_boss_hit_count(), last_boss_montage="",
             guard_window=window, player_hp_at_guard_start=player_hp_at_guard_start,
             guard_source_log_seen=False, guard_armed_api_seen=False,
             player_hit_count_before=intake.get_boss_hit_count(),
             last_guard_state_elapsed=-0.5, guard_state_after_hit=False)
    log("input_context_active=True; injecting held pack IA_Block and refilling player health every guard tick; IsGuardCounterArmed triggers immediate R2 inside configured window=%.2fs player_hp_at_guard_start=%s" %
        (window, S["player_hp_at_guard_start"]))


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
        hp_before_refill = attr(boss, "Attribute.Health")
        hp_max = max_attr(boss, "Attribute.Health")
        if not math.isfinite(hp_max) or hp_max <= 0.0:
            finish("boss max health is not positive; refusing to arm probe")
            return
        if (not isinstance(hp_before_refill, (float, int)) or
                not math.isfinite(hp_before_refill)):
            finish("boss current health could not be read before refill: %s" % hp_before_refill)
            return
        if abs(hp_before_refill - hp_max) > 0.5:
            set_attr(boss, "Attribute.Health", hp_max)
        hp_after_refill = attr(boss, "Attribute.Health")
        if (not isinstance(hp_after_refill, (float, int)) or
                not math.isfinite(hp_after_refill) or abs(hp_after_refill - hp_max) > 0.5):
            finish("boss health max refill did not read back: before=%s max=%s after=%s" %
                   (hp_before_refill, hp_max, hp_after_refill))
            return
        location = boss.get_actor_location()
        player_location = unreal.Vector(location.x + 900.0, location.y, location.z)
        yaw = unreal.Rotator(0.0, 0.0, 180.0)
        pawn.set_actor_location_and_rotation(player_location, yaw, False, True)
        pc.set_control_rotation(yaw)
        asc = comp(pawn, "BP_AdvancedAbilitySystemComponent_C")
        if not asc:
            finish("player ability component unavailable; cannot activate Ability.EnterCombat")
            return
        asc.call_method("Try Activate Abilities By Tag", args=(enter_combat_tag(),))
        S.update(phase="settle", elapsed=0.0)
        log("setup boss_held=False player_distance_cm=900 enter_combat_tag=Ability.EnterCombat framework_executor_present=%s boss_hp_before_refill=%s boss_hp_max=%s boss_hp_after_refill=%s" %
            (bool(framework_executor), hp_before_refill, hp_max, hp_after_refill))
        return

    if S["phase"] == "settle":
        if S["elapsed"] >= 12.0:
            if not dodge.is_elden_ring_input_active():
                finish("Elden Ring input context is inactive after Ability.EnterCombat activation")
                return
            S.update(phase="warmup", elapsed=0.0, warmup_sent=False)
            log("input_context_active=True; starting accepted R2 draw/warmup before IA_Block probe")
        return

    if S["phase"] == "warmup":
        # Match the accepted Lead input probe: the first R2 charge draws the
        # weapon and is excluded from the guard-counter measurement.
        if S["elapsed"] >= 0.5 and not S["warmup_sent"]:
            set_key(pc, COUNTER_KEY, True)
            S["warmup_sent"] = True
        if S["elapsed"] >= 1.2 and COUNTER_KEY in S["held"]:
            set_key(pc, COUNTER_KEY, False)
        if S["elapsed"] >= 3.7:
            begin_guard_phase(pc, pawn, boss, dodge, intake)
        return

    if S["phase"] == "guard":
        # Enhanced Input injection is frame-scoped; repeat it to hold the
        # pack's actual block action. A raw L1 key event alone did not block.
        debug = comp(boss, "RPGCombatDebug") if boss else None
        if not debug:
            finish("RPGCombatDebug disappeared during guard window")
            return
        debug.debug_refill_player()
        inject_guard_action(pc)
        if S["elapsed"] - S.get("last_guard_state_elapsed", -0.5) >= 0.5:
            try:
                state = dodge.describe_guard_state()
            except Exception as exc:
                state = "ERROR:%s" % exc
            log("GUARD_STATE held_IA_Block=True elapsed=%.2f boss_hp=%s boss_hp_max=%s boss_montage=%s player_hp=%s player_hp_max=%s player_distance_cm=%.1f armed_api=%s %s" %
                (S["elapsed"], attr(boss, "Attribute.Health"), max_attr(boss, "Attribute.Health"),
                 montage_name(boss), attr(pawn, "Attribute.Health"), max_attr(pawn, "Attribute.Health"), distance_cm(pawn, boss),
                 dodge.is_guard_counter_armed(), state))
            S["last_guard_state_elapsed"] = S["elapsed"]
            hit_count = intake.get_boss_hit_count()
            before_hits = S.get("player_hit_count_before", 0)
            if (not S.get("guard_state_after_hit", False) and
                    isinstance(hit_count, int) and isinstance(before_hits, int) and hit_count > before_hits):
                try:
                    hit_state = dodge.describe_guard_state()
                except Exception as exc:
                    hit_state = "ERROR:%s" % exc
                log("GUARD_STATE_AFTER_REAL_HIT hit_count_before=%s hit_count_after=%s %s" %
                    (before_hits, hit_count, hit_state))
                S["guard_state_after_hit"] = True
        tail_guard_confirmations()
        armed = bool(dodge.is_guard_counter_armed())
        if armed and not S.get("guard_armed_api_seen", False):
            S["guard_confirmed"] = True
            S["guard_armed_api_seen"] = True
            log("GUARD_COUNTER_ARMED_API rising_edge=True game_time=%.3f; tapping R2 now" %
                world.get_time_seconds())
        current_boss_montage = montage_name(boss)
        if current_boss_montage != S.get("last_boss_montage"):
            S["last_boss_montage"] = current_boss_montage
            if current_boss_montage != "None":
                log("boss_montage=%s player_montage=%s player_hp=%s boss_hp=%s" %
                    (current_boss_montage, montage_name(pawn), attr(pawn, "Attribute.Health"),
                     attr(boss, "Attribute.Health")))
        if armed and not S.get("counter_sent", False):
            S["guard_confirm_game_time"] = world.get_time_seconds()
            S["hp_before"] = attr(boss, "Attribute.Health")
            S["player_hp_before"] = attr(pawn, "Attribute.Health")
            S["record_count_before"] = intake.get_boss_hit_count()
            S["records_before"] = records(intake)
            set_key(pc, COUNTER_KEY, True)
            S.update(phase="counter_release", elapsed=0.0, counter_sent=True,
                     guard_game_time=world.get_time_seconds())
            log("COUNTER_TAP armed_api_rising_edge=True game_time=%.3f configured_window=%.2fs source_log_seen=%s boss_hp_before=%s player_hp_before=%s" %
                (S["guard_game_time"], S["guard_window"], S["guard_source_log_seen"],
                 S["hp_before"], S["player_hp_before"]))
            return
        if S["elapsed"] >= MAX_GUARD_SECONDS:
            S["hp_after"] = attr(boss, "Attribute.Health")
            S["player_hp_after"] = attr(pawn, "Attribute.Health")
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
            S["player_hp_after"] = attr(pawn, "Attribute.Health")
            S["record_count_after"] = intake.get_boss_hit_count()
            S["records_after"] = records(intake)
            log("RESULT guard_armed_api_seen=%s guard_source_log_seen=%s counter_accept_logged=%s configured_window=%.3fs player_montage=%s boss_hp_before=%s boss_hp_after=%s boss_hp_delta=%s player_hp_before=%s player_hp_after=%s hit_count_before=%s hit_count_after=%s" %
                (S["guard_armed_api_seen"], S["guard_source_log_seen"], S["counter_accept_logged"], S["guard_window"],
                 montage_name(pawn), S["hp_before"], S["hp_after"],
                 (S["hp_after"] - S["hp_before"] if isinstance(S["hp_before"], (float, int)) and
                  isinstance(S["hp_after"], (float, int)) else "unknown"),
                 S.get("player_hp_before"), S.get("player_hp_after"),
                 S["record_count_before"], S["record_count_after"]))
            finish("counter result sampled")


HANDLE = unreal.register_slate_post_tick_callback(tick)
log("driver registered; pack IA_Block is injected every guard tick until the source emits successful guarded contact, then R2 is tapped immediately")
