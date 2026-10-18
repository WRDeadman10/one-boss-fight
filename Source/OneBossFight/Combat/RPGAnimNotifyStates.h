// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimNotifies/AnimNotify.h"
#include "Animation/AnimNotifies/AnimNotifyState.h"
#include "RPGAnimNotifyStates.generated.h"

class URPGCombatComponent;
class UParticleSystem;
class USoundBase;

/** Shared plumbing: finds the owner's combat component. Does nothing in editor previews that have none. */
UCLASS(Abstract)
class ONEBOSSFIGHT_API URPGAnimNotifyStateBase : public UAnimNotifyState
{
	GENERATED_BODY()

protected:
	static URPGCombatComponent* GetCombat(const USkeletalMeshComponent* MeshComp);
};

/** Damage window: the melee trace sweeps while this is active. */
UCLASS(meta = (DisplayName = "RPG Hit Window"))
class ONEBOSSFIGHT_API URPGANS_HitWindow : public URPGAnimNotifyStateBase
{
	GENERATED_BODY()

public:
	virtual void NotifyBegin(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, float TotalDuration, const FAnimNotifyEventReference& EventReference) override;
	virtual void NotifyEnd(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, const FAnimNotifyEventReference& EventReference) override;
	virtual FString GetNotifyName_Implementation() const override { return TEXT("RPG Hit Window"); }
};

/** The next attack in the chain may start; a buffered attack press is consumed on entry. */
UCLASS(meta = (DisplayName = "RPG Combo Window"))
class ONEBOSSFIGHT_API URPGANS_ComboWindow : public URPGAnimNotifyStateBase
{
	GENERATED_BODY()

public:
	virtual void NotifyBegin(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, float TotalDuration, const FAnimNotifyEventReference& EventReference) override;
	virtual void NotifyEnd(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, const FAnimNotifyEventReference& EventReference) override;
	virtual FString GetNotifyName_Implementation() const override { return TEXT("RPG Combo Window"); }
};

/** Invulnerability frames (dodge). Hits arriving while active are ignored. */
UCLASS(meta = (DisplayName = "RPG I-Frames"))
class ONEBOSSFIGHT_API URPGANS_IFrames : public URPGAnimNotifyStateBase
{
	GENERATED_BODY()

public:
	virtual void NotifyBegin(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, float TotalDuration, const FAnimNotifyEventReference& EventReference) override;
	virtual void NotifyEnd(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, const FAnimNotifyEventReference& EventReference) override;
	virtual FString GetNotifyName_Implementation() const override { return TEXT("RPG I-Frames"); }
};

/** The recovery may be cancelled into a dodge while this is active. */
UCLASS(meta = (DisplayName = "RPG Cancel Window"))
class ONEBOSSFIGHT_API URPGANS_CancelWindow : public URPGAnimNotifyStateBase
{
	GENERATED_BODY()

public:
	virtual void NotifyBegin(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, float TotalDuration, const FAnimNotifyEventReference& EventReference) override;
	virtual void NotifyEnd(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, const FAnimNotifyEventReference& EventReference) override;
	virtual FString GetNotifyName_Implementation() const override { return TEXT("RPG Cancel Window"); }
};

/** One-shot area hit for shockwaves and slams, centered ForwardOffset ahead of the attacker. */
UCLASS(meta = (DisplayName = "RPG Radial Hit"))
class ONEBOSSFIGHT_API URPGAN_RadialHit : public UAnimNotify
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Radial Hit", meta = (ClampMin = "1"))
	float Radius = 300.f;

	/** Distance in front of the attacker (negative = behind). Zero centers on the attacker. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Radial Hit")
	float ForwardOffset = 0.f;

	/** Spawned at the center of the hit, on the ground. Optional. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Radial Hit")
	TObjectPtr<UParticleSystem> Effect;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Radial Hit")
	TObjectPtr<USoundBase> Sound;

	/** Lowers the effect from the actor origin to the floor (half the capsule height is typical). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Radial Hit")
	float EffectGroundDrop = 0.f;

	virtual void Notify(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, const FAnimNotifyEventReference& EventReference) override;
	virtual FString GetNotifyName_Implementation() const override { return TEXT("RPG Radial Hit"); }
};
