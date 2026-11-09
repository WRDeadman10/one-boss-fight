// Copyright One Boss Fight. All Rights Reserved.

#include "EmberMontageTimingAuditCommandlet.h"

#include "Animation/AnimMontage.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "Misc/Parse.h"
#include "Modules/ModuleManager.h"
#include "Player/RPGAttackTracker.h"
#include "Player/RPGMontageNotifyTiming.h"
#include "UObject/Package.h"

namespace
{
	constexpr TCHAR EmberMontageRoot[] = TEXT("/Game/OneBossFight/Boss01/Animations");
	constexpr float TimingToleranceSeconds = 0.02f;

	bool ShouldFailStrictAudit(bool bStrict, int32 Mismatches, int32 Duplicates, int32 Invalid)
	{
		return bStrict && (Mismatches > 0 || Duplicates > 0 || Invalid > 0);
	}

	bool IsRowForMontage(const FRPGAttackTiming& Row, const FString& MontagePath)
	{
		return Row.MontagePath == MontagePath || Row.OptionalTrackerMontagePath == MontagePath;
	}

	void AddMismatch(TArray<FString>& OutMismatches, const TCHAR* Field, float Authored, float Tracker, float Tolerance)
	{
		if (!FMath::IsFinite(Authored) || !FMath::IsFinite(Tracker) || FMath::Abs(Authored - Tracker) > Tolerance)
		{
			OutMismatches.Add(FString::Printf(TEXT("%s annotation=%.6g tracker=%.6g"), Field, Authored, Tracker));
		}
	}

	TArray<FString> Compare(const RPGMontageNotifyTiming::FAnnotation& A, const FRPGAttackTiming& T,
		float TrackerBranchRange, float TrackerBranchCone)
	{
		TArray<FString> Mismatches;
		if (A.MoveId != T.MoveId) Mismatches.Add(TEXT("MoveId"));
		AddMismatch(Mismatches, TEXT("CommitTime"), A.CommitTime, T.CommitTime, TimingToleranceSeconds);
		AddMismatch(Mismatches, TEXT("WindowStartTime"), A.WindowStartTime, T.ActiveStartTime, TimingToleranceSeconds);
		AddMismatch(Mismatches, TEXT("WindowEndTime"), A.WindowEndTime, T.ActiveEndTime, TimingToleranceSeconds);
		AddMismatch(Mismatches, TEXT("RecoveryEndTime"), A.RecoveryEndTime, T.RecoveryEndTime, TimingToleranceSeconds);
		AddMismatch(Mismatches, TEXT("TrackTurnRate"), A.TrackTurnRate, T.TrackTurnRate, 0.02f);
		if (A.bBranchStage)
		{
			AddMismatch(Mismatches, TEXT("BranchRange"), A.BranchRange, TrackerBranchRange, 0.02f);
			AddMismatch(Mismatches, TEXT("BranchConeDegrees"), A.BranchConeDegrees, TrackerBranchCone, 0.02f);
		}
		if (A.bBranchStage != T.bBranchStage) Mismatches.Add(TEXT("bBranchStage"));
		if (A.bAuthoredWindup != T.bAuthoredWindup) Mismatches.Add(TEXT("bAuthoredWindup"));
		return Mismatches;
	}
}

UEmberMontageTimingAuditCommandlet::UEmberMontageTimingAuditCommandlet()
{
	IsClient = false;
	IsServer = false;
	IsEditor = true;
	LogToConsole = true;
}

