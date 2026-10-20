import unreal

LEVEL = "/Game/OneBossFight/Levels/L_SevarogArena"
DR = "/Game/Deadly_Ruins/"

def main():
    world = unreal.EditorLevelLibrary.get_editor_world()
    arenas = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if isinstance(a, unreal.RPGGreyboxArena)]
    if not arenas:
        print("No RPGGreyboxArena found!")
        return
    arena = arenas[0]
    print("Found arena:", arena.get_name())

    # Load authentic Deadly Ruins assets
    pillar_intact = unreal.load_asset(DR + "Meshes/Architecture/SM_pillar1")
    pillar_cracked = unreal.load_asset(DR + "Meshes/Architecture/SM__pillar3")
    pillar_broken = unreal.load_asset(DR + "Meshes/Architecture/SM__pillar2")
    arch = unreal.load_asset(DR + "Meshes/Architecture/SM_archway_1")
    brazier = unreal.load_asset(DR + "Meshes/Prop/SM_Brazer")
    rubble = unreal.load_asset(DR + "Meshes/Prop/SM_brickrubble1")

    # Materials
    floor_mat = unreal.load_asset(DR + "Materials/Instances/MI_Floor_Relief")
    wall_mat = unreal.load_asset(DR + "Materials/Instances/MI_TIling_Brick")
    brazier_mat = unreal.load_asset(DR + "Materials/Instances/MI_TIling_Metal")

    # Assign meshes
    arena.set_editor_property("PillarIntact", pillar_intact)
    arena.set_editor_property("PillarCracked", pillar_cracked)
    arena.set_editor_property("PillarBroken", pillar_broken)
    arena.set_editor_property("EntranceArch", arch)
    arena.set_editor_property("Brazier", brazier)
    arena.set_editor_property("Rubble", rubble)

    # Assign materials - setting to None allows meshes to use their native authored PBR materials!
    arena.set_editor_property("FloorMaterial", floor_mat)
    arena.set_editor_property("PillarMaterial", None)
    arena.set_editor_property("WallMaterial", wall_mat)
    arena.set_editor_property("ArchMaterial", None)
    arena.set_editor_property("BrazierMaterial", brazier_mat)
    arena.set_editor_property("RubbleMaterial", None)

    # Increase rubble count slightly for better ancient atmosphere
    arena.set_editor_property("RubbleCount", 24)

    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    print("Arena successfully updated with authentic Deadly Ruins assets!")

main()
