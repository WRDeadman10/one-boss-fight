// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS

#include "GameFramework/Actor.h"
#include "Animation/AnimMontage.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Player/RPGAttackTracker.h"
#include "Player/RPGMontageNotifyTiming.h"
#include "Player/RPGBossAttackTrackerAdapters.h"
#include "UObject/Package.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGBossAttackTrackerConfigDefaultsTest, "OneBossFight.Boss.AttackTracker.TypedDefaultsAndAdapter",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGBossAttackTrackerConfigDefaultsTest::RunTest(const FString& Parameters)
{
	const FRPGAttackTrackerConfig Defaults;
	AActor* Owner = NewObject<AActor>(GetTransientPackage());
	if (!TestNotNull(TEXT("unbegun test owner"), Owner)) { return false; }
	URPGAttackTracker* Legacy = NewObject<URPGAttackTracker>(Owner, TEXT("LegacyTracker"));
	URPGAttackTracker* Selected = NewObject<URPGAttackTracker>(Owner, TEXT("SelectedTracker"));
	if (!TestNotNull(TEXT("legacy native tracker"), Legacy) || !TestNotNull(TEXT("selected prepared tracker"), Selected)) { return false; }
	TestTrue(TEXT("native defaults match the configuration record field-for-field"), Legacy->Attacks.Num() == Defaults.Attacks.Num()
		&& Legacy->bEnabled == Defaults.bEnabled && !Legacy->bUseMontageNotifyTimings && Legacy->bVetoIllegalStarts == Defaults.bVetoIllegalStarts
		&& Legacy->BranchRange == Defaults.BranchRange && Legacy->BranchConeDegrees == Defaults.BranchConeDegrees);
	if (Legacy->Attacks.Num() == Defaults.Attacks.Num())
	{
		for (int32 Index = 0; Index < Defaults.Attacks.Num(); ++Index)
		{
			const FRPGAttackTiming& A = Legacy->Attacks[Index];
			const FRPGAttackTiming& B = Defaults.Attacks[Index];
			TestTrue(TEXT("each legacy attack timing exactly matches native config defaults"), A.MoveId == B.MoveId && A.MontageName == B.MontageName
				&& A.FallbackMontageName == B.FallbackMontageName && A.MontagePath == B.MontagePath && A.bAuthoredWindup == B.bAuthoredWindup
				&& A.CommitTime == B.CommitTime && A.ActiveStartTime == B.ActiveStartTime && A.ActiveEndTime == B.ActiveEndTime && A.RecoveryEndTime == B.RecoveryEndTime
				&& A.TrackTurnRate == B.TrackTurnRate && A.bBranchStage == B.bBranchStage && A.ClipPath == B.ClipPath);
		}
	}
	FRPGParticipantConfig Config;
	Config.AttackTracker = Defaults;
	FString Error;
	TestTrue(TEXT("legacy native default table retains its pre-integration reference semantics"),
		RPGBossAttackTrackerAdapters::ValidateAttackTracker(Defaults, Error) && Error.IsEmpty());
	TestTrue(TEXT("selected route config applies on an unbegun unregistered owner"), RPGBossAttackTrackerAdapters::ConfigureAttackTracker(*Selected, Config, Error) && Error.IsEmpty());
	TestTrue(TEXT("selected tracker matches legacy defaults after configure"), Selected->Attacks.Num() == Legacy->Attacks.Num()
		&& Selected->bEnabled == Legacy->bEnabled && Selected->bVetoIllegalStarts == Legacy->bVetoIllegalStarts
		&& Selected->BranchRange == Legacy->BranchRange && Selected->BranchConeDegrees == Legacy->BranchConeDegrees);
	if (Selected->Attacks.Num() == Legacy->Attacks.Num())
	{
		for (int32 Index = 0; Index < Legacy->Attacks.Num(); ++Index)
		{
			const FRPGAttackTiming& A = Legacy->Attacks[Index];
			const FRPGAttackTiming& B = Selected->Attacks[Index];
			TestTrue(TEXT("selected-route and legacy tracker timings have bit-identical field values"), A.MoveId == B.MoveId && A.MontageName == B.MontageName
				&& A.FallbackMontageName == B.FallbackMontageName && A.MontagePath == B.MontagePath && A.bAuthoredWindup == B.bAuthoredWindup
				&& A.CommitTime == B.CommitTime && A.ActiveStartTime == B.ActiveStartTime && A.ActiveEndTime == B.ActiveEndTime && A.RecoveryEndTime == B.RecoveryEndTime
				&& A.TrackTurnRate == B.TrackTurnRate && A.bBranchStage == B.bBranchStage && A.ClipPath == B.ClipPath);
		}
	}
	FRPGAttackTrackerConfig Invalid = Defaults;
	Invalid.Attacks[1].MoveId = Invalid.Attacks[0].MoveId;
	TestFalse(TEXT("duplicate move IDs are refused"), RPGBossAttackTrackerAdapters::ValidateAttackTracker(Invalid, Error));
	TestTrue(TEXT("duplicate move refusal has its stable token"), Error.StartsWith(TEXT("InvalidAttackTracker.DuplicateMoveId")));
	Invalid = Defaults;
	Invalid.BranchRange = std::numeric_limits<float>::quiet_NaN();
	TestFalse(TEXT("non-finite branch range is refused"), RPGBossAttackTrackerAdapters::ValidateAttackTracker(Invalid, Error));
	TestTrue(TEXT("branch range refusal is named"), Error.StartsWith(TEXT("InvalidAttackTracker.BranchRange")));
	Invalid = Defaults;
	Invalid.Attacks[0].ActiveStartTime = Invalid.Attacks[0].CommitTime - 0.01f;
	TestFalse(TEXT("out-of-order attack windows are refused"), RPGBossAttackTrackerAdapters::ValidateAttackTracker(Invalid, Error));
	TestTrue(TEXT("window-order refusal is named"), Error.StartsWith(TEXT("InvalidAttackTracker.Order")));
	Invalid = Defaults;
	Invalid.BranchRange += 1.f;
	Invalid.Attacks[0].MontageName.Reset();
	Invalid.Attacks[0].ClipPath.Reset();
	Invalid.Attacks[0].MontagePath.Reset();
	Invalid.Attacks[0].FallbackMontageName.Reset();
	TestFalse(TEXT("non-default configs still require an explicit montage identity"), RPGBossAttackTrackerAdapters::ValidateAttackTracker(Invalid, Error));
	TestTrue(TEXT("custom missing-reference refusal is named"), Error.StartsWith(TEXT("InvalidAttackTracker.Reference")));
	// Lead fix: an actor outside a world never begins play (DispatchBeginPlay needs a world), so spawn it in a
	// transient game world, the same scope pattern as RPGBossExecutorHarnessTests.cpp FExecutorHarnessWorld.
	UWorld* World = GEngine ? UWorld::CreateWorld(EWorldType::Game, false) : nullptr;
	if (!TestNotNull(TEXT("transient world for the begun-owner case"), World)) return false;
	FWorldContext& Context = GEngine->CreateNewWorldContext(EWorldType::Game);
	Context.SetCurrentWorld(World);
	World->InitializeActorsForPlay(FURL());
	AActor* BegunOwner = World->SpawnActor<AActor>(FVector::ZeroVector, FRotator::ZeroRotator);
	if (TestNotNull(TEXT("begun owner spawns"), BegunOwner))
	{
		URPGAttackTracker* BegunTracker = NewObject<URPGAttackTracker>(BegunOwner);
		BegunOwner->DispatchBeginPlay();
		TestTrue(TEXT("owner really began play"), BegunOwner->HasActorBegunPlay());
		TestFalse(TEXT("configuration after owner BeginPlay is refused"), RPGBossAttackTrackerAdapters::ConfigureAttackTracker(*BegunTracker, Config, Error));
		TestTrue(TEXT("begun-owner refusal is named"), Error.Contains(TEXT("OwnerBegunPlay")));
	}
	GEngine->DestroyWorldContext(World);
	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGMontageNotifyTimingRulesTest, "OneBossFight.Boss.AttackTracker.MontageNotifyTimingRules",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGMontageNotifyTimingRulesTest::RunTest(const FString& Parameters)
{
	using namespace RPGMontageNotifyTiming;
	FAnnotation Annotation;
	Annotation.MontageObjectPath = FString(TEXT("/Game/")) + TEXT("Boss/AM_A1.AM_A1");
	Annotation.MoveId = TEXT("A1");
	Annotation.MontageLength = 1.2f;
	Annotation.CommitTime = 0.33f;
	Annotation.WindowStartTime = 0.35f;
	Annotation.WindowEndTime = 0.50f;
	Annotation.RecoveryEndTime = 1.2f;
	Annotation.TrackTurnRate = 250.f;
	Annotation.BranchRange = 333.f;
	Annotation.BranchConeDegrees = 84.f;
	Annotation.bBranchStage = true;
	Annotation.bAuthoredWindup = true;
	FString Error;
	TestTrue(TEXT("a complete finite annotation validates"), Validate(Annotation, Error));
	UAnimMontage* EmptyMontage = NewObject<UAnimMontage>(GetTransientPackage());
	TArray<FAnnotation> Collected;
	TestTrue(TEXT("montage with no authored timing notifies collects successfully"), EmptyMontage && CollectAnnotations(*EmptyMontage, Collected, Error));
	TestTrue(TEXT("montage with no authored timing notifies yields empty fallback data"), Collected.IsEmpty());

	FRPGAttackTiming Fallback;
	Fallback.MoveId = TEXT("A1");
	Fallback.MontageName = TEXT("LegacyA1");
	Fallback.FallbackMontageName = TEXT("LegacyFallback");
	Fallback.MontagePath = FString(TEXT("/Game/")) + TEXT("Legacy/Legacy.Legacy");
	Fallback.OptionalTrackerMontagePath = FString(TEXT("/Game/")) + TEXT("Legacy/Preview.Preview");
	Fallback.ClipPath = FString(TEXT("/Game/")) + TEXT("Legacy/Clip.Clip");
	Fallback.CommitTime = 0.3f;
	Fallback.bBranchStage = false;
	FRPGAttackTiming Selected;
	float BranchRange = 550.f;
	float BranchCone = 120.f;
	TestTrue(TEXT("disabled observer falls back to legacy table"), SelectTiming(false, {Annotation}, Annotation.MontageObjectPath, Annotation.MoveId, Fallback, 550.f, 120.f, Selected, BranchRange, BranchCone, Error));
	TestTrue(TEXT("disabled observer preserves legacy timing"), Selected.CommitTime == Fallback.CommitTime && Selected.MontageName == Fallback.MontageName);
	TestTrue(TEXT("empty annotation list falls back to legacy table"), SelectTiming(true, {}, Annotation.MontageObjectPath, Annotation.MoveId, Fallback, 550.f, 120.f, Selected, BranchRange, BranchCone, Error));
	TestTrue(TEXT("empty annotation fallback is bit-identical"), Selected.CommitTime == Fallback.CommitTime && Selected.ActiveStartTime == Fallback.ActiveStartTime);
	TestTrue(TEXT("enabled observer selects exact montage identity and MoveId"), SelectTiming(true, {Annotation}, Annotation.MontageObjectPath, Annotation.MoveId, Fallback, 550.f, 120.f, Selected, BranchRange, BranchCone, Error));
	TestTrue(TEXT("selected timing is sourced from annotation"), Selected.CommitTime == Annotation.CommitTime && Selected.ActiveStartTime == Annotation.WindowStartTime && Selected.ActiveEndTime == Annotation.WindowEndTime);
	TestTrue(TEXT("matched annotation preserves legacy montage references"), Selected.MontageName == Fallback.MontageName && Selected.FallbackMontageName == Fallback.FallbackMontageName
		&& Selected.MontagePath == Fallback.MontagePath && Selected.OptionalTrackerMontagePath == Fallback.OptionalTrackerMontagePath && Selected.ClipPath == Fallback.ClipPath);
	TestTrue(TEXT("annotation branch range and cone are returned to their consumer"), BranchRange == Annotation.BranchRange && BranchCone == Annotation.BranchConeDegrees);
	TestTrue(TEXT("annotation turn rate and authored windup remain observable"), Selected.TrackTurnRate == Annotation.TrackTurnRate && Selected.bAuthoredWindup);
	const FString OtherMontagePath = FString(TEXT("/Game/")) + TEXT("Boss/Other.Other");
	TestTrue(TEXT("unknown montage identity falls back"), SelectTiming(true, {Annotation}, OtherMontagePath, Annotation.MoveId, Fallback, 550.f, 120.f, Selected, BranchRange, BranchCone, Error));
	TestTrue(TEXT("unknown MoveId falls back"), SelectTiming(true, {Annotation}, Annotation.MontageObjectPath, TEXT("A2"), Fallback, 550.f, 120.f, Selected, BranchRange, BranchCone, Error));

	FAnnotation Invalid = Annotation;
	Invalid.WindowEndTime = Invalid.WindowStartTime;
	TestFalse(TEXT("empty active window is rejected"), Validate(Invalid, Error));
	Invalid = Annotation;
	Invalid.MontageObjectPath.Reset();
	TestFalse(TEXT("missing montage object identity is rejected"), Validate(Invalid, Error));
	TArray<FAnnotation> Duplicates{Annotation, Annotation};
	TestFalse(TEXT("duplicate annotation identity is rejected"), SelectTiming(true, Duplicates, Annotation.MontageObjectPath, Annotation.MoveId, Fallback, 550.f, 120.f, Selected, BranchRange, BranchCone, Error));
	TestTrue(TEXT("invalid annotation selection retains the full legacy row"), Selected.MontageName == Fallback.MontageName && Selected.ClipPath == Fallback.ClipPath);
	FObserver Observer;
	EPhase Phase = EPhase::Tell;
	TestFalse(TEXT("observer defaults off"), Observer.Begin(Annotation.MontageObjectPath, Annotation.MoveId));
	Observer.bEnabled = true;
	TestTrue(TEXT("observer begins with exact montage identity and move"), Observer.Begin(Annotation.MontageObjectPath, Annotation.MoveId));
	TestTrue(TEXT("observer reports commitment phase from montage-local sample"), Observer.Sample(0.34f, Annotation, Phase) && Phase == EPhase::Committed);
	TestTrue(TEXT("observer reports active window from montage-local sample"), Observer.Sample(0.40f, Annotation, Phase) && Phase == EPhase::Active);
	TestFalse(TEXT("observer releases state on a backwards montage seek"), Observer.Sample(0.39f, Annotation, Phase));
	TestFalse(TEXT("interrupted/reset observer cannot retain an active window"), Observer.Sample(0.45f, Annotation, Phase));
	UAnimMontage* InvalidMontage = NewObject<UAnimMontage>(GetTransientPackage());
	URPGANS_BossMoveTiming* InvalidNotify = NewObject<URPGANS_BossMoveTiming>(InvalidMontage);
	InvalidNotify->MoveId = TEXT("A1");
	FAnimNotifyEvent& InvalidEvent = InvalidMontage->Notifies.AddDefaulted_GetRef();
	InvalidEvent.NotifyStateClass = InvalidNotify;
	RPGMontageNotifyTiming::FCache Cache;
	bool bWarnOnce = false;
	TestFalse(TEXT("invalid optional notify fails validation"), Cache.Resolve(true, InvalidMontage, 17, Fallback.MoveId, Fallback, 550.f, 120.f,
		Selected, BranchRange, BranchCone, Error, bWarnOnce));
	TestTrue(TEXT("invalid optional notify falls back and emits one warning signal"), bWarnOnce && Selected.MontageName == Fallback.MontageName
		&& Selected.ClipPath == Fallback.ClipPath && BranchRange == 550.f && BranchCone == 120.f);
	TestFalse(TEXT("repeated invalid sample reuses cache without another warning"), Cache.Resolve(true, InvalidMontage, 17, Fallback.MoveId, Fallback, 550.f, 120.f,
		Selected, BranchRange, BranchCone, Error, bWarnOnce));
	TestFalse(TEXT("warning signal is emitted only once for the montage instance"), bWarnOnce);
	return true;
}

#endif
