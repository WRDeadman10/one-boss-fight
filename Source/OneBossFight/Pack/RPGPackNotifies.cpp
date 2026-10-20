// Copyright One Boss Fight. All Rights Reserved.

#include "Pack/RPGPackNotifies.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "NiagaraFunctionLibrary.h"
#include "NiagaraSystem.h"
#include "Sound/SoundBase.h"

void URPGAN_SpawnEffect::Notify(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, const FAnimNotifyEventReference& EventReference)
{
	Super::Notify(MeshComp, Animation, EventReference);

	const AActor* Owner = MeshComp ? MeshComp->GetOwner() : nullptr;
	UWorld* World = Owner ? Owner->GetWorld() : nullptr;
	if (!World)
	{
		return;
	}

	const FVector Where = Owner->GetActorLocation() + Owner->GetActorForwardVector() * ForwardOffset - FVector(0.f, 0.f, GroundDrop);
	if (NiagaraEffect)
	{
		UNiagaraFunctionLibrary::SpawnSystemAtLocation(World, NiagaraEffect, Where, Owner->GetActorRotation(), FVector(Scale));
	}
	if (Sound)
	{
		UGameplayStatics::PlaySoundAtLocation(World, Sound, Where);
	}
}

void URPGANS_ChargeToTarget::NotifyTick(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, float FrameDeltaTime, const FAnimNotifyEventReference& EventReference)
{
	Super::NotifyTick(MeshComp, Animation, FrameDeltaTime, EventReference);

	ACharacter* Character = MeshComp ? Cast<ACharacter>(MeshComp->GetOwner()) : nullptr;
	const APawn* Target = Character ? UGameplayStatics::GetPlayerPawn(Character, 0) : nullptr;
	UCharacterMovementComponent* Movement = Character ? Character->GetCharacterMovement() : nullptr;
	if (!Movement || !Target)
	{
		return;
	}

	FVector ToTarget = Target->GetActorLocation() - Character->GetActorLocation();
	ToTarget.Z = 0.f;
	const float Distance = ToTarget.Size();
	if (Distance <= StopDistance)
	{
		return;
	}

	// Montage time left in the window, converted to real time with the current play rate.
	float RemainingReal = 0.1f;
	if (const UAnimMontage* Montage = Cast<UAnimMontage>(Animation))
	{
		if (const UAnimInstance* Anim = MeshComp->GetAnimInstance())
		{
			const float Rate = FMath::Max(FMath::Abs(Anim->Montage_GetPlayRate(Montage)), 0.05f);
			RemainingReal = FMath::Max((WindowEndTime - Anim->Montage_GetPosition(Montage)) / Rate, 0.05f);
		}
	}
	const float Speed = FMath::Min((Distance - StopDistance) / RemainingReal, MaxSpeed);
	const FVector Direction = ToTarget / Distance;
	Movement->Velocity = FVector(Direction.X * Speed, Direction.Y * Speed, Movement->Velocity.Z);
}
