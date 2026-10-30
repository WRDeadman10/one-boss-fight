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
#include "Player/RPGBossMath.h"
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
    ResetBleed();CurrentPhaseId=Dependencies->FirstCard()->Spec().PhaseId;bPhaseTwoLatched=false;Posture=double(Dependencies->Profile->PostureMax);LastPostureDrain=-1.;bStaggered=bStaggerAbortedAttack=false;
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
    if(PostureEnabled())
    {
        if(bStaggered)
        {
            GetCharacterMovement()->StopMovementImmediately();
            if(GetWorld()->GetTimeSeconds()>=StaggerEndsAt)EndStagger();
            return;   // no selection while down
        }
        const float Before=float(Posture); Posture=RPGBossMath::RegenStep(float(Posture),P.PostureMax,GetWorld()->GetTimeSeconds(),LastPostureDrain,P.PostureRegenDelaySeconds,P.PostureRegenPerSecond,Delta);
        if(float(Posture)>Before+KINDA_SMALL_NUMBER&&FMath::IsNearlyEqual(float(Posture),P.PostureMax)){UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] posture_regen_full posture=%g max=%g"),Posture,double(P.PostureMax));}
    }
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
    const auto& P=*Dependencies->Profile.Get();
    return ApplyHit(Multiplier,double(P.PlayerPostureHitAmount)*Multiplier,double(P.BleedBuildupPerHit)*Multiplier);
}
double ARPGFrameworkBossCharacter::ApplyPlayerAttackHit(const FRPGWeaponAttackRow& Row, double Multiplier)
{
    if (!bHittable||bDead||bFailed||!bInitialized||!FMath::IsFinite(Multiplier)||Multiplier<0.||!FMath::IsFinite(Row.HealthDamageMultiplier)||Row.HealthDamageMultiplier<0.f) return 0.;
    return ApplyHit(double(Row.HealthDamageMultiplier)*Multiplier,double(Row.PostureDamage)*Multiplier,double(Row.BleedBuildup)*Multiplier);
}
double ARPGFrameworkBossCharacter::ApplyHit(double HealthFactor, double PostureAmount, double BleedAmount)
{
    if (!bHittable||bDead||bFailed||!bInitialized) return 0.;
    const double Before=Health, Loss=FMath::Min(Health,double(Dependencies->Profile->PlayerHitDamage)*HealthFactor);
    Health-=Loss;
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] boss_hit damage=%g healthBefore=%g healthAfter=%g"),Loss,Before,Health);
    if (Health<=0.) {Die();return Loss;}
    if (PostureEnabled())
    {
        const double Now=GetWorld()->GetTimeSeconds();
        if (bStaggered) {UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] posture_held reason=StaggerActive posture=%g"),Posture);}
        else
        {
            const double Drain=FMath::Min(Posture,PostureAmount);
            Posture-=Drain; LastPostureDrain=Now;
            UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] posture_drain amount=%g postureBefore=%g postureAfter=%g max=%g"),Drain,Posture+Drain,Posture,double(Dependencies->Profile->PostureMax));
            RPGBossRules::FFlags Flags; Flags.bDead=bDead; Flags.bStaggered=bStaggered;
            if (Posture<=0. && RPGBossRules::ResolveBreak(Flags,false)==RPGBossRules::EBreakResult::Started) StartStagger();
        }
    }
    if (BleedEnabled()) ApplyBleed(BleedAmount);
    return Loss;
}
bool ARPGFrameworkBossCharacter::BleedEnabled() const {return bInitialized&&bHittable&&Dependencies&&Dependencies->Profile->BleedBuildupPerHit>0.f;}
void ARPGFrameworkBossCharacter::ResetBleed()
{
    BleedState=RPGBleedRules::FState(); BleedProcFrame=MAX_uint64;
    if (Dependencies) BleedState.Threshold=Dependencies->Profile->BleedInitialThreshold;
}
void ARPGFrameworkBossCharacter::ApplyBleed(double BleedAmount)
{
    // The legacy pure rules, unchanged: no buildup on a dead boss or in the same frame as a proc; a proc takes a fraction of the maximum health, never the last point.
    const auto& P=*Dependencies->Profile.Get();
    RPGBleedRules::FConfig Config; Config.InitialThreshold=P.BleedInitialThreshold; Config.ThresholdIncrease=P.BleedThresholdIncrease; Config.ThresholdMax=P.BleedThresholdMax; Config.HpFraction=P.BleedHpFraction;
    const float Amount=float(BleedAmount);
    const RPGBleedRules::EResult Result=RPGBleedRules::Apply(BleedState,Config,Amount,bDead,false,false,BleedProcFrame==GFrameCounter);
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] bleed_buildup amount=%g buildup=%g threshold=%g result=%s"),double(Amount),double(BleedState.Buildup),double(BleedState.Threshold),RPGBleedRules::Name(Result));
    if (Result!=RPGBleedRules::EResult::Proc) return;
    BleedProcFrame=GFrameCounter;
    const double Before=Health, Damage=double(RPGBleedRules::ProcDamage(float(MaxHealth),float(Health),Config));
    Health-=Damage;
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] bleed_proc procs=%d damage=%g healthBefore=%g healthAfter=%g nextThreshold=%g"),BleedState.Procs,Damage,Before,Health,double(BleedState.Threshold));
}
bool ARPGFrameworkBossCharacter::PostureEnabled() const {return bInitialized&&bHittable&&Dependencies&&Dependencies->Profile->PostureMax>0.f;}
void ARPGFrameworkBossCharacter::StartStagger()
{
    // Stance break (reached only alive; Dead outranks it in ResolveBreak). A running attack is aborted (windows closed, montage stopped); in neutral nothing is aborted.
    const bool bMidAttack=bStartedMove&&!Executor->DidFinish();
    bStaggered=true; StaggerEndsAt=GetWorld()->GetTimeSeconds()+double(Dependencies->Profile->StaggerSeconds);
    if(auto* AI=Cast<ARPGFrameworkBossController>(GetController()))AI->StopOwnedWalk();
    GetCharacterMovement()->StopMovementImmediately();
    if(bMidAttack){Executor->Abort(TEXT("StanceBreak"));bStaggerAbortedAttack=true;}
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] stance_break state=%s duration=%g generation=%llu phase=%s"),bMidAttack?TEXT("MidAttack"):TEXT("Neutral"),double(Dependencies->Profile->StaggerSeconds),GenerationId,*CurrentPhaseId.ToString());
}
void ARPGFrameworkBossCharacter::EndStagger()
{
    bool bRecovered=true;
    if(bStaggerAbortedAttack){bRecovered=Executor->RecoverAfterAbort();bStartedMove=false;bStaggerAbortedAttack=false;}
    if(!bRecovered){Fail(TEXT("Framework.Playback.StaggerRecover"));return;}
    bStaggered=false; Posture=double(Dependencies->Profile->PostureMax); LastPostureDrain=-1.;
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] stagger_recovery postureRefilled=%g generation=%llu"),Posture,GenerationId);
    // A break while the boss was still walking to the band stopped the owned walk: ask for it again (the arrival check and the walk timeout run as before).
    if(!bArrived)
    {
        FString WalkError; auto* AI=Cast<ARPGFrameworkBossController>(GetController());
        if(!AI||!AI->WalkToBand(this,WalkError)){Fail(WalkError.IsEmpty()?FString(TEXT("Framework.Boss.Controller")):WalkError);return;}
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] walk_resumed generation=%llu"),GenerationId);
    }
}
bool ARPGFrameworkBossCharacter::RestartEncounter(uint64 NewGeneration,FString& Error)
{
    Error.Reset();
    if (!CanRestart(NewGeneration)||!IsInGameThread()) {Error=TEXT("Framework.Boss.RestartState");return false;}
    double HP=0.; if (!ValidateTarget(HP)) {Error=TEXT("Framework.Boss.TargetHealth");return false;}
    if (!Executor->Rearm(NewGeneration,Error)) return false;
    const TCHAR* OldState=bDead?TEXT("Dead"):TEXT("Finished");
    GenerationId=NewGeneration; TargetHPBefore=ExpectedTargetHP=HP; AttacksDone=0; bStartedMove=false; bArrived=false; bSucceeded=false; bDead=false;
    if (bHittable) Health=MaxHealth;
    Posture=double(Dependencies->Profile->PostureMax); LastPostureDrain=-1.; bStaggered=bStaggerAbortedAttack=false; ResetBleed();
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
