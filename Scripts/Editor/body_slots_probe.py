"""Logs the material slots of the imported Boss01 body. Log prefix [BodySlots]."""
import unreal
m = unreal.load_asset("/Game/OneBossFight/Boss01/Body/SK_Boss01_Body")
slots = m.get_editor_property("materials")
unreal.log("[BodySlots] %d slots: %s" % (len(slots), [(str(s.get_editor_property("material_slot_name")), s.get_editor_property("material_interface").get_name() if s.get_editor_property("material_interface") else None) for s in slots]))
