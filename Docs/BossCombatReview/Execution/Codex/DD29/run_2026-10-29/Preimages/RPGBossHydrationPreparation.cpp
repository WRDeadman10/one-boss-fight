// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossHydrationPreparation.h"
#include "Components/ActorComponent.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGPreparation, Log, All);

namespace
{
#if WITH_DEV_AUTOMATION_TESTS
	// Dev automation only: the ordinal of the injected failure (0 = none), the step counter of the current PrepareBatch call and whether the fault fired. Game thread only.
	int32 GFailAfterStep = 0;
	int32 GStepCount = 0;
	bool GFaultFired = false;
	bool GFaultScopeActive = false;
#endif

	/** Called after every real allocation and every real configure. In a production build it never fails. */
	bool InjectedFaultAfterStep(FString& OutError)
	{
#if WITH_DEV_AUTOMATION_TESTS
		++GStepCount;
		if (GFailAfterStep > 0 && GStepCount == GFailAfterStep)
		{
			GFaultFired = true;
			OutError = FString::Printf(TEXT("Preparation.InjectedFault: test-only injected failure after step %d (a real allocation or configure had completed)"), GStepCount);
			return true;
		}
#else
		(void)OutError;
#endif
		return false;
	}
}

/** The preparation algorithm. A friend of FRPGPreparedBatch so that the artifact has no public way to create or register a component. */
class FRPGBatchPreparer
{
public:
	static FRPGPreparationResult Run(const FRPGHydrationPreflightInput& Input);

private:
	/** The world, the encounter, the role and the weak actor of a member are still what the preflight validated. Never dereferences a stale pointer. */
	static bool CheckMember(const FRPGPreparedBatch& Batch, int32 MemberIndex, FString& OutError);
	/** The component at PlanIndex of a member is still the live, exact-class, correctly named, owned, unregistered and not begun component that was allocated. */
	static bool CheckComponent(const FRPGPreparedBatch& Batch, int32 MemberIndex, int32 PlanIndex, FString& OutError);
	static bool Allocate(FRPGPreparedBatch& Batch, FString& OutError);
	static bool Configure(FRPGPreparedBatch& Batch, FString& OutError);
};

bool FRPGBatchPreparer::CheckMember(const FRPGPreparedBatch& Batch, int32 MemberIndex, FString& OutError)
{
	const FRPGPreflightParticipantPlan& Participant = Batch.Plan->Participants[MemberIndex];
	const FString Slot = Participant.Slot.ToString();
	UWorld* World = Batch.Plan->World.Get();
	if (!World || !IsValid(World))
	{
		OutError = FString::Printf(TEXT("Preparation.MemberInvalid[slot=%s]: the world is no longer valid"), *Slot);
		return false;
	}
	if (!Batch.Plan->EncounterInstance.IsValid())
	{
		OutError = FString::Printf(TEXT("Preparation.MemberInvalid[slot=%s]: the encounter identity is not valid"), *Slot);
		return false;
	}
	if (Participant.Role != ERPGPreflightRole::BossCore)
	{
		OutError = FString::Printf(TEXT("Preparation.MemberInvalid[slot=%s]: only a boss-core member receives components"), *Slot);
		return false;
	}
	AActor* Actor = Participant.Actor.Get(); // null for a stale or garbage actor
	if (!Actor || !IsValid(Actor))
	{
		OutError = FString::Printf(TEXT("Preparation.MemberInvalid[slot=%s]: the actor is no longer valid"), *Slot);
		return false;
	}
	if (Actor->IsActorBeingDestroyed())
	{
		OutError = FString::Printf(TEXT("Preparation.MemberInvalid[slot=%s]: the actor is being destroyed"), *Slot);
		return false;
	}
	if (Actor->GetWorld() != World)
	{
		OutError = FString::Printf(TEXT("Preparation.MemberInvalid[slot=%s]: the actor is no longer in the expected world"), *Slot);
		return false;
	}
	if (Actor->HasActorBegunPlay() || Actor->IsActorBeginningPlay())
	{
		OutError = FString::Printf(TEXT("Preparation.MemberInvalid[slot=%s]: the actor began or is beginning play"), *Slot);
		return false;
	}
	return true;
}

