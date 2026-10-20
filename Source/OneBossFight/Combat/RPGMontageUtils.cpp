// Copyright One Boss Fight. All Rights Reserved.

#include "Combat/RPGMontageUtils.h"
#include "Animation/AnimMontage.h"
#include "Animation/AnimNotifies/AnimNotify.h"
#include "Animation/AnimNotifies/AnimNotifyState.h"

int32 URPGMontageUtils::SetMontageSlot(UAnimMontage* Montage, FName SlotName)
{
	if (!Montage)
	{
		return 0;
	}

	int32 Changed = 0;
	for (FSlotAnimationTrack& Track : Montage->SlotAnimTracks)
	{
		if (Track.SlotName != SlotName)
		{
			Track.SlotName = SlotName;
			++Changed;
		}
	}
	if (Changed > 0)
	{
		Montage->MarkPackageDirty();
	}
	return Changed;
}

FName URPGMontageUtils::GetMontageSlot(const UAnimMontage* Montage)
{
	return (Montage && Montage->SlotAnimTracks.Num() > 0) ? Montage->SlotAnimTracks[0].SlotName : NAME_None;
}

TArray<FString> URPGMontageUtils::DescribeNotifies(const UAnimMontage* Montage)
{
	TArray<FString> Lines;
	if (!Montage)
	{
		return Lines;
	}
	Lines.Add(FString::Printf(TEXT("length %.3f s, rate scale %.2f, sections %d, blend in %.2f out %.2f"), Montage->GetPlayLength(), Montage->RateScale, Montage->CompositeSections.Num(),
		Montage->BlendIn.GetBlendTime(), Montage->BlendOut.GetBlendTime()));
	for (const FAnimNotifyEvent& Event : Montage->Notifies)
	{
		const FString Kind = Event.NotifyStateClass ? Event.NotifyStateClass->GetClass()->GetName() : (Event.Notify ? Event.Notify->GetClass()->GetName() : Event.NotifyName.ToString());
		Lines.Add(FString::Printf(TEXT("%s%s at %.3f s%s"), Event.NotifyStateClass ? TEXT("[state] ") : TEXT(""), *Kind, Event.GetTriggerTime(),
			Event.NotifyStateClass ? *FString::Printf(TEXT(" for %.3f s"), Event.GetDuration()) : TEXT("")));
	}
	return Lines;
}
