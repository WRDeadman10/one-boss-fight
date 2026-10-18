// Copyright One Boss Fight. All Rights Reserved.

#include "Combat/RPGMontageUtils.h"
#include "Animation/AnimMontage.h"

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