bool FRPGBatchPreparer::CheckComponent(const FRPGPreparedBatch& Batch, int32 MemberIndex, int32 PlanIndex, FString& OutError)
{
	const FRPGPreflightParticipantPlan& Participant = Batch.Plan->Participants[MemberIndex];
	const FRPGComponentPlan& ComponentPlan = Participant.Plans[PlanIndex];
	const FString Label = FString::Printf(TEXT("[slot=%s][component=%s]"), *Participant.Slot.ToString(), *ComponentPlan.InstanceName.ToString());
	const TArray<FRPGPreparedBatch::FOwnedComponent>& Owned = Batch.Members[MemberIndex].Owned;
	if (!Owned.IsValidIndex(PlanIndex))
	{
		OutError = FString::Printf(TEXT("Preparation.ComponentInvalid%s: no component was leased for this plan"), *Label);
		return false;
	}
	UActorComponent* Component = Owned[PlanIndex].Component.Get();
	AActor* Actor = Participant.Actor.Get();
	if (!Component || !IsValid(Component) || Component->IsBeingDestroyed())
	{
		OutError = FString::Printf(TEXT("Preparation.ComponentInvalid%s: the component is missing, destroyed or being destroyed"), *Label);
	}
	else if (Component->GetClass() != ComponentPlan.Class)
	{
		OutError = FString::Printf(TEXT("Preparation.ComponentInvalid%s: the component is not exactly the planned class"), *Label);
	}
	else if (Component->GetFName() != ComponentPlan.InstanceName)
	{
		OutError = FString::Printf(TEXT("Preparation.ComponentInvalid%s: the component does not carry the planned instance name"), *Label);
	}
	else if (!Actor || Component->GetOwner() != Actor || !Actor->GetComponents().Contains(Component))
	{
		OutError = FString::Printf(TEXT("Preparation.ComponentInvalid%s: the component is not owned by the member's actor"), *Label);
	}
	else if (Component->IsRegistered() || Component->HasBegunPlay())
	{
		OutError = FString::Printf(TEXT("Preparation.ComponentInvalid%s: the component is registered or has begun play"), *Label);
	}
	else
	{
		return true;
	}
	return false;
}

bool FRPGBatchPreparer::Allocate(FRPGPreparedBatch& Batch, FString& OutError)
{
	for (int32 MemberIndex = 0; MemberIndex < Batch.Plan->Participants.Num(); ++MemberIndex)
	{
		const FRPGPreflightParticipantPlan& Participant = Batch.Plan->Participants[MemberIndex];
		if (Participant.Role != ERPGPreflightRole::BossCore)
		{
			continue; // a target-only member receives no component
		}
		for (int32 PlanIndex = 0; PlanIndex < Participant.Plans.Num(); ++PlanIndex)
		{
			const FRPGComponentPlan& ComponentPlan = Participant.Plans[PlanIndex];
			if (!CheckMember(Batch, MemberIndex, OutError))
			{
				return false;
			}
			AActor* Actor = Participant.Actor.Get();
			if (!ComponentPlan.Class || ComponentPlan.InstanceName.IsNone() || Actor->FindComponentByClass(ComponentPlan.Class))
			{
				OutError = FString::Printf(TEXT("Preparation.AllocationFailed[slot=%s][component=%s]: no class, no name or a consumer of that class appeared on the actor"), *Participant.Slot.ToString(), *ComponentPlan.InstanceName.ToString());
				return false;
			}
			// No other object may already carry the instance name under the actor: the engine would replace it in place (or abort on a class mismatch). Only a destroyed (garbage) object of exactly the planned class, left by an
			// earlier aborted artifact and not yet collected, may be found; it is replaced by the engine, so nobody may still hold a reference to it.
			const UObject* Existing = StaticFindObjectFast(UObject::StaticClass(), Actor, ComponentPlan.InstanceName);
			if (Existing && (IsValid(Existing) || Existing->GetClass() != ComponentPlan.Class))
			{
				OutError = FString::Printf(TEXT("Preparation.AllocationFailed[slot=%s][component=%s]: another live object, or an object of another class, already carries the instance name under the actor"), *Participant.Slot.ToString(), *ComponentPlan.InstanceName.ToString());
				return false;
			}
			// The component is leased in the same statement that holds it, so that no failure after this line can lose it.
			UActorComponent* Created = NewObject<UActorComponent>(Actor, ComponentPlan.Class, ComponentPlan.InstanceName);
			Batch.Members[MemberIndex].Owned.Emplace(ComponentPlan.InstanceName, Created);
			if (!Created)
			{
				OutError = FString::Printf(TEXT("Preparation.AllocationFailed[slot=%s][component=%s]: NewObject returned no component"), *Participant.Slot.ToString(), *ComponentPlan.InstanceName.ToString());
				return false;
			}
			if (!CheckComponent(Batch, MemberIndex, PlanIndex, OutError) || !CheckMember(Batch, MemberIndex, OutError))
			{
				return false;
			}
			if (InjectedFaultAfterStep(OutError))
			{
				return false;
			}
		}
	}
	return true;
}

