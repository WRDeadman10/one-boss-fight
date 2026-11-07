// Copyright One Boss Fight. All Rights Reserved.

#include "Combat/RPGMontageUtils.h"
#include "Animation/AnimMontage.h"
#include "Animation/AnimSequence.h"
#include "Misc/AutomationTest.h"
#include "UObject/Package.h"

#if WITH_EDITOR
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGMontageSegmentRangeTest,
	"OneBossFight.Authoring.MontageSegmentRange",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FRPGMontageSegmentRangeTest::RunTest(const FString& Parameters)
{
	TestFalse(TEXT("Null montage is rejected"), URPGMontageUtils::SetMontageSegmentRange(nullptr, 0.333333f, 1.133333f));

	UAnimMontage* EmptyMontage = NewObject<UAnimMontage>(GetTransientPackage());
	// UAnimMontage's constructor already adds an empty DefaultSlot track (UE 5.5), which is the case under test.
	TestEqual(TEXT("A new montage has one default slot"), EmptyMontage->SlotAnimTracks.Num(), 1);
	TestFalse(TEXT("A slot without a segment is rejected"), URPGMontageUtils::SetMontageSegmentRange(EmptyMontage, 0.333333f, 1.133333f));

	UPackage* TestPackage = CreatePackage(TEXT("/Temp/RPGMontageSegmentRangeTest"));
	TestPackage->ClearDirtyFlag();
	// UE 5.5 keeps UAnimSequenceBase::SequenceLength protected (the data model owns it), so the test slices a real pack
	// sequence: it is only referenced by the transient montage below, never modified or saved.
	UAnimSequence* Sequence = LoadObject<UAnimSequence>(nullptr,
		TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle.Dodge_To_Idle"));
	if (!TestNotNull(TEXT("Pack source sequence loads"), Sequence))
	{
		return false;
	}
	const float SourceLength = Sequence->GetPlayLength();
	if (!TestTrue(TEXT("Pack source sequence is long enough to slice"), SourceLength > 0.2f))
	{
		return false;
	}
	const float SliceStart = SourceLength * 0.2f;
	const float SliceEnd = SourceLength * 0.68f;

	UAnimMontage* Montage = NewObject<UAnimMontage>(TestPackage);
	// Use the constructor's DefaultSlot track: AddSlot would append a second track and the helper edits the first.
	FSlotAnimationTrack& Slot = Montage->SlotAnimTracks[0];
	FAnimSegment Segment;
	Segment.SetAnimReference(Sequence, true);
	Segment.AnimStartTime = 0.0f;
	Segment.AnimEndTime = SourceLength;
	Slot.AnimTrack.AnimSegments.Add(Segment);
	Montage->SetCompositeLength(SourceLength);
	// Building the test montage dirties its package; reset so the rejected calls below are checked on their own.
	TestPackage->ClearDirtyFlag();

	TestFalse(TEXT("Negative start is rejected"), URPGMontageUtils::SetMontageSegmentRange(Montage, -0.1f, SliceEnd));
	TestFalse(TEXT("Empty range is rejected"), URPGMontageUtils::SetMontageSegmentRange(Montage, SliceStart, SliceStart));
	TestFalse(TEXT("Range past source animation is rejected"), URPGMontageUtils::SetMontageSegmentRange(Montage, SliceStart, SourceLength + 0.1f));
	TestTrue(TEXT("Rejected requests leave the segment unchanged"), FMath::IsNearlyEqual(Montage->SlotAnimTracks[0].AnimTrack.AnimSegments[0].AnimEndTime, SourceLength));
	TestFalse(TEXT("Rejected requests leave the package clean"), TestPackage->IsDirty());
	TestTrue(TEXT("Valid slice is applied"), URPGMontageUtils::SetMontageSegmentRange(Montage, SliceStart, SliceEnd));

	const FAnimSegment& Result = Montage->SlotAnimTracks[0].AnimTrack.AnimSegments[0];
	TestTrue(TEXT("Segment start is updated"), FMath::IsNearlyEqual(Result.AnimStartTime, SliceStart));
	TestTrue(TEXT("Segment end is updated"), FMath::IsNearlyEqual(Result.AnimEndTime, SliceEnd));
	TestTrue(TEXT("Montage length is recomputed from segment range"), FMath::IsNearlyEqual(Montage->GetPlayLength(), SliceEnd - SliceStart, 1.0e-3f));
	TestTrue(TEXT("Montage package is marked dirty"), Montage->GetPackage()->IsDirty());
	TestFalse(TEXT("Source sequence package is not dirtied"), Sequence->GetPackage()->IsDirty());
	return true;
}
#endif
