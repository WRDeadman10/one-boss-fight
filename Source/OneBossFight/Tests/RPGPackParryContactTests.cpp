// Copyright One Boss Fight. All Rights Reserved.

#include <limits> // Lead fix C-1145: TNumericLimits has no QuietNaN in UE 5.5
#include "Misc/AutomationTest.h"
#include "Player/RPGPackParryRules.h"
#include "Player/RPGBossPosture.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPackParryCandidateRulesTest,
	"OneBossFight.Player.PackParry.CandidateRules",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FRPGPackParryCandidateRulesTest::RunTest(const FString& Parameters)
{
	using namespace RPGPackParry;
	TestTrue(TEXT("current open native parry window admits a candidate"), CanStartCandidate(true, false));
	TestTrue(TEXT("the preceding sampled open frame admits a candidate"), CanStartCandidate(true, false));
	TestFalse(TEXT("closed now and previously does not admit a candidate"), CanStartCandidate(false, false));
	// Status.ParryActive is deliberately not an input: a stale mirrored tag cannot override the native timer.
	TestFalse(TEXT("Status.ParryActive true with the native window closed still rejects"), CanStartCandidate(false, false));
	TestFalse(TEXT("dodge invulnerability rejects a candidate"), CanStartCandidate(true, true));

	TestTrue(TEXT("confirmation waits until 0.1 seconds"),
		EvaluateCandidate(true, 100.0, 100.0, 0.099) == ECandidateDecision::Pending);
	TestTrue(TEXT("no health loss confirms at the boundary"),
		EvaluateCandidate(true, 100.0, 100.0, 0.1) == ECandidateDecision::Confirmed);
	TestTrue(TEXT("health gain does not count as health loss"),
		EvaluateCandidate(true, 90.0, 95.0, 0.11) == ECandidateDecision::Confirmed);
	TestTrue(TEXT("any health loss rejects the candidate"),
		EvaluateCandidate(true, 100.0, 99.0, 0.11) == ECandidateDecision::Rejected);
	TestTrue(TEXT("unknown health fails closed"),
		EvaluateCandidate(false, 100.0, 100.0, 0.11) == ECandidateDecision::Rejected);
	TestTrue(TEXT("non-finite health fails closed"),
		EvaluateCandidate(true, 100.0, std::numeric_limits<double>::quiet_NaN(), 0.11) == ECandidateDecision::Rejected);
	TestTrue(TEXT("non-finite observation time fails closed"),
		EvaluateCandidate(true, 100.0, 100.0, std::numeric_limits<double>::quiet_NaN()) == ECandidateDecision::Rejected);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPackParryPostureDefaultTest,
	"OneBossFight.Player.PackParry.PostureDefaultIsInert",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FRPGPackParryPostureDefaultTest::RunTest(const FString& Parameters)
{
	const URPGBossPosture* Posture = NewObject<URPGBossPosture>();
	TestNotNull(TEXT("posture component can be constructed"), Posture);
	if (Posture)
	{
		TestEqual(TEXT("owner-configured parry posture damage defaults to zero"), Posture->ParryPostureDamage, 0.f);
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPackParryAttackKeyTest,
	"OneBossFight.Player.PackParry.AttackIdentityAndDeduplication",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FRPGPackParryAttackKeyTest::RunTest(const FString& Parameters)
{
	using namespace RPGPackParry;
	const FString Tracked = BuildAttackKey(3, 42, TEXT("A1b"), 18, TEXT("Ignored"), 12.3);
	TestFalse(TEXT("tracked instance has a stable key"), Tracked.IsEmpty());
	TestEqual(TEXT("tracked identity ignores trace-window montage positions"),
		Tracked, BuildAttackKey(3, 42, TEXT("A1b"), 18, TEXT("Other"), 40.0));
	TestFalse(TEXT("a different tracked instance has a distinct key"),
		Tracked == BuildAttackKey(3, 42, TEXT("A1b"), 19, TEXT("Ignored"), 12.3));

	const FString UntrackedA = BuildAttackKey(3, 42, NAME_None, 0, TEXT("Mid01_Anim_Montage"), 12.341);
	const FString UntrackedB = BuildAttackKey(3, 42, NAME_None, 0, TEXT("Mid01_Anim_Montage"), 12.344);
	TestFalse(TEXT("untracked montage has a stable fallback key"), UntrackedA.IsEmpty());
	TestEqual(TEXT("untracked playback start is rounded to centiseconds"), UntrackedA, UntrackedB);
	TestFalse(TEXT("distinct untracked playback start has a distinct key"),
		UntrackedA == BuildAttackKey(3, 42, NAME_None, 0, TEXT("Mid01_Anim_Montage"), 12.35));
	TestTrue(TEXT("unresolved untracked identity fails closed"),
		BuildAttackKey(3, 42, NAME_None, 0, NAME_None, std::numeric_limits<double>::quiet_NaN()).IsEmpty());

	FRewardDeduplicator Deduplicator;
	TestTrue(TEXT("first trace window is accepted"), Deduplicator.TryAccept(3, Tracked));
	TestFalse(TEXT("another trace window of the same attack is deduplicated"), Deduplicator.TryAccept(3, Tracked));
	TestTrue(TEXT("new attack instance is accepted"), Deduplicator.TryAccept(3, BuildAttackKey(3, 42, TEXT("A1b"), 19, NAME_None, 0.0)));
	TestTrue(TEXT("new encounter generation may reuse an attack number"), Deduplicator.TryAccept(4, Tracked));
	TestFalse(TEXT("empty key never creates a reward"), Deduplicator.TryAccept(4, FString()));
	return true;
}
