#pragma once
#include "CoreMinimal.h"
#include "Player/RPGEncounterBinding.h"

namespace RPGTimeline
{
enum class ETraversal : uint8 { Forward, Reverse, Loop, SectionJump, Unknown };
enum class EEdge : uint8 { Begin, End, Marker, Closed };
enum class EStatus : uint8 { Match, Candidate, Untracked, Inconclusive, MissingMetadata, InvalidRun };
enum class EOverhangPolicy : uint8 { Reject, ClipDiagnosticToPlaybackEnd };

struct FKey
{
	FName Move, Variant, Slot, Section;
	FString AssetPath, AssetSHA256, AdapterSHA256;
	int32 Schema = 1;
	bool bSyntheticFixture = false;
	EOverhangPolicy ProjectionPolicy = EOverhangPolicy::Reject;
	bool operator==(const FKey& B) const;
};
struct FWindow
{
	FName Id, Semantic;
	double Begin = 0., End = 0.; // montage-local animation seconds, not wall seconds
	TOptional<double> RawEnd; // retained when a diagnostic projection clips a notify overhang
	FString SourceObject, PayloadHash;
};
struct FMarker
{
	FName Id, Semantic;
	double Position = 0.;
	FString Provenance;
};
struct FCompiled
{
	FKey Key;
	double Length = 0.;
	TArray<FWindow> Windows;
	TArray<FMarker> Markers;
	TArray<FString> Diagnostics;
};
struct FCompileResult
{
	TSharedPtr<const FCompiled> Value;
	TArray<FString> Errors;
};
/** Inputs must ALREADY be mapped to montage-local seconds. Unsupported segment maps reject. */
ONEBOSSFIGHT_API FCompileResult Compile(const FKey& Key, double Length,
	const TArray<FWindow>& Windows, const TArray<FMarker>& Markers, bool bSegmentMappingVerified,
	EOverhangPolicy Overhang = EOverhangPolicy::Reject);
#if WITH_DEV_AUTOMATION_TESTS
ONEBOSSFIGHT_API FKey SyntheticKey(FName Move, FName Variant);
#endif

struct FLegacySample
{
	bool bTracked = false;
	FName Move;
	FString Phase;
	int32 Instance = 0, IllegalStarts = 0, DoubleLaunches = 0;
	TOptional<double> ActiveBegin, ActiveEnd, Position;
};
struct FObservation
{
	FRPGParticipantKey Participant;
	uint64 Sample = 0, PlaybackOrdinal = 0;
	FKey Timeline;
	FString ObservedSourceAsset, ObservedSegmentAsset;
	double Previous = 0., Current = 0., GameTime = 0.;
	float Rate = 1.f;
	ETraversal Traversal = ETraversal::Unknown;
	uint32 LoopOrdinal = 0;
	/** Supplied only by a verified traversal source; a backwards position alone is insufficient. */
	bool bLoopPathVerified = false;
	TOptional<double> LoopBegin, LoopEnd;
	TOptional<int32> EngineInstance;
	// A diagnostic ordinal is NEVER an authoritative action identity.
	TOptional<FString> AuthoritativeAction;
	FLegacySample Legacy;
	bool bStopped = false;
};
struct FCrossing
{
	FName Id, Semantic;
	double Position = 0.;
	EEdge Edge = EEdge::Marker;
	uint32 LoopOrdinal = 0;
};
struct FAdvance
{
	TArray<FCrossing> Crossings;
	EStatus Status = EStatus::Inconclusive;
	FString Limitation;
};
class ONEBOSSFIGHT_API FCursor
{
public:
	FAdvance Advance(const FCompiled& Timeline, const FObservation& Observation);
	void Close();
	bool IsOpen() const { return bOpen; }
private:
	bool bOpen = false, bSeen = false;
	FObservation Last;
};
struct FExpectedDifference
{
	FName Id;
	FString Boundary, Evidence;
};
ONEBOSSFIGHT_API const TArray<FExpectedDifference>& ExpectedDifferences();
}
