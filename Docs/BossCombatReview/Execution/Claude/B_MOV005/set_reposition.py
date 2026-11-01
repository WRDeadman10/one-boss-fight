# MOV-005 proof (lead, Claude): reposition_max 3 + reposition_turn_deg_per_second 180 on MY OWN new profile DA_Sevarog_ArenaLeash_MOV005.
# After the leash the boss faces away from the returning target: the existing opt-in repositioning (turn + walk) lets it decide again instead of failing with Selector.NoCandidate. Reads back, saves.
import unreal
a = unreal.load_asset('/Game/OneBossFight/FrameworkProof/DA_Sevarog_ArenaLeash_MOV005')
if a is None:
    raise SystemExit('profile missing')
a.set_editor_property('reposition_max', 3)
a.set_editor_property('reposition_turn_deg_per_second', 180.0)
if int(a.get_editor_property('reposition_max')) != 3 or abs(float(a.get_editor_property('reposition_turn_deg_per_second')) - 180.0) > 1e-4 or not a.get_editor_property('arena_leash') or abs(float(a.get_editor_property('arena_radius_cm')) - 250.0) > 1e-4:
    raise SystemExit('readback mismatch')
if not unreal.EditorAssetLibrary.save_loaded_asset(a):
    raise SystemExit('save failed')
unreal.log('[MOV005_REPOS] reposition_max=3 turn=180 arena_radius=250 arena_leash=True saved')
