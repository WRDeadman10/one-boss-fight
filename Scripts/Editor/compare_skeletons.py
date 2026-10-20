"""Compares the bone hierarchy of the imported SK_Boss01_Body with the pack mannequin (log prefix [SkelCmp])."""
import unreal

log = lambda m: unreal.log("[SkelCmp] " + m)


def hierarchy(mesh):
    mod = unreal.SkeletalMeshModifier() if hasattr(unreal, "SkeletalMeshModifier") else None
    sk = unreal.SkeletonModifier()
    sk.set_skeletal_mesh(mesh)
    names = [str(n) for n in sk.get_all_bone_names()]
    parents = {n: str(sk.get_parent_bone_name(n)) for n in names}
    return names, parents


a = unreal.load_asset("/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin_Simple")
b = unreal.load_asset("/Game/OneBossFight/Boss01/Body/SK_Boss01_Body")
log("body skeleton asset: %s" % (b.get_editor_property("skeleton").get_path_name() if b.get_editor_property("skeleton") else None))
na, pa = hierarchy(a)
nb, pb = hierarchy(b)
log("mannequin bones %d, body bones %d" % (len(na), len(nb)))
log("only in mannequin: %s" % [n for n in na if n not in nb][:30])
log("only in body: %s" % [n for n in nb if n not in na][:30])
diff = [(n, pa[n], pb[n]) for n in na if n in pb and pa[n] != pb[n]]
log("different parent: %s" % diff[:30])
log("order same: %s" % (na == nb))
if na != nb:
    for i, (x, y) in enumerate(zip(na, nb)):
        if x != y:
            log("first order difference at index %d: mannequin %s vs body %s" % (i, x, y))
            break
