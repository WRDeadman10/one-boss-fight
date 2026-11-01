# Authoring helper (lead, Claude): derives create_warp_content.py from the HIT-011 ring content script. Run once: python -I make_warp_script.py
import os

HERE = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(HERE, '..', 'B_HIT011', 'create_ring_content.py'), encoding='utf-8').read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:60], s.count(old))
    s = s.replace(old, new)


rep("DA_Sevarog_Ring_HIT011", "DA_Sevarog_Warp_ANM006")
rep("L_SevarogFrameworkProofHIT011", "L_SevarogFrameworkProofANM006")
s = s.replace("Move_Sevarog_HeavyRing_HIT011", "Move_Sevarog_HeavyWarp_ANM006")
i = s.index("ring = unreal.RPGBossMoveWindow()")
j = s.index("tag('RING_CARD'")
j = s.index("\n", j) + 1
new = '''# BOSS-ANM-006: the blade window stays as it is; the card gets a bounded warp from its commit to its active end (through the strike): at most 150 cm and 45 degrees in total, standoff 80 cm (design values, proposed).
commit = float(spec.get_editor_property('commit_seconds'))
active_end = float(spec.get_editor_property('active_end_seconds'))
tag('CARD_TIMES', {'commit': commit, 'active_start': float(spec.get_editor_property('active_start_seconds')), 'active_end': active_end})
if active_end - commit < 0.1:
    fatal('no room for a 0.1 s warp between commit and active end')
spec.set_editor_property('warp_start_seconds', commit)
spec.set_editor_property('warp_end_seconds', active_end)
spec.set_editor_property('warp_max_distance_cm', 150.0)
spec.set_editor_property('warp_max_angle_degrees', 45.0)
spec.set_editor_property('warp_standoff_cm', 80.0)
nc.set_editor_property('spec', spec)
back = nc.get_editor_property('spec')
if abs(float(back.get_editor_property('warp_max_distance_cm')) - 150.0) > 1e-3 or abs(float(back.get_editor_property('warp_max_angle_degrees')) - 45.0) > 1e-3 or abs(float(back.get_editor_property('warp_standoff_cm')) - 80.0) > 1e-3:
    fatal('warp readback mismatch')
if not lib.save_loaded_asset(nc):
    fatal('card save failed')
tag('WARP_CARD', {'start': commit, 'end': active_end, 'max_distance_cm': 150.0, 'max_angle_deg': 45.0, 'standoff_cm': 80.0})
'''
s = s[:i] + new + s[j:]
open(os.path.join(HERE, 'create_warp_content.py'), 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
