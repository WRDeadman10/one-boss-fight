"""Logs whether PIE is running and the boss HUD state. Log prefix [PieState]."""
import unreal

w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
unreal.log("[PieState] game world: %s" % (w.get_name() if w else None))
if w:
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None)
    pc = unreal.GameplayStatics.get_player_controller(w, 0)
    unreal.log("[PieState] boss=%s pc=%s pawn=%s" % (boss, pc, pc.get_controlled_pawn() if pc else None))
    if boss:
        hud = next((c for c in boss.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == "RPGBossHud"), None)
        unreal.log("[PieState] hud=%s state=%s victories=%s" % (hud, hud.get_state_name() if hud else None, hud.get_victory_count() if hud else None))
