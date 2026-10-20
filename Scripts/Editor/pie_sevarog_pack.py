"""
PIE check of Sevarog on the pack framework: spawns BP_SevarogBossPack in the pack demo level in front of the Greystone player and logs
what the boss does for DURATION seconds (distance, montage, health, poise of both, state). Run via execute_script with the demo level open.
Frames are captured by Scripts/CaptureLoop.ps1 (flag file Saved/m7_flag.txt). Log prefix [SevPie]. Deletes the boss from the editor level at the end.
"""
import os
import unreal

log = lambda m: unreal.log("[SevPie] " + m)
FLAG = os.path.join(unreal.Paths.project_saved_dir(), "m7_flag.txt")
BOSS = "/Game/OneBossFight/SevarogPack/BP_SevarogBossPack"
DURATION = 40.0
CHASE = False  # the player walks up to the boss once he is awake
FIGHT = True  # the player attacks back
KILL_AT = 0.0
GATE_TEST = True  # the player walks towards the sleeping boss until the entrance gate opens
FORCE = [(30.0, "GA_Sev_CloseRare")]  # (seconds, ability): start boss abilities on purpose to capture their effects
LIGHTNING_AT = 16.0  # seconds: ask the director for a lightning strike (0 = off)
PLAYER_KILL_AT = 0.0  # seconds: set the player's health to 0 to watch death and respawn (0 = off)
PHASE_AT = 0.0  # seconds: drop the boss to 700 HP (phase two at 750) so the roar and lightning start (0 = off)  # seconds into the fight: drop the boss to 20 HP so the next hit kills him (0 = off)
state = {"phase": "start", "t": 0.0, "log_t": 0.0, "boss": None}
handle = None
editor_boss = None


def flag(tag):
    if tag is None:
        if os.path.exists(FLAG):
            os.remove(FLAG)
    else:
        open(FLAG, "w").write(tag)


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


def player_fights(pawn, boss, dt):
    """Keeps the player healthy, facing the boss and swinging whenever the boss is within reach (test driver, not a bot worth shipping)."""
    st = state
    st["swing_t"] = st.get("swing_t", 0.0) + dt
    st["heal_t"] = st.get("heal_t", 0.0) + dt
    asc = comp(pawn, "BP_AdvancedAbilitySystemComponent_C")
    attrs = comp(pawn, "BP_AttributesComponent_C")
    to_boss = boss.get_actor_location() - pawn.get_actor_location()
    if st["heal_t"] > 1.0 and attrs and not st.get("no_heal"):
        st["heal_t"] = 0.0
        t = unreal.GameplayTag()
        t.import_text('(TagName="Attribute.Health")')
        try:
            attrs.call_method("Set Current Attribute Value", args=(t, 100.0))
        except Exception as e:
            log("heal failed " + str(e)[:80])
    if CHASE and 190.0 < to_boss.length() < 1400.0 and gate_open(boss):
        pawn.add_movement_input(unreal.Vector(to_boss.x, to_boss.y, 0).normal(), 1.0, False)
    if to_boss.length() < 420.0 and asc:
        yaw = unreal.MathLibrary.make_rot_from_x(unreal.Vector(to_boss.x, to_boss.y, 0)).yaw
        pawn.set_actor_rotation(unreal.Rotator(0, 0, yaw), False)
        if not st.get("combat"):
            asc.call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))
            st["combat"] = True
            st["swing_t"] = 0.0
        elif st["swing_t"] > 1.6:
            st["swing_t"] = 0.0
            asc.call_method("Try Activate Abilities By Tag", args=(tags("Ability.Melee"),))


def gate_open(boss):
    d = comp(boss, "RPGSevarogDirector")
    return d.is_gate_open() if d else True


def finish(reason):
    global handle
    flag(None)
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("finished: " + reason)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish("error")


def montage_of(actor):
    mc = actor.get_components_by_class(unreal.SkeletalMeshComponent)
    if not mc:
        return None
    inst = mc[0].get_anim_instance()
    m = inst.get_current_active_montage() if inst else None
    if not m:
        return None
    return "%s@%.2f" % (m.get_name(), inst.montage_get_position(m))


