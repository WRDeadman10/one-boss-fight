"""Poses the level's boss mesh with an imported clip at a time (editor world, no PIE). Reads Saved/pose.txt: "<clip asset name> <seconds>". Log prefix [Pose]."""
import unreal
clip, t = open(unreal.SystemLibrary.get_project_directory() + "Saved/pose.txt").read().split()
sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
boss = next(a for a in sub.get_all_level_actors() if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C")
mesh = boss.get_components_by_class(unreal.SkeletalMeshComponent)[0]
anim = unreal.load_asset("/Game/OneBossFight/Boss01/Animations/" + clip)
mesh.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
mesh.play_animation(anim, False)
mesh.set_position(float(t), False)
mesh.set_play_rate(0.0)
mesh.tick_animation(0.0, False)
mesh.refresh_bone_transforms()
unreal.log("[Pose] %s at %s s, boss at %s" % (clip, t, boss.get_actor_location()))
