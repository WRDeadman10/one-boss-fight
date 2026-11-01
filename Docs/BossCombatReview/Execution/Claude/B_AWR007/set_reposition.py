# AWR-007 proof (lead, Claude): reposition_max 3 + reposition_turn_deg_per_second 180 on MY OWN new profile DA_Sevarog_LosSearch_AWR007C.
# After the search walk the boss faces away from the target: the existing opt-in repositioning (turn + walk) lets it decide again instead of failing with Selector.NoCandidate. Reads back, saves.
import unreal
a = unreal.load_asset('/Game/OneBossFight/FrameworkProof/DA_Sevarog_LosSearch_AWR007C')
if a is None:
    raise SystemExit('profile missing')
a.set_editor_property('reposition_max', 3)
a.set_editor_property('reposition_turn_deg_per_second', 180.0)
if int(a.get_editor_property('reposition_max')) != 3 or abs(float(a.get_editor_property('reposition_turn_deg_per_second')) - 180.0) > 1e-4:
    raise SystemExit('readback mismatch')
if not unreal.EditorAssetLibrary.save_loaded_asset(a):
    raise SystemExit('save failed')
unreal.log('[AWR007_REPOS] reposition_max=3 turn=180 saved')
