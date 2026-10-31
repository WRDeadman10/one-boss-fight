# Repositioning proof (lead, Claude): sets reposition_turn_deg_per_second = 180 on MY OWN new proof profile DA_Sevarog_RepositionProof_MOV (the field was added after the asset was created), reads back, saves only that asset.
import unreal
a = unreal.load_asset('/Game/OneBossFight/FrameworkProof/DA_Sevarog_RepositionProof_MOV')
if a is None:
    raise SystemExit('profile missing')
a.set_editor_property('reposition_turn_deg_per_second', 180.0)
if abs(float(a.get_editor_property('reposition_turn_deg_per_second')) - 180.0) > 1e-4 or int(a.get_editor_property('reposition_max')) != 3:
    raise SystemExit('readback mismatch')
if not unreal.EditorAssetLibrary.save_loaded_asset(a):
    raise SystemExit('save failed')
unreal.log('[MOV_TURN] reposition_turn_deg_per_second=180 reposition_max=3 saved')