int32 UEmberMontageTimingAuditCommandlet::Main(const FString& Params)
{
	const bool bStrict = FParse::Param(*Params, TEXT("Strict"));
	UE_LOG(LogTemp, Display, TEXT("[EmberTimingAudit] BEGIN root=%s strict=%d read_only=true"), EmberMontageRoot, bStrict ? 1 : 0);
	URPGAttackTracker* Tracker = NewObject<URPGAttackTracker>(GetTransientPackage());
	if (!Tracker)
	{
		UE_LOG(LogTemp, Error, TEXT("[EmberTimingAudit] INVALID unable_to_construct_tracker"));
		return 2;
	}

	FAssetRegistryModule& AssetRegistryModule = FModuleManager::LoadModuleChecked<FAssetRegistryModule>(TEXT("AssetRegistry"));
	IAssetRegistry& Registry = AssetRegistryModule.Get();
	const TArray<FString> ScanPaths{FString(EmberMontageRoot)};
	Registry.ScanPathsSynchronous(ScanPaths, true);
	TArray<FAssetData> Assets;
	Registry.GetAssetsByPath(FName(EmberMontageRoot), Assets, true);
	Assets.Sort([](const FAssetData& A, const FAssetData& B) { return A.GetObjectPathString() < B.GetObjectPathString(); });

	int32 MontageCount = 0;
	int32 MissingCount = 0;
	int32 MismatchCount = 0;
	int32 DuplicateCount = 0;
	int32 InvalidCount = 0;
	int32 UntrackedCount = 0;
	for (const FAssetData& Asset : Assets)
	{
		UAnimMontage* Montage = Cast<UAnimMontage>(Asset.GetAsset());
		if (!Montage) continue;
		++MontageCount;
		const FString MontagePath = Montage->GetPathName();
		TArray<const FRPGAttackTiming*> Rows;
		for (const FRPGAttackTiming& Row : Tracker->Attacks)
			if (IsRowForMontage(Row, MontagePath)) Rows.Add(&Row);

		TSet<FName> RawMoveIds;
		for (const FAnimNotifyEvent& Event : Montage->Notifies)
		{
			const URPGANS_BossMoveTiming* Notify = Cast<URPGANS_BossMoveTiming>(Event.NotifyStateClass);
			if (Notify && !Notify->MoveId.IsNone() && RawMoveIds.Contains(Notify->MoveId))
			{
				++DuplicateCount;
				UE_LOG(LogTemp, Error, TEXT("[EmberTimingAudit] DUPLICATE asset=%s move=%s"), *MontagePath, *Notify->MoveId.ToString());
			}
			else if (Notify && !Notify->MoveId.IsNone())
			{
				RawMoveIds.Add(Notify->MoveId);
			}
		}

		TArray<RPGMontageNotifyTiming::FAnnotation> Annotations;
		FString ValidationError;
		const bool bValid = RPGMontageNotifyTiming::CollectAnnotations(*Montage, Annotations, ValidationError);
		if (!bValid)
		{
			++InvalidCount;
			UE_LOG(LogTemp, Error, TEXT("[EmberTimingAudit] INVALID asset=%s reason=%s"), *MontagePath, *ValidationError);
			continue;
		}

		TSet<FName> SeenMoveIds;
		for (const RPGMontageNotifyTiming::FAnnotation& Annotation : Annotations)
		{
			if (SeenMoveIds.Contains(Annotation.MoveId)) continue;
			SeenMoveIds.Add(Annotation.MoveId);

			const FRPGAttackTiming* const* MatchingRowPtr = Rows.FindByPredicate([&Annotation](const FRPGAttackTiming* Row) { return Row->MoveId == Annotation.MoveId; });
			const FRPGAttackTiming* MatchingRow = MatchingRowPtr ? *MatchingRowPtr : nullptr;
			if (!MatchingRow)
			{
				++MismatchCount;
				UE_LOG(LogTemp, Error, TEXT("[EmberTimingAudit] MISMATCH asset=%s move=%s reason=no_tracker_row_for_montage"), *MontagePath, *Annotation.MoveId.ToString());
				continue;
			}

			const TArray<FString> Mismatches = Compare(Annotation, *MatchingRow, Tracker->BranchRange, Tracker->BranchConeDegrees);
			if (!Mismatches.IsEmpty())
			{
				++MismatchCount;
				UE_LOG(LogTemp, Error, TEXT("[EmberTimingAudit] MISMATCH asset=%s move=%s fields=%s"), *MontagePath, *Annotation.MoveId.ToString(), *FString::Join(Mismatches, TEXT(",")));
			}
			else
			{
				UE_LOG(LogTemp, Display, TEXT("[EmberTimingAudit] MATCH asset=%s move=%s"), *MontagePath, *Annotation.MoveId.ToString());
			}
		}

		if (Rows.IsEmpty())
		{
			++UntrackedCount;
			UE_LOG(LogTemp, Display, TEXT("[EmberTimingAudit] UNTRACKED asset=%s annotations=%d"), *MontagePath, Annotations.Num());
			continue;
		}
		for (const FRPGAttackTiming* Row : Rows)
		{
			if (!SeenMoveIds.Contains(Row->MoveId))
			{
				++MissingCount;
				UE_LOG(LogTemp, Display, TEXT("[EmberTimingAudit] MISSING asset=%s move=%s"), *MontagePath, *Row->MoveId.ToString());
			}
		}
	}

	UE_LOG(LogTemp, Display, TEXT("[EmberTimingAudit] SUMMARY montages=%d missing=%d mismatch=%d duplicate=%d invalid=%d untracked=%d strict=%d read_only=true"),
		MontageCount, MissingCount, MismatchCount, DuplicateCount, InvalidCount, UntrackedCount, bStrict ? 1 : 0);
	return ShouldFailStrictAudit(bStrict, MismatchCount, DuplicateCount, InvalidCount) ? 1 : 0;
}

