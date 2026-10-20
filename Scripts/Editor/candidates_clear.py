"""Removes the CandTest actors again. Log prefix [Cand]."""
import unreal

sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
n = 0
for a in sub.get_all_level_actors():
    if a.get_folder_path() == "CandTest":
        sub.destroy_actor(a)
        n += 1
unreal.log("[Cand] removed %d" % n)
