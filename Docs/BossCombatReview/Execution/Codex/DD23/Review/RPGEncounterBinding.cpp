#include "Player/RPGEncounterBinding.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossEncounterPolicyAdapters.h"
#include "Player/RPGBossStaggerPolicyAdapters.h"
#include "Player/RPGBossPhaseFlowAdapters.h"
#include "Player/RPGBossPhasesClusterAdapters.h"
#include "Player/RPGBossStaggerClusterAdapters.h"
#include "Player/RPGBossDormantWakeAdapters.h"
#include "Player/RPGBossBleedAdapters.h"
#include "Player/RPGBossLowSweepAdapters.h"
#include "Player/RPGBossShockwaveAdapters.h"
#include "Player/RPGBossHealPunishAdapters.h"
#include "Player/RPGBossLookAdapters.h"
#include "Engine/World.h"
#include "Animation/AnimSequenceBase.h"
#include "Animation/Skeleton.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "GameFramework/Character.h"
#include "UObject/StrongObjectPtr.h"

namespace RPGCombatHydration
{
static bool IsSHA256(const FString& Text)
{
	if (Text.Len() != 64) { return false; }
	for (TCHAR C : Text) { if (!FChar::IsHexDigit(C)) { return false; } }
	return true;
}
static FRPGHydrationResult CompileParticipantImpl(const URPGBossDefinition& D,
	TSharedPtr<const RPGCombatRegistry::FEpoch> Content, const FString& Hash,
	TSharedPtr<const FRPGParticipantConfig>& Out, bool bSynthetic)
{
	Out.Reset(); FRPGHydrationResult Result;
	if (D.Schema != 1 || D.DefinitionId.IsNone() || D.PresentationId.IsNone()
		|| !Content || !Content->Id.IsValid() || !IsSHA256(Hash))
	{
		Result.Fail(TEXT("definition/schema/content/manifest identity absent"));
	}
	if (!FMath::IsFinite(D.Stats.MaxHealth) || D.Stats.MaxHealth <= 0.f
		|| !FMath::IsFinite(D.Stats.MaxPosture) || D.Stats.MaxPosture <= 0.f
		|| !FMath::IsFinite(D.Stats.PostureRegenDelay) || D.Stats.PostureRegenDelay < 0.f
		|| !FMath::IsFinite(D.Stats.PostureRegenRate) || D.Stats.PostureRegenRate < 0.f)
	{
		Result.Fail(TEXT("invalid stats (no constructor/Boss01 substitution)"));
	}
	FString PolicyError;
	if (!RPGBossEncounterPolicyAdapters::ValidateEncounterPolicy(D.EncounterPolicy, PolicyError)) { Result.Fail(PolicyError); } // never replaced by the 1200/true authoring defaults
	FString StaggerError;
	if (!RPGBossStaggerPolicyAdapters::ValidateStaggerPolicy(D.StaggerPolicy, StaggerError)) { Result.Fail(StaggerError); } // never replaced by the authoring defaults, never clamped
	FString PhaseFlowError;
	if (!RPGBossPhaseFlowAdapters::ValidatePhaseFlow(D.PhaseFlow, PhaseFlowError)) { Result.Fail(PhaseFlowError); } // never replaced by the authoring defaults, never trimmed or normalized
	FString FireballError;
	if (!RPGBossPhasesClusterAdapters::ValidateFireball(D.Fireball, FireballError)) { Result.Fail(FireballError); } // never replaced by the authoring defaults, never reordered
	FString DependencyError;
	if (!RPGBossPhasesClusterAdapters::ValidatePhaseDependencies(D.PhaseDependencies, D.PhaseFlow.bUseRoarClip, DependencyError)) { Result.Fail(DependencyError); } // structure only, no registry query, no load
	FString StaggerProfileError;
	if (!RPGBossStaggerClusterAdapters::ValidateStaggerProfile(D.StaggerProfile, StaggerProfileError)) { Result.Fail(StaggerProfileError); } // structure only, no registry query, no load
	FString DormantWakeError;
	if (!RPGBossDormantWakeAdapters::ValidateDormantWake(D.DormantWake, DormantWakeError)) { Result.Fail(DormantWakeError); } // structure only, no registry query, no load, never defaulted
	FString BleedError;
	if (!RPGBossBleedAdapters::ValidateBleed(D.Bleed, BleedError)) { Result.Fail(BleedError); } // structure only, no registry query, no load, never defaulted, never clamped
	FString LowSweepError;
	if (!RPGBossLowSweepAdapters::ValidateLowSweep(D.LowSweep, LowSweepError)) { Result.Fail(LowSweepError); } // C258 authored structure; MoveId is not tracker-table resolution
	FString ShockwaveError;
	if (!RPGBossShockwaveAdapters::ValidateShockwave(D.Shockwave,ShockwaveError)) { Result.Fail(ShockwaveError); } // authored record only, no tracker resolution
	FString PunishError;
	// C265 authored structure; no move/socket resolution.
	if (!RPGBossHealPunishAdapters::ValidateHealPunish(D.HealPunish, PunishError))
	{
		Result.Fail(PunishError);
	}
	FString LookError;
	if (!RPGBossLookAdapters::ValidateLook(D.Look, LookError))
	{
		Result.Fail(LookError);
	}
	TSet<FName> PhaseIds;
	for (const FRPGPhaseConfig& Phase : D.Phases)
	{
		if (Phase.PhaseId.IsNone() || PhaseIds.Contains(Phase.PhaseId)
			|| !FMath::IsFinite(Phase.EntryHealthFraction) || Phase.EntryHealthFraction <= 0.f || Phase.EntryHealthFraction > 1.f
			|| !FMath::IsFinite(Phase.SpeedMultiplier) || Phase.SpeedMultiplier <= 0.f
			|| !FMath::IsFinite(Phase.RateMultiplier) || Phase.RateMultiplier <= 0.f
			|| !FMath::IsFinite(Phase.AttackMultiplier) || Phase.AttackMultiplier <= 0.f)
		{
			Result.Fail(TEXT("invalid/duplicate phase"));
		}
		PhaseIds.Add(Phase.PhaseId);
	}
	TSet<FString> Fields;
	for (const FRPGParityField& F : D.Fields)
	{
		if (F.FieldPath.IsEmpty() || Fields.Contains(F.FieldPath) || F.Type.IsEmpty()
			|| F.SourcePath.IsEmpty() || !IsSHA256(F.SourceSHA256) || F.SourceSite.IsEmpty()
			|| F.Origin.IsEmpty() || F.Precedence.IsEmpty() || F.Destination.IsEmpty()
			|| F.FirstRead.IsEmpty() || F.Witness.IsEmpty())
		{
			Result.Fail(TEXT("incomplete/duplicate field-source manifest"));
		}
		Fields.Add(F.FieldPath);
	}
	if (Fields.IsEmpty()) { Result.Fail(TEXT("field manifest required")); }
	if (!Result.IsReady()) { return Result; }
	auto Value = MakeShared<FRPGParticipantConfig>();
	Value->BossId = D.DefinitionId; Value->PresentationId = D.PresentationId;
	Value->Schema = D.Schema; Value->StableManifestHash = Hash;
	Value->Stats = D.Stats; Value->Phases = D.Phases; Value->Fields = D.Fields;
	Value->EncounterPolicy = D.EncounterPolicy;
	Value->StaggerPolicy = D.StaggerPolicy;
	Value->PhaseFlow = D.PhaseFlow;
	Value->Fireball = D.Fireball;
	Value->PhaseDependencies = D.PhaseDependencies;
	Value->StaggerProfile = D.StaggerProfile;
	Value->DormantWake = D.DormantWake;
	Value->Bleed = D.Bleed;
	Value->LowSweep = D.LowSweep;
	Value->Shockwave = D.Shockwave;
	Value->HealPunish = D.HealPunish;
	Value->Look = D.Look;
	Value->Content = MoveTemp(Content); Out = Value;
	Value->bSyntheticFixture = bSynthetic;
	if (!bSynthetic)
	{
		Value->Skeleton.Reset(D.Skeleton.LoadSynchronous());
		if (!Value->Skeleton.IsValid() || D.Animations.IsEmpty()) { Result.Fail(TEXT("required skeleton/animation dependencies missing")); }
		for (const auto& Ref : D.Animations)
		{
			UAnimSequenceBase* Animation = Ref.LoadSynchronous();
			if (!Animation || Animation->GetSkeleton() != Value->Skeleton.Get()) { Result.Fail(TEXT("animation/skeleton identity mismatch; explicit retargeted dependency required")); }
			else { Value->Animations.Emplace(Animation); }
		}
	}
	if (!Result.IsReady()) { Out.Reset(); }
	return Result;
}

FRPGHydrationResult CompileParticipant(const URPGBossDefinition& D, TSharedPtr<const RPGCombatRegistry::FEpoch> C,
	const FString& H, TSharedPtr<const FRPGParticipantConfig>& Out)
{
	return CompileParticipantImpl(D, MoveTemp(C), H, Out, false);
}
#if WITH_DEV_AUTOMATION_TESTS
FRPGHydrationResult CompileSyntheticParticipant(const URPGBossDefinition& D, TSharedPtr<const RPGCombatRegistry::FEpoch> C,
	const FString& H, TSharedPtr<const FRPGParticipantConfig>& Out)
{
	return CompileParticipantImpl(D, MoveTemp(C), H, Out, true);
}
#endif
}

