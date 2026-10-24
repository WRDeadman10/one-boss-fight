// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossDeath.h"
#include "Player/RPGBossClips.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossDormantWake.h"
#include "Player/RPGBossRemains.h"
#include "Player/RPGBossPhases.h"
#include "Player/RPGBossPosture.h"
#include "Player/RPGBossStagger.h"
#include "Pack/RPGBlueprintCall.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Animation/AnimSequence.h"
#include "Components/SceneComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "GameFramework/Character.h"
#include "UObject/UnrealType.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGBossDeath, Log, All);

using namespace RPGPack;

namespace
{
	constexpr const TCHAR* DeathHealthTag = TEXT("Attribute.Health");
}

URPGBossDeath::URPGBossDeath()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.bStartWithTickEnabled = true;
	PrimaryComponentTick.TickInterval = 0.f;

	DeathClip = TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Animations/AN_Boss01_DeathLegend.AN_Boss01_DeathLegend")));
	DeathMontage = TSoftObjectPtr<UAnimMontage>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Animations/AM_Boss01_DeathLegend.AM_Boss01_DeathLegend")));
}

URPGBossDeath* URPGBossDeath::Attach(AActor* Boss, ERPGBossDeathMode Mode)
{
	if (!Boss)
	{
		return nullptr;
	}
	if (URPGBossDeath* Existing = Boss->FindComponentByClass<URPGBossDeath>())
	{
		return Existing;
	}
	URPGBossDeath* Death = NewObject<URPGBossDeath>(Boss, TEXT("RPGBossDeath"));
	Death->DeathMode = Mode;
	Death->RegisterComponent();
	return Death;
}

FString URPGBossDeath::GetDeathStateName() const
{
	switch (State)
	{
	case EState::Dying: return TEXT("dying");
	case EState::Dead: return TEXT("dead");
	default: return TEXT("alive");
	}
}

FString URPGBossDeath::GetDeathModeName() const
{
	return DeathMode == ERPGBossDeathMode::OwnClip ? TEXT("own_clip") : TEXT("pack_montage");
}

double URPGBossDeath::GetDeathAge() const
{
	const UWorld* World = GetWorld();
	return State != EState::Alive && World ? World->GetTimeSeconds() - DeathTime : -1.0;
}

void URPGBossDeath::SetDeathModeForTest(const FString& Mode)
{
#if !UE_BUILD_SHIPPING
	DeathMode = Mode.StartsWith(TEXT("own"), ESearchCase::IgnoreCase) ? ERPGBossDeathMode::OwnClip : ERPGBossDeathMode::PackMontage;
	bPreloaded = false; // the next tick loads what the new mode needs
	NextPackPoll = 0.0;
#endif
}

FString URPGBossDeath::ApplyPackMontageNow()
{
#if UE_BUILD_SHIPPING
	return TEXT("unavailable in Shipping");
#else
	ApplyPackMontage();
	return LastPackResult;
#endif
}

void URPGBossDeath::BeginPlay()
{
	Super::BeginPlay();
	NextPackPoll = 0.0; // the first tick, one frame after BeginPlay, looks at the pack's death ability
	LastResetCount = -1;
	// The code that raises the death (a lethal riposte in Stagger's tick, a bleed in Posture, a phase in Phases) ticks first, so the guard sees the death in the same frame and the pack's ragdoll never gets a free physics step (review D). Components added later are simply not ordered.
	if (URPGBossStagger* Stagger = GetOwner()->FindComponentByClass<URPGBossStagger>())
	{
		AddTickPrerequisiteComponent(Stagger);
	}
	if (URPGBossPosture* Posture = GetOwner()->FindComponentByClass<URPGBossPosture>())
	{
		AddTickPrerequisiteComponent(Posture);
	}
	if (URPGBossPhases* Phases = GetOwner()->FindComponentByClass<URPGBossPhases>())
	{
		AddTickPrerequisiteComponent(Phases);
	}
}

void URPGBossDeath::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if (!bEnding && State == EState::Dead && EndPlayReason == EEndPlayReason::Destroyed)
	{
		if (UWorld* World = GetWorld(); World && !World->bIsTearingDown && bRemainsTransformKnown)
		{
			ARPGBossRemains::Spawn(World, LastRemainsTransform, LoadedRemainsMesh, LoadedRemainsMaterial, LoadedRemainsBurst);
		}
	}
	// The pack destroys a dead boss a few seconds after its death (KI-083): from here on the mesh, its physics and its montages are not touched.
	bEnding = true;
	bGuardActive = false;
	Super::EndPlay(EndPlayReason);
}

