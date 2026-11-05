// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/SoftObjectPtr.h"

class UNiagaraSystem;
class UNiagaraComponent;
class UWorld;

namespace RPGTier1Visuals
{
	/** Uses authored overrides in every build; the built-in Tier 1 preview is opt-in in Development. */
	inline TSoftObjectPtr<UNiagaraSystem> SelectEffect(const TSoftObjectPtr<UNiagaraSystem>& Authored,
		const TCHAR* Tier1Path, bool bTier1PreviewEnabled)
	{
		if (!Authored.IsNull()) return Authored;
		return bTier1PreviewEnabled ? TSoftObjectPtr<UNiagaraSystem>(FSoftObjectPath(Tier1Path)) : TSoftObjectPtr<UNiagaraSystem>();
	}

	/** Always false outside Development: authored references remain usable there. */
	ONEBOSSFIGHT_API bool IsTier1PreviewEnabled();
	ONEBOSSFIGHT_API UNiagaraComponent* SpawnConfiguredEffect(UWorld* World,
		const TSoftObjectPtr<UNiagaraSystem>& Authored, const TCHAR* Tier1Path,
		const FVector& Location, const FRotator& Rotation, const FVector& Scale = FVector::OneVector);
}
