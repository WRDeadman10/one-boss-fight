// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RPGBossTrackerTickOrderFixtures.generated.h"

UCLASS(Transient)
class URPGBossTrackerTickOrderProbe : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGBossTrackerTickOrderProbe();
	int32 FrameState = 0;

protected:
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
};

UCLASS(Transient)
class URPGBossTrackerTickConsumerProbe : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGBossTrackerTickConsumerProbe();
	int32 ObservedFrameState = INDEX_NONE;
	TWeakObjectPtr<UActorComponent> BoundTracker;

protected:
	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
};
