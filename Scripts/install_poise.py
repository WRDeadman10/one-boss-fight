"""
Installs poise into the Advanced ARPG pack (stage 4). The pack is git-ignored and can be re-imported, which wipes these
edits; run this again after a re-import. Needs the editor open (UnrealClaude plugin server on port 3000) and the
Attribute.Poise tag in Config/DefaultGameplayTags.ini. Then run Scripts/Editor/poise_data.py in the editor (execute_script)
for the PlayerInfo / EnemyInfo data. Skips the graph edit if GA_BaseHitReaction already has the bUsesPoise variable.

What it builds (all of it measured in Scripts/Editor/pie_poise_test.py):
  * BP_PoiseExtendedAttribute (copy of the stamina attribute, tag Attribute.Poise, regenerates after 4 s)
  * GA_BaseHitReaction "Can Activate Ability?": when the parent check passes and bUsesPoise is true, poise drops by 20; if
    it stays above 0 the hit is absorbed (no hit reaction), otherwise poise refills to its maximum and the hit stuns.
    Characters without a poise attribute keep the stock behaviour (always stun).
  * bUsesPoise: true on the hit stun abilities, false on block reactions, knockdowns and the no-hit-data stun. Child
    Blueprint defaults are frozen when the variable is added, so every subclass is set explicitly.
Usage: python Scripts/install_poise.py   (Git Bash: set MSYS_NO_PATHCONV=1 first)
"""
import json
import sys
import urllib.error
import urllib.request

sys.path.insert(0, __file__.rsplit("Scripts", 1)[0] + "Scripts")
from bp_edit import Graph, call  # noqa: E402

A = "/Game/AdvancedARPGCombat/"
CORE = A + "AdvancedCombatFramework/CoreCombatSystem/"
ABIL = CORE + "Abilities/"
ATTR_COMPONENT = A + "AdvancedCombatFramework/AttributesSystem/BP_AttributesComponent.BP_AttributesComponent_C"
POISE_DAMAGE = -20.0
TAG = '(TagName="Attribute.Poise")'

# Existing nodes of the stock graph (guids are stable in the pack's asset).
ENTRY_VALID, PARENT_CALL = "ED2411CD41E04B6E38356C8FA768AD66", "D3AD98F746630B6140E156A7D4C34A1D"
RET_FALSE, RET_TRUE = "AD448F9940FF06267CE3E5B89655C735", "F872F7064492AF326D50D8A7A026BAB1"
HIT_STUN_USERS = ["GA_EnemyHitStun", "GA_AxeEnemy_HitStun", "GA_BowEnemy_HitStun", "GA_GS_Boss_HitStun", "GA_MagicEnemy_HitStun", "GA_PlayerHitStun",
                  "GA_SwordEnemy_HitStun", "GA_SwordnShield_Boss_HitStun", "GA_TestDummy_HitStun", "GA_ToughSwordEnemy_HitStun", "GA_HitStun"]
NO_POISE = ["GA_Knockdown", "GA_EnemyKnockdown", "GA_PlayerKnockdown", "GA_BlockReaction", "GA_EnemyBlockReaction", "GA_Sword_BlockReaction",
            "GA_Sword_BlockReaction_Shield", "GA_SwordnShield_Boss_BlockReaction", "GA_ToughSwordEnemy_BlockReaction", "GA_HitStun_NoHitData"]


def find(name):
    paths = {a["path"].split(".")[0] for a in call("asset_search", {"name_pattern": name, "path_filter": A, "limit": 50})["data"]["assets"] if a["name"] == name}
    return sorted(paths)


