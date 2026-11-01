# Authoring helper (lead, Claude): derives create_defense_content.py from the PAC-003 punish content script. Run once: python -I make_defense_script.py
# Variants (env DEF005_VARIANT): pass (backstep cooldown 3.0 s) | fail (cooldown 1.0 s: the profile must be refused with Framework.Profile.DefenseCooldown).
import os

HERE = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(HERE, '..', 'B_PAC003', 'create_punish_content.py'), encoding='utf-8').read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:70], s.count(old))
    s = s.replace(old, new)


rep("VARIANT = os.environ.get('PAC003_VARIANT', 'pass')   # pass | fail", "VARIANT = os.environ.get('DEF005_VARIANT', 'pass')   # pass | fail")
rep("MARGIN = 0.3 if VARIANT == 'pass' else 0.9", "MARGIN = 0.3")
rep("DA_Sevarog_Punish_PAC003", "DA_Sevarog_Defense_DEF005")
rep("L_SevarogFrameworkProofPAC003", "L_SevarogFrameworkProofDEF005")
rep("COOLDOWNS = {'Move_Sevarog_SwingSlow_F7': 0.1, 'Move_Sevarog_HeavySlam_F7': 0.1}",
    "COOLDOWNS = {'Move_Sevarog_HeavySlam_F7': 0.1, 'Move_Sevarog_BackStep_DEF005': 3.0 if VARIANT == 'pass' else 1.0}")
rep("ORDER = ['Move_Sevarog_SwingSlow_F7', 'Move_Sevarog_HeavySlam_F7']", "ORDER = ['Move_Sevarog_HeavySlam_F7', 'Move_Sevarog_BackStep_DEF005']")
# the new backstep card, created once (the fail variant reuses it), BEFORE the cards are loaded
anchor = "cards = [unreal.load_asset(DIR + '/Cards/' + m) for m in ORDER]"
card = '''# BOSS-DEF-005: ONE new card: a copy of HeavySlam_F7 turned into a BACKSTEP: the Sevarog Run_Bwd clip (in place, 1.6 s), no hit window, no damage, defensive, a warp that moves the boss AWAY (150 cm budget, back to 300 cm from the target at most).
# Timeline (design values, proposed): commit 0.10, the move starts at 0.30 (a 0.30 s telegraph), ends at 0.70, recovery ends at 1.45 (the clip is 1.6 s).
BACK = DIR + '/Cards/Move_Sevarog_BackStep_DEF005'
if VARIANT == 'pass':
    if lib.does_asset_exist(BACK):
        fatal('destination exists, refusing: ' + BACK)
    if not lib.duplicate_asset(DIR + '/Cards/Move_Sevarog_HeavySlam_F7', BACK):
        fatal('duplicate failed')
    bc = unreal.load_asset(BACK)
    bs = bc.get_editor_property('spec')
    clip = unreal.load_asset('/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Run_Bwd')
    if clip is None:
        fatal('Run_Bwd not loaded')
    bs.set_editor_property('move_id', 'Move_Sevarog_BackStep_DEF005')
    bs.set_editor_property('sequence', clip)
    bs.set_editor_property('windows', [])
    bs.set_editor_property('hp_damage', 0.0)
    bs.set_editor_property('defensive', True)
    bs.set_editor_property('warp_away', True)
    bs.set_editor_property('commit_seconds', 0.10)
    bs.set_editor_property('active_start_seconds', 0.30)
    bs.set_editor_property('active_end_seconds', 0.70)
    bs.set_editor_property('recovery_end_seconds', 1.45)
    bs.set_editor_property('warp_start_seconds', 0.30)
    bs.set_editor_property('warp_end_seconds', 0.70)
    bs.set_editor_property('warp_max_distance_cm', 150.0)
    bs.set_editor_property('warp_max_angle_degrees', 0.0)
    bs.set_editor_property('warp_standoff_cm', 300.0)
    bs.set_editor_property('hold_min_seconds', 0.0)
    bs.set_editor_property('hold_max_seconds', 0.0)
    bs.set_editor_property('cues', [])
    bc.set_editor_property('spec', bs)
    back = bc.get_editor_property('spec')
    if not back.get_editor_property('defensive') or not back.get_editor_property('warp_away') or len(list(back.get_editor_property('windows'))) != 0 or abs(float(back.get_editor_property('hp_damage'))) > 1e-6:
        fatal('backstep readback mismatch')
    if not lib.save_loaded_asset(bc):
        fatal('backstep save failed')
    tag('BACKSTEP_CARD', {'clip_length': float(clip.get_play_length()), 'play_rate': float(back.get_editor_property('play_rate')), 'telegraph': 0.30, 'budget_cm': 150.0})
'''
rep(anchor, card + anchor)
# the hug context makes the selector prefer the backstep when the target hugs the boss (profile anti-cheese: hugging within 200 cm), x3 (design values, proposed)
rep("prof.set_editor_property('reposition_turn_deg_per_second', 180.0)\n",
    "prof.set_editor_property('reposition_turn_deg_per_second', 180.0)\nprof.set_editor_property('anti_cheese_hug_range_cm', 200.0)\nprof.set_editor_property('anti_cheese_streak', 1)\n")
rep("    e.set_editor_property('heavy_finisher', move == 'Move_Sevarog_HeavySlam_F7')   # BOSS-PAC-003: the slam is the heavy finisher (MC-04)",
    "    e.set_editor_property('heavy_finisher', move == 'Move_Sevarog_HeavySlam_F7')   # BOSS-PAC-003: the slam is the heavy finisher (MC-04)\n    e.set_editor_property('hug_weight_multiplier', 3.0 if move == 'Move_Sevarog_BackStep_DEF005' else 1.0)   # BOSS-DEF-005 / PHS-005: a target that hugs the boss gets the backstep")
open(os.path.join(HERE, 'create_defense_content.py'), 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
