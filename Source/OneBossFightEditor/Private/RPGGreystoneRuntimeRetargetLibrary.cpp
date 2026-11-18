// Copyright One Boss Fight. All Rights Reserved.
#include "RPGGreystoneRuntimeRetargetLibrary.h"

#include "Animation/AnimBlueprint.h"
#include "Animation/AnimInstance.h"
#include "Animation/Skeleton.h"
#include "AnimationGraph.h"
#include "AnimGraphNode_Root.h"
#include "AnimGraphNode_RetargetPoseFromMesh.h"
#include "AnimNodes/AnimNode_RetargetPoseFromMesh.h"
#include "AssetToolsModule.h"
#include "Kismet2/BlueprintEditorUtils.h"
#include "Engine/BlueprintGeneratedClass.h"
#include "Components/SkeletalMeshComponent.h"
#include "EdGraphSchema_K2.h"
#include "GameFramework/Character.h"
#include "Engine/InheritableComponentHandler.h"
#include "Engine/SCS_Node.h"
#include "Engine/SimpleConstructionScript.h"
#include "Factories/AnimBlueprintFactory.h"
#include "Kismet2/KismetEditorUtilities.h"
#include "Modules/ModuleManager.h"
#include "Retargeter/IKRetargeter.h"
#include "UObject/UnrealType.h"

namespace
{
	// Lead diagnostic (C-1633): UE Python drops out-params when a bool UFUNCTION returns false, so log the token here.
	struct FLogErrorOnExit { const FString& Error; ~FLogErrorOnExit() { if (!Error.IsEmpty()) { UE_LOG(LogTemp, Error, TEXT("[GreystoneRetarget] %s"), *Error); } } };

	const TCHAR* const PlayerPath = TEXT("/Game/OneBossFight/Player/Greystone/BP_GreystoneERPlayer");
	const TCHAR* const AnimBlueprintPath = TEXT("/Game/OneBossFight/Player/Greystone/ABP_Greystone_RuntimeRetarget");
	const TCHAR* const SkeletonPath = TEXT("/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone_Skeleton.Greystone_Skeleton");
	const TCHAR* const MeshPath = TEXT("/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone.Greystone");
	const TCHAR* const RetargeterPath = TEXT("/Game/OneBossFight/GreystonePack/RTG_CombatMannequin_To_Greystone.RTG_CombatMannequin_To_Greystone");
	const TCHAR* const PackPlayerPath = TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.BP_CombatPlayerCharacter");
	const FName VisibleComponentName(TEXT("GreystoneRuntimeVisual"));

	bool GetCanonicalPackMeshAndAnim(USkeletalMesh*& OutMesh, UClass*& OutAnimClass, FString& OutError)
	{
		OutMesh = nullptr;
		OutAnimClass = nullptr;
		UBlueprint* PackPlayerBlueprint = LoadObject<UBlueprint>(nullptr, PackPlayerPath);
		ACharacter* PackPlayerCDO = PackPlayerBlueprint && PackPlayerBlueprint->GeneratedClass
			? Cast<ACharacter>(PackPlayerBlueprint->GeneratedClass->GetDefaultObject()) : nullptr;
		USkeletalMeshComponent* PackMeshComponent = PackPlayerCDO ? PackPlayerCDO->GetMesh() : nullptr;
		OutMesh = PackMeshComponent ? PackMeshComponent->GetSkeletalMeshAsset() : nullptr;
		OutAnimClass = PackMeshComponent ? PackMeshComponent->GetAnimClass() : nullptr;
		// C-1633: the pack player uses SKM_CombatMannequin_Simple; a generated AnimBP class name carries the _C suffix.
		if (!OutMesh || !OutMesh->GetName().StartsWith(TEXT("SKM_CombatMannequin")) || !OutAnimClass || OutAnimClass->GetName() != TEXT("ABP_CombatCharacter_C"))
		{
			OutError = TEXT("GreystoneRetarget.CanonicalPackMannequinOrAnimBPUnavailable");
			return false;
		}
		return true;
	}

	UAnimationGraph* FindAnimGraph(UAnimBlueprint* Blueprint)
	{
		if (!Blueprint) { return nullptr; }
		for (UEdGraph* Graph : Blueprint->FunctionGraphs)
		{
			if (UAnimationGraph* AnimGraph = Cast<UAnimationGraph>(Graph)) { return AnimGraph; }
		}
		return nullptr;
	}

