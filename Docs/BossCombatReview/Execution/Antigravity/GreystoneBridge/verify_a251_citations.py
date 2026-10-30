#!/usr/bin/env python3
"""
verify_a251_citations.py
========================
Offline verification of engine header file citations in ANIMBP_AUTHORING_OPTIONS.md (A-251).
"""

import sys
from pathlib import Path

ENGINE_ROOT = Path(r"C:\Program Files\Epic Games\UE_5.5\Engine")

CITED_HEADERS = [
    (ENGINE_ROOT / "Source/Editor/UnrealEd/Classes/Factories/AnimBlueprintFactory.h", 17, "class UAnimBlueprintFactory"),
    (ENGINE_ROOT / "Source/Editor/UnrealEd/Classes/Factories/AnimBlueprintFactory.h", 27, "TSubclassOf<class UAnimInstance> ParentClass;"),
    (ENGINE_ROOT / "Source/Editor/UnrealEd/Classes/Factories/AnimBlueprintFactory.h", 31, "TObjectPtr<class USkeleton> TargetSkeleton;"),
    (ENGINE_ROOT / "Source/Editor/AnimGraph/Public/AnimationGraph.h", 18, "class ANIMGRAPH_API UAnimationGraph"),
    (ENGINE_ROOT / "Source/Editor/AnimGraph/Public/AnimationGraph.h", 31, "void GetGraphNodesOfClass"),
    (ENGINE_ROOT / "Source/Runtime/Engine/Classes/EdGraph/EdGraph.h", 1, "Copyright Epic Games, Inc."),
    (ENGINE_ROOT / "Source/Editor/BlueprintEditorLibrary/Public/BlueprintEditorLibrary.h", 82, "static void CompileBlueprint"),
    (ENGINE_ROOT / "Source/Editor/AnimationBlueprintLibrary/Public/AnimationBlueprintLibrary.h", 603, "static void GetAnimationGraphs"),
    (ENGINE_ROOT / "Source/Editor/AnimationBlueprintLibrary/Public/AnimationBlueprintLibrary.h", 607, "static void GetNodesOfClass"),
    (ENGINE_ROOT / "Source/Editor/AnimationBlueprintLibrary/Public/AnimationBlueprintLibrary.h", 618, "static void AddNodeAssetOverride"),
    (ENGINE_ROOT / "Plugins/Animation/IKRig/Source/IKRigDeveloper/Public/AnimGraphNode_RetargetPoseFromMesh.h", 16, "class IKRIGDEVELOPER_API UAnimGraphNode_RetargetPoseFromMesh"),
    (ENGINE_ROOT / "Plugins/Animation/IKRig/Source/IKRigDeveloper/Public/AnimGraphNode_RetargetPoseFromMesh.h", 21, "FAnimNode_RetargetPoseFromMesh Node;"),
    (ENGINE_ROOT / "Source/Runtime/Engine/Classes/Components/SkinnedMeshComponent.h", 1694, "SetLeaderPoseComponent"),
    (ENGINE_ROOT / "Source/Runtime/Engine/Private/Components/SkinnedMeshComponent.cpp", 2974, "const FName BoneName = FollowerRefSkeleton.GetBoneName"),
    (ENGINE_ROOT / "Source/Runtime/Engine/Public/Animation/AnimInstanceProxy.h", 644, "virtual bool Evaluate(FPoseContext& Output)"),
]

def main():
    print("================================================================================")
    print(" VERIFYING A-251 ANIMBP AUTHORING OPTIONS CITATIONS")
    print("================================================================================")

    doc_path = Path("Docs/BossCombatReview/Execution/Antigravity/GreystoneBridge/ANIMBP_AUTHORING_OPTIONS.md")
    assert doc_path.is_file(), f"Missing doc file: {doc_path}"

    raw = doc_path.read_bytes()
    assert b"\r\r\n" not in raw, "No double CRLF"
    assert b"\n" in raw, "Must have newlines"
    print(f"[OK] ANIMBP_AUTHORING_OPTIONS.md raw bytes: {len(raw):,} bytes, clean CRLF")

    for path, line_no, token in CITED_HEADERS:
        assert path.is_file(), f"Engine source missing: {path}"
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        assert line_no <= len(lines), f"Line {line_no} out of range in {path}"
        line_text = lines[line_no - 1]
        assert token in line_text, f"Token '{token}' not found on line {line_no} of {path.name} (found: '{line_text.strip()}')"
        print(f"[OK] Citation {path.name}:{line_no} verified: '{token}'")

    print("\n================================================================================")
    print(f" ALL {len(CITED_HEADERS)} ENGINE CITATIONS 100% VERIFIED OFFLINE")
    print("================================================================================")

if __name__ == "__main__":
    main()
