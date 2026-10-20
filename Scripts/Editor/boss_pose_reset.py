"""Puts the level boss's mesh back to Animation Blueprint mode after boss_pose.py, and removes the failed SK_Boss01_Body import (nothing references it). Log prefix [Pose]."""
import unreal
sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
boss = next(a for a in sub.get_all_level_actors() if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C")
mesh = boss.get_components_by_class(unreal.SkeletalMeshComponent)[0]
mesh.set_animation_mode(unreal.AnimationMode.ANIMATION_BLUEPRINT)
mesh.set_play_rate(1.0)
unreal.log("[Pose] boss mesh mode %s, anim class %s" % (mesh.get_editor_property("animation_mode"), mesh.get_editor_property("anim_class")))
p = "/Game/OneBossFight/Boss01/Body/SK_Boss01_Body"
if unreal.EditorAssetLibrary.does_asset_exist(p):
    unreal.log("[Pose] deleted failed import: %s" % unreal.EditorAssetLibrary.delete_asset(p))
