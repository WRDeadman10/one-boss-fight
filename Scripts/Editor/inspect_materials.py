"""
inspect_materials.py - Inspects material assignments for all 6 character builds.
"""
import unreal

builds = [
    "SKM_Samurai",
    "SKM_IndianYoddha",
    "SKM_MedievalWarrior",
    "SKM_Viking",
    "SKM_IndianGoddess",
    "SKM_GirlWarrior"
]

print("="*60)
for b in builds:
    m = unreal.load_asset(f"/Game/OneBossFight/Characters/Builds/{b}")
    if not m:
        print(f"[-] {b} not found!")
        continue
    mats = m.get_editor_property("materials")
    print(f"=== {b} ({len(mats)} material slots) ===")
    for i, s in enumerate(mats):
        mat_interface = s.get_editor_property("material_interface")
        slot_name = s.get_editor_property("material_slot_name")
        print(f"  [{i}] slot '{slot_name}' -> {mat_interface.get_name() if mat_interface else 'None'}")
print("="*60)
