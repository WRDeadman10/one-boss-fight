"""G3 audit step 2 (log prefix [G3A]): prints the editable properties of the pack's melee attack data assets and of the weapon abilities' default objects (Claymore, Sword, DualSword, Twinblades melee abilities), to find where the player's posture damage, attack power, stamina cost and hit data live.
Only prints properties whose names contain one of the key words, plus every numeric or bool property of a data asset (they are small). Run with Scripts/run_in_editor.py."""
import unreal

log = lambda m: unreal.log("[G3A] " + m)
BASE = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/"
DATA = ["DataAssets/AttackData/DefaultMeleeAttackData", "DataAssets/AttackData/StrongMeleeAttackData", "DataAssets/AttackData/ChargedMeleeAttackData", "DataAssets/AttackData/MeleeKnockdownAttackData"]
GAS = ["Weapons/Claymore/GA_Claymore_Melee", "Weapons/Sword/GA_Sword_Melee", "Weapons/DualSwords/GA_DuaSword_Melee", "Weapons/Twinblades/GA_Twinblades_Melee"]
KEYS = ("poise", "stamina", "cost", "power", "damage", "attack", "hyper", "armor", "combo", "multiplier", "tag")
skip = set(dir(unreal.Object)) | set(dir(unreal.DataAsset)) if hasattr(unreal, "DataAsset") else set(dir(unreal.Object))


def props(obj, everything):
    out = []
    for name in sorted(set(dir(obj)) - skip):
        if name.startswith("_"):
            continue
        low = name.lower()
        if not everything and not any(k in low for k in KEYS):
            continue
        try:
            v = obj.get_editor_property(name)
        except Exception:
            continue
        if callable(v):
            continue
        s = str(v)
        out.append("%s = %s" % (name, s[:160]))
    return out


for rel in DATA:
    obj = unreal.load_asset(BASE + rel)
    log("=== %s (%s)" % (rel, obj.get_class().get_name() if obj else None))
    for line in props(obj, True) if obj else []:
        log("   " + line)
for rel in GAS:
    cls = unreal.load_class(None, BASE + rel + "." + rel.split("/")[-1] + "_C")
    log("=== %s (class %s)" % (rel, cls.get_name() if cls else None))
    if cls:
        cdo = unreal.get_default_object(cls)
        for line in props(cdo, False):
            log("   " + line)
log("done")
