// Copyright One Boss Fight. All Rights Reserved.

#include "Boss/RPGBossStateTree.h"
#include "OneBossFight.h"
#include "StateTree.h"
#include "StateTreeExecutionContext.h"
#include "StateTreeReference.h"

#if WITH_EDITOR
#include "AssetRegistry/AssetRegistryModule.h"
#include "Components/StateTreeComponentSchema.h"
#include "StateTreeCompiler.h"
#include "StateTreeCompilerLog.h"
#include "StateTreeEditingSubsystem.h"
#include "StateTreeEditorData.h"
#include "StateTreeState.h"
#include "UObject/Package.h"
#endif

namespace
{
	URPGBossCombatComponent* FindBossComponent(const FStateTreeExecutionContext& Context)
	{
		UObject* Owner = Context.GetOwner();
		AActor* Actor = Cast<AActor>(Owner);
		if (!Actor)
		{
			if (const UActorComponent* Component = Cast<UActorComponent>(Owner))
			{
				Actor = Component->GetOwner();
			}
		}
		return Actor ? Actor->FindComponentByClass<URPGBossCombatComponent>() : nullptr;
	}
}

bool FRPGBossStateCondition::TestCondition(FStateTreeExecutionContext& Context) const
{
	const FInstanceDataType& Data = Context.GetInstanceData(*this);
	const URPGBossCombatComponent* Boss = FindBossComponent(Context);
	return Boss && Boss->GetBossState() == Data.ExpectedState;
}

EStateTreeRunStatus FRPGBossMirrorTask::EnterState(FStateTreeExecutionContext& Context, const FStateTreeTransitionResult& Transition) const
{
	const FInstanceDataType& Data = Context.GetInstanceData(*this);
	if (URPGBossCombatComponent* Boss = FindBossComponent(Context))
	{
		Boss->NotifyStateTreeEntered(Data.MirroredState);
	}
	// Stay running: the state ends only through the component-driven transitions.
	return EStateTreeRunStatus::Running;
}

// -------------------------------------------------------------------------------------------------
// Component
// -------------------------------------------------------------------------------------------------

URPGBossStateTreeComponent::URPGBossStateTreeComponent(const FObjectInitializer& ObjectInitializer)
	: Super(ObjectInitializer)
{
}

void URPGBossStateTreeComponent::InitializeComponent()
{
	if (BossStateTree)
	{
		StateTreeRef.SetStateTree(BossStateTree);
	}
	Super::InitializeComponent();
}

void URPGBossStateTreeComponent::SetStateTreeAsset(UStateTree* NewStateTree)
{
	BossStateTree = NewStateTree;
	StateTreeRef.SetStateTree(NewStateTree);
}

// -------------------------------------------------------------------------------------------------
// Authoring
// -------------------------------------------------------------------------------------------------

UStateTree* URPGBossStateTreeBuilder::BuildBossStateTree(const FString& PackagePath, const FString& AssetName)
{
#if WITH_EDITOR
	const FString PackageName = PackagePath / AssetName;
	UPackage* Package = CreatePackage(*PackageName);
	if (!Package)
	{
		return nullptr;
	}

	UStateTree* StateTree = FindObject<UStateTree>(Package, *AssetName);
	if (!StateTree)
	{
		StateTree = NewObject<UStateTree>(Package, UStateTree::StaticClass(), *AssetName, RF_Public | RF_Standalone | RF_Transactional);
		FAssetRegistryModule::AssetCreated(StateTree);
	}

	UStateTreeEditorData* EditorData = NewObject<UStateTreeEditorData>(StateTree, FName(), RF_Transactional);
	EditorData->Schema = NewObject<UStateTreeComponentSchema>(EditorData);
	StateTree->EditorData = EditorData;

	UStateTreeState& Root = EditorData->AddRootState();

	struct FBossStateDef { ERPGBossState State; const TCHAR* Name; };
	const FBossStateDef Defs[] = {
		{ERPGBossState::Dormant, TEXT("Dormant")},
		{ERPGBossState::Entrance, TEXT("Entrance")},
		{ERPGBossState::Combat, TEXT("Combat")},
		{ERPGBossState::PhaseTransition, TEXT("PhaseTransition")},
		{ERPGBossState::Dead, TEXT("Dead")},
	};

	// States first, so transitions can point at any of them.
	TArray<UStateTreeState*> States;
	for (const FBossStateDef& Def : Defs)
	{
		UStateTreeState& State = Root.AddChildState(FName(Def.Name));
		State.AddEnterCondition<FRPGBossStateCondition>().GetInstanceData().ExpectedState = Def.State;
		State.AddTask<FRPGBossMirrorTask>().GetInstanceData().MirroredState = Def.State;
		States.Add(&State);
	}

	// From every state, follow the boss component to any other state.
	for (int32 From = 0; From < States.Num(); ++From)
	{
		for (int32 To = 0; To < States.Num(); ++To)
		{
			if (From == To)
			{
				continue;
			}
			FStateTreeTransition& Transition = States[From]->AddTransition(
				EStateTreeTransitionTrigger::OnTick, EStateTreeTransitionType::GotoState, States[To]);
			Transition.AddCondition<FRPGBossStateCondition>().GetInstanceData().ExpectedState = Defs[To].State;
		}
	}

	FStateTreeCompilerLog Log;
	const bool bCompiled = UStateTreeEditingSubsystem::CompileStateTree(StateTree, Log);
	if (!bCompiled)
	{
		UE_LOG(LogOneBossFight, Error, TEXT("Boss StateTree failed to compile."));
		Log.DumpToLog(LogOneBossFight);
		return nullptr;
	}

	Package->MarkPackageDirty();
	return StateTree;
#else
	return nullptr;
#endif
}
