// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossLeashRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossArenaLeashInsideRadius,
    "OneBossFight.Framework.ArenaLeash.InsideRadius",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossArenaLeashInsideRadius::RunTest(const FString&)
{
    TestFalse(TEXT("249 cm planar distance is inside a 250 cm arena"),RPGBossLeashRules::IsOutsideArena(FVector(249.f,0.f,0.f),FVector::ZeroVector,250.));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossArenaLeashExactRadius,
    "OneBossFight.Framework.ArenaLeash.ExactRadius",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossArenaLeashExactRadius::RunTest(const FString&)
{
    TestFalse(TEXT("exactly 250 cm remains inside because the comparison is strict"),RPGBossLeashRules::IsOutsideArena(FVector(250.f,0.f,0.f),FVector::ZeroVector,250.));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossArenaLeashOneCentimeterOutside,
    "OneBossFight.Framework.ArenaLeash.OneCentimeterOutside",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossArenaLeashOneCentimeterOutside::RunTest(const FString&)
{
    TestTrue(TEXT("251 cm planar distance is outside a 250 cm arena"),RPGBossLeashRules::IsOutsideArena(FVector(251.f,0.f,0.f),FVector::ZeroVector,250.));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossArenaLeashUsesPlanarDistance,
    "OneBossFight.Framework.ArenaLeash.PlanarDistance",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossArenaLeashUsesPlanarDistance::RunTest(const FString&)
{
    TestFalse(TEXT("vertical offset does not change an exact-radius planar classification"),RPGBossLeashRules::IsOutsideArena(FVector(250.f,0.f,10000.f),FVector(0.f,0.f,-10000.f),250.));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossArenaLeashInvalidAndDisabledRadius,
    "OneBossFight.Framework.ArenaLeash.InvalidAndDisabledRadius",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossArenaLeashInvalidAndDisabledRadius::RunTest(const FString&)
{
    TestTrue(TEXT("nonfinite position fails closed"),RPGBossLeashRules::IsOutsideArena(FVector(std::numeric_limits<double>::infinity(),0.,0.),FVector::ZeroVector,250.));
    TestFalse(TEXT("zero radius disables the leash for finite coordinates"),RPGBossLeashRules::IsOutsideArena(FVector(1000000.f,0.f,0.f),FVector::ZeroVector,0.));
    return true;
}
#endif
