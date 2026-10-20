// Copyright One Boss Fight. All Rights Reserved.

#include "Audio/RPGFootsteps.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundAttenuation.h"
#include "Sound/SoundBase.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGFootsteps, Log, All);

URPGFootsteps::URPGFootsteps()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickGroup = TG_PostPhysics; // after animation has posed the bones this frame
}

void URPGFootsteps::BeginPlay()
{
	Super::BeginPlay();
	Character = Cast<ACharacter>(GetOwner());
	Feet[0].Bone = LeftFootBone;
	Feet[1].Bone = RightFootBone;
	Attenuation = NewObject<USoundAttenuation>(this);
	FSoundAttenuationSettings& Settings = Attenuation->Attenuation;
	Settings.bAttenuate = true;
	Settings.bSpatialize = true;
	Settings.AttenuationShape = EAttenuationShape::Sphere;
	Settings.AttenuationShapeExtents = FVector(300.f, 0.f, 0.f);
	Settings.FalloffDistance = AudibleRange;
	if (Character)
	{
		Character->LandedDelegate.AddDynamic(this, &URPGFootsteps::OnLanded);
	}
}

void URPGFootsteps::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if (Character)
	{
		Character->LandedDelegate.RemoveDynamic(this, &URPGFootsteps::OnLanded);
	}
	Super::EndPlay(EndPlayReason);
}

USoundBase* URPGFootsteps::PickSound(float Speed) const
{
	if (Speed >= RunSpeed && RunSound)
	{
		return RunSound;
	}
	if (Speed >= JogSpeed && JogSound)
	{
		return JogSound;
	}
	return WalkSound ? WalkSound.Get() : (JogSound ? JogSound.Get() : RunSound.Get());
}

void URPGFootsteps::PlayAt(USoundBase* Sound, const FVector& Location, float Volume, float Pitch) const
{
	if (Sound && GetWorld())
	{
		UGameplayStatics::PlaySoundAtLocation(GetWorld(), Sound, Location, FRotator::ZeroRotator, Volume * VolumeScale, Pitch * PitchScale, 0.f, Attenuation);
	}
}

void URPGFootsteps::OnLanded(const FHitResult& Hit)
{
	if (!Character)
	{
		return;
	}
	const float Fall = FMath::Clamp(-Character->GetCharacterMovement()->Velocity.Z / 900.f, 0.5f, 1.4f);
	PlayAt(LandSound, Character->GetActorLocation() - FVector(0.f, 0.f, Character->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()), Fall, FMath::RandRange(0.95f, 1.05f));
}

void URPGFootsteps::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	if (!Character)
	{
		return;
	}
	USkeletalMeshComponent* Mesh = Character->GetMesh();
	UCharacterMovementComponent* Movement = Character->GetCharacterMovement();
	if (!Mesh || !Movement)
	{
		return;
	}
	const float HalfHeight = Character->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
	const float FloorZ = Character->GetActorLocation().Z - HalfHeight;
	const float BodyScale = HalfHeight / 98.f;
	const float Speed = Movement->Velocity.Size2D();
	for (FFootState& Foot : Feet)
	{
		Foot.Cooldown = FMath::Max(0.f, Foot.Cooldown - DeltaTime);
		if (Mesh->GetBoneIndex(Foot.Bone) == INDEX_NONE)
		{
			if (!bWarnedMissingBones)
			{
				UE_LOG(LogRPGFootsteps, Warning, TEXT("%s has no bone %s: no footsteps"), *GetNameSafe(Character), *Foot.Bone.ToString());
				bWarnedMissingBones = true;
			}
			continue;
		}
		const FVector Position = Mesh->GetBoneLocation(Foot.Bone, EBoneSpaces::WorldSpace);
		const float Height = Position.Z - FloorZ;
		// The planted height of the bone drifts between poses (idle plants lower than a walk), so the reference rises slowly and drops at once.
		Foot.LowestHeight = Foot.bHaveLowest ? FMath::Min(Height, Foot.LowestHeight + DeltaTime * 10.f * BodyScale) : Height;
		Foot.bHaveLowest = true;
		if (Height > Foot.LowestHeight + LiftHeight * BodyScale)
		{
			Foot.bLifted = true;
		}
		else if (Foot.bLifted && Height < Foot.LowestHeight + TouchHeight * BodyScale)
		{
			Foot.bLifted = false;
			// Only a grounded, moving body steps: a foot that swings through the air in an attack makes no sound.
			if (Movement->IsMovingOnGround() && Speed > 40.f && Foot.Cooldown <= 0.f)
			{
				Foot.Cooldown = 0.16f;
				++StepCount;
				const float Loudness = FMath::GetMappedRangeValueClamped(FVector2D(40.f, RunSpeed), FVector2D(0.45f, 1.f), Speed);
				PlayAt(PickSound(Speed), FVector(Position.X, Position.Y, FloorZ), Loudness, FMath::RandRange(0.94f, 1.06f));
			}
		}
	}
}
