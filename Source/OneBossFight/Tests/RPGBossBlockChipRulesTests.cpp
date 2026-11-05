// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossBlockChipRules.h"
#include "Player/RPGBossGuardRules.h"
#include "Player/RPGDamageResolver.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossBlockChipRules,"OneBossFight.Framework.BlockChip.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossBlockChipRules::RunTest(const FString&)
{
    using namespace RPGBossBlockChip;
    for (int32 I=0;I<=100;++I)
    {
        const double Fraction=double(I)/100.;
        const double Damage=GuardedDamage(123.4,Fraction);
        TestTrue(TEXT("chip damage remains within [0,incoming]"),FMath::IsFinite(Damage)&&Damage>=0.&&Damage<=123.4);
        if (I>0) TestTrue(TEXT("chip damage is monotonic in fraction"),Damage+1.e-9>=GuardedDamage(123.4,double(I-1)/100.));
    }
    TestTrue(TEXT("invalid amount or fraction fails closed"),GuardedDamage(-1.,.2)==0.&&GuardedDamage(10.,1.1)==0.&&GuardedDamage(std::numeric_limits<double>::quiet_NaN(),.2)==0.);
    for(int32 I=0;I<=100;++I)
    {
        const double Incoming=double(I)*10.;const double Zero=GuardedDamage(Incoming,0.),Full=GuardedDamage(Incoming,1.);
        TestTrue(*FString::Printf(TEXT("damage endpoints %d"),I),Zero==0.&&FMath::IsNearlyEqual(Full,Incoming));
        TestEqual(*FString::Printf(TEXT("zero chip never changes for any incoming value %d"),I),GuardedDamage(Incoming,.0),0.);
    }
    TestEqual(TEXT("infinite damage fails closed"),GuardedDamage(std::numeric_limits<double>::infinity(),.5),0.);
    TestEqual(TEXT("NaN fraction fails closed"),GuardedDamage(10.,std::numeric_limits<double>::quiet_NaN()),0.);
    // HIT-008 integration contract: guard scales the payload before the resolver decides the contact;
    // ordinary blocking remains Accepted with chip, while parry and dodge still suppress HP application.
    {
        constexpr double Incoming=80.,Chip=.25;
        const double BlockedPayload=GuardedDamage(Incoming,Chip);
        TestEqual(TEXT("blocking scales payload before resolver input"),BlockedPayload,20.);
        TestTrue(TEXT("blocking classification remains Guarded"),RPGBossGuard::Classify(true,false)==RPGBossGuard::EGuardState::Guarded);
        TestTrue(TEXT("chip damage does not invent a resolver Guarded outcome"),RPGDamageRules::Decide(true,true,true,false,false,false)==ERPGDamageOutcome::Accepted);
        TestEqual(TEXT("accepted blocked contact retains scaled nonzero damage"),BlockedPayload,20.);
        TestTrue(TEXT("parry still suppresses scaled damage"),RPGDamageRules::Decide(true,true,true,false,false,true)==ERPGDamageOutcome::Parried);
        TestTrue(TEXT("dodge invulnerability precedes parry"),RPGDamageRules::Decide(true,true,true,false,true,true)==ERPGDamageOutcome::RejectedInvulnerable);
    }
    return true;
}
#endif
