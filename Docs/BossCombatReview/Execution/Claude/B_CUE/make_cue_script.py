# Authoring helper (lead, Claude): derives create_cue_content.py from the ANM-006 warp content script. Run once: python -I make_cue_script.py
import os

HERE = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(HERE, '..', 'B_ANM006', 'create_warp_content.py'), encoding='utf-8').read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:60], s.count(old))
    s = s.replace(old, new)


rep("DA_Sevarog_Warp_ANM006", "DA_Sevarog_Cue_ANM003")
rep("L_SevarogFrameworkProofANM006", "L_SevarogFrameworkProofCUE")
s = s.replace("Move_Sevarog_HeavyWarp_ANM006", "Move_Sevarog_HeavyHold_ANM003")
i = s.index("# BOSS-ANM-006: the blade window stays")
j = s.index("tag('WARP_CARD'")
j = s.index("\n", j) + 1
new = '''# BOSS-ANM-003 / PAC-004 / QA-007: the blade window stays as it is. The card HOLDS its windup between the commit (0.40 s) and the active start (0.475 s): at 0.42 s the montage stops for a seeded 0.4 to 0.9 s, then goes on.
# Two cues, each with a visual AND a sound, distinct from each other in both: Release (when the hold ends: hit spark at the weapon, the Sevarog attack effort) and Recovery (at the end of the active state: dust at the boss's feet, the winded breathing).
# Every number is a design value, proposed. The sounds and the flipbook sheets are existing project / pack assets (no new art).
commit = float(spec.get_editor_property('commit_seconds'))
active_start = float(spec.get_editor_property('active_start_seconds'))
active_end = float(spec.get_editor_property('active_end_seconds'))
tag('CARD_TIMES', {'commit': commit, 'active_start': active_start, 'active_end': active_end})
hold_at = commit + 0.02
if not (commit <= hold_at < active_start):
    fatal('no room for a hold between commit and active start')
SND = '/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/'
snd_release = unreal.load_asset(SND + 'Sevarog_Effort_Attack')
snd_recovery = unreal.load_asset(SND + 'Sevarog_Effort_BreathingLowHealth')
if snd_release is None or snd_recovery is None:
    fatal('cue sounds not loaded')
release = unreal.RPGBossCue()
release.set_editor_property('cue_id', 'HoldRelease')
release.set_editor_property('at_hold_release', True)
release.set_editor_property('visual', unreal.RPGBossCueVisual.HIT_SPARK)
release.set_editor_property('sound', snd_release)
release.set_editor_property('socket', 'weapon_r')
recovery = unreal.RPGBossCue()
recovery.set_editor_property('cue_id', 'RecoveryOpen')
recovery.set_editor_property('time_seconds', active_end)
recovery.set_editor_property('visual', unreal.RPGBossCueVisual.DODGE_DUST)
recovery.set_editor_property('sound', snd_recovery)
spec.set_editor_property('hold_at_seconds', hold_at)
spec.set_editor_property('hold_min_seconds', 0.4)
spec.set_editor_property('hold_max_seconds', 0.9)
spec.set_editor_property('hold_seed', 11)
spec.set_editor_property('cues', [release, recovery])
nc.set_editor_property('spec', spec)
back = nc.get_editor_property('spec')
cues = list(back.get_editor_property('cues'))
if abs(float(back.get_editor_property('hold_max_seconds')) - 0.9) > 1e-4 or len(cues) != 2 or str(cues[0].get_editor_property('cue_id')) != 'HoldRelease' or cues[1].get_editor_property('sound') is None:
    fatal('hold or cue readback mismatch')
if not lib.save_loaded_asset(nc):
    fatal('card save failed')
tag('HOLD_CARD', {'hold_at': hold_at, 'min': 0.4, 'max': 0.9, 'cues': [str(c.get_editor_property('cue_id')) for c in cues]})
'''
s = s[:i] + new + s[j:]
s = s.replace("'attack_count': 1,", "'attack_count': 4,")
open(os.path.join(HERE, 'create_cue_content.py'), 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
