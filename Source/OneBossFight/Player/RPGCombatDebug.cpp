// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGCombatDebug.h"
#include "Player/RPGAttackTracker.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossHealPunish.h"
#include "Player/RPGBossLowSweep.h"
#include "Player/RPGDamageResolver.h"
#include "Player/RPGTraceAudit.h"
#include "Player/RPGBossPhases.h"
#include "Player/RPGBossPosture.h"
#include "Player/RPGBossStagger.h"
#include "Player/RPGDodgeTiming.h"
#include "Player/RPGBossClips.h"
#include "Player/RPGIFrameMonitor.h"
#include "Pack/RPGBlueprintCall.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/BlueprintGeneratedClass.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"

#if !UE_BUILD_SHIPPING
DEFINE_LOG_CATEGORY_STATIC(LogRPGDebug, Log, All); // every use is inside a non-Shipping block: the Shipping binary carries no debug log category and no rpg.Debug variable (Gate 4 G4-3, Scripts/CheckShippingBinary.py)
#endif

using namespace RPGPack;

#if !UE_BUILD_SHIPPING
static TAutoConsoleVariable<int32> CVarRPGDebug(TEXT("rpg.Debug"), 0, TEXT("Combat debug: 0 off, 1 on-screen overlay, 2 overlay plus one log line per second (LogRPGDebug)."), ECVF_Default);
#endif

namespace
{
	FString MontageLine(const AActor* Actor)
	{
		const ACharacter* Character = Cast<ACharacter>(Actor);
		const UAnimInstance* Anim = Character && Character->GetMesh() ? Character->GetMesh()->GetAnimInstance() : nullptr;
		UAnimMontage* Montage = Anim ? Anim->GetCurrentActiveMontage() : nullptr;
		if (!Montage)
		{
			return TEXT("montage none");
		}
		return FString::Printf(TEXT("montage %s at %.2f of %.2f s, rate %.2f"), *Montage->GetName(), Anim->Montage_GetPosition(Montage), Montage->GetPlayLength(), Anim->Montage_GetEffectivePlayRate(Montage));
	}

	FString AttributeLine(const AActor* Actor, const TCHAR* Tag, const TCHAR* Label)
	{
		double Now = 0.0, Max = 0.0;
		if (ReadAttribute(Actor, Tag, false, Now) && ReadAttribute(Actor, Tag, true, Max))
		{
			return FString::Printf(TEXT("%s %.0f/%.0f"), Label, Now, Max);
		}
		return FString::Printf(TEXT("%s ?"), Label);
	}
}

URPGCombatDebug::URPGCombatDebug()
{
#if UE_BUILD_SHIPPING
	PrimaryComponentTick.bCanEverTick = false;
	PrimaryComponentTick.bStartWithTickEnabled = false;
#else
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.bStartWithTickEnabled = true;
#endif
}