bool URPGCombatParticipant::ConfigureBeforeRegistration(TSharedPtr<const FRPGParticipantConfig> Config,
	const FRPGParticipantKey& Key, URPGCombatContextSubsystem& OwnerContext)
{
	if (Snapshot || IsRegistered() || HasBegunPlay() || !Config || !OwnerContext.IsCurrent(Key)) { return false; }
	Snapshot = MoveTemp(Config); ParticipantKey = Key; Context = &OwnerContext;
	return true;
}

bool URPGCombatParticipant::IsReady() const
{
	return Snapshot && Context.IsValid() && Context->IsHydrated(ParticipantKey);
}

FString URPGCombatParticipant::GetKeyDiagnostic() const
{
	return ParticipantKey.WorldSession.ToString() + TEXT("/") + ParticipantKey.EncounterInstance.ToString()
		+ TEXT("/") + ParticipantKey.Slot.ToString() + TEXT("/") + LexToString(ParticipantKey.Generation);
}

void URPGCombatParticipant::EndPlay(const EEndPlayReason::Type Reason)
{
	if (Context.IsValid() && GetOwner()) { Context->UnbindActor(*GetOwner()); }
	Snapshot.Reset(); Context.Reset(); Super::EndPlay(Reason);
}

bool URPGCombatContextSubsystem::ShouldCreateSubsystem(UObject* Outer) const
{
	const UWorld* World = Cast<UWorld>(Outer); return World && World->IsGameWorld();
}

void URPGCombatContextSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection); Session = FGuid::NewGuid();
}

void URPGCombatContextSubsystem::Deinitialize()
{
	Records.Reset(); Session.Invalidate(); Super::Deinitialize();
}

FRPGHydrationResult URPGCombatContextSubsystem::BindEncounter(const ARPGEncounterBinding& Binding,
	const TMap<FName, TSharedPtr<const FRPGParticipantConfig>>& Configs)
{
	FRPGHydrationResult Result;
	if (bHydrationInProgress || Binding.GetWorld() != GetWorld() || !Session.IsValid() || !Binding.EncounterInstance.IsValid()
		|| Binding.Participants.IsEmpty() || Configs.Num() != Binding.Participants.Num())
	{
		Result.Fail(TEXT("invalid world/encounter/config batch")); return Result;
	}
	TSet<FName> Slots; TSet<AActor*> Actors;
	TArray<FRecord> Pending;
	for (const FRecord& Old : Records)
	{
		if (Old.Key.EncounterInstance == Binding.EncounterInstance)
		{
			Result.Fail(TEXT("encounter already bound; no live rebinding")); return Result;
		}
	}
	for (const FRPGPlacedParticipantBinding& B : Binding.Participants)
	{
		AActor* Actor = B.Actor.Get(); const auto* Config = Configs.Find(B.Slot);
		if (B.Slot.IsNone() || Slots.Contains(B.Slot) || !IsValid(Actor) || Actors.Contains(Actor)
			|| Actor->GetWorld() != GetWorld() || Actor->HasActorBegunPlay() || FindParticipant(*Actor).IsSet()
			|| !Config || !*Config || !(*Config)->Content)
		{
			Result.Fail(TEXT("duplicate/unbound/foreign/already begun participant or missing config")); continue;
		}
		Slots.Add(B.Slot); Actors.Add(Actor);
		if (!(*Config)->bSyntheticFixture)
		{
			if (!B.Definition || B.Definition->DefinitionId != (*Config)->BossId || B.Definition->Schema != (*Config)->Schema)
			{
				Result.Fail(TEXT("explicit definition/config mismatch")); continue;
			}
			const ACharacter* Character = Cast<ACharacter>(Actor);
			const USkeletalMesh* Mesh = Character && Character->GetMesh() ? Character->GetMesh()->GetSkeletalMeshAsset() : nullptr;
			const auto WorldContent = RPGCombatRegistry::ForWorld(GetWorld());
			if (!Mesh || !(*Config)->Skeleton.IsValid() || !(*Config)->Skeleton->IsCompatibleMesh(Mesh)
				|| !WorldContent || WorldContent->Id != (*Config)->Content->Id)
			{
				Result.Fail(TEXT("mesh/skeleton/world content mismatch")); continue;
			}
		}
#if !WITH_DEV_AUTOMATION_TESTS
		else { Result.Fail(TEXT("synthetic fixture unavailable in this target")); continue; }
#endif
		FRecord Record; Record.Actor = Actor; Record.Key = {Session, Binding.EncounterInstance, B.Slot, 1};
		Record.TargetSlot = B.TargetSlot; Record.Config = *Config; Pending.Add(MoveTemp(Record));
	}
	for (const FRecord& R : Pending)
	{
		if (!Slots.Contains(R.TargetSlot)) { Result.Fail(TEXT("explicit target slot missing")); }
	}
	if (Result.IsReady()) { Records.Append(MoveTemp(Pending)); }
	return Result;
}

