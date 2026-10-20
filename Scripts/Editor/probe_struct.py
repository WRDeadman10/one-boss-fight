import json, re, unreal
log = lambda m: unreal.log("[ProbeStruct] " + m)
bp = unreal.load_asset("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/Sword/GA_Sword_Melee")
cdo = unreal.get_default_object(bp.generated_class())
v = cdo.get_editor_property("AttackMontages")
t = v[0].export_text()
log("text: " + t[:900])
mapping = json.load(open(unreal.Paths.project_saved_dir() + "greystone_retarget_map.json"))
for m in re.findall(r"/Game/[A-Za-z0-9_/\-]+\.[A-Za-z0-9_\-]+", t):
    pkg = m.split(".")[0]
    log("  path %s mapped=%s" % (m, pkg in mapping))