bool FRPGBatchPreparer::Configure(FRPGPreparedBatch& Batch, FString& OutError)
{
	for (int32 MemberIndex = 0; MemberIndex < Batch.Plan->Participants.Num(); ++MemberIndex)
	{
		const FRPGPreflightParticipantPlan& Participant = Batch.Plan->Participants[MemberIndex];
		if (Participant.Role != ERPGPreflightRole::BossCore)
		{
			continue;
		}
		for (int32 PlanIndex = 0; PlanIndex < Participant.Plans.Num(); ++PlanIndex)
		{
			const FRPGComponentPlan& ComponentPlan = Participant.Plans[PlanIndex];
			if (!CheckMember(Batch, MemberIndex, OutError) || !CheckComponent(Batch, MemberIndex, PlanIndex, OutError))
			{
				return false;
			}
			if (!Participant.Config.IsValid() || !ComponentPlan.Configure)
			{
				OutError = FString::Printf(TEXT("Preparation.ConfigureRejected[slot=%s][component=%s]: no config lease or no configure callback"), *Participant.Slot.ToString(), *ComponentPlan.InstanceName.ToString());
				return false;
			}
			UActorComponent* Component = Batch.Members[MemberIndex].Owned[PlanIndex].Component.Get();
			FString ConfigureError;
			// The accepted callback runs before any registration and has its own whole-record guards; its diagnostic is carried unchanged.
			if (!ComponentPlan.Configure(*Component, *Participant.Config, ConfigureError))
			{
				OutError = FString::Printf(TEXT("Preparation.ConfigureRejected[slot=%s][component=%s]: %s"), *Participant.Slot.ToString(), *ComponentPlan.InstanceName.ToString(), *ConfigureError);
				return false;
			}
			if (!CheckComponent(Batch, MemberIndex, PlanIndex, OutError) || !CheckMember(Batch, MemberIndex, OutError))
			{
				return false;
			}
			if (InjectedFaultAfterStep(OutError))
			{
				return false;
			}
		}
	}
	return true;
}

