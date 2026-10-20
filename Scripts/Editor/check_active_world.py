import unreal

def check():
    sub = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = sub.get_editor_world()
    print("Editor world:", world.get_path_name() if world else "None")
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    print(f"Actors count: {len(actors)}")
    for a in actors[:10]:
        print(f"  {a.get_name()} ({a.get_class().get_name()})")

check()
