"""V-C041 diagnostic: timestamp input injection to first observed player montage change.

Run once per route in L_SevarogArena. For the selected/data route set
H019_ENCOUNTER_DEFINITION before starting the editor; leave it unset for legacy.
This is a PIE driver for the Lead. Measurements are bounded by game-tick sampling
and are reported as observations, not hardware input latency or acceptance limits.
Log prefix: [InputMontageLatency].
"""
import os
import time
import unreal

LOG = "[InputMontageLatency] "
INPUT_ROOT = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/"
CASES = [
    ("attack", "IA_NormalAttack"),
    ("dodge", "IA_Dodge"),
    ("parry", "IA_Parry"),
]
S = {"phase": "start", "elapsed": 0.0, "case": 0, "press_until": 0.0,
     "press_real": None, "baseline": None, "done": False}
HANDLE = None


def log(message):
    unreal.log(LOG + message)


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent)
                 if c.get_class().get_name() == name), None)


def player_montage(pawn):
    meshes = pawn.get_components_by_class(unreal.SkeletalMeshComponent)
    inst = meshes[0].get_anim_instance() if meshes else None
    montage = inst.get_current_active_montage() if inst else None
    return montage.get_name() if montage else None


def enter_combat_tag():
    tags = unreal.GameplayTagContainer()
    tags.import_text('(GameplayTags=((TagName="Ability.EnterCombat")))')
    return tags


def finish(reason):
    global HANDLE
    if HANDLE is not None:
        unreal.unregister_slate_post_tick_callback(HANDLE)
        HANDLE = None
    log("finished: " + reason)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("driver error: " + traceback.format_exc())
        finish("exception")


def _tick(dt):
    S["elapsed"] += dt
    if S["phase"] == "start":
        if S["elapsed"] > 0.5:
            selection = os.environ.get("H019_ENCOUNTER_DEFINITION", "").strip()
            if selection:
                unreal.SystemLibrary.execute_console_command(None, "rpg.EncounterDefinition " + selection)
                log("route=data selection=" + selection)
            else:
                log("route=legacy (H019_ENCOUNTER_DEFINITION unset)")
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            S.update(phase="setup", elapsed=0.0)
        return

    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
    pawn = pc.get_controlled_pawn() if pc else None
    if pawn is None:
        if S["elapsed"] > 20.0:
            finish("no possessed player within 20 game seconds")
        return

    if S["phase"] == "setup":
        # Let the map settle and remove boss pressure as in the existing input probes.
        for actor in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character):
            if actor.get_class().get_name() == "BP_ExampleGreatSwordBoss_C":
                actor.destroy_actor()
        if S["elapsed"] > 2.0:
            comp(pawn, "BP_AdvancedAbilitySystemComponent_C").call_method(
                "Try Activate Abilities By Tag",
                args=(enter_combat_tag(),))
            S.update(phase="settle", elapsed=0.0)
        return

    if S["phase"] == "settle":
        if S["elapsed"] > 1.0:
            S.update(phase="arm", elapsed=0.0)
        return

    if S["phase"] == "arm":
        if S["case"] >= len(CASES):
            finish("three action samples recorded")
            return
        name, action_name = CASES[S["case"]]
        S["baseline"] = player_montage(pawn)
        S["press_real"] = time.perf_counter()
        S["press_until"] = S["elapsed"] + 0.12
        S["phase"] = "observe"
        log("press action=%s baseline=%s" % (name, S["baseline"]))
        return

    if S["phase"] == "observe":
        name, action_name = CASES[S["case"]]
        if S["elapsed"] <= S["press_until"]:
            action = unreal.load_asset(INPUT_ROOT + action_name)
            unreal.RPGInputTestUtils.inject_action(pc, action, unreal.Vector(1, 0, 0))
        current = player_montage(pawn)
        if current is not None and current != S["baseline"]:
            latency_ms = (time.perf_counter() - S["press_real"]) * 1000.0
            log("sample action=%s montage=%s observed_ms=%.2f tick_s=%.5f" %
                (name, current, latency_ms, dt))
            S.update(phase="cooldown", elapsed=0.0)
        elif S["elapsed"] - S["press_until"] > 2.0:
            log("NO_MONTAGE_CHANGE action=%s baseline=%s final=%s" %
                (name, S["baseline"], current))
            S.update(phase="cooldown", elapsed=0.0)
        return

    if S["phase"] == "cooldown" and S["elapsed"] > 2.0:
        S["case"] += 1
        S.update(phase="arm", elapsed=0.0)


HANDLE = unreal.register_slate_post_tick_callback(tick)
log("driver registered")
