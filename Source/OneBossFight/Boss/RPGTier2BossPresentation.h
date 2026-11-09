// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "UObject/SoftObjectPtr.h"
#include "RPGTier2BossPresentation.generated.h"

class UAnimMontage;
class UNiagaraComponent;
class UNiagaraSystem;

/** Config-enabled Tier 2 effects on the live pack boss. Attached by RPGPlayerMovesSubsystem on either route. */
UCLASS(ClassGroup = (Boss))
class ONEBOSSFIGHT_API URPGTier2BossPresentation : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGTier2BossPresentation();

	/** Called only from URPGPlayerParry::NotifyParried after a successful player parry. */
	bool PlayParryRecoil();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Tier2")
	TSoftObjectPtr<UNiagaraSystem> PhaseTwoAuraEffect;

	/** Optional mesh socket for the phase-two aura. NAME_None preserves the approved mesh-origin attachment. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Tier2")
	FName AuraAttachSocket = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Tier2")
	TSoftObjectPtr<UAnimMontage> ParryRecoilMontage;

protected:
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
	void ClearAura();

	UPROPERTY(Transient)
	TObjectPtr<UNiagaraComponent> AuraComponent = nullptr;
	bool bAuraActivatedThisPhase = false;
};
