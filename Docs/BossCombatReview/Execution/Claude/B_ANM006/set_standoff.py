# ANM-006 proof (lead, Claude): standoff on MY OWN new card Move_Sevarog_HeavyWarp_ANM006. The first run showed that 80 cm is inside the touching distance of the two capsules (60 + 42 = 102 cm), so the swept warp was blocked there: the standoff becomes 105 cm (reachable). Reads back, saves.
import unreal
a = unreal.load_asset('/Game/OneBossFight/FrameworkProof/Cards/Move_Sevarog_HeavyWarp_ANM006')
if a is None:
    raise SystemExit('card missing')
spec = a.get_editor_property('spec')
spec.set_editor_property('warp_standoff_cm', 105.0)
a.set_editor_property('spec', spec)
if abs(float(a.get_editor_property('spec').get_editor_property('warp_standoff_cm')) - 105.0) > 1e-4:
    raise SystemExit('readback mismatch')
if not unreal.EditorAssetLibrary.save_loaded_asset(a):
    raise SystemExit('save failed')
unreal.log('[ANM006_STANDOFF] 105 saved')
