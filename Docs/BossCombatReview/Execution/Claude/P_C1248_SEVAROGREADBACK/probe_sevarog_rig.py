"""C-1248 Lead read-only rig readback for the Sevarog first-five card plan (C1247). Saves nothing.
Every engine call is guarded: an unexposed API prints 'n/a <reason>' and the probe continues."""
import unreal

ROOT = "/Game/ParagonSevarog/Characters/Heroes/Sevarog"
MESH = ROOT + "/Meshes/Sevarog"
SKEL = ROOT + "/Meshes/Sevarog_Skeleton"
ANIMBP = ROOT + "/Sevarog_AnimBlueprint"
SEQS = ["Swing1_Medium", "Swing2_Medium", "Swing3_Slow", "Speedburst", "Swing1_FAST_v2"]
NAMES = ["weapon_r", "root_weapon_end_r", "hand_r", "weapon_l", "root"]


def log(m):
    unreal.log("[SevRig] " + str(m))


def g(label, fn):
    try:
        return fn()
    except Exception as ex:  # read-only probe: never abort on one field
        return "n/a %s (%s)" % (label, type(ex).__name__)


def name_of(obj):
    return obj.get_path_name() if hasattr(obj, "get_path_name") else str(obj)


mesh = unreal.EditorAssetLibrary.load_asset(MESH)
skel = unreal.EditorAssetLibrary.load_asset(SKEL)
log("mesh=%s loaded=%s" % (MESH, mesh is not None))
log("skeleton asset=%s loaded=%s" % (SKEL, skel is not None))
if mesh is not None:
    log("mesh.skeleton=%s" % g("mesh.skeleton", lambda: name_of(mesh.get_editor_property("skeleton"))))
    n = g("num_sockets", lambda: mesh.num_sockets())
    log("mesh.num_sockets=%s" % n)
    if isinstance(n, int):
        for i in range(n):
            log("  socket[%d] %s" % (i, g("socket", lambda: (lambda s: "%s bone=%s" % (s.get_editor_property("socket_name"), s.get_editor_property("bone_name")))(mesh.get_socket_by_index(i)))))
    for nm in NAMES:
        log("mesh.find_socket(%s)=%s" % (nm, g("find_socket", lambda: (lambda s: "socket bone=%s" % s.get_editor_property("bone_name") if s else "None")(mesh.find_socket(nm)))))
seq0 = None
for s in SEQS:
    a = unreal.EditorAssetLibrary.load_asset(ROOT + "/Animations/" + s)
    if a is None:
        log("SEQ %s MISSING" % s)
        continue
    seq0 = seq0 or a
    log("SEQ %s skeleton=%s length=%s root_motion=%s" % (
        s, g("skeleton", lambda: name_of(a.get_editor_property("skeleton"))), g("len", lambda: "%.6f" % a.get_play_length()),
        g("root_motion", lambda: a.get_editor_property("enable_root_motion"))))
if seq0 is not None:
    for nm in NAMES:
        log("bone %s exists=%s" % (nm, g("does_bone_name_exist", lambda: unreal.AnimationLibrary.does_bone_name_exist(seq0, nm))))
bp = unreal.EditorAssetLibrary.load_asset(ANIMBP)
log("animbp=%s loaded=%s class=%s" % (ANIMBP, bp is not None, g("class", lambda: bp.get_class().get_name())))
log("FullBody slot: n/a (AnimBP slot metadata is not readable from Python; confirm in the editor or via the C++ validator)")
log("done")
