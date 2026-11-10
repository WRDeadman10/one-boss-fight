// Copyright One Boss Fight. All Rights Reserved.
#include "RPGMontageWrapperLibrary.h"

#include "Animation/AnimMontage.h"
#include "Animation/Skeleton.h"
#include "Misc/AutomationTest.h"
#include "UObject/Package.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGMontageWrapperLibrarySynthetic,
	"OneBossFight.Editor.MontageWrapper.SyntheticCopyAndGuards",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FRPGMontageWrapperLibrarySynthetic::RunTest(const FString&)
{
	USkeleton* TargetSkeleton = LoadObject<USkeleton>(nullptr,
		TEXT("/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone_Skeleton.Greystone_Skeleton"));
	UAnimSequence* TargetSequence = LoadObject<UAnimSequence>(nullptr,
		TEXT("/Game/OneBossFight/Player/FitTest/Greystone/AN_ER_Backstep_Mixamo_V2_Fit_Greystone.AN_ER_Backstep_Mixamo_V2_Fit_Greystone"));
	UAnimMontage* SourceAsset = LoadObject<UAnimMontage>(nullptr,
		TEXT("/Game/OneBossFight/Player/Animations/AM_ER_Backstep_Mixamo_V2.AM_ER_Backstep_Mixamo_V2"));
	if (!TestNotNull(TEXT("fixture target skeleton loads"), TargetSkeleton) ||
		!TestNotNull(TEXT("fixture target sequence loads"), TargetSequence) ||
		!TestNotNull(TEXT("fixture source montage loads"), SourceAsset)) return false;
	UAnimMontage* Source = DuplicateObject<UAnimMontage>(SourceAsset, GetTransientPackage());
	if (!TestNotNull(TEXT("synthetic source montage duplicates"), Source)) return false;
	Source->RateScale = 1.25f;
	Source->bEnableAutoBlendOut = false;
	Source->bEnableRootMotionTranslation = true;
	Source->bEnableRootMotionRotation = true;
	Source->RootMotionRootLock = ERootMotionRootLock::AnimFirstFrame;
	const int32 SourceSlots = Source->SlotAnimTracks.Num();
	const int32 SourceSections = Source->CompositeSections.Num();
	const int32 SourceNotifies = Source->Notifies.Num();
	TestTrue(TEXT("synthetic source has montage slot tracks"), SourceSlots > 0);
	TestTrue(TEXT("synthetic source has notify events"), SourceNotifies > 0);

	FString Error;
	const FString Destination = TEXT("/Game/OneBossFight/Player/Greystone/TransientMontageWrapperTest_") + FGuid::NewGuid().ToString(EGuidFormats::Digits);
	UAnimMontage* Wrapper = URPGMontageWrapperLibrary::CreateRetargetWrapper(
		Source, TargetSequence, TargetSkeleton, Destination, Error);
	TestNotNull(TEXT("synthetic montage produces a wrapper"), Wrapper);
	TestTrue(TEXT("success has no diagnostic"), Error.IsEmpty());
	if (Wrapper)
	{
		TestEqual(TEXT("wrapper uses target skeleton"), Wrapper->GetSkeleton(), TargetSkeleton);
		TestEqual(TEXT("all source sections are preserved"), Wrapper->CompositeSections.Num(), SourceSections);
		TestEqual(TEXT("all slot names are preserved"), Wrapper->SlotAnimTracks.Num(), SourceSlots);
		TestEqual(TEXT("all montage notifies are preserved"), Wrapper->Notifies.Num(), SourceNotifies);
		TArray<FString> SourceRows;
		TArray<FString> TargetRows;
		SourceRows = URPGMontageWrapperLibrary::DescribeMontageNotifies(Source);
		TargetRows = URPGMontageWrapperLibrary::DescribeMontageNotifies(Wrapper);
		TestEqual(TEXT("one source readback row per notify"), SourceRows.Num(), SourceNotifies);
		TestEqual(TEXT("one target readback row per notify"), TargetRows.Num(), SourceNotifies);
		if (SourceRows.Num() > 0 && TargetRows.Num() == SourceRows.Num())
		{
			TestTrue(TEXT("source row includes timing, track, slot, and segment path"),
				SourceRows[0].Contains(TEXT("class=")) && SourceRows[0].Contains(TEXT("trigger=")) &&
				SourceRows[0].Contains(TEXT("duration=")) && SourceRows[0].Contains(TEXT("track=")) &&
				SourceRows[0].Contains(TEXT("slots=[")) && SourceRows[0].Contains(*Source->GetFirstAnimReference()->GetPathName()));
			TestTrue(TEXT("target row points to retarget sequence and reports its length"),
				TargetRows[0].Contains(*TargetSequence->GetPathName()) && TargetRows[0].Contains(TEXT("@")));
		}
		TestEqual(TEXT("source rate scale is preserved"), Wrapper->RateScale, 1.25f);
		TestFalse(TEXT("source auto blend-out setting is preserved"), Wrapper->bEnableAutoBlendOut);
		TestTrue(TEXT("source root motion translation setting is preserved"), Wrapper->bEnableRootMotionTranslation);
		TestTrue(TEXT("source root motion rotation setting is preserved"), Wrapper->bEnableRootMotionRotation);
		bool bAllSegmentsUseTarget = Wrapper->SlotAnimTracks.Num() == SourceSlots;
		for (const FSlotAnimationTrack& WrapperSlot : Wrapper->SlotAnimTracks)
		{
			for (const FAnimSegment& WrapperSegment : WrapperSlot.AnimTrack.AnimSegments)
			{
				bAllSegmentsUseTarget &= WrapperSegment.GetAnimReference().Get() == TargetSequence;
			}
		}
		TestTrue(TEXT("every slot segment points at the target"), bAllSegmentsUseTarget);
	}
	TestNull(TEXT("destination outside Greystone allowlist is rejected"),
		URPGMontageWrapperLibrary::CreateRetargetWrapper(Source, TargetSequence, TargetSkeleton,
			TEXT("/Game/Other/Rejected"), Error));
	TestEqual(TEXT("path rejection is diagnosable"), Error, FString(TEXT("MontageWrapper.PackagePathOutsideGreystoneAllowlist")));
	USkeleton* MismatchSkeleton = NewObject<USkeleton>(GetTransientPackage());
	TestNull(TEXT("target sequence skeleton mismatch is rejected"),
		URPGMontageWrapperLibrary::CreateRetargetWrapper(Source, TargetSequence, MismatchSkeleton,
			TEXT("/Game/OneBossFight/Player/Greystone/Mismatch_") + FGuid::NewGuid().ToString(EGuidFormats::Digits), Error));
	TestEqual(TEXT("skeleton rejection is diagnosable"), Error, FString(TEXT("MontageWrapper.TargetSkeletonMismatch")));
	FAnimNotifyEvent& LateNotify = Source->Notifies.AddDefaulted_GetRef();
	LateNotify.NotifyName = TEXT("LateNotify");
	LateNotify.Link(Source, TargetSequence->GetPlayLength() + 0.1f, 0);
	TestNull(TEXT("target shorter than the last source notify is rejected"),
		URPGMontageWrapperLibrary::CreateRetargetWrapper(Source, TargetSequence, TargetSkeleton,
			TEXT("/Game/OneBossFight/Player/Greystone/TooShort_") + FGuid::NewGuid().ToString(EGuidFormats::Digits), Error));
	TestTrue(TEXT("short-target rejection identifies notify end"),
		Error.StartsWith(TEXT("MontageWrapper.TargetShorterThanLastNotify")));
	UAnimMontage* TransientWrapper = URPGMontageWrapperLibrary::CreateRetargetWrapper(
		SourceAsset, TargetSequence, TargetSkeleton, TEXT(""), Error);
	TestNotNull(TEXT("transient wrapper is created without a destination package"), TransientWrapper);
	TestTrue(TEXT("transient wrapper creation has no error"), Error.IsEmpty());
	if (TransientWrapper)
	{
		TestTrue(TEXT("transient wrapper has transient flags"), TransientWrapper->HasAnyFlags(RF_Transient));
		TestEqual(TEXT("transient wrapper outer is transient package"), TransientWrapper->GetOutermost(), GetTransientPackage());
		TArray<FString> SourceRows;
		TArray<FString> TargetRows;
		SourceRows = URPGMontageWrapperLibrary::DescribeMontageNotifies(SourceAsset);
		TargetRows = URPGMontageWrapperLibrary::DescribeMontageNotifies(TransientWrapper);
		TestEqual(TEXT("transient path preserves one row per source notify"), TargetRows.Num(), SourceRows.Num());
	}
	const TArray<FString> InvalidRows = URPGMontageWrapperLibrary::DescribeMontageNotifies(nullptr);
	TestTrue(TEXT("null montage readback clears output"), InvalidRows.IsEmpty());
	return true;
}
#endif
