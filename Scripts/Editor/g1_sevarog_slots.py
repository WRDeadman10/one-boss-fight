"""Material slots, size and sockets of the Paragon Sevarog base skin (for Brief 02 T1). Log prefix [SevSlots]."""
import unreal
m = unreal.load_asset("/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog")
b = m.get_bounds()
unreal.log("[SevSlots] size %.0f x %.0f x %.0f cm, origin z %.0f" % (b.box_extent.x * 2, b.box_extent.y * 2, b.box_extent.z * 2, b.origin.z))
for i, mat in enumerate(m.get_editor_property("materials")):
    unreal.log("[SevSlots] slot %d %s -> %s" % (i, mat.get_editor_property("material_slot_name"), mat.get_editor_property("material_interface").get_name() if mat.get_editor_property("material_interface") else None))
unreal.log("[SevSlots] sockets %s" % [str(m.get_socket_by_index(i).get_editor_property("socket_name")) for i in range(m.num_sockets())])
try:
    unreal.log("[SevSlots] skeleton %s" % m.get_editor_property("skeleton").get_path_name())
except Exception as e:
    unreal.log("[SevSlots] skeleton ERR %s" % e)
