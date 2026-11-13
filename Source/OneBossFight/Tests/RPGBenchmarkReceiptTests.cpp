// Copyright One Boss Fight. All Rights Reserved.
// BQ-21 (Queue BQ batch 5; D4): pins the session classification used in the summary.json run_identity block. The live summary output
// (run id, UTC time, build version, host fingerprint) stays ENG: it needs a benchmark run. Written, not compiled/run.
#include "Benchmark/RPGBenchmarkRunner.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBenchmarkReceiptSessionTest, "OneBossFight.Benchmark.ReceiptSessionType", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBenchmarkReceiptSessionTest::RunTest(const FString&)
{
	using RPGBenchmarkReceipt::ClassifySession;
	TestEqual(TEXT("local console session"), ClassifySession(TEXT("Console")), FString(TEXT("console")));
	TestEqual(TEXT("case and spaces ignored"), ClassifySession(TEXT("  console ")), FString(TEXT("console")));
	TestEqual(TEXT("remote desktop session"), ClassifySession(TEXT("RDP-Tcp#3")), FString(TEXT("remote")));
	TestEqual(TEXT("unset: unknown, never console"), ClassifySession(FString()), FString(TEXT("unknown")));
	TestEqual(TEXT("other value: unknown"), ClassifySession(TEXT("ICA-tcp#0")), FString(TEXT("unknown")));
	return true;
}
#endif