UAnimSequence* URPGBossDeath::GetClip()
{
	if (!LoadedClip && !bClipTried)
	{
		bClipTried = true; // a clip that is not there is reported once, not on every tick
		LoadedClip = DeathClip.LoadSynchronous();
		if (!LoadedClip)
		{
			UE_LOG(LogRPGBossDeath, Warning, TEXT("the death clip %s did not load"), *DeathClip.ToString());
		}
	}
	return LoadedClip.Get();
}

UAnimMontage* URPGBossDeath::GetMontage()
{
	if (!LoadedMontage && !bMontageTried)
	{
		bMontageTried = true;
		LoadedMontage = DeathMontage.LoadSynchronous();
		if (!LoadedMontage)
		{
			UE_LOG(LogRPGBossDeath, Warning, TEXT("the death montage %s did not load (run Scripts/Editor/make_death_montage.py)"), *DeathMontage.ToString());
		}
	}
	return LoadedMontage.Get();
}

void URPGBossDeath::Preload()
{
	bPreloaded = true;
	// Resident before the kill, so the frame of the death never waits for the disk. Only what the mode needs: a montage that was never made must not warn in OwnClip mode.
	if (DeathMode == ERPGBossDeathMode::OwnClip)
	{
		GetClip();
	}
	else
	{
		GetMontage();
	}
	UE_LOG(LogRPGBossDeath, Log, TEXT("%s: death handling ready, mode %s (clip %d, montage %d)"), *GetOwner()->GetName(), *GetDeathModeName(), LoadedClip ? 1 : 0, LoadedMontage ? 1 : 0);
}

void URPGBossDeath::CaptureMeshPlacement(const ACharacter* Character)
{
	const USkeletalMeshComponent* Mesh = Character->GetMesh();
	if (!Mesh || Mesh->IsAnySimulatingPhysics())
	{
		return; // a ragdoll that is already running must not be taken for the place the mesh belongs
	}
	MeshParent = Mesh->GetAttachParent();
	MeshSocket = Mesh->GetAttachSocketName();
	MeshRelativeLocation = Mesh->GetRelativeLocation();
	MeshRelativeRotation = Mesh->GetRelativeRotation();
	bMeshPlacementKnown = MeshParent.IsValid();
}

void URPGBossDeath::CaptureRemainsTransform(const ACharacter* Character)
{
	const USkeletalMeshComponent* Mesh = Character ? Character->GetMesh() : nullptr;
	if (Mesh && !Mesh->IsAnySimulatingPhysics())
	{
		LastRemainsTransform = Mesh->GetComponentTransform();
		bRemainsTransformKnown = true;
	}
}

bool URPGBossDeath::NotePackMiss(const FString& Why)
{
	LastPackResult = Why;
	++PackMissCount;
	if (PackMissCount == 5)
	{
		UE_LOG(LogRPGBossDeath, Warning, TEXT("%s: the pack's death montage could not be set after %d looks: %s"), *GetOwner()->GetName(), PackMissCount, *Why);
	}
	return false;
}

void URPGBossDeath::PollPack(double Now)
{
	const URPGBossEncounter* Encounter = GetOwner()->FindComponentByClass<URPGBossEncounter>();
	const int32 Resets = Encounter ? Encounter->GetResetCount() : 0;
	if (Resets != LastResetCount)
	{
		LastResetCount = Resets; // the first tick (-1 -> 0) and every encounter reset: look at once
		NextPackPoll = 0.0;
	}
	if (Now < NextPackPoll)
	{
		return;
	}
	NextPackPoll = Now + PackPollSeconds;
	ApplyPackMontage();
}

