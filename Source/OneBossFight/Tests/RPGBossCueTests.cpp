// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossCueRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossCueRules,"OneBossFight.Framework.Cue.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossCueRules::RunTest(const FString&)
{
    // BOSS-ANM-003 / PAC-004 / QA-007: the accessibility channels, the bounded seeded hold, and the distinct-channels rule.
    using namespace RPGBossCue;
    TestTrue(TEXT("mode 0: both channels at full size"),ChannelsFor(0).bVisual&&ChannelsFor(0).bAudio&&ChannelsFor(0).VisualScale==1.f);
    TestTrue(TEXT("mode 1: visual only"),ChannelsFor(1).bVisual&&!ChannelsFor(1).bAudio);
    TestTrue(TEXT("mode 2: audio only"),!ChannelsFor(2).bVisual&&ChannelsFor(2).bAudio);
    TestTrue(TEXT("mode 3: both, the visual at half size"),ChannelsFor(3).bVisual&&ChannelsFor(3).bAudio&&ChannelsFor(3).VisualScale==.5f);
    TestTrue(TEXT("a mode that does not exist is mode 0"),ChannelsFor(-7).bVisual&&ChannelsFor(99).bAudio);
    for (int32 I=0;I<64;++I)
    {
        const double H=HoldSeconds(.4f,.9f,7,I);
        if (!(H>=.4&&H<=.9)) AddError(FString::Printf(TEXT("hold %d outside [0.4, 0.9]: %g"),I,H));
    }
    TestTrue(TEXT("the hold is repeatable for the same seed and index"),HoldSeconds(.4f,.9f,7,3)==HoldSeconds(.4f,.9f,7,3));
    bool bVaries=false; for (int32 I=1;I<16;++I) bVaries=bVaries||HoldSeconds(.4f,.9f,7,I)!=HoldSeconds(.4f,.9f,7,0);
    TestTrue(TEXT("the hold varies from attack to attack"),bVaries);
    {   // The holds of neighbouring attacks are not a trend: over 64 attacks they cover most of the window and their mean sits near its middle.
        double Lo=1.e9,Hi=-1.e9,Sum=0.;for(int32 I=0;I<64;++I){const double H=HoldSeconds(.4f,.9f,11,I);Lo=FMath::Min(Lo,H);Hi=FMath::Max(Hi,H);Sum+=H;}
        TestTrue(TEXT("64 holds spread over at least 0.3 s of the 0.5 s window"),Hi-Lo>=.3);
        TestTrue(TEXT("their mean is near the middle of the window (0.55 to 0.75)"),Sum/64.>=.55&&Sum/64.<=.75);
        int32 Rising=0;for(int32 I=1;I<64;++I)Rising+=HoldSeconds(.4f,.9f,11,I)>HoldSeconds(.4f,.9f,11,I-1)?1:0;
        TestTrue(TEXT("neither always rising nor always falling"),Rising>10&&Rising<54);
    }
    TestTrue(TEXT("min = max is a fixed hold"),HoldSeconds(.5f,.5f,1,4)==.5);
    TestTrue(TEXT("invalid windows are -1"),HoldSeconds(0.f,.9f,1,0)==-1.&&HoldSeconds(.9f,.4f,1,0)==-1.&&HoldSeconds(.4f,3.5f,1,0)==-1.&&HoldSeconds(std::numeric_limits<float>::quiet_NaN(),.9f,1,0)==-1.);
    FCueKey A; A.Id=TEXT("Release"); A.Visual=1; A.Sound=TEXT("/Game/OneBossFight/Audio/CueA");
    FCueKey B; B.Id=TEXT("Recovery"); B.Visual=2; B.Sound=TEXT("/Game/OneBossFight/Audio/CueB");
    TestTrue(TEXT("two cues that differ in id, visual and sound are distinct"),DistinctChannels({A,B}));
    FCueKey SameVisual=B; SameVisual.Visual=A.Visual; TestFalse(TEXT("the same visual: the picture alone could not tell them apart"),DistinctChannels({A,SameVisual}));
    FCueKey SameSound=B; SameSound.Sound=A.Sound; TestFalse(TEXT("the same sound: the audio alone could not tell them apart"),DistinctChannels({A,SameSound}));
    FCueKey SameId=B; SameId.Id=A.Id; TestFalse(TEXT("the same id"),DistinctChannels({A,SameId}));
    TestTrue(TEXT("one cue or none is trivially distinct"),DistinctChannels({A})&&DistinctChannels({}));
    return true;
}
#endif
