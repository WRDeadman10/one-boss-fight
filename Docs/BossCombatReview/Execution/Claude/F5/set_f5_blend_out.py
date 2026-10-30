# F5 amendment (lead, Claude): BlendOutSeconds 0.04 -> 0.03 on the F5 proof profile: Swing2_Medium clip 1.1333 s, card recovery 1.10 s, so RecoveryEnd + BlendOut must be <= 1.1333 (0.04 gave 1.14: Framework.Profile.CardBandOrBlendTail).
import json
import unreal

PATH = '/Game/OneBossFight/FrameworkProof/DA_Sevarog_SelectorProof_F5'
prof = unreal.load_asset(PATH)
if prof is None:
    raise SystemExit('profile missing')
before = prof.get_editor_property('blend_out_seconds')
prof.set_editor_property('blend_out_seconds', 0.03)
after = prof.get_editor_property('blend_out_seconds')
ok = unreal.EditorAssetLibrary.save_loaded_asset(prof)
unreal.log('[F5C_AMEND] ' + json.dumps({'before': before, 'after': after, 'saved': ok}))
if abs(after - 0.03) > 1e-6 or not ok:
    raise SystemExit('amend failed')
