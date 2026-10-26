#include "Boss/RPGShadowCompare.h"
#include "Player/RPGAttackTracker.h"
#include "Player/RPGBossEncounter.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Animation/AnimSequenceBase.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/Character.h"
#include "Engine/World.h"
#include "Dom/JsonObject.h"
#include "Dom/JsonValue.h"
#include "Policies/CondensedJsonPrintPolicy.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"

namespace RPGTimeline
{
FPassiveSnapshot CaptureAfterTracker(const URPGAttackTracker& Tracker)
{
	FPassiveSnapshot S;
	S.Legacy.Move = Tracker.GetCurrentMove(); S.Legacy.bTracked = !S.Legacy.Move.IsNone();
	S.Legacy.Phase = Tracker.GetPhaseName(); S.Legacy.Instance = Tracker.GetAttackInstance();
	S.Legacy.IllegalStarts = Tracker.GetIllegalStartCount(); S.Legacy.DoubleLaunches = Tracker.GetDoubleLaunchCount();
	if (S.Legacy.bTracked)
	{
		S.Legacy.Position = Tracker.GetPosition(); FRPGAttackTiming Timing;
		if (Tracker.GetTiming(S.Legacy.Move, Timing)) { S.Legacy.ActiveBegin = Timing.ActiveStartTime; S.Legacy.ActiveEnd = Timing.ActiveEndTime; }
	}
	const ACharacter* Actor = Cast<ACharacter>(Tracker.GetOwner());
	const UAnimInstance* Anim = Actor && Actor->GetMesh() ? Actor->GetMesh()->GetAnimInstance() : nullptr;
	const UAnimMontage* Montage = Anim ? Anim->GetCurrentActiveMontage() : nullptr;
	if (Montage)
	{
		S.SourceAsset = Montage->GetPathName(); S.Position = Anim->Montage_GetPosition(Montage);
		S.Rate = Anim->Montage_GetPlayRate(Montage); S.Section = Anim->Montage_GetCurrentSection(Montage);
		if (const FAnimMontageInstance* Instance = Anim->GetActiveInstanceForMontage(Montage)) { S.EngineInstance = Instance->GetInstanceID(); }
		if (!Montage->SlotAnimTracks.IsEmpty())
		{
			S.Slot = Montage->SlotAnimTracks[0].SlotName;
			// Metadata only. Positions remain MONTAGE-local; importer must map segment-local notifies.
			if (const FAnimSegment* Segment = Montage->SlotAnimTracks[0].AnimTrack.GetSegmentAtTime(static_cast<float>(S.Position.GetValue())))
			{
				if (const UAnimSequenceBase* Clip = Segment->GetAnimReference()) { S.CurrentSegmentAsset = Clip->GetPathName(); }
			}
		}
	}
	S.GameTime = Tracker.GetWorld() ? Tracker.GetWorld()->GetTimeSeconds() : 0.;
	return S;
}

TOptional<FObservation> FPlaybackAdapter::Observe(const FPassiveSnapshot& S, const FRPGParticipantKey& Key,
	const TArray<TSharedPtr<const FCompiled>>& Artifacts)
{
	++Sequence;
	if (!S.Position.IsSet())
	{
		if (!Last.IsSet() || Last->bStopped) { return {}; }
		FObservation Stop = Last.GetValue(); Stop.Sample = Sequence; Stop.bStopped = true;
		Stop.GameTime = S.GameTime; Stop.Legacy = S.Legacy; Last = Stop; return Stop;
	}
	const FCompiled* Match = nullptr;
	for (const auto& Artifact : Artifacts)
	{
		if (!Artifact || (Artifact->Key.AssetPath != S.SourceAsset && Artifact->Key.AssetPath != S.CurrentSegmentAsset)
			|| Artifact->Key.Slot != S.Slot || Artifact->Key.Section != S.Section) { continue; }
		if (Match) { Last.Reset(); return {}; } // ambiguous metadata is uncovered, never first-variant fallback
		Match = Artifact.Get();
	}
	if (!Match) { Last.Reset(); return {}; }
	FObservation O; O.Participant = Key; O.Sample = Sequence; O.Timeline = Match->Key;
	O.ObservedSourceAsset = S.SourceAsset; O.ObservedSegmentAsset = S.CurrentSegmentAsset;
	O.Current = S.Position.GetValue(); O.Previous = O.Current; O.GameTime = S.GameTime;
	O.Rate = S.Rate.Get(0.f); O.EngineInstance = S.EngineInstance; O.Legacy = S.Legacy;
	const bool Same = Last.IsSet() && !Last->bStopped && Last->Participant == Key && Last->Timeline == O.Timeline
		&& Last->EngineInstance == O.EngineInstance && O.EngineInstance.IsSet();
	if (!Same) { ++Ordinal; }
	else { O.Previous = Last->Current; }
	O.PlaybackOrdinal = Ordinal;
	O.Traversal = !S.Rate.IsSet() ? ETraversal::Unknown : O.Rate < 0.f ? ETraversal::Reverse
		: (Same && O.Current < O.Previous ? ETraversal::Unknown : ETraversal::Forward);
	Last = O; return O;
}
}

