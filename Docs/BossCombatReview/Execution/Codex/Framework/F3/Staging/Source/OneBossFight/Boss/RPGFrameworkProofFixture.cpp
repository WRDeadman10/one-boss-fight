// Copyright One Boss Fight. All Rights Reserved.
#include "Boss/RPGFrameworkProofFixture.h"
#include "Boss/RPGFrameworkBossCharacter.h"
#include "Player/RPGBossFrameworkProfile.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/PlayerStart.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "Pack/RPGBlueprintCall.h"
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
    double HP=0.;
    if(!ExplicitPlayer.IsValid()||!RPGPack::ReadAttribute(ExplicitPlayer.Get(),TEXT("Attribute.Health"),false,HP)||!FMath::IsFinite(HP)||HP<=0.)
    {if(GetWorld()->GetTimeSeconds()-WaitStart>ResolvedProfile->WalkTimeoutSeconds)Fail(TEXT("Framework.Fixture.TargetInitializationTimeout"));return;}
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
void ARPGFrameworkProofFixture::InvalidateTarget(){Fail(TEXT("Framework.Fixture.PossessionChanged"));ExplicitPlayer.Reset();}
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
