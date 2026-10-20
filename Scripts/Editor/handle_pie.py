import unreal

sub = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
game_world = sub.get_game_world()
print("Game world in PIE:", game_world.get_path_name() if game_world else "None")
if game_world:
    print("Ending PIE...")
    sub.request_end_play_map()
