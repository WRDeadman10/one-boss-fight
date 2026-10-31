# F11 (lead, Claude): read-only dump of the Sevarog stagger / transition candidate clips (length, additive type, skeleton, root motion). Writes nothing.
# Run in the editor: run_editor_script.ps1 -Script <this file> -OutDir <absolute dir> -Task f11_anims -NullRhi 1
import json
import unreal

DIR = '/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/'
NAMES = ['Stun_Start', 'Stun_Loop', 'Stun_End', 'Hitreact_Front', 'Knock_back', 'Ultimate_Targeting', 'Ultimate_Swing_120fps', 'Soul_Siphon', 'Subjugation',
         'LevelStart', 'Victory_Emote', 'Emote_Pointing_MC_T3', 'Speedburst', 'Recall', 'Bound', 'Cast', 'Idle']
for n in NAMES:
    a = unreal.load_asset(DIR + n + '.' + n)
    if a is None:
        unreal.log('[F11_ANIM] %s MISSING' % n)
        continue
    info = {'name': n, 'class': a.get_class().get_name()}
    try:
        info['length'] = round(float(a.get_editor_property('sequence_length')), 4)
    except Exception:
        try:
            info['length'] = round(float(a.get_play_length()), 4)
        except Exception as e:
            info['length'] = 'n/a %s' % e
    for prop in ('additive_anim_type', 'enable_root_motion', 'rate_scale'):
        try:
            info[prop] = str(a.get_editor_property(prop))
        except Exception:
            pass
    try:
        info['skeleton'] = a.get_editor_property('skeleton').get_path_name()
    except Exception:
        pass
    unreal.log('[F11_ANIM] ' + json.dumps(info))
