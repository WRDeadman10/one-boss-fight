# F6 amendment (lead, Claude): proof band 150..180 -> 140..160 on the F5 and F6 proof profiles (KI-147: the second card sat at the far end of the band).
# Measured now: pack player capsule radius 42.0 / half height 96.0 (Claude/F6/player_probe_run1); AntiGreed reach 138 + blade 15 + target 42 = 195 from the boss root.
import json
import unreal

for name in ('DA_Sevarog_SelectorProof_F5', 'DA_Sevarog_BossHealthProof_F6'):
    path = '/Game/OneBossFight/FrameworkProof/' + name
    prof = unreal.load_asset(path)
    if prof is None:
        raise SystemExit('profile missing: ' + path)
    before = (prof.get_editor_property('band_min_cm'), prof.get_editor_property('band_max_cm'))
    prof.set_editor_property('band_min_cm', 140.0)
    prof.set_editor_property('band_max_cm', 160.0)
    after = (prof.get_editor_property('band_min_cm'), prof.get_editor_property('band_max_cm'))
    ok = unreal.EditorAssetLibrary.save_loaded_asset(prof)
    unreal.log('[F6C_BAND] ' + json.dumps({'asset': name, 'before': before, 'after': after, 'saved': ok}))
    if after != (140.0, 160.0) or not ok:
        raise SystemExit('amend failed: ' + name)
