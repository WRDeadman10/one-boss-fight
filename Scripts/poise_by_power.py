"""
Poise damage by attack power, in the pack's GA_BaseHitReaction "Can Activate Ability?" (the gate installed by install_poise.py, which subtracts a constant 20).
Replaces the constant with  -20 - 30 * (HitData.GetAttackPower >= 3)  : power NONE/light 20, heavy and above (strong, charged, knockdown attack data) 50.
Nodes: Get Hit Data -> GetAttackPower -> To Integer (Byte) -> integer >= 3 -> Bool to Double -> x -30 -> + -20 -> Modify Attribute.Value.
Pack asset edited in place (git-ignored): run after install_poise.py on a re-imported pack. Needs the editor open. Guards against running twice.
Usage: MSYS_NO_PATHCONV=1 python -I Scripts/poise_by_power.py
"""
import sys

sys.path.insert(0, __file__.rsplit("Scripts", 1)[0] + "Scripts")
from bp_edit import Graph, call  # noqa: E402

HIT = "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/Abilities/GA_BaseHitReaction"
HITDATA = "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CollisionSystem/Objects/BP_HitData.BP_HitData_C"
GRAPH = "Can Activate Ability?"
M = "KismetMathLibrary"
nodes = call("blueprint_query", {"operation": "get_nodes", "blueprint_path": HIT, "graph_name": GRAPH})["data"]["nodes"]


def one(pred, what):
    hits = [n["node_guid"] for n in nodes if pred(n)]
    assert len(hits) == 1, (what, hits)
    return hits[0]


if any("Get Attack Power" in n["title"] for n in nodes):
    sys.exit("poise by power already installed")
get_hit_data = one(lambda n: n["title"].startswith("Get Hit Data"), "Get Hit Data")
modify = one(lambda n: n["title"].startswith("Modify Attribute"), "Modify Attribute")
g = Graph(HIT, GRAPH)
power = g.add("CallFunction", 100, 1250, function="GetAttackPower", target_class=HITDATA)
to_int = g.add("CallFunction", 400, 1250, function="Conv_ByteToInt", target_class=M)
ge = g.add("CallFunction", 600, 1250, function="GreaterEqual_IntInt", target_class=M)
to_dbl = g.add("CallFunction", 800, 1250, function="Conv_BoolToDouble", target_class=M)
mul = g.add("CallFunction", 1000, 1250, function="Multiply_DoubleDouble", target_class=M)
add = g.add("CallFunction", 1200, 1250, function="Add_DoubleDouble", target_class=M)
g.connect(get_hit_data, "ReturnValue", power, "self")
g.connect(power, "ReturnValue", to_int, "InByte")
g.connect(to_int, "ReturnValue", ge, "A")
g.pin(ge, "B", "3")
g.connect(ge, "ReturnValue", to_dbl, "InBool")
g.connect(to_dbl, "ReturnValue", mul, "A")
g.pin(mul, "B", "-30.0")
g.connect(mul, "ReturnValue", add, "A")
g.pin(add, "B", "-20.0")
g.connect(add, "ReturnValue", modify, "Value")
call("asset", {"operation": "save_asset", "asset_path": HIT})
print("poise by power installed")
