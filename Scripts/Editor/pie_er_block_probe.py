"""
Probe (lead, Claude, 2026-11-06; guard counter design input): what happens on the PLAYER when the arena's pack boss hits a blocking player.
The player stands 220 cm in front of the boss facing it and holds the real guard key (Gamepad_LeftShoulder) for the whole run; the boss is NOT held, so it
attacks. Every tick logs any change of: the player's montage, the player's tags that contain Block/Guard/Hit/Stun/Parry, health and stamina.
Player health is refilled every 2 s so the probe survives. 35 s. Log prefix [BlockProbe]. Read-only (no property set in PIE, KI-083).
"""
import unreal

log = lambda m: unreal.log("[BlockProbe] " + m)
state = {"phase": "start", "t": 0.0, "last": {}}
handle = None


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def attr(actor, tag):
    c = comp(actor, "BP_AttributesComponent_C")
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % tag)
    try:
        return round(c.call_method("Get Current Attribute Value", args=(t,)), 1)
    except Exception:
        return None


def montage(actor):
    mc = actor.get_components_by_class(unreal.SkeletalMeshComponent)
    inst = mc[0].get_anim_instance() if mc else None
    m = inst.get_current_active_montage() if inst else None
    return m.get_name() if m else None


def tags_of(pawn):
    try:
        names = [str(x.get_editor_property("tag_name")) for x in pawn.call_method("GetOwnedGameplayTags").get_editor_property("gameplay_tags")]
    except Exception as e:
        return "tags?%s" % e
    keep = [n for n in names if any(k in n for k in ("Block", "Guard", "Hit", "Stun", "Parry", "Stagger"))]
    return ",".join(sorted(keep))


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("SUMMARY probe finished")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def _tick(dt):
    s = state
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="wake", t=0.0)
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    if pawn is None or boss is None:
        return
    dbg = comp(boss, "RPGCombatDebug")
    if dbg and s["phase"] in ("wake", "draw"):
        dbg.debug_refill_player()
    if s["phase"] == "wake":
        if s["t"] > 6.0:
            bl = boss.get_actor_location()
            fwd = boss.get_actor_forward_vector()
            pawn.set_actor_location(unreal.Vector(bl.x + fwd.x * 220, bl.y + fwd.y * 220, bl.z), False, True)
            look = unreal.MathLibrary.find_look_at_rotation(pawn.get_actor_location(), bl)
            pawn.set_actor_rotation(unreal.Rotator(0, 0, look.yaw), False)
            pc.set_control_rotation(unreal.Rotator(0, 0, look.yaw))
            # probe2: the player died during setup and the light press drew nothing. Hold the boss, enter combat through the pack tag, then release.
            enc = comp(boss, "RPGBossEncounter")
            if enc:
                enc.hold_for_test(True)
            c = unreal.GameplayTagContainer()
            c.import_text('(GameplayTags=((TagName="Ability.EnterCombat")))')
            comp(pawn, "BP_AdvancedAbilitySystemComponent_C").call_method("Try Activate Abilities By Tag", args=(c,))
            unreal.RPGInputTestUtils.set_key_down(pc, "Gamepad_RightTrigger", True)  # an R2 hold drew the sword in pie1/pie3
            s.update(phase="draw", t=0.0)
        return
    if s["phase"] == "draw":
        if s["t"] > 0.8 and not s.get("released"):
            unreal.RPGInputTestUtils.set_key_down(pc, "Gamepad_RightTrigger", False)
            s["released"] = True
        if s["t"] > 4.0:
            enc = comp(boss, "RPGBossEncounter")
            if enc:
                enc.hold_for_test(False)
            unreal.RPGInputTestUtils.set_key_down(pc, "Gamepad_LeftShoulder", True)
            s.update(phase="probe", t=0.0, refill=0.0)
            log("weapon drawn (montage seen: %s); guard held; boss at %.0f cm" % (s.get("draw_seen"), pawn.get_distance_to(boss)))
        else:
            m = montage(pawn)
            if m:
                s["draw_seen"] = m
        return
    if s["phase"] == "probe":
        if dbg:
            dbg.debug_refill_player()  # every tick: a dead player cannot guard (probe2)
        now = {"montage": montage(pawn), "tags": tags_of(pawn), "hp": attr(pawn, "Attribute.Health"), "stamina": attr(pawn, "Attribute.Stamina"), "boss_montage": montage(boss)}
        changed = {k: v for k, v in now.items() if s["last"].get(k) != v}
        if changed:
            log("t=%.2f %s" % (s["t"], " ".join("%s=%s" % (k, v) for k, v in changed.items())))
            s["last"].update(now)
        if s["t"] > 35.0:
            unreal.RPGInputTestUtils.set_key_down(pc, "Gamepad_LeftShoulder", False)
            finish()
            s["phase"] = "done"


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish()


handle = unreal.register_slate_post_tick_callback(tick)