FRPGPreparationResult FRPGBatchPreparer::Run(const FRPGHydrationPreflightInput& Input)
{
	FRPGPreparationResult Result;
	// Before any UObject (including the input's weak pointers) is read.
	if (!IsInGameThread())
	{
		Result.Errors.Add(TEXT("Preparation.NotGameThread: a batch is prepared on the game thread only"));
		return Result;
	}
#if WITH_DEV_AUTOMATION_TESTS
	GStepCount = 0;
	GFaultFired = false;
#endif

	// The whole batch first: the accepted preflight over the ENTIRE input. A rejection creates no component for any actor.
	TSharedPtr<const FRPGHydrationPreflightPlan> Plan;
	const FRPGHydrationResult Preflight = RPGBossHydrationPreflight::CompilePreflight(Input, Plan);
	if (!Preflight.IsReady() || !Plan.IsValid())
	{
		Result.Errors = Preflight.Errors;
		if (Result.Errors.IsEmpty())
		{
			Result.Errors.Add(TEXT("Preparation.PlanMismatch: the preflight produced no plan and no error"));
		}
		return Result;
	}
	if (Plan->Participants.Num() != Input.Requests.Num())
	{
		Result.Errors.Add(TEXT("Preparation.PlanMismatch: the plan and the request list differ in length"));
		return Result;
	}
	TArray<FName> SelectedPhaseIds;
	for (int32 Index = 0; Index < Input.Requests.Num(); ++Index)
	{
		if (Plan->Participants[Index].Slot != Input.Requests[Index].Slot || Plan->Participants[Index].Role != Input.Requests[Index].Role)
		{
			Result.Errors.Add(FString::Printf(TEXT("Preparation.PlanMismatch: participant #%d of the plan is not request #%d"), Index, Index));
			return Result;
		}
		SelectedPhaseIds.Add(Input.Requests[Index].SelectedPhaseId);
	}

	TUniquePtr<FRPGPreparedBatch> Batch(new FRPGPreparedBatch(Plan.ToSharedRef(), MoveTemp(SelectedPhaseIds)));
	FString Error;
	if (!Allocate(*Batch, Error) || !Configure(*Batch, Error))
	{
		// Everything created so far, for every member, is destroyed here; nothing survives a failed preparation.
		Result.Errors.Add(Error);
		const FRPGPreparationAbortReport Cleanup = Batch->Abort();
		Result.Errors.Append(Cleanup.Errors);
		UE_LOG(LogRPGPreparation, Log, TEXT("batch preparation failed and was cleaned up: %s (destroyed %d, already gone %d, violations %d)"), *Error, Cleanup.Destroyed, Cleanup.AlreadyGone, Cleanup.ContractViolations);
		return Result;
	}
	Batch->bPrepared = true;
	Result.Batch = MoveTemp(Batch);
	return Result;
}

FRPGPreparedBatch::FRPGPreparedBatch(TSharedRef<const FRPGHydrationPreflightPlan> InPlan, TArray<FName>&& InSelectedPhaseIds)
	: Plan(InPlan)
{
	Members.SetNum(Plan->Participants.Num());
	for (int32 Index = 0; Index < Members.Num() && Index < InSelectedPhaseIds.Num(); ++Index)
	{
		Members[Index].SelectedPhaseId = InSelectedPhaseIds[Index];
	}
}

FRPGPreparedBatch::~FRPGPreparedBatch()
{
	if (bAborted)
	{
		return;
	}
	if (IsInGameThread())
	{
		const FRPGPreparationAbortReport Cleanup = Abort();
		if (!Cleanup.IsClean())
		{
			UE_LOG(LogRPGPreparation, Warning, TEXT("a prepared batch was destroyed without Abort and its cleanup reported %d problem(s)"), Cleanup.Errors.Num());
		}
	}
	else
	{
		// A contract violation: no UObject may be touched here. The leases are released by the members; the components stay with their owners.
		ensureMsgf(false, TEXT("a prepared batch was destroyed off the game thread; its components were not destroyed"));
	}
}

