// Copyright One Boss Fight. All Rights Reserved.
#include "RPGBossCardValidationLibrary.h"
#include "Player/RPGBossMoveCard.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossCardValidationBridgeParity,
	"OneBossFight.Editor.BossCardValidationBridge.SyntheticParity",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FBossCardValidationBridgeParity::RunTest(const FString&)
{
	FRPGBossMoveCardSpec Spec;
	Spec.Schema = 1;
	Spec.MoveId = TEXT("SyntheticBridgeCard");
	Spec.FamilyId = TEXT("SyntheticFamily");
	Spec.PhaseId = TEXT("SyntheticPhase");
	Spec.Skeleton = TSoftObjectPtr<USkeleton>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Skeleton.Skeleton")));
	Spec.Sequence = TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Sequence.Sequence")));
	Spec.SlotName = TEXT("SyntheticSlot");
	Spec.PlayRate = 1.0f;
	Spec.CommitSeconds = 0.2f;
	Spec.ActiveStartSeconds = 0.4f;
	Spec.ActiveEndSeconds = 0.8f;
	Spec.RecoveryEndSeconds = 1.2f;
	Spec.MaxRangeCm = 350.f;
	Spec.FrontConeDegrees = 120.f;
	Spec.HPDamage = 17.f;
	FRPGBossMoveWindow Window;
	Window.WindowId = TEXT("Contact");
	Window.HitGroup = TEXT("Primary");
	Window.StartSeconds = 0.4f;
	Window.EndSeconds = 0.8f;
	Window.SocketA = TEXT("WeaponBase");
	Window.SocketB = TEXT("WeaponTip");
	Window.RadiusCm = 8.f;
	Spec.Windows.Add(Window);

	FRPGBossMoveMetadata Metadata;
	Metadata.AnimationPath = Spec.Sequence.ToSoftObjectPath();
	Metadata.SkeletonPath = Spec.Skeleton.ToSoftObjectPath();
	Metadata.AnimationSkeletonPath = Metadata.SkeletonPath;
	Metadata.MeshSkeletonPath = Metadata.SkeletonPath;
	Metadata.ClipLengthSeconds = 1.5;
	Metadata.Slots.Add(Spec.SlotName);
	Metadata.SocketOrBoneNames.Add(Window.SocketA);
	Metadata.SocketOrBoneNames.Add(Window.SocketB);
	TArray<FString> Diagnostics;

	TestTrue(TEXT("valid synthetic card passes the bridge's production validator"),
		URPGBossCardValidationLibrary::ValidateMoveCardMetadata(Spec, Metadata, Diagnostics));
	TestTrue(TEXT("valid synthetic card has no diagnostics"), Diagnostics.IsEmpty());

	Spec.Windows.Reset();
	TestFalse(TEXT("non-defensive card without a window fails"),
		URPGBossCardValidationLibrary::ValidateMoveCardMetadata(Spec, Metadata, Diagnostics));
	TestTrue(TEXT("invalid result preserves runtime MoveCard.Window token"),
		Diagnostics.ContainsByPredicate([](const FString& Value) { return Value.StartsWith(TEXT("MoveCard.Window")); }));
	return true;
}
#endif
