// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"
#include "Pack/RPGOwnedTagCleanup.h"
#include "GameFramework/Actor.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/Package.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGOwnedTagCleanupRetryPolicyTest,
	"OneBossFight.Player.OwnedTagCleanup.RetryPolicy",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FRPGOwnedTagCleanupRetryPolicyTest::RunTest(const FString&)
{
	TestTrue(TEXT("a live owner with a failed reflected removal keeps a retry owner"), RPGOwnedTagCleanup::ShouldRetry(true, false));
	TestFalse(TEXT("stop after the removal call succeeds"), RPGOwnedTagCleanup::ShouldRetry(true, true));
	TestFalse(TEXT("stop when the owner is gone"), RPGOwnedTagCleanup::ShouldRetry(false, false));
	TestFalse(TEXT("no work for a dead owner without the tag"), RPGOwnedTagCleanup::ShouldRetry(false, false));
	for (const TPair<int32, float>& Case : {TPair<int32, float>(-10, .25f), {1, .25f}, {2, .5f}, {3, 1.f}, {4, 2.f}, {5, 4.f}, {6, 4.f}, {10000, 4.f}})
	{
		TestEqual(FString::Printf(TEXT("retry delay is bounded for attempt %d"), Case.Key), RPGOwnedTagCleanup::RetryDelaySeconds(Case.Key), Case.Value);
	}
	int32 Attempts = 0;
	bool bRemovalSucceeded = false;
	while (RPGOwnedTagCleanup::ShouldRetry(true, bRemovalSucceeded) && Attempts < 3)
	{
		++Attempts;
		if (Attempts == 3)
		{
			bRemovalSucceeded = true;
		}
	}
	TestEqual(TEXT("a transient failure retains the retry owner until a later successful removal"), Attempts, 3);
	return true;
}


// BQ-03 (Queue BQ batch 1; BF-X23/X24 retry-on-reused-actor race): the delayed cleanup only removes the tag when the captured owner is
// still the same live actor AND its binding generation is unchanged, so a retry scheduled for an old encounter cannot strip the tag a new
// encounter re-added on a reused live actor. RPGOwnedTagCleanup::MayRemoveForGeneration had no regression test. Written, not compiled/run.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGOwnedTagCleanupGenerationFenceTest,
	"OneBossFight.Player.OwnedTagCleanup.GenerationFence",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FRPGOwnedTagCleanupGenerationFenceTest::RunTest(const FString&)
{
	TStrongObjectPtr<AActor> Reused(NewObject<AActor>(GetTransientPackage(), TEXT("BQ03ReusedOwner")));
	TStrongObjectPtr<AActor> Other(NewObject<AActor>(GetTransientPackage(), TEXT("BQ03OtherOwner")));
	if (!TestTrue(TEXT("fixture actors exist"), Reused.IsValid() && Other.IsValid()))
	{
		return false;
	}
	using RPGOwnedTagCleanup::MayRemoveForGeneration;
	TestTrue(TEXT("same live owner, same generation: the retry may remove"), MayRemoveForGeneration(Reused.Get(), Reused.Get(), 7, 7));
	TestFalse(TEXT("reused live owner, newer generation: the stale retry is cancelled"), MayRemoveForGeneration(Reused.Get(), Reused.Get(), 7, 8));
	TestFalse(TEXT("generation went backwards: cancelled"), MayRemoveForGeneration(Reused.Get(), Reused.Get(), 8, 7));
	TestFalse(TEXT("a different current owner: cancelled"), MayRemoveForGeneration(Reused.Get(), Other.Get(), 7, 7));
	TestFalse(TEXT("null captured owner: cancelled"), MayRemoveForGeneration(nullptr, Reused.Get(), 7, 7));
	TestFalse(TEXT("ambiguous binding (MAX_uint64 from CurrentGeneration): cancelled"), MayRemoveForGeneration(Reused.Get(), Reused.Get(), 7, MAX_uint64));
	TestTrue(TEXT("legacy/unbound route (generation 0 both times): unchanged behaviour"), MayRemoveForGeneration(Reused.Get(), Reused.Get(), 0, 0));
	TestFalse(TEXT("unbound when captured, bound now: cancelled"), MayRemoveForGeneration(Reused.Get(), Reused.Get(), 0, 3));
	return true;
}
