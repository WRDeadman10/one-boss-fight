import unreal

print("AssetToolsHelpers:", hasattr(unreal, "AssetToolsHelpers"))
print("FbxImportUI:", hasattr(unreal, "FbxImportUI"))
print("FbxMeshImportData:", hasattr(unreal, "FbxMeshImportData"))
print("FbxSkeletalMeshImportData:", hasattr(unreal, "FbxSkeletalMeshImportData"))

skel = unreal.load_asset("/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin")
print("SK_CombatMannequin loaded:", skel)
