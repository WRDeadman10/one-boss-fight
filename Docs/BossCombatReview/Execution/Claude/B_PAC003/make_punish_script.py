# Authoring helper (lead, Claude): derives create_punish_content.py from the AWR-006 greed content script. Run once: python -I make_punish_script.py
# Variants (env PAC003_VARIANT): pass (margin 0.3 s, the real cards must clear it) | fail (margin 0.9 s, no card can: the profile must be refused).
import os

HERE = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(HERE, '..', 'B_AWR006', 'create_greed_content.py'), encoding='utf-8').read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:60], s.count(old))
    s = s.replace(old, new)


rep("import unreal\n", "import os\nimport unreal\n\nVARIANT = os.environ.get('PAC003_VARIANT', 'pass')   # pass | fail\nSUFFIX = '' if VARIANT == 'pass' else '_Fail'\nMARGIN = 0.3 if VARIANT == 'pass' else 0.9\n")
rep("DA_Sevarog_Greed_AWR006", "DA_Sevarog_Punish_PAC003' + SUFFIX + '")
rep("L_SevarogFrameworkProofAWR006", "L_SevarogFrameworkProofPAC003' + SUFFIX + '")
rep("    e.set_editor_property('greed_weight_multiplier', 2.0 if move == 'Move_Sevarog_SwingSlow_F7' else 1.0)   # BOSS-AWR-006: the swing stands in for the fast anti-greed card MC-03 (design value, proposed)",
    "    e.set_editor_property('heavy_finisher', move == 'Move_Sevarog_HeavySlam_F7')   # BOSS-PAC-003: the slam is the heavy finisher (MC-04)")
# the profile punish fields go right after the reposition lines
anchor = "prof.set_editor_property('reposition_turn_deg_per_second', 180.0)\n"
rep(anchor, anchor + '''prof.set_editor_property('punish_margin_seconds', MARGIN)   # design values, proposed: 0.3 s light margin; the fail variant asks 0.9 s on purpose
prof.set_editor_property('player_light_montage', unreal.load_asset('/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/Attack_PrimaryA_Montage'))
prof.set_editor_property('player_heavy_montage', unreal.load_asset('/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/ChargedAttack_Montage'))
prof.set_editor_property('player_reach_cm', 150.0)   # design value, proposed: capsule 42 + the sword, until measured
if abs(float(prof.get_editor_property('punish_margin_seconds')) - MARGIN) > 1e-6 or prof.get_editor_property('player_light_montage') is None or prof.get_editor_property('player_heavy_montage') is None:
    fatal('punish readback mismatch')
tag('PUNISH', {'margin': MARGIN, 'reach': 150.0})
''')
open(os.path.join(HERE, 'create_punish_content.py'), 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
