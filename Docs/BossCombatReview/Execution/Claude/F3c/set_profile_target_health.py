# F3c amendment (lead, Claude): sets TargetHealth on the profile this release created (uncommitted, referenced only by the proof map). 800 = Hero V3 manifest Stats.MaxHealth.
import json
import unreal

PATH = '/Game/OneBossFight/FrameworkProof/DA_Sevarog_SwingProof'
prof = unreal.load_asset(PATH)
if prof is None:
    raise SystemExit('profile missing')
before = prof.get_editor_property('target_health')
prof.set_editor_property('target_health', 800.0)
after = prof.get_editor_property('target_health')
ok = unreal.EditorAssetLibrary.save_loaded_asset(prof)
unreal.log('[F3C_AMEND] ' + json.dumps({'before': before, 'after': after, 'saved': ok}))
if after != 800.0 or not ok:
    raise SystemExit('amend failed')