URPGCombatTimelineShadow::URPGCombatTimelineShadow() { PrimaryComponentTick.bCanEverTick = false; }

bool URPGCombatTimelineShadow::Configure(const TArray<TSharedPtr<const RPGTimeline::FCompiled>>& Values,
	const FRPGParticipantKey& Key, TSharedPtr<const RPGCombatRegistry::FEpoch> Lease)
{
	if (!Timelines.IsEmpty() || IsRegistered() || Values.IsEmpty() || !Lease || !Key.WorldSession.IsValid() || !Key.EncounterInstance.IsValid()
		|| Key.Slot.IsNone() || Key.Generation == 0) { return false; }
	for (int32 I = 0; I < Values.Num(); ++I)
	{
		if (!Values[I]) { return false; }
		for (int32 J = 0; J < I; ++J) { if (Values[J]->Key == Values[I]->Key) { return false; } }
	}
	Timelines = Values; Participant = Key; ContentLease = MoveTemp(Lease); return true;
}

bool URPGCombatTimelineShadow::BindTracker(URPGAttackTracker& Tracker, URPGCombatContextSubsystem& InContext)
{
#if UE_BUILD_SHIPPING
	return false;
#else
	if (Timelines.IsEmpty() || BoundTracker.IsValid() || Tracker.GetOwner() != GetOwner()
		|| !InContext.IsCurrent(Participant)) { return false; }
	BoundTracker = &Tracker; Context = &InContext;
	// Requires the staged tracker seam; never poll/tick the tracker a second time.
	ObservationHandle = Tracker.OnAfterObservation.AddUObject(this, &URPGCombatTimelineShadow::OnSnapshot);
	return true;
#endif
}

void URPGCombatTimelineShadow::OnSnapshot(const RPGTimeline::FPassiveSnapshot& Sample)
{
	if (!Context.IsValid() || !GetOwner()) { Cursor.Close(); return; }
	const auto CurrentKey = Context->FindParticipant(*GetOwner());
	if (!CurrentKey.IsSet()) { Cursor.Close(); return; }
	if (!(Participant == CurrentKey.GetValue())) { Cursor.Close(); Participant = CurrentKey.GetValue(); }
	if (auto Observation = Playback.Observe(Sample, Participant, Timelines)) { ObserveAfterTracker(Observation.GetValue()); }
	else if (Sample.Position.IsSet()) { ++Dropped; } // unmatched playback reduces coverage; idle isn't a dropped event
}

