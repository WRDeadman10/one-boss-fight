import unreal

arenas = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if isinstance(a, unreal.RPGGreyboxArena)]
if arenas:
    a = arenas[0]
    prop_mat = a.get_editor_property("floor_material")
    print("Arena floor_material property:", prop_mat.get_name() if prop_mat else "None")
    for comp in a.get_components_by_class(unreal.StaticMeshComponent):
        mat = comp.get_material(0)
        print(f"Component {comp.get_name()} static mesh: {comp.static_mesh.get_name() if comp.static_mesh else 'None'}, Mat0: {mat.get_name() if mat else 'None'}")
