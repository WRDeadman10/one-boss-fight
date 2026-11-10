// Copyright One Boss Fight. All Rights Reserved.
#include "RPGMontageWrapperLibrary.h"

#include "Animation/AnimMontage.h"
#include "Animation/AnimSequence.h"
#include "Animation/Skeleton.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "Misc/PackageName.h"
#include "UObject/Package.h"

namespace
{
	constexpr TCHAR GreystoneRoot[] = TEXT("/Game/OneBossFight/Player/Greystone/");
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
	UAnimMontage* Wrapper = DuplicateObject<UAnimMontage>(Source, Package, AssetName);
	if (!Wrapper)
	{
		OutError = TEXT("MontageWrapper.DuplicateFailed");
		return nullptr;
	}
	Wrapper->SetFlags(RF_Public | RF_Standalone);
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
	Wrapper->MarkPackageDirty();
	FAssetRegistryModule::AssetCreated(Wrapper);
	return Wrapper;
}
