// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Player/RPGBossCloseClipSwapRules.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGBossCloseClipSwapRulesTest, "OneBossFight.Boss.CloseClipSwapRules",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGBossCloseClipSwapRulesTest::RunTest(const FString& Parameters)
{
	using namespace RPGBossCloseClipSwapRules;
	struct FMapping { const TCHAR* Pack; const TCHAR* Replacement; bool bPackClose; };
	const FMapping Cases[] = {
		{TEXT("GS_Attack01_Montage"), TEXT("AM_Boss01_A3a"), true},
		{TEXT("GS_Attack02_Montage"), TEXT("AM_Boss01_A3b"), true},
		{TEXT("GS_Attack03_Montage"), TEXT("AM_Boss01_A1"), true},
		{TEXT("GS_Attack04_Montage"), TEXT(""), true},
		{TEXT("GS_LeapAttack_Montage"), TEXT(""), false},
		{TEXT(""), TEXT(""), false},
	};
	for (const FMapping& Case : Cases)
	{
		const FName Pack(Case.Pack);
		TestEqual(*FString::Printf(TEXT("%s replacement table row"), Case.Pack), ReplacementFor(Pack), FName(Case.Replacement));
		TestEqual(*FString::Printf(TEXT("%s close montage membership"), Case.Pack), IsPackCloseMontage(Pack), Case.bPackClose);
	}
	return true;
}

#endif
