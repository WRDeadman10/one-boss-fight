import unreal

DR = "/Game/Deadly_Ruins/"

def main():
    arenas = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if isinstance(a, unreal.RPGGreyboxArena)]
    if not arenas:
        print("No RPGGreyboxArena found!")
        return
    arena = arenas[0]

    for comp in arena.get_components_by_class(unreal.StaticMeshComponent):
        name = comp.get_name()
        # Clear material overrides so each mesh uses its authored materials
        if name in ("Pillars", "PillarsCracked", "PillarsBroken", "Debris", "Arch"):
            comp.set_material(0, None)
            print(f"Cleared material override on {name}, now using: {comp.get_material(0).get_name() if comp.get_material(0) else 'None'}")
        elif name == "Floor":
            floor_mat = unreal.load_asset("/Game/OneBossFight/Environment/Materials/MI_Arena_Floor")
            comp.set_material(0, floor_mat)
            print(f"Set {name} to {floor_mat.get_name()}")
        elif name in ("Walls", "WallsDamaged"):
            wall_mat = unreal.load_asset(DR + "Materials/Instances/MI_TIling_Brick")
            comp.set_material(0, wall_mat)
            print(f"Set {name} to {wall_mat.get_name()}")
        elif name == "Braziers":
            metal_mat = unreal.load_asset(DR + "Materials/Instances/MI_TIling_Metal")
            comp.set_material(0, metal_mat)
            print(f"Set {name} to {metal_mat.get_name()}")

    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    print("Done resetting component materials!")

main()
