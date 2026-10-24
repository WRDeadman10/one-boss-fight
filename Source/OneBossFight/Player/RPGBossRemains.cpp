// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossRemains.h"

#include "Components/StaticMeshComponent.h"
#include "HAL/IConsoleManager.h"
#include "EngineUtils.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "NiagaraFunctionLibrary.h"
#include "NiagaraSystem.h"

namespace
{
	const TCHAR* RemainsMeshPath = TEXT("/Game/OneBossFight/Boss01/Remains/SM_Boss01_CorpseStatue.SM_Boss01_CorpseStatue");
	const TCHAR* RemainsMaterialPath = TEXT("/Game/OneBossFight/Boss01/Remains/M_Boss01_Remains.M_Boss01_Remains");
	const TCHAR* BurstPath = TEXT("/Game/BloodPack/Hit/Niagara/NS_BulletHit_Med.NS_BulletHit_Med");

#if !UE_BUILD_SHIPPING
	TAutoConsoleVariable<float> CVarRemainsFormSeconds(
		TEXT("rpg.RemainsFormSeconds"), 2.5f,
		TEXT("Seconds for the boss monument to dissolve in."), ECVF_Default);
#endif

	FLinearColor TintForSlot(FName SlotName)
	{
		if (SlotName == TEXT("M_Boss01_EmberCore"))
		{
			return FLinearColor(0.9f, 0.28f, 0.04f);
		}
		if (SlotName == TEXT("M_Boss01_AncientSteel"))
		{
			return FLinearColor(0.05f, 0.055f, 0.065f);
		}
		return FLinearColor(0.10f, 0.095f, 0.09f);
	}

	float CoreGlowForSlot(FName SlotName)
	{
		return SlotName == TEXT("M_Boss01_EmberCore") ? 0.45f : 0.f;
	}
}

ARPGBossRemains::ARPGBossRemains()
{
	PrimaryActorTick.bCanEverTick = true;
	SetCanBeDamaged(false);
	Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RemainsMesh"));
	SetRootComponent(Mesh);
	Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
}

void ARPGBossRemains::PreloadAssets(UStaticMesh*& OutMesh, UMaterialInterface*& OutMaterial, UNiagaraSystem*& OutBurst)
{
	OutMesh = TSoftObjectPtr<UStaticMesh>(FSoftObjectPath(RemainsMeshPath)).LoadSynchronous();
	OutMaterial = TSoftObjectPtr<UMaterialInterface>(FSoftObjectPath(RemainsMaterialPath)).LoadSynchronous();
	OutBurst = TSoftObjectPtr<UNiagaraSystem>(FSoftObjectPath(BurstPath)).LoadSynchronous();
}

ARPGBossRemains* ARPGBossRemains::Spawn(UWorld* World, const FTransform& Transform, UStaticMesh* InMesh, UMaterialInterface* InMaterial, UNiagaraSystem* InBurst)
{
	if (!World || World->bIsTearingDown || !InMesh || !InMaterial)
	{
		return nullptr;
	}
	ARPGBossRemains* Remains = World->SpawnActorDeferred<ARPGBossRemains>(StaticClass(), Transform, nullptr, nullptr, ESpawnActorCollisionHandlingMethod::AlwaysSpawn);
	if (!Remains)
	{
		return nullptr;
	}
	Remains->Initialize(InMesh, InMaterial, InBurst);
	Remains->FinishSpawning(Transform);
	return Remains;
}

void ARPGBossRemains::DestroyForWorld(UWorld* World)
{
	if (!World)
	{
		return;
	}
	for (TActorIterator<ARPGBossRemains> It(World); It; ++It)
	{
		It->Destroy();
	}
}

void ARPGBossRemains::Initialize(UStaticMesh* InMesh, UMaterialInterface* InMaterial, UNiagaraSystem* InBurst)
{
	LoadedMesh = InMesh;
	LoadedMaterial = InMaterial;
	LoadedBurst = InBurst;
	Mesh->SetStaticMesh(LoadedMesh);
	ApplyMaterials();
	if (LoadedBurst)
	{
		UNiagaraFunctionLibrary::SpawnSystemAtLocation(GetWorld(), LoadedBurst, GetActorLocation(), GetActorRotation());
	}
}

void ARPGBossRemains::ApplyMaterials()
{
	SlotCount = Mesh && Mesh->GetStaticMesh() ? Mesh->GetStaticMesh()->GetStaticMaterials().Num() : 0;
	Materials.Reset();
	for (int32 Slot = 0; Mesh && LoadedMaterial && Slot < SlotCount; ++Slot)
	{
		const FName SlotName = Mesh->GetStaticMesh()->GetStaticMaterials()[Slot].MaterialSlotName;
		if (UMaterialInstanceDynamic* Mid = Mesh->CreateDynamicMaterialInstance(Slot, LoadedMaterial))
		{
			Mid->SetVectorParameterValue(TEXT("Tint"), TintForSlot(SlotName));
			Mid->SetScalarParameterValue(TEXT("EmissiveBoost"), 1.f);
			Mid->SetScalarParameterValue(TEXT("CoreGlow"), CoreGlowForSlot(SlotName));
			Materials.Add(Mid);
		}
	}
	ApplyDissolve(0.f);
}

void ARPGBossRemains::ApplyDissolve(float Value)
{
	Dissolve = Value;
	for (UMaterialInstanceDynamic* Mid : Materials)
	{
		if (Mid)
		{
			Mid->SetScalarParameterValue(TEXT("Dissolve"), Dissolve);
		}
	}
}

float ARPGBossRemains::GetFormSeconds()
{
#if UE_BUILD_SHIPPING
	return 2.5f;
#else
	return FMath::Max(CVarRemainsFormSeconds.GetValueOnGameThread(), KINDA_SMALL_NUMBER);
#endif
}

void ARPGBossRemains::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (bFinished)
	{
		return;
	}
	Elapsed += DeltaSeconds;
	const RPGBossRemainsRules::FSample Sample = RPGBossRemainsRules::Sample(Elapsed, GetFormSeconds());
	ApplyDissolve(Sample.Dissolve);
	bFinished = Sample.bFinished;
	if (bFinished)
	{
		SetActorTickEnabled(false);
	}
}