bool URPGBossDeath::ApplyPackMontage()
{
	UObject* Ability = FindAbilityByClassName(GetOwner(), PackDeathAbilityClassName);
	if (!Ability)
	{
		return NotePackMiss(FString::Printf(TEXT("no %s on the boss yet"), *PackDeathAbilityClassName.ToString()));
	}
	UAnimMontage* Montage = GetMontage();
	if (!Montage)
	{
		return NotePackMiss(TEXT("the death montage did not load"));
	}
	const FArrayProperty* Array = FindFProperty<FArrayProperty>(Ability->GetClass(), PackDeathMontagesName);
	if (!Array || !Array->Inner)
	{
		return NotePackMiss(FString::Printf(TEXT("%s has no array %s"), *Ability->GetClass()->GetName(), *PackDeathMontagesName.ToString()));
	}
	// The array holds montages or, as the pack's own ability variables do (AttackMontages), F_AbilityMontage structs whose AnimMontage_<n>_<guid> field is the montage.
	const FObjectPropertyBase* ObjectInner = CastField<FObjectPropertyBase>(Array->Inner);
	const FStructProperty* StructInner = CastField<FStructProperty>(Array->Inner);
	const FObjectPropertyBase* MontageField = nullptr;
	if (StructInner && StructInner->Struct)
	{
		for (TFieldIterator<FProperty> It(StructInner->Struct); It; ++It)
		{
			if (const FObjectPropertyBase* Candidate = CastField<FObjectPropertyBase>(*It))
			{
				if (Candidate->GetName().StartsWith(TEXT("AnimMontage")))
				{
					MontageField = Candidate;
					break;
				}
			}
		}
	}
	const FObjectPropertyBase* MontageSlot = ObjectInner ? ObjectInner : MontageField;
	if (!MontageSlot)
	{
		return NotePackMiss(FString::Printf(TEXT("the elements of %s are %s: no montage slot found"), *PackDeathMontagesName.ToString(), *Array->Inner->GetCPPType()));
	}
	const UClass* Wanted = MontageSlot->PropertyClass.Get();
	if (Wanted && !Montage->GetClass()->IsChildOf(Wanted))
	{
		return NotePackMiss(FString::Printf(TEXT("the montage slot of %s holds %s, not a montage"), *PackDeathMontagesName.ToString(), *Wanted->GetName()));
	}

	FScriptArrayHelper Helper(Array, Array->ContainerPtrToValuePtr<void>(Ability));
	if (Helper.Num() == 1)
	{
		uint8* First = Helper.GetRawPtr(0);
		const void* Value = ObjectInner ? static_cast<const void*>(First) : static_cast<const void*>(MontageField->ContainerPtrToValuePtr<void>(First));
		if (MontageSlot->GetObjectPropertyValue(Value) == Montage)
		{
			PackMissCount = 0;
			LastPackResult = TEXT("already set");
			return true;
		}
	}
	// The ability's instance is the pack's own object: only this instance's array is written (the Blueprint's defaults stay untouched), and the entry is built from the struct's own defaults.
	Helper.EmptyValues();
	Helper.AddValue();
	uint8* Element = Helper.GetRawPtr(0);
	if (ObjectInner)
	{
		ObjectInner->SetObjectPropertyValue(Element, Montage);
	}
	else
	{
		MontageField->SetObjectPropertyValue(MontageField->ContainerPtrToValuePtr<void>(Element), Montage);
		if (PackEndTimeMultiplier > 0.f)
		{
			for (TFieldIterator<FProperty> It(StructInner->Struct); It; ++It)
			{
				const FNumericProperty* Number = CastField<FNumericProperty>(*It);
				if (Number && Number->IsFloatingPoint() && Number->GetName().StartsWith(TEXT("EndTimeMultiplier")))
				{
					Number->SetFloatingPointPropertyValue(Number->ContainerPtrToValuePtr<void>(Element), static_cast<double>(PackEndTimeMultiplier));
				}
			}
		}
	}
	++PackSetCount;
	PackMissCount = 0;
	const FString ElementKind = ObjectInner ? FString(TEXT("montage entries")) : StructInner->Struct->GetName();
	LastPackResult = FString::Printf(TEXT("set %s (%s)"), *Montage->GetName(), *ElementKind);
	UE_LOG(LogRPGBossDeath, Log, TEXT("%s: %s of %s set to [%s] (%s), %d so far"), *GetOwner()->GetName(), *PackDeathMontagesName.ToString(), *Ability->GetClass()->GetName(), *Montage->GetName(), *ElementKind, PackSetCount);
	return true;
}

