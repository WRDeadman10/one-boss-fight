"""Reflect over key pack Blueprints: own variables of their CDOs and the values of the data assets they use. Headless."""
import unreal
log = lambda m: unreal.log("[PackBP] " + m)
BASE = "/Game/AdvancedARPGCombat/"
MELEE = BASE + "MeleeCombatSystem/Blueprints/"
CORE = BASE + "AdvancedCombatFramework/CoreCombatSystem/"

def own_vars(obj):
    names = []
    for n in dir(obj):
        if n.startswith("_") or n in ("cast", "get_class", "get_name", "get_outer", "get_path_name", "get_world", "get_editor_property", "set_editor_property"):
            continue
        try:
            v = getattr(obj, n)
        except Exception:
            continue
        if callable(v):
            continue
        names.append((n, v))
    return names

def parent_name(asset, cls):
    try:
        return asset.get_editor_property("parent_class").get_name()
    except Exception:
        return "-"


def dump(path, max_items=60, skip_prefix=()):
    asset = unreal.load_asset(path)
    if asset is None:
        log("MISSING " + path); return
    cls = asset.generated_class() if hasattr(asset, "generated_class") else None
    obj = unreal.get_default_object(cls) if cls else asset
    log("== %s (%s) parent=%s" % (path.split("/")[-1], obj.get_class().get_name(), parent_name(asset, cls)))
    shown = 0
    for n, v in own_vars(obj):
        if any(n.startswith(p) for p in skip_prefix): continue
        text = str(v)
        if len(text) > 140: text = text[:140] + "..."
        log("   %s = %s" % (n, text)); shown += 1
        if shown >= max_items: log("   ..."); break

for p in (CORE + "BP_BaseCombatCharacter", MELEE + "BP_CombatPlayerCharacter", CORE + "AI/BP_MasterEnemy", MELEE + "AI/BP_MasterSoulEnemy",
          MELEE + "AI/BP_ExampleGreatSwordBoss", CORE + "DataAssets/BP_PlayerInfo", CORE + "DataAssets/BP_CombatStyle", CORE + "DataAssets/BP_AttackData",
          CORE + "AI/DataAssets/BP_EnemyInfo", CORE + "Abilities/GA_Attack", MELEE + "AI/GA_GS_Boss_CloseAttack"):
    dump(p)
for p in (MELEE + "DataAssets/PlayerInfo", MELEE + "AI/ExampleGreatSwordBoss", MELEE + "AI/ExampleGreatSwordBossCombatStyle", MELEE + "DataAssets/DefaultMeleeAttackData",
          MELEE + "DataAssets/DefaultPlayerAbilities"):
    dump(p)
