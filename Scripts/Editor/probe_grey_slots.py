import traceback
import unreal
try:
    g = unreal.load_asset("/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone")
    for i, m in enumerate(g.get_editor_property("materials")):
        print("[Slot] %d name=%s mat=%s" % (i, m.get_editor_property("material_slot_name"), m.get_editor_property("material_interface").get_name() if m.get_editor_property("material_interface") else None))
    bp = unreal.load_asset("/Game/OneBossFight/GreystonePack/BP_GreystonePlayer")
    cdo = unreal.get_default_object(bp.generated_class())
    mc = cdo.get_editor_property("mesh")
    print("[Slot] player mesh override materials: %s" % [x.get_name() if x else None for x in mc.get_editor_property("override_materials")])
except Exception:
    print("[Slot] " + traceback.format_exc())