void URPGCombatTimelineShadow::ObserveAfterTracker(const RPGTimeline::FObservation& O)
{
#if !UE_BUILD_SHIPPING
	if (!(Participant == O.Participant)) { return; }
	const TSharedPtr<const RPGTimeline::FCompiled>* Found = Timelines.FindByPredicate([&O](const auto& A) { return A && A->Key == O.Timeline; });
	if (!Found) { ++Dropped; return; }
	const auto& Timeline = *Found;
	// Keep cursor chronology even after report capacity is exhausted.
	const RPGTimeline::FAdvance Advance = Cursor.Advance(*Timeline, O);
	if (Records.Num() >= MaxRecords) { ++Dropped; return; }
	auto Row = MakeShared<FJsonObject>();
	Row->SetStringField(TEXT("world_session"), Participant.WorldSession.ToString());
	Row->SetStringField(TEXT("encounter_instance"), Participant.EncounterInstance.ToString());
	Row->SetStringField(TEXT("participant_slot"), Participant.Slot.ToString());
	Row->SetNumberField(TEXT("generation"), Participant.Generation);
	// uint64 cannot be represented losslessly by JSON numbers; serialize decimal strings.
	Row->SetStringField(TEXT("observation_ordinal"), LexToString(O.Sample));
	Row->SetStringField(TEXT("playback_ordinal"), LexToString(O.PlaybackOrdinal));
	if (O.AuthoritativeAction.IsSet()) { Row->SetStringField(TEXT("authoritative_action"), O.AuthoritativeAction.GetValue()); }
	else { Row->SetField(TEXT("authoritative_action"), MakeShared<FJsonValueNull>()); }
	Row->SetStringField(TEXT("source_asset"), O.Timeline.AssetPath);
	Row->SetStringField(TEXT("observed_source_asset"), O.ObservedSourceAsset);
	Row->SetStringField(TEXT("observed_segment_asset"), O.ObservedSegmentAsset);
	Row->SetStringField(TEXT("asset_sha256"), O.Timeline.AssetSHA256);
	Row->SetStringField(TEXT("adapter_sha256"), O.Timeline.AdapterSHA256);
	Row->SetBoolField(TEXT("synthetic_fixture"), O.Timeline.bSyntheticFixture);
	Row->SetNumberField(TEXT("projection_policy"), static_cast<int32>(O.Timeline.ProjectionPolicy));
	Row->SetStringField(TEXT("move"), O.Timeline.Move.ToString()); Row->SetStringField(TEXT("variant"), O.Timeline.Variant.ToString());
	Row->SetStringField(TEXT("section"), O.Timeline.Section.ToString());
	Row->SetStringField(TEXT("coverage_scope"), TEXT("GetCurrentActiveMontage result; first slot track/current segment only; other slots, additive sequences, inactive blend-outs UNCOVERED"));
	Row->SetNumberField(TEXT("previous"), O.Previous); Row->SetNumberField(TEXT("current"), O.Current);
	Row->SetNumberField(TEXT("game_time"), O.GameTime); Row->SetNumberField(TEXT("actual_rate"), O.Rate);
	Row->SetNumberField(TEXT("traversal"), static_cast<int32>(O.Traversal)); Row->SetNumberField(TEXT("loop"), O.LoopOrdinal);
	if (O.EngineInstance.IsSet()) { Row->SetNumberField(TEXT("engine_instance"), O.EngineInstance.GetValue()); }
	else { Row->SetField(TEXT("engine_instance"), MakeShared<FJsonValueNull>()); }
	auto Legacy = MakeShared<FJsonObject>();
	Legacy->SetBoolField(TEXT("tracked"), O.Legacy.bTracked); Legacy->SetStringField(TEXT("move"), O.Legacy.Move.ToString());
	Legacy->SetStringField(TEXT("phase"), O.Legacy.Phase); Legacy->SetNumberField(TEXT("instance"), O.Legacy.Instance);
	Legacy->SetNumberField(TEXT("illegal_starts"), O.Legacy.IllegalStarts); Legacy->SetNumberField(TEXT("double_launches"), O.Legacy.DoubleLaunches);
	Row->SetObjectField(TEXT("legacy_snapshot"), Legacy);
	TArray<TSharedPtr<FJsonValue>> Crossings;
	for (const RPGTimeline::FCrossing& C : Advance.Crossings)
	{
		auto Item = MakeShared<FJsonObject>(); Item->SetStringField(TEXT("id"), C.Id.ToString());
		Item->SetStringField(TEXT("semantic"), C.Semantic.ToString()); Item->SetNumberField(TEXT("position"), C.Position);
		Item->SetNumberField(TEXT("edge"), static_cast<int32>(C.Edge)); Crossings.Add(MakeShared<FJsonValueObject>(Item));
		Item->SetNumberField(TEXT("loop_ordinal"), C.LoopOrdinal);
	}
	Row->SetArrayField(TEXT("compiled_crossings"), Crossings);
	TArray<TSharedPtr<FJsonValue>> Projections;
	for (const auto& W : Timeline->Windows)
	{
		if (!W.RawEnd.IsSet()) { continue; }
		auto Projection = MakeShared<FJsonObject>(); Projection->SetStringField(TEXT("window_id"), W.Id.ToString());
		Projection->SetNumberField(TEXT("ClampedFrom"), W.RawEnd.GetValue()); Projection->SetNumberField(TEXT("effective_end"), W.End);
		Projection->SetStringField(TEXT("provenance_flag"), TEXT("DIAGNOSTIC_PLAYBACK_END_PROJECTION_NOT_OBSERVED_NOTIFY_CLEANUP"));
		Projections.Add(MakeShared<FJsonValueObject>(Projection));
	}
	Row->SetArrayField(TEXT("window_projections"), Projections);
	FString Status = TEXT("INCONCLUSIVE_SAMPLING");
	if (Advance.Status == RPGTimeline::EStatus::InvalidRun) { Status = TEXT("INVALID_RUN"); }
	else if (Advance.Status == RPGTimeline::EStatus::MissingMetadata) { Status = TEXT("MISSING_METADATA"); }
	else if (Advance.Status == RPGTimeline::EStatus::Match)
	{
		if (!O.Legacy.bTracked) { Status = TEXT("UNTRACKED_PACK_PATH"); }
		else if (!O.Legacy.ActiveBegin.IsSet() || !O.Legacy.ActiveEnd.IsSet()) { Status = TEXT("MISSING_METADATA"); }
		else
		{
			bool EngineActive = false, HasActiveMetadata = false;
			for (const auto& W : Timeline->Windows)
			{
				if (W.Semantic == FName(TEXT("Collision")) || W.Semantic == FName(TEXT("ActiveDamage")))
				{
					HasActiveMetadata = true;
					if (O.Current >= W.Begin && O.Current < W.End) { EngineActive = true; }
				}
			}
			const bool LegacyActive = O.Legacy.Phase == TEXT("Active");
			Status = !HasActiveMetadata ? TEXT("MISSING_METADATA") : EngineActive == LegacyActive ? TEXT("MATCH") : TEXT("REGRESSION_CANDIDATE");
		}
	}
	Row->SetStringField(TEXT("comparison_status"), Status);
	Row->SetStringField(TEXT("limitation"), Advance.Limitation + TEXT("; MATCH covers sampled active state only, not hit/geometry/cause parity"));
	// Registry entries annotate possible explanations; never whitelist an arbitrary discrepancy.
	TArray<TSharedPtr<FJsonValue>> References;
	for (const auto& Expected : RPGTimeline::ExpectedDifferences())
	{
		auto Ref = MakeShared<FJsonObject>(); Ref->SetStringField(TEXT("id"), Expected.Id.ToString());
		Ref->SetStringField(TEXT("boundary"), Expected.Boundary); Ref->SetStringField(TEXT("evidence"), Expected.Evidence);
		References.Add(MakeShared<FJsonValueObject>(Ref));
	}
	Row->SetArrayField(TEXT("possible_explanations_not_acceptance"), References);
	Records.Add(Row);
#endif
}

