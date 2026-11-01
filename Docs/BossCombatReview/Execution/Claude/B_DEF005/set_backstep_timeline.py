# DEF-005 proof (lead, Claude): timeline of MY OWN new card Move_Sevarog_BackStep_DEF005. The first run showed that the Run_Bwd clip has its own rate scale 1.25, so its montage is 1.28 s long, not 1.6: the card (recovery end 1.45) stopped early.
# New timeline (design values, proposed), play rate 0.8 so the montage runs 1.6 s real: commit 0.10, the move starts at 0.30 (0.375 real seconds of telegraph), ends at 0.60, recovery ends at 1.20 (0.75 real seconds after the move). Reads back, saves.
import unreal
a = unreal.load_asset('/Game/OneBossFight/FrameworkProof/Cards/Move_Sevarog_BackStep_DEF005')
if a is None:
    raise SystemExit('card missing')
s = a.get_editor_property('spec')
for k, v in (('play_rate', 0.8), ('commit_seconds', 0.10), ('active_start_seconds', 0.30), ('active_end_seconds', 0.60), ('recovery_end_seconds', 1.20), ('warp_start_seconds', 0.30), ('warp_end_seconds', 0.60)):
    s.set_editor_property(k, v)
a.set_editor_property('spec', s)
b = a.get_editor_property('spec')
for k, v in (('play_rate', 0.8), ('recovery_end_seconds', 1.20), ('warp_end_seconds', 0.60)):
    if abs(float(b.get_editor_property(k)) - v) > 1e-4:
        raise SystemExit('readback mismatch ' + k)
if not unreal.EditorAssetLibrary.save_loaded_asset(a):
    raise SystemExit('save failed')
unreal.log('[DEF005_TIMELINE] play_rate 0.8 commit 0.1 move 0.3..0.6 recovery_end 1.2 saved')
