// Copyright One Boss Fight. All Rights Reserved.
#include "Boss/RPGFrameworkBossCharacter.h"
#include <limits>
#include "Boss/RPGFrameworkBossController.h"
#include "Boss/RPGFrameworkMoveExecutor.h"
#include "Boss/RPGFrameworkProofFixture.h"
#include "Components/CapsuleComponent.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Animation/AnimSequence.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/Engine.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Controller.h"
#include "NavigationSystem.h"
#include "Pack/RPGBlueprintCall.h"
#include "Player/RPGHitIntake.h"
#include "Player/RPGBossGuardRules.h"
#include "Player/RPGBossStrafeRules.h"
#include "Player/RPGBossDamage.h"
#include "Combat/RPGInputTestUtils.h"
#include "InputAction.h"
#include "Player/RPGDamageResolver.h"
#include "Player/RPGSwingTracker.h"
#include "Player/RPGBossMath.h"
#include "Player/RPGBossOverlayRules.h"
#include "Player/RPGPlayerParry.h"
#include "Player/RPGBossTrackRules.h"
#include "Player/RPGBossStuckRules.h"
#include "Player/RPGBossLeashRules.h"
#include "Player/RPGBossYawProbeRules.h"
#include "Player/RPGBossFatigueRules.h"
#include "Player/RPGBossRules.h"
#if !UE_BUILD_SHIPPING
static TAutoConsoleVariable<float> CVarBossProofBystander(TEXT("rpg.BossProofBystander"),0.f,TEXT("Test hook (BOSS-HIT-005): above 0 spawns one plain Character (a second pawn that is not the target) that many cm to the side of the target when the boss starts its first attack of an encounter. 0 = off. Not compiled into shipping builds."),ECVF_Default);
static TAutoConsoleVariable<float> CVarBossProofIFrameSweep(TEXT("rpg.BossProofIFrameSweep"),-1.f,TEXT("Test hook (BOSS-HIT-009): at this many game seconds after the boss's first attack of an encounter the player's REAL dodge input (IA_Dodge, held 0.12 s) is injected, and every tick from the press for 1.2 s a 1 HP probe goes through the damage resolver; the outcome of every probe is logged. Negative = off. Not compiled into shipping builds."),ECVF_Default);
static TAutoConsoleVariable<int32> CVarBossProofPlayerGuard(TEXT("rpg.BossProofPlayerGuard"),0,TEXT("Test hook (BOSS-COM-004 / HIT-008): 1 = from the boss's first attack of an encounter the player's REAL block input (IA_Block) is held for rpg.BossProofPlayerGuardSeconds; 2 = the REAL parry input (IA_Parry) is pressed every 0.5 s in that time. The guard tags of the player are logged every tick. 0 = off. Not compiled into shipping builds."),ECVF_Default);
static TAutoConsoleVariable<float> CVarBossProofPlayerGuardSeconds(TEXT("rpg.BossProofPlayerGuardSeconds"),6.f,TEXT("Test hook (BOSS-COM-004 / HIT-008): how long the guard input of rpg.BossProofPlayerGuard is driven."),ECVF_Default);
static TAutoConsoleVariable<float> CVarBossProofPlayerGuardPhaseSeconds(TEXT("rpg.BossProofPlayerGuardPhaseSeconds"),0.f,TEXT("Test hook (BOSS-COM-004): seconds added to time since the first attack for periodic IA_Parry pulses; 0 preserves the existing phase. Not compiled into shipping builds."),ECVF_Default);
static TAutoConsoleVariable<FString> CVarBossProofPlayerHits(TEXT("rpg.BossProofPlayerHits"),TEXT(""),TEXT("Test hook (BOSS-QA-003): comma separated seconds after the boss's first attack of an encounter at which the target's hit intake lands one test hit on the boss (game clock, so a fixed time step replays it exactly). Empty = off. Not compiled into shipping builds."),ECVF_Default);
static TAutoConsoleVariable<FString> CVarBossProofTargetShift(TEXT("rpg.BossProofTargetShift"),TEXT(""),TEXT("Test hook (BOSS-MOV-005): 'seconds:dx,dy,dz|seconds:dx,dy,dz' moves the target by that vector at those game-clock seconds after the boss first attack of an encounter (teleport). Empty = off. Not compiled into shipping builds."),ECVF_Default);
static TAutoConsoleVariable<int32> CVarBossTurnLatch(TEXT("rpg.BossProofTurnLatch"),1,TEXT("Test hook (BOSS-MOV-003): 0 turns the reposition turn WITHOUT the direction latch (control run: it still counts the direction changes). 1 = latch on (default behaviour). Not compiled into shipping builds."),ECVF_Default);
static TAutoConsoleVariable<FString> CVarBossProofPlayerDrink(TEXT("rpg.BossProofPlayerDrink"),TEXT(""),TEXT("Test hook (BOSS-SEL-009): comma separated seconds after the boss's first attack of an encounter at which the target plays its DrinkingPotion montage (game clock). Empty = off. Not compiled into shipping builds."),ECVF_Default);
static TAutoConsoleVariable<FString> CVarBossProofPlayerDodge(TEXT("rpg.BossProofPlayerDodge"),TEXT(""),TEXT("Test hook (BOSS-AWR-008): comma separated 'seconds' (backward) or 'seconds:F' (forward) after the boss's first attack of an encounter at which the target is launched away from / toward the boss (game clock). Empty = off. Not compiled into shipping builds."),ECVF_Default);
static TAutoConsoleVariable<int32> CVarBossProofTargetFault(TEXT("rpg.BossProofTargetFault"),0,TEXT("Test hook (BOSS-AWR-001): 1 sets the target's health to 0, 2 destroys the target pawn, when the boss starts its first attack of an encounter. 0 = off. Not compiled into shipping builds."),ECVF_Default);
static TAutoConsoleVariable<int32> CVarBossProofSkipInitialWalk(TEXT("rpg.BossProofSkipInitialWalk"),0,TEXT("Test hook (C-1258a): 1 skips the initial approach only when a test-authorized target is already within the profile band. 0 = off. Not compiled into shipping builds."),ECVF_Default);
static TAutoConsoleVariable<int32> CVarBossComboDuplicateGate(TEXT("rpg.BossComboDuplicateGate"),0,TEXT("Test hook (BOSS-COM-005): 1 evaluates every combo branch gate a second time with the SAME gate id right after the first, and logs that the duplicate was ignored without changing the combo state."),ECVF_Default);
static TAutoConsoleVariable<float> CVarBossProofYawProbe(TEXT("rpg.BossProofYawProbe"),0.f,TEXT("Test hook: positive degrees replaces selector snapshot yaw with a period-24 sinusoid centered at half the first card cone; <= 0 = off. Not compiled into shipping builds."),ECVF_Default);
#endif
static TAutoConsoleVariable<int32> CVarBossOverlay(TEXT("rpg.BossOverlay"),0,TEXT("Framework boss runtime overlay (BOSS-QA-001): 0 off, 1 on screen, 2 on screen and one [FrameworkProof] overlay log line per second."),ECVF_Default);
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
    return InitializeProofInternal(Fixture,Profile,InTarget,Encounter,Generation,Error,false);
}
bool ARPGFrameworkBossCharacter::InitializeWithProfileForTest(URPGBossFrameworkProfile* Profile,APawn* InTarget,FString& Error)
{
#if UE_BUILD_SHIPPING
    Error=TEXT("Framework.Boss.TestHookUnavailable");return false;
#else
    Error.Reset();
    if(!IsValid(Profile)){Error=TEXT("Framework.Boss.Profile");return false;}
    return InitializeProofInternal(nullptr,Profile,InTarget,1,1,Error,true);
#endif
}
ARPGFrameworkBossCharacter* ARPGFrameworkBossCharacter::SpawnFrameworkBossForTest(UObject* WorldContextObject,TSubclassOf<ARPGFrameworkBossCharacter> CharacterClass,FVector Location,FRotator Rotation)
{
#if UE_BUILD_SHIPPING
    return nullptr;
#else
    if(!CharacterClass||!CharacterClass->IsChildOf(StaticClass()))return nullptr;
    UWorld* World=WorldContextObject?WorldContextObject->GetWorld():nullptr;
    if(!IsValid(World)||!World->IsGameWorld())return nullptr;
    FActorSpawnParameters Params;
    Params.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;
    Params.ObjectFlags|=RF_Transient;
    return World->SpawnActor<ARPGFrameworkBossCharacter>(CharacterClass,Location,Rotation,Params);
#endif
}
bool ARPGFrameworkBossCharacter::InitializeProofInternal(ARPGFrameworkProofFixture* Fixture,URPGBossFrameworkProfile* Profile,APawn* InTarget,uint64 Encounter,uint64 Generation,FString& Error,bool bAllowDevTest)
{
    Error.Reset();
    const bool bFixtureAuthorized=IsValid(Fixture)&&Fixture->GetWorld()==GetWorld()&&Fixture->Authorizes(this,InTarget);
    const bool bTestAuthorized=bAllowDevTest&&!UE_BUILD_SHIPPING&&GetNetMode()==NM_Standalone&&IsValid(InTarget)&&InTarget->GetWorld()==GetWorld();
    if(bInitialized||!IsInGameThread()||(!bFixtureAuthorized&&!bTestAuthorized)||
        !GetWorld()||GetNetMode()!=NM_Standalone||!IsValid(InTarget)||InTarget==this||InTarget->GetWorld()!=GetWorld()||!Encounter||!Generation)
    {Error=TEXT("Framework.Boss.ProofAuthority");return false;}
    TUniquePtr<FRPGFrameworkDependencies> D;
    if(!RPGFramework::ResolveProfile(Profile,D,Error))return false;
    if(!InTarget->IsA(D->TargetClass.Get())){Error=TEXT("Framework.Boss.TargetClass");return false;}
    if(bTestAuthorized)
    {
        double MaxBack=0.,CurrentBack=0.;const double TestHealth=double(D->Profile->TargetHealth);
        if(!RPGPack::WriteMaxAttribute(InTarget,TEXT("Attribute.Health"),TestHealth)||!RPGPack::ReadAttribute(InTarget,TEXT("Attribute.Health"),true,MaxBack)||!FMath::IsNearlyEqual(MaxBack,TestHealth)
            ||!RPGPack::WriteAttribute(InTarget,TEXT("Attribute.Health"),TestHealth)||!RPGPack::ReadAttribute(InTarget,TEXT("Attribute.Health"),false,CurrentBack)||!FMath::IsNearlyEqual(CurrentBack,TestHealth))
        {Error=TEXT("Framework.Boss.TestTargetHealthInit");return false;}
    }
    Target=InTarget;TargetController=InTarget->GetController();ArenaOrigin=D->Profile->bArenaCenterAuthored?D->Profile->ArenaCenter:InTarget->GetActorLocation();
    if(!ValidateTarget(TargetHPBefore)){Target.Reset();Error=TEXT("Framework.Boss.TargetHealth");return false;}
    ExpectedTargetHP=TargetHPBefore;
    Dependencies=MoveTemp(D);ProofFixture=Fixture;bTestInitialized=bTestAuthorized;EncounterId=Encounter;GenerationId=Generation;
    if (Dependencies->Candidates.Num()>0)
    {
        FRPGBossSelectorConfig Config; Config.RepeatPenalty=Dependencies->Profile->RepeatPenalty; Config.RepeatMemory=Dependencies->Profile->RepeatMemory; Config.TieBand=Dependencies->Profile->SelectorTieBand; Config.TieSeed=Dependencies->Profile->SelectorTieSeed;
        TArray<FRPGBossSelectorCandidate> List;
        for (const auto& C:Dependencies->Candidates) {FRPGBossSelectorCandidate X; X.Card=C.Card; X.CooldownSeconds=C.CooldownSeconds; X.Weight=C.Weight; X.KiteMultiplier=C.KiteMultiplier; X.HugMultiplier=C.HugMultiplier; X.BackDodgeMultiplier=C.BackDodgeMultiplier; X.GreedMultiplier=C.GreedMultiplier; List.Add(X);}
        if (!Selector.Initialize(Config,List,Error)) {Fail(Error);return false;}
    }
    const auto& P=*Dependencies->Profile.Get();
    ComboGraph=RPGFramework::BuildComboGraph(*Dependencies->Profile.Get());bComboActive=false;ResetBleed();CurrentPhaseId=Dependencies->FirstCard()->Spec().PhaseId;bPhaseTwoLatched=false;Posture=double(Dependencies->Profile->PostureMax);LastPostureDrain=-1.;bStaggered=bStaggerAbortedAttack=false;StrafeDirFlip=1;StrafeStuck=RPGBossStuck::FStuck();YawProbeSampleIndex=0;PendingParryRecoverySeconds=ParryRecoveryUntil=0.;PendingParryRecoveryGrade=0;AggroBand=RPGBossAggro::EBand::Balanced;AggroDodgeTimes.Reset();FatigueWhiffs=0;bFatigueFinishedCardSeen=false;
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
    // F11: the clips play in the profile's slot node; refuse when the boss AnimBP has none of that name (same read-only graph check the executor uses for the cards).
    if((Dependencies->StaggerStart.IsValid()||Dependencies->PhaseTransition.IsValid())&&!RPGFramework::HasSlotNode(GetMesh()->GetAnimInstance(),P.AnimSlotName))
    {Error=TEXT("Framework.Profile.StaggerAnim.SlotNode");Fail(Error);return false;}
    SpawnDefaultController();auto* AI=Cast<ARPGFrameworkBossController>(GetController());
    if(!AI){Error=TEXT("Framework.Boss.Controller");Fail(Error);return false;}
    GetCharacterMovement()->MaxWalkSpeed=P.WalkSpeedCmPerSecond;GetCharacterMovement()->SetMovementMode(MOVE_Walking);
    StartedAt=GetWorld()->GetTimeSeconds();WalkStart=GetActorLocation();bInitialized=true;
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] dependencies mesh=%s skeleton=%s animClass=%s sequence=%s slot=%s resolved=1 label=%s"),*Dependencies->Mesh->GetPathName(),*Dependencies->FirstCard()->Spec().Skeleton.ToSoftObjectPath().ToString(),*Dependencies->AnimClass->GetPathName(),*Dependencies->FirstCard()->Spec().Sequence.ToSoftObjectPath().ToString(),*Dependencies->FirstCard()->Spec().SlotName.ToString(),*Dependencies->Profile->FixtureLabel.Replace(TEXT(" "),TEXT("_")));
    const double InitialRange=FVector::Dist2D(GetActorLocation(),InTarget->GetActorLocation());
    if(bTestAuthorized)
    {
        UNavigationSystemV1* Nav=FNavigationSystem::GetCurrent<UNavigationSystemV1>(GetWorld());FNavLocation SpawnProjected;
        const bool bSpawnProjected=Nav&&Nav->ProjectPointToNavigation(GetActorLocation(),SpawnProjected);
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] test_nav_probe system=%d spawnProjected=%d spawn=%s projected=%s projectionDeltaCm=%g"),
            Nav?1:0,bSpawnProjected?1:0,*GetActorLocation().ToCompactString(),bSpawnProjected?*SpawnProjected.Location.ToCompactString():TEXT("none"),
            bSpawnProjected?FVector::Dist(GetActorLocation(),SpawnProjected.Location):-1.);
    }
    if(bTestAuthorized&&CVarBossProofSkipInitialWalk.GetValueOnGameThread()>0&&GetCharacterMovement()->IsMovingOnGround()&&InitialRange>=P.BandMinCm&&InitialRange<=P.BandMaxCm)
    {
        // The test bridge may receive an explicitly positioned in-band target. Avoid issuing an unnecessary path request
        // whose later MoveFailed would deactivate an otherwise ready test actor before its requested card can start.
        bArrived=true;GetCharacterMovement()->StopMovementImmediately();AI->StopOwnedWalk();
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] test_walk_skipped reason=target_in_profile_band rangeCm=%g bandMin=%g bandMax=%g navSkipped=1"),InitialRange,P.BandMinCm,P.BandMaxCm);
        return true;
    }
    if(!AI->WalkToBand(this,Error)){Fail(Error);return false;}return true;
}
bool ARPGFrameworkBossCharacter::StartCardForTest(FName MoveId)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if(!bTestInitialized||!bInitialized||bFailed||bDead||bSucceeded||!Dependencies||!Executor||MoveId.IsNone()||!Executor->IsIdle())return false;
    int32 CardIndex=INDEX_NONE;
    for(int32 I=0;I<Dependencies->Candidates.Num();++I)
        if(Dependencies->Candidates[I].Card.IsValid()&&Dependencies->Candidates[I].Card->Spec().MoveId==MoveId){CardIndex=I;break;}
    if(CardIndex==INDEX_NONE)return false;
    double TargetMax=0.,TargetHealth=0.;
    if(!RPGPack::ReadAttribute(Target.Get(),TEXT("Attribute.Health"),true,TargetMax)||!FMath::IsFinite(TargetMax)||TargetMax<=0.
        ||!RPGPack::WriteAttribute(Target.Get(),TEXT("Attribute.Health"),TargetMax)||!RPGPack::ReadAttribute(Target.Get(),TEXT("Attribute.Health"),false,TargetHealth)||!FMath::IsNearlyEqual(TargetHealth,TargetMax))return false;
    TargetHPBefore=ExpectedTargetHP=TargetHealth;
    if(bHittable)Health=MaxHealth;
    if(PostureEnabled()){Posture=Dependencies->Profile->PostureMax;LastPostureDrain=-1.;bStaggered=false;}
    if(Executor->DidFinish()&&!Executor->PrepareNextAttack())return false;
    const FRPGBossDecisionSnapshot Snapshot=MakeSnapshot();FString Error;
    if(!Executor->StartCard(Dependencies->Candidates[CardIndex].Card,Snapshot,Error))return false;
    bComboActive=false;bComboPausing=false;ComboPendingCard=INDEX_NONE;
    bStartedMove=true;bFatigueFinishedCardSeen=false;
    Selector.NoteStarted(CardIndex,Snapshot.ClockSeconds);
    ComboHitsAtStart=Executor->AcceptedHits();ComboGuardedAtStart=Executor->GuardedHits();ComboParriedAtStart=Executor->ParriedHits();
    return true;
