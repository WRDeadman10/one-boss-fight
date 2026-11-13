// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "EngineUtils.h"
#include "Engine/World.h"
#include "GameplayTagContainer.h"
#include "TimerManager.h"
#include "Pack/RPGBlueprintCall.h"
#include "Player/RPGEncounterBinding.h"

/** Teardown retry owner for pack tags on actors that outlive a component. */
namespace RPGOwnedTagCleanup
{
    /** Resolve the live binding generation for an actor. Zero is the legacy/unbound route; ambiguity fails closed. */
    inline uint64 CurrentGeneration(const AActor* Owner)
    {
        UWorld* World = Owner ? Owner->GetWorld() : nullptr;
        if (!World) return 0;
        uint64 Generation = 0;
        bool bFoundOwner = false;
        for (TActorIterator<ARPGEncounterBinding> It(World); It; ++It)
        {
            for (const FRPGPlacedParticipantBinding& Participant : It->Participants)
            {
                if (Participant.Actor.Get() != Owner) continue;
                if (bFoundOwner) return MAX_uint64;
                bFoundOwner = true;
                Generation = It->ParticipantGeneration;
            }
        }
        return Generation;
    }

    inline bool MayRemoveForGeneration(const AActor* CapturedOwner, const AActor* CurrentOwner,
        uint64 ExpectedGeneration, uint64 CurrentOwnerGeneration)
    {
        return IsValid(CapturedOwner) && CapturedOwner == CurrentOwner
            && ExpectedGeneration == CurrentOwnerGeneration;
    }

    /** A failed reflected removal keeps a retry owner while its actor remains alive. */
    constexpr bool ShouldRetry(bool bOwnerAlive, bool bRemovalCallSucceeded) noexcept
    {
        return bOwnerAlive && !bRemovalCallSucceeded;
    }

    /** Exponential retry delay with both the first attempt and long-lived retries bounded. */
    constexpr float RetryDelaySeconds(int32 Attempt) noexcept
    {
        const int32 Exponent = Attempt <= 1 ? 0 : (Attempt >= 5 ? 4 : Attempt - 1);
        return 0.25f * float(1 << Exponent);
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

    inline void RetryUntilRemovalIssued(TWeakObjectPtr<AActor> WeakOwner, FGameplayTag Tag, FName Source,
        uint64 ExpectedGeneration, int32 Attempt = 1)
    {
        AActor* Owner = WeakOwner.Get();
        if (!Owner || Owner->IsActorBeingDestroyed())
        {
            return;
        }

        const uint64 Current = CurrentGeneration(Owner);
        if (!MayRemoveForGeneration(Owner, Owner, ExpectedGeneration, Current))
        {
            UE_LOG(LogTemp, Display, TEXT("[OwnedTagCleanup] cancelled_stale source=%s tag=%s expectedGeneration=%llu currentGeneration=%llu"),
                *Source.ToString(), *Tag.ToString(), static_cast<unsigned long long>(ExpectedGeneration),
                static_cast<unsigned long long>(Current));
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
        const float RetryDelay = RetryDelaySeconds(Attempt);
        World->GetTimerManager().SetTimer(RetryHandle,
            FTimerDelegate::CreateLambda([WeakOwner, Tag, Source, ExpectedGeneration, Attempt]()
            {
                RetryUntilRemovalIssued(WeakOwner, Tag, Source, ExpectedGeneration, Attempt + 1);
            }),
            RetryDelay, false);
    }

    /** Call only after this component's own immediate removal call failed. */
    inline void ScheduleAfterRemovalFailure(AActor* Owner, const TCHAR* TagName, const TCHAR* Source, uint64 ExpectedGeneration)
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
        RetryUntilRemovalIssued(Owner, Tag, FName(Source), ExpectedGeneration);
    }
}