void URPGBossDeath::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	ACharacter* Character = Cast<ACharacter>(GetOwner());
	const UWorld* World = GetWorld();
	if (bEnding || !Character || !World)
	{
		return;
	}
	const double Now = World->GetTimeSeconds();
	if (!bPreloaded)
	{
		Preload();
	}
	double Health = 1.0;
	const bool bHealthKnown = ReadAttribute(Character, DeathHealthTag, false, Health);
	if (bHealthKnown && Health > 0.0)
	{
		bSeenAlive = true;
	}
	// The pack's attributes read 0 for the first frames of a PIE (KI-081): a health of 0 counts as a death only after the boss has been seen alive, or the clip would play on a living boss at the start of the level.
	const bool bDead = bHealthKnown && Health <= 0.0 && bSeenAlive;
	if (State == EState::Alive)
	{
		if (!bDead)
		{
			CaptureMeshPlacement(Character);
			if (DeathMode == ERPGBossDeathMode::PackMontage)
			{
				PollPack(Now);
			}
			return;
		}
		BeginDeath(Character, Now);
	}
	else if (bHealthKnown && !bDead)
	{
		KeepPhysicsOff(Character); // a ragdoll the pack switched on in the dying window must not outlive the state (the boss is only reset if it is not destroyed meanwhile)
		EndDeathState(Character, TEXT("health is back, the encounter was reset"));
		return;
	}
	TickDeath(Character, Now);
}

void URPGBossDeath::BeginDeath(ACharacter* Character, double Now)
{
	URPGBossDormantWake::StopFor(GetOwner(), TEXT("death"));
	State = EState::Dying;
	DeathTime = Now;
	bPoseHeld = false;
	RestartsThisDeath = 0;
	++DeathCount;
	CaptureRemainsTransform(Character);
	UStaticMesh* RemainsMesh = nullptr;
	UMaterialInterface* RemainsMaterial = nullptr;
	UNiagaraSystem* RemainsBurst = nullptr;
	ARPGBossRemains::PreloadAssets(RemainsMesh, RemainsMaterial, RemainsBurst);
	LoadedRemainsMesh = RemainsMesh;
	LoadedRemainsMaterial = RemainsMaterial;
	LoadedRemainsBurst = RemainsBurst;
	UE_LOG(LogRPGBossDeath, Log, TEXT("%s: death seen (health 0), mode %s"), *Character->GetName(), *GetDeathModeName());
	if (DeathMode == ERPGBossDeathMode::OwnClip)
	{
		// The clip starts in this frame. Whatever the pack does next (its ragdoll starts in the same frame) is handled by the guard in TickDeath, never by waiting.
		bGuardActive = StartOwnClip(Character, 0.f);
		if (!bGuardActive)
		{
			UE_LOG(LogRPGBossDeath, Warning, TEXT("%s: the death clip did not play, the pack's own death runs alone"), *Character->GetName());
		}
	}
	else
	{
		ClipMontage = LoadedMontage.Get(); // the pack plays it; only the guard (bGuardPackDeath) ever touches it
		bGuardActive = bGuardPackDeath;
		if (PackSetCount == 0)
		{
			UE_LOG(LogRPGBossDeath, Warning, TEXT("%s: the pack's DeathMontages was never set (%s): the pack plays its own death"), *Character->GetName(), *LastPackResult);
		}
	}
}

void URPGBossDeath::EndDeathState(ACharacter* Character, const TCHAR* Why)
{
	ARPGBossRemains::DestroyForWorld(GetWorld());
	UE_LOG(LogRPGBossDeath, Log, TEXT("%s: death state ended (%s), after %.2f s, pose held %d"), *Character->GetName(), Why, GetDeathAge(), bPoseHeld ? 1 : 0);
	UAnimMontage* Montage = ClipMontage.Get();
	UAnimInstance* Anim = Character->GetMesh() ? Character->GetMesh()->GetAnimInstance() : nullptr;
	if (Montage && Anim && (DeathMode == ERPGBossDeathMode::OwnClip || bPoseHeld))
	{
		Anim->Montage_Stop(0.2f, Montage); // only the montage this component plays or froze, never the others
	}
	ClipMontage = nullptr;
	State = EState::Alive;
	DeathTime = -1.0;
	bPoseHeld = false;
	bGuardActive = false;
	NextPackPoll = 0.0;
}

void URPGBossDeath::TickDeath(ACharacter* Character, double Now)
{
	CaptureRemainsTransform(Character);
	const double Age = Now - DeathTime;
	if (State == EState::Dying && Age >= DyingSeconds)
	{
		State = EState::Dead;
		UE_LOG(LogRPGBossDeath, Log, TEXT("%s: dead after %.2f s (pose held %d, physics switched off %d times)"), *Character->GetName(), Age, bPoseHeld ? 1 : 0, PhysicsOffCount);
	}
	if (bGuardActive)
	{
		KeepPhysicsOff(Character);
		KeepClip(Character, Age);
	}
}

