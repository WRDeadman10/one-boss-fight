"""G3 audit (log prefix [G3Probe], variables appear as LogRPGDebug OBJECT lines): starts PIE, asks the boss's debug component to dump what decides the player's hit on the boss:
the player's collision component with its trace targets (depth 2), the melee attack data assets, the attack cost and damage gameplay effects, the hit data class defaults and the hit reaction ability on the boss.
Run with Scripts/run_in_editor.py after the warm-up; read the log between the markers. Ends PIE."""
import unreal

log = lambda m: unreal.log("[G3Probe] " + m)
state = {"t": 0.0, "phase": "start", "done": False}
handle = None
BASE = "/Game/AdvancedARPGCombat/"
DATA = [BASE + "MeleeCombatSystem/Blueprints/DataAssets/AttackData/" + n for n in ("DefaultMeleeAttackData", "StrongMeleeAttackData", "ChargedMeleeAttackData", "MeleeKnockdownAttackData")]
CLASSES = [BASE + "MeleeCombatSystem/Blueprints/GameplayEffects/GE_MeleeAttackCost", BASE + "MeleeCombatSystem/Blueprints/GameplayEffects/GE_MeleeDamage", BASE + "AdvancedCombatFramework/CollisionSystem/Objects/BP_HitData"]


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def _tick(dt):
    global handle
    s = state
    s["t"] += dt
    if s["phase"] == "start" and s["t"] > 0.5:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
        s.update(phase="play", t=0.0)
        return
    if s["phase"] != "play":
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    if w is None:
        return
    if not s["done"] and s["t"] > 10.0:
        boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None)
        pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
        dbg = comp(boss, "RPGCombatDebug") if boss else None
        if dbg and pawn:
            log("=== BEGIN player collision component")
            dbg.dump_object(comp(pawn, "BP_CollisionComponent_C"), 2)
            log("=== BEGIN player combat component")
            dbg.dump_object(comp(pawn, "BP_CombatComponent_C"), 1)
            for p in DATA:
                log("=== BEGIN data asset %s" % p.split("/")[-1])
                dbg.dump_object(unreal.load_asset(p), 1)
            for p in CLASSES:
                cls = unreal.load_class(None, p + "." + p.split("/")[-1] + "_C")
                log("=== BEGIN class defaults %s" % p.split("/")[-1])
                if cls:
                    dbg.dump_object(unreal.get_default_object(cls), 1)
            log("=== END")
        else:
            log("no boss, debug component or pawn")
        s["done"] = True
    if s["t"] > 14.0:
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