#endif
}
bool ARPGFrameworkBossCharacter::StartComboForTest(FName RootMoveId)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if(!bTestInitialized||!bInitialized||bFailed||bDead||bSucceeded||!Dependencies||!Executor||RootMoveId.IsNone()||!Executor->IsIdle())return false;
    const int32 RootIndex=RPGBossCombo::FindNode(ComboGraph,ComboGraph.Root);
    if(RootIndex==INDEX_NONE||ComboGraph.Nodes[RootIndex].MoveId!=RootMoveId)return false;
    int32 CardIndex=INDEX_NONE;
    for(int32 I=0;I<Dependencies->Candidates.Num();++I)
        if(Dependencies->Candidates[I].Card.IsValid()&&Dependencies->Candidates[I].Card->Spec().MoveId==RootMoveId){CardIndex=I;break;}
    if(CardIndex==INDEX_NONE)return false;
    double TargetMax=0.,TargetHealth=0.;
    if(!RPGPack::ReadAttribute(Target.Get(),TEXT("Attribute.Health"),true,TargetMax)||!FMath::IsFinite(TargetMax)||TargetMax<=0.
        ||!RPGPack::WriteAttribute(Target.Get(),TEXT("Attribute.Health"),TargetMax)||!RPGPack::ReadAttribute(Target.Get(),TEXT("Attribute.Health"),false,TargetHealth)||!FMath::IsNearlyEqual(TargetHealth,TargetMax))return false;
    TargetHPBefore=ExpectedTargetHP=TargetHealth;
    if(bHittable)Health=MaxHealth;
    if(PostureEnabled()){Posture=Dependencies->Profile->PostureMax;LastPostureDrain=-1.;bStaggered=false;}
    if(Executor->DidFinish()&&!Executor->PrepareNextAttack())return false;
    // This hook starts an isolated test combo after any standalone test cards;
    // those cards must not consume the profile's per-combo attack budget.
    AttacksDone=0;
    ComboState=RPGBossCombo::FComboState();ComboState.Node=ComboGraph.Root;bComboActive=true;bComboPausing=false;ComboPendingCard=INDEX_NONE;
    const FRPGBossDecisionSnapshot Snapshot=MakeSnapshot();FString Error;
    if(!Executor->StartCard(Dependencies->Candidates[CardIndex].Card,Snapshot,Error)){bComboActive=false;return false;}
    bStartedMove=true;bFatigueFinishedCardSeen=false;Selector.NoteStarted(CardIndex,Snapshot.ClockSeconds);
    ComboHitsAtStart=Executor->AcceptedHits();ComboGuardedAtStart=Executor->GuardedHits();ComboParriedAtStart=Executor->ParriedHits();
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] combo_test_start node=%s move=%s depth=%d attackBudgetReset=1"),*ComboState.Node.ToString(),*RootMoveId.ToString(),ComboState.Depth);
    return true;
