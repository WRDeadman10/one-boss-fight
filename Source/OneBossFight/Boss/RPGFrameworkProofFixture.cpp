// Copyright One Boss Fight. All Rights Reserved.
#include "Boss/RPGFrameworkProofFixture.h"
#include "Boss/RPGFrameworkBossCharacter.h"
#include "Player/RPGBossFrameworkProfile.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/PlayerStart.h"
#include "NavigationSystem.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "Pack/RPGBlueprintCall.h"
#include "Pack/RPGPackReflect.h"
namespace
{
    // KI-150 (second cause, measured): about 9.4 s after PIE start the pack equips its combat style (BP_CombatComponent_C.CurrentCombatStyle None -> SwordCombatStyle) and the player's
    // Health/Max are reset to 100/120. Anything written before that moment is lost, so the fixture waits for the pack to have answered before it prepares the target.
    bool PackStyleKnown(const AActor* Player)
    {
        const UObject* Combat=RPGPack::FindComponentByClassName(Player,TEXT("BP_CombatComponent_C"));
        const UObject* Style=Combat?RPGPackReflect::ReadObject(Combat,TEXT("CurrentCombatStyle")):nullptr;
        return Style!=nullptr;
    }
    // KI-150: the pack's regeneration clamps Health to the attribute MAXIMUM (PlayerInfo default 100), so a target health above it is pulled back to 100 at an unpredictable time
    // after damage. Write the maximum FIRST, then the current value, and read both back; the pack's own regeneration then stays inside the fixture's value.
    bool SetTargetHealth(const AActor* Player,double Value)
    {
        double MaxBack=0.,CurrentBack=0.;
        return RPGPack::WriteMaxAttribute(Player,TEXT("Attribute.Health"),Value)&&RPGPack::ReadAttribute(Player,TEXT("Attribute.Health"),true,MaxBack)&&FMath::IsNearlyEqual(MaxBack,Value)
            &&RPGPack::WriteAttribute(Player,TEXT("Attribute.Health"),Value)&&RPGPack::ReadAttribute(Player,TEXT("Attribute.Health"),false,CurrentBack)&&FMath::IsNearlyEqual(CurrentBack,Value);
    }
}
ARPGFrameworkProofFixture::ARPGFrameworkProofFixture(){PrimaryActorTick.bCanEverTick=true;}
void ARPGFrameworkProofFixture::BeginPlay()
{
    Super::BeginPlay();WaitStart=GetWorld()->GetTimeSeconds();
    auto* Mode=Cast<ARPGFrameworkProofGameMode>(GetWorld()->GetAuthGameMode());
    if(!Mode||GetNetMode()!=NM_Standalone||EncounterId<=0||Generation<=0||!IsValid(TargetStart)||TargetStart->GetWorld()!=GetWorld()||BossSpawnTransform.ContainsNaN()||!BossSpawnTransform.IsValid())
    {Fail(TEXT("Framework.Fixture.Authority"));return;}
    ResolvedProfile=Profile.LoadSynchronous();FString Error;
    if(!IsValid(ResolvedProfile)||!RPGFramework::ValidateProfile(*ResolvedProfile,Error)||!Mode->RegisterFixture(this,Error))
    {Fail(Error.IsEmpty()?TEXT("Framework.Fixture.Profile"):Error);return;}
}
void ARPGFrameworkProofFixture::SetExplicitTarget(APawn* Pawn)
{
    if(!IsValid(Pawn)||Pawn->GetWorld()!=GetWorld()||ExplicitPlayer.IsValid()) {Fail(TEXT("Framework.Fixture.TargetPublication"));return;}
    ExplicitPlayer=Pawn;
}
bool ARPGFrameworkProofFixture::Authorizes(const ARPGFrameworkBossCharacter* Boss,const APawn* Pawn) const
{return !bFailed&&Boss==OwnedBoss&&Pawn==ExplicitPlayer.Get()&&Boss&&Pawn&&Boss->GetWorld()==GetWorld()&&Pawn->GetWorld()==GetWorld();}
void ARPGFrameworkProofFixture::Tick(float Delta)
{
    Super::Tick(Delta);if(bFailed||bAttempted||!ResolvedProfile)return;
    if(ExplicitPlayer.IsValid()&&!bTargetPrepared)
    {
        if(!PackStyleKnown(ExplicitPlayer.Get()))
        {
            if(GetWorld()->GetTimeSeconds()-WaitStart>PackStyleWaitSeconds){Fail(TEXT("Framework.Fixture.PackStyleTimeout"));}
            return;
        }
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] pack_style_known waitedSeconds=%g"),GetWorld()->GetTimeSeconds()-WaitStart);
        WaitStart=GetWorld()->GetTimeSeconds();   // the target-health and navigation waits (walk timeout) count from here
        // A bare proof map leaves the pack player at health 0: write the profile value explicitly, read it back, never relax the target-alive gate.
        bTargetPrepared=true;double Back=0.;
        if(!SetTargetHealth(ExplicitPlayer.Get(),ResolvedProfile->TargetHealth)||!RPGPack::ReadAttribute(ExplicitPlayer.Get(),TEXT("Attribute.Health"),false,Back)||!FMath::IsNearlyEqual(Back,double(ResolvedProfile->TargetHealth)))
        {Fail(TEXT("Framework.Fixture.TargetHealthInit"));return;}
        UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] target_health_init value=%g readback=%g label=%s"),double(ResolvedProfile->TargetHealth),Back,*ResolvedProfile->FixtureLabel.Replace(TEXT(" "),TEXT("_")));
    }
    double HP=0.;
    if(!ExplicitPlayer.IsValid()||!RPGPack::ReadAttribute(ExplicitPlayer.Get(),TEXT("Attribute.Health"),false,HP)||!FMath::IsFinite(HP)||HP<=0.)
    {if(GetWorld()->GetTimeSeconds()-WaitStart>ResolvedProfile->WalkTimeoutSeconds)Fail(TEXT("Framework.Fixture.TargetInitializationTimeout"));return;}
    // The navmesh of a proof map is built at PIE start and is not ready on the first ticks (measured: Framework.Nav.Projection failed in one run of three):
    // wait until a build is not running AND the target's own position projects onto it, else fail closed at the walk timeout.
    UNavigationSystemV1* Nav=FNavigationSystem::GetCurrent<UNavigationSystemV1>(GetWorld()); FNavLocation Probe;
    const FVector TargetAt=ExplicitPlayer->GetActorLocation(); const FVector Away=(BossSpawnTransform.GetLocation()-TargetAt).GetSafeNormal2D();
    // The same point the boss will walk to (band centre on the boss side of the target): ready means THAT point projects onto the navmesh.
    if(!Nav||Nav->IsNavigationBuildInProgress()||!Nav->ProjectPointToNavigation(TargetAt+Away*((ResolvedProfile->BandMinCm+ResolvedProfile->BandMaxCm)*.5f),Probe))
    {
        if(GetWorld()->GetTimeSeconds()-WaitStart>ResolvedProfile->WalkTimeoutSeconds)
        {
            UE_LOG(LogTemp,Error,TEXT("[FrameworkProof] nav_not_ready navSystem=%d buildInProgress=%d targetLocation=%s"),Nav!=nullptr,Nav?Nav->IsNavigationBuildInProgress():0,*ExplicitPlayer->GetActorLocation().ToString());
            Fail(TEXT("Framework.Fixture.NavigationNotReady"));
        }
        return;
    }
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] nav_ready waitedSeconds=%g"),GetWorld()->GetTimeSeconds()-WaitStart);
    bAttempted=true;
    OwnedBoss=GetWorld()->SpawnActorDeferred<ARPGFrameworkBossCharacter>(ARPGFrameworkBossCharacter::StaticClass(),BossSpawnTransform,this,nullptr,ESpawnActorCollisionHandlingMethod::DontSpawnIfColliding);
    if(!OwnedBoss){Fail(TEXT("Framework.Fixture.SpawnCollision"));return;}
    UGameplayStatics::FinishSpawningActor(OwnedBoss,BossSpawnTransform);
    FString Error;
    if(!OwnedBoss->InitializeProof(this,ResolvedProfile,ExplicitPlayer.Get(),uint64(EncounterId),uint64(Generation),Error))Fail(Error);
}
void ARPGFrameworkProofFixture::Fail(const FString& Error)
{
    if(bFailed)return;bFailed=true;if(IsValid(OwnedBoss))OwnedBoss->Fail(Error);
    UE_LOG(LogTemp,Error,TEXT("[FrameworkProof] ERROR token=%s fixtureInactive=1"),*Error);
    if(GEngine)GEngine->AddOnScreenDebugMessage(-1,10.f,FColor::Red,TEXT("FrameworkProof: ")+Error);
}
bool ARPGFrameworkProofFixture::RestartEncounterForTest(int32 NewGeneration)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    FString Error;
    if (bFailed||!IsValid(OwnedBoss)||!ExplicitPlayer.IsValid()||!ResolvedProfile||NewGeneration<=0
        ||!OwnedBoss->CanRestart(uint64(NewGeneration))   // refuse BEFORE any write: an active or stale-generation boss must not see its target's health rewritten (X-370)
        ||!SetTargetHealth(ExplicitPlayer.Get(),ResolvedProfile->TargetHealth)||!OwnedBoss->RestartEncounter(uint64(NewGeneration),Error))
    {
        UE_LOG(LogTemp,Error,TEXT("[FrameworkProof] encounter_reset refused generation=%d reason=%s"),NewGeneration,Error.IsEmpty()?TEXT("Framework.Fixture.RestartState"):*Error);
        return false;
    }
    return true;
