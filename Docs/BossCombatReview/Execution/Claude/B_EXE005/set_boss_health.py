# EXE-005 proof (lead, Claude): boss_max_health 250 -> 500 on MY OWN new profile DA_Sevarog_PhaseSupersedes_EXE005 (first run: the posture break and the phase threshold fell on the SAME hit, which proves little).
# With 500 hp, a threshold of 0.5 (250 hp) and 100 damage per hit, hit 1 -> 400, hit 2 -> 300 (posture breaks), hit 3 -> 200 (threshold crossed WHILE staggered). Reads back, saves.
import unreal
a = unreal.load_asset('/Game/OneBossFight/FrameworkProof/DA_Sevarog_PhaseSupersedes_EXE005')
if a is None:
    raise SystemExit('profile missing')
a.set_editor_property('boss_max_health', 500.0)
if abs(float(a.get_editor_property('boss_max_health')) - 500.0) > 1e-4 or abs(float(a.get_editor_property('phase_two_fraction')) - 0.5) > 1e-5 or not a.get_editor_property('phase_supersedes_stagger'):
    raise SystemExit('readback mismatch')
if not unreal.EditorAssetLibrary.save_loaded_asset(a):
    raise SystemExit('save failed')
unreal.log('[EXE005_HEALTH] boss_max_health=500 phase_two_fraction=0.5 phase_supersedes_stagger=True saved')
