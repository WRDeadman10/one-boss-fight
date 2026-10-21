// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossJavelin.h"
#include "Components/PointLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Pack/RPGBlueprintCall.h"
#include "Player/RPGBossDamage.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossHealPunish.h"
#include "UObject/ConstructorHelpers.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGJavelin, Log, All);

using namespace RPGPack;

namespace
{
	// A hit on geometry the javelin starts inside of is ignored for this many cm of flight (a boss with its back to a wall).
	constexpr float LeaveHandDistance = 150.f;
}

ARPGBossJavelin::ARPGBossJavelin()
{
	PrimaryActorTick.bCanEverTick = true;
	SetCanBeDamaged(false);

	Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
	SetRootComponent(Mesh);
	Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision); // moved and tested by sweeps in Tick
	Mesh->SetCastShadow(false);
	// Antigravity's javelin (160 cm, origin at the tail, point along +X, three slots) when it is imported; else an engine cylinder as a thin 140 cm spear.
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Javelin(TEXT("/Game/OneBossFight/Boss01/Weapons/SM_Boss01_EmberJavelin.SM_Boss01_EmberJavelin"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Cylinder(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	if (Javelin.Succeeded())
	{
		Mesh->SetStaticMesh(Javelin.Object);
	}
	else if (Cylinder.Succeeded())
	{
		Mesh->SetStaticMesh(Cylinder.Object);
		// The cylinder's axis is Z; turn it along X (the flight direction).
		Mesh->SetRelativeRotation(FRotator(90.f, 0.f, 0.f));
		Mesh->SetRelativeScale3D(FVector(0.06f, 0.06f, 1.4f));
	}

	Glow = CreateDefaultSubobject<UPointLightComponent>(TEXT("Glow"));
	Glow->SetupAttachment(Mesh);
	Glow->SetLightColor(FLinearColor(1.f, 0.45f, 0.1f));
	Glow->SetIntensity(6000.f);
	Glow->SetAttenuationRadius(450.f);
	Glow->SetCastShadows(false);
}

void ARPGBossJavelin::Launch(URPGBossHealPunish* InOwner, const FVector& InDirection, float InSpeed, float InRadius, float InDamage, float InMaxRange, int32 InGeneration)
{
	Source = InOwner;
	Direction = InDirection.GetSafeNormal();
	Speed = InSpeed;
	Radius = InRadius;
	Damage = InDamage;
	MaxRange = InMaxRange;
	Generation = InGeneration;
	SetActorRotation(Direction.Rotation());
	// Placeholder materials until the javelin has its own: the engine's tintable basic material on every slot (iron, grip, ember band; the light does the glowing).
	UMaterialInterface* Base = LoadObject<UMaterialInterface>(nullptr, TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
	static const FLinearColor SlotColors[] = {FLinearColor(0.05f, 0.05f, 0.06f), FLinearColor(0.12f, 0.06f, 0.03f), FLinearColor(1.f, 0.4f, 0.05f)};
	for (int32 Slot = 0; Base && Slot < Mesh->GetNumMaterials(); ++Slot)
	{
		if (UMaterialInstanceDynamic* Material = Mesh->CreateDynamicMaterialInstance(Slot, Base))
		{
			Material->SetVectorParameterValue(TEXT("Color"), SlotColors[FMath::Min(Slot, 2)]);
		}
	}
}

void ARPGBossJavelin::Finish(ERPGJavelinResult Result, const TCHAR* Reason)
{
	if (bFinished)
	{
		return;
	}
	bFinished = true;
	UE_LOG(LogRPGJavelin, Log, TEXT("javelin ended (%s) after %.0f cm"), Reason, Travelled);
	if (URPGBossHealPunish* Punish = Source.Get())
	{
		Punish->ReportJavelin(Result);
	}
	Destroy();
}

void ARPGBossJavelin::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	URPGBossHealPunish* Punish = Source.Get();
	AActor* Boss = Punish ? Punish->GetOwner() : nullptr;
	if (bFinished || !Boss)
	{
		Finish(ERPGJavelinResult::Cancelled, TEXT("the boss is gone"));
		return;
	}
	// A javelin belongs to the fight that threw it (Freeze 32.2).
	const URPGBossEncounter* Encounter = Boss->FindComponentByClass<URPGBossEncounter>();
	double BossHealth = 1.0;
	ReadAttribute(Boss, TEXT("Attribute.Health"), false, BossHealth);
	if (BossHealth <= 0.0 || (Encounter && Encounter->GetGeneration() != Generation))
	{
		Finish(ERPGJavelinResult::Cancelled, BossHealth <= 0.0 ? TEXT("boss dead") : TEXT("encounter reset"));
		return;
	}

	const FVector Start = GetActorLocation();
	const float Step = Speed * DeltaSeconds;
	const FVector End = Start + Direction * Step;
	FCollisionQueryParams Params(SCENE_QUERY_STAT(RPGJavelin), false);
	Params.AddIgnoredActor(Boss);
	Params.AddIgnoredActor(this);
	const FCollisionShape Shape = FCollisionShape::MakeSphere(Radius);

	FHitResult WorldHit;
	bool bWorld = GetWorld()->SweepSingleByObjectType(WorldHit, Start, End, FQuat::Identity, RPGBossDamage::WorldBlockers(), Shape, Params);
	if (bWorld && WorldHit.bStartPenetrating && Travelled < LeaveHandDistance)
	{
		bWorld = false; // the boss stands against a wall and its hand is inside the wall's collision: the javelin leaves the wall, it does not die in it
	}
	FHitResult PawnHit;
	const bool bPawn = GetWorld()->SweepSingleByObjectType(PawnHit, Start, End, FQuat::Identity, FCollisionObjectQueryParams(ECC_Pawn), Shape, Params);
	ACharacter* Player = Cast<ACharacter>(UGameplayStatics::GetPlayerPawn(this, 0));
	const bool bPlayerHit = bPawn && Player && PawnHit.GetActor() == Player;

	if (bPlayerHit && (!bWorld || PawnHit.Time <= WorldHit.Time))
	{
		if (RPGBossDamage::IsInvulnerable(Player))
		{
			if (!bDodgedCounted)
			{
				bDodgedCounted = true;
				UE_LOG(LogRPGJavelin, Log, TEXT("javelin passes through the player: invulnerable (dodge i-frames)"));
				Punish->ReportJavelin(ERPGJavelinResult::Dodged);
			}
		}
		else if (RPGBossDamage::IsAlive(Player))
		{
			double Before = 0.0;
			double After = 0.0;
			if (RPGBossDamage::HurtPlayer(Player, Damage, Before, After))
			{
				UE_LOG(LogRPGJavelin, Log, TEXT("javelin hit the player after %.0f cm: health %.0f -> %.0f"), Travelled + Step * PawnHit.Time, Before, After);
			}
			Finish(ERPGJavelinResult::Hit, TEXT("hit the player"));
			return;
		}
	}
	else if (bWorld)
	{
		Finish(ERPGJavelinResult::HitWorld, *FString::Printf(TEXT("hit %s"), *GetNameSafe(WorldHit.GetActor())));
		return;
	}

	SetActorLocation(End);
	Travelled += Step;
	if (Travelled >= MaxRange)
	{
		Finish(ERPGJavelinResult::Expired, TEXT("max range"));
	}
}
