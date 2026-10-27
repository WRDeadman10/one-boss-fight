// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "BehaviorTree/BTTaskNode.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "RPGScratchRouteA.generated.h"

/**
 * SCRATCH PROOF ONLY (owner approval G-3, 2026-10-26): adapter route (a) of the boss combat program. Nothing here ships behaviour;
 * it exists to show, with readback, that a project behaviour-tree task can run under the pack's AI controller and blackboard
 * when a project-owned EnemyInfo names a project tree, and that a reservation can be allocated BEFORE the pack ability starts.
 * No pack asset is edited; the helpers only read or set properties on an actor spawned by the test itself.
 */
UCLASS()
class ONEBOSSFIGHT_API URPGScratchRouteATask : public UBTTaskNode
{
	GENERATED_BODY()

public:
	/** The pack ability tag asked for (the same route the pack tree uses, through RPGPack::TryActivateByTag). */
	UPROPERTY(EditAnywhere, Category = "Scratch")
	FName AbilityTag = TEXT("Ability.EnterCombat");

	/** The project's own route (RPGAttackTracker, RPGBossStagger) forces the pack ability; the scratch task uses the same call. */
	UPROPERTY(EditAnywhere, Category = "Scratch")
	bool bForceActivate = true;

	/** When true the diagnostic reservation is refused: the task must not call the pack and must change nothing. */
	UPROPERTY(EditAnywhere, Category = "Scratch")
	bool bDenyReservation = false;

	virtual EBTNodeResult::Type ExecuteTask(UBehaviorTreeComponent& OwnerComp, uint8* NodeMemory) override;
	virtual FString GetStaticDescription() const override;
};

UCLASS()
class ONEBOSSFIGHT_API URPGScratchRouteALibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/** Editor only: creates and saves a NEW minimal tree (selector of two sequences: denied task, then allowed task). Refuses to overwrite an existing package. */
	UFUNCTION(BlueprintCallable, Category = "RPG|Scratch")
	static bool CreateScratchBehaviorTree(const FString& PackagePath, const FString& BlackboardPath, FString& OutError);

	/** Spawns BossClass with its EnemyInfoRef set BEFORE BeginPlay (deferred spawn), so the info is read exactly as for a placed boss; spawns the default controller when none was created. */
	UFUNCTION(BlueprintCallable, Category = "RPG|Scratch")
	static AActor* SpawnBossWithInfo(UObject* WorldContext, UClass* BossClass, UObject* InfoAsset, FVector Location, FString& OutError);

	/** Readback: EnemyInfoRef object path, controller class, running tree, blackboard asset, pawn state. */
	UFUNCTION(BlueprintCallable, Category = "RPG|Scratch")
	static FString DescribeAI(AActor* Boss);

	/** READ-ONLY diagnostics (owner approval 2026-10-26, scratch only): one line per reflected property of the object's class chain: owner class, name, kind, declared constraint (object class, meta class, struct, array element, map key/value) and the current value text. Writes nothing, changes nothing. */
	UFUNCTION(BlueprintCallable, Category = "RPG|Scratch")
	static TArray<FString> DumpTypedProperties(UObject* Object);

	/** Capture tooling (owner scratch approval): spawns a plain CameraActor in the given world at Location, looking at LookAt. Test runs only, destroyed by the caller. */
	UFUNCTION(BlueprintCallable, Category = "RPG|Scratch")
	static AActor* SpawnCaptureCamera(UObject* WorldContext, FVector Location, FVector LookAt);

	/** Fixture tooling (owner approval 2026-10-26 'Yes' for the typed-ABI test assets): exports one property of an object as text (read-only), and imports text into one property of an object, ONLY when the object's path starts with /Game/OneBossFight/ReviewFixtures/ . Never touches a pack or shipped asset. */
	UFUNCTION(BlueprintCallable, Category = "RPG|Scratch")
	static FString ExportPropertyText(UObject* Object, FName PropertyName);

	UFUNCTION(BlueprintCallable, Category = "RPG|Scratch")
	static FString ImportPropertyTextToFixture(UObject* Object, FName PropertyName, const FString& Text); // returns the empty string on success, otherwise the error

	UFUNCTION(BlueprintCallable, Category = "RPG|Scratch")
	static TArray<FString> GetRouteAReport();

	UFUNCTION(BlueprintCallable, Category = "RPG|Scratch")
	static void ResetRouteAReport();
};
