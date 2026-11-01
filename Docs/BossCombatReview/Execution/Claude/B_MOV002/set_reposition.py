# MOV-002 proof (lead, Claude): reposition_max 3 + reposition_turn_deg_per_second 180 on MY OWN new profile DA_Sevarog_CenterBias_MOV002.
# After the walk past the target the boss faces away from it: the existing opt-in repositioning (turn + walk) lets it decide again instead of failing with Selector.NoCandidate. Reads back, saves.
import unreal
a = unreal.load_asset('/Game/OneBossFight/FrameworkProof/DA_Sevarog_CenterBias_MOV002')
if a is None:
    raise SystemExit('profile missing')
a.set_editor_property('reposition_max', 3)
a.set_editor_property('reposition_turn_deg_per_second', 180.0)
if int(a.get_editor_property('reposition_max')) != 3 or abs(float(a.get_editor_property('reposition_turn_deg_per_second')) - 180.0) > 1e-4 or abs(float(a.get_editor_property('arena_radius_cm')) - 300.0) > 1e-4:
    raise SystemExit('readback mismatch')
if not unreal.EditorAssetLibrary.save_loaded_asset(a):
    raise SystemExit('save failed')
unreal.log('[MOV002_REPOS] reposition_max=3 turn=180 arena_radius=300 bias=1 saved')
