"""
Verification script for GREYSTONE_VISUAL_BRIDGE_DESIGN.md (A-241).
Verifies that all documentation citations, engine source file:line references,
and asset targets on disk exist and match expected lines.
"""
import os
import sys

def verify_file_line(path, line_num, expected_token):
    if not os.path.isfile(path):
        print(f"FAILED: File not found: {path}")
        return False
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    if line_num > len(lines):
        print(f"FAILED: Line {line_num} out of range in {path} (total {len(lines)})")
        return False
    actual_line = lines[line_num - 1]
    if expected_token not in actual_line:
        print(f"FAILED: Expected '{expected_token}' in {path}:{line_num}, found: {actual_line.strip()[:80]}")
        return False
    print(f"VERIFIED: {path}:{line_num} -> {actual_line.strip()[:70]}")
    return True

def verify_asset(path):
    if not os.path.isfile(path):
        print(f"FAILED: Asset not found: {path}")
        return False
    size = os.path.getsize(path)
    print(f"VERIFIED ASSET: {path} ({size:,} bytes)")
    return True

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.."))
    engine_root = "C:/Program Files/Epic Games/UE_5.5/Engine"
    
    citations = [
        (os.path.join(repo_root, "Documentation/DECISIONS.md"), 294, "Revert the 60 pack assets"),
        (os.path.join(repo_root, "Documentation/KNOWN_ISSUES.md"), 44, "KI-040"),
        (os.path.join(repo_root, "Documentation/KNOWN_ISSUES.md"), 55, "KI-052"),
        (os.path.join(engine_root, "Plugins/Animation/IKRig/Source/IKRig/Public/AnimNodes/AnimNode_RetargetPoseFromMesh.h"), 17, "struct IKRIG_API FAnimNode_RetargetPoseFromMesh"),
        (os.path.join(engine_root, "Plugins/Animation/IKRig/Source/IKRigDeveloper/Public/AnimGraphNode_RetargetPoseFromMesh.h"), 16, "class IKRIGDEVELOPER_API UAnimGraphNode_RetargetPoseFromMesh"),
        (os.path.join(engine_root, "Source/Runtime/Engine/Classes/Components/ActorComponent.h"), 1139, "AddTickPrerequisiteComponent"),
        (os.path.join(engine_root, "Source/Runtime/Engine/Classes/Components/SkinnedMeshComponent.h"), 87, "AlwaysTickPoseAndRefreshBones"),
    ]
    
    assets = [
        os.path.join(repo_root, "Content/OneBossFight/GreystonePack/RTG_CombatMannequin_To_Greystone.uasset"),
        os.path.join(repo_root, "Content/OneBossFight/GreystonePack/IK_CombatMannequin.uasset"),
        os.path.join(repo_root, "Content/OneBossFight/Characters/Greystone/IK_Greystone.uasset"),
        os.path.join(repo_root, "Content/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin.uasset"),
        os.path.join(repo_root, "Content/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone_Skeleton.uasset"),
        os.path.join(repo_root, "Content/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone.uasset"),
        os.path.join(repo_root, "Content/OneBossFight/GreystonePack/M_GreyHiddenSlot.uasset"),
    ]
    
    all_ok = True
    print("--- Verifying File & Line Citations ---")
    for path, line_num, token in citations:
        if not verify_file_line(path, line_num, token):
            all_ok = False
            
    print("\n--- Verifying On-Disk Asset Targets ---")
    for asset in assets:
        if not verify_asset(asset):
            all_ok = False
            
    if not all_ok:
        print("\nVERIFICATION FAILED")
        sys.exit(1)
        
    print("\nALL CITATIONS & ASSET TARGETS 100% VERIFIED AGAINST DISK.")

if __name__ == "__main__":
    main()
