import json

lines = open('Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/examples/boss_draft_profiles.json').readlines()
keys = ['stats', 'encounter_policy', 'stagger_policy', 'phase_flow', 'fireball', 'phase_dependencies', 'stagger_profile', 'dormant_wake', 'bleed', 'low_sweep', 'shockwave', 'heal_punish', 'look', 'close_clip_swap', 'death']

for k in keys:
    needle = f'"{k}":'
    for i, l in enumerate(lines):
        if needle in l:
            print(f'{k} -> line {i+1}: {l.strip()[:60]}')
            break

