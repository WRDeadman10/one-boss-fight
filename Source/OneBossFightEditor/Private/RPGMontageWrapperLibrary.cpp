// Copyright One Boss Fight. All Rights Reserved.
#include "RPGMontageWrapperLibrary.h"

#include "Animation/AnimMontage.h"
#include "Animation/AnimNotifies/AnimNotifyState.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimSequenceBase.h"
#include "Animation/Skeleton.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "Misc/PackageName.h"
#include "UObject/Package.h"

namespace
{
	constexpr TCHAR GreystoneRoot[] = TEXT("/Game/OneBossFight/Player/Greystone/");

	UAnimMontage* DuplicateRetargetedMontage(const UAnimMontage* Source, UAnimSequence* TargetSequence,
		USkeleton* TargetSkeleton, UObject* Outer, FName AssetName, bool bTransient, FString& OutError)
	{
		UAnimMontage* Wrapper = DuplicateObject<UAnimMontage>(Source, Outer, AssetName);
		if (!Wrapper)
		{
			OutError = TEXT("MontageWrapper.DuplicateFailed");
			return nullptr;
		}
		if (bTransient)
		{
			Wrapper->ClearFlags(RF_Public | RF_Standalone);
			Wrapper->SetFlags(RF_Transient);
		}
		else
		{
			Wrapper->SetFlags(RF_Public | RF_Standalone);
		}
		Wrapper->SetSkeleton(TargetSkeleton);
		int32 SegmentCount = 0;
		for (FSlotAnimationTrack& Slot : Wrapper->SlotAnimTracks)
		{
			for (FAnimSegment& Segment : Slot.AnimTrack.AnimSegments)
			{
				Segment.SetAnimReference(TargetSequence, false);
				++SegmentCount;
			}
		}
		if (SegmentCount == 0)
		{
			Wrapper->ClearFlags(RF_Public | RF_Standalone);
			Wrapper->MarkAsGarbage();
			OutError = TEXT("MontageWrapper.SourceHasNoSegments");
			return nullptr;
		}
		Wrapper->CalculateSequenceLength();
		Wrapper->PostEditChange();
		if (!bTransient)
		{
			Wrapper->MarkPackageDirty();
			FAssetRegistryModule::AssetCreated(Wrapper);
		}
		return Wrapper;
	}
}

UAnimMontage* URPGMontageWrapperLibrary::CreateRetargetWrapper(UAnimMontage* Source,
	UAnimSequence* TargetSequence, USkeleton* TargetSkeleton, FString PackagePath, FString& OutError)
{
	OutError.Reset();
	if (!IsInGameThread())
	{
		OutError = TEXT("MontageWrapper.NotGameThread");
		return nullptr;
	}
	if (!IsValid(Source) || !IsValid(TargetSequence) || !IsValid(TargetSkeleton))
	{
		OutError = TEXT("MontageWrapper.RequiredObject");
		return nullptr;
	}
	if (PackagePath.IsEmpty())
	{
		return CreateTransientRetargetWrapper(Source, TargetSequence, TargetSkeleton, OutError);
	}
	if (!PackagePath.StartsWith(GreystoneRoot, ESearchCase::CaseSensitive) ||
		!FPackageName::IsValidLongPackageName(PackagePath))
	{
		OutError = TEXT("MontageWrapper.PackagePathOutsideGreystoneAllowlist");
		return nullptr;
	}
	if (TargetSequence->GetSkeleton() != TargetSkeleton)
	{
		OutError = TEXT("MontageWrapper.TargetSkeletonMismatch");
		return nullptr;
	}
	if (Source->SlotAnimTracks.IsEmpty())
	{
		OutError = TEXT("MontageWrapper.SourceHasNoSlotTracks");
		return nullptr;
	}
	float LastNotifyEnd = 0.f;
	for (const FAnimNotifyEvent& Event : Source->Notifies)
	{
		LastNotifyEnd = FMath::Max(LastNotifyEnd,
			Event.NotifyStateClass ? Event.GetEndTriggerTime() : Event.GetTriggerTime());
	}
	if (TargetSequence->GetPlayLength() + KINDA_SMALL_NUMBER < LastNotifyEnd)
	{
		OutError = FString::Printf(TEXT("MontageWrapper.TargetShorterThanLastNotify: target=%.6f notifyEnd=%.6f"),
			TargetSequence->GetPlayLength(), LastNotifyEnd);
		return nullptr;
	}
	if (FindPackage(nullptr, *PackagePath) || FPackageName::DoesPackageExist(PackagePath))
	{
		OutError = TEXT("MontageWrapper.DestinationAlreadyExists");
		return nullptr;
	}
	UPackage* Package = CreatePackage(*PackagePath);
	if (!Package)
	{
		OutError = TEXT("MontageWrapper.CreatePackageFailed");
		return nullptr;
	}
	const FName AssetName(*FPackageName::GetLongPackageAssetName(PackagePath));
	return DuplicateRetargetedMontage(Source, TargetSequence, TargetSkeleton, Package, AssetName, false, OutError);
}

