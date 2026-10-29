// Copyright One Boss Fight. All Rights Reserved.
#pragma once
class UWorld;
class UActorComponent;
namespace RPGStartupChronology
{
    void AtWorldBeginPlay(UWorld& World);
    void AtComponentBeginPlay(UActorComponent& Component);
}
