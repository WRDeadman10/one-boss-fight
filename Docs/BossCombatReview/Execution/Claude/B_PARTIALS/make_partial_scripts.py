# Authoring helper (lead, Claude): derives two content scripts. Run once: python -I make_partial_scripts.py
#  create_telegraph_content.py  (BOSS-ANM-002): from the cue content script of ANM-003: the hold card gets a THIRD cue, Telegraph, at 0.05 s (before the commit at 0.40 s): a BloodBurst + Sevarog_Effort_Ability_Primary.
#  create_flaskpunish_content.py (BOSS-PHS-004): from the AWR-006 greed content script: the same two cards with the reaction delay of SEL-009 (0.3 .. 0.6 s) ON, so the boss reacts to a flask only after a fair delay.
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def derive(src, dst, edits):
    s = open(os.path.join(HERE, '..', src), encoding='utf-8').read()
    for old, new in edits:
        assert s.count(old) == 1, (dst, old[:70], s.count(old))
        s = s.replace(old, new)
    open(os.path.join(HERE, dst), 'w', encoding='utf-8', newline='\n').write(s)


derive('B_CUE/create_cue_content.py', 'create_telegraph_content.py', [
    ("DA_Sevarog_Cue_ANM003", "DA_Sevarog_Telegraph_ANM002"),
    ("L_SevarogFrameworkProofCUE", "L_SevarogFrameworkProofANM002"),
    ("spec.set_editor_property('cues', [release, recovery])",
     "telegraph = unreal.RPGBossCue()\ntelegraph.set_editor_property('cue_id', 'Telegraph')\ntelegraph.set_editor_property('time_seconds', 0.05)   # BOSS-ANM-002: inside the telegraph phase [0, commit = 0.40 s]\n"
     "telegraph.set_editor_property('visual', unreal.RPGBossCueVisual.BLOOD_BURST)\ntelegraph.set_editor_property('sound', unreal.load_asset(SND + 'Sevarog_Effort_Ability_Primary'))\n"
     "spec.set_editor_property('cues', [telegraph, release, recovery])"),
    ("len(cues) != 2 or str(cues[0].get_editor_property('cue_id')) != 'HoldRelease'", "len(cues) != 3 or str(cues[1].get_editor_property('cue_id')) != 'HoldRelease'"),
    ("'attack_count': 4,", "'attack_count': 2,"),
])
s = open(os.path.join(HERE, 'create_telegraph_content.py'), encoding='utf-8').read()
s = s.replace("Move_Sevarog_HeavyHold_ANM003", "Move_Sevarog_HeavyTelegraph_ANM002")
open(os.path.join(HERE, 'create_telegraph_content.py'), 'w', encoding='utf-8', newline='\n').write(s)

derive('B_AWR006/create_greed_content.py', 'create_flaskpunish_content.py', [
    ("DA_Sevarog_Greed_AWR006", "DA_Sevarog_FlaskPunish_PHS004"),
    ("L_SevarogFrameworkProofAWR006", "L_SevarogFrameworkProofPHS004"),
    ("prof.set_editor_property('reposition_turn_deg_per_second', 180.0)\n",
     "prof.set_editor_property('reposition_turn_deg_per_second', 180.0)\nprof.set_editor_property('reaction_delay_min_seconds', 0.3)   # BOSS-SEL-009 / PHS-004: the boss reacts to a flask only after 0.3 .. 0.6 s (design values, proposed)\nprof.set_editor_property('reaction_delay_max_seconds', 0.6)\nprof.set_editor_property('reaction_seed', 5)\n"),
])
print('ok')
