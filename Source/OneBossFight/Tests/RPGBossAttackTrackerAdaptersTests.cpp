// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS

#include "GameFramework/Actor.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Player/RPGAttackTracker.h"
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
		&& Legacy->bEnabled == Defaults.bEnabled && Legacy->bVetoIllegalStarts == Defaults.bVetoIllegalStarts
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

#endif
