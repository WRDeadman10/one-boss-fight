"""
verify_builds.py - Verifies all 6 character builds in Unreal Engine.
"""

import unreal

build_names = [
    "SKM_Samurai",
    "SKM_IndianYoddha",
    "SKM_MedievalWarrior",
    "SKM_Viking",
    "SKM_IndianGoddess",
    "SKM_GirlWarrior"
]

target_skel = unreal.load_asset("/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin")
print(f"Target Skeleton: {target_skel.get_path_name()}")

print("="*60)
all_ok = True
for name in build_names:
    path = f"/Game/OneBossFight/Characters/Builds/{name}"
    mesh = unreal.load_asset(path)
    if not mesh:
        print(f"[-] {name}: FAILED TO LOAD")
        all_ok = False
        continue
        
    skel = mesh.get_editor_property("skeleton")
    num_mats = len(mesh.get_editor_property("materials"))
    is_same_skel = (skel == target_skel)
    
    status = "OK" if is_same_skel else "SKELETON MISMATCH"
    print(f"[+] {name}: {status}")
    print(f"    Class: {mesh.get_class().get_name()}")
    print(f"    Skeleton: {skel.get_path_name() if skel else 'None'}")
    print(f"    Materials Count: {num_mats}")
    if not is_same_skel:
        all_ok = False

print("="*60)
print(f"OVERALL STATUS: {'ALL 6 BUILDS VERIFIED SUCCESSFULLY' if all_ok else 'SOME BUILDS FAILED'}")
