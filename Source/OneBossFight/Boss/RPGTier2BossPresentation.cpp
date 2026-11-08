// Copyright One Boss Fight. All Rights Reserved.
#include "Boss/RPGTier2BossPresentation.h"
#include "Boss/RPGTier2BossRules.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/Character.h"
#include "NiagaraComponent.h"
#include "NiagaraFunctionLibrary.h"
#include "NiagaraSystem.h"
#include "Pack/RPGBlueprintCall.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGTier1VisualRules.h"

URPGTier2BossPresentation::URPGTier2BossPresentation()
{
	PrimaryComponentTick.bCanEverTick = UE_BUILD_DEVELOPMENT != 0;
	PrimaryComponentTick.TickInterval = 0.1f;
	PhaseTwoAuraEffect = TSoftObjectPtr<UNiagaraSystem>(FSoftObjectPath(TEXT("/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura.NS_Boss_PhaseTwoAura")));
	ParryRecoilMontage = TSoftObjectPtr<UAnimMontage>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Animations/AM_Boss01_ParryRecoil.AM_Boss01_ParryRecoil")));
}

void URPGTier2BossPresentation::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	const bool bTier2Enabled = RPGTier1Visuals::IsTier2PreviewEnabled();
	if (!bTier2Enabled)
	{
		ClearAura();
		return;
	}
	AActor* Boss = GetOwner();
	double Health = 0., MaxHealth = 0.;
	const bool bHealthRead = Boss && RPGPack::ReadAttribute(Boss, TEXT("Attribute.Health"), false, Health)
		&& RPGPack::ReadAttribute(Boss, TEXT("Attribute.Health"), true, MaxHealth);
	const URPGBossEncounter* Encounter = Boss ? Boss->FindComponentByClass<URPGBossEncounter>() : nullptr;
	const bool bShow = bHealthRead && RPGTier2BossRules::ShouldShowAura(bTier2Enabled,
		Health, MaxHealth, Encounter && Encounter->IsDormant());
	if (!bShow)
	{
		ClearAura();
		return;
	}
	if (!RPGTier2BossRules::ShouldSpawnAura(bTier2Enabled, Health, MaxHealth, false, bAuraActivatedThisPhase))
	{
		return;
	}
	ACharacter* Character = Cast<ACharacter>(Boss);
	USkeletalMeshComponent* Mesh = Character ? Character->GetMesh() : nullptr;
	UNiagaraSystem* Aura = Mesh ? PhaseTwoAuraEffect.LoadSynchronous() : nullptr;
	if (Aura)
	{
		AuraComponent = UNiagaraFunctionLibrary::SpawnSystemAttached(Aura, Mesh, NAME_None, FVector::ZeroVector,
			FRotator::ZeroRotator, EAttachLocation::KeepRelativeOffset, true);
		bAuraActivatedThisPhase = IsValid(AuraComponent);
	}
}

bool URPGTier2BossPresentation::PlayParryRecoil()
{
	if (!RPGTier2BossRules::ShouldPlayParryRecoil(RPGTier1Visuals::IsTier2PreviewEnabled(), true))
	{
		return false;
	}
	ACharacter* Character = Cast<ACharacter>(GetOwner());
	UAnimInstance* Anim = Character && Character->GetMesh() ? Character->GetMesh()->GetAnimInstance() : nullptr;
	UAnimMontage* Montage = Anim ? ParryRecoilMontage.LoadSynchronous() : nullptr;
	return Montage && Anim->Montage_Play(Montage, 1.f) > 0.f;
}

void URPGTier2BossPresentation::ClearAura()
{
	if (IsValid(AuraComponent))
	{
		AuraComponent->DestroyComponent();
	}
	AuraComponent = nullptr;
	bAuraActivatedThisPhase = false;
}

void URPGTier2BossPresentation::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	ClearAura();
	Super::EndPlay(EndPlayReason);
}
