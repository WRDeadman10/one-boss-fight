#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
#include "Boss/RPGTimelineCompiler.h"
#include "Boss/RPGShadowCompare.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGTimelineDraftTest, "OneBossFight.Timeline.DraftCrossings",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)
bool FRPGTimelineDraftTest::RunTest(const FString& Parameters)
{
	using namespace RPGTimeline;
	FKey Key = SyntheticKey(TEXT("Synthetic"), TEXT("VariantA"));
	FWindow W; W.Id = TEXT("trace1"); W.Semantic = TEXT("Collision"); W.Begin = .2; W.End = .4;
	W.SourceObject = TEXT("synthetic notify"); W.PayloadHash = FString::ChrN(64, TEXT('c'));
	FWindow W2 = W; W2.Id = TEXT("trace2"); W2.Begin = .6; W2.End = .8;
	FMarker M; M.Id = TEXT("start"); M.Semantic = TEXT("Start"); M.Position = 0.; M.Provenance = TEXT("synthetic");
	auto CompileResult = Compile(Key, 1., {W, W2}, {M}, true);
	if (!TestTrue(TEXT("compile valid synthetic artifact"), CompileResult.Value.IsValid())) { return false; }
	TestFalse(TEXT("segment map must be verified"), Compile(Key, 1., {W}, {M}, false).Value.IsValid());
	TestFalse(TEXT("duplicate notify rejected"), Compile(Key, 1., {W, W}, {}, true).Value.IsValid());
	FKey BadKey = Key; BadKey.AssetSHA256 = TEXT("bad");
	TestFalse(TEXT("hash key rejected"), Compile(BadKey, 1., {W}, {}, true).Value.IsValid());
	TestFalse(TEXT("zero samples not empty timeline pass"), Compile(Key, 1., {}, {}, true).Value.IsValid());
	FWindow Overhang = W; Overhang.End = 2.;
	TestFalse(TEXT("overhang needs explicit projection policy"), Compile(Key, 1., {Overhang}, {}, true).Value.IsValid());
	auto Clipped = Compile(Key, 1., {Overhang}, {}, true, EOverhangPolicy::ClipDiagnosticToPlaybackEnd);
	TestTrue(TEXT("projection retains raw end and diagnostic"), Clipped.Value && Clipped.Value->Windows[0].End == 1.
		&& Clipped.Value->Windows[0].RawEnd.Get(0.) == 2. && !Clipped.Value->Diagnostics.IsEmpty());
	Overhang.Begin = 1.2;
	TestFalse(TEXT("begin beyond length cannot be clamped to backwards window"), Compile(Key, 1., {Overhang}, {}, true, EOverhangPolicy::ClipDiagnosticToPlaybackEnd).Value.IsValid());
	FObservation O; O.Participant = {FGuid::NewGuid(), FGuid::NewGuid(), TEXT("Boss"), 1};
	O.Timeline = Key; O.Sample = 1; O.PlaybackOrdinal = 1; O.EngineInstance = 12;
	O.Previous = 0.; O.Current = .1; O.Traversal = ETraversal::Forward;
	FCursor First, Second;
	auto R = First.Advance(*CompileResult.Value, O);
	TestEqual(TEXT("start0 once"), R.Crossings.Num(), 1);
	TestEqual(TEXT("duplicate produces no edges"), First.Advance(*CompileResult.Value, O).Crossings.Num(), 0);
	O.Sample = 2; O.Previous = .1; O.Current = .9;
	R = First.Advance(*CompileResult.Value, O);
	TestEqual(TEXT("hitch crosses both windows in/out"), R.Crossings.Num(), 4);
	TestTrue(TEXT("chronological edges"), R.Crossings.Num() == 4 && R.Crossings[0].Position == .2 && R.Crossings[3].Position == .8);
	O.Sample = 3; O.Previous = .9; O.Current = 1.;
	TestEqual(TEXT("no repeated edges"), First.Advance(*CompileResult.Value, O).Crossings.Num(), 0);
	O.Sample = 4; O.bStopped = true;
	TestEqual(TEXT("stop closes once"), First.Advance(*CompileResult.Value, O).Crossings.Num(), 1);
	O.Sample = 5;
	TestEqual(TEXT("repeat stop not duplicated"), First.Advance(*CompileResult.Value, O).Crossings.Num(), 0);
	O.bStopped = false; O.PlaybackOrdinal = 2; O.EngineInstance = 13; O.Sample = 6; O.Previous = 0.; O.Current = .2;
	TestEqual(TEXT("same asset new instance starts fresh incl exact endpoint"), First.Advance(*CompileResult.Value, O).Crossings.Num(), 2);
	O.Participant.Generation = 2; O.Sample = 7; O.PlaybackOrdinal = 3; O.EngineInstance = 14; O.Previous = 0.; O.Current = .1;
	R = First.Advance(*CompileResult.Value, O);
	TestTrue(TEXT("generation closes old and opens new"), R.Crossings.Num() == 2 && R.Crossings[0].Edge == EEdge::Closed);
	O.Sample = 8; O.Traversal = ETraversal::Reverse; O.Rate = -1.f; O.Previous = .1; O.Current = 0.;
	TestTrue(TEXT("reverse explicitly inconclusive"), First.Advance(*CompileResult.Value, O).Status == EStatus::Inconclusive);
	O.Sample = 9; O.Traversal = ETraversal::SectionJump; O.Current = .7;
	TestTrue(TEXT("jump doesn't infer skipped hits"), First.Advance(*CompileResult.Value, O).Crossings.IsEmpty());
	O.Sample = 10; O.Traversal = ETraversal::Loop; O.Current = .1; O.LoopOrdinal = 1;
	TestTrue(TEXT("loop explicit inconclusive"), First.Advance(*CompileResult.Value, O).Status == EStatus::Inconclusive);
	FObservation Independent = O; Independent.Sample = 1; Independent.Previous = 0.; Independent.Current = .1;
	Independent.Traversal = ETraversal::Forward; Independent.Rate = 1.f;
	TestEqual(TEXT("second cursor independent"), Second.Advance(*CompileResult.Value, Independent).Crossings.Num(), 1);
	First.Close(); TestTrue(TEXT("closing first leaves second open"), Second.IsOpen());
	Independent.Sample = 2; Independent.EngineInstance.Reset();
	TestTrue(TEXT("missing engine identity inconclusive"), Second.Advance(*CompileResult.Value, Independent).Status == EStatus::Inconclusive);
	TestEqual(TEXT("six expected differences retained"), ExpectedDifferences().Num(), 6);
	FCursor LoopCursor; FObservation Loop = O; Loop.Sample = 1; Loop.Previous = 0.; Loop.Current = .9;
	Loop.Traversal = ETraversal::Forward; Loop.Rate = 1.f; Loop.LoopOrdinal = 0; Loop.EngineInstance = 99;
	LoopCursor.Advance(*CompileResult.Value, Loop);
	Loop.Sample = 2; Loop.Previous = .9; Loop.Current = .3; Loop.Traversal = ETraversal::Loop;
	Loop.LoopOrdinal = 1; Loop.bLoopPathVerified = true; Loop.LoopBegin = 0.; Loop.LoopEnd = 1.;
	auto Wrapped = LoopCursor.Advance(*CompileResult.Value, Loop);
	TestTrue(TEXT("verified single loop emits marker0 and next begin"), Wrapped.Status == EStatus::Match && Wrapped.Crossings.Num() == 2
		&& Wrapped.Crossings[0].LoopOrdinal == 1 && Wrapped.Crossings[1].LoopOrdinal == 1);
	TestTrue(TEXT("duplicate loop no second crossings"), LoopCursor.Advance(*CompileResult.Value, Loop).Crossings.IsEmpty());
	AddInfo(TEXT("Synthetic trace replay is not natural boss playback or engine off/on parity."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGTimelineA2GoldenDraftTest, "OneBossFight.Timeline.DraftA2Golden",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGTimelineA2GoldenDraftTest::RunTest(const FString& Parameters)
{
	using namespace RPGTimeline;
	// Independently checked scalar subset of AG16 Rev02 timeline_expected.json against
	// montage_notifies_2026-10-25.txt SHA256 c72b2c938b8aa8cfbe5be089a8449079df9269d03c6218d3c50fe3fa752763fc.
	// This is a synthetic replay of rounded export metadata, NOT the live montage or a full-payload proof.
	FKey Key = SyntheticKey(TEXT("AG16_A2_ScalarSubset"), TEXT("ExportRev02"));
	Key.AssetSHA256 = TEXT("c72b2c938b8aa8cfbe5be089a8449079df9269d03c6218d3c50fe3fa752763fc");
	const double Length = 3.4000000953674316;
	TArray<FWindow> Windows;
	auto Add = [&](const TCHAR* Id, const TCHAR* Semantic, double Begin, double End, const TCHAR* Hash)
	{
		FWindow W; W.Id = Id; W.Semantic = Semantic; W.Begin = Begin; W.End = End;
		W.SourceObject = TEXT("montage_notifies_2026-10-25.txt / GS_ChargedAttack_Montage"); W.PayloadHash = Hash;
		Windows.Add(W);
	};
	Add(TEXT("MovementLock"), TEXT("MovementLock"), 0., 4.933, TEXT("cc0c15572697ae1e519d150059af94498f7caa5e34ffc4ac7cb39cad0ef6e758"));
	Add(TEXT("Collision1"), TEXT("ActiveDamage"), 1.567, 1.760, TEXT("c6e25f9fc8c1c2357d53f315650aa46a8a22e7f3d7010bc5ea64a0ee4cc6a375"));
	Add(TEXT("Collision2"), TEXT("ActiveDamage"), 1.925, 2.104, TEXT("df596f6bb1fef1b43db24c0237c3871aefdd8a246a139c0935ffba352997366d"));
	TArray<FMarker> Markers;
	FMarker First; First.Id = TEXT("Sound1"); First.Semantic = TEXT("AcousticCue"); First.Position = 1.593; First.Provenance = Key.AssetSHA256;
	FMarker Second = First; Second.Id = TEXT("Sound2"); Second.Position = 1.817; Markers = {First, Second};
	auto C = Compile(Key, Length, Windows, Markers, true, EOverhangPolicy::ClipDiagnosticToPlaybackEnd);
	if (!TestTrue(TEXT("scalar export subset compiles with explicit projection"), C.Value.IsValid())) { return false; }
	TestTrue(TEXT("overhang retained, not normalized away"), C.Value->Windows[0].RawEnd.Get(0.) == 4.933 && C.Value->Windows[0].End == Length);
	FObservation O; O.Participant = {FGuid::NewGuid(), FGuid::NewGuid(), TEXT("Boss"), 1};
	O.Timeline = C.Value->Key; O.Sample = 1; O.PlaybackOrdinal = 1; O.EngineInstance = 11;
	O.Current = Length; O.Previous = 0.; O.Traversal = ETraversal::Forward;
	FCursor Cursor; auto R = Cursor.Advance(*C.Value, O);
	TestEqual(TEXT("full hitch:3 windows x2 edges +2 markers"), R.Crossings.Num(), 8);
	TestTrue(TEXT("both collision intervals retained independently"), C.Value->Windows[1].Begin == 1.567 && C.Value->Windows[2].Begin == 1.925);
	AddInfo(TEXT("AG16 jump/out-of-bounds/full-payload/section graph claims remain unaccepted; only independently checked scalar rows used here."));
	return true;
}
#endif