FRPGPreparationAbortReport FRPGPreparedBatch::Abort()
{
	FRPGPreparationAbortReport Report;
	if (!IsInGameThread())
	{
		Report.bRefused = true;
		Report.Errors.Add(TEXT("Preparation.NotGameThread: a prepared batch is aborted on the game thread only"));
		return Report;
	}
	if (bAborted)
	{
		return Report; // idempotent: nothing is owned any more
	}
	// DD28: unregister only registrations owned by a successful call of this batch.
	// With this flag false, the historical Abort branch below is unchanged.
	if (bRegisteredByBatch)
	{
		for (int32 MemberIndex = Members.Num() - 1; MemberIndex >= 0; --MemberIndex)
		{
			AActor* Owner = Plan->Participants[MemberIndex].Actor.Get();
			for (int32 Index = Members[MemberIndex].Owned.Num() - 1; Index >= 0; --Index)
			{
				UActorComponent* Component = Members[MemberIndex].Owned[Index].Component.Get();
				if (IsValid(Owner) && IsValid(Component) && !Component->IsBeingDestroyed()
					&& Component->GetOwner() == Owner && !Component->HasBegunPlay() && Component->IsRegistered())
				{
					Component->UnregisterComponent();
				}
			}
		}
		bRegisteredByBatch = false;
	}
	bAborted = true;

	for (int32 MemberIndex = Members.Num() - 1; MemberIndex >= 0; --MemberIndex)
	{
		const FRPGPreflightParticipantPlan& Participant = Plan->Participants[MemberIndex];
		TArray<FOwnedComponent>& Owned = Members[MemberIndex].Owned;
		for (int32 OwnedIndex = Owned.Num() - 1; OwnedIndex >= 0; --OwnedIndex)
		{
			const FString Label = FString::Printf(TEXT("[slot=%s][component=%s]"), *Participant.Slot.ToString(), *Owned[OwnedIndex].Name.ToString());
			UActorComponent* Component = Owned[OwnedIndex].Component.Get();
			const AActor* Owner = Participant.Actor.Get(); // null for a stale or garbage actor
			if (!Component || !IsValid(Component) || Component->IsBeingDestroyed() || !Owner || !IsValid(Owner))
			{
				++Report.AlreadyGone; // destroyed by someone else or its owner is gone: released, never touched
			}
			else if (Component->GetOwner() != Owner || Component->IsRegistered() || Component->HasBegunPlay())
			{
				// Somebody registered or began it, or moved it: this artifact cannot undo that and does not destroy gameplay objects.
				++Report.ContractViolations;
				Report.Errors.Add(FString::Printf(TEXT("Preparation.ContractViolation%s: the component was registered, begun or moved outside the artifact; it was left in place and is no longer owned"), *Label));
			}
			else
			{
				Component->DestroyComponent();
				++Report.Destroyed;
			}
		}
		Owned.Reset(); // releases every lease
	}
	return Report;
}

int32 FRPGPreparedBatch::GetOwnedComponentCount() const
{
	int32 Count = 0;
	for (const FMember& Member : Members)
	{
		Count += Member.Owned.Num();
	}
	return Count;
}

TArray<FRPGPreparedParticipantInfo> FRPGPreparedBatch::GetParticipants() const
{
	TArray<FRPGPreparedParticipantInfo> Infos;
	for (int32 Index = 0; Index < Members.Num(); ++Index)
	{
		FRPGPreparedParticipantInfo Info;
		Info.Slot = Plan->Participants[Index].Slot;
		Info.TargetSlot = Plan->Participants[Index].TargetSlot;
		Info.Role = Plan->Participants[Index].Role;
		Info.SelectedPhaseId = Members[Index].SelectedPhaseId;
		Info.OwnedComponentCount = Members[Index].Owned.Num();
		Infos.Add(Info);
	}
	return Infos;
}

#if WITH_DEV_AUTOMATION_TESTS
TArray<const UActorComponent*> FRPGPreparedBatch::OwnedComponentsForTest() const
{
	TArray<const UActorComponent*> Components;
	for (const FMember& Member : Members)
	{
		for (const FOwnedComponent& Owned : Member.Owned)
		{
			if (const UActorComponent* Component = Owned.Component.Get())
			{
				Components.Add(Component);
			}
		}
	}
	return Components;
}
#endif

namespace RPGBossHydrationPreparation
{
	FRPGPreparationResult PrepareBatch(const FRPGHydrationPreflightInput& Input)
	{
		return FRPGBatchPreparer::Run(Input);
	}

#if WITH_DEV_AUTOMATION_TESTS
	FFaultInjectionScope::FFaultInjectionScope(int32 InFailAfterStep)
	{
		check(IsInGameThread());
		ensureMsgf(!GFaultScopeActive, TEXT("fault injection scopes do not nest"));
		GFaultScopeActive = true;
		GFailAfterStep = InFailAfterStep;
		GStepCount = 0;
		GFaultFired = false;
	}

