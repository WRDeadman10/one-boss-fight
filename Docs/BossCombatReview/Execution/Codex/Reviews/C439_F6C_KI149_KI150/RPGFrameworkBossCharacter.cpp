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
#include "Player/RPGBossRules.h"
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
    if (Dependencies->Candidates.Num()>0)
    {
        FRPGBossSelectorConfig Config; Config.RepeatPenalty=Dependencies->Profile->RepeatPenalty; Config.RepeatMemory=Dependencies->Profile->RepeatMemory;
        TArray<FRPGBossSelectorCandidate> List;
        for (const auto& C:Dependencies->Candidates) {FRPGBossSelectorCandidate X; X.Card=C.Card; X.CooldownSeconds=C.CooldownSeconds; X.Weight=C.Weight; List.Add(X);}
        if (!Selector.Initialize(Config,List,Error)) {Fail(Error);return false;}
    }
    const auto& P=*Dependencies->Profile.Get();
    CurrentPhaseId=Dependencies->FirstCard()->Spec().PhaseId;bPhaseTwoLatched=false;
    if (Dependencies->Profile->BossMaxHealth>0.f)
    {
        bHittable=true; MaxHealth=Health=Dependencies->Profile->BossMaxHealth;
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] boss_health max=%g playerHitDamage=%g label=%s"),MaxHealth,double(Dependencies->Profile->PlayerHitDamage),*Dependencies->Profile->FixtureLabel.Replace(TEXT(" "),TEXT("_")));
    }
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
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] dependencies mesh=%s skeleton=%s animClass=%s sequence=%s slot=%s resolved=1 label=%s"),*Dependencies->Mesh->GetPathName(),*Dependencies->FirstCard()->Spec().Skeleton.ToSoftObjectPath().ToString(),*Dependencies->AnimClass->GetPathName(),*Dependencies->FirstCard()->Spec().Sequence.ToSoftObjectPath().ToString(),*Dependencies->FirstCard()->Spec().SlotName.ToString(),*Dependencies->Profile->FixtureLabel.Replace(TEXT(" "),TEXT("_")));
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
    Super::Tick(Delta);if(!bInitialized||bFailed||bSucceeded||bDead)return;
    double HP=0.;const bool bTargetOk=ProofFixture.IsValid()&&ValidateTarget(HP);
    if(!bTargetOk||!FMath::IsNearlyEqual(HP,ExpectedTargetHP))
    {
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] target_health_mismatch valid=%d actual=%g expected=%g generation=%llu"),bTargetOk?1:0,HP,ExpectedTargetHP,GenerationId);
        Fail(TEXT("Framework.Boss.TargetLifeOrHealthChanged"));return;
    }
    const auto& P=*Dependencies->Profile.Get();
    if(!bArrived&&GetWorld()->GetTimeSeconds()-StartedAt>P.WalkTimeoutSeconds){Fail(TEXT("Framework.Nav.Timeout"));return;}
    if(bArrived&&!bStartedMove)
    {
        // F6c phase gate: only here (neutral, nothing playing), the pure legacy rule decides; the phase latches until restart.
        if(bHittable&&P.PhaseTwoFraction>0.f&&!bPhaseTwoLatched)
        {
            RPGBossRules::FFlags Flags;
            if(RPGBossRules::ResolveTransition(Flags,Health,MaxHealth,P.PhaseTwoFraction)==RPGBossRules::ETransitionResult::Start)
            {
                bPhaseTwoLatched=true;
                UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] phase_transition attack=%d from=%s to=%s health=%g max=%g fraction=%g"),AttacksDone+1,*CurrentPhaseId.ToString(),*P.PhaseTwoId.ToString(),Health,MaxHealth,double(P.PhaseTwoFraction));
                CurrentPhaseId=P.PhaseTwoId;
            }
        }
        const FVector D=Target->GetActorLocation()-GetActorLocation();FRPGBossDecisionSnapshot S;
        S.EncounterId=EncounterId;S.Generation=GenerationId;S.TargetId=uint64(Target->GetUniqueID());S.FrameId=GFrameCounter;
        S.PhaseId=CurrentPhaseId;S.ClockSeconds=GetWorld()->GetTimeSeconds();S.RangeCm=D.Size2D();
        S.SignedYawDegrees=FMath::FindDeltaAngleDegrees(GetActorRotation().Yaw,D.Rotation().Yaw);S.bTargetValid=S.bNeutral=true;
        GetCharacterMovement()->StopMovementImmediately();FString Error;
        if(Dependencies->Candidates.Num()>0)
        {
            FRPGBossSelectorDecision Decision;
            const bool bAsked=Selector.Select(Executor->Model(),S,Decision);
            for(const FRPGBossSelectorTrace& T:Decision.Traces)
            {
                if(T.bEligible){UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] candidate attack=%d card=%s score=%g"),AttacksDone+1,*T.MoveId.ToString(),T.Score);}
                else{UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] refusal attack=%d card=%s reason=%s"),AttacksDone+1,*T.MoveId.ToString(),*T.Refusal);}
            }
            if(!bAsked||Decision.ChosenIndex==INDEX_NONE){Fail(TEXT("Framework.Selector.NoCandidate"));return;}
            UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] decision attack=%d chosen=%s score=%g range=%g phase=%s"),AttacksDone+1,*Decision.MoveId.ToString(),Decision.Score,S.RangeCm,*S.PhaseId.ToString());
            if(!Executor->StartCard(Dependencies->Candidates[Decision.ChosenIndex].Card,S,Error)){Fail(Error);return;}
            Selector.NoteStarted(Decision.ChosenIndex,S.ClockSeconds);
        }
        else if(!Executor->Start(S,Error)){Fail(Error);return;}
        bStartedMove=true;
    }
    if(bStartedMove&&Executor->DidFinish()&&Executor->IsClean()&&Dependencies->Candidates.Num()>0&&AttacksDone+1<Dependencies->Profile->AttackCount)
    {
        // F5: the selector decides every attack; re-arm the executor and decide again on the next tick.
        ++AttacksDone;
        if(!Executor->PrepareNextAttack()){Fail(TEXT("Framework.Playback.NextAttack"));return;}
        bStartedMove=false;
        return;
    }
    if(bStartedMove&&Executor->DidFinish()&&Executor->IsClean())
    {
        bSucceeded=true;
        if(Dependencies->Profile->bDamageEnabled)
        {
            UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] invariant targetHPBefore=%g targetHPAfter=%g expectedHP=%g acceptedHits=%d appliedDamage=%g"),TargetHPBefore,HP,ExpectedTargetHP,Executor->AcceptedHits(),Executor->AppliedDamageTotal());
            UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] RESULT outcome=CompletedWithDamage acceptedHits=%d attacks=%d"),Executor->AcceptedHits(),AttacksDone+1);
        }
        else
        {
            UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] invariant targetHPBefore=%g targetHPAfter=%g damageAPIInvocationsByThisExecutor=0"),TargetHPBefore,HP);
            UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] RESULT outcome=CompletedTelemetryOnly"));
        }
    }
}
double ARPGFrameworkBossCharacter::ApplyPlayerHit(double Multiplier)
{
    if (!bHittable||bDead||bFailed||!bInitialized||!FMath::IsFinite(Multiplier)||Multiplier<0.) return 0.;
    const double Before=Health, Loss=FMath::Min(Health,double(Dependencies->Profile->PlayerHitDamage)*Multiplier);
    Health-=Loss;
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] boss_hit damage=%g healthBefore=%g healthAfter=%g"),Loss,Before,Health);
    if (Health<=0.) Die();
    return Loss;
}
bool ARPGFrameworkBossCharacter::RestartEncounter(uint64 NewGeneration,FString& Error)
{
    Error.Reset();
    if (!bInitialized||bFailed||(!bDead&&!bSucceeded)||NewGeneration<=GenerationId||!IsInGameThread()) {Error=TEXT("Framework.Boss.RestartState");return false;}
    double HP=0.; if (!ValidateTarget(HP)) {Error=TEXT("Framework.Boss.TargetHealth");return false;}
    if (!Executor->Rearm(NewGeneration,Error)) return false;
    const TCHAR* OldState=bDead?TEXT("Dead"):TEXT("Finished");
    GenerationId=NewGeneration; TargetHPBefore=ExpectedTargetHP=HP; AttacksDone=0; bStartedMove=false; bArrived=false; bSucceeded=false; bDead=false;
    if (bHittable) Health=MaxHealth;
    Selector.Reset(); CurrentPhaseId=Dependencies->FirstCard()->Spec().PhaseId; bPhaseTwoLatched=false;
    SetActorLocation(WalkStart,false,nullptr,ETeleportType::TeleportPhysics);
    FVector Face=Target->GetActorLocation()-WalkStart; Face.Z=0.f; if (!Face.IsNearlyZero()) SetActorRotation(FRotator(0.f,Face.Rotation().Yaw,0.f));
    GetCharacterMovement()->SetMovementMode(MOVE_Walking);
    StartedAt=GetWorld()->GetTimeSeconds();
    auto* AI=Cast<ARPGFrameworkBossController>(GetController());
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] encounter_reset generation=%llu oldState=%s executorRearmed=1 bossHealth=%g targetHealth=%g"),GenerationId,OldState,Health,HP);
    if (!AI||!AI->WalkToBand(this,Error)) {Fail(Error.IsEmpty()?FString(TEXT("Framework.Boss.Controller")):Error);return false;}
    return true;
}
void ARPGFrameworkBossCharacter::Die()
{
    // Death: the attack in progress ends through the executor's abort (windows closed, owned montage stopped), movement stops, the encounter is over.
    if (bDead) return;
    bDead=true;
    if(auto* AI=Cast<ARPGFrameworkBossController>(GetController()))AI->StopOwnedWalk();
    GetCharacterMovement()->StopMovementImmediately();GetCharacterMovement()->DisableMovement();
    Executor->Abort(TEXT("BossDead"));
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] boss_dead generation=%llu executorAborted=1"),GenerationId);
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] RESULT outcome=BossDefeated acceptedHits=%d attacks=%d"),Executor->AcceptedHits(),AttacksDone+(bStartedMove?1:0));
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
