#include "Boss/RPGTimelineCompiler.h"

namespace RPGTimeline
{
namespace
{
bool IsDigest(const FString& Text)
{
	if (Text.Len() != 64) { return false; }
	for (TCHAR C : Text) { if (!FChar::IsHexDigit(C)) { return false; } }
	return true;
}
}
bool FKey::operator==(const FKey& B) const
{
	return Move == B.Move && Variant == B.Variant && Slot == B.Slot && Section == B.Section
		&& AssetPath == B.AssetPath && AssetSHA256 == B.AssetSHA256 && AdapterSHA256 == B.AdapterSHA256 && Schema == B.Schema
		&& bSyntheticFixture == B.bSyntheticFixture && ProjectionPolicy == B.ProjectionPolicy;
}
#if WITH_DEV_AUTOMATION_TESTS
FKey SyntheticKey(FName Move, FName Variant)
{
	FKey Key; Key.Move = Move; Key.Variant = Variant; Key.Slot = TEXT("DefaultSlot");
	Key.AssetPath = TEXT("/__Synthetic__/") + Move.ToString();
	Key.AssetSHA256 = FString::ChrN(64, TEXT('a')); Key.AdapterSHA256 = FString::ChrN(64, TEXT('b'));
	Key.bSyntheticFixture = true; return Key; // synthetic tokens, never attested file hashes
}
#endif
FCompileResult Compile(const FKey& Key, double Length, const TArray<FWindow>& Windows,
	const TArray<FMarker>& Markers, bool bSegmentMappingVerified, EOverhangPolicy Overhang)
{
	FCompileResult Result;
#if !WITH_DEV_AUTOMATION_TESTS
	if (Key.bSyntheticFixture) { Result.Errors.Add(TEXT("synthetic keys unavailable in this target")); }
#endif
	if (Key.bSyntheticFixture && !Key.AssetPath.StartsWith(TEXT("/__Synthetic__/"))) { Result.Errors.Add(TEXT("synthetic key must use explicit synthetic domain")); }
	if (Key.Schema != 1 || Key.Move.IsNone() || Key.Variant.IsNone() || Key.Slot.IsNone()
		|| Key.AssetPath.IsEmpty() || !IsDigest(Key.AssetSHA256) || !IsDigest(Key.AdapterSHA256)
		|| !FMath::IsFinite(Length) || Length <= 0. || !bSegmentMappingVerified)
	{
		Result.Errors.Add(TEXT("timeline identity/duration/segment mapping missing"));
	}
	TSet<FName> Ids;
	for (const FWindow& W : Windows)
	{
		if (W.Id.IsNone() || Ids.Contains(W.Id) || W.Semantic.IsNone() || W.SourceObject.IsEmpty()
			|| !IsDigest(W.PayloadHash) || !FMath::IsFinite(W.Begin) || !FMath::IsFinite(W.End)
			|| W.Begin < 0. || W.Begin >= Length || W.End <= W.Begin
			|| (W.End > Length && Overhang == EOverhangPolicy::Reject))
		{
			Result.Errors.Add(TEXT("invalid/duplicate window"));
		}
		Ids.Add(W.Id);
	}
	for (const FMarker& M : Markers)
	{
		if (M.Id.IsNone() || Ids.Contains(M.Id) || M.Semantic.IsNone() || M.Provenance.IsEmpty()
			|| !FMath::IsFinite(M.Position) || M.Position < 0. || M.Position > Length)
		{
			Result.Errors.Add(TEXT("invalid/duplicate marker"));
		}
		Ids.Add(M.Id);
	}
	if (Ids.IsEmpty()) { Result.Errors.Add(TEXT("empty timeline is uncovered, not a match")); }
	if (!Result.Errors.IsEmpty()) { return Result; }
	auto Out = MakeShared<FCompiled>(); Out->Key = Key; Out->Length = Length;
	Out->Key.ProjectionPolicy = Overhang;
	Out->Windows = Windows; Out->Markers = Markers; Result.Value = Out;
	for (FWindow& W : Out->Windows)
	{
		if (W.End > Length)
		{
			W.RawEnd = W.End; W.End = Length;
			Out->Diagnostics.Add(TEXT("notify overhang clipped for playback-position diagnostics only; raw end retained, blend-out lifespan unproved: ") + W.Id.ToString());
		}
	}
	return Result;
}

void FCursor::Close() { bOpen = false; }

FAdvance FCursor::Advance(const FCompiled& Timeline, const FObservation& O)
{
	FAdvance R;
	if (!(O.Timeline == Timeline.Key)) { R.Status = EStatus::MissingMetadata; R.Limitation = TEXT("artifact key mismatch"); return R; }
	if (!O.Participant.WorldSession.IsValid() || !O.Participant.EncounterInstance.IsValid()
		|| O.Participant.Slot.IsNone() || O.Participant.Generation == 0 || O.Sample == 0 || O.PlaybackOrdinal == 0
		|| !FMath::IsFinite(O.Previous) || !FMath::IsFinite(O.Current) || !FMath::IsFinite(O.GameTime)
		|| !FMath::IsFinite(O.Rate) || O.Previous < 0. || O.Current < 0. || O.Current > Timeline.Length || O.Previous > Timeline.Length)
	{
		R.Status = EStatus::InvalidRun; R.Limitation = TEXT("invalid participant/sample/time"); return R;
	}
	if (bSeen && O.Sample <= Last.Sample)
	{
		R.Limitation = TEXT("duplicate/out-of-order sample ignored"); return R;
	}
	const bool Same = bSeen && O.Participant == Last.Participant && O.PlaybackOrdinal == Last.PlaybackOrdinal
		&& O.Timeline == Last.Timeline && O.EngineInstance == Last.EngineInstance;
	if (bOpen && !Same)
	{
		R.Crossings.Add({NAME_None, TEXT("observed-replacement-or-generation"), Last.Current, EEdge::Closed}); Close();
	}
	if (O.bStopped)
	{
		if (bOpen) { R.Crossings.Add({NAME_None, TEXT("observed-stop-cause-unknown"), O.Current, EEdge::Closed}); }
		Close(); Last = O; bSeen = true; R.Limitation = TEXT("stop observed; final crossed interval not inferred"); return R;
	}
	// A closed cursor cannot be resurrected by another sample of the same playback.
	if (Same && !bOpen)
	{
		Last = O; R.Limitation = TEXT("closed playback requires new ordinal"); return R;
	}
	const bool Initial = !bOpen;
	const bool Contiguous = !Same || FMath::Abs(O.Previous - Last.Current) <= 1.e-6;
	const bool Forward = O.Traversal == ETraversal::Forward && O.Rate >= 0.f && O.Current >= O.Previous;
	const bool KnownLoop = Same && O.Traversal == ETraversal::Loop && O.bLoopPathVerified
		&& O.LoopBegin.IsSet() && O.LoopEnd.IsSet()
		&& FMath::IsFinite(O.LoopBegin.GetValue()) && FMath::IsFinite(O.LoopEnd.GetValue())
		&& O.LoopBegin.GetValue() >= 0. && O.LoopEnd.GetValue() <= Timeline.Length
		&& O.LoopEnd.GetValue() > O.LoopBegin.GetValue() && O.Rate >= 0.f
		&& O.LoopOrdinal > Last.LoopOrdinal && O.LoopOrdinal - Last.LoopOrdinal == 1
		&& O.Previous >= O.LoopBegin.GetValue() && O.Previous <= O.LoopEnd.GetValue()
		&& O.Current >= O.LoopBegin.GetValue() && O.Current <= O.LoopEnd.GetValue();
	const bool SameLoopForward = Forward && (!Same || O.LoopOrdinal == Last.LoopOrdinal);
	const bool StartsAtZero = Initial && O.Previous == 0.;
	const uint32 PreviousLoop = bSeen ? Last.LoopOrdinal : O.LoopOrdinal;
	bOpen = true; Last = O; bSeen = true;
	if ((!SameLoopForward && !KnownLoop) || !Contiguous || (Initial && !StartsAtZero) || !O.EngineInstance.IsSet())
	{
		R.Limitation = TEXT("reverse/loop/jump/gap/midclip/uncertain instance; path not inferred"); return R;
	}
	auto AddSpan = [&](double Begin, double End, bool IncludeBegin, uint32 Loop)
	{
		auto Crossed = [&](double Time) { return (Time > Begin && Time <= End) || (IncludeBegin && Time == Begin); };
		for (const FWindow& W : Timeline.Windows)
		{
			if (Crossed(W.Begin)) { R.Crossings.Add({W.Id, W.Semantic, W.Begin, EEdge::Begin, Loop}); }
			if (Crossed(W.End)) { R.Crossings.Add({W.Id, W.Semantic, W.End, EEdge::End, Loop}); }
		}
		for (const FMarker& M : Timeline.Markers)
		{
			if (Crossed(M.Position)) { R.Crossings.Add({M.Id, M.Semantic, M.Position, EEdge::Marker, Loop}); }
		}
	};
	if (KnownLoop)
	{
		AddSpan(O.Previous, O.LoopEnd.GetValue(), false, PreviousLoop);
		AddSpan(O.LoopBegin.GetValue(), O.Current, true, O.LoopOrdinal);
	}
	else { AddSpan(O.Previous, O.Current, StartsAtZero, O.LoopOrdinal); }
	R.Crossings.Sort([](const FCrossing& A, const FCrossing& B)
	{
		if (A.Edge == EEdge::Closed || B.Edge == EEdge::Closed) { return A.Edge == EEdge::Closed && B.Edge != EEdge::Closed; }
		if (A.LoopOrdinal != B.LoopOrdinal) { return A.LoopOrdinal < B.LoopOrdinal; }
		if (A.Position != B.Position) { return A.Position < B.Position; }
		if (A.Edge != B.Edge) { return static_cast<uint8>(A.Edge) < static_cast<uint8>(B.Edge); }
		return A.Id.LexicalLess(B.Id);
	});
	R.Status = EStatus::Match; // Traversal extraction valid only; NOT gameplay parity acceptance.
	return R;
}

const TArray<FExpectedDifference>& ExpectedDifferences()
{
	static const TArray<FExpectedDifference> Rows = {
		{TEXT("A2_ENGINE_VS_TRACKER_WINDOWS"), TEXT("two engine collision intervals vs legacy 1.93-2.11; retain both"), TEXT("E-005; E-002-10")},
		{TEXT("A2_OBSERVED_EARLY_TERMINATION"), TEXT("frozen six-fight sample: 9 Windup,1 Active,1 Recovery replacement; T4 1.388s, cause unknown; not future frequencies"), TEXT("E-005")},
		{TEXT("PACK_UNTRACKED"), TEXT("Mid01/sprint/retaliation lack native tracker identity; no natural-frequency inference"), TEXT("E-002; E-004")},
		{TEXT("A4_QUERY_VS_BOUNDS_ENDPOINT"), TEXT("planar query vs estimated bounds endpoint; angle51..174; no physical socket/floor proof"), TEXT("E-008")},
		{TEXT("A5_INTENT_VS_COMPAT_RELEASE"), TEXT("0.40 intent vs 0.45 nominal/0.47 first sampled; never retime"), TEXT("E-007")},
		{TEXT("FALLBACK_ALIAS_TIMELINE"), TEXT("authored/fallback can alias legacy row; artifact remains per variant"), TEXT("E-002-10; RV-03")}
	};
	return Rows;
}
}