#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FEmberMontageTimingAuditComparisonTest,
	"OneBossFight.Editor.EmberMontageTimingAudit.Comparison",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FEmberMontageTimingAuditComparisonTest::RunTest(const FString& Parameters)
{
	RPGMontageNotifyTiming::FAnnotation Annotation;
	Annotation.MoveId = TEXT("A1");
	Annotation.CommitTime = 0.33f;
	Annotation.WindowStartTime = 0.35f;
	Annotation.WindowEndTime = 0.50f;
	Annotation.RecoveryEndTime = 1.20f;
	Annotation.TrackTurnRate = 360.f;
	Annotation.bBranchStage = true;
	Annotation.bAuthoredWindup = true;
	Annotation.BranchRange = 400.f;
	Annotation.BranchConeDegrees = 120.f;
	FRPGAttackTiming Tracker;
	Tracker.MoveId = TEXT("A1");
	Tracker.CommitTime = 0.33f;
	Tracker.ActiveStartTime = 0.35f;
	Tracker.ActiveEndTime = 0.50f;
	Tracker.RecoveryEndTime = 1.20f;
	Tracker.TrackTurnRate = 360.f;
	Tracker.bBranchStage = true;
	Tracker.bAuthoredWindup = true;
	TestTrue(TEXT("matching annotation reports no mismatch"), Compare(Annotation, Tracker, 400.f, 120.f).IsEmpty());

	Annotation.WindowEndTime += 0.0201f;
	TestTrue(TEXT("time difference above 0.02 seconds is reported"), Compare(Annotation, Tracker, 400.f, 120.f).ContainsByPredicate(
		[](const FString& Field) { return Field.StartsWith(TEXT("WindowEndTime")); }));
	Annotation.WindowEndTime = Tracker.ActiveEndTime;
	Annotation.bBranchStage = false;
	TestTrue(TEXT("boolean tracker differences are reported exactly"), Compare(Annotation, Tracker, 400.f, 120.f).Contains(TEXT("bBranchStage")));
	Annotation.bBranchStage = true;
	Annotation.BranchRange = 350.f;
	TestTrue(TEXT("branch range is checked against tracker instance value"), Compare(Annotation, Tracker, 400.f, 120.f).ContainsByPredicate(
		[](const FString& Field) { return Field.StartsWith(TEXT("BranchRange")); }));
	Annotation.BranchRange = 400.f;
	Annotation.BranchConeDegrees = 110.f;
	TestTrue(TEXT("branch cone is checked against tracker instance value"), Compare(Annotation, Tracker, 400.f, 120.f).ContainsByPredicate(
		[](const FString& Field) { return Field.StartsWith(TEXT("BranchConeDegrees")); }));
	Annotation.BranchConeDegrees = 120.f;
	Annotation.TrackTurnRate += 1.f;
	TestTrue(TEXT("non-time numeric tracker differences are reported"), Compare(Annotation, Tracker, 400.f, 120.f).ContainsByPredicate(
		[](const FString& Field) { return Field.StartsWith(TEXT("TrackTurnRate")); }));
	TestFalse(TEXT("non-strict audit remains report-only for annotation defects"), ShouldFailStrictAudit(false, 1, 1, 1));
	TestTrue(TEXT("strict audit fails on any annotation mismatch"), ShouldFailStrictAudit(true, 1, 0, 0));
	TestTrue(TEXT("strict audit fails on any duplicate"), ShouldFailStrictAudit(true, 0, 1, 0));
	TestTrue(TEXT("strict audit fails on any invalid annotation"), ShouldFailStrictAudit(true, 0, 0, 1));
	return true;
}
#endif
