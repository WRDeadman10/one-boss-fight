// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"
#include "Pack/RPGOwnedTagCleanup.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGOwnedTagCleanupRetryPolicyTest,
	"OneBossFight.Player.OwnedTagCleanup.RetryPolicy",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FRPGOwnedTagCleanupRetryPolicyTest::RunTest(const FString&)
{
	TestTrue(TEXT("a live owner with a failed reflected removal keeps a retry owner"), RPGOwnedTagCleanup::ShouldRetry(true, false));
	TestFalse(TEXT("stop after the removal call succeeds"), RPGOwnedTagCleanup::ShouldRetry(true, true));
	TestFalse(TEXT("stop when the owner is gone"), RPGOwnedTagCleanup::ShouldRetry(false, false));
	TestFalse(TEXT("no work for a dead owner without the tag"), RPGOwnedTagCleanup::ShouldRetry(false, false));
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