def bb_info(boss):
    try:
        ctrl = boss.get_controller()
        if ctrl is None:
            return "no controller"
        bbs = ctrl.get_components_by_class(unreal.BlackboardComponent)
        bb = bbs[0] if bbs else None
        if bb is None:
            return "no blackboard"
        return "ctrl=%s tgt=%s combat=%s dist=%s angle=%s beh=%s" % (ctrl.get_class().get_name(), bb.get_value_as_object("TargetActor"), bb.get_value_as_bool("bCombatEnabled"),
                                                                      bb.get_value_as_float("DistanceToTarget"), bb.get_value_as_float("AngleToTarget"), bb.get_value_as_name("CurrentBehaviorTag"))
    except Exception as e:
        return "bb err " + str(e)[:80]


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
    if pawn is None:
        return
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.load_class(None, BOSS + ".BP_SevarogBossPack_C"))), None)
    if boss is None:
        return
    if s["phase"] == "wait":
        if s["t"] > 8.0:
            log("player %s at %s | boss %s at %s" % (pawn.get_class().get_name(), pawn.get_actor_location(), boss.get_name(), boss.get_actor_location()))
            try:
                ref = boss.get_editor_property("EnemyInfoRef")
                log("boss EnemyInfoRef=%s mesh=%s anim=%s" % (ref.get_name() if ref else None,
                    boss.get_components_by_class(unreal.SkeletalMeshComponent)[0].get_editor_property("skeletal_mesh_asset").get_name(),
                    boss.get_components_by_class(unreal.SkeletalMeshComponent)[0].get_editor_property("anim_class")))
            except Exception as e:
                log("diag failed " + str(e)[:100])
            for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character):
                d = (a.get_actor_location() - pawn.get_actor_location()).length()
                if d < 4000:
                    log("  near: %s dist=%.0f" % (a.get_name(), d))
            s.update(phase="watch", t=0.0, log_t=99.0)
            flag("fight")
        return
    if s["phase"] == "watch":
        s["log_t"] += dt
        if s["log_t"] >= 1.0:
            s["log_t"] = 0.0
            d = (boss.get_actor_location() - pawn.get_actor_location()).length()
            log("gt=%5.1f t=%4.1f dist=%5.0f boss_montage=%s boss_hp=%s boss_poise=%s | player_montage=%s player_hp=%s poise=%s" % (
                unreal.GameplayStatics.get_time_seconds(w), s["t"], d, montage_of(boss), attr(boss, "Attribute.Health"), attr(boss, "Attribute.Poise"),
                montage_of(pawn), attr(pawn, "Attribute.Health"), attr(pawn, "Attribute.Poise")))
        mname = (montage_of(boss) or "").split("@")[0]
        if mname != s.get("last_montage", ""):
            s["last_montage"] = mname
            flag(mname.replace("AM_SevPack_", "").replace("AM_Sevarog_", "") or "idle")  # capture frames are named after the boss montage
            log("   boss montage -> %s (dist %.0f)" % (mname or "none", (boss.get_actor_location() - pawn.get_actor_location()).length()))
        if FIGHT:
            player_fights(pawn, boss, dt)
        if GATE_TEST and not gate_open(boss) and s["t"] > 2.0:
            d = boss.get_actor_location() - pawn.get_actor_location()
            pawn.add_movement_input(unreal.Vector(d.x, d.y, 0).normal(), 1.0, False)
            if int(s["t"] * 2) % 6 == 0:
                log("walking in, dist %.0f, gate closed" % d.length())
        if PLAYER_KILL_AT and s["t"] > PLAYER_KILL_AT and not s.get("pkilled"):
            s["pkilled"] = True
            s["no_heal"] = True
            pa = comp(pawn, "BP_AttributesComponent_C")
            t = unreal.GameplayTag()
            t.import_text('(TagName="Attribute.Health")')
            pa.call_method("Set Current Attribute Value", args=(t, 0.0))
            log("player health set to 0")
        if LIGHTNING_AT and s["t"] > LIGHTNING_AT and not s.get("bolt") and int(s["t"] * 4) % 4 == 0 and (montage_of(boss) is None):
            d = comp(boss, "RPGSevarogDirector")
            ok = d.call_method("TriggerLightning")
            log("director lightning -> %s" % ok)
            s["bolt"] = bool(ok)
        for when, ability in FORCE:
            if s["t"] > when and ("forced_" + ability) not in s:
                s["forced_" + ability] = True
                basc = comp(boss, "BP_AdvancedAbilitySystemComponent_C")
                cls = unreal.load_object(None, "/Game/OneBossFight/SevarogPack/Abilities/%s.%s_C" % (ability, ability))
                cc = comp(boss, "BP_CombatComponent_C")
                log("before: active=%s combat=%s" % (basc.call_method("Is Ability Active By Class?", args=(cls,)), cc.call_method("IsCombatEnabled?") if cc else None))
                log("forcing %s -> %s" % (ability, basc.call_method("Try Activate Ability by Class", args=(cls, True))))
                log("after: active=%s combat=%s montage=%s" % (basc.call_method("Is Ability Active By Class?", args=(cls,)), cc.call_method("IsCombatEnabled?") if cc else None, montage_of(boss)))
        if PHASE_AT and s["t"] > PHASE_AT and not s.get("phased"):
            s["phased"] = True
            c = comp(boss, "BP_AttributesComponent_C")
            t = unreal.GameplayTag()
            t.import_text('(TagName="Attribute.Health")')
            c.call_method("Set Current Attribute Value", args=(t, 700.0))
            log("boss health set to 700 (below 50 %)")
        if KILL_AT and s["t"] > KILL_AT and not s.get("killed"):
            s["killed"] = True
            c = comp(boss, "BP_AttributesComponent_C")
            t = unreal.GameplayTag()
            t.import_text('(TagName="Attribute.Health")')
            c.call_method("Set Current Attribute Value", args=(t, 1.0))
            log("boss health set to 20")
        if int(s["t"]) % 4 == 0 and s["log_t"] == 0.0:
            log("   bb: " + bb_info(boss))
        if s["t"] > DURATION:
            finish("done")


# Spawn the boss in the editor world, in front of the player start (levels that already contain Sevarog, such as L_SevarogArena, are used as they are).
if unreal.EditorLevelLibrary.get_editor_world().get_name() != "L_SevarogArena":
    # Spawn the boss in the editor world, in front of the player start.
    level = unreal.EditorLevelLibrary
    for old in level.get_all_level_actors():
        if old.get_class().get_name() == "BP_SevarogBossPack_C":
            old.destroy_actor()
    starts = [a for a in level.get_all_level_actors() if a.get_class().get_name() == "PlayerStart"]
    origin = starts[0].get_actor_location() if starts else unreal.Vector(0, 0, 200)
    fwd = starts[0].get_actor_forward_vector() if starts else unreal.Vector(1, 0, 0)
    loc = origin + fwd * 1100.0 + unreal.Vector(0, 0, 160)
    editor_boss = level.spawn_actor_from_class(unreal.load_class(None, BOSS + ".BP_SevarogBossPack_C"), loc, unreal.Rotator(0, 0, 180 + starts[0].get_actor_rotation().yaw if starts else 180))
    editor_boss.set_actor_label("SevPieBoss")
    log("player start %s, boss spawned at %s" % (origin, loc))
handle = unreal.register_slate_post_tick_callback(tick)