#endif
}
bool ARPGFrameworkBossCharacter::ValidateTarget(double& HP) const {return TargetFault(HP).IsNone();}
double ARPGFrameworkBossCharacter::FloorSeparationCm() const
{
    float Radius=0.f,BossHalf=0.f,TargetHalf=0.f; GetSimpleCollisionCylinder(Radius,BossHalf); Target->GetSimpleCollisionCylinder(Radius,TargetHalf);
    return FMath::Abs((double(Target->GetActorLocation().Z)-double(TargetHalf))-(double(GetActorLocation().Z)-double(BossHalf)));
}
FName ARPGFrameworkBossCharacter::TargetFault(double& HP) const
{
    HP=0.;
    if(!TargetController.IsValid()||!Target.IsValid())return TEXT("Invalid");
    if(Target->IsActorBeingDestroyed())return TEXT("Destroyed");
    if(Target->GetController()!=TargetController.Get()||TargetController->GetPawn()!=Target.Get()||Target->GetWorld()!=GetWorld())return TEXT("Invalid");
    const URPGBossFrameworkProfile* P=ProofProfile();
    if(P&&RPGBossLeashRules::IsOutsideArena(Target->GetActorLocation(),ArenaOrigin,double(P->ArenaRadiusCm)))return TEXT("OffArena");
    if(!RPGPack::ReadAttribute(Target.Get(),TEXT("Attribute.Health"),false,HP)||!FMath::IsFinite(HP))return TEXT("Unreadable");
    return HP>0.?FName(NAME_None):FName(TEXT("Dead"));
}
void ARPGFrameworkBossCharacter::TickDodge()
{
    // BOSS-AWR-008: a dodge is the rise of the target's flat speed to the profile threshold; its direction (seen from the boss) goes into the history ring.
    const auto& P=*Dependencies->Profile.Get();
    if((P.DodgeHistoryDepth<1&&!P.bAggroEnabled)||!Target.IsValid())return;
    const FVector V=Target->GetVelocity();const bool bFast=FVector(V.X,V.Y,0.).Size()>=double(P.DodgeSpeedCm);const double Now=GetWorld()->GetTimeSeconds();
    if(bFast&&!bDodgeWasFast&&Now-DodgeSeenAt>.5)
    {
        const RPGBossTrack::EDodgeDir Dir=RPGBossTrack::ClassifyDodge(V,Target->GetActorLocation()-GetActorLocation(),P.DodgeSpeedCm);
        if(Dir!=RPGBossTrack::EDodgeDir::None)
        {
            DodgeSeenAt=Now;++DodgesSeen;DodgeHistory.Push(Dir,P.DodgeHistoryDepth);if(P.bAggroEnabled)AggroDodgeTimes.Add(Now);
            UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] dodge_observed n=%d direction=%s speedCm=%g back=%d depth=%d"),DodgesSeen,Dir==RPGBossTrack::EDodgeDir::Back?TEXT("Back"):Dir==RPGBossTrack::EDodgeDir::Forward?TEXT("Forward"):TEXT("Side"),FVector(V.X,V.Y,0.).Size(),DodgeHistory.BackCount(),DodgeHistory.Dirs.Num());
        }
    }
    bDodgeWasFast=bFast;
}
void ARPGFrameworkBossCharacter::TickLos()
{
    // BOSS-AWR-007: one visibility trace per tick from the boss to the target (both actors ignored); the memory rule reports the moment sight is lost / regained / the search times out.
    const auto& P=*Dependencies->Profile.Get();
    if(!(P.LosSearchSeconds>0.f)||!Target.IsValid()||bLeashed)return;
    FHitResult Hit;FCollisionQueryParams Params(SCENE_QUERY_STAT(BossLos),false,this);Params.AddIgnoredActor(Target.Get());
    const bool bBlocked=GetWorld()->LineTraceSingleByChannel(Hit,GetActorLocation(),Target->GetActorLocation(),ECC_Visibility,Params);
    const double Now=GetWorld()->GetTimeSeconds();
    switch(RPGBossTrack::LosStep(Los,!bBlocked,Now,double(P.LosSearchSeconds),Target->GetActorLocation()))
    {
    case RPGBossTrack::ELosEvent::Lost: UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] los_lost lastKnownX=%g lastKnownY=%g blocker=%s"),Los.LastKnown.X,Los.LastKnown.Y,Hit.GetActor()?*Hit.GetActor()->GetName():TEXT("None"));break;
    case RPGBossTrack::ELosEvent::Regained: UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] los_regained lostForSeconds=%g"),Now-Los.LostAt);break;
    case RPGBossTrack::ELosEvent::TimedOut: UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] los_search_timeout seconds=%g"),Now-Los.LostAt);break;
    default:break;
    }
}
void ARPGFrameworkBossCharacter::TickActivity()
{
    // BOSS-AWR-006: what the boss reads from the player: a flask drink (after the boss's reaction delay when the profile has one, else at once) or a heavy attack in progress (the player's swing tracker knows the kind of the swing,
    // the animation instance whether its montage is still playing). Read only when a card of the profile has a greed multiplier, so every other profile is unchanged.
    bool bWanted=false; for(const auto& C:Dependencies->Candidates) if(!FMath::IsNearlyEqual(C.GreedMultiplier,1.f)) {bWanted=true;break;}
    if(!bWanted||!Target.IsValid()) {Activity=RPGBossTrack::EPlayerActivity::None;return;}
    const auto& P=*Dependencies->Profile.Get();
    const ACharacter* Player=Cast<ACharacter>(Target.Get()); UAnimInstance* PA=Player&&Player->GetMesh()?Player->GetMesh()->GetAnimInstance():nullptr;
    bool bFlask=false;
    if(P.ReactionDelayMinSeconds>0.f) bFlask=bFlaskKnown;
    else
    {
        if(!DrinkMontage.IsValid()) DrinkMontage=LoadObject<UAnimMontage>(nullptr,TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/DrinkingPotion_Montage.DrinkingPotion_Montage"));
        bFlask=PA&&DrinkMontage.IsValid()&&PA->Montage_IsPlaying(DrinkMontage.Get());
    }
    bool bHeavy=false; ERPGAttackKind Kind=ERPGAttackKind::Unknown;
    if(const URPGSwingTracker* Tracker=Target->FindComponentByClass<URPGSwingTracker>())
    {
        const FRPGSwing& Swing=Tracker->GetCurrentSwing(); const UAnimMontage* Playing=PA?PA->GetCurrentActiveMontage():nullptr;
        if(Swing.IsAttack()&&Playing&&Playing->GetFName()==Swing.Montage) {Kind=Swing.Kind; bHeavy=RPGBossTrack::IsHeavyAttackKind(Kind);}
    }
    // Every attack swing in progress is logged on its edges (the proof that a LIGHT swing was running and did not count).
    if(Kind!=SwingKindSeen) {UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] player_swing from=%s to=%s heavy=%d"),RPGAttackKindName(SwingKindSeen),RPGAttackKindName(Kind),bHeavy?1:0); SwingKindSeen=Kind;}
    const RPGBossTrack::EPlayerActivity Now=RPGBossTrack::ClassifyPlayerActivity(bFlask,bHeavy);
    if(Now!=Activity)
    {
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] player_activity from=%s to=%s attackKind=%s"),RPGBossTrack::PlayerActivityName(Activity),RPGBossTrack::PlayerActivityName(Now),RPGAttackKindName(Kind));
        Activity=Now;
    }
}
void ARPGFrameworkBossCharacter::TickFlask()
{
    // BOSS-SEL-009: the boss PERCEIVES a flask drink at the edge of the target's DrinkingPotion montage (the same signal the legacy heal punish uses), and may REACT only after a seeded delay inside the profile window.
    const auto& P=*Dependencies->Profile.Get();
    if(P.ReactionDelayMinSeconds<=0.f||!Target.IsValid())return;
    const ACharacter* Drinker=Cast<ACharacter>(Target.Get());UAnimInstance* DA=Drinker&&Drinker->GetMesh()?Drinker->GetMesh()->GetAnimInstance():nullptr;
    if(!DrinkMontage.IsValid())DrinkMontage=LoadObject<UAnimMontage>(nullptr,TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/DrinkingPotion_Montage.DrinkingPotion_Montage"));
    const bool bPlaying=DA&&DrinkMontage.IsValid()&&DA->Montage_IsPlaying(DrinkMontage.Get());
    const double Now=GetWorld()->GetTimeSeconds();
    if(bPlaying&&!bDrinkWasPlaying)
    {
        const double Latency=RPGBossTrack::ReactionDelaySeconds(P.ReactionDelayMinSeconds,P.ReactionDelayMaxSeconds,P.ReactionSeed,FlaskPerceivedCount);
        ++FlaskPerceivedCount;bFlaskPending=true;bFlaskKnown=false;FlaskPerceivedAt=Now;FlaskReactAt=Now+Latency;
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] flask_perceived count=%d latencySeconds=%g windowMin=%g windowMax=%g"),FlaskPerceivedCount,Latency,double(P.ReactionDelayMinSeconds),double(P.ReactionDelayMaxSeconds));
    }
    if(bFlaskPending&&Now>=FlaskReactAt)
    {
        bFlaskPending=false;bFlaskKnown=true;
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] flask_reaction count=%d measuredSeconds=%g windowMin=%g windowMax=%g"),FlaskPerceivedCount,Now-FlaskPerceivedAt,double(P.ReactionDelayMinSeconds),double(P.ReactionDelayMaxSeconds));
    }
    if(!bPlaying&&bDrinkWasPlaying){bFlaskPending=false;bFlaskKnown=false;UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] flask_end count=%d"),FlaskPerceivedCount);}
    bDrinkWasPlaying=bPlaying;
}
void ARPGFrameworkBossCharacter::HandleLeash()
{
    const auto& P=*Dependencies->Profile.Get();auto* AI=Cast<ARPGFrameworkBossController>(GetController());
    if(!bLeashed)
    {
        bLeashed=true;bLeashAtCenter=false;
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] arena_leash state=Start targetDistanceCm=%g radiusCm=%g centerX=%g centerY=%g"),FVector::Dist2D(Target->GetActorLocation(),ArenaOrigin),double(P.ArenaRadiusCm),ArenaOrigin.X,ArenaOrigin.Y);
        if(bStartedMove&&!Executor->DidFinish())
        {
            Executor->Abort(TEXT("ArenaLeash"));
            if(!Executor->RecoverAfterAbort()){Fail(TEXT("Framework.Playback.LeashRecover"));return;}
            bStartedMove=false;if(bComboActive){bComboActive=false;UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] combo_end reason=ArenaLeash"));}
        }
        if(AI)AI->StopOwnedWalk();GetCharacterMovement()->StopMovementImmediately();
        if(AI)AI->MoveToLocation(ArenaOrigin,P.AcceptanceCm,false,true,true,false);
    }
    else if(!bLeashAtCenter&&FVector::Dist2D(GetActorLocation(),ArenaOrigin)<=double(P.AcceptanceCm)+30.)
    {
        bLeashAtCenter=true;GetCharacterMovement()->StopMovementImmediately();
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] arena_leash state=AtCenter distanceCm=%g"),FVector::Dist2D(GetActorLocation(),ArenaOrigin));
    }
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
    if(bParryReactionPending){bParryReactionPending=false;const double GradeScale=PendingParryReactionScale;PendingParryReactionScale=0.;if(Dependencies&&Dependencies->Profile&&Dependencies->Profile->ParryPostureAmount>0.f){const double Amount=double(Dependencies->Profile->ParryPostureAmount)*GradeScale;UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] parry_reaction posture=%g"),Amount);ApplyHit(0.,Amount,0.);}}
#if !UE_BUILD_SHIPPING
    if(ProofShiftStart>=0.&&ProofShiftsDone<ProofShifts.Num()&&Target.IsValid()&&GetWorld()->GetTimeSeconds()-ProofShiftStart>=ProofShifts[ProofShiftsDone].Key)
    {
        const FVector Move=ProofShifts[ProofShiftsDone].Value;Target->SetActorLocation(Target->GetActorLocation()+Move,false,nullptr,ETeleportType::TeleportPhysics);
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] target_shift_injected n=%d dx=%g dy=%g dz=%g"),ProofShiftsDone+1,Move.X,Move.Y,Move.Z);++ProofShiftsDone;
    }
#endif
    double HP=0.;const FName Fault=(ProofFixture.IsValid()||bTestInitialized)?TargetFault(HP):FName(TEXT("Invalid"));const bool bTargetOk=Fault.IsNone();
    // BOSS-MOV-005: a leashing profile does not fail when the target leaves the arena: the boss goes home and waits, and resumes when the target is back.
    if(Fault==FName(TEXT("OffArena"))&&Dependencies->Profile->bArenaLeash){HandleLeash();return;}
    if(bLeashed&&bTargetOk)
    {
        const bool bWasAtCenter=bLeashAtCenter;bLeashed=false;bLeashAtCenter=false;FString WalkError;auto* AI=Cast<ARPGFrameworkBossController>(GetController());
        if(AI)AI->StopMovement();bArrived=false;StartedAt=GetWorld()->GetTimeSeconds();
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] arena_leash state=Resume bossDistanceToCenterCm=%g atCenter=%d"),FVector::Dist2D(GetActorLocation(),ArenaOrigin),bWasAtCenter?1:0);
        if(!AI||!AI->WalkToBand(this,WalkError)){Fail(WalkError.IsEmpty()?FString(TEXT("Framework.Boss.Controller")):WalkError);return;}
    }
    if(!bTargetOk||!FMath::IsNearlyEqual(HP,ExpectedTargetHP))
    {
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] target_health_mismatch valid=%d actual=%g expected=%g generation=%llu reason=%s"),bTargetOk?1:0,HP,ExpectedTargetHP,GenerationId,bTargetOk?TEXT("HealthChanged"):*Fault.ToString());
        Fail(TEXT("Framework.Boss.TargetLifeOrHealthChanged"));return;
    }
    const auto& P=*Dependencies->Profile.Get();
