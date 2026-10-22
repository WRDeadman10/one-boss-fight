"""
What the pack does when the boss dies (log prefix [DeathProbe]): finds the boss's GA_EnemyRagdollDeath instance, logs its DeathMontages and the Death Task class, kills the boss through the pack's attribute (DebugKillBoss) and samples
every 0.25 s for 12 s: does the boss exist, is its mesh simulating physics (ragdoll), which montage plays, where is the pelvis, is the actor hidden or collision off. Mode from Saved/death_probe_mode.txt: "plain" (default) or "montage"
(DeathMontages of the live ability instance is first set to the montage asset /Game/OneBossFight/Boss01/Animations/AM_Boss01_DeathLegend, created by make_death_montage.py). One run per PIE: the dead boss is destroyed by the pack.
Run pie_debug_overlay.py once after an editor start first."""
import os
import unreal

log = lambda m: unreal.log("[DeathProbe] " + m)
_mf = os.path.join(unreal.SystemLibrary.get_project_directory(), "Saved", "death_probe_mode.txt")
MODE = open(_mf).read().strip() if os.path.exists(_mf) else "plain"
S = {"phase": "start", "t": 0.0, "step": 0, "wait": 0.0, "i": 0, "t0": 0.0}
handle = None


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()


def ability(boss, cls):
    asc = comp(boss, "BP_AdvancedAbilitySystemComponent_C")
    for a in asc.get_editor_property("CreatedAbilities"):
        if a is not None and a.get_class().get_name() == cls:
            return a
    return None


def _tick(dt):
    global handle
    s = S
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0, wait=9.0)
        return
    w = world()
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    if s["t"] < s["wait"]:
        return
    if s["step"] == 0:
        if boss is None:
            return
        comp(boss, "RPGBossEncounter").wake()
        comp(boss, "RPGBossEncounter").hold_for_test(True)
        s.update(step=1, wait=s["t"] + 2.5)
        return
    if s["step"] == 1:
        ab = ability(boss, "GA_EnemyRagdollDeath_C")
        log("death ability %s, DeathMontages %s, Random Montage Index %s, Death Task %s, mode %s" % (ab.get_name() if ab else None, ab.get_editor_property("DeathMontages") if ab else None, ab.get_editor_property("Random Montage Index?") if ab else None, ab.get_editor_property("Death Task") if ab else None, MODE))
        if ab is not None and MODE == "montage":
            import re
            m = unreal.load_asset("/Game/OneBossFight/Boss01/Animations/AM_Boss01_DeathLegend")
            # DeathMontages holds F_AbilityMontage structs (as sevarog_pack_05b_death_style.py): borrow one from the enter-combat ability and point its montage at ours
            enter = ability(boss, "GA_GS_Boss_EnterCombat_C")
            tpl = enter.get_editor_property("Enter Combat Montage")
            quote = chr(39)
            text = re.sub(r'AnimMontage_5_[0-9A-F]+="[^"]*"', lambda mm: 'AnimMontage_5_2620D50C4D110CA156B1A28F49A30836="/Script/Engine.AnimMontage' + quote + m.get_path_name() + quote + '"', tpl.export_text())
            tpl.import_text(text)
            ab.set_editor_property("DeathMontages", [tpl])
            log("DeathMontages set to %s" % ab.get_editor_property("DeathMontages"))
        s.update(step=2, wait=s["t"] + 0.5)
        return
    if s["step"] == 2:
        s["t0"] = s["t"]
        comp(boss, "RPGCombatDebug").debug_kill_boss()
        log("boss killed")
        s.update(step=3, wait=s["t"] + 0.1)
        return
    if s["step"] == 3:
        i = s["i"]
        if boss is None:
            log("t=%.2f the boss is gone (destroyed by the pack)" % (s["t"] - s["t0"]))
            unreal.unregister_slate_post_tick_callback(handle)
            handle = None
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
            return
        mesh = boss.get_components_by_class(unreal.SkeletalMeshComponent)[0]
        inst = mesh.get_anim_instance()
        m = inst.get_current_active_montage() if inst else None
        pelvis = mesh.get_socket_location("pelvis")
        log("t=%.2f simulating %s, montage %s (%s) at %s, pelvis z %.0f, actor z %.0f" % (s["t"] - s["t0"], mesh.is_simulating_physics(), m.get_name() if m else None, comp(boss, "RPGCombatDebug").debug_boss_montage_anim_name() if m else "-", ("%.2f" % inst.montage_get_position(m)) if m else None,
            pelvis.z, boss.get_actor_location().z))
        s["i"] += 1
        s["wait"] = s["t"] + 0.25
        if s["t"] - s["t0"] > 14.0:
            unreal.unregister_slate_post_tick_callback(handle)
            handle = None
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())


handle = unreal.register_slate_post_tick_callback(tick)
