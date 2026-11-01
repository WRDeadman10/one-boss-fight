# Authoring helper (lead, Claude): derives create_greed_content.py from the AWR-008 dodge content script. Run once: python -I make_greed_script.py
import os

HERE = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(HERE, '..', 'B_AWR008', 'create_dodge_content.py'), encoding='utf-8').read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:60], s.count(old))
    s = s.replace(old, new)


rep("DA_Sevarog_DodgeMemory_AWR008", "DA_Sevarog_Greed_AWR006")
rep("L_SevarogFrameworkProofAWR008", "L_SevarogFrameworkProofAWR006")
i = s.index("prof.set_editor_property('dodge_history_depth'")
j = s.index("tag('DODGE'")
j = s.index("\n", j) + 1
s = s[:i] + '''prof.set_editor_property('reposition_max', 3)   # kept from the dodge proof
prof.set_editor_property('reposition_turn_deg_per_second', 180.0)
''' + s[j:]
rep("e.set_editor_property('back_dodge_weight_multiplier', 2.0 if move == 'Move_Sevarog_SwingSlow_F7' else 1.0)   # BOSS-AWR-008: the swing stands in for the forward roll-catch card",
    "e.set_editor_property('greed_weight_multiplier', 2.0 if move == 'Move_Sevarog_SwingSlow_F7' else 1.0)   # BOSS-AWR-006: the swing stands in for the fast anti-greed card MC-03 (design value, proposed)")
open(os.path.join(HERE, 'create_greed_content.py'), 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