#if !UE_BUILD_SHIPPING
    if(ProofGStart>=0.&&Target.IsValid())
    {
        // BOSS-COM-004 / HIT-008: the REAL guard input of the pack's player, driven on the game clock, and the guard tags it produces, logged every tick (the observer reads exactly these tags).
        const double Since=GetWorld()->GetTimeSeconds()-ProofGStart; APlayerController* GPC=Cast<APlayerController>(Cast<APawn>(Target.Get())->GetController());
        if(Since<=double(CVarBossProofPlayerGuardSeconds.GetValueOnGameThread())&&GPC)
        {
            const int32 RawMode=CVarBossProofPlayerGuard.GetValueOnGameThread(); const bool bToggle=RawMode>=3; const int32 Mode=RawMode==5?1:(RawMode==6?0:(bToggle?RawMode-2:RawMode));   // 3 / 4 = the same as 1 / 2 after a tap of the toggle-combat input (weapon drawn) in the first 0.12 s; 5 = 3 plus a tap of IA_Parry every 0.5 s while the block is held
            const float RequestedGuardPhase=CVarBossProofPlayerGuardPhaseSeconds.GetValueOnGameThread(); const double PhaseLimit=double(std::numeric_limits<float>::max());
            const double GuardPhase=FMath::IsFinite(RequestedGuardPhase)?FMath::Clamp(double(RequestedGuardPhase),-PhaseLimit,PhaseLimit):0.;
            if(bToggle&&Since<=.12) if(UInputAction* TA=LoadObject<UInputAction>(nullptr,TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_ToggleCombat.IA_ToggleCombat")))URPGInputTestUtils::InjectAction(GPC,TA,FVector(1.,0.,0.));
            const TCHAR* Asset=Mode==2?TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_Parry.IA_Parry"):TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_Block.IA_Block");
            if(Mode>0&&Since>(bToggle?.5:0.)&&(Mode==1||RPGBossGuard::IsProofParryPulse(Since,GuardPhase))) if(UInputAction* IA=LoadObject<UInputAction>(nullptr,Asset))URPGInputTestUtils::InjectAction(GPC,IA,FVector(1.,0.,0.));
            if(RawMode==6&&Since>.5&&Executor&&Executor->OpenWindowCount()>0) if(UInputAction* PerfectParry=LoadObject<UInputAction>(nullptr,TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_Parry.IA_Parry")))URPGInputTestUtils::InjectAction(GPC,PerfectParry,FVector(1.,0.,0.));   // 6 = toggle combat, then press the parry while a boss hit window is open (perfect timing)
            if(RawMode==5&&Since>.5&&RPGBossGuard::IsProofParryPulse(Since,GuardPhase)) if(UInputAction* PA=LoadObject<UInputAction>(nullptr,TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_Parry.IA_Parry")))URPGInputTestUtils::InjectAction(GPC,PA,FVector(1.,0.,0.));
            UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] guard_tags since=%.4f statusBlocking=%d stateBlocking=%d abilityParry=%d abilityBlock=%d statusParryActive=%d hasParryAbility=%d hasGuardAbility=%d"),Since,RPGBossDamage::HasTag(Target.Get(),TEXT("Status.Blocking"))?1:0,RPGBossDamage::HasTag(Target.Get(),TEXT("State.Blocking"))?1:0,RPGBossDamage::HasTag(Target.Get(),TEXT("Ability.Parry"))?1:0,RPGBossDamage::HasTag(Target.Get(),TEXT("Ability.Block"))?1:0,RPGBossDamage::HasTag(Target.Get(),TEXT("Status.ParryActive"))?1:0,RPGPack::FindAbilityByClassName(Target.Get(),TEXT("GA_PlayerParry_C"))?1:0,RPGPack::FindAbilityByClassName(Target.Get(),TEXT("GA_PlayerGuardBlock_C"))?1:0);
        }
        else if(ProofGStart>=0.){UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] guard_hook_end"));ProofGStart=-2.;}
    }
    if(ProofIFStart>=0.&&Target.IsValid())
    {
        // BOSS-HIT-009: the press of the REAL dodge input on the game clock, then one probe per tick through the damage resolver (the path every boss hit takes): the player's invulnerability window, measured.
        const double Now=GetWorld()->GetTimeSeconds(); APlayerController* IFPC=Cast<APlayerController>(Cast<APawn>(Target.Get())->GetController());
        if(!bProofIFPressed&&Now-ProofIFStart>=double(CVarBossProofIFrameSweep.GetValueOnGameThread()))
        {
            bProofIFPressed=true;ProofIFPressAt=Now;
            UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] iframe_sweep_press t=%.4f sinceFirstAttack=%.4f"),Now,Now-ProofIFStart);
        }
        if(bProofIFPressed&&IFPC)
        {
            const double Since=Now-ProofIFPressAt;
            if(Since<=.12)
            {
                static const TCHAR* DodgeAsset=TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_Dodge.IA_Dodge");
                if(UInputAction* IA=LoadObject<UInputAction>(nullptr,DodgeAsset))URPGInputTestUtils::InjectAction(IFPC,IA,FVector(1.,0.,0.));
            }
            if(Since<=1.2)
            {
                if(URPGDamageResolver* R=URPGDamageResolver::FindOrAdd(this))
                {
                    FRPGDamagePayload Payload;Payload.MoveId=TEXT("IFrameProbe");Payload.AttackInstance=9000+ProofIFProbes;Payload.Generation=GenerationId;Payload.HitKey=FName(*FString::Printf(TEXT("IFProbe_%d"),ProofIFProbes));Payload.HPDamage=1.f;
                    const FRPGDamageResult Result=R->Resolve(Target.Get(),Payload);
                    if(Result.Outcome==ERPGDamageOutcome::Accepted)NoteDamageApplied(Result.HPApplied);   // the boss's own accounting of the target's health, as for every hit it lands
                    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] iframe_probe n=%d sinceDodgePress=%.4f outcome=%s hpApplied=%g"),ProofIFProbes,Since,*UEnum::GetValueAsString(Result.Outcome),Result.HPApplied);
                }
                ++ProofIFProbes;
            }
            else if(ProofIFStart>=0.){UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] iframe_sweep_end probes=%d"),ProofIFProbes);ProofIFStart=-2.;}
        }
    }
    if(ProofHitStart>=0.&&ProofHitsDone<ProofHitOffsets.Num()&&GetWorld()->GetTimeSeconds()-ProofHitStart>=ProofHitOffsets[ProofHitsDone])
    {
        URPGHitIntake* Intake=Target.IsValid()?Target->FindComponentByClass<URPGHitIntake>():nullptr;
        if(Intake)Intake->InjectBossHitForTest(this);
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] player_hit_injected n=%d offset=%g ok=%d"),ProofHitsDone+1,ProofHitOffsets[ProofHitsDone],Intake?1:0);
        ++ProofHitsDone;
    }
#endif
#if !UE_BUILD_SHIPPING
    if(ProofDrinkStart>=0.&&ProofDrinksDone<ProofDrinkOffsets.Num()&&GetWorld()->GetTimeSeconds()-ProofDrinkStart>=ProofDrinkOffsets[ProofDrinksDone])
    {
        const ACharacter* Drinker=Cast<ACharacter>(Target.Get());UAnimInstance* DA=Drinker&&Drinker->GetMesh()?Drinker->GetMesh()->GetAnimInstance():nullptr;
        if(!DrinkMontage.IsValid())DrinkMontage=LoadObject<UAnimMontage>(nullptr,TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/DrinkingPotion_Montage.DrinkingPotion_Montage"));
        const float Len=(DA&&DrinkMontage.IsValid())?DA->Montage_Play(DrinkMontage.Get()):0.f;
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] player_drink_started n=%d offset=%g ok=%d length=%g"),ProofDrinksDone+1,ProofDrinkOffsets[ProofDrinksDone],Len>0.f?1:0,Len);++ProofDrinksDone;
    }
#endif
#if !UE_BUILD_SHIPPING
    if(ProofDodgeStart>=0.&&ProofDodgesDone<ProofDodges.Num()&&Target.IsValid()&&GetWorld()->GetTimeSeconds()-ProofDodgeStart>=ProofDodges[ProofDodgesDone].Key)
    {
        ACharacter* Dodger=Cast<ACharacter>(Target.Get());FVector Away=Target->GetActorLocation()-GetActorLocation();Away.Z=0.;Away.Normalize();
        const bool bBack=ProofDodges[ProofDodgesDone].Value;if(Dodger)Dodger->LaunchCharacter(Away*(bBack?1.:-1.)*900.,true,false);
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] player_dodge_started n=%d offset=%g direction=%s ok=%d"),ProofDodgesDone+1,ProofDodges[ProofDodgesDone].Key,bBack?TEXT("Back"):TEXT("Forward"),Dodger?1:0);++ProofDodgesDone;
    }