TOptional<FRPGParticipantKey> URPGCombatContextSubsystem::FindParticipant(const AActor& Actor) const
{
	for (const FRecord& R : Records)
	{
		if (!R.bPoisoned && R.Actor.Get() == &Actor) { return R.Key; }
	}
	return {};
}

bool URPGCombatContextSubsystem::IsCurrent(const FRPGParticipantKey& Key) const
{
	return Records.ContainsByPredicate([&Key](const FRecord& R) { return !R.bPoisoned && R.Actor.IsValid() && R.Key == Key; });
}

bool URPGCombatContextSubsystem::IsHydrated(const FRPGParticipantKey& Key) const
{
	return Records.ContainsByPredicate([&Key](const FRecord& R) { return !R.bPoisoned && R.bHydrated && R.Actor.IsValid() && R.Key == Key; });
}

AActor* URPGCombatContextSubsystem::ResolveTarget(const FRPGParticipantKey& Key, FName TargetSlot) const
{
	if (!IsHydrated(Key)) { return nullptr; }
	for (const FRecord& R : Records)
	{
		if (R.Key.WorldSession == Key.WorldSession && R.Key.EncounterInstance == Key.EncounterInstance
			&& R.Key.Slot == TargetSlot && IsHydrated(R.Key)) { return R.Actor.Get(); }
	}
	return nullptr;
}

URPGBossEncounter* URPGCombatContextSubsystem::ResolveEncounter(const AActor& Requester) const
{
	for (const FRecord& R : Records)
	{
		if (R.Actor.Get() != &Requester || !IsHydrated(R.Key)) { continue; }
		if (auto* Own = Requester.FindComponentByClass<URPGBossEncounter>()) { return Own; }
		AActor* Target = ResolveTarget(R.Key, R.TargetSlot);
		return Target ? Target->FindComponentByClass<URPGBossEncounter>() : nullptr;
	}
	return nullptr;
}

bool URPGCombatContextSubsystem::OnGenerationChanged(AActor& Actor, uint32 NewGeneration)
{
	FRecord* Origin = Records.FindByPredicate([&Actor](const FRecord& R) { return R.Actor.Get() == &Actor; });
	if (bHydrationInProgress || !Origin || Origin->bPoisoned || NewGeneration <= Origin->Key.Generation) { return false; }
	const FGuid Encounter = Origin->Key.EncounterInstance;
	for (FRecord& R : Records)
	{
		if (R.Key.EncounterInstance != Encounter) { continue; }
		R.Key.Generation = NewGeneration;
		if (AActor* Bound = R.Actor.Get())
		{
			if (auto* P = Bound->FindComponentByClass<URPGCombatParticipant>()) { P->ParticipantKey = R.Key; }
		}
	}
	return true;
}

void URPGCombatContextSubsystem::UnbindActor(AActor& Actor)
{
	const FRecord* Found = Records.FindByPredicate([&Actor](const FRecord& R) { return R.Actor.Get() == &Actor; });
	if (!Found) { return; }
	const FGuid Encounter = Found->Key.EncounterInstance;
	// A missing member invalidates the whole encounter, not a half-live target relation.
	Records.RemoveAll([Encounter](const FRecord& R) { return R.Key.EncounterInstance == Encounter; });
}

int32 URPGCombatContextSubsystem::GetBoundCount() const
{
	int32 Count = 0;
	for (const FRecord& R : Records) { if (R.Actor.IsValid() && !R.bPoisoned) { ++Count; } }
	return Count;
}

