# BOSS-DEF-002 proof (lead, Claude): raises posture_regen_per_second of MY OWN new proof profile to 200 so the regeneration reaches the maximum before the short proof run ends. Edits only DA_Sevarog_RegenProof_DEF002, reads back, saves it.
import unreal
P = '/Game/OneBossFight/FrameworkProof/DA_Sevarog_RegenProof_DEF002'
a = unreal.load_asset(P)
if a is None:
    raise SystemExit('profile missing')
a.set_editor_property('posture_regen_per_second', 200.0)
if abs(float(a.get_editor_property('posture_regen_per_second')) - 200.0) > 1e-4:
    raise SystemExit('readback mismatch')
if not unreal.EditorAssetLibrary.save_loaded_asset(a):
    raise SystemExit('save failed')
unreal.log('[DEF002_RATE] posture_regen_per_second=200 saved')
