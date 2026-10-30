// Copyright One Boss Fight. All Rights Reserved.
#include "Boss/RPGFrameworkBossController.h"
#include "Boss/RPGFrameworkBossCharacter.h"
#include "Player/RPGBossFrameworkProfile.h"
#include "NavigationSystem.h"
#include "NavigationPath.h"
#include "Navigation/PathFollowingComponent.h"
bool ARPGFrameworkBossController::WalkToBand(ARPGFrameworkBossCharacter* Boss,FString& Error)
{
    Error.Reset();
    if (!IsValid(Boss)||GetPawn()!=Boss||!IsValid(Boss->ExplicitTarget())||!Boss->ProofProfile())
    {Error=TEXT("Framework.Nav.OwnerTarget");return false;}
    const auto& P=*Boss->ProofProfile(); const FVector Target=Boss->ExplicitTarget()->GetActorLocation();
    FVector Away=Boss->GetActorLocation()-Target; Away.Z=0.f;
    if (!Away.Normalize()) {Error=TEXT("Framework.Nav.Coincident");return false;}
    UNavigationSystemV1* Nav=FNavigationSystem::GetCurrent<UNavigationSystemV1>(GetWorld()); FNavLocation Projected;
    if (!Nav||!Nav->ProjectPointToNavigation(Target+Away*((P.BandMinCm+P.BandMaxCm)*.5f),Projected))
    {Error=TEXT("Framework.Nav.Projection");return false;}
    FAIMoveRequest Request; Request.SetGoalLocation(Projected.Location); Request.SetAcceptanceRadius(P.AcceptanceCm);
    Request.SetUsePathfinding(true);Request.SetAllowPartialPath(false);Request.SetReachTestIncludesAgentRadius(false);Request.SetReachTestIncludesGoalRadius(false);
    // Engine order (PathFollowingComponent.cpp RequestMove): callbacks fired inside MoveTo carry the id of the ABORTED previous
    // request or of an immediate-finish request (failed/already-at-goal, handled below via R.Code); a new accepted request only
    // starts moving there, so its completion cannot arrive before OwnedRequest is assigned. Invalidate first so an old id is ignored.
    OwnedRequest=FAIRequestID::InvalidRequest;
    FNavPathSharedPtr Path; BossOwner=Boss;
    const FPathFollowingRequestResult R=MoveTo(Request,&Path);
    if (R.Code==EPathFollowingRequestResult::Failed||!Path.IsValid()||Path->IsPartial())
    {StopOwnedWalk();Error=TEXT("Framework.Nav.NoFullPath");return false;}
    OwnedRequest=R.MoveId;
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] nav request=%u projected=%s fullPath=1 result=%d"),uint32(OwnedRequest),*Projected.Location.ToString(),int32(R.Code));
    if(R.Code==EPathFollowingRequestResult::AlreadyAtGoal) {OwnedRequest=FAIRequestID::InvalidRequest;Boss->WalkArrived();}
    return true;
}
void ARPGFrameworkBossController::OnMoveCompleted(FAIRequestID RequestID,const FPathFollowingResult& Result)
{
    Super::OnMoveCompleted(RequestID,Result);
    if (OwnedRequest==FAIRequestID::InvalidRequest||RequestID!=OwnedRequest) return;
    OwnedRequest=FAIRequestID::InvalidRequest;
    if (!BossOwner.IsValid()) return;
    if (Result.Code==EPathFollowingResult::Success) BossOwner->WalkArrived();
    else BossOwner->Fail(TEXT("Framework.Nav.MoveFailed"));
}
void ARPGFrameworkBossController::OnUnPossess()
{
    StopOwnedWalk();
    Super::OnUnPossess();
}
void ARPGFrameworkBossController::StopOwnedWalk()
{
    // Invalidate before StopMovement, whose completion callback can run synchronously.
    OwnedRequest=FAIRequestID::InvalidRequest; StopMovement();BossOwner.Reset();
}