#endif
    TickDodge();
    TickFlask();
    TickActivity();
    TickLos();
    // BOSS-EXE-007: the executor's watchdog aborted the running card (end notification dropped / montage stuck): recover and decide again, never stall.
    if(Executor->WatchdogFired())
    {
        if(!Executor->RecoverAfterAbort()){Fail(TEXT("Framework.Playback.WatchdogRecover"));return;}
        bStartedMove=false; if(bComboActive){bComboActive=false;UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] combo_end reason=Watchdog"));}
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] watchdog_recovered attacksDone=%d"),AttacksDone);
    }
    TickOverlay();
    if(!bArrived&&GetWorld()->GetTimeSeconds()-StartedAt>P.WalkTimeoutSeconds){Fail(TEXT("Framework.Nav.Timeout"));return;}
    if(PostureEnabled())
    {
        if(bStaggered)
        {
            GetCharacterMovement()->StopMovementImmediately();
            // BOSS-EXE-005: a phase threshold crossed while down supersedes the stagger: it ends now, and the neutral phase gate below starts the transition in this same tick.
            RPGBossRules::FFlags NoFlags;
            if(P.bPhaseSupersedesStagger&&bHittable&&P.PhaseTwoFraction>0.f&&!bPhaseTwoLatched&&RPGBossRules::ResolveTransition(NoFlags,Health,MaxHealth,P.PhaseTwoFraction)==RPGBossRules::ETransitionResult::Start)
            {
                UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] stagger_superseded reason=PhaseTransition health=%g max=%g fraction=%g"),Health,MaxHealth,double(P.PhaseTwoFraction));
                StopF11Clip();EndStagger();if(bFailed)return;
            }
            else
            {
                TickStaggerAnim();
                if(GetWorld()->GetTimeSeconds()>=StaggerEndsAt)EndStagger();
                return;   // no selection while down
            }
        }
        const float Before=float(Posture); Posture=RPGBossMath::RegenStep(float(Posture),P.PostureMax,GetWorld()->GetTimeSeconds(),LastPostureDrain,P.PostureRegenDelaySeconds,P.PostureRegenPerSecond,Delta);
        if(float(Posture)>Before+KINDA_SMALL_NUMBER&&!bPostureRegenLogged){bPostureRegenLogged=true;UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] posture_regen_start posture=%g sinceLastDrainSeconds=%g delaySeconds=%g perSecond=%g"),double(Before),GetWorld()->GetTimeSeconds()-LastPostureDrain,double(P.PostureRegenDelaySeconds),double(P.PostureRegenPerSecond));}
        if(float(Posture)>Before+KINDA_SMALL_NUMBER&&FMath::IsNearlyEqual(float(Posture),P.PostureMax)){UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] posture_regen_full posture=%g max=%g"),Posture,double(P.PostureMax));}
    }
    if(bArrived&&!bStartedMove&&!bTestInitialized)
    {
        // BOSS-AWR-007: no sight of the target (a pillar): no decision, no blind strike: search where it was last seen, go back to the band when it is seen again.
        if(P.LosSearchSeconds>0.f)
        {
            auto* LosAI=Cast<ARPGFrameworkBossController>(GetController());
            if(Los.bLost)
            {
                if(!bLosWalking){bLosWalking=true;if(LosAI)LosAI->MoveToLocation(Los.LastKnown,P.AcceptanceCm,false,true,true,false);UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] los_search_start x=%g y=%g"),Los.LastKnown.X,Los.LastKnown.Y);}
                return;
            }
            if(bLosWalking)
            {
                bLosWalking=false;FString WalkError;if(LosAI)LosAI->StopMovement();bArrived=false;StartedAt=GetWorld()->GetTimeSeconds();
                UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] los_resume"));
                if(!LosAI||!LosAI->WalkToBand(this,WalkError)){Fail(WalkError.IsEmpty()?FString(TEXT("Framework.Boss.Controller")):WalkError);}
                return;
            }
        }
        // F11: while the phase transition clip plays the selector is held for the clip length, then phase two selection starts in this tick.
        if(bPhaseHold)
        {
            GetCharacterMovement()->StopMovementImmediately();
            if(RPGStaggerAnim::PhaseHoldActive(Dependencies->PhaseTransition->GetPlayLength(),float(GetWorld()->GetTimeSeconds()-PhaseHoldStartedAt)))return;
            bPhaseHold=false;F11Montage.Reset();
            UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] phase_anim state=Finished phase=%s"),*CurrentPhaseId.ToString());
        }
        // F6c phase gate: only here (neutral, nothing playing), the pure legacy rule decides; the phase latches until restart.
        if(bHittable&&P.PhaseTwoFraction>0.f&&!bPhaseTwoLatched)
        {
            RPGBossRules::FFlags Flags;
            if(RPGBossRules::ResolveTransition(Flags,Health,MaxHealth,P.PhaseTwoFraction)==RPGBossRules::ETransitionResult::Start)
            {
                bPhaseTwoLatched=true;
                UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] phase_transition attack=%d from=%s to=%s health=%g max=%g fraction=%g"),AttacksDone+1,*CurrentPhaseId.ToString(),*P.PhaseTwoId.ToString(),Health,MaxHealth,double(P.PhaseTwoFraction));
                const FName FromPhase=CurrentPhaseId;
                CurrentPhaseId=P.PhaseTwoId;
                FatigueWhiffs=0;bFatigueFinishedCardSeen=false;
                if(Dependencies->PhaseTransition.IsValid())
                {
                    // F11: play the transition clip and hold the selector for its length (no clip = no hold, as before).
                    PhaseHoldStartedAt=GetWorld()->GetTimeSeconds();bPhaseHold=true;GetCharacterMovement()->StopMovementImmediately();
                    if(!PlayF11Clip(Dependencies->PhaseTransition.Get(),1)){Fail(TEXT("Framework.Playback.PhaseAnim"));return;}
                    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] phase_anim state=Triggered sequence=%s slot=%s length=%g from=%s to=%s"),*Dependencies->PhaseTransition->GetName(),*P.AnimSlotName.ToString(),double(Dependencies->PhaseTransition->GetPlayLength()),*FromPhase.ToString(),*CurrentPhaseId.ToString());
                    return;
                }
            }
        }
        const FVector D=Target->GetActorLocation()-GetActorLocation();FRPGBossDecisionSnapshot S;
        S.EncounterId=EncounterId;S.Generation=GenerationId;S.TargetId=uint64(Target->GetUniqueID());S.FrameId=GFrameCounter;
        S.PhaseId=CurrentPhaseId;S.ClockSeconds=GetWorld()->GetTimeSeconds();S.RangeCm=D.Size2D();
        S.SignedYawDegrees=FMath::FindDeltaAngleDegrees(GetActorRotation().Yaw,D.Rotation().Yaw);S.VerticalDeltaCm=FloorSeparationCm();S.bTargetValid=S.bNeutral=true;
        GetCharacterMovement()->StopMovementImmediately();FString Error;
        if(Dependencies->Candidates.Num()>0)
        {
            FRPGBossSelectorDecision Decision;
#if !UE_BUILD_SHIPPING
            const float YawProbeAmplitude=CVarBossProofYawProbe.GetValueOnGameThread();
            if(FMath::IsFinite(YawProbeAmplitude)&&YawProbeAmplitude>0.f)
            {
                const int32 Sample=YawProbeSampleIndex++;
                const double Center=double(Dependencies->Candidates[0].Card->Spec().FrontConeDegrees)*.5;
                S.SignedYawDegrees=RPGBossYawProbe::YawAt(Sample,Center,double(YawProbeAmplitude),24);
                UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] yaw_probe sample=%d yaw=%g"),Sample,S.SignedYawDegrees);
            }
#endif
            // BOSS-PHS-005: the pattern of the target at this decision: N consecutive chosen decisions (this one included) with the range beyond / inside the profile's thresholds.
            FRPGBossSelectorContext Pattern;
            Pattern.ConeHysteresisDegrees=double(P.ConeHysteresisDegrees);   // BOSS-AWR-004: 0 = off, the cone filter is exactly the old one
            if(P.bAggroEnabled)
            {
                RPGBossAggro::FConfig AggroConfig;AggroConfig.EnterCloseCm=P.AggroEnterCloseCm;AggroConfig.ExitCloseCm=P.AggroExitCloseCm;AggroConfig.EnterFarCm=P.AggroEnterFarCm;AggroConfig.ExitFarCm=P.AggroExitFarCm;
                AggroConfig.EnterDodgeRate=P.AggroDodgeEnterRate;AggroConfig.ExitDodgeRate=P.AggroDodgeExitRate;AggroConfig.DodgeRateWindowSeconds=P.AggroDodgeWindowSeconds;
                const double Now=GetWorld()->GetTimeSeconds();AggroDodgeTimes.RemoveAll([Now,&P](double T){return T<Now-double(P.AggroDodgeWindowSeconds);});
                const double DodgeRate=double(AggroDodgeTimes.Num())/double(P.AggroDodgeWindowSeconds);const RPGBossAggro::EBand PreviousBand=AggroBand;
                AggroBand=RPGBossAggro::Step(AggroBand,S.RangeCm,false,false,DodgeRate,AggroConfig);Pattern.PreferredAggroBand=AggroBand;
                if(AggroBand!=PreviousBand)UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] aggro_switch from=%d to=%d"),static_cast<int32>(PreviousBand),static_cast<int32>(AggroBand));
            }
            if(P.AntiCheeseKiteRangeCm>0.f&&S.RangeCm>=double(P.AntiCheeseKiteRangeCm)&&KiteStreak+1>=P.AntiCheeseStreak) Pattern.bKiting=true;
            if(P.AntiCheeseHugRangeCm>0.f&&S.RangeCm<=double(P.AntiCheeseHugRangeCm)&&HugStreak+1>=P.AntiCheeseStreak) Pattern.bHugging=true;
            if(P.DodgeHistoryDepth>0&&DodgeHistory.BackCount()>=P.DodgeBackThreshold) Pattern.bBackDodging=true;   // BOSS-AWR-008
            if(Activity!=RPGBossTrack::EPlayerActivity::None) Pattern.bGreedy=true;   // BOSS-AWR-006
            const bool bAsked=Selector.Select(Executor->Model(),S,Decision,Pattern);const int32 Seq=++DecisionSeq;
            if(Pattern.ConeHysteresisDegrees>0.) UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] cone_hysteresis degrees=%g seq=%d"),Pattern.ConeHysteresisDegrees,Seq);   // BOSS-AWR-004
            if(Pattern.bGreedy) UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] greed_pattern state=Greedy source=%s seq=%d"),RPGBossTrack::PlayerActivityName(Activity),Seq);
            if(Pattern.bBackDodging) UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] dodge_pattern state=BackDodging back=%d depth=%d threshold=%d seq=%d"),DodgeHistory.BackCount(),DodgeHistory.Dirs.Num(),P.DodgeBackThreshold,Seq);
            if(Pattern.bKiting||Pattern.bHugging) UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] anticheese state=%s streak=%d rangeCm=%g thresholdCm=%g seq=%d"),Pattern.bKiting?TEXT("Kiting"):TEXT("Hugging"),Pattern.bKiting?KiteStreak+1:HugStreak+1,S.RangeCm,Pattern.bKiting?double(P.AntiCheeseKiteRangeCm):double(P.AntiCheeseHugRangeCm),Seq);
            for(const FRPGBossSelectorTrace& T:Decision.Traces)
            {
                if(T.bEligible){UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] candidate attack=%d card=%s score=%g seq=%d"),AttacksDone+1,*T.MoveId.ToString(),T.Score,Seq);}
                else{UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] refusal attack=%d card=%s reason=%s seq=%d"),AttacksDone+1,*T.MoveId.ToString(),*T.Refusal,Seq);}
            }
            if(bAsked&&Decision.ChosenIndex==INDEX_NONE&&P.RepositionMax>0&&S.RangeCm>=P.BandMinCm&&S.RangeCm<=P.BandMaxCm)
            {
                // Inside the band but nobody is eligible: the boss does not face the target (the cone filter). Turn in place at the profile rate; bounded to 3 s, then fail closed as before.
                const double Now=GetWorld()->GetTimeSeconds(); if(RepositionTurnStartedAt<0.){RepositionTurnStartedAt=Now;UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] reposition_turn start yawToTarget=%g range=%g ratePerSecond=%g"),S.SignedYawDegrees,S.RangeCm,double(P.RepositionTurnDegPerSecond));}
                if(Now-RepositionTurnStartedAt>3.){Fail(TEXT("Framework.Selector.NoCandidate"));return;}
#if !UE_BUILD_SHIPPING
                const bool bLatch=CVarBossTurnLatch.GetValueOnGameThread()!=0;
#else
                const bool bLatch=true;
#endif
                SetActorRotation(FRotator(0.f,RPGBossTrack::StepYawLatched(GetActorRotation().Yaw,D.Rotation().Yaw,P.RepositionTurnDegPerSecond,Delta,false,RepositionLatch,bLatch),0.f));
                return;
            }
            if(RepositionTurnStartedAt>=0.)UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] reposition_turn_end flips=%d latchDir=%d seconds=%g"),RepositionLatch.Flips,RepositionLatch.Dir,GetWorld()->GetTimeSeconds()-RepositionTurnStartedAt);
            RepositionTurnStartedAt=-1.;RepositionLatch=RPGBossTrack::FTurnLatch();
            if(bAsked&&Decision.ChosenIndex==INDEX_NONE&&RepositionsInARow<P.RepositionMax)
            {
                // Opt-in repositioning: nobody is eligible from here (the target left the band): walk back to the band through the controller and decide again on arrival.
                ++RepositionsInARow;bArrived=false;StartedAt=GetWorld()->GetTimeSeconds();FString WalkError;
                UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] reposition attempt=%d max=%d range=%g reason=NoCandidate"),RepositionsInARow,P.RepositionMax,S.RangeCm);
                auto* AI=Cast<ARPGFrameworkBossController>(GetController());
                if(!AI||!AI->WalkToBand(this,WalkError)){Fail(WalkError.IsEmpty()?FString(TEXT("Framework.Boss.Controller")):WalkError);}
                return;
            }
            if(bAsked&&Decision.ChosenIndex==INDEX_NONE&&P.NeutralStrafeSeconds>0.f)
            {
                // BOSS-SEL-008: nobody is eligible (cooldowns), the boss is in its band and faces the target: circle it instead of freezing, decide again every tick, fail closed only after the budget.
                const double StrafeNow=GetWorld()->GetTimeSeconds(); if(StrafeStartedAt<0.){StrafeStartedAt=StrafeNow;StrafeLastLog=-1.;StrafeDirFlip=1;StrafeStuck=RPGBossStuck::FStuck();UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] strafe_start range=%g budgetSeconds=%g speedCmPerSecond=%g seq=%d"),S.RangeCm,double(P.NeutralStrafeSeconds),double(P.WalkSpeedCmPerSecond),Seq);}
                if(StrafeLastTick>=0.&&StrafeNow-StrafeLastTick>.5){StrafeStartedAt=StrafeNow;StrafeLastLog=-1.;StrafeDirFlip=1;StrafeStuck=RPGBossStuck::FStuck();UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] strafe_budget_restarted gapSeconds=%g reason=Interrupted"),StrafeNow-StrafeLastTick);}   // a stagger or phase hold paused the strafe: the budget counts strafing time only
                StrafeLastTick=StrafeNow;
                const double Elapsed=StrafeNow-StrafeStartedAt;
                if(Elapsed<=double(P.NeutralStrafeSeconds))
                {
                    const int32 StrafeDir=RPGBossStrafe::DirectionAt(P.SelectorTieSeed,Elapsed,P.NeutralStrafeMinHoldSeconds,P.NeutralStrafeMaxHoldSeconds)*StrafeDirFlip;
                    const FVector2D Boss2(GetActorLocation().X,GetActorLocation().Y), Next=RPGBossStrafe::NextPosition(Boss2,FVector2D(Target->GetActorLocation().X,Target->GetActorLocation().Y),double(P.WalkSpeedCmPerSecond),double(Delta),StrafeDir);
                    SetActorLocation(FVector(Next.X,Next.Y,GetActorLocation().Z),true);
                    const FVector2D After(GetActorLocation().X,GetActorLocation().Y);
                    const double MovedCm=FVector2D::Distance(Boss2,After),ExpectedCm=double(P.WalkSpeedCmPerSecond)*double(Delta);
                    RPGBossStuck::Update(StrafeStuck,ExpectedCm,MovedCm,double(Delta));
                    const double MovedRatio=StrafeStuck.AccumExpected>0.?StrafeStuck.AccumMoved/StrafeStuck.AccumExpected:1.;
                    if(RPGBossStuck::IsStuck(StrafeStuck,.5,.3)){StrafeDirFlip*=-1;UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] strafe_stuck flipped=1 movedRatio=%g"),MovedRatio);}
                    SetActorRotation(FRotator(0.f,D.Rotation().Yaw,0.f));
                    if(StrafeLastLog<0.||Elapsed-StrafeLastLog>=.5){StrafeLastLog=Elapsed;UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] strafe_step elapsed=%.3f dir=%d range=%g movedCm=%g"),Elapsed,StrafeDir,S.RangeCm,MovedCm);}
                    return;
                }
                UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] strafe_budget_exhausted seconds=%g"),Elapsed);
            }
            if(!bAsked||Decision.ChosenIndex==INDEX_NONE){Fail(TEXT("Framework.Selector.NoCandidate"));return;}
            if(StrafeStartedAt>=0.){UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] strafe_end seconds=%g reason=CandidateEligible card=%s"),GetWorld()->GetTimeSeconds()-StrafeStartedAt,*Decision.MoveId.ToString());StrafeStartedAt=-1.;StrafeLastTick=-1.;StrafeDirFlip=1;StrafeStuck=RPGBossStuck::FStuck();}
            // BOSS-PAC-006: at every decision the boss is in neutral: the executor is idle and no hit window is open.
            UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] neutral_state seq=%d executorIdle=%d openWindows=%d"),Seq,Executor->IsIdle()?1:0,Executor->OpenWindowCount());
            UE_LOG(LogTemp,Display,TEXT("[CARD_DECISION] seq=%d attack=%d card=%s score=%g rangeCm=%g phase=%s"),Seq,AttacksDone+1,*Decision.MoveId.ToString(),Decision.Score,S.RangeCm,*S.PhaseId.ToString());
            UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] decision attack=%d chosen=%s score=%g range=%g phase=%s seq=%d"),AttacksDone+1,*Decision.MoveId.ToString(),Decision.Score,S.RangeCm,*S.PhaseId.ToString(),Seq);
            FRPGBossDecisionSnapshot StartSnapshot=S;if(Decision.Traces.IsValidIndex(Decision.ChosenIndex))StartSnapshot.ConeHoldSlackDegrees=Decision.Traces[Decision.ChosenIndex].ConeHoldSlackDegrees;   // AWR-004 fix (live long run): the start must see the same cone slack as the selection
            if(!Executor->StartCard(Dependencies->Candidates[Decision.ChosenIndex].Card,StartSnapshot,Error)){Fail(Error);return;}
            bFatigueFinishedCardSeen=false;
            Selector.NoteStarted(Decision.ChosenIndex,S.ClockSeconds);RepositionsInARow=0;
            KiteStreak=(P.AntiCheeseKiteRangeCm>0.f&&S.RangeCm>=double(P.AntiCheeseKiteRangeCm))?KiteStreak+1:0;HugStreak=(P.AntiCheeseHugRangeCm>0.f&&S.RangeCm<=double(P.AntiCheeseHugRangeCm))?HugStreak+1:0;
