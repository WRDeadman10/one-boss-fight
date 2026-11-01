# Authoring helper (lead, Claude): derives create_grab_content.py from the HIT-011 ring content script. Run once: python -I make_grab_script.py
import os

HERE = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(HERE, '..', 'B_HIT011', 'create_ring_content.py'), encoding='utf-8').read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:60], s.count(old))
    s = s.replace(old, new)


rep("DA_Sevarog_Ring_HIT011", "DA_Sevarog_Grab_HIT012' + SUFFIX + '")
rep("L_SevarogFrameworkProofHIT011", "L_SevarogFrameworkProofHIT012' + SUFFIX + '")
s = s.replace("Move_Sevarog_HeavyRing_HIT011", "Move_Sevarog_HeavyGrab_HIT012")
# the variant: plain (no posture: the boss dies to three hits) or posture (two hits break the posture: stagger aborts the grab)
rep("import unreal\n", "import os\nimport unreal\n\nVARIANT = os.environ.get('HIT012_VARIANT', 'plain')   # plain | posture\nSUFFIX = '' if VARIANT == 'plain' else '_Posture'\n")
# the card is created once (the posture variant reuses it)
i = s.index("if lib.does_asset_exist(NEW_CARD):")
j = s.index("tag('RING_CARD'")
j = s.index("\n", j) + 1
card = '''if VARIANT == 'plain':
    if lib.does_asset_exist(NEW_CARD):
        fatal('destination exists, refusing: ' + NEW_CARD)
    if not lib.duplicate_asset(SRC, NEW_CARD):
        fatal('duplicate failed')
    nc = unreal.load_asset(NEW_CARD)
    spec = nc.get_editor_property('spec')
    spec.set_editor_property('move_id', 'Move_Sevarog_HeavyGrab_HIT012')
    direct = list(spec.get_editor_property('windows'))
    if len(direct) != 1:
        fatal('expected one window in HeavySlam_F7, got %d' % len(direct))
    d0 = direct[0]
    # BOSS-HIT-012: the blade window becomes the GRAB window: a wider radius (x3, as in the HIT-010 proof) so it reaches the target, caught to the left hand, released at 1.1 s (card time, inside the recovery).
    d0.set_editor_property('radius_cm', float(d0.get_editor_property('radius_cm')) * 3.0)
    d0.set_editor_property('grab', True)
    d0.set_editor_property('grab_attach_socket', 'hand_l')
    d0.set_editor_property('grab_release_seconds', 1.1)
    spec.set_editor_property('windows', [d0])
    nc.set_editor_property('spec', spec)
    back = nc.get_editor_property('spec').get_editor_property('windows')
    if len(back) != 1 or not back[0].get_editor_property('grab') or str(back[0].get_editor_property('grab_attach_socket')) != 'hand_l' or abs(float(back[0].get_editor_property('grab_release_seconds')) - 1.1) > 1e-4:
        fatal('window readback mismatch')
    if not lib.save_loaded_asset(nc):
        fatal('card save failed')
    tag('GRAB_CARD', {'release': 1.1, 'recovery_end': float(spec.get_editor_property('recovery_end_seconds'))})
'''
s = s[:i] + card + s[j:]
# the posture variant
rep("'posture_max': 0.0, 'player_posture_hit_amount': 0.0, 'stagger_seconds': 0.0, 'posture_regen_delay_seconds': 0.0, 'posture_regen_per_second': 0.0,",
    "'posture_max': 0.0 if VARIANT == 'plain' else 100.0, 'player_posture_hit_amount': 0.0 if VARIANT == 'plain' else 60.0, 'stagger_seconds': 0.0 if VARIANT == 'plain' else 1.0, 'posture_regen_delay_seconds': 0.0 if VARIANT == 'plain' else 6.0, 'posture_regen_per_second': 0.0 if VARIANT == 'plain' else 13.0,")
# the destination preflight must not refuse the shared card
open(os.path.join(HERE, 'create_grab_content.py'), 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