int32 URPGCombatContextSubsystem::GetReadyCount() const
{
	int32 Count = 0;
	for (const FRecord& R : Records) { if (R.Actor.IsValid() && !R.bPoisoned && R.bHydrated) { ++Count; } }
	return Count;
}

FRPGHydrationResult URPGCombatContextSubsystem::CreateConfigureRegister(AActor& Actor, const TArray<FRPGComponentPlan>& Plans)
{
	FRPGHydrationResult Result;
	FRecord* Record = Records.FindByPredicate([&Actor](const FRecord& R) { return R.Actor.Get() == &Actor; });
	if (bHydrationInProgress || !Record || Record->bPoisoned || Record->bHydrated || Actor.HasActorBegunPlay() || Plans.IsEmpty())
	{
		Result.Fail(TEXT("unbound/late/repeated/empty hydration")); return Result;
	}
	TSet<UClass*> Classes; TSet<FName> Names; TSet<FString> Manifest;
	for (const FRPGParityField& Field : Record->Config->Fields) { Manifest.Add(Field.FieldPath); }
	for (const FRPGComponentPlan& Plan : Plans)
	{
		if (!Plan.Class || !Plan.Class->IsChildOf(UActorComponent::StaticClass()) || Plan.Class->HasAnyClassFlags(CLASS_Abstract)
			|| Plan.Class == URPGCombatParticipant::StaticClass() || Classes.Contains(Plan.Class) || Names.Contains(Plan.InstanceName)
			|| Plan.InstanceName.IsNone() || !Plan.Configure || Actor.FindComponentByClass(Plan.Class))
		{
			Result.Fail(TEXT("invalid/duplicate/pre-existing consumer; defaults may already have been read"));
		}
		for (const FString& Field : Plan.RequiredFields)
		{
			if (!Manifest.Contains(Field)) { Result.Fail(TEXT("required parity field missing: ") + Field); }
		}
		Classes.Add(Plan.Class); Names.Add(Plan.InstanceName);
	}
	if (Actor.FindComponentByClass<URPGCombatParticipant>()) { Result.Fail(TEXT("pre-existing participant")); }
	if (!Result.IsReady()) { return Result; }
	TGuardValue<bool> HydrationGuard(bHydrationInProgress, true);
	const FRPGParticipantKey OriginalKey = Record->Key;
	const TSharedPtr<const FRPGParticipantConfig> Snapshot = Record->Config;
	// Leases keep all unregistered components alive across configure callbacks/GC.
	TArray<TStrongObjectPtr<UActorComponent>> Pending;
	TArray<TStrongObjectPtr<UClass>> ClassLeases;
	for (const auto& Plan : Plans) { ClassLeases.Emplace(Plan.Class); }
	TStrongObjectPtr<URPGCombatParticipant> Participant(NewObject<URPGCombatParticipant>(&Actor));
	if (!Participant->ConfigureBeforeRegistration(Snapshot, OriginalKey, *this))
	{
		Result.Fail(TEXT("participant configure failed")); return Result;
	}
	for (const FRPGComponentPlan& Plan : Plans)
	{
		UActorComponent* Component = NewObject<UActorComponent>(&Actor, Plan.Class, Plan.InstanceName);
		Pending.Emplace(Component);
		FString Error;
		if (!Component || !Plan.Configure(*Component, *Snapshot, Error) || Component->IsRegistered() || Component->HasBegunPlay()
			|| !IsCurrent(OriginalKey))
		{
			Result.Fail(TEXT("configure contract violated: ") + Error); break;
		}
	}
	if (!Result.IsReady())
	{
		for (auto& Component : Pending) { if (Component.IsValid()) { Component->DestroyComponent(); } }
		Participant->DestroyComponent(); return Result;
	}
	// This is NOT a rollback transaction once registration callbacks run.
	// Caller must have validated the entire encounter and all typed adapters beforehand.
	Participant->RegisterComponent();
	for (auto& Component : Pending) { Component->RegisterComponent(); }
	bool Ready = Participant->IsRegistered();
	for (const auto& Component : Pending) { Ready &= Component->IsRegistered(); }
	Record = Records.FindByPredicate([&OriginalKey](const FRecord& R) { return R.Key == OriginalKey; });
	if (!Record) { Result.Fail(TEXT("binding invalidated during registration")); return Result; }
	Record->bHydrated = Ready; Record->bPoisoned = !Ready;
	if (!Ready) { Result.Fail(TEXT("registration failed; context poisoned; do not activate gameplay")); }
	return Result;
}