#if !UE_BUILD_SHIPPING
            if(ProofShiftStart<0.&&!CVarBossProofTargetShift.GetValueOnGameThread().IsEmpty())
            {
                ProofShiftStart=GetWorld()->GetTimeSeconds();ProofShiftsDone=0;ProofShifts.Reset();TArray<FString> Steps;CVarBossProofTargetShift.GetValueOnGameThread().ParseIntoArray(Steps,TEXT("|"));
                for(const FString& Step:Steps){FString When,Vec;if(!Step.Split(TEXT(":"),&When,&Vec))continue;TArray<FString> V;Vec.ParseIntoArray(V,TEXT(","));if(V.Num()==3)ProofShifts.Add(TPair<double,FVector>(FCString::Atod(*When),FVector(FCString::Atod(*V[0]),FCString::Atod(*V[1]),FCString::Atod(*V[2]))));}
                UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] target_shifts_scheduled count=%d"),ProofShifts.Num());
            }
            if(ProofDrinkStart<0.&&!CVarBossProofPlayerDrink.GetValueOnGameThread().IsEmpty())
            {
                ProofDrinkStart=GetWorld()->GetTimeSeconds();ProofDrinksDone=0;ProofDrinkOffsets.Reset();TArray<FString> Parts;CVarBossProofPlayerDrink.GetValueOnGameThread().ParseIntoArray(Parts,TEXT(","));
                for(const FString& Part:Parts)ProofDrinkOffsets.Add(FCString::Atod(*Part));
                UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] player_drinks_scheduled count=%d"),ProofDrinkOffsets.Num());
            }
            if(ProofGStart<0.&&CVarBossProofPlayerGuard.GetValueOnGameThread()>0){ProofGStart=GetWorld()->GetTimeSeconds();const float RequestedPhase=CVarBossProofPlayerGuardPhaseSeconds.GetValueOnGameThread();const double PhaseLimit=double(std::numeric_limits<float>::max());const double Phase=FMath::IsFinite(RequestedPhase)?FMath::Clamp(double(RequestedPhase),-PhaseLimit,PhaseLimit):0.;UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] guard_hook_armed mode=%d seconds=%g phaseSeconds=%g"),CVarBossProofPlayerGuard.GetValueOnGameThread(),double(CVarBossProofPlayerGuardSeconds.GetValueOnGameThread()),Phase);}
            if(ProofIFStart<0.&&CVarBossProofIFrameSweep.GetValueOnGameThread()>=0.f){ProofIFStart=GetWorld()->GetTimeSeconds();ProofIFPressAt=-1.;ProofIFProbes=0;bProofIFPressed=false;UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] iframe_sweep_armed dodgeAtSeconds=%g"),double(CVarBossProofIFrameSweep.GetValueOnGameThread()));}
            if(ProofDodgeStart<0.&&!CVarBossProofPlayerDodge.GetValueOnGameThread().IsEmpty())
            {
                ProofDodgeStart=GetWorld()->GetTimeSeconds();ProofDodgesDone=0;ProofDodges.Reset();TArray<FString> Parts;CVarBossProofPlayerDodge.GetValueOnGameThread().ParseIntoArray(Parts,TEXT(","));
                for(const FString& Part:Parts){FString When,Dir;const bool bHasDir=Part.Split(TEXT(":"),&When,&Dir);ProofDodges.Add(TPair<double,bool>(FCString::Atod(bHasDir?*When:*Part),!(bHasDir&&Dir.StartsWith(TEXT("F")))));}
                UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] player_dodges_scheduled count=%d"),ProofDodges.Num());
            }
            if(ProofHitStart<0.&&!CVarBossProofPlayerHits.GetValueOnGameThread().IsEmpty())
            {
                ProofHitStart=GetWorld()->GetTimeSeconds();ProofHitsDone=0;ProofHitOffsets.Reset();TArray<FString> Parts;CVarBossProofPlayerHits.GetValueOnGameThread().ParseIntoArray(Parts,TEXT(","));
                for(const FString& Part:Parts)ProofHitOffsets.Add(FCString::Atod(*Part));
                UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] player_hits_scheduled count=%d"),ProofHitOffsets.Num());
            }
            if(CVarBossProofTargetFault.GetValueOnGameThread()>0&&!bTargetFaultInjected)
            {
                bTargetFaultInjected=true;const int32 Kind=CVarBossProofTargetFault.GetValueOnGameThread();
                UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] target_fault_injected kind=%s"),Kind==2?TEXT("Destroy"):TEXT("Kill"));
                if(Kind==2)Target->Destroy();else RPGPack::WriteAttribute(Target.Get(),TEXT("Attribute.Health"),0.);
            }
            if(CVarBossProofBystander.GetValueOnGameThread()>0.f&&!bBystanderSpawned)
            {
                bBystanderSpawned=true;const FVector ToTarget=(Target->GetActorLocation()-GetActorLocation()).GetSafeNormal2D();
                const FVector Where=Target->GetActorLocation()+FVector::CrossProduct(FVector::UpVector,ToTarget)*CVarBossProofBystander.GetValueOnGameThread();
                FActorSpawnParameters Spawn;Spawn.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
                const ACharacter* Bystander=GetWorld()->SpawnActor<ACharacter>(ACharacter::StaticClass(),Where,FRotator::ZeroRotator,Spawn);
                UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] bystander_spawned ok=%d name=%s x=%g y=%g z=%g"),Bystander?1:0,Bystander?*Bystander->GetName():TEXT("None"),Where.X,Where.Y,Where.Z);
            }
