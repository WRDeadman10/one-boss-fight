// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Boss/RPGBossCombatComponent.h"
#include "Components/StateTreeComponent.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "StateTreeConditionBase.h"
#include "StateTreeTaskBase.h"
#include "RPGBossStateTree.generated.h"

class UStateTree;

/**
 * The boss's top-level states as a StateTree: Dormant, Entrance, Combat, PhaseTransition, Dead.
 *
 * The tree is a thin mirror. URPGBossCombatComponent owns the flow and decides every change; the tree
 * follows it (a transition fires when the component's state differs from the active state) and each state's
 * mirror task reports back, so the tree is visible in the StateTree debugger and the two can be compared.
 */

USTRUCT()
struct FRPGBossStateConditionInstanceData
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, Category = "Parameter")
	ERPGBossState ExpectedState = ERPGBossState::Dormant;
};

/** True while the boss component is in ExpectedState. Used for state entry and for every transition. */
USTRUCT(meta = (DisplayName = "RPG Boss State Is"))
struct ONEBOSSFIGHT_API FRPGBossStateCondition : public FStateTreeConditionCommonBase
{
	GENERATED_BODY()

	using FInstanceDataType = FRPGBossStateConditionInstanceData;

	virtual const UStruct* GetInstanceDataType() const override { return FInstanceDataType::StaticStruct(); }
	virtual bool TestCondition(FStateTreeExecutionContext& Context) const override;
};

USTRUCT()
struct FRPGBossMirrorTaskInstanceData
{
	GENERATED_BODY()

	/** The boss state this StateTree state stands for. */
	UPROPERTY(EditAnywhere, Category = "Parameter")
	ERPGBossState MirroredState = ERPGBossState::Dormant;
};

/** Runs for as long as its state is active and tells the boss component which state the tree is in. */
USTRUCT(meta = (DisplayName = "RPG Boss Mirror"))
struct ONEBOSSFIGHT_API FRPGBossMirrorTask : public FStateTreeTaskCommonBase
{
	GENERATED_BODY()

	using FInstanceDataType = FRPGBossMirrorTaskInstanceData;

	FRPGBossMirrorTask()
	{
		bShouldCallTick = false;
	}

	virtual const UStruct* GetInstanceDataType() const override { return FInstanceDataType::StaticStruct(); }
	virtual EStateTreeRunStatus EnterState(FStateTreeExecutionContext& Context, const FStateTreeTransitionResult& Transition) const override;
};

/** StateTree component that takes its asset from a plain property, so Blueprints and tests can assign it. */
UCLASS(ClassGroup = (AI), meta = (BlueprintSpawnableComponent))
class ONEBOSSFIGHT_API URPGBossStateTreeComponent : public UStateTreeComponent
{
	GENERATED_BODY()

public:
	URPGBossStateTreeComponent(const FObjectInitializer& ObjectInitializer = FObjectInitializer::Get());

	virtual void InitializeComponent() override;

	/** The StateTree asset to run (build it with URPGBossStateTreeBuilder). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Boss")
	TObjectPtr<UStateTree> BossStateTree;

	/** Assigns the asset at runtime. Call before StartLogic. */
	UFUNCTION(BlueprintCallable, Category = "Boss")
	void SetStateTreeAsset(UStateTree* NewStateTree);
};

/** Editor-only: builds and compiles the boss StateTree asset. Called by Scripts/Editor/setup_m4_statetree.py. */
UCLASS()
class ONEBOSSFIGHT_API URPGBossStateTreeBuilder : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/**
	 * Creates (or replaces the contents of) the StateTree asset at PackagePath/AssetName with the five boss states,
	 * their mirror tasks and the transitions between them, and compiles it. Returns null on failure. The caller saves.
	 */
	UFUNCTION(BlueprintCallable, Category = "RPG|Authoring")
	static UStateTree* BuildBossStateTree(const FString& PackagePath, const FString& AssetName);
};
