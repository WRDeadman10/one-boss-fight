# QA-003 tie proof (lead, Claude): attack_count 3 -> 8 on MY OWN new profile DA_Sevarog_TieProof_QA003 (three decisions all picked the same card by chance; eight make the seeded pick visible). Reads back, saves.
import unreal
a = unreal.load_asset('/Game/OneBossFight/FrameworkProof/DA_Sevarog_TieProof_QA003')
if a is None:
    raise SystemExit('profile missing')
a.set_editor_property('attack_count', 8)
if int(a.get_editor_property('attack_count')) != 8 or abs(float(a.get_editor_property('selector_tie_band')) - 0.35) > 1e-5 or int(a.get_editor_property('selector_tie_seed')) != 11:
    raise SystemExit('readback mismatch')
if not unreal.EditorAssetLibrary.save_loaded_asset(a):
    raise SystemExit('save failed')
unreal.log('[QA003_ATTACKS] attack_count=8 tie_band=0.35 tie_seed=11 saved')