#endif
            if(ComboGraph.Nodes.Num()>0)
            {
                const int32 RootIndex=RPGBossCombo::FindNode(ComboGraph,ComboGraph.Root);
                if(RootIndex!=INDEX_NONE&&ComboGraph.Nodes[RootIndex].MoveId==Decision.MoveId)
                {
                    bComboActive=true;ComboState=RPGBossCombo::FComboState();ComboState.Node=ComboGraph.Root;ComboHitsAtStart=Executor->AcceptedHits();ComboGuardedAtStart=Executor->GuardedHits();ComboParriedAtStart=Executor->ParriedHits();
                    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] combo_start root=%s move=%s maxDepth=%d"),*ComboGraph.Root.ToString(),*Decision.MoveId.ToString(),ComboGraph.MaxDepth);
                }
            }
        }
        else if(!Executor->Start(S,Error)){Fail(Error);return;}
        bStartedMove=true;
    }
    if(bStartedMove&&Executor->DidFinish()&&Executor->IsClean())
    {
        const double Now=GetWorld()->GetTimeSeconds();
        if(!bFatigueFinishedCardSeen)
        {
            bFatigueFinishedCardSeen=true;
            if(Dependencies->Profile->FatigueFloor>0.f)
            {
                if(Executor->CurrentCardHadContact()) FatigueWhiffs=0; else ++FatigueWhiffs;
                RPGBossFatigue::FConfig Fatigue;Fatigue.GraceWhiffs=Dependencies->Profile->FatigueGraceWhiffs;Fatigue.MinRateScale=Dependencies->Profile->FatigueFloor;
                UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] fatigue whiffs=%d scale=%g"),FatigueWhiffs,RPGBossFatigue::RateScale(FatigueWhiffs,Fatigue));
            }
        }
        if(PendingParryRecoverySeconds>0.)
        {
            ParryRecoveryUntil=Now+PendingParryRecoverySeconds;
            UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] parry_recovery grade=%d extra=%g"),PendingParryRecoveryGrade,PendingParryRecoverySeconds);
            PendingParryRecoverySeconds=0.;PendingParryRecoveryGrade=0;
        }
        if(Now<ParryRecoveryUntil)return;
        ParryRecoveryUntil=0.;
    }
    if(bComboPausing){if(GetWorld()->GetTimeSeconds()<ComboPauseUntil)return;StartComboCard();return;}
    if(bStartedMove&&bComboActive&&Executor->DidFinish()&&Executor->IsClean()&&HandleComboGate())return;
    if(bTestInitialized&&bStartedMove&&Executor->DidFinish()&&Executor->IsClean())
    {
        ++AttacksDone;
        if(!Executor->PrepareNextAttack()){Fail(TEXT("Framework.Playback.NextAttack"));return;}
        bStartedMove=false;return;
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
            // every hit parried (no accepted hit, at least one parry): its own token, so the result does not claim damage that never happened (Codex X-412)
            const bool bAllParried=Executor->AcceptedHits()==0&&Executor->ParriedHits()>0;
            UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] RESULT outcome=%s acceptedHits=%d attacks=%d parriedHits=%d"),bAllParried?TEXT("CompletedAllParried"):TEXT("CompletedWithDamage"),Executor->AcceptedHits(),AttacksDone+1,Executor->ParriedHits());
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
        else if(HyperArmorNow())
        {
            // BOSS-DEF-004: the running card has hyperarmor and is in its ACTIVE state: the hit costs health only.
            UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] hyperarmor_absorbed card=%s postureKept=%g amountSkipped=%g"),*Executor->ActiveCard()->Spec().MoveId.ToString(),Posture,PostureAmount);
        }
        else
        {
            const double Drain=FMath::Min(Posture,PostureAmount);
            Posture-=Drain; LastPostureDrain=Now; bPostureRegenLogged=false;
            UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] posture_drain amount=%g postureBefore=%g postureAfter=%g max=%g"),Drain,Posture+Drain,Posture,double(Dependencies->Profile->PostureMax));
            RPGBossRules::FFlags Flags; Flags.bDead=bDead; Flags.bStaggered=bStaggered;
            if (Posture<=0. && RPGBossRules::ResolveBreak(Flags,false)==RPGBossRules::EBreakResult::Started) StartStagger();
        }
    }
    if (BleedEnabled()) ApplyBleed(BleedAmount);
    return Loss;
}
bool ARPGFrameworkBossCharacter::HyperArmorNow() const
{
    const FRPGCompiledBossMoveCard* Active=Executor->ActiveCard(); if(!Active||!Dependencies) return false;
    bool bArmor=false; for(const auto& C:Dependencies->Candidates) if(C.Card->Spec().MoveId==Active->Spec().MoveId){bArmor=C.bHyperArmor;break;}
    return RPGBossRules::HyperArmorActive(bArmor,Executor->Model().State()==ERPGBossMoveModelState::Active);
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
    // An interrupted combo card ends the combo: no later, unrelated move may be taken for its continuation.
    if(bComboActive){bComboActive=false;bComboPausing=false;ComboPendingCard=INDEX_NONE;UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] combo_end reason=StanceBreak"));}
    if(bPhaseHold)
    {
        // F11: a stance break during the transition clip stops it; the phase stays latched and the clip is not replayed.
        StopF11Clip();bPhaseHold=false;
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] phase_anim state=Aborted reason=StanceBreak phase=%s"),*CurrentPhaseId.ToString());
    }
    if(Dependencies->StaggerStart.IsValid())
    {
        const auto& P=*Dependencies->Profile.Get();
        StaggerStartedAt=GetWorld()->GetTimeSeconds();StaggerAnimState=RPGStaggerAnim::EState::Start;bStaggerAnimActive=true;
        if(!PlayF11Clip(Dependencies->StaggerStart.Get(),1)){Fail(TEXT("Framework.Playback.StaggerAnim"));return;}
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] stagger_anim state=Start sequence=%s slot=%s length=%g"),*Dependencies->StaggerStart->GetName(),*P.AnimSlotName.ToString(),double(Dependencies->StaggerStart->GetPlayLength()));
    }
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] stance_break state=%s duration=%g generation=%llu phase=%s"),bMidAttack?TEXT("MidAttack"):TEXT("Neutral"),double(Dependencies->Profile->StaggerSeconds),GenerationId,*CurrentPhaseId.ToString());
}
void ARPGFrameworkBossCharacter::EndStagger()
{
    bool bRecovered=true;
    if(bStaggerAbortedAttack){bRecovered=Executor->RecoverAfterAbort();bStartedMove=false;bStaggerAbortedAttack=false;}
    if(!bRecovered){Fail(TEXT("Framework.Playback.StaggerRecover"));return;}
    bStaggered=false; Posture=double(Dependencies->Profile->PostureMax); LastPostureDrain=-1.;
    if(bStaggerAnimActive){bStaggerAnimActive=false;F11Montage.Reset();UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] stagger_anim state=Finished postureRefilled=%g"),Posture);}
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] stagger_recovery postureRefilled=%g generation=%llu"),Posture,GenerationId);
    // A break while the boss was still walking to the band stopped the owned walk: ask for it again (the arrival check and the walk timeout run as before).
    if(!bArrived)
    {
        FString WalkError; auto* AI=Cast<ARPGFrameworkBossController>(GetController());
        if(!AI||!AI->WalkToBand(this,WalkError)){Fail(WalkError.IsEmpty()?FString(TEXT("Framework.Boss.Controller")):WalkError);return;}
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] walk_resumed generation=%llu"),GenerationId);
    }
}
void ARPGFrameworkBossCharacter::TickOverlay()
{
    const int32 Mode=CVarBossOverlay.GetValueOnGameThread();
    if(Mode<=0||!Dependencies||!Target.IsValid())return;
    RPGBossOverlay::FInput I; const auto& P=*Dependencies->Profile.Get();
    const FRPGCompiledBossMoveCard* Card=Executor->ActiveCard();
    if(Card){I.CardId=Card->Spec().MoveId.ToString();I.Cone=Card->Spec().FrontConeDegrees;}
    const ERPGBossMoveModelState State=Executor->Model().State();
    I.State=State==ERPGBossMoveModelState::Idle?TEXT("Idle"):State==ERPGBossMoveModelState::Committed?TEXT("Committed"):State==ERPGBossMoveModelState::Active?TEXT("Active"):TEXT("Recovery");
    I.bWindowOpen=State==ERPGBossMoveModelState::Active;I.Phase=CurrentPhaseId.ToString();
    I.Range=FVector::Dist2D(GetActorLocation(),Target->GetActorLocation());
    I.Posture=Posture;I.PostureMax=P.PostureMax;I.Health=Health;I.MaxHealth=MaxHealth;I.bStaggered=bStaggered;I.bPhaseHold=bPhaseHold;
    if(const URPGPlayerParry* Parry=Target->FindComponentByClass<URPGPlayerParry>()){I.bHasParryData=true;I.bParryWindowOpen=Parry->IsWindowOpen();I.LastParryGrade=Parry->LastGradeName();}
    const FString Line=RPGBossOverlay::Format(I);
    if(GEngine)GEngine->AddOnScreenDebugMessage(int32(GetUniqueID()&0x7fffffff),.1f,FColor::Yellow,TEXT("Boss: ")+Line);
    const double Now=GetWorld()->GetTimeSeconds();
    // Mode 2 logs once per second and also on every change of the move state, so a short Open window is caught.
    const bool bStateChanged=I.State!=OverlayLastState; OverlayLastState=I.State;
    if(Mode>=2&&(bStateChanged||OverlayLoggedAt<0.||Now-OverlayLoggedAt>=1.)){OverlayLoggedAt=Now;UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] overlay %s"),*Line);}
}
FRPGBossDecisionSnapshot ARPGFrameworkBossCharacter::MakeSnapshot() const
{
    const FVector D=Target->GetActorLocation()-GetActorLocation();FRPGBossDecisionSnapshot S;
    S.EncounterId=EncounterId;S.Generation=GenerationId;S.TargetId=uint64(Target->GetUniqueID());S.FrameId=GFrameCounter;
    S.PhaseId=CurrentPhaseId;S.ClockSeconds=GetWorld()->GetTimeSeconds();S.RangeCm=D.Size2D();
    S.SignedYawDegrees=FMath::FindDeltaAngleDegrees(GetActorRotation().Yaw,D.Rotation().Yaw);S.VerticalDeltaCm=FloorSeparationCm();S.bTargetValid=S.bNeutral=true;
    return S;
}
bool ARPGFrameworkBossCharacter::HandleComboGate()
{
    // A card of the combo finished: one branch gate with the FRESH snapshot of now (RPGBossCombo::Step). Returns true when the next card of the combo was started.
    const FRPGBossDecisionSnapshot S=MakeSnapshot();
    RPGBossCombo::FComboGate Gate; Gate.GateId=++ComboGateCounter; Gate.RangeCm=S.RangeCm; Gate.SignedYawDegrees=S.SignedYawDegrees; Gate.bTargetValid=true;
    // BOSS-COM-004: the strongest thing the player did to this card (parry > guard > hit > whiff), from the guard the executor read at every accepted contact.
    const RPGBossGuard::ECardOutcome Card=RPGBossGuard::CardOutcome(Executor->AcceptedHits()-ComboHitsAtStart,Executor->GuardedHits()-ComboGuardedAtStart,Executor->ParriedHits()-ComboParriedAtStart);
    Gate.Outcome=Card==RPGBossGuard::ECardOutcome::Parried?RPGBossCombo::EOutcome::Parried:Card==RPGBossGuard::ECardOutcome::Guarded?RPGBossCombo::EOutcome::Guarded:Card==RPGBossGuard::ECardOutcome::Hit?RPGBossCombo::EOutcome::Hit:RPGBossCombo::EOutcome::Whiff;
    const FName From=ComboState.Node; const RPGBossCombo::FComboStep R=RPGBossCombo::Step(ComboGraph,ComboState,Gate);
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] combo_gate gate=%llu node=%s outcome=%s range=%g yaw=%g result=%s next=%s reason=%s"),Gate.GateId,*From.ToString(),Gate.Outcome==RPGBossCombo::EOutcome::Parried?TEXT("Parried"):Gate.Outcome==RPGBossCombo::EOutcome::Guarded?TEXT("Guarded"):Gate.Outcome==RPGBossCombo::EOutcome::Hit?TEXT("Hit"):TEXT("Whiff"),S.RangeCm,S.SignedYawDegrees,
        R.Kind==RPGBossCombo::EStep::Continue?TEXT("Continue"):R.Kind==RPGBossCombo::EStep::Finished?TEXT("Finished"):R.Kind==RPGBossCombo::EStep::Ignored?TEXT("Ignored"):TEXT("Recover"),*R.NextNode.ToString(),*R.Reason);
#if !UE_BUILD_SHIPPING
    if(CVarBossComboDuplicateGate.GetValueOnGameThread()>0&&R.Kind!=RPGBossCombo::EStep::Ignored)
    {
        const RPGBossCombo::FComboState Before=ComboState; const RPGBossCombo::FComboStep Dup=RPGBossCombo::Step(ComboGraph,ComboState,Gate);   // the same gate id again
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] combo_gate_duplicate gate=%llu result=%s reason=%s stateUnchanged=%d"),Gate.GateId,Dup.Kind==RPGBossCombo::EStep::Ignored?TEXT("Ignored"):TEXT("NOT_IGNORED"),*Dup.Reason,(Before.Node==ComboState.Node&&Before.Depth==ComboState.Depth&&Before.LastGateId==ComboState.LastGateId)?1:0);
    }