#endif
}
void ARPGFrameworkProofFixture::InvalidateTarget()
{
    // After a clean finish or the boss's death the proof is over: the controller logging out at the end of PIE is not a failure.
    if(IsValid(OwnedBoss)&&(OwnedBoss->Succeeded()||OwnedBoss->IsDead())){ExplicitPlayer.Reset();return;}
    Fail(TEXT("Framework.Fixture.PossessionChanged"));ExplicitPlayer.Reset();
}
void ARPGFrameworkProofFixture::EndPlay(const EEndPlayReason::Type Reason)
{if(IsValid(OwnedBoss))OwnedBoss->Destroy();OwnedBoss=nullptr;ExplicitPlayer.Reset();Super::EndPlay(Reason);}
ARPGFrameworkProofGameMode::ARPGFrameworkProofGameMode(){DefaultPawnClass=nullptr;}
bool ARPGFrameworkProofGameMode::RegisterFixture(ARPGFrameworkProofFixture* F,FString& Error)
{
    Error.Reset();if(Fixture.IsValid()||!IsValid(F)||F->GetWorld()!=GetWorld()||!F->LoadedProfile())
    {Error=TEXT("Framework.Fixture.DuplicateOrWorld");return false;}
    UClass* TargetClass=F->LoadedProfile()->TargetPawnClass.LoadSynchronous();
    if(!IsValid(TargetClass)||!TargetClass->IsChildOf(APawn::StaticClass())||TargetClass->HasAnyClassFlags(CLASS_Abstract))
    {Error=TEXT("Framework.Fixture.TargetClass");return false;}
    DefaultPawnClass=TargetClass;Fixture=F;TrySpawnTarget();return true;
}
void ARPGFrameworkProofGameMode::HandleStartingNewPlayer_Implementation(APlayerController* Player)
{
    // Intentionally suppress the default automatic pawn choice. PostLogin publishes the explicit controller.
    TrySpawnTarget();
}
void ARPGFrameworkProofGameMode::PostLogin(APlayerController* Player)
{
    Super::PostLogin(Player);
    if(ExplicitController.IsValid()||!IsValid(Player))
    {if(Fixture.IsValid())Fixture->InvalidateTarget();return;}
    ExplicitController=Player;TrySpawnTarget();
}
void ARPGFrameworkProofGameMode::TrySpawnTarget()
{
    if(bSpawnAttempted||!Fixture.IsValid()||!ExplicitController.IsValid())return;
    bSpawnAttempted=true;
    if(!IsValid(Fixture->TargetStart)||!DefaultPawnClass||ExplicitController->GetPawn()) {Fixture->InvalidateTarget();return;}
    APawn* Pawn=SpawnDefaultPawnAtTransform(ExplicitController.Get(),Fixture->TargetStart->GetActorTransform());
    if(!IsValid(Pawn)||!Pawn->IsA(DefaultPawnClass)){if(Pawn)Pawn->Destroy();Fixture->InvalidateTarget();return;}
    ExplicitController->Possess(Pawn);
    if(ExplicitController->GetPawn()!=Pawn){Pawn->Destroy();Fixture->InvalidateTarget();return;}
    Fixture->SetExplicitTarget(Pawn);
}
void ARPGFrameworkProofGameMode::Logout(AController* Exiting)
{if(Exiting==ExplicitController.Get()&&Fixture.IsValid())Fixture->InvalidateTarget();Super::Logout(Exiting);}