TArray<FString> URPGCombatDebug::BuildLines() const
{
	TArray<FString> Lines;
	const AActor* Boss = GetOwner();
	if (!Boss)
	{
		return Lines;
	}
	const URPGBossEncounter* Encounter = Boss->FindComponentByClass<URPGBossEncounter>();
	const URPGBossPhases* Phases = Boss->FindComponentByClass<URPGBossPhases>();
	const URPGBossStagger* Stagger = Boss->FindComponentByClass<URPGBossStagger>();
	const APawn* Player = UGameplayStatics::GetPlayerPawn(this, 0);

	FString State = TEXT("Combat");
	double BossHealth = 1.0;
	if (ReadAttribute(Boss, TEXT("Attribute.Health"), false, BossHealth) && BossHealth <= 0.0)
	{
		State = TEXT("Dead");
	}
	else if (Encounter && Encounter->IsDormant())
	{
		State = TEXT("Dormant");
	}
	else if (Phases && Phases->IsInTransition())
	{
		State = TEXT("PhaseTransition");
	}
	else if (Stagger && Stagger->IsStaggered())
	{
		State = TEXT("Staggered");
	}
	Lines.Add(FString::Printf(TEXT("BOSS %s  state %s  phase %d  generation %d  resets %d"), *Boss->GetName(), *State, Phases && Phases->IsPhaseTwo() ? 2 : 1, Encounter ? Encounter->GetGeneration() : 0, Encounter ? Encounter->GetResetCount() : 0));
	Lines.Add(FString::Printf(TEXT("  %s  %s  stance breaks %d  critical window %d"), *AttributeLine(Boss, TEXT("Attribute.Health"), TEXT("health")), *AttributeLine(Boss, TEXT("Attribute.Poise"), TEXT("poise")),
		Stagger ? Stagger->GetStaggerCount() : 0, Stagger ? Stagger->IsCriticalWindowOpen() : 0));
	if (Stagger)
	{
		Lines.Add(FString::Printf(TEXT("  riposte armed %d  accepted %d  rejected %d  last press: %s"), Stagger->IsRiposteArmed(), Stagger->GetRiposteCount(), Stagger->GetRiposteRejectCount(), *Stagger->GetLastRiposteResult()));
		// Freeze 919 and 922: the stance break cooldown, what the break gate dropped and why, the queued transition and the posture hold.
		Lines.Add(FString::Printf(TEXT("  stance break cooldown %.1f s  breaks dropped: transition %d dead %d dormant %d staggered %d cooldown %d  last: %s"), Stagger->GetCooldownRemaining(), Stagger->GetDroppedBreakCount(TEXT("transition")),
			Stagger->GetDroppedBreakCount(TEXT("dead")), Stagger->GetDroppedBreakCount(TEXT("dormant")), Stagger->GetDroppedBreakCount(TEXT("staggered")), Stagger->GetDroppedBreakCount(TEXT("cooldown")), *Stagger->GetLastBreakResult()));
		const URPGBossPosture* HoldPosture = Boss->FindComponentByClass<URPGBossPosture>();
		Lines.Add(FString::Printf(TEXT("  transition queued %d  last start %.1f s  queued starts %d  posture hold %s  ignored posture hits %d"), Phases && Phases->IsTransitionQueued(), Phases ? Phases->GetLastTransitionStartTime() : -1.0,
			Phases ? Phases->GetQueuedStartCount() : 0, HoldPosture ? *HoldPosture->GetHoldName() : TEXT("-"), HoldPosture ? HoldPosture->GetSuppressedDrainCount() : 0));
	}
	if (const URPGBossPosture* PostureComponent = Boss->FindComponentByClass<URPGBossPosture>())
	{
		const double Now = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
		Lines.Add(FString::Printf(TEXT("  posture %.0f/%.0f  drains %d  last drain %.1f s ago  regen %.0f s delay, %.0f/s%s"), PostureComponent->GetPosture(), PostureComponent->GetMaxPosture(), PostureComponent->GetDrainCount(),
			PostureComponent->GetLastDrainTime() >= 0.0 ? Now - PostureComponent->GetLastDrainTime() : -1.0, PostureComponent->RegenDelaySeconds, PostureComponent->RegenPerSecond, PostureComponent->IsConfigured() ? TEXT("") : TEXT("  (not configured)")));
	}
	Lines.Add(FString::Printf(TEXT("  %s"), *MontageLine(Boss)));
	if (const URPGAttackTracker* Tracker = Boss->FindComponentByClass<URPGAttackTracker>())
	{
		Lines.Add(FString::Printf(TEXT("  attack %s  phase %s  instance %d  commits %d  interrupted %d  committed yaw %.0f  drift %.1f"), *Tracker->GetCurrentMove().ToString(), *Tracker->GetPhaseName(), Tracker->GetAttackInstance(),
			Tracker->GetCommitCount(), Tracker->GetInterruptedCount(), Tracker->GetCommittedYaw(), Tracker->GetMaxYawDriftAfterCommit()));
	}
	if (const URPGTraceAudit* TraceAudit = Boss->FindComponentByClass<URPGTraceAudit>())
	{
		Lines.Append(TraceAudit->BuildLines());
	}
	if (const URPGBossLowSweep* Sweep = Boss->FindComponentByClass<URPGBossLowSweep>())
	{
		Lines.Add(FString::Printf(TEXT("  A4 blade %s angle %.0f  sweeps %d  hits %d  jumped %d  invulnerable %d  blocked %d"), Sweep->IsBladeActive() ? TEXT("ACTIVE") : TEXT("idle"), Sweep->GetBladeAngle(), Sweep->GetSweepCount(), Sweep->GetHitCount(),
			Sweep->GetJumpedCount(), Sweep->GetInvulnerableCount(), Sweep->GetBlockedCount()));
	}
	if (const URPGBossHealPunish* Punish = Boss->FindComponentByClass<URPGBossHealPunish>())
	{
		Lines.Add(FString::Printf(TEXT("  A5 heal punish %s  cooldown %.1f s  heals %d  accepted %d  released %d  discarded busy %d range %d sight %d cooldown %d pending %d  javelin hit %d dodged %d world %d"), Punish->IsPending() ? TEXT("PENDING") : TEXT("ready"),
			Punish->GetCooldownRemaining(), Punish->GetHealEventCount(), Punish->GetAcceptedCount(), Punish->GetReleasedCount(), Punish->GetDiscardedBusyCount(), Punish->GetDiscardedRangeCount(), Punish->GetDiscardedSightCount(),
			Punish->GetDiscardedCooldownCount(), Punish->GetDiscardedPendingCount(), Punish->GetJavelinHitCount(), Punish->GetJavelinDodgedCount(), Punish->GetJavelinWorldCount()));
	}
	if (const URPGDamageResolver* Resolver = Boss->FindComponentByClass<URPGDamageResolver>())
	{
		Lines.Add(Resolver->BuildSummaryLine());
	}
	if (const ACharacter* BossCharacter = Cast<ACharacter>(Boss))
	{
		const UCharacterMovementComponent* Movement = BossCharacter->GetCharacterMovement();
		Lines.Add(FString::Printf(TEXT("  speed %.0f cm/s  distance to player %.0f cm"), Movement ? Movement->Velocity.Size2D() : 0.f, Player ? FVector::Dist2D(Boss->GetActorLocation(), Player->GetActorLocation()) : -1.f));
	}
	if (Player)
	{
		const URPGDodgeTiming* Dodge = Player->FindComponentByClass<URPGDodgeTiming>();
		Lines.Add(FString::Printf(TEXT("PLAYER  dodge %s  presses %d  forced rolls %d  ignored %d  last gap %.3f s (window %.2f)"), Dodge ? *Dodge->GetStageName() : TEXT("?"), Dodge ? Dodge->GetPressCount() : 0,
			Dodge ? Dodge->GetForcedRollCount() : 0, Dodge ? Dodge->GetIgnoredPressCount() : 0, Dodge ? Dodge->GetLastPressGap() : -1.0, Dodge ? Dodge->DoubleTapWindow : 0.f));
		Lines.Add(FString::Printf(TEXT("  %s  %s  %s"), *AttributeLine(Player, TEXT("Attribute.Health"), TEXT("health")), *AttributeLine(Player, TEXT("Attribute.Stamina"), TEXT("stamina")), *MontageLine(Player)));
		if (const URPGIFrameMonitor* IFrames = Player->FindComponentByClass<URPGIFrameMonitor>())
		{
			Lines.Add(FString::Printf(TEXT("  IFRAME  invulnerable %s  source %s  records %d  early drops %d  stale cleared %d  death clears %d  reset clears %d"), IFrames->IsInvulnerableNow() ? TEXT("ON") : TEXT("off"), *IFrames->GetSourceText(),
				IFrames->GetRecordCount(), IFrames->GetUnexpectedDropCount(), IFrames->GetStaleClearedCount(), IFrames->GetDeathClearCount(), IFrames->GetResetClearCount()));
		}
	}
	return Lines;
}

