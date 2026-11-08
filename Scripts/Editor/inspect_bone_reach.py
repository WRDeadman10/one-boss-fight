"""
Inspects bone travel for hand_r on PrimaryB animation sequence
across the strike window 0.20 to 1.067 s.
"""

import unreal

AL = unreal.AnimationLibrary

def test_reach():
    anim_path = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/Attack_PrimaryB_Anim"
    anim = unreal.load_asset(anim_path)
    if not anim:
        unreal.log(f"Cannot load {anim_path}")
        return
        
    num_frames = AL.get_num_frames(anim)
    length = anim.get_play_length()
    unreal.log(f"Loaded {anim.get_name()}, length={length:.4f}s, frames={num_frames}")
    
    # Sample times from 0.0 to 1.4 at 0.05s steps
    bone_name = "hand_r"
    root_name = "root"
    pelvis_name = "pelvis"
    
    samples = []
    t = 0.0
    while t <= length:
        try:
            pose = AL.get_bone_pose_for_time(anim, bone_name, t, True)
            loc = pose.translation
            samples.append((t, loc.x, loc.y, loc.z))
            unreal.log(f"t={t:.3f}s: {bone_name} loc=({loc.x:.1f}, {loc.y:.1f}, {loc.z:.1f})")
        except Exception as e:
            unreal.log(f"Error at t={t:.3f}s: {e}")
            break
        t += 0.05

if __name__ == "__main__":
    test_reach()
    unreal.SystemLibrary.quit_editor()