#endif
    if(R.Kind==RPGBossCombo::EStep::Ignored)return false;
    if(R.Kind!=RPGBossCombo::EStep::Continue){bComboActive=false;return false;}   // recovery or end of the combo: the normal next attack logic follows
    if(AttacksDone+1>=Dependencies->Profile->AttackCount){bComboActive=false;UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] combo_end reason=AttackBudget"));return false;}
    const int32 NodeIndex=RPGBossCombo::FindNode(ComboGraph,R.NextNode);
    int32 CardIndex=INDEX_NONE; for(int32 I=0;I<Dependencies->Candidates.Num();++I) if(NodeIndex!=INDEX_NONE&&Dependencies->Candidates[I].Card->Spec().MoveId==ComboGraph.Nodes[NodeIndex].MoveId) CardIndex=I;
    if(R.PauseSeconds>0.f&&CardIndex!=INDEX_NONE)
    {
        // BOSS-PAC-002: a deliberate tempo pause: the boss stands in neutral, then StartComboCard starts the card with a fresh snapshot.
        bComboPausing=true;ComboPauseUntil=GetWorld()->GetTimeSeconds()+double(R.PauseSeconds);ComboPendingCard=CardIndex;
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] combo_pause seconds=%g next=%s"),double(R.PauseSeconds),*ComboState.Node.ToString());
        return true;
    }
    FString Error;
    ++AttacksDone; if(!Executor->PrepareNextAttack()){Fail(TEXT("Framework.Playback.NextAttack"));return true;}
    bStartedMove=false;
    if(CardIndex==INDEX_NONE||!Executor->StartCard(Dependencies->Candidates[CardIndex].Card,S,Error))
    {
        bComboActive=false;UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] combo_end reason=NextCardRefused detail=%s"),*Error);return true;   // the next tick decides with the selector
    }
    bFatigueFinishedCardSeen=false;Selector.NoteStarted(CardIndex,S.ClockSeconds);ComboHitsAtStart=Executor->AcceptedHits();ComboGuardedAtStart=Executor->GuardedHits();ComboParriedAtStart=Executor->ParriedHits();bStartedMove=true;
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] combo_step node=%s move=%s depth=%d"),*ComboState.Node.ToString(),*Dependencies->Candidates[CardIndex].Card->Spec().MoveId.ToString(),ComboState.Depth);
    return true;
}
void ARPGFrameworkBossCharacter::StartComboCard()
{
    // The pause is over: the same start the gate does without a pause (BOSS-COM-001), with a fresh snapshot of now.
    bComboPausing=false;const int32 CardIndex=ComboPendingCard;ComboPendingCard=INDEX_NONE;
    const FRPGBossDecisionSnapshot S=MakeSnapshot();FString Error;
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] combo_pause_end"));
    ++AttacksDone; if(!Executor->PrepareNextAttack()){Fail(TEXT("Framework.Playback.NextAttack"));return;}
    bStartedMove=false;
    if(!Dependencies->Candidates.IsValidIndex(CardIndex)||!Executor->StartCard(Dependencies->Candidates[CardIndex].Card,S,Error))
    {
        bComboActive=false;UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] combo_end reason=NextCardRefused detail=%s"),*Error);return;
    }
    bFatigueFinishedCardSeen=false;Selector.NoteStarted(CardIndex,S.ClockSeconds);ComboHitsAtStart=Executor->AcceptedHits();ComboGuardedAtStart=Executor->GuardedHits();ComboParriedAtStart=Executor->ParriedHits();bStartedMove=true;
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] combo_step node=%s move=%s depth=%d"),*ComboState.Node.ToString(),*Dependencies->Candidates[CardIndex].Card->Spec().MoveId.ToString(),ComboState.Depth);
}
bool ARPGFrameworkBossCharacter::PlayF11Clip(UAnimSequence* Clip,int32 Loops)
{
    // The same runtime path the executor uses for the cards: a dynamic montage of the loaded sequence in the profile's slot. Loaded dependency only, no load here.
    UAnimInstance* Anim=GetMesh()?GetMesh()->GetAnimInstance():nullptr;
    if(!IsValid(Clip)||!IsValid(Anim)||!Dependencies)return false;
    const auto& P=*Dependencies->Profile.Get();
    F11Montage=Anim->PlaySlotAnimationAsDynamicMontage(Clip,P.AnimSlotName,P.BlendInSeconds,P.BlendOutSeconds,1.f,FMath::Max(1,Loops),-1.f,0.f);
    return F11Montage.IsValid();
}
void ARPGFrameworkBossCharacter::StopF11Clip()
{
    UAnimMontage* Montage=F11Montage.Get();F11Montage.Reset();
    UAnimInstance* Anim=GetMesh()?GetMesh()->GetAnimInstance():nullptr;
    if(IsValid(Montage)&&IsValid(Anim)&&Dependencies)Anim->Montage_Stop(Dependencies->Profile->BlendOutSeconds,Montage);
}
void ARPGFrameworkBossCharacter::TickStaggerAnim()
{
    // The sub state follows the time since the break (RPGStaggerAnim::Evaluate): Start, then Loop (looped to fill the middle), then End started so that it finishes with StaggerSeconds.
    if(!bStaggerAnimActive||!Dependencies||!Dependencies->StaggerStart.IsValid())return;
    const auto& P=*Dependencies->Profile.Get();
    const float StartLen=Dependencies->StaggerStart->GetPlayLength(), LoopLen=Dependencies->StaggerLoop->GetPlayLength(), EndLen=Dependencies->StaggerEnd->GetPlayLength();
    const RPGStaggerAnim::EState Now=RPGStaggerAnim::Evaluate(StartLen,EndLen,P.StaggerSeconds,float(GetWorld()->GetTimeSeconds()-StaggerStartedAt));
    if(Now==StaggerAnimState||Now==RPGStaggerAnim::EState::Finished)return;
    StaggerAnimState=Now;
    if(Now==RPGStaggerAnim::EState::Loop)
    {
        const int32 Loops=RPGStaggerAnim::LoopCount(P.StaggerSeconds,StartLen,EndLen,LoopLen);
        if(!PlayF11Clip(Dependencies->StaggerLoop.Get(),Loops)){Fail(TEXT("Framework.Playback.StaggerAnim"));return;}
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] stagger_anim state=Loop sequence=%s slot=%s loops=%d"),*Dependencies->StaggerLoop->GetName(),*P.AnimSlotName.ToString(),Loops);
    }
    else
    {
        StopF11Clip();
        if(!PlayF11Clip(Dependencies->StaggerEnd.Get(),1)){Fail(TEXT("Framework.Playback.StaggerAnim"));return;}
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] stagger_anim state=End sequence=%s slot=%s length=%g"),*Dependencies->StaggerEnd->GetName(),*P.AnimSlotName.ToString(),double(EndLen));
    }
}
bool ARPGFrameworkBossCharacter::RestartEncounter(uint64 NewGeneration,FString& Error)
{
    Error.Reset();
    if (!CanRestart(NewGeneration)||!IsInGameThread()) {Error=TEXT("Framework.Boss.RestartState");return false;}
    double HP=0.; if (!ValidateTarget(HP)) {Error=TEXT("Framework.Boss.TargetHealth");return false;}
    if (!Executor->Rearm(NewGeneration,Error)) return false;
    const TCHAR* OldState=bDead?TEXT("Dead"):TEXT("Finished");
    GenerationId=NewGeneration; TargetHPBefore=ExpectedTargetHP=HP; AttacksDone=0; StrafeStartedAt=-1.; StrafeLastTick=-1.; StrafeLastLog=-1.; StrafeDirFlip=1; StrafeStuck=RPGBossStuck::FStuck(); YawProbeSampleIndex=0; RepositionTurnStartedAt=-1.;RepositionLatch=RPGBossTrack::FTurnLatch(); bParryReactionPending=false; PendingParryReactionScale=0.;PendingParryRecoverySeconds=ParryRecoveryUntil=0.;PendingParryRecoveryGrade=0;AggroBand=RPGBossAggro::EBand::Balanced;AggroDodgeTimes.Reset();FatigueWhiffs=0;bFatigueFinishedCardSeen=false; bStartedMove=false; bArrived=false; bSucceeded=false; bDead=false;
    if (bHittable) Health=MaxHealth;
    Posture=double(Dependencies->Profile->PostureMax); LastPostureDrain=-1.; bPostureRegenLogged=false; bStaggered=bStaggerAbortedAttack=false; StopF11Clip(); bStaggerAnimActive=bPhaseHold=false; bComboActive=false; RepositionsInARow=0; DodgeHistory=RPGBossTrack::FDodgeHistory(); bDodgeWasFast=false; DodgesSeen=0; ProofDodgeStart=-1.; ProofDodgesDone=0; Los=RPGBossTrack::FLosMemory(); bLosWalking=false; bDrinkWasPlaying=bFlaskPending=bFlaskKnown=false; FlaskPerceivedCount=0; ProofDrinkStart=-1.; ProofDrinksDone=0; KiteStreak=HugStreak=0; bComboPausing=false; ComboPendingCard=INDEX_NONE; bLeashed=bLeashAtCenter=false; ProofShiftStart=-1.; ProofShiftsDone=0; bBystanderSpawned=false; bTargetFaultInjected=false; ProofHitStart=-1.; ProofHitsDone=0; ResetBleed();
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
    bDead=true; RepositionTurnStartedAt=-1.;RepositionLatch=RPGBossTrack::FTurnLatch();PendingParryRecoverySeconds=ParryRecoveryUntil=0.;PendingParryRecoveryGrade=0;
    if(auto* AI=Cast<ARPGFrameworkBossController>(GetController()))AI->StopOwnedWalk();
    GetCharacterMovement()->StopMovementImmediately();GetCharacterMovement()->DisableMovement();
    Executor->Abort(TEXT("BossDead"));StopF11Clip();bStaggerAnimActive=bPhaseHold=false;
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] boss_dead generation=%llu executorAborted=1"),GenerationId);
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] RESULT outcome=BossDefeated acceptedHits=%d attacks=%d"),Executor->AcceptedHits(),AttacksDone+(bStartedMove?1:0));
}
void ARPGFrameworkBossCharacter::Fail(const FString& Error)
{
    if(bFailed)return;bFailed=true;RepositionTurnStartedAt=-1.;RepositionLatch=RPGBossTrack::FTurnLatch();PendingParryRecoverySeconds=ParryRecoveryUntil=0.;PendingParryRecoveryGrade=0;
    if(auto* AI=Cast<ARPGFrameworkBossController>(GetController()))AI->StopOwnedWalk();
    GetCharacterMovement()->StopMovementImmediately();GetCharacterMovement()->DisableMovement();Executor->Abort(Error);StopF11Clip();
    UE_LOG(LogTemp,Error,TEXT("[FrameworkProof] ERROR token=%s bossInactive=1"),*Error);
    if(GEngine)GEngine->AddOnScreenDebugMessage(-1,10.f,FColor::Red,TEXT("FrameworkProof: ")+Error);
}
void ARPGFrameworkBossCharacter::EndPlay(const EEndPlayReason::Type Reason)
{
    if(auto* AI=Cast<ARPGFrameworkBossController>(GetController()))AI->StopOwnedWalk();Executor->Abort(TEXT("EndPlay"));StopF11Clip();
    Dependencies.Reset();Target.Reset();TargetController.Reset();ProofFixture.Reset();Super::EndPlay(Reason);
}
