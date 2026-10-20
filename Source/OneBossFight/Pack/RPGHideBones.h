// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RPGHideBones.generated.h"

/**
 * Hides the vertices skinned to the named bones (and their children) on the character's mesh at BeginPlay. Greystone's Paragon mesh has a sword and a shield baked in; the
 * pack attaches its own weapons, so the baked ones are hidden by bone (sword_bottom, shield_inner), which leaves the fur in the same material slot visible.
 */
UCLASS(ClassGroup = (Pack), meta = (BlueprintSpawnableComponent))
class ONEBOSSFIGHT_API URPGHideBones : public UActorComponent
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Hide Bones")
	TArray<FName> BoneNames;

protected:
	virtual void BeginPlay() override;
};