def main():
    # 1. The attribute class.
    if not find("BP_PoiseExtendedAttribute") and not call("asset", {"operation": "get_asset_info", "asset_path": "/Game/OneBossFight/Poise/BP_PoiseExtendedAttribute"}).get("success"):
        call("asset", {"operation": "duplicate", "asset_path": CORE + "Attributes/BP_StaminaExtendedAttribute", "destination_path": "/Game/OneBossFight/Poise/BP_PoiseExtendedAttribute"})
        call("class_defaults", {"operation": "set_defaults", "blueprint_path": "/Game/OneBossFight/Poise/BP_PoiseExtendedAttribute",
                                "properties": {"Extended Attribute Tag": TAG, "StatRegenCoolDown": 4.0, "CurrentRegenRate": 2.0, "InitialRegenRate": 2.0}})
        print("created BP_PoiseExtendedAttribute")

    # 2. The graph edit.
    hit = ABIL + "GA_BaseHitReaction"
    info = call("blueprint_query", {"operation": "inspect", "blueprint_path": hit, "include_variables": True})["data"]
    if any(v["name"] == "bUsesPoise" for v in info.get("variables", [])):
        print("GA_BaseHitReaction already has bUsesPoise: graph edit skipped")
    else:
        call("blueprint_modify", {"operation": "add_variable", "blueprint_path": hit, "variable_name": "bUsesPoise", "variable_type": "bool"})
        g = Graph(hit, "Can Activate Ability?")
        perf = g.add("CallFunction", 700, 700, function="GetPerformingActor")
        comp = g.add("CallFunction", 600, 600, function="GetComponentByClass", target_class="Actor")
        g.pin(comp, "ComponentClass", ATTR_COMPONENT)  # retypes the return pin to BP_AttributesComponent
        b_parent, b_comp, b_poise, b_uses = (g.add("Branch", 700, y) for y in (800, 1000, 1200, 900))
        uses = g.add("VariableGet", 500, 900, variable="bUsesPoise")
        modify = g.add("CallFunction", 900, 700, function="Modify Attribute", target_class=ATTR_COMPONENT)
        get_max = g.add("CallFunction", 900, 800, function="GetMaxAttributeValue", target_class=ATTR_COMPONENT)
        get_cur = g.add("CallFunction", 1100, 1000, function="Get Current Attribute Value", target_class=ATTR_COMPONENT)
        less = g.add("CallFunction", 1300, 1000, function="LessEqual_DoubleDouble", target_class="KismetMathLibrary")
        valid = g.add("CallFunction", 1500, 1000, function="IsValid", target_class="KismetSystemLibrary")
        set_cur = g.add("CallFunction", 1500, 1100, function="Set Current Attribute Value", target_class=ATTR_COMPONENT)
        g.disconnect(ENTRY_VALID, "Is Valid", RET_TRUE, "execute")
        g.disconnect(PARENT_CALL, "Condition", RET_TRUE, "Condition")
        g.connect(ENTRY_VALID, "Is Valid", b_parent, "execute")
        g.connect(PARENT_CALL, "Condition", b_parent, "Condition")
        g.connect(b_parent, "else", RET_FALSE, "execute")
        g.connect(b_parent, "then", b_uses, "execute")
        g.connect(uses, "bUsesPoise", b_uses, "Condition")
        g.connect(b_uses, "else", RET_TRUE, "execute")
        g.connect(b_uses, "then", b_comp, "execute")
        g.connect(perf, "ReturnValue", comp, "self")
        g.connect(comp, "ReturnValue", valid, "Object")
        g.connect(valid, "ReturnValue", b_comp, "Condition")
        g.connect(b_comp, "else", RET_TRUE, "execute")
        g.connect(b_comp, "then", modify, "execute")
        g.connect(comp, "ReturnValue", modify, "self")
        g.pin(modify, "AttributeTag", TAG)
        g.pin(modify, "ValueType", "NewEnumerator1")
        g.pin(modify, "CalculationType", "NewEnumerator0")
        g.pin(modify, "Value", str(POISE_DAMAGE))
        g.connect(modify, "then", b_poise, "execute")
        g.connect(comp, "ReturnValue", get_cur, "self"); g.pin(get_cur, "AttributeTag", TAG)
        g.connect(get_cur, "Value", less, "A"); g.pin(less, "B", "0.0")
        g.connect(less, "ReturnValue", b_poise, "Condition")
        g.connect(b_poise, "then", set_cur, "execute")
        g.connect(comp, "ReturnValue", set_cur, "self"); g.pin(set_cur, "AttributeTag", TAG)
        g.connect(comp, "ReturnValue", get_max, "self"); g.pin(get_max, "AttributeTag", TAG)
        g.connect(get_max, "Value", set_cur, "Value")
        g.connect(set_cur, "then", RET_TRUE, "execute")
        g.connect(b_poise, "else", RET_FALSE, "execute")
        g.pin(RET_TRUE, "Condition", "true")
        call("class_defaults", {"operation": "set_defaults", "blueprint_path": hit, "properties": {"bUsesPoise": True}})
        call("asset", {"operation": "save_asset", "asset_path": hit})

    # 3. Switch values, set explicitly because subclass defaults are frozen.
    for names, value in ((HIT_STUN_USERS, True), (NO_POISE, False)):
        for name in names:
            for path in find(name):
                call("class_defaults", {"operation": "set_defaults", "blueprint_path": path, "properties": {"bUsesPoise": value}})
                call("asset", {"operation": "save_asset", "asset_path": path})
                print("%s bUsesPoise=%s" % (name, value))


main()
