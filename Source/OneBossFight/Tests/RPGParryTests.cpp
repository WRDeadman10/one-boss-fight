// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGParryRules.h"
#include "Player/RPGDamageResolver.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FPlayerParryRules,"OneBossFight.Framework.Parry.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FPlayerParryRules::RunTest(const FString&)
{
    // The parry window of the player: a press opens it, the cooldown stops spam, a contact outside it is not parried.
    using namespace RPGParry;
    FState S;
    TestFalse(TEXT("nothing is open before any press"),IsOpen(S,0.,.25));
    TestTrue(TEXT("the first press opens a window"),Press(S,10.,.25,.7));
    TestTrue(TEXT("the opening instant is inside"),IsOpen(S,10.,.25));
    TestTrue(TEXT("inside the window"),IsOpen(S,10.2,.25));
    TestFalse(TEXT("the closing instant is outside"),IsOpen(S,10.25,.25));
    TestFalse(TEXT("after the window"),IsOpen(S,10.5,.25));
    TestFalse(TEXT("a contact before the press is not parried"),IsOpen(S,9.99,.25));
    TestFalse(TEXT("a press in the cooldown does nothing"),Press(S,10.6,.25,.7));
    TestFalse(TEXT("and does not move the window"),IsOpen(S,10.65,.25));
    TestTrue(TEXT("a press when the cooldown is over opens again"),Press(S,10.7,.25,.7));
    TestTrue(TEXT("the new window is open"),IsOpen(S,10.8,.25));
    FState Short;
    TestTrue(TEXT("cooldown shorter than the window is raised to the window"),Press(Short,0.,.5,.1)&&!Press(Short,.4,.5,.1)&&Press(Short,.5,.5,.1));
    FState Bad;
    const double NaN=std::numeric_limits<double>::quiet_NaN();
    TestFalse(TEXT("bad numbers never open a window"),Press(Bad,NaN,.25,.7)||Press(Bad,1.,NaN,.7)||Press(Bad,1.,.25,NaN)||Press(Bad,1.,0.,.7)||Press(Bad,1.,-.1,.7));
    TestFalse(TEXT("bad numbers are never open"),IsOpen(S,NaN,.25)||IsOpen(S,10.1,NaN)||IsOpen(S,10.1,0.));
    // The decision order of one contact with the parry (HIT-008): dead / stale / duplicate / dodge i-frames all come BEFORE the parry; a parry beats a plain hit; no parry = the old answer.
    using RPGDamageRules::Decide;
    TestTrue(TEXT("alive, current, fresh, not invulnerable, parrying: Parried"),Decide(true,true,true,false,false,true)==ERPGDamageOutcome::Parried);
    TestTrue(TEXT("the dodge i-frames win over the parry"),Decide(true,true,true,false,true,true)==ERPGDamageOutcome::RejectedInvulnerable);
    TestTrue(TEXT("a duplicate swing is a duplicate, not a second parry"),Decide(true,true,true,true,false,true)==ERPGDamageOutcome::RejectedDuplicate);
    TestTrue(TEXT("a dead player is dead"),Decide(false,true,true,false,false,true)==ERPGDamageOutcome::RejectedDead);
    TestTrue(TEXT("a stale attacker is stale"),Decide(true,false,true,false,false,true)==ERPGDamageOutcome::RejectedStale&&Decide(true,true,false,false,false,true)==ERPGDamageOutcome::RejectedStale);
    TestTrue(TEXT("no parry: the old answers"),Decide(true,true,true,false,false)==ERPGDamageOutcome::Accepted&&Decide(true,true,true,false,true)==ERPGDamageOutcome::RejectedInvulnerable);
    TestTrue(TEXT("the outcome has a stable name"),FString(RPGDamageRules::Name(ERPGDamageOutcome::Parried))==TEXT("Parried"));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FPlayerParryPressSchedule,"OneBossFight.Framework.Parry.PressSchedule",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FPlayerParryPressSchedule::RunTest(const FString&)
{
    using namespace RPGParry;
    FState State;FRandomStream Random(0x89A11);double LastAccepted=-1.e9;int32 Accepted=0,Rejected=0;
    constexpr double Window=.25,Cooldown=.7;
    for(int32 Tick=0;Tick<10000;++Tick)
    {
        const double Now=double(Tick)*.01;
        if(Random.FRand()<.35f)
        {
            const double OldOpened=State.OpenedAt,OldReady=State.ReadyAt;
            const bool bOpened=Press(State,Now,Window,Cooldown);
            if(bOpened){++Accepted;TestTrue(TEXT("accepted presses respect cooldown"),Now>=LastAccepted+Cooldown-1.e-9);LastAccepted=Now;}
            else{++Rejected;TestEqual(TEXT("rejected press preserves open time"),State.OpenedAt,OldOpened);TestEqual(TEXT("rejected press preserves ready time"),State.ReadyAt,OldReady);}
        }
        TestEqual(TEXT("window membership matches half-open schedule"),IsOpen(State,Now,Window),Now>=State.OpenedAt&&Now<State.OpenedAt+Window);
        if(State.OpenedAt>-1.e8)TestTrue(TEXT("ready time is never before window end"),State.ReadyAt>=State.OpenedAt+Window);
    }
    TestTrue(TEXT("schedule includes accepted and cooldown-rejected presses"),Accepted>0&&Rejected>0);
    return true;
}
#endif
