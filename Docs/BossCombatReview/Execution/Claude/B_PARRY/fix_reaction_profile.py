# PARRY reaction (lead, Claude): Framework.Profile.PhaseCooldownStarvation with attack_count 4; back to the F8 value 2 (in place, new profile only).
import unreal
p = unreal.load_asset('/Game/OneBossFight/FrameworkProof/DA_Sevarog_ParryReaction_PARRY')
p.set_editor_property('attack_count', 2)
assert int(p.get_editor_property('attack_count')) == 2 and float(p.get_editor_property('parry_posture_amount')) == 100.0
assert unreal.EditorAssetLibrary.save_loaded_asset(p)
unreal.log('[PARRY_RX3] attack_count=2 parry_posture_amount=100')
