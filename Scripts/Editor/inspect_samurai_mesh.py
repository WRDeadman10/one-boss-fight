import unreal

m = unreal.load_asset("/Game/OneBossFight/Characters/Builds/SKM_Samurai")
print("SKM_Samurai:", m)
if m:
    mats = m.get_editor_property("materials")
    print(f"Num materials: {len(mats)}")
    for i, slot in enumerate(mats):
        print(f"Slot {i}: {slot.get_editor_property('material_slot_name')} -> {slot.get_editor_property('material_interface')}")
