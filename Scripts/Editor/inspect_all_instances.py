import unreal

arenas = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if isinstance(a, unreal.RPGGreyboxArena)]
if arenas:
    a = arenas[0]
    for comp in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        count = comp.get_instance_count()
        sm_name = comp.static_mesh.get_name() if comp.static_mesh else "None"
        print(f"InstancedComp: {comp.get_name()}, Mesh: {sm_name}, Instances: {count}")

    # Are there any other actors in the level?
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    print("All level actors:")
    for act in actors:
        if not act.get_name().startswith("Default__"):
            print(f"  {act.get_name()} ({act.get_class().get_name()}) at {act.get_actor_location()}")