static void DumpAbilitiesOf(const AActor* Actor)
{
#if !UE_BUILD_SHIPPING
	UObject* Asc = FindComponentByClassName(Actor, TEXT("BP_AdvancedAbilitySystemComponent_C"));
	const FArrayProperty* Created = Asc ? FindFProperty<FArrayProperty>(Asc->GetClass(), TEXT("CreatedAbilities")) : nullptr;
	const FObjectProperty* Inner = Created ? CastField<FObjectProperty>(Created->Inner) : nullptr;
	if (!Inner)
	{
		UE_LOG(LogRPGDebug, Warning, TEXT("DumpAbilities: no ability list on %s"), *GetNameSafe(Actor));
		return;
	}
	FScriptArrayHelper Abilities(Created, Created->ContainerPtrToValuePtr<void>(Asc));
	for (int32 Index = 0; Index < Abilities.Num(); ++Index)
	{
		UObject* Ability = Inner->GetObjectPropertyValue(Abilities.GetRawPtr(Index));
		if (!Ability)
		{
			continue;
		}
		UE_LOG(LogRPGDebug, Log, TEXT("ABILITY %s"), *Ability->GetClass()->GetName());
		for (TFieldIterator<FProperty> It(Ability->GetClass()); It; ++It)
		{
			// Blueprint variables only: skip what native classes define (their owner is a native class).
			if (!Cast<UBlueprintGeneratedClass>(It->GetOwnerClass()))
			{
				continue;
			}
			FString Value;
			const void* Ptr = It->ContainerPtrToValuePtr<void>(Ability);
			It->ExportTextItem_Direct(Value, Ptr, nullptr, nullptr, PPF_None);
			UE_LOG(LogRPGDebug, Log, TEXT("   %s (%s) = %s"), *It->GetName(), *It->GetClass()->GetName(), *Value.Left(500));
		}
	}
#endif
}

