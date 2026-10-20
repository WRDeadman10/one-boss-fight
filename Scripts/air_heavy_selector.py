"""
Jump heavy, selector edit. GA_Player_MeleeBase_Combined "Update Desired Attack Ability" (the pack's attack selector, used by every weapon's melee ability):
when the character is falling it always chose Ability.Melee.FallingAttack (light air attack) or nothing. New route inside the falling path:
  IsFalling -> [new] Branch(CanActivateStrongAttack?) -> then: SetDesiredAttackAbility(Ability.Melee.StrongAttack) -> Return(true)
                                                        else: the existing light-air logic
so a buffered strong input in the air plays the weapon's own heavy montage (GetAttackMontages(StrongAttack) = StrongAttackMontages).
Weapons without a heavy montage (twinblades, polearm): CanActivateStrongAttack? is false there, they keep the light air attack.
Pack asset edited in place (git-ignored): run again after a pack re-import. Needs the editor open. Guards against running twice.
Usage: MSYS_NO_PATHCONV=1 python -I Scripts/air_heavy_selector.py
"""
import sys

sys.path.insert(0, __file__.rsplit("Scripts", 1)[0] + "Scripts")
from bp_edit import Graph, call  # noqa: E402

BP = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/Player/GA_Player_MeleeBase_Combined"
BP_CLASS = BP + ".GA_Player_MeleeBase_Combined_C"
GRAPH = "Update Desired Attack Ability"
nodes = call("blueprint_query", {"operation": "get_nodes", "blueprint_path": BP, "graph_name": GRAPH})["data"]["nodes"]


def guid(prefix):
    hits = [n["node_guid"] for n in nodes if n["node_guid"].startswith(prefix)]
    assert len(hits) == 1, (prefix, hits)
    return hits[0]


already = [n for n in nodes if n["class"] == "K2Node_CallFunction" and "StrongAttack" in str(n["pins"]) and n["pos_x"] == -300 and n["pos_y"] == -1300]
if already:
    sys.exit("selector edit already applied")

IS_FALLING_BRANCH, FALL_BRANCH, RET_TRUE = guid("7B7A5C3D"), guid("A344E5D5"), guid("2F4EF731")
g = Graph(BP, GRAPH)
check = g.add("CallFunction", -300, -1300, function="CanActivateStrongAttack?", target_class=BP_CLASS)
branch = g.add("Branch", -300, -1200)
setter = g.add("CallFunction", -60, -1260, function="SetDesiredAttackAbility", target_class=BP_CLASS)
g.pin(setter, "InDesiredAttackAbilityTags", '(GameplayTags=((TagName="Ability.Melee.StrongAttack")))')
g.disconnect(IS_FALLING_BRANCH, "then", FALL_BRANCH, "execute")
g.connect(IS_FALLING_BRANCH, "then", branch, "execute")
g.connect(check, "ReturnValue", branch, "Condition")
g.connect(branch, "then", setter, "execute")
g.connect(setter, "then", RET_TRUE, "execute")
g.connect(branch, "else", FALL_BRANCH, "execute")
call("asset", {"operation": "save_asset", "asset_path": BP})
print("selector edit applied")