	bool SaveAnimBlueprintGraph(UAnimBlueprint* Blueprint, UIKRetargeter* Retargeter, FString& OutError)
	{
		UAnimationGraph* Graph = FindAnimGraph(Blueprint);
		if (!Graph) { OutError = TEXT("GreystoneRetarget.AnimGraphMissing"); return false; }

		UAnimGraphNode_Root* Root = nullptr;
		UAnimGraphNode_RetargetPoseFromMesh* RetargetNode = nullptr;
		for (UEdGraphNode* Node : Graph->Nodes)
		{
			if (UAnimGraphNode_Root* CandidateRoot = Cast<UAnimGraphNode_Root>(Node))
			{
				if (Root) { OutError = TEXT("GreystoneRetarget.MultipleRootNodes"); return false; }
				Root = CandidateRoot;
			}
			else if (UAnimGraphNode_RetargetPoseFromMesh* Candidate = Cast<UAnimGraphNode_RetargetPoseFromMesh>(Node))
			{
				if (RetargetNode) { OutError = TEXT("GreystoneRetarget.MultipleRetargetNodes"); return false; }
				RetargetNode = Candidate;
			}
			else
			{
				OutError = TEXT("GreystoneRetarget.UnexpectedGraphNode");
				return false;
			}
		}
		if (!Root) { OutError = TEXT("GreystoneRetarget.RootNodeMissing"); return false; }
		if (!RetargetNode)
		{
			RetargetNode = NewObject<UAnimGraphNode_RetargetPoseFromMesh>(Graph, NAME_None, RF_Transactional);
			if (!RetargetNode) { OutError = TEXT("GreystoneRetarget.NodeCreateFailed"); return false; }
			RetargetNode->NodePosX = 0;
			RetargetNode->NodePosY = 0;
			Graph->AddNode(RetargetNode, false, false);
			RetargetNode->CreateNewGuid();
			RetargetNode->PostPlacedNewNode();
			RetargetNode->AllocateDefaultPins();
		}

		FStructProperty* NodeProperty = FindFProperty<FStructProperty>(RetargetNode->GetClass(), TEXT("Node"));
		if (!NodeProperty || NodeProperty->Struct != FAnimNode_RetargetPoseFromMesh::StaticStruct())
		{
			OutError = TEXT("GreystoneRetarget.NodeSettingsReflectionMissing");
			return false;
		}
		FAnimNode_RetargetPoseFromMesh* Settings = NodeProperty->ContainerPtrToValuePtr<FAnimNode_RetargetPoseFromMesh>(RetargetNode);
		Settings->IKRetargeterAsset = Retargeter;
		Settings->bUseAttachedParent = true;
		Settings->SourceMeshComponent.Reset();
		RetargetNode->ReconstructNode();

		UEdGraphPin* RootInput = Root->FindPin(TEXT("Result"));
		UEdGraphPin* PoseOutput = nullptr;
		for (UEdGraphPin* Pin : RetargetNode->Pins)
		{
			if (Pin && Pin->Direction == EGPD_Output && Pin->PinType.PinCategory == UEdGraphSchema_K2::PC_Struct)
			{
				if (PoseOutput) { OutError = TEXT("GreystoneRetarget.MultiplePoseOutputs"); return false; }
				PoseOutput = Pin;
			}
		}
		if (!RootInput || !PoseOutput) { OutError = TEXT("GreystoneRetarget.PosePinsMissing"); return false; }
		for (UEdGraphPin* LinkedPin : RootInput->LinkedTo)
		{
			if (LinkedPin) { LinkedPin->BreakLinkTo(RootInput); }
		}
		const UEdGraphSchema* Schema = Graph->GetSchema();
		if (!Schema || !Schema->TryCreateConnection(PoseOutput, RootInput))
		{
			OutError = TEXT("GreystoneRetarget.PoseConnectionFailed");
			return false;
		}
		Graph->NotifyGraphChanged();
		FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);
		FKismetEditorUtilities::CompileBlueprint(Blueprint);
		if (!Blueprint->GeneratedClass || Blueprint->Status == BS_Error)
		{
			OutError = TEXT("GreystoneRetarget.AnimBlueprintCompileFailed");
			return false;
		}
		return true;
	}

	UAnimBlueprint* CreateOrLoadAnimBlueprint(FString& OutError)
	{
		USkeleton* Skeleton = LoadObject<USkeleton>(nullptr, SkeletonPath);
		USkeletalMesh* Mesh = LoadObject<USkeletalMesh>(nullptr, MeshPath);
		if (!Skeleton || !Mesh || Mesh->GetSkeleton() != Skeleton)
		{
			OutError = TEXT("GreystoneRetarget.TargetMeshOrSkeletonMissingOrMismatched");
			return nullptr;
		}
		if (UAnimBlueprint* Existing = LoadObject<UAnimBlueprint>(nullptr, TEXT("/Game/OneBossFight/Player/Greystone/ABP_Greystone_RuntimeRetarget.ABP_Greystone_RuntimeRetarget")))
		{
			if (Existing->TargetSkeleton != Skeleton)
			{
				OutError = TEXT("GreystoneRetarget.ExistingAnimBPSkeletonMismatch");
				return nullptr;
			}
			return Existing;
		}

		UAnimBlueprintFactory* Factory = NewObject<UAnimBlueprintFactory>();
		Factory->BlueprintType = BPTYPE_Normal;
		Factory->ParentClass = UAnimInstance::StaticClass();
		Factory->TargetSkeleton = Skeleton;
		Factory->PreviewSkeletalMesh = Mesh;
		Factory->bTemplate = false;
		FAssetToolsModule& AssetToolsModule = FModuleManager::LoadModuleChecked<FAssetToolsModule>(TEXT("AssetTools"));
		UAnimBlueprint* Created = Cast<UAnimBlueprint>(AssetToolsModule.Get().CreateAsset(
			TEXT("ABP_Greystone_RuntimeRetarget"), TEXT("/Game/OneBossFight/Player/Greystone"), UAnimBlueprint::StaticClass(), Factory));
		if (!Created) { OutError = TEXT("GreystoneRetarget.AnimBPCreateFailed"); return nullptr; }
		return Created;
	}

	USkeletalMeshComponent* GetSourceOverride(UBlueprint* Blueprint, FString& OutError)
	{
		UClass* GeneratedClass = Blueprint ? Blueprint->GeneratedClass : nullptr;
		ACharacter* CDO = GeneratedClass ? Cast<ACharacter>(GeneratedClass->GetDefaultObject()) : nullptr;
		USkeletalMeshComponent* InheritedMesh = CDO ? CDO->GetMesh() : nullptr;
		if (!InheritedMesh)
		{
			OutError = TEXT("GreystoneRetarget.InheritedCharacterMeshUnavailable");
			return nullptr;
		}
		UBlueprintGeneratedClass* BlueprintClass = Cast<UBlueprintGeneratedClass>(GeneratedClass);
		if (!BlueprintClass) { OutError = TEXT("GreystoneRetarget.PlayerGeneratedClassInvalid"); return nullptr; }
		UInheritableComponentHandler* Handler = BlueprintClass->GetInheritableComponentHandler(true);
		if (!Handler) { OutError = TEXT("GreystoneRetarget.InheritableComponentHandlerMissing"); return nullptr; }
		const FComponentKey Key = Handler->FindKey(InheritedMesh->GetFName());
		if (!Key.IsValid())
		{
			// C-1633 lead fix: CharacterMesh0 is a NATIVE ACharacter default subobject, not a parent-Blueprint SCS node, so the
			// inheritable component handler has no key for it. Native component defaults of a Blueprint live on its CDO
			// subobject; edit that instance (this is what the Blueprint editor's details panel does for inherited native components).
			InheritedMesh->Modify();
			return InheritedMesh;
		}
		USkeletalMeshComponent* Template = Cast<USkeletalMeshComponent>(Handler->GetOverridenComponentTemplate(Key));
		if (!Template) { Template = Cast<USkeletalMeshComponent>(Handler->CreateOverridenComponentTemplate(Key)); }
		if (!Template) { OutError = TEXT("GreystoneRetarget.CharacterMeshOverrideCreateFailed"); return nullptr; }
		return Template;
	}

	FString MakeComponentInventoryRow(const UActorComponent* Component, const USCS_Node* SourceNode)
	{
		const USkeletalMeshComponent* SkeletalComponent = Cast<USkeletalMeshComponent>(Component);
		const FString Parent = SourceNode ? SourceNode->ParentComponentOrVariableName.ToString() : FString();
		const FString Socket = SourceNode ? SourceNode->AttachToName.ToString() : FString();
		const FString RowMeshPath = SkeletalComponent && SkeletalComponent->GetSkeletalMeshAsset()
			? SkeletalComponent->GetSkeletalMeshAsset()->GetPathName() : FString();
		// GetAnimClass() is non-const in UE 5.5; read the AnimClass property directly on the const template.
		const UClass* AnimClass = SkeletalComponent ? SkeletalComponent->AnimClass.Get() : nullptr;
		const FString AnimClassPath = AnimClass ? AnimClass->GetPathName() : FString();
		const FName ComponentName = SourceNode ? SourceNode->GetVariableName()
			: (Component ? Component->GetFName() : NAME_None);
		return FString::Printf(TEXT("%s|%s|%s|%s|%s|%s"),
			*ComponentName.ToString(),
			Component ? *Component->GetClass()->GetPathName() : TEXT("<null>"),
			*Parent, *Socket, *RowMeshPath, *AnimClassPath);
	}
}

