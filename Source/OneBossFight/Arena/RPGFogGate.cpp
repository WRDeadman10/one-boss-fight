// Copyright One Boss Fight. All Rights Reserved.

#include "Arena/RPGFogGate.h"
#include "Arena/RPGPerfSwitches.h"
#include "Pack/RPGBlueprintCall.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGPlayerMovesSubsystem.h"
#include "Components/BoxComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Pawn.h"
#include "Materials/MaterialInterface.h"

using namespace RPGPack;

ARPGFogGate::ARPGFogGate()
{
	PrimaryActorTick.bCanEverTick = true;
	Blocker = CreateDefaultSubobject<UBoxComponent>(TEXT("Blocker"));
	SetRootComponent(Blocker);
	Blocker->SetBoxExtent(BlockerHalfExtent);
	Blocker->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Blocker->SetCollisionResponseToAllChannels(ECR_Ignore);
	Blocker->SetCollisionResponseToChannel(ECC_Pawn, ECR_Block);
	Blocker->SetCollisionObjectType(ECC_WorldStatic);
	Blocker->SetHiddenInGame(true);
	Cards = CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("Cards"));
	Cards->SetupAttachment(Blocker);
	Cards->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Cards->SetCastShadow(false);
}

void ARPGFogGate::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	Rebuild();
}

void ARPGFogGate::Rebuild()
{
	Blocker->SetBoxExtent(BlockerHalfExtent);
	Cards->ClearInstances();
	if (!CardMesh)
	{
		return;
	}
	Cards->SetStaticMesh(CardMesh);
	if (CardMaterial)
	{
		Cards->SetMaterial(0, CardMaterial);
	}
	// Cards stand across the doorway: lying card meshes tipped up by 90 degrees (pitch), three heights as in the earlier static version.
	for (int32 Index = 0; Index < CardCount; ++Index)
	{
		const float Y = (Index - (CardCount - 1) * 0.5f) * CardSpacing;
		const float Z = -BlockerHalfExtent.Z + 40.f + (Index % 3) * 140.f;
		Cards->AddInstance(FTransform(FRotator(90.f, 0.f, 0.f), FVector(0.f, Y, Z), FVector(CardScale)));
	}
	// In the editor the gate shows closed so it can be seen; in a game it starts at its idle size.
	Amount = (GetWorld() && GetWorld()->IsGameWorld()) ? IdleAmount : 1.f;
	ApplyAmount();
}

void ARPGFogGate::BeginPlay()
{
	Super::BeginPlay();
	Amount = IdleAmount;
	State = EState::Idle;
	ApplyAmount();
}

FString ARPGFogGate::GetStateName() const
{
	switch (State)
	{
	case EState::Closed: return TEXT("Closed");
	case EState::Cleared: return TEXT("Cleared");
	default: return TEXT("Idle");
	}
}

bool ARPGFogGate::IsBlocking() const
{
	return Blocker && Blocker->GetCollisionEnabled() != ECollisionEnabled::NoCollision;
}

ARPGFogGate::EState ARPGFogGate::ReadBossState()
{
	for (TActorIterator<APawn> It(GetWorld()); It; ++It)
	{
		if (!URPGPlayerMovesSubsystem::IsPackBoss(*It))
		{
			continue;
		}
		double Health = 1.0;
		const bool bHealth = ReadAttribute(*It, TEXT("Attribute.Health"), false, Health);
		if (bHealth && Health > 0.0)
		{
			bSeenAlive = true;
		}
		if (bHealth && Health <= 0.0 && bSeenAlive)
		{
			// Only a boss that was seen alive can die: the attributes read zero for a moment right after the level starts.
			bCleared = true; // stays cleared until the level restarts: a dead boss does not come back
			return EState::Cleared;
		}
		const URPGBossEncounter* Encounter = It->FindComponentByClass<URPGBossEncounter>();
		if (Encounter && !Encounter->IsDormant())
		{
			return EState::Closed;
		}
		return EState::Idle;
	}
	return EState::Idle;
}

void ARPGFogGate::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
#if !UE_BUILD_SHIPPING
	if (Cards)
	{
		Cards->SetVisibility(RPGPerf::GateMist());
	}
#endif
	const UWorld* World = GetWorld();
	if (!World || !World->IsGameWorld())
	{
		return;
	}
	if (World->GetTimeSeconds() >= NextRead)
	{
		NextRead = World->GetTimeSeconds() + 0.2;
		State = bCleared ? EState::Cleared : ReadBossState();
	}
	const float Target = State == EState::Closed ? 1.f : (State == EState::Cleared ? 0.f : IdleAmount);
	Amount = FMath::FInterpConstantTo(Amount, Target, DeltaSeconds, 1.f / FMath::Max(0.1f, FadeSeconds));
	ApplyAmount();
	// The doorway is blocked while the boss fight runs (closed), even before the mist is fully grown.
	const ECollisionEnabled::Type Wanted = State == EState::Closed ? ECollisionEnabled::QueryAndPhysics : ECollisionEnabled::NoCollision;
	if (Blocker->GetCollisionEnabled() != Wanted)
	{
		Blocker->SetCollisionEnabled(Wanted);
	}
}

void ARPGFogGate::ApplyAmount()
{
	const int32 Count = Cards->GetInstanceCount();
	if (Count == 0)
	{
		return;
	}
	Cards->SetVisibility(Amount > 0.01f);
	for (int32 Index = 0; Index < Count; ++Index)
	{
		const float Y = (Index - (Count - 1) * 0.5f) * CardSpacing;
		const float Z = -BlockerHalfExtent.Z + 40.f + (Index % 3) * 140.f;
		Cards->UpdateInstanceTransform(Index, FTransform(FRotator(90.f, 0.f, 0.f), FVector(0.f, Y, Z), FVector(CardScale * FMath::Max(Amount, 0.001f))), false, Index == Count - 1, true);
	}
}
