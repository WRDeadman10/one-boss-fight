import traceback
import unreal
try:
    g = unreal.load_asset("/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone")
    n = g.num_sockets()
    print("[PS] mesh num_sockets=%s" % n)
    print("[PS] names %s" % [str(g.get_socket_by_index(i).get_editor_property("socket_name")) for i in range(n)])
    print("[PS] skeleton dir %s" % [x for x in dir(g.get_editor_property("skeleton")) if "sock" in x.lower()])
except Exception:
    print("[PS] " + traceback.format_exc())
