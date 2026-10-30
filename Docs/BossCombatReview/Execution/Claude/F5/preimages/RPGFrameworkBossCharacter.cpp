// Copyright One Boss Fight. All Rights Reserved.
#include "Boss/RPGFrameworkBossCharacter.h"
#include "Boss/RPGFrameworkBossController.h"
#include "Boss/RPGFrameworkMoveExecutor.h"
#include "Boss/RPGFrameworkProofFixture.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/Engine.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Controller.h"
#include "Pack/RPGBlueprintCall.h"
ARPGFrameworkBossCharacter::ARPGFrameworkBossCharacter()
{
    PrimaryActorTick.bCanEverTick=true; AutoPossessAI=EAutoPossessAI::Disabled;
    AIControllerClass=ARPGFrameworkBossController::StaticClass(); bUseControllerRotationYaw=false;
    GetCharacterMovement()->DisableMovement();GetCharacterMovement()->bOrientRotationToMovement=false;
    GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    GetMesh()->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
    Executor=CreateDefaultSubobject<URPGFrameworkMoveExecutor>(TEXT("FrameworkExecutor"));SetCanBeDamaged(false);
}
bool ARPGFrameworkBossCharacter::InitializeProof(ARPGFrameworkProofFixture* Fixture,URPGBossFrameworkProfile* Profile,APawn* InTarget,uint64 Encounter,uint64 Generation,FString& Error)
{
    Error.Reset();
    if(bInitialized||!IsInGameThread()||!IsValid(Fixture)||Fixture->GetWorld()!=GetWorld()||!Fixture->Authorizes(this,InTarget)||
        !GetWorld()||GetNetMode()!=NM_Standalone||!IsValid(InTarget)||InTarget==this||InTarget->GetWorld()!=GetWorld()||!Encounter||!Generation)
    {Error=TEXT("Framework.Boss.ProofAuthority");return false;}
    TUniquePtr<FRPGFrameworkDependencies> D;
    if(!RPGFramework::ResolveProfile(Profile,D,Error))return false;
    if(!InTarget->IsA(D->TargetClass.Get())){Error=TEXT("Framework.Boss.TargetClass");return false;}
    Target=InTarget;TargetController=InTarget->GetController();
    if(!ValidateTarget(TargetHPBefore)){Target.Reset();Error=TEXT("Framework.Boss.TargetHealth");return false;}
    ExpectedTargetHP=TargetHPBefore;
    Dependencies=MoveTemp(D);ProofFixture=Fixture;EncounterId=Encounter;GenerationId=Generation;
    const auto& P=*Dependencies->Profile.Get();
    GetCapsuleComponent()->SetCapsuleSize(P.CapsuleRadiusCm,P.CapsuleHalfHeightCm);
    GetMesh()->SetSkeletalMesh(Dependencies->Mesh.Get());GetMesh()->SetRelativeTransform(P.MeshRelativeTransform);
    GetMesh()->SetAnimInstanceClass(Dependencies->AnimClass.Get());
    for(FName Bone:{FName(TEXT("weapon_r")),FName(TEXT("root_weapon_end_r"))})
        if(!GetMesh()->DoesSocketExist(Bone)){Error=TEXT("Framework.Boss.WeaponBone");Fail(Error);return false;}
    if(GetMesh()->GetSocketLocation(TEXT("weapon_r")).Equals(GetMesh()->GetSocketLocation(TEXT("root_weapon_end_r"))))
    {Error=TEXT("Framework.Boss.DegenerateSegment");Fail(Error);return false;}
    if(!Executor->Initialize(this,*Dependencies,InTarget,Encounter,Generation,Error)){Fail(Error);return false;}
    SpawnDefaultController();auto* AI=Cast<ARPGFrameworkBossController>(GetController());
    if(!AI){Error=TEXT("Framework.Boss.Controller");Fail(Error);return false;}
    GetCharacterMovement()->MaxWalkSpeed=P.WalkSpeedCmPerSecond;GetCharacterMovement()->SetMovementMode(MOVE_Walking);
    StartedAt=GetWorld()->GetTimeSeconds();WalkStart=GetActorLocation();bInitialized=true;
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] dependencies mesh=%s skeleton=%s animClass=%s sequence=%s slot=%s resolved=1 label=%s"),*Dependencies->Mesh->GetPathName(),*Dependencies->Card->Spec().Skeleton.ToSoftObjectPath().ToString(),*Dependencies->AnimClass->GetPathName(),*Dependencies->Card->Spec().Sequence.ToSoftObjectPath().ToString(),*Dependencies->Card->Spec().SlotName.ToString(),*Dependencies->Profile->FixtureLabel.Replace(TEXT(" "),TEXT("_")));
    if(!AI->WalkToBand(this,Error)){Fail(Error);return false;}return true;
}
bool ARPGFrameworkBossCharacter::ValidateTarget(double& HP) const
{
    HP=0.;return TargetController.IsValid()&&Target.IsValid()&&Target->GetController()==TargetController.Get()&&TargetController->GetPawn()==Target.Get()&&!Target->IsActorBeingDestroyed()&&Target->GetWorld()==GetWorld()&&
        RPGPack::ReadAttribute(Target.Get(),TEXT("Attribute.Health"),false,HP)&&FMath::IsFinite(HP)&&HP>0.;
}
void ARPGFrameworkBossCharacter::WalkArrived()
{
    if(!bInitialized||bFailed||bArrived)return;
    const auto& P=*Dependencies->Profile.Get();const double Range=FVector::Dist2D(GetActorLocation(),Target->GetActorLocation());
    if(!FMath::IsFinite(Range)||Range<P.BandMinCm||Range>P.BandMaxCm||!GetCharacterMovement()->IsMovingOnGround())
    {Fail(TEXT("Framework.Nav.ArrivalBandOrGround"));return;}
    bArrived=true;GetCharacterMovement()->StopMovementImmediately();
    if(auto* AI=Cast<ARPGFrameworkBossController>(GetController()))AI->StopOwnedWalk();
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] walk start=%s end=%s distanceCm=%g rangeCm=%g bandMin=%g bandMax=%g capsule=%s mesh=%s"),*WalkStart.ToString(),*GetActorLocation().ToString(),FVector::Dist(WalkStart,GetActorLocation()),Range,P.BandMinCm,P.BandMaxCm,*GetCapsuleComponent()->GetComponentLocation().ToString(),*GetMesh()->GetComponentLocation().ToString());
}
void ARPGFrameworkBossCharacter::Tick(float Delta)
{
    Super::Tick(Delta);if(!bInitialized||bFailed||bSucceeded)return;
    double HP=0.;if(!ProofFixture.IsValid()||!ValidateTarget(HP)||!FMath::IsNearlyEqual(HP,ExpectedTargetHP)){Fail(TEXT("Framework.Boss.TargetLifeOrHealthChanged"));return;}
    const auto& P=*Dependencies->Profile.Get();
    if(!bArrived&&GetWorld()->GetTimeSeconds()-StartedAt>P.WalkTimeoutSeconds){Fail(TEXT("Framework.Nav.Timeout"));return;}
    if(bArrived&&!bStartedMove)
    {
        const FVector D=Target->GetActorLocation()-GetActorLocation();FRPGBossDecisionSnapshot S;
        S.EncounterId=EncounterId;S.Generation=GenerationId;S.TargetId=uint64(Target->GetUniqueID());S.FrameId=GFrameCounter;
        S.PhaseId=Dependencies->Card->Spec().PhaseId;S.ClockSeconds=GetWorld()->GetTimeSeconds();S.RangeCm=D.Size2D();
        S.SignedYawDegrees=FMath::FindDeltaAngleDegrees(GetActorRotation().Yaw,D.Rotation().Yaw);S.bTargetValid=S.bNeutral=true;
        GetCharacterMovement()->StopMovementImmediately();FString Error;
        if(!Executor->Start(S,Error)){Fail(Error);return;}bStartedMove=true;
    }
    if(bStartedMove&&Executor->DidFinish()&&Executor->IsClean())
    {
        bSucceeded=true;
        if(Dependencies->Profile->bDamageEnabled)
        {
            UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] invariant targetHPBefore=%g targetHPAfter=%g expectedHP=%g acceptedHits=%d appliedDamage=%g"),TargetHPBefore,HP,ExpectedTargetHP,Executor->AcceptedHits(),Executor->AppliedDamageTotal());
            UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] RESULT outcome=CompletedWithDamage acceptedHits=%d"),Executor->AcceptedHits());
        }
        else
        {
            UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] invariant targetHPBefore=%g targetHPAfter=%g damageAPIInvocationsByThisExecutor=0"),TargetHPBefore,HP);
            UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] RESULT outcome=CompletedTelemetryOnly"));
        }
    }
}
void ARPGFrameworkBossCharacter::Fail(const FString& Error)
{
    if(bFailed)return;bFailed=true;
    if(auto* AI=Cast<ARPGFrameworkBossController>(GetController()))AI->StopOwnedWalk();
    GetCharacterMovement()->StopMovementImmediately();GetCharacterMovement()->DisableMovement();Executor->Abort(Error);
    UE_LOG(LogTemp,Error,TEXT("[FrameworkProof] ERROR token=%s bossInactive=1"),*Error);
    if(GEngine)GEngine->AddOnScreenDebugMessage(-1,10.f,FColor::Red,TEXT("FrameworkProof: ")+Error);
}
void ARPGFrameworkBossCharacter::EndPlay(const EEndPlayReason::Type Reason)
{
    if(auto* AI=Cast<ARPGFrameworkBossController>(GetController()))AI->StopOwnedWalk();Executor->Abort(TEXT("EndPlay"));
    Dependencies.Reset();Target.Reset();TargetController.Reset();ProofFixture.Reset();Super::EndPlay(Reason);
}
