import unreal

arenas = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if isinstance(a, unreal.RPGGreyboxArena)]
if arenas:
    a = arenas[0]
    fm = a.get_floor_mesh()
    prop_mat = a.get_editor_property("floor_material")
    comp_mat = fm.get_material(0)
    print("Arena floor_material property:", prop_mat.get_name() if prop_mat else "None")
    print("FloorMesh component material 0:", comp_mat.get_name() if comp_mat else "None")
