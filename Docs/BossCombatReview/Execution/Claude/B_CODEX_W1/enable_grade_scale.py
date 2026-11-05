# W1 proof (lead, Claude): in-place edit of the NEW parry reaction profile: grade scaling on (b_parry_grade_scale True). Nothing else changes.
import unreal
p = unreal.load_asset('/Game/OneBossFight/FrameworkProof/DA_Sevarog_ParryReaction_PARRY')
p.set_editor_property('parry_grade_scale', True)
assert p.get_editor_property('parry_grade_scale') is True
assert unreal.EditorAssetLibrary.save_loaded_asset(p)
unreal.log('[W1_FIX] parry grade scale on; parry posture %s' % p.get_editor_property('parry_posture_amount'))
