// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGStartupChronology.h"
#if WITH_DEV_AUTOMATION_TESTS
#include "Components/ActorComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Pawn.h"
#include "HAL/PlatformTime.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Player/RPGCombatCatalog.h"
#include "Player/RPGEncounterBinding.h"
#include "Player/RPGPlayerMovesSubsystem.h"
DEFINE_LOG_CATEGORY_STATIC(LogRPGStartupChronology, Log, All);
namespace
{
    uint64 Sequence = 0; // diagnostic-only state; all calls are game thread
    TSet<TWeakObjectPtr<AActor>> FirstObserved;
    bool Enabled() { return IsInGameThread() && FParse::Param(FCommandLine::Get(), TEXT("DD30Chronology")); }
    const TCHAR* Role(AActor* Actor)
    {
        return URPGPlayerMovesSubsystem::IsPackBoss(Actor) ? TEXT("Boss") :
            URPGPlayerMovesSubsystem::IsPackPlayer(Actor) ? TEXT("Player") : TEXT("OtherPawn");
    }
    void Inputs(UWorld& World, const TCHAR* Phase)
    {
        UGameInstance* GI = World.GetGameInstance();
        const auto* Catalog = GI ? GI->GetSubsystem<URPGCombatCatalogSubsystem>() : nullptr;
        // Read the EXISTING GI publication, never ForWorld/Legacy/create/publish a fallback.
        const auto Epoch = Catalog ? Catalog->GetEpoch() : TSharedPtr<const RPGCombatRegistry::FEpoch>();
        const auto* Context = World.GetSubsystem<URPGCombatContextSubsystem>();
        int32 Bindings = 0;
        for (TActorIterator<ARPGEncounterBinding> It(&World); It; ++It)
        {
            ++Bindings;
            UE_LOG(LogRPGStartupChronology, Display, TEXT("[DD30_CHRONO] binding phase=%s world=%s actor=%s encounter=%s members=%d"),
                Phase, *World.GetPathName(), *It->GetPathName(), *It->EncounterInstance.ToString(), It->Participants.Num());
            for (const FRPGPlacedParticipantBinding& P : It->Participants)
            {
                UE_LOG(LogRPGStartupChronology, Display, TEXT("[DD30_CHRONO] binding_member slot=%s target=%s actor=%s definition=%s"),
                    *P.Slot.ToString(), *P.TargetSlot.ToString(), *GetPathNameSafe(P.Actor.Get()), *GetPathNameSafe(P.Definition.Get()));
            }
        }
        UE_LOG(LogRPGStartupChronology, Display, TEXT("[DD30_CHRONO] inputs phase=%s world=%s gi=%d catalog=%d epoch_valid=%d epoch=%s bindings=%d context=%d bound=%d ready=%d selection_store=NOT_DEFINED"),
            Phase, *World.GetPathName(), GI != nullptr, Catalog != nullptr, Epoch.IsValid() && Epoch->Id.IsValid(),
            Epoch.IsValid() ? *Epoch->Id.ToString() : TEXT("NONE"), Bindings, Context != nullptr,
            Context ? Context->GetBoundCount() : -1, Context ? Context->GetReadyCount() : -1);
    }
    void ActorLine(UWorld& World, AActor& Actor, const TCHAR* Phase, const TCHAR* Route)
    {
        UE_LOG(LogRPGStartupChronology, Display, TEXT("[DD30_CHRONO] actor seq=%llu seconds=%.9f phase=%s route=%s world=%s world_begun=%d actor=%s class=%s role=%s actor_begun=%d actor_beginning=%d"),
            static_cast<unsigned long long>(++Sequence), FPlatformTime::Seconds(), Phase, Route,
            *World.GetPathName(), World.HasBegunPlay(), *Actor.GetPathName(), *Actor.GetClass()->GetPathName(), Role(&Actor),
            Actor.HasActorBegunPlay(), Actor.IsActorBeginningPlay());
    }
}
#endif
void RPGStartupChronology::AtWorldBeginPlay(UWorld& World)
{
#if WITH_DEV_AUTOMATION_TESTS
    if (!Enabled()) return;
    UE_LOG(LogRPGStartupChronology, Display, TEXT("[DD30_CHRONO] callback=PlayerMoves.OnWorldBeginPlay world=%s world_begun=%d"), *World.GetPathName(), World.HasBegunPlay());
    int32 Bosses = 0, Players = 0, Pawns = 0;
    for (TActorIterator<APawn> It(&World); It; ++It)
    {
        ++Pawns; Bosses += URPGPlayerMovesSubsystem::IsPackBoss(*It) ? 1 : 0;
        Players += URPGPlayerMovesSubsystem::IsPackPlayer(*It) ? 1 : 0;
        ActorLine(World, **It, TEXT("OnWorldBeginPlay"), TEXT("subsystem-entry-before-Attach"));
    }
    UE_LOG(LogRPGStartupChronology, Display, TEXT("[DD30_CHRONO] census pawns=%d bosses=%d players=%d"), Pawns, Bosses, Players);
    Inputs(World, TEXT("OnWorldBeginPlay"));
#endif
}
void RPGStartupChronology::AtComponentBeginPlay(UActorComponent& Component)
{
#if WITH_DEV_AUTOMATION_TESTS
    if (!Enabled()) return;
    AActor* Actor = Component.GetOwner(); UWorld* World = Component.GetWorld();
    if (!Actor || !World || (!URPGPlayerMovesSubsystem::IsPackBoss(Actor) && !URPGPlayerMovesSubsystem::IsPackPlayer(Actor))) return;
    const TWeakObjectPtr<AActor> Key(Actor);
    if (FirstObserved.Contains(Key)) return;
    FirstObserved.Add(Key);
    const TCHAR* Route = Actor->IsActorBeginningPlay() ? TEXT("inside-actor-BeginPlay-route") :
        Actor->HasActorBegunPlay() ? TEXT("LATE-component-attachment-not-first-actor-BeginPlay") : TEXT("unexpected-owner-not-beginning");
    ActorLine(*World, *Actor, TEXT("FirstObservedComponentBeginPlay"), Route);
    UE_LOG(LogRPGStartupChronology, Display, TEXT("[DD30_CHRONO] witness_component=%s before_component_SuperBeginPlay=1"), *Component.GetPathName());
    Inputs(*World, TEXT("FirstObservedComponentBeginPlay"));
#endif
}
