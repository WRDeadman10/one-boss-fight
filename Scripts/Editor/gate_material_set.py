"""Sets the emissive intensity of MI_Arena_FogGate from Saved/gate_emissive.txt (default 60) and saves it. Log prefix [GateMat]."""
import os
import unreal

f = os.path.join(unreal.SystemLibrary.get_project_directory(), "Saved", "gate_emissive.txt")
value = float(open(f).read().strip()) if os.path.exists(f) else 60.0
mi = unreal.EditorAssetLibrary.load_asset("/Game/OneBossFight/Environment/Materials/MI_Arena_FogGate")
unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(mi, "Emissive intensity", value)
unreal.MaterialEditingLibrary.update_material_instance(mi)
unreal.EditorAssetLibrary.save_loaded_asset(mi)
unreal.log("[GateMat] emissive intensity set to %.1f" % value)