#if !UE_BUILD_SHIPPING
static void DumpObjectVariables(const UObject* Object, int32 Depth, const FString& Indent, TSet<const UObject*>& Seen)
{
	if (!Object || Seen.Contains(Object))
	{
		return;
	}
	Seen.Add(Object);
	UE_LOG(LogRPGDebug, Log, TEXT("%sOBJECT %s (%s)"), *Indent, *Object->GetName(), *Object->GetClass()->GetName());
	for (TFieldIterator<FProperty> It(Object->GetClass()); It; ++It)
	{
		// Blueprint variables only: skip what native classes define.
		if (!Cast<UBlueprintGeneratedClass>(It->GetOwnerClass()) || It->GetName() == TEXT("UberGraphFrame"))
		{
			continue;
		}
		FString Value;
		const void* Ptr = It->ContainerPtrToValuePtr<void>(Object);
		It->ExportTextItem_Direct(Value, Ptr, nullptr, nullptr, PPF_None);
		UE_LOG(LogRPGDebug, Log, TEXT("%s   %s (%s) = %s"), *Indent, *It->GetName(), *It->GetClass()->GetName(), *Value.Left(300));
		if (const FMulticastDelegateProperty* Delegate = CastField<FMulticastDelegateProperty>(*It))
		{
			// The signature of an event dispatcher: what a listener would receive.
			FString Params;
			if (const UFunction* Signature = Delegate->SignatureFunction)
			{
				for (TFieldIterator<FProperty> P(Signature); P && P->HasAnyPropertyFlags(CPF_Parm); ++P)
				{
					const FObjectPropertyBase* ObjectParam = CastField<FObjectPropertyBase>(*P);
					Params += FString::Printf(TEXT("%s%s:%s"), Params.IsEmpty() ? TEXT("") : TEXT(", "), *P->GetName(), ObjectParam && ObjectParam->PropertyClass ? *ObjectParam->PropertyClass->GetName() : *P->GetClass()->GetName());
				}
			}
			UE_LOG(LogRPGDebug, Log, TEXT("%s      SIGNATURE %s(%s)"), *Indent, *It->GetName(), *Params);
		}
		if (Depth <= 0)
		{
			continue;
		}
		if (const FObjectProperty* Reference = CastField<FObjectProperty>(*It))
		{
			if (const UObject* Child = Reference->GetObjectPropertyValue(Ptr))
			{
				if (!Child->IsA<UClass>() && !Child->IsA<UWorld>() && !Child->IsA<AActor>() && !Child->IsA<UActorComponent>())
				{
					DumpObjectVariables(Child, Depth - 1, Indent + TEXT("      "), Seen);
				}
			}
		}
		else if (const FArrayProperty* Array = CastField<FArrayProperty>(*It))
		{
			if (const FObjectProperty* Inner = CastField<FObjectProperty>(Array->Inner))
			{
				FScriptArrayHelper Helper(Array, Ptr);
				for (int32 Index = 0; Index < Helper.Num() && Index < 12; ++Index)
				{
					if (const UObject* Child = Inner->GetObjectPropertyValue(Helper.GetRawPtr(Index)))
					{
						if (!Child->IsA<UClass>() && !Child->IsA<AActor>())
						{
							DumpObjectVariables(Child, Depth - 1, Indent + TEXT("      "), Seen);
						}
					}
				}
			}
		}
	}
}
#endif