bool URPGBossDeath::StartOwnClip(ACharacter* Character, float StartAt)
{
	UAnimSequence* Clip = GetClip();
	if (!Clip)
	{
		return false;
	}
	// A restart (StartAt above 0) joins the pose without a blend; the clip has no blend out: it is frozen at HoldAtSeconds, long before its end.
	UAnimMontage* Montage = RPGBossClips::Play(Character, Clip, StartAt > 0.f ? 0.f : BlendInSeconds, 0.f, 1.f, 1, StartAt);
	if (!Montage)
	{
		return false;
	}
	ClipMontage = Montage;
	++ClipPlayCount;
	if (StartAt >= HoldAtSeconds)
	{
		if (UAnimInstance* Anim = Character->GetMesh() ? Character->GetMesh()->GetAnimInstance() : nullptr)
		{
			Anim->Montage_Pause(Montage);
			bPoseHeld = true;
			++PoseHoldCount;
		}
	}
	return true;
}

void URPGBossDeath::KeepPhysicsOff(ACharacter* Character)
{
	USkeletalMeshComponent* Mesh = Character->GetMesh();
	if (!Mesh || !Mesh->IsAnySimulatingPhysics())
	{
		return;
	}
	// The pack's ragdoll ability switched the simulation on (it throws the body at PhysicsVelocitySpeed): off again, bodies and component, and the mesh back where it sits on the capsule.
	Mesh->SetAllBodiesSimulatePhysics(false);
	Mesh->SetSimulatePhysics(false);
	USceneComponent* Parent = MeshParent.Get();
	if (bMeshPlacementKnown && Parent)
	{
		if (Mesh->GetAttachParent() != Parent)
		{
			Mesh->AttachToComponent(Parent, FAttachmentTransformRules::KeepRelativeTransform, MeshSocket);
		}
		Mesh->SetRelativeLocationAndRotation(MeshRelativeLocation, MeshRelativeRotation, false, nullptr, ETeleportType::TeleportPhysics);
	}
	++PhysicsOffCount;
	if (PhysicsOffCount == 1 || PhysicsOffCount % 60 == 0)
	{
		UE_LOG(LogRPGBossDeath, Log, TEXT("%s: the pack's ragdoll switched the mesh to physics %.2f s after the death: taken out again (%d times so far)"), *Character->GetName(), GetDeathAge(), PhysicsOffCount);
	}
}

void URPGBossDeath::KeepClip(ACharacter* Character, double Age)
{
	UAnimInstance* Anim = Character->GetMesh() ? Character->GetMesh()->GetAnimInstance() : nullptr;
	if (!Anim)
	{
		return;
	}
	UAnimMontage* Montage = ClipMontage.Get();
	if (Montage && Anim->Montage_IsActive(Montage))
	{
		if (!bPoseHeld && Anim->Montage_GetPosition(Montage) >= HoldAtSeconds)
		{
			Anim->Montage_Pause(Montage); // the pose from 2.5 s on is the same to the last frame: it stays
			bPoseHeld = true;
			++PoseHoldCount;
			UE_LOG(LogRPGBossDeath, Log, TEXT("%s: death pose frozen at %.2f s of the clip (%.2f s after the death)"), *Character->GetName(), HoldAtSeconds, Age);
		}
		return;
	}
	if (DeathMode != ERPGBossDeathMode::OwnClip)
	{
		return; // the pack's montage ended on its own: the pack's flow, not ours
	}
	// Something stopped the clip (the pack's death flow, another montage): start it again at the place it should have reached, up to MaxClipRestarts times.
	if (RestartsThisDeath >= MaxClipRestarts)
	{
		if (RestartsThisDeath == MaxClipRestarts)
		{
			++RestartsThisDeath;
			UE_LOG(LogRPGBossDeath, Warning, TEXT("%s: the death clip was stopped %d times, not started again (something keeps replacing it)"), *Character->GetName(), MaxClipRestarts);
		}
		return;
	}
	++RestartsThisDeath;
	++ClipRestartCount;
	const float StartAt = FMath::Clamp(static_cast<float>(Age), 0.f, HoldAtSeconds);
	UE_LOG(LogRPGBossDeath, Log, TEXT("%s: the death clip was stopped at %.2f s after the death, started again at %.2f s of the clip (%d)"), *Character->GetName(), Age, StartAt, RestartsThisDeath);
	StartOwnClip(Character, StartAt);
}
