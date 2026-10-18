"""Prints the Greystone AnimBP parent class and its variables/functions (what it expects from the pawn)."""
import unreal

PATH = "/Game/ParagonGreystone/Characters/Heroes/Greystone/Greystone_AnimBlueprint"


def log(m):
    unreal.log("[GreystoneABP] " + m)


bp = unreal.load_asset(PATH)
gen = bp.generated_class()
log("class=%s super=%s" % (gen.get_name(), gen.get_super_struct() if hasattr(gen, "get_super_struct") else "?"))
cdo = unreal.get_default_object(gen)
props = [p for p in dir(cdo) if not p.startswith("_") and not callable(getattr(cdo, p, None))]
log("props: %s" % props)
vals = {}
for p in props:
    try:
        vals[p] = str(cdo.get_editor_property(p))[:60]
    except Exception:
        pass
log("values: %s" % vals)