void URPGCombatDebug::DumpObject(UObject* Object, int32 Depth) const
{
#if !UE_BUILD_SHIPPING
	TSet<const UObject*> Seen;
	DumpObjectVariables(Object, FMath::Clamp(Depth, 0, 4), FString(), Seen);
#endif
}

void URPGCombatDebug::DumpAbilities() const
{
	DumpAbilitiesOf(GetOwner());
}

void URPGCombatDebug::DumpPlayerAbilities() const
{
	DumpAbilitiesOf(UGameplayStatics::GetPlayerPawn(this, 0));
}

void URPGCombatDebug::DumpPlayerFunctions() const
{
	DumpFunctionsOf(UGameplayStatics::GetPlayerPawn(this, 0));
}

void URPGCombatDebug::DumpBossFunctions() const
{
	DumpFunctionsOf(GetOwner());
}

void URPGCombatDebug::DumpFunctionsOf(const AActor* Player) const
{
#if !UE_BUILD_SHIPPING
	if (!Player)
	{
		return;
	}
	auto DumpClass = [](const UObject* Object)
	{
		for (TFieldIterator<UFunction> It(Object->GetClass(), EFieldIteratorFlags::IncludeSuper); It; ++It)
		{
			if (!Cast<UBlueprintGeneratedClass>(It->GetOwnerClass()))
			{
				continue;
			}
			FString Params;
			for (TFieldIterator<FProperty> P(*It); P && P->HasAnyPropertyFlags(CPF_Parm); ++P)
			{
				Params += FString::Printf(TEXT("%s%s:%s"), Params.IsEmpty() ? TEXT("") : TEXT(", "), *P->GetName(), *P->GetClass()->GetName());
			}
			UE_LOG(LogRPGDebug, Log, TEXT("FUNCTION %s::%s(%s)"), *Object->GetClass()->GetName(), *It->GetName(), *Params);
		}
	};
	DumpClass(Player);
	TInlineComponentArray<UActorComponent*> Components(Player);
	for (const UActorComponent* Component : Components)
	{
		if (Cast<UBlueprintGeneratedClass>(Component->GetClass()))
		{
			DumpClass(Component);
		}
	}
#endif
}

void URPGCombatDebug::DumpAttributes() const
{
#if !UE_BUILD_SHIPPING
	UObject* Attributes = FindComponentByClassName(GetOwner(), TEXT("BP_AttributesComponent_C"));
	if (!Attributes)
	{
		return;
	}
	for (TFieldIterator<FArrayProperty> ArrayIt(Attributes->GetClass()); ArrayIt; ++ArrayIt)
	{
		const FObjectProperty* Inner = CastField<FObjectProperty>(ArrayIt->Inner);
		if (!Inner)
		{
			continue;
		}
		FScriptArrayHelper Array(*ArrayIt, ArrayIt->ContainerPtrToValuePtr<void>(Attributes));
		for (int32 Index = 0; Index < Array.Num(); ++Index)
		{
			UObject* Object = Inner->GetObjectPropertyValue(Array.GetRawPtr(Index));
			if (!Object)
			{
				continue;
			}
			UE_LOG(LogRPGDebug, Log, TEXT("ATTRIBUTE OBJECT %s in %s"), *Object->GetClass()->GetName(), *ArrayIt->GetName());
			for (TFieldIterator<FProperty> It(Object->GetClass()); It; ++It)
			{
				if (!Cast<UBlueprintGeneratedClass>(It->GetOwnerClass()))
				{
					continue;
				}
				FString Value;
				It->ExportTextItem_Direct(Value, It->ContainerPtrToValuePtr<void>(Object), nullptr, nullptr, PPF_None);
				UE_LOG(LogRPGDebug, Log, TEXT("   %s (%s) = %s"), *It->GetName(), *It->GetClass()->GetName(), *Value.Left(200));
			}
		}
	}
#endif
}

