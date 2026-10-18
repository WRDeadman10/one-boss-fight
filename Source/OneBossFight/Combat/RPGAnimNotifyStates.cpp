// Copyright One Boss Fight. All Rights Reserved.

#include "Combat/RPGAnimNotifyStates.h"
#include "Combat/RPGCombatComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Particles/ParticleSystem.h"
#include "Sound/SoundBase.h"

URPGCombatComponent* URPGAnimNotifyStateBase::GetCombat(const USkeletalMeshComponent* MeshComp)
{
	const AActor* Owner = MeshComp ? MeshComp->GetOwner() : nullptr;
	return Owner ? Owner->FindComponentByClass<URPGCombatComponent>() : nullptr;
}

void URPGANS_HitWindow::NotifyBegin(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, float TotalDuration, const FAnimNotifyEventReference& EventReference)
{
	Super::NotifyBegin(MeshComp, Animation, TotalDuration, EventReference);
	if (URPGCombatComponent* Combat = GetCombat(MeshComp))
	{
		Combat->SetHitWindow(true);
	}
}

void URPGANS_HitWindow::NotifyEnd(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, const FAnimNotifyEventReference& EventReference)
{
	Super::NotifyEnd(MeshComp, Animation, EventReference);
	if (URPGCombatComponent* Combat = GetCombat(MeshComp))
	{
		Combat->SetHitWindow(false);
	}
}

void URPGANS_ComboWindow::NotifyBegin(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, float TotalDuration, const FAnimNotifyEventReference& EventReference)
{
	Super::NotifyBegin(MeshComp, Animation, TotalDuration, EventReference);
	if (URPGCombatComponent* Combat = GetCombat(MeshComp))
	{
		Combat->SetComboWindow(true);
	}
}

void URPGANS_ComboWindow::NotifyEnd(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, const FAnimNotifyEventReference& EventReference)
{
	Super::NotifyEnd(MeshComp, Animation, EventReference);
	if (URPGCombatComponent* Combat = GetCombat(MeshComp))
	{
		Combat->SetComboWindow(false);
	}
}

void URPGANS_IFrames::NotifyBegin(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, float TotalDuration, const FAnimNotifyEventReference& EventReference)
{
	Super::NotifyBegin(MeshComp, Animation, TotalDuration, EventReference);
	if (URPGCombatComponent* Combat = GetCombat(MeshComp))
	{
		Combat->SetInvulnerable(true);
	}
}

void URPGANS_IFrames::NotifyEnd(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, const FAnimNotifyEventReference& EventReference)
{
	Super::NotifyEnd(MeshComp, Animation, EventReference);
	if (URPGCombatComponent* Combat = GetCombat(MeshComp))
	{
		Combat->SetInvulnerable(false);
	}
}

void URPGANS_CancelWindow::NotifyBegin(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, float TotalDuration, const FAnimNotifyEventReference& EventReference)
{
	Super::NotifyBegin(MeshComp, Animation, TotalDuration, EventReference);
	if (URPGCombatComponent* Combat = GetCombat(MeshComp))
	{
		Combat->SetCancelWindow(true);
	}
}

void URPGANS_CancelWindow::NotifyEnd(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, const FAnimNotifyEventReference& EventReference)
{
	Super::NotifyEnd(MeshComp, Animation, EventReference);
	if (URPGCombatComponent* Combat = GetCombat(MeshComp))
	{
		Combat->SetCancelWindow(false);
	}
}

void URPGAN_RadialHit::Notify(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, const FAnimNotifyEventReference& EventReference)
{
	Super::Notify(MeshComp, Animation, EventReference);

	const AActor* Owner = MeshComp ? MeshComp->GetOwner() : nullptr;
	URPGCombatComponent* Combat = Owner ? Owner->FindComponentByClass<URPGCombatComponent>() : nullptr;
	if (Owner && Combat)
	{
		const FVector Center = Owner->GetActorLocation() + Owner->GetActorForwardVector() * ForwardOffset;
		Combat->ApplyRadialHit(Center, Radius);

		const FVector Ground = Center - FVector(0.f, 0.f, EffectGroundDrop);
		if (Effect && Owner->GetWorld())
		{
			UGameplayStatics::SpawnEmitterAtLocation(Owner->GetWorld(), Effect, Ground, Owner->GetActorRotation(), true);
		}
		if (Sound && Owner->GetWorld())
		{
			UGameplayStatics::PlaySoundAtLocation(Owner->GetWorld(), Sound, Ground);
		}
	}
}