	FFaultInjectionScope::~FFaultInjectionScope()
	{
		GFailAfterStep = 0;
		GFaultScopeActive = false;
	}

	bool FFaultInjectionScope::Fired() const
	{
		return GFaultFired;
	}
#endif
}

namespace
{
#if WITH_DEV_AUTOMATION_TESTS
	int32 GRegistrationFailAfter = 0;
	bool GRegistrationFaultActive = false;
	bool GRegistrationFaultFired = false;
#endif
}

bool FRPGPreparedBatch::RegisterOwnedComponents(FRPGRegistrationReport& OutReport)
{
	OutReport = FRPGRegistrationReport();
	// Refusals for thread/state do not consume a valid earlier registration.
	if (!IsInGameThread())
	{
		OutReport.Errors.Add(TEXT("Activation.NotGameThread: registration requires the game thread"));
		return false;
	}
	if (!IsPrepared() || bRegisteredByBatch)
	{
		OutReport.Errors.Add(bRegisteredByBatch ? TEXT("Activation.AlreadyRegistered: this batch already registered its components")
			: TEXT("Activation.NotPrepared: this batch is not prepared or has been aborted"));
		return false;
	}
	TArray<TWeakObjectPtr<UActorComponent>> RegisteredThisCall;
	int32 MemberIndex = INDEX_NONE;
	int32 PlanIndex = INDEX_NONE;
	UClass* CurrentClass = nullptr;
	auto Fail = [&](const FString& Reason)
	{
		OutReport.FailedMemberIndex = MemberIndex;
		OutReport.FailedPlanIndex = PlanIndex;
		OutReport.FailedClassName = CurrentClass ? CurrentClass->GetFName() : NAME_None;
		OutReport.Errors.Add(Reason);
		for (int32 Index = RegisteredThisCall.Num() - 1; Index >= 0; --Index)
		{
			UActorComponent* Component = RegisteredThisCall[Index].Get();
			if (IsValid(Component) && !Component->IsBeingDestroyed() && Component->IsRegistered())
			{
				Component->UnregisterComponent();
			}
		}
		OutReport.Cleanup = Abort();
		OutReport.Errors.Append(OutReport.Cleanup.Errors);
		return false;
	};
	auto CheckMember = [&]() -> bool
	{
		if (!Plan.IsValid() || !Plan->Participants.IsValidIndex(MemberIndex) || !Members.IsValidIndex(MemberIndex))
		{
			return false;
		}
		UWorld* World = Plan->World.Get();
		AActor* Actor = Plan->Participants[MemberIndex].Actor.Get();
		return IsValid(World) && !World->HasBegunPlay() && Plan->EncounterInstance.IsValid()
			&& IsValid(Actor) && !Actor->IsActorBeingDestroyed() && Actor->GetWorld() == World
			&& !Actor->HasActorBegunPlay() && !Actor->IsActorBeginningPlay();
	};
	auto CheckComponent = [&]() -> bool
	{
		if (!CheckMember()) { return false; }
		const FRPGPreflightParticipantPlan& Participant = Plan->Participants[MemberIndex];
		if (Participant.Role != ERPGPreflightRole::BossCore || !Participant.Plans.IsValidIndex(PlanIndex)
			|| !Members[MemberIndex].Owned.IsValidIndex(PlanIndex)) { return false; }
		const FRPGComponentPlan& Wanted = Participant.Plans[PlanIndex];
		UActorComponent* Component = Members[MemberIndex].Owned[PlanIndex].Component.Get();
		AActor* Actor = Participant.Actor.Get();
		return IsValid(Component) && !Component->IsBeingDestroyed() && Component->GetClass() == Wanted.Class
			&& Component->GetFName() == Wanted.InstanceName && Members[MemberIndex].Owned[PlanIndex].Name == Wanted.InstanceName
			&& Component->GetOwner() == Actor && Actor->GetComponents().Contains(Component)
			&& !Component->IsRegistered() && !Component->HasBegunPlay();
	};
	if (!Plan.IsValid() || Plan->Participants.Num() != Members.Num())
	{
		return Fail(TEXT("Activation.PlanMismatch: member shape changed"));
	}
	// Validate the WHOLE batch, including target-only actors, before the first registration.
	for (MemberIndex = 0; MemberIndex < Members.Num(); ++MemberIndex)
	{
		PlanIndex = INDEX_NONE;
		CurrentClass = nullptr;
		if (!CheckMember()) { return Fail(TEXT("Activation.MemberInvalid: owner/world invalid, begun or beginning play")); }
		const FRPGPreflightParticipantPlan& Participant = Plan->Participants[MemberIndex];
		if (Participant.Role == ERPGPreflightRole::TargetOnly)
		{
			if (!Members[MemberIndex].Owned.IsEmpty() || !Participant.Plans.IsEmpty())
			{ return Fail(TEXT("Activation.PlanMismatch: target-only member owns plans/components")); }
			continue;
		}
		if (Participant.Role != ERPGPreflightRole::BossCore || Participant.Plans.Num() != Members[MemberIndex].Owned.Num())
		{ return Fail(TEXT("Activation.PlanMismatch: role or component count changed")); }
		for (PlanIndex = 0; PlanIndex < Participant.Plans.Num(); ++PlanIndex)
		{
			CurrentClass = Participant.Plans[PlanIndex].Class;
			if (!CheckComponent()) { return Fail(TEXT("Activation.ComponentInvalid: owned component failed whole-batch validation")); }
		}
	}
	for (MemberIndex = 0; MemberIndex < Members.Num(); ++MemberIndex)
	{
		const FRPGPreflightParticipantPlan& Participant = Plan->Participants[MemberIndex];
		for (PlanIndex = 0; PlanIndex < Members[MemberIndex].Owned.Num(); ++PlanIndex)
		{
			CurrentClass = Participant.Plans[PlanIndex].Class;
			if (!CheckComponent()) { return Fail(TEXT("Activation.ComponentInvalid: state changed before registration")); }
			UActorComponent* Component = Members[MemberIndex].Owned[PlanIndex].Component.Get();
			Component->RegisterComponent();
			if (IsValid(Component) && Component->IsRegistered()) { RegisteredThisCall.Add(Component); }
			if (!IsValid(Component) || Component->IsBeingDestroyed() || !Component->IsRegistered() || Component->HasBegunPlay()
				|| !CheckMember() || Component->GetOwner() != Participant.Actor.Get())
			{ return Fail(TEXT("Activation.RegistrationFailed: component did not remain registered and never begun")); }
			FRPGRegisteredComponentInfo Info;
			Info.MemberIndex = MemberIndex;
			Info.PlanIndex = PlanIndex;
			Info.Slot = Participant.Slot;
			Info.ClassName = Component->GetClass()->GetFName();
			Info.InstanceName = Component->GetFName();
			OutReport.Registered.Add(Info);
#if WITH_DEV_AUTOMATION_TESTS
			if (GRegistrationFaultActive && GRegistrationFailAfter > 0 && RegisteredThisCall.Num() == GRegistrationFailAfter)
			{
				GRegistrationFaultFired = true;
				return Fail(TEXT("Activation.InjectedFault: test-only failure after real registration"));
			}
#endif
		}
	}
	bRegisteredByBatch = true;
	OutReport.bSucceeded = true;
	return true;
}

#if WITH_DEV_AUTOMATION_TESTS
RPGBossActivation::FRegistrationFaultScope::FRegistrationFaultScope(int32 InFailAfterRegistration)
{
	check(IsInGameThread() && !GRegistrationFaultActive && InFailAfterRegistration > 0);
	GRegistrationFaultActive = true;
	GRegistrationFailAfter = InFailAfterRegistration;
	GRegistrationFaultFired = false;
}
RPGBossActivation::FRegistrationFaultScope::~FRegistrationFaultScope()
{
	check(IsInGameThread() && GRegistrationFaultActive);
	GRegistrationFaultActive = false;
	GRegistrationFailAfter = 0;
}
bool RPGBossActivation::FRegistrationFaultScope::Fired() const { return GRegistrationFaultFired; }
#endif
