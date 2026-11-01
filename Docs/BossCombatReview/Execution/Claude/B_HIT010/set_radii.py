# HIT-010 proof (lead, Claude): radii on MY OWN new card Move_Sevarog_HeavySplash_HIT010 (the first run showed that the original direct blade radius never reaches the target at this range, so only the splash window hit):
# direct window radius x2 and splash window radius x3 of the original, so BOTH windows touch the target in the same tick. Reads back, saves.
import unreal
a = unreal.load_asset('/Game/OneBossFight/FrameworkProof/Cards/Move_Sevarog_HeavySplash_HIT010')
if a is None:
    raise SystemExit('card missing')
spec = a.get_editor_property('spec')
ws = list(spec.get_editor_property('windows'))
if len(ws) != 2 or not ws[0].get_editor_property('secondary') or ws[1].get_editor_property('secondary'):
    raise SystemExit('unexpected windows')
r_splash_old = float(ws[0].get_editor_property('radius_cm'))   # 2x the original
r0 = r_splash_old / 2.0
ws[1].set_editor_property('radius_cm', r0 * 2.0)
ws[0].set_editor_property('radius_cm', r0 * 3.0)
spec.set_editor_property('windows', ws)
a.set_editor_property('spec', spec)
back = list(a.get_editor_property('spec').get_editor_property('windows'))
if abs(float(back[1].get_editor_property('radius_cm')) - r0 * 2.0) > 1e-4 or abs(float(back[0].get_editor_property('radius_cm')) - r0 * 3.0) > 1e-4:
    raise SystemExit('readback mismatch')
if not unreal.EditorAssetLibrary.save_loaded_asset(a):
    raise SystemExit('save failed')
unreal.log('[HIT010_RADII] original=%g direct=%g splash=%g saved' % (r0, r0 * 2.0, r0 * 3.0))
