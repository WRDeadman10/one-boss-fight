# Builds Claude/F11/create_f11_content.py from the F8 authoring script (same four cards, band, posture values) plus the F11 clips. Offline text transform, writes one file.
import os
src = 'C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/F6c/create_f8_content.py'
dst = 'C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/F11/create_f11_content.py'
t = open(src, encoding='utf-8').read().replace('\r\n', '\n')


def rep(old, new):
    global t
    assert t.count(old) == 1, old[:60]
    t = t.replace(old, new)


rep("# F8 posture proof (C-448):", "# F11 stagger and phase transition animations proof (lead, Claude; owner decision 3 Option B, spec Antigravity/Reviews/F11_STAGGER_PHASE_ANIM_SPEC.md): the F8 profile (same four cards, band, posture 100 / hit 60) with stagger_seconds 4.0 and the Sevarog clips Stun_Start 1.7 s, Stun_Loop 2.033 s, Stun_End 0.733 s and the phase transition clip Soul_Siphon 1.833 s (clip choice = proof value, proposed; the owner can overrule). NEW profile and map only.\n# (kept from F8) F8 posture proof (C-448):")
rep("PROFILE_NAME = 'DA_Sevarog_PostureProof_F8'", "PROFILE_NAME = 'DA_Sevarog_AnimProof_F11'")
rep("LEVEL_PATH = DIR + '/L_SevarogFrameworkProofF8'", "LEVEL_PATH = DIR + '/L_SevarogFrameworkProofF11'")
rep("'stagger_seconds': 1.0", "'stagger_seconds': 4.0")
rep("prof.set_editor_property('phase_two_id', 'Phase_2')\n", """prof.set_editor_property('phase_two_id', 'Phase_2')
ANIM = '/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/'
CLIPS = {'stagger_start_anim': 'Stun_Start', 'stagger_loop_anim': 'Stun_Loop', 'stagger_end_anim': 'Stun_End', 'phase_transition_anim': 'Soul_Siphon'}
for prop, name in CLIPS.items():
    clip = unreal.load_asset(ANIM + name + '.' + name)
    if clip is None:
        fatal('clip missing ' + name)
    prof.set_editor_property(prop, clip)
prof.set_editor_property('anim_slot_name', 'FullBody')
for prop, name in CLIPS.items():
    g = prof.get_editor_property(prop)
    if g is None or g.get_name() != name:
        fatal('F11 clip readback mismatch ' + prop)
if str(prof.get_editor_property('anim_slot_name')) != 'FullBody':
    fatal('slot readback')
tag('F11_CLIPS', {k: v for k, v in CLIPS.items()})
""")
open(dst, 'w', encoding='utf-8', newline='\n').write(t)
print('ok', len(t))
