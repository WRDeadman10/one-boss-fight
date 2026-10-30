// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "AIController.h"
#include "RPGFrameworkBossController.generated.h"
class ARPGFrameworkBossCharacter;
UCLASS()
class ONEBOSSFIGHT_API ARPGFrameworkBossController : public AAIController
{
    GENERATED_BODY()
public:
    bool WalkToBand(ARPGFrameworkBossCharacter* Boss,FString& Error);
    void StopOwnedWalk();
    virtual void OnMoveCompleted(FAIRequestID RequestID,const FPathFollowingResult& Result) override;
    virtual void OnUnPossess() override;
private:
    FAIRequestID OwnedRequest=FAIRequestID::InvalidRequest;
    TWeakObjectPtr<ARPGFrameworkBossCharacter> BossOwner;
};
