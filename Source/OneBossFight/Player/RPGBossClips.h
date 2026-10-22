// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Animation/AnimSequenceBase.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/Character.h"

/**
 * Plays the project's own boss clips (Content/OneBossFight/Boss01/Animations, authored by Antigravity on the pack's mannequin skeleton) on the pack boss as dynamic montages in the slot the pack's boss montages use.
 * One place for the slot name and the call, so the attack tracker, the phase roar, the stance break and the riposte play their clips the same way.
 */
namespace RPGBossClips
{
	/** The slot the pack's boss montages play in, read from one of them (not guessed). */
	inline FName SlotName()
	{
		static FName Slot;
		if (Slot.IsNone())
		{
			Slot = TEXT("DefaultSlot");
			const UAnimMontage* Reference = LoadObject<UAnimMontage>(nullptr, TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_Attack01_Montage.GS_Attack01_Montage"));
			if (Reference && Reference->SlotAnimTracks.Num() > 0)
			{
				Slot = Reference->SlotAnimTracks[0].SlotName;
			}
		}
		return Slot;
	}

	/** The name of the animation asset a (dynamic) montage plays: the asset of its first segment, the montage's own name when it has none. For tests and logs (Python cannot read the montage's segments). */
	inline FString MontageAnimName(const UAnimMontage* Montage)
	{
		if (!Montage)
		{
			return FString();
		}
		if (Montage->SlotAnimTracks.Num() > 0 && Montage->SlotAnimTracks[0].AnimTrack.AnimSegments.Num() > 0)
		{
			if (const UAnimSequenceBase* Anim = Montage->SlotAnimTracks[0].AnimTrack.AnimSegments[0].GetAnimReference())
			{
				return Anim->GetName();
			}
		}
		return Montage->GetName();
	}

	/** Plays Clip as a dynamic montage on the character's mesh. PlayRate below zero plays it backwards from StartTime (clip seconds); Loops is the number of plays (1 = once). Returns the montage, null when it cannot play. */
	inline UAnimMontage* Play(const ACharacter* Character, UAnimSequenceBase* Clip, float BlendIn, float BlendOut, float PlayRate = 1.f, int32 Loops = 1, float StartTime = 0.f)
	{
		UAnimInstance* Anim = Character && Character->GetMesh() ? Character->GetMesh()->GetAnimInstance() : nullptr;
		if (!Anim || !Clip)
		{
			return nullptr;
		}
		return Anim->PlaySlotAnimationAsDynamicMontage(Clip, SlotName(), BlendIn, BlendOut, PlayRate, Loops, -1.f, StartTime);
	}
}