void URPGCombatDebug::DebugSetBossPosture(float Value) const
{
#if !UE_BUILD_SHIPPING
	if (URPGBossPosture* Posture = GetOwner()->FindComponentByClass<URPGBossPosture>())
	{
		Posture->SetPostureForTest(Value);
	}
#endif
}

void URPGCombatDebug::DebugDrainBossPosture(float Amount) const
{
#if !UE_BUILD_SHIPPING
	if (URPGBossPosture* Posture = GetOwner()->FindComponentByClass<URPGBossPosture>())
	{
		Posture->ApplyPostureDamage(Amount, TEXT("debug"));
	}
#endif
}

void URPGCombatDebug::DebugSetBossHealthFraction(float Fraction) const
{
#if !UE_BUILD_SHIPPING
	double Max = 0.0;
	if (ReadAttribute(GetOwner(), TEXT("Attribute.Health"), true, Max))
	{
		WriteAttribute(GetOwner(), TEXT("Attribute.Health"), Max * FMath::Clamp(Fraction, 0.f, 1.f));
	}
#endif
}

void URPGCombatDebug::DebugKillBoss() const
{
#if !UE_BUILD_SHIPPING
	WriteAttribute(GetOwner(), TEXT("Attribute.Health"), 0.0);
	TryActivateByTag(GetOwner(), TEXT("Ability.Dead"), true); // writing the attribute alone does not start the pack's death ability
#endif
}

void URPGCombatDebug::DebugSpawnWall(FVector Location, FRotator Rotation, FVector Scale)
{
#if !UE_BUILD_SHIPPING
	AStaticMeshActor* Wall = GetWorld() ? GetWorld()->SpawnActor<AStaticMeshActor>(Location, Rotation) : nullptr;
	UStaticMesh* Cube = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
	if (!Wall || !Cube)
	{
		UE_LOG(LogRPGDebug, Warning, TEXT("DebugSpawnWall: could not spawn the wall"));
		return;
	}
	Wall->SetMobility(EComponentMobility::Movable);
	Wall->GetStaticMeshComponent()->SetStaticMesh(Cube);
	Wall->SetActorScale3D(Scale);
	TestWalls.Add(Wall);
#endif
}

void URPGCombatDebug::DebugClearWalls()
{
#if !UE_BUILD_SHIPPING
	for (AActor* Wall : TestWalls)
	{
		if (Wall)
		{
			Wall->Destroy();
		}
	}
	TestWalls.Reset();
#endif
}

#if !UE_BUILD_SHIPPING
void URPGCombatDebug::DebugAddSkeletalPiece(USkeletalMesh* Piece)
{
	ACharacter* Boss = Cast<ACharacter>(GetOwner());
	if (!Boss || !Boss->GetMesh() || !Piece)
	{
		return;
	}
	USkeletalMeshComponent* Component = NewObject<USkeletalMeshComponent>(Boss, *FString::Printf(TEXT("RPGDebugPiece_%s"), *Piece->GetName()));
	Component->SetSkeletalMesh(Piece);
	Component->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Component->RegisterComponent();
	Component->AttachToComponent(Boss->GetMesh(), FAttachmentTransformRules::SnapToTargetNotIncludingScale);
	Component->SetLeaderPoseComponent(Boss->GetMesh());
}

void URPGCombatDebug::DebugAttachTestMesh(UStaticMesh* Mesh, FName Socket, FRotator RelativeRotation, FVector RelativeLocation)
{
	ACharacter* Boss = Cast<ACharacter>(GetOwner());
	if (!Boss || !Boss->GetMesh())
	{
		return;
	}
	if (!TestMeshComponent)
	{
		TestMeshComponent = NewObject<UStaticMeshComponent>(Boss, TEXT("RPGDebugTestMesh"));
		TestMeshComponent->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		TestMeshComponent->RegisterComponent();
		TestMeshComponent->AttachToComponent(Boss->GetMesh(), FAttachmentTransformRules::SnapToTargetNotIncludingScale, Socket);
	}
	TestMeshComponent->SetStaticMesh(Mesh);
	TestMeshComponent->SetRelativeRotation(RelativeRotation);
	TestMeshComponent->SetRelativeLocation(RelativeLocation);
}
#else
void URPGCombatDebug::DebugAddSkeletalPiece(USkeletalMesh* Piece)
{
}

