// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGFlipbookEffect.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Camera/PlayerCameraManager.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "Math/RotationMatrix.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
	float DurationFor(ERPGEFlipbookKind Kind)
	{
		switch (Kind)
		{
		case ERPGEFlipbookKind::BloodBurst: return 0.6f;
		case ERPGEFlipbookKind::HitSpark: return 0.25f;
		case ERPGEFlipbookKind::DodgeDust: return 0.8f;
		default: return 0.6f;
		}
	}

	float SizeFor(ERPGEFlipbookKind Kind)
	{
		switch (Kind)
		{
		case ERPGEFlipbookKind::BloodBurst: return 140.f;
		case ERPGEFlipbookKind::HitSpark: return 90.f;
		case ERPGEFlipbookKind::DodgeDust: return 220.f;
		default: return 100.f;
		}
	}

	const TCHAR* PathFor(ERPGEFlipbookKind Kind)
	{
		switch (Kind)
		{
		case ERPGEFlipbookKind::BloodBurst: return TEXT("/Game/OneBossFight/Effects/Flipbook/MI_Boss01_FB_BloodBurst.MI_Boss01_FB_BloodBurst");
		case ERPGEFlipbookKind::HitSpark: return TEXT("/Game/OneBossFight/Effects/Flipbook/MI_Boss01_FB_HitSpark.MI_Boss01_FB_HitSpark");
		case ERPGEFlipbookKind::DodgeDust: return TEXT("/Game/OneBossFight/Effects/Flipbook/MI_Boss01_FB_DodgeDust.MI_Boss01_FB_DodgeDust");
		default: return nullptr;
		}
	}
}

ARPGFlipbookEffect::ARPGFlipbookEffect()
{
	PrimaryActorTick.bCanEverTick = true;
	SetCanBeDamaged(false);
	Plane = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Plane"));
	SetRootComponent(Plane);
	Plane->SetMobility(EComponentMobility::Movable); // it turns to the camera every tick: a static component refuses to move at runtime
	Plane->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Plane->SetCastShadow(false);
	static ConstructorHelpers::FObjectFinder<UStaticMesh> BasicPlane(TEXT("/Engine/BasicShapes/Plane.Plane"));
	if (BasicPlane.Succeeded())
	{
		Plane->SetStaticMesh(BasicPlane.Object);
	}
}

UMaterialInterface* ARPGFlipbookEffect::LoadMaterial(ERPGEFlipbookKind Kind)
{
	const TCHAR* Path = PathFor(Kind);
	return Path ? LoadObject<UMaterialInterface>(nullptr, Path) : nullptr;
}

ARPGFlipbookEffect* ARPGFlipbookEffect::Spawn(UWorld* World, const FVector& Location, ERPGEFlipbookKind Kind, UMaterialInterface* Material)
{
	if (!World || !Material)
	{
		return nullptr;
	}
	const float Size = SizeFor(Kind);
	// the dust sits low in its cell (the smudge is about 0.18 of the cell height below the middle): lift a square plane so the smudge lies on the floor
	const FVector SpawnLocation = Location + (Kind == ERPGEFlipbookKind::DodgeDust ? FVector(0.f, 0.f, Size * 0.23f) : FVector::ZeroVector);
	ARPGFlipbookEffect* Effect = World->SpawnActor<ARPGFlipbookEffect>(ARPGFlipbookEffect::StaticClass(), SpawnLocation, FRotator::ZeroRotator);
	if (Effect)
	{
		Effect->Initialize(Kind, Material);
	}
	return Effect;
}

void ARPGFlipbookEffect::Initialize(ERPGEFlipbookKind InKind, UMaterialInterface* Material)
{
	EffectKind = InKind;
	PlaybackSeconds = DurationFor(EffectKind);
	const float Scale = SizeFor(EffectKind) / 100.f;
	Plane->SetRelativeScale3D(FVector(Scale, Scale, 1.f)); // the sheet cells are square: never squash them
	DynamicMaterial = Plane->CreateDynamicMaterialInstance(0, Material);
	if (DynamicMaterial)
	{
		DynamicMaterial->SetScalarParameterValue(TEXT("Frame"), 0.f);
	}
}

void ARPGFlipbookEffect::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (APlayerCameraManager* Camera = UGameplayStatics::GetPlayerCameraManager(this, 0))
	{
		// The engine Plane has u along +X and v along +Y (v runs down the picture): to read upright its X must be the screen right, its Y the screen down and its normal (Z) must point at the camera.
		const FRotationMatrix CameraAxes(Camera->GetCameraRotation());
		SetActorRotation(FRotationMatrix::MakeFromXY(CameraAxes.GetScaledAxis(EAxis::Y), -CameraAxes.GetScaledAxis(EAxis::Z)).Rotator());
	}
	Elapsed += DeltaSeconds;
	const RPGFlipbookRules::FSample Sample = RPGFlipbookRules::Sample(Elapsed, PlaybackSeconds);
	FrameIndex = Sample.Frame;
	if (DynamicMaterial)
	{
		DynamicMaterial->SetScalarParameterValue(TEXT("Frame"), static_cast<float>(FrameIndex));
	}
	if (Sample.bFinished && !bFinishing)
	{
		bFinishing = true;
		SetActorTickEnabled(false); // retain frame 63 for one render frame before removal
		SetLifeSpan(0.05f);
	}
}

FString ARPGFlipbookEffect::GetEffectName() const
{
	switch (EffectKind)
	{
	case ERPGEFlipbookKind::BloodBurst: return TEXT("blood");
	case ERPGEFlipbookKind::HitSpark: return TEXT("spark");
	case ERPGEFlipbookKind::DodgeDust: return TEXT("dust");
	default: return TEXT("unknown");
	}
}
