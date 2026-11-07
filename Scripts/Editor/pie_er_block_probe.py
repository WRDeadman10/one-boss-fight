"""
Lead-run, read-only ER block probe v4. Samples the player against the arena boss
after entering combat with the pack's mapped R key, then compares a real
Gamepad_LeftShoulder hold with direct per-frame IA_Block injection. Logs every
owned player gameplay tag on change, player/boss montages, health, stamina, and
input delivery. Health/stamina are refilled each tick through RPGCombatDebug.
No cause is inferred. Log prefix [BlockProbeV4].
"""
import unreal

log = lambda message: unreal.log("[BlockProbeV4] " + str(message))
state = {"phase": "start", "t": 0.0, "last": {}, "handle": None}

IA_BLOCK = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_Block"


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
        return round(component.call_method("Get Current Attribute Value", args=(tag,)), 1)
    except Exception as exc:
        return "error:%s" % exc


def active_montages(actor):
    found = []
    for mesh in actor.get_components_by_class(unreal.SkeletalMeshComponent):
        instance = mesh.get_anim_instance()
        montage = instance.get_current_active_montage() if instance else None
        if montage:
            found.append(montage.get_name())
    return ",".join(sorted(set(found))) or "None"


def all_tags(pawn):
    try:
        container = pawn.call_method("GetOwnedGameplayTags")
        tags = container.get_editor_property("gameplay_tags")
        return ",".join(sorted(str(tag.get_editor_property("tag_name")) for tag in tags))
    except Exception as exc:
        return "ERROR:%s" % exc


def actors():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((actor for actor in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)
                 if actor.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if world else None
    return world, pc, pawn, boss


def release_inputs(pc):
    if not pc:
        return
    for key in ("R", "Gamepad_LeftShoulder"):
        try:
            unreal.RPGInputTestUtils.set_key_down(pc, key, False)
        except Exception:
            pass


def finish(reason):
    handle = state.get("handle")
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        state["handle"] = None
    try:
        _, pc, _, _ = actors()
        release_inputs(pc)
    except Exception:
        pass
    log("SUMMARY finished reason=%s" % reason)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def sample_player(pawn, boss, label):
    now = {
        "player_tags_all": all_tags(pawn),
        "player_montages": active_montages(pawn),
        "player_hp": attr(pawn, "Attribute.Health"),
        "player_stamina": attr(pawn, "Attribute.Stamina"),
        "boss_montages": active_montages(boss),
    }
    changed = {key: value for key, value in now.items() if state["last"].get(key) != value}
    if changed:
        log("t=%.2f %s %s" % (state["t"], label,
                              " ".join("%s=%s" % pair for pair in changed.items())))
        state["last"].update(now)
    return now


def begin_arm(pc, arm):
    release_inputs(pc)
    state.update(phase=arm, t=0.0, arm_t=0.0, last={"arm": None}, inject_ok=0, inject_fail=0)
    if arm == "real_key_guard":
        ok = unreal.RPGInputTestUtils.set_key_down(pc, "Gamepad_LeftShoulder", True)
        log("ARM real_key_guard duration=15s key=Gamepad_LeftShoulder set_key_down=%s" % ok)
    else:
        state["block_action"] = unreal.load_asset(IA_BLOCK)
        log("ARM injected_IA_Block duration=15s action_loaded=%s asset=%s" %
            (bool(state["block_action"]), IA_BLOCK))


def _tick(delta_seconds):
    state["t"] += delta_seconds
    if state["phase"] == "start":
        if state["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            state.update(phase="wake", t=0.0)
        return

    world, pc, pawn, boss = actors()
    if not world or not pc or not pawn or not boss:
        if state["t"] > 12.0:
            finish("world/player/boss unavailable")
        return

    debug = comp(boss, "RPGCombatDebug")
    if not debug:
        finish("RPGCombatDebug unavailable; cannot keep player alive")
        return
    debug.debug_refill_player()  # each tick in every probe phase

    phase = state["phase"]
    if phase == "wake":
        if state["t"] > 6.0:
            boss_location = boss.get_actor_location()
            forward = boss.get_actor_forward_vector()
            pawn.set_actor_location(unreal.Vector(boss_location.x + forward.x * 220,
                                                  boss_location.y + forward.y * 220,
                                                  boss_location.z), False, True)
            look = unreal.MathLibrary.find_look_at_rotation(pawn.get_actor_location(), boss_location)
            facing = unreal.Rotator(0, 0, look.yaw)
            pawn.set_actor_rotation(facing, False)
            pc.set_control_rotation(facing)
            encounter = comp(boss, "RPGBossEncounter")
            if encounter:
                encounter.hold_for_test(True)
            result = unreal.RPGInputTestUtils.set_key_down(pc, "R", True)
            state.update(phase="combat_toggle", t=0.0, toggle_press=result,
                         toggle_released=False, player_montages_seen=set(), weapon_montage_seen=False)
            log("COMBAT toggle mapped_key=R pressed_via_input_mapping=%s boss_held=True" % result)
        return

    if phase == "combat_toggle":
        if not state["toggle_released"] and state["t"] >= 0.15:
            released = unreal.RPGInputTestUtils.set_key_down(pc, "R", False)
            state["toggle_released"] = True
            log("COMBAT toggle mapped_key=R released=%s" % released)
        montage_names = active_montages(pawn)
        if montage_names != "None":
            state["player_montages_seen"].update(montage_names.split(","))
        if "EquipWeapon" in montage_names or "Weapon" in montage_names:
            state["weapon_montage_seen"] = True
        sample_player(pawn, boss, "combat_toggle")
        if state["t"] >= 3.0:
            encounter = comp(boss, "RPGBossEncounter")
            if encounter:
                encounter.hold_for_test(False)
            log("COMBAT result player_weapon_montage_seen=%s player_montages_seen=%s" %
                (state["weapon_montage_seen"], ",".join(sorted(state["player_montages_seen"])) or "None"))
            begin_arm(pc, "real_key_guard")
        return

    if phase in ("real_key_guard", "injected_IA_Block"):
        state["arm_t"] += delta_seconds
        if phase == "injected_IA_Block":
            action = state.get("block_action")
            if action:
                if unreal.RPGInputTestUtils.inject_action(pc, action, unreal.Vector(1, 0, 0)):
                    state["inject_ok"] += 1
                else:
                    state["inject_fail"] += 1
        sample_player(pawn, boss, phase)
        if state["arm_t"] >= 15.0:
            log("ARM_RESULT arm=%s seconds=%.2f injected_ok_frames=%d injected_failed_frames=%d" %
                (phase, state["arm_t"], state["inject_ok"], state["inject_fail"]))
            if phase == "real_key_guard":
                begin_arm(pc, "injected_IA_Block")
            else:
                finish("both guard input arms complete")


def tick(delta_seconds):
    try:
        _tick(delta_seconds)
    except Exception:
        import traceback
        log("ERROR tick_exception=%s" % traceback.format_exc())
        finish("tick exception")


state["handle"] = unreal.register_slate_post_tick_callback(tick)