UAnimMontage* URPGMontageWrapperLibrary::CreateTransientRetargetWrapper(UAnimMontage* Source,
	UAnimSequence* TargetSequence, USkeleton* TargetSkeleton, FString& OutError)
{
	OutError.Reset();
	if (!IsInGameThread())
	{
		OutError = TEXT("MontageWrapper.NotGameThread");
		return nullptr;
	}
	if (!IsValid(Source) || !IsValid(TargetSequence) || !IsValid(TargetSkeleton))
	{
		OutError = TEXT("MontageWrapper.RequiredObject");
		return nullptr;
	}
	if (TargetSequence->GetSkeleton() != TargetSkeleton)
	{
		OutError = TEXT("MontageWrapper.TargetSkeletonMismatch");
		return nullptr;
	}
	if (Source->SlotAnimTracks.IsEmpty())
	{
		OutError = TEXT("MontageWrapper.SourceHasNoSlotTracks");
		return nullptr;
	}
	float LastNotifyEnd = 0.f;
	for (const FAnimNotifyEvent& Event : Source->Notifies)
	{
		LastNotifyEnd = FMath::Max(LastNotifyEnd,
			Event.NotifyStateClass ? Event.GetEndTriggerTime() : Event.GetTriggerTime());
	}
	if (TargetSequence->GetPlayLength() + KINDA_SMALL_NUMBER < LastNotifyEnd)
	{
		OutError = FString::Printf(TEXT("MontageWrapper.TargetShorterThanLastNotify: target=%.6f notifyEnd=%.6f"),
			TargetSequence->GetPlayLength(), LastNotifyEnd);
		return nullptr;
	}
	const FName Name = MakeUniqueObjectName(GetTransientPackage(), UAnimMontage::StaticClass(),
		FName(*(Source->GetName() + TEXT("_TransientRetarget"))));
	return DuplicateRetargetedMontage(Source, TargetSequence, TargetSkeleton, GetTransientPackage(), Name, true, OutError);
}

TArray<FString> URPGMontageWrapperLibrary::DescribeMontageNotifies(const UAnimMontage* Montage)
{
	TArray<FString> OutRows;
	if (!IsValid(Montage))
	{
		return OutRows;
	}
	TArray<FString> Slots;
	TArray<FString> Segments;
	for (const FSlotAnimationTrack& Slot : Montage->SlotAnimTracks)
	{
		Slots.Add(Slot.SlotName.ToString());
		for (const FAnimSegment& Segment : Slot.AnimTrack.AnimSegments)
		{
			const UAnimSequenceBase* Animation = Segment.GetAnimReference().Get();
			Segments.Add(FString::Printf(TEXT("%s@%.6f"), Animation ? *Animation->GetPathName() : TEXT("<null>"),
				Animation ? Animation->GetPlayLength() : 0.0f));
		}
	}
	for (int32 Index = 0; Index < Montage->Notifies.Num(); ++Index)
	{
		const FAnimNotifyEvent& Event = Montage->Notifies[Index];
		const FString NotifyClass = Event.NotifyStateClass ? Event.NotifyStateClass->GetClass()->GetName()
			: (Event.Notify ? Event.Notify->GetClass()->GetName() : Event.NotifyName.ToString());
		OutRows.Add(FString::Printf(TEXT("notify=%d class=%s trigger=%.6f duration=%.6f track=%d slots=[%s] segments=[%s]"),
			Index, *NotifyClass, Event.GetTriggerTime(), Event.NotifyStateClass ? Event.GetDuration() : 0.0f,
			Event.TrackIndex, *FString::Join(Slots, TEXT(",")), *FString::Join(Segments, TEXT(","))));
	}
	return OutRows;
}