bool URPGGreystoneRuntimeRetargetLibrary::PlanGreystoneRuntimeRetarget(FString& OutReport, FString& OutError)
{
	OutReport.Reset();
	OutError.Reset();
	const FLogErrorOnExit ErrorLog{OutError};
	if (!LoadObject<UBlueprint>(nullptr, TEXT("/Game/OneBossFight/Player/Greystone/BP_GreystoneERPlayer.BP_GreystoneERPlayer")))
	{
		OutError = TEXT("GreystoneRetarget.PlayerBlueprintMissing");
		return false;
	}
	if (!LoadObject<UIKRetargeter>(nullptr, RetargeterPath))
	{
		OutError = TEXT("GreystoneRetarget.IKRetargeterMissing");
		return false;
	}
	OutReport = FString::Printf(TEXT("PLAYER=%s ANIMBP=%s SKELETON=%s MESH=%s RETARGETER=%s MODE=DRY_RUN"),
		PlayerPath, AnimBlueprintPath, SkeletonPath, MeshPath, RetargeterPath);
	return true;
}

bool URPGGreystoneRuntimeRetargetLibrary::CreateGreystoneRuntimeRetargetAnimBlueprint(FString& OutAssetPath, FString& OutError)
{
	OutAssetPath.Reset();
	OutError.Reset();
	const FLogErrorOnExit ErrorLog{OutError};
	UIKRetargeter* Retargeter = LoadObject<UIKRetargeter>(nullptr, RetargeterPath);
	if (!Retargeter) { OutError = TEXT("GreystoneRetarget.IKRetargeterMissing"); return false; }
	UAnimBlueprint* Blueprint = CreateOrLoadAnimBlueprint(OutError);
	if (!Blueprint || !SaveAnimBlueprintGraph(Blueprint, Retargeter, OutError)) { return false; }
	OutAssetPath = Blueprint->GetPathName();
	return true;
}

