// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Engine/World.h"
#include "GameplayTagContainer.h"
#include "TimerManager.h"
#include "Pack/RPGBlueprintCall.h"

/** Teardown retry owner for pack tags on actors that outlive a component. */
namespace RPGOwnedTagCleanup
{
    /** A failed reflected removal keeps a retry owner while its actor remains alive. */
    constexpr bool ShouldRetry(bool bOwnerAlive, bool bRemovalCallSucceeded) noexcept
    {
        return bOwnerAlive && !bRemovalCallSucceeded;
    }

    inline bool RemoveOwnedTag(AActor* Owner, const FGameplayTag& Tag)
    {
        return RPGPack::CallBlueprintFunction(Owner, TEXT("RemoveOwnedGameplayTag"),
            [&Tag](UFunction& Function, uint8* Params)
            {
                RPGPack::SetTag(Function, Params, TEXT("TagToRemove"), Tag);
            },
            [](UFunction&, uint8*) {});
    }

    inline void RetryUntilRemovalIssued(TWeakObjectPtr<AActor> WeakOwner, FGameplayTag Tag, FName Source, int32 Attempt = 1)
    {
        AActor* Owner = WeakOwner.Get();
        if (!Owner || Owner->IsActorBeingDestroyed())
        {
            return;
        }

        const bool bCalled = RemoveOwnedTag(Owner, Tag);
        if (!ShouldRetry(true, bCalled))
        {
            UE_LOG(LogTemp, Display, TEXT("[OwnedTagCleanup] removal_issued source=%s tag=%s attempt=%d"), *Source.ToString(), *Tag.ToString(), Attempt);
            return;
        }
        UE_LOG(LogTemp, Warning, TEXT("[OwnedTagCleanup] retry source=%s tag=%s attempt=%d removeCall=%d"),
            *Source.ToString(), *Tag.ToString(), Attempt, bCalled ? 1 : 0);

        UWorld* World = Owner->GetWorld();
        if (!World)
        {
            return;
        }
        FTimerHandle RetryHandle;
        const float RetryDelay = FMath::Min(0.25f * float(1 << FMath::Min(Attempt - 1, 4)), 4.0f);
        World->GetTimerManager().SetTimer(RetryHandle,
            FTimerDelegate::CreateLambda([WeakOwner, Tag, Source, Attempt]()
            {
                RetryUntilRemovalIssued(WeakOwner, Tag, Source, Attempt + 1);
            }),
            RetryDelay, false);
    }

    /** Call only after this component's own immediate removal call failed. */
    inline void ScheduleAfterRemovalFailure(AActor* Owner, const TCHAR* TagName, const TCHAR* Source)
    {
        if (!Owner || Owner->IsActorBeingDestroyed())
        {
            return;
        }
        const FGameplayTag Tag = FGameplayTag::RequestGameplayTag(FName(TagName), false);
        if (!Tag.IsValid())
        {
            return;
        }
        UE_LOG(LogTemp, Warning, TEXT("[OwnedTagCleanup] scheduled source=%s tag=%s"), Source, *Tag.ToString());
        RetryUntilRemovalIssued(Owner, Tag, FName(Source));
    }
}
