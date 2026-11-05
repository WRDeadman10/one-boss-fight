// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGTier1VisualRules.h"
#include "NiagaraComponent.h"
#include "NiagaraFunctionLibrary.h"
#include "NiagaraSystem.h"
#include "Engine/World.h"

#if UE_BUILD_DEVELOPMENT
#include "HAL/IConsoleManager.h"
namespace
{
	TAutoConsoleVariable<int32> CVarTier1Art(TEXT("rpg.Art.Tier1"), 0,
		TEXT("Development-only Tier 1 Niagara preview when a visual override field is empty."), ECVF_Default);
	TAutoConsoleVariable<int32> CVarTier2Art(TEXT("rpg.Art.Tier2"), 0,
		TEXT("Development-only opt-in for optional Tier 2 presentation hooks."), ECVF_Default);
}
#endif

bool RPGTier1Visuals::IsTier1PreviewEnabled()
{
#if UE_BUILD_DEVELOPMENT
	return CVarTier1Art.GetValueOnGameThread() != 0;
#else
	return false;
#endif
}

bool RPGTier1Visuals::IsTier2PreviewEnabled()
{
#if UE_BUILD_DEVELOPMENT
	return RPGPresentationRules::IsTier2PreviewEnabledForBuild(true, CVarTier2Art.GetValueOnGameThread());
#else
	return RPGPresentationRules::IsTier2PreviewEnabledForBuild(false, 0);
#endif
}

UNiagaraComponent* RPGTier1Visuals::SpawnConfiguredEffect(UWorld* World,
	const TSoftObjectPtr<UNiagaraSystem>& Authored, const TCHAR* Tier1Path,
	const FVector& Location, const FRotator& Rotation, const FVector& Scale)
{
	if (!World) return nullptr;
	const TSoftObjectPtr<UNiagaraSystem> Selected = SelectEffect(Authored, Tier1Path, IsTier1PreviewEnabled());
	if (Selected.IsNull()) return nullptr;
	UNiagaraSystem* System = Selected.LoadSynchronous();
	return System ? UNiagaraFunctionLibrary::SpawnSystemAtLocation(World, System, Location, Rotation, Scale) : nullptr;
}