bool URPGGreystoneRuntimeRetargetLibrary::ConfigureGreystonePlayerBlueprint(UBlueprint* PlayerBlueprint, FString& OutReport, FString& OutError)
{
	OutReport.Reset();
	OutError.Reset();
	const FLogErrorOnExit ErrorLog{OutError};
	if (!PlayerBlueprint || PlayerBlueprint->GetOutermost()->GetName() != FString(PlayerPath))
	{
		OutError = TEXT("GreystoneRetarget.PlayerBlueprintOutsideAllowlist");
		return false;
	}
	UAnimBlueprint* AnimBlueprint = LoadObject<UAnimBlueprint>(nullptr, TEXT("/Game/OneBossFight/Player/Greystone/ABP_Greystone_RuntimeRetarget.ABP_Greystone_RuntimeRetarget"));
	USkeletalMesh* GreystoneMesh = LoadObject<USkeletalMesh>(nullptr, MeshPath);
	if (!AnimBlueprint || !GreystoneMesh || AnimBlueprint->TargetSkeleton != GreystoneMesh->GetSkeleton())
	{
		OutError = TEXT("GreystoneRetarget.AnimBPOrMeshUnavailable");
		return false;
	}
	USkeletalMeshComponent* SourceTemplate = GetSourceOverride(PlayerBlueprint, OutError);
	if (!SourceTemplate) { if (OutError.IsEmpty()) { OutError = TEXT("GreystoneRetarget.CharacterMeshTemplateUnavailable"); } return false; }
	USkeletalMesh* PackMesh = nullptr;
	UClass* PackAnimClass = nullptr;
	if (!GetCanonicalPackMeshAndAnim(PackMesh, PackAnimClass, OutError)) { return false; }
	SourceTemplate->Modify();
	SourceTemplate->SetSkeletalMesh(PackMesh);
	SourceTemplate->SetAnimationMode(EAnimationMode::AnimationBlueprint);
	SourceTemplate->SetAnimInstanceClass(PackAnimClass);
	SourceTemplate->SetVisibility(false, false);
	SourceTemplate->SetHiddenInGame(true, false);
	SourceTemplate->VisibilityBasedAnimTickOption = EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
	SourceTemplate->SetComponentTickEnabled(true);

	USimpleConstructionScript* SCS = PlayerBlueprint->SimpleConstructionScript;
	if (!SCS) { OutError = TEXT("GreystoneRetarget.PlayerSCSMissing"); return false; }
	USCS_Node* VisualNode = SCS->FindSCSNode(VisibleComponentName);
	if (!VisualNode)
	{
		VisualNode = SCS->CreateNode(USkeletalMeshComponent::StaticClass(), VisibleComponentName);
		if (!VisualNode) { OutError = TEXT("GreystoneRetarget.VisibleNodeCreateFailed"); return false; }
		SCS->AddNode(VisualNode);
	}
	USkeletalMeshComponent* VisualTemplate = Cast<USkeletalMeshComponent>(VisualNode->ComponentTemplate);
	if (!VisualTemplate) { OutError = TEXT("GreystoneRetarget.VisibleNodeWrongType"); return false; }
	VisualNode->SetParent(SourceTemplate);
	VisualTemplate->Modify();
	VisualTemplate->SetSkeletalMesh(GreystoneMesh);
	VisualTemplate->SetAnimationMode(EAnimationMode::AnimationBlueprint);
	VisualTemplate->SetAnimInstanceClass(AnimBlueprint->GeneratedClass);
	VisualTemplate->SetRelativeTransform(FTransform::Identity);
	VisualTemplate->SetVisibility(true, false);
	VisualTemplate->SetHiddenInGame(false, false);
	VisualTemplate->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	VisualTemplate->SetGenerateOverlapEvents(false);
	VisualTemplate->VisibilityBasedAnimTickOption = EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
	VisualTemplate->PrimaryComponentTick.AddPrerequisite(SourceTemplate, SourceTemplate->PrimaryComponentTick);
	VisualTemplate->CastShadow = SourceTemplate->CastShadow;
	VisualTemplate->bReceivesDecals = SourceTemplate->bReceivesDecals;
	const FString SourceAnimClassName = SourceTemplate->GetAnimClass() ? SourceTemplate->GetAnimClass()->GetName() : FString();
	const FString VisibleTemplatePath = VisualTemplate->GetPathName();

	PlayerBlueprint->Modify();
	FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(PlayerBlueprint);
	FKismetEditorUtilities::CompileBlueprint(PlayerBlueprint);
	if (!PlayerBlueprint->GeneratedClass || PlayerBlueprint->Status == BS_Error)
	{
		OutError = TEXT("GreystoneRetarget.PlayerBlueprintCompileFailed");
		return false;
	}
	OutReport = FString::Printf(TEXT("SOURCE=CharacterMesh0 hidden=1 tick=AlwaysTickPoseAndRefreshBones sourceAnim=%s VISIBLE=%s animBP=%s attachedTo=CharacterMesh0 collision=NoCollision"),
		*SourceAnimClassName, *VisibleTemplatePath, *AnimBlueprint->GetPathName());
	return true;
}

