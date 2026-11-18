# C-1621 Greystone runtime-retarget feasibility (2026-11-13)

## Finding

UE 5.5.4 contains the exact editor graph node `UAnimGraphNode_RetargetPoseFromMesh` in the IKRigDeveloper editor module, backed by runtime `FAnimNode_RetargetPoseFromMesh` in IKRig. The runtime node exposes `SourceMeshComponent`, `bUseAttachedParent` (defaults true), `IKRetargeterAsset`, and retarget profile settings. The editor node's `Node` property is private, so an asset author cannot safely populate it by direct property assignment.

The Anim Blueprint factory exists as `UAnimBlueprintFactory`, with reflected `ParentClass`, `TargetSkeleton`, and `PreviewSkeletalMesh` properties; Python factory-based asset creation is therefore a plausible option if the class is exposed in the installed Python build. The local source confirms no supported Python route for constructing and wiring AnimGraph nodes. Python may create the shell asset, but graph editing/recompilation should be implemented through an Editor C++ helper using `UAnimGraph`, `FBlueprintEditorUtils`, and the IKRigDeveloper node class. Treat Python-only graph generation as unproven; do not attempt it in the authored project.

Relevant engine source:

- `Engine/Source/Editor/UnrealEd/Classes/Factories/AnimBlueprintFactory.h`
- `Engine/Plugins/Animation/IKRig/Source/IKRig/Public/AnimNodes/AnimNode_RetargetPoseFromMesh.h`
- `Engine/Plugins/Animation/IKRig/Source/IKRigDeveloper/Public/AnimGraphNode_RetargetPoseFromMesh.h`
- `IKRigDeveloper.Build.cs` depends on `UnrealEd`, `AnimGraph`, `BlueprintGraph`, and Persona only for editor targets.

## Proposed implementation plan (not implemented)

1. Keep the mannequin skeletal mesh component on the Greystone player as the source. Keep its existing pack AnimBP and layer classes so the `GetMainAnimBP` cast succeeds. Hide it from rendering, set `VisibilityBasedAnimTickOption=AlwaysTickPoseAndRefreshBones`, and keep it ticking before the visible target mesh.
2. Add the Greystone skeletal mesh as a visible component at the same root-relative transform. Use the existing mannequin-to-Greystone IK Retargeter and a minimal Greystone-targeted AnimBP with one `Retarget Pose From Mesh` node. Prefer attached-parent sourcing if the visible component is directly attached to the hidden mannequin mesh; otherwise expose and bind `SourceMeshComponent` explicitly.
3. Build the minimal graph in a new editor-module authoring helper. Add editor-only dependencies `AnimGraph`, `BlueprintGraph`, and `IKRigDeveloper` to `OneBossFightEditor`; keep runtime modules free of editor node types. Create or update assets in place and preserve references. Compile, save, reopen, and verify target skeleton/retargeter/source binding.
4. Audit component consumers before swapping visuals: weapon/socket attachments, lock-on target, hit reactions, death/stagger montages, cloth, visibility, shadow, and collision. Keep collision and gameplay authority on the existing capsule/source component; ensure weapon visuals attach to the visible retargeted mesh where required.
5. Under a separate Claude-approved C-1155 runner, verify one normal play run: zero `GetMainAnimBP` failures, hidden source still updates, Greystone visible mesh follows source pose, forward roll capsule travel 248–334 cm and backstep about 100 cm, weapon/socket alignment, no duplicate shadows, and no gameplay/collision regression. No map save is part of this plan.

This is a read-only feasibility note. It creates no AnimBP, component, map or other asset and does not authorize an Editor launch.