void URPGCombatDebug::DebugAttachTestMesh(UStaticMesh* Mesh, FName Socket, FRotator RelativeRotation, FVector RelativeLocation)
{
}
#endif

void URPGCombatDebug::DebugSetPlayerHealth(float Value) const
{
#if !UE_BUILD_SHIPPING
	if (const APawn* Player = UGameplayStatics::GetPlayerPawn(this, 0))
	{
		WriteAttribute(Player, TEXT("Attribute.Health"), Value);
	}
#endif
}

namespace
{
	FString ActiveMontageAnimName(const ACharacter* Character)
	{
		const UAnimInstance* Anim = Character && Character->GetMesh() ? Character->GetMesh()->GetAnimInstance() : nullptr;
		return Anim ? RPGBossClips::MontageAnimName(Anim->GetCurrentActiveMontage()) : FString();
	}
}

FString URPGCombatDebug::DebugBossMontageAnimName() const
{
	return ActiveMontageAnimName(Cast<ACharacter>(GetOwner()));
}

FString URPGCombatDebug::DebugPlayerMontageAnimName() const
{
	return ActiveMontageAnimName(Cast<ACharacter>(UGameplayStatics::GetPlayerPawn(this, 0)));
}

TArray<FString> URPGCombatDebug::DebugBossMontageInstances() const
{
	TArray<FString> Lines;
#if !UE_BUILD_SHIPPING
	const ACharacter* Boss = Cast<ACharacter>(GetOwner());
	const USkeletalMeshComponent* Mesh = Boss ? Boss->GetMesh() : nullptr;
	const UAnimInstance* Anim = Mesh ? Mesh->GetAnimInstance() : nullptr;
	if (!Mesh || !Anim)
	{
		return Lines;
	}

	const FVector RelativeLocation = Mesh->GetRelativeLocation();
	const FRotator RelativeRotation = Mesh->GetRelativeRotation();
	Lines.Add(FString::Printf(TEXT("mesh relative loc %.2f %.2f %.2f rot %.2f %.2f %.2f"), RelativeLocation.X, RelativeLocation.Y, RelativeLocation.Z, RelativeRotation.Roll, RelativeRotation.Pitch, RelativeRotation.Yaw));
	for (const FAnimMontageInstance* Instance : Anim->MontageInstances)
	{
		if (!Instance)
		{
			continue;
		}
		Lines.Add(FString::Printf(TEXT("montage %s weight %.3f pos %.3f playing %d stopped %d rootMotionDisabled %d"), *GetNameSafe(Instance->Montage), Instance->GetWeight(), Instance->GetPosition(), Instance->IsPlaying() ? 1 : 0, Instance->IsStopped() ? 1 : 0, Instance->IsRootMotionDisabled() ? 1 : 0));
	}
#endif
	return Lines;
}

void URPGCombatDebug::DebugRefillPlayer() const
{
#if !UE_BUILD_SHIPPING
	if (const APawn* Player = UGameplayStatics::GetPlayerPawn(this, 0))
	{
		for (const TCHAR* Tag : {TEXT("Attribute.Health"), TEXT("Attribute.Stamina")})
		{
			double Max = 0.0;
			if (ReadAttribute(Player, Tag, true, Max))
			{
				WriteAttribute(Player, Tag, Max);
			}
		}
	}
#endif
}

void URPGCombatDebug::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
#if !UE_BUILD_SHIPPING
	const int32 Mode = CVarRPGDebug.GetValueOnGameThread();
	if (Mode <= 0 || !GEngine)
	{
		return;
	}
	const TArray<FString> Lines = BuildLines();
	for (int32 Index = 0; Index < Lines.Num(); ++Index)
	{
		// Fixed keys replace the previous frame's line instead of stacking.
		GEngine->AddOnScreenDebugMessage(static_cast<uint64>(0x52504700) + Index, 0.f, Index == 0 || Lines[Index].StartsWith(TEXT("PLAYER")) ? FColor::Yellow : FColor::White, Lines[Index]);
	}
	const double Now = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
	if (Mode >= 2 && Now >= NextLog)
	{
		NextLog = Now + 1.0;
		for (const FString& Line : Lines)
		{
			UE_LOG(LogRPGDebug, Log, TEXT("%s"), *Line);
		}
	}
#endif
}
