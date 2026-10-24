// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Player/RPGBossCloseClipSwapRules.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGBossCloseClipSwapRulesTest, "OneBossFight.Boss.CloseClipSwapRules",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGBossCloseClipSwapRulesTest::RunTest(const FString& Parameters)
{
	using namespace RPGBossCloseClipSwapRules;
	TestEqual(TEXT("Attack03 maps to authored A1"), ReplacementFor(TEXT("GS_Attack03_Montage")), FName(TEXT("AM_Boss01_A1")));
	TestEqual(TEXT("Attack01 maps to authored A3a"), ReplacementFor(TEXT("GS_Attack01_Montage")), FName(TEXT("AM_Boss01_A3a")));
	TestEqual(TEXT("Attack02 maps to authored A3b"), ReplacementFor(TEXT("GS_Attack02_Montage")), FName(TEXT("AM_Boss01_A3b")));
	TestTrue(TEXT("Attack04 remains pack owned"), ReplacementFor(TEXT("GS_Attack04_Montage")).IsNone());
	for (const FName Name : { FName(TEXT("GS_Attack01_Montage")), FName(TEXT("GS_Attack02_Montage")), FName(TEXT("GS_Attack03_Montage")), FName(TEXT("GS_Attack04_Montage")) })
	{
		TestTrue(*FString::Printf(TEXT("%s is a validated pack close montage"), *Name.ToString()), IsPackCloseMontage(Name));
	}
	TestFalse(TEXT("an unrelated montage fails closed"), IsPackCloseMontage(TEXT("GS_LeapAttack_Montage")));
	TestTrue(TEXT("an unrelated montage has no replacement"), ReplacementFor(TEXT("GS_LeapAttack_Montage")).IsNone());
	return true;
}

#endif
