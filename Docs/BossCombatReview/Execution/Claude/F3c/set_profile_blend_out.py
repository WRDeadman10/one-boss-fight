# F3c amendment 2 (lead, Claude): BlendOutSeconds 0.10 -> 0.04. The live resolver requires RecoveryEnd (1.65) + BlendOut <= clip length (1.70): 1.75 failed (F3d run3, token Framework.Profile.CardBandOrBlendTail).
import json
import unreal

PATH = '/Game/OneBossFight/FrameworkProof/DA_Sevarog_SwingProof'
prof = unreal.load_asset(PATH)
if prof is None:
    raise SystemExit('profile missing')
before = prof.get_editor_property('blend_out_seconds')
prof.set_editor_property('blend_out_seconds', 0.04)
after = prof.get_editor_property('blend_out_seconds')
ok = unreal.EditorAssetLibrary.save_loaded_asset(prof)
unreal.log('[F3C_AMEND2] ' + json.dumps({'before': before, 'after': after, 'saved': ok}))
if abs(after - 0.04) > 1e-6 or not ok:
    raise SystemExit('amend failed')
