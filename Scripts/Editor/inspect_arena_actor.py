import unreal

def main():
    world = unreal.EditorLevelLibrary.get_editor_world()
    print("Current level:", world.get_path_name())
    arenas = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if isinstance(a, unreal.RPGGreyboxArena)]
    print(f"Found {len(arenas)} RPGGreyboxArena actors")
    for a in arenas:
        print("Arena name:", a.get_name())
        for prop in ["PillarIntact", "PillarCracked", "PillarBroken", "WallIntact", "WallDamaged",
                     "EntranceArch", "Brazier", "Rubble", "FloorMaterial", "PillarMaterial",
                     "WallMaterial", "ArchMaterial", "BrazierMaterial", "RubbleMaterial"]:
            val = a.get_editor_property(prop)
            print(f"  {prop}: {val.get_path_name() if val else 'None'}")

main()