bool URPGCombatTimelineShadow::FlushReport(const TSharedRef<FJsonObject>& RunHeader, FString& OutPath)
{
	OutPath.Reset();
#if UE_BUILD_SHIPPING
	return false;
#else
	// Reject incomplete provenance rather than inventing run validity or DLL identity.
	const TCHAR* Required[] = {TEXT("run_id"), TEXT("dll_hash"), TEXT("source_manifest"), TEXT("map"),
		TEXT("requested_source"), TEXT("published_source"), TEXT("content_hash"), TEXT("local_epoch"),
		TEXT("validity"), TEXT("cvars_start"), TEXT("cvars_end"), TEXT("window_state"), TEXT("game_sample_dt"),
		TEXT("slate_sample_dt"), TEXT("assets_before_after"), TEXT("scripts_before_after"), TEXT("net_mode_role")};
	for (const TCHAR* Field : Required) { if (!RunHeader->HasField(Field)) { return false; } }
	auto Header = MakeShared<FJsonObject>(); Header->Values = RunHeader->Values;
	Header->SetNumberField(TEXT("schema"), 1); Header->SetNumberField(TEXT("dropped_records"), Dropped);
	Header->SetNumberField(TEXT("record_count"), Records.Num());
	if (Records.IsEmpty()) { Header->SetStringField(TEXT("coverage"), TEXT("UNCOVERED")); }
	FString Text, Line;
	if (!FJsonSerializer::Serialize(Header.ToSharedRef(), TJsonWriterFactory<TCHAR, TCondensedJsonPrintPolicy<TCHAR>>::Create(&Line))) { return false; }
	Text = Line + TEXT("\n");
	for (const auto& Row : Records)
	{
		Line.Reset();
		if (!FJsonSerializer::Serialize(Row.ToSharedRef(), TJsonWriterFactory<TCHAR, TCondensedJsonPrintPolicy<TCHAR>>::Create(&Line))) { return false; }
		Text += Line + TEXT("\n");
	}
	const FString Directory = FPaths::Combine(FPaths::ProjectSavedDir(), TEXT("BossCombatReview/Shadow"));
	if (!IFileManager::Get().MakeDirectory(*Directory, true)) { return false; }
	const FString Path = FPaths::Combine(Directory, FGuid::NewGuid().ToString(EGuidFormats::Digits) + TEXT(".jsonl"));
	if (!FFileHelper::SaveStringToFile(Text, *Path, FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM)) { return false; }
	OutPath = Path; Records.Reset(); Dropped = 0; return true;
#endif
}

void URPGCombatTimelineShadow::EndPlay(const EEndPlayReason::Type Reason)
{
	if (BoundTracker.IsValid())
	{
#if !UE_BUILD_SHIPPING
		BoundTracker->OnAfterObservation.Remove(ObservationHandle);
#endif
	}
	BoundTracker.Reset(); Context.Reset(); Cursor.Close(); Timelines.Reset(); ContentLease.Reset(); Records.Reset(); Super::EndPlay(Reason);
}
