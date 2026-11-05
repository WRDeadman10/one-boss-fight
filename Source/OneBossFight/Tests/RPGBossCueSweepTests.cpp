// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossCueRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossCueSweep,"OneBossFight.Framework.Cue.Sweep",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossCueSweep::RunTest(const FString&)
{
    using namespace RPGBossCue;
    for (int32 Seed=-5000;Seed<5000;++Seed)
    {
        const double Hold=HoldSeconds(.15f,2.75f,Seed,Seed*17);
        if (!(FMath::IsFinite(Hold)&&Hold>=.15&&Hold<=2.75))
        {
            AddError(FString::Printf(TEXT("hold out of range for seed %d: %g"),Seed,Hold));
        }
    }
    FCueKey A; A.Id=TEXT("A"); A.Visual=1; A.Sound=TEXT("SoundA");
    FCueKey B; B.Id=TEXT("B"); B.Visual=2; B.Sound=TEXT("SoundB");
    const TArray<FCueKey> Forward{A,B}, Reverse{B,A};
    TestTrue(TEXT("distinct channel result is symmetric under cue order"),DistinctChannels(Forward)==DistinctChannels(Reverse));
    TestTrue(TEXT("distinct pair passes"),DistinctChannels(Forward));
    B.Visual=A.Visual;
    TestFalse(TEXT("visual collision fails in either order"),DistinctChannels({A,B})||DistinctChannels({B,A}));
    B.Visual=2; B.Sound=A.Sound;
    TestFalse(TEXT("sound collision fails in either order"),DistinctChannels({A,B})||DistinctChannels({B,A}));
    B.Sound=TEXT("SoundB"); B.Id=A.Id;
    TestFalse(TEXT("duplicate ids fail in either order"),DistinctChannels({A,B})||DistinctChannels({B,A}));
    return true;
}
#endif
