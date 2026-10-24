"""Look test of the death remains in place (log prefix [RemainsPlace]): kills the boss like pie_remains.py, shoots the dead boss 1.5 s after the death (the pose to match), then the statue once formed, from the same camera spot. Screenshots land in Saved/Screenshots/WindowsEditor."""
import unreal

log = lambda m: unreal.log("[RemainsPlace] " + m)
S = {"phase": "start", "t": 0.0, "cam": None}
handle = None


def comp(a, n):
    return next((c for c in a.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == n), None)


def tags(*names):
    v = unreal.GameplayTagContainer()
    v.import_text("(GameplayTags=(%s))" % ",".join('(TagName="%s")' % n for n in names))
    return v


def look(pawn, pc, spot, target):
    yaw = unreal.MathLibrary.find_look_at_rotation(spot, target).yaw
    pawn.set_actor_hidden_in_game(True)
    pawn.set_actor_location_and_rotation(spot, unreal.Rotator(0, 0, yaw), False, True)
    pc.set_control_rotation(unreal.Rotator(roll=0, pitch=-10, yaw=yaw))


def _tick(dt):
    global handle
    S["t"] += dt
    if S["phase"] == "start":
        if S["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            S.update(phase="warm", t=0.0)
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    statues = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if a.get_class().get_name() == "RPGBossRemains"] if w else []
    if pawn is None:
        return
    if S["phase"] == "warm":
        if boss and S["t"] > 9.0:
            comp(boss, "RPGBossEncounter").wake()
            comp(boss, "RPGBossEncounter").hold_for_test(True)
            comp(boss, "RPGCombatDebug").debug_refill_player()
            comp(pawn, "BP_AdvancedAbilitySystemComponent_C").call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))
            S.update(phase="kill", t=0.0)
        return
    if S["phase"] == "kill" and S["t"] > 2.5:
        bl = boss.get_actor_location()
        S["cam"] = unreal.Vector(bl.x + 330.0, bl.y - 330.0, 150.0)
        S["target"] = unreal.Vector(bl.x, bl.y, 60.0)
        comp(boss, "RPGCombatDebug").debug_kill_boss()
        S.update(phase="corpse", t=0.0)
        return
    if S["phase"] == "corpse":
        if boss:
            look(pawn, pc, S["cam"], S["target"])
        if S["t"] > 2.6 and "shot_corpse" not in S:
            unreal.SystemLibrary.execute_console_command(w, "Shot ShowUI")
            S["shot_corpse"] = True
            log("shot dead boss")
        if boss is None and statues:
            S.update(phase="form", t=0.0)
        return
    if S["phase"] == "form":
        look(pawn, pc, S["cam"], S["target"])
        if S["t"] > 1.4 and "s1" not in S:
            S["s1"] = True
            unreal.SystemLibrary.execute_console_command(w, "Shot ShowUI")
            log("shot forming, dissolve %.2f" % statues[0].get_dissolve())
        if S["t"] > 4.5:
            unreal.SystemLibrary.execute_console_command(w, "Shot ShowUI")
            log("shot formed, dissolve %.2f" % statues[0].get_dissolve())
            S["phase"] = "end"
            S["t"] = 0.0
        return
    if S["phase"] == "end" and S["t"] > 1.0:
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
