# SEL-008 (lead, Claude): in-place edit of the NEW profile: reposition_max 0 and turn rate 0, so the old turn-in-place branch (which idles through a cooldown even when the boss already faces the target) does not preempt the neutral strafe.
import unreal
p = unreal.load_asset('/Game/OneBossFight/FrameworkProof/DA_Sevarog_NeutralStrafe_SEL008')
p.set_editor_property('reposition_max', 0)
p.set_editor_property('reposition_turn_deg_per_second', 0.0)
assert int(p.get_editor_property('reposition_max')) == 0 and float(p.get_editor_property('reposition_turn_deg_per_second')) == 0.0
assert float(p.get_editor_property('neutral_strafe_seconds')) == 8.0
assert unreal.EditorAssetLibrary.save_loaded_asset(p)
unreal.log('[SEL008_FIX] reposition_max=0 turn=0 neutral_strafe_seconds=8')