bool URPGGreystoneRuntimeRetargetLibrary::GetGreystonePlayerComponentInventory(UBlueprint* PlayerBlueprint, TArray<FString>& OutRows, FString& OutError)
{
	OutRows.Reset();
	OutError.Reset();
	const FLogErrorOnExit ErrorLog{OutError};
	if (!PlayerBlueprint || PlayerBlueprint->GetOutermost()->GetName() != FString(PlayerPath))
	{
		OutError = TEXT("GreystoneRetarget.PlayerBlueprintOutsideAllowlist");
		return false;
	}
	USimpleConstructionScript* SCS = PlayerBlueprint->SimpleConstructionScript;
	UBlueprintGeneratedClass* BlueprintClass = Cast<UBlueprintGeneratedClass>(PlayerBlueprint->GeneratedClass);
	if (!SCS || !BlueprintClass)
	{
		OutError = TEXT("GreystoneRetarget.ComponentInventoryBlueprintStructureUnavailable");
		return false;
	}

	for (USCS_Node* Node : SCS->GetAllNodes())
	{
		if (!Node || !Node->ComponentTemplate) { continue; }
		OutRows.Add(MakeComponentInventoryRow(Node->ComponentTemplate, Node));
	}

	UInheritableComponentHandler* Handler = BlueprintClass->GetInheritableComponentHandler(false);
	if (Handler)
	{
		for (auto It = Handler->CreateRecordIterator(); It; ++It)
		{
			const FComponentOverrideRecord& Record = *It;
			if (!Record.ComponentTemplate) { continue; }
			const USCS_Node* OriginalNode = Record.ComponentKey.FindSCSNode();
			OutRows.Add(MakeComponentInventoryRow(Record.ComponentTemplate, OriginalNode));
		}
	}
	if (OutRows.IsEmpty())
	{
		OutError = TEXT("GreystoneRetarget.ComponentInventoryEmpty");
		return false;
	}
	return true;
}
