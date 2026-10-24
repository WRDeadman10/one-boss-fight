// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGHitIntake.h"
#include "Pack/RPGBlueprintCall.h"
#include "Player/RPGBossBleed.h"
#include "Player/RPGBossPosture.h"
#include "Player/RPGPlayerMovesSubsystem.h"
#include "Player/RPGSwingTracker.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Misc/PackageName.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "TimerManager.h"
#include "UObject/UnrealType.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGHitIntake, Log, All);

using namespace RPGPack;

namespace
{
	/** A Blueprint variable of an object by its exact name (the pack's names carry spaces and question marks). */
	const FProperty* Find(const UObject* Object, const TCHAR* Name)
	{
		return Object ? Object->GetClass()->FindPropertyByName(FName(Name)) : nullptr;
	}

	UObject* ReadObject(const UObject* Object, const TCHAR* Name)
	{
		const FObjectProperty* Property = CastField<FObjectProperty>(Find(Object, Name));
		return Property ? Property->GetObjectPropertyValue(Property->ContainerPtrToValuePtr<void>(Object)) : nullptr;
	}

	bool ReadBool(const UObject* Object, const TCHAR* Name, bool bFallback = false)
	{
		const FBoolProperty* Property = CastField<FBoolProperty>(Find(Object, Name));
		return Property ? Property->GetPropertyValue_InContainer(Object) : bFallback;
	}

	int32 ReadByte(const UObject* Object, const TCHAR* Name, int32 Fallback = -1)
	{
		const FProperty* Property = Find(Object, Name);
		if (const FByteProperty* Byte = CastField<FByteProperty>(Property))
		{
			return Byte->GetPropertyValue_InContainer(Object);
		}
		if (const FEnumProperty* Enum = CastField<FEnumProperty>(Property))
		{
			return static_cast<int32>(Enum->GetUnderlyingProperty()->GetSignedIntPropertyValue(Enum->ContainerPtrToValuePtr<void>(Object)));
		}
		return Fallback;
	}

	float ReadFloat(const UObject* Object, const TCHAR* Name, float Fallback = -1.f)
	{
		const FNumericProperty* Property = CastField<FNumericProperty>(Find(Object, Name));
		return Property ? static_cast<float>(Property->GetFloatingPointPropertyValue(Property->ContainerPtrToValuePtr<void>(Object))) : Fallback;
	}

	/** The trace target of the player's collision component that is doing the swing now: the first with collision enabled, else the first that holds hit data. */
	UObject* FindActiveTarget(const UObject* Collision)
	{
		const FArrayProperty* Created = CastField<FArrayProperty>(Find(Collision, TEXT("CreatedTargetTypes")));
		const FObjectProperty* Inner = Created ? CastField<FObjectProperty>(Created->Inner) : nullptr;
		if (!Inner)
		{
			return nullptr;
		}
		FScriptArrayHelper Targets(Created, Created->ContainerPtrToValuePtr<void>(Collision));
		UObject* WithData = nullptr;
		for (int32 Index = 0; Index < Targets.Num(); ++Index)
		{
			UObject* Target = Inner->GetObjectPropertyValue(Targets.GetRawPtr(Index));
			if (!Target)
			{
				continue;
			}
			if (ReadBool(Target, TEXT("bCollisionEnabled?")))
			{
				return Target;
			}
			if (!WithData && (ReadObject(Target, TEXT("HitData")) || ReadObject(Target, TEXT("Attack Data"))))
			{
				WithData = Target;
			}
		}
		return WithData;
	}
}

FString FRPGHitRecord::ToString() const
{
	return FString::Printf(TEXT("hit %d at %.2f s: weapon %s, kind %s%s, posture %.0f, stamina %.0f, bleed %.0f%s, attack data %s (power %d, pack poise damage %.0f, from %s), montage %s, %s, bone %s, target %s"), Id, Time, *Weapon.ToString(), RPGAttackKindName(Kind), bAmbiguous ? TEXT(" (shared frame)") : TEXT(""),
		Row.PostureDamage, Row.StaminaCost, Row.BleedBuildup, bRowFound ? TEXT("") : TEXT(" (no row: fallback)"),
		*AttackData.ToString(), AttackPower, PackPoiseDamage, *Source.ToString(), *Montage.ToString(), bAirborne ? TEXT("airborne") : (bAirborneAtStart ? TEXT("grounded, started airborne") : TEXT("grounded")), *HitBone.ToString(), *GetNameSafe(Target.Get()));
}

bool URPGHitIntake::CheckPackNames(FString& OutMissing)
{
	OutMissing.Reset();
	const FString Base = TEXT("/Game/AdvancedARPGCombat/");
	const UClass* Collision = LoadClass<UObject>(nullptr, *(Base + TEXT("AdvancedCombatFramework/CollisionSystem/BP_CollisionComponent.BP_CollisionComponent_C")));
	const UClass* WeaponTarget = LoadClass<UObject>(nullptr, *(Base + TEXT("AdvancedCombatFramework/CoreCombatSystem/Collision/BP_WeaponTraceTarget.BP_WeaponTraceTarget_C")));
	const UClass* HitData = LoadClass<UObject>(nullptr, *(Base + TEXT("AdvancedCombatFramework/CollisionSystem/Objects/BP_HitData.BP_HitData_C")));
	const UClass* AttackData = LoadClass<UObject>(nullptr, *(Base + TEXT("AdvancedCombatFramework/CoreCombatSystem/DataAssets/BP_AttackData.BP_AttackData_C")));
	if (!Collision || !WeaponTarget || !HitData || !AttackData)
	{
		OutMissing = TEXT("the pack's hit classes (BP_CollisionComponent_C, BP_WeaponTraceTarget_C, BP_HitData_C, BP_AttackData_C) could not be loaded");
		return false;
	}
	auto Need = [&OutMissing](const UClass* Class, const TCHAR* Property)
	{
		if (!Class->FindPropertyByName(FName(Property)))
		{
			OutMissing += FString::Printf(TEXT("%s.%s; "), *Class->GetName(), Property);
		}
	};
	Need(WeaponTarget, TEXT("HitData"));
	Need(WeaponTarget, TEXT("Attack Data"));
	Need(WeaponTarget, TEXT("bCollisionEnabled?"));
	Need(Collision, TEXT("CreatedTargetTypes"));
	Need(HitData, TEXT("AttackData"));
	Need(AttackData, TEXT("AttackPower"));
	Need(AttackData, TEXT("PoiseDamage"));
	// OnHit must be an event dispatcher with the one parameter FHitResult.
	const FMulticastDelegateProperty* OnHit = CastField<FMulticastDelegateProperty>(Collision->FindPropertyByName(TEXT("OnHit")));
	int32 ParamCount = 0;
	bool bHitResult = false;
	if (OnHit && OnHit->SignatureFunction)
	{
		for (TFieldIterator<FProperty> It(OnHit->SignatureFunction); It && It->HasAnyPropertyFlags(CPF_Parm); ++It)
		{
			++ParamCount;
			const FStructProperty* Struct = CastField<FStructProperty>(*It);
			bHitResult = Struct && Struct->Struct == TBaseStructure<FHitResult>::Get();
		}
	}
	if (!OnHit || ParamCount != 1 || !bHitResult)
	{
		OutMissing += TEXT("BP_CollisionComponent_C.OnHit(FHitResult); ");
	}
	// The pack's own melee attack data assets that the classifier names (RPGClassifyAttack).
	for (const TCHAR* Name : {TEXT("DefaultMeleeAttackData"), TEXT("StrongMeleeAttackData"), TEXT("ChargedMeleeAttackData"), TEXT("MeleeKnockdownAttackData")})
	{
		if (!FPackageName::DoesPackageExist(Base + TEXT("MeleeCombatSystem/Blueprints/DataAssets/AttackData/") + Name))
		{
			OutMissing += FString::Printf(TEXT("attack data %s; "), Name);
		}
	}
	return OutMissing.IsEmpty();
}

URPGHitIntake::URPGHitIntake()
{
	PrimaryComponentTick.bCanEverTick = true; // every frame: the stance at the start of an attack montage is latched
}

void URPGHitIntake::BeginPlay()
{
	Super::BeginPlay();
	Table = URPGWeaponAttackTable::LoadOrDefault();
	TryBind();
}

void URPGHitIntake::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	Unbind();
	Super::EndPlay(EndPlayReason);
}

void URPGHitIntake::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	// The pack's collision component may not exist yet at the first frame, and a new pawn after a respawn is a new object: look again until bound.
	if (bBound && !BoundCollision.IsValid())
	{
		bBound = false;
	}
	if (!bBound)
	{
		BindRetryTimer += DeltaTime;
		if (BindRetryTimer >= 0.25f)
		{
			BindRetryTimer = 0.f;
			TryBind();
		}
	}
	TrackMontage();
	TrackBossHealth(DeltaTime);
}

void URPGHitIntake::TrackBossHealth(float DeltaTime)
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}
	AActor* Boss = WatchedBoss.Get();
	if (!Boss)
	{
		BossSearchTimer += DeltaTime;
		if (BossSearchTimer < 0.5f)
		{
			return;
		}
		BossSearchTimer = 0.f;
		for (TActorIterator<ACharacter> It(World); It; ++It)
		{
			if (URPGPlayerMovesSubsystem::IsPackBoss(*It))
			{
				Boss = *It;
				WatchedBoss = Boss;
				PrevBossHealth = -1.0;
				break;
			}
		}
		if (!Boss)
		{
			return;
		}
	}
	// Reading a pack attribute is a reflected Blueprint call: every frame only around a weapon hit (HandlePackHit arms it), otherwise ten times a second.
	HealthSampleTimer += DeltaTime;
	if (World->GetTimeSeconds() > HotUntil && HealthSampleTimer < 0.1f)
	{
		return;
	}
	HealthSampleTimer = 0.f;
	double Health = 0.0;
	if (!RPGPack::ReadAttribute(Boss, TEXT("Attribute.Health"), false, Health))
	{
		return;
	}
	if (PrevBossHealth >= 0.0 && Health > PrevBossHealth + 0.5)
	{
		// A gain is an encounter reset (the refill) or a heal: whatever the scaler still holds belongs to the old fight (a pending scaled hit would refund 61 percent of the first loss of the next one).
		Scaler.Reset();
	}
	if (PrevBossHealth >= 0.0 && Health < PrevBossHealth - 0.01)
	{
		const double Adjust = Scaler.OnLoss(World->GetTimeSeconds(), PrevBossHealth - Health);
		if (FMath::Abs(Adjust) > 0.01)
		{
			AdjustBossHealth(Boss, Adjust, TEXT("loss first"));
			RPGPack::ReadAttribute(Boss, TEXT("Attribute.Health"), false, Health);
		}
	}
	PrevBossHealth = Health;
}

void URPGHitIntake::AdjustBossHealth(AActor* Boss, double Adjust, const TCHAR* Why)
{
	double Health = 0.0, MaxHealth = 0.0;
	if (!Boss || !RPGPack::ReadAttribute(Boss, TEXT("Attribute.Health"), false, Health) || !RPGPack::ReadAttribute(Boss, TEXT("Attribute.Health"), true, MaxHealth) || Health <= 0.0)
	{
		return; // a dead boss stays dead: the scaler never revives and never kills
	}
	const double NewHealth = FRPGDamageScaler::Apply(Health, Adjust, MaxHealth);
	if (FMath::Abs(NewHealth - Health) < 0.01)
	{
		return;
	}
	RPGPack::WriteAttribute(Boss, TEXT("Attribute.Health"), NewHealth);
	PrevBossHealth = NewHealth;
	++ScaledHitCount;
	HealthAdjustTotal += NewHealth - Health;
	UE_LOG(LogRPGHitIntake, Log, TEXT("health damage multiplier (%s): boss health %.1f -> %.1f (%+.1f)"), Why, Health, NewHealth, NewHealth - Health);
}

void URPGHitIntake::TrackMontage()
{
	const ACharacter* Character = Cast<ACharacter>(GetOwner());
	const USkeletalMeshComponent* Mesh = Character ? Character->GetMesh() : nullptr;
	const UAnimInstance* Anim = Mesh ? Mesh->GetAnimInstance() : nullptr;
	const UAnimMontage* Montage = Anim ? Anim->GetCurrentActiveMontage() : nullptr;
	if (!Montage)
	{
		TrackedMontage = NAME_None;
		LastMontagePosition = 0.f;
		return;
	}
	const float Position = Anim->Montage_GetPosition(Montage);
	// A new montage, or the same one started again (its position went back): a new attack starts now, in the stance the player is in.
	if (Montage->GetFName() != TrackedMontage || Position + KINDA_SMALL_NUMBER < LastMontagePosition)
	{
		TrackedMontage = Montage->GetFName();
		bTrackedAirborneAtStart = Character->GetCharacterMovement() && Character->GetCharacterMovement()->IsFalling();
	}
	LastMontagePosition = Position;
}

bool URPGHitIntake::TryBind()
{
	if (bBound)
	{
		return true;
	}
	UObject* Collision = FindComponentByClassName(GetOwner(), TEXT("BP_CollisionComponent_C"));
	const FMulticastDelegateProperty* OnHit = Collision ? CastField<FMulticastDelegateProperty>(Collision->GetClass()->FindPropertyByName(TEXT("OnHit"))) : nullptr;
	if (!OnHit)
	{
		return false;
	}
	// Bind only to OnHit(FHitResult): a pack update that changes the signature must not make us write into the wrong memory.
	const UFunction* Signature = OnHit->SignatureFunction;
	int32 ParamCount = 0;
	bool bHitResult = false;
	if (Signature)
	{
		for (TFieldIterator<FProperty> It(Signature); It && It->HasAnyPropertyFlags(CPF_Parm); ++It)
		{
			++ParamCount;
			const FStructProperty* Struct = CastField<FStructProperty>(*It);
			bHitResult = Struct && Struct->Struct == TBaseStructure<FHitResult>::Get();
		}
	}
	if (ParamCount != 1 || !bHitResult)
	{
		if (!bWarnedSignature)
		{
			bWarnedSignature = true;
			UE_LOG(LogRPGHitIntake, Warning, TEXT("%s: the pack's OnHit is not OnHit(FHitResult) (%d parameters): the hit intake stays off"), *GetOwner()->GetName(), ParamCount);
		}
		return false;
	}
	FScriptDelegate Delegate;
	Delegate.BindUFunction(this, GET_FUNCTION_NAME_CHECKED(URPGHitIntake, HandlePackHit));
	OnHit->AddDelegate(MoveTemp(Delegate), Collision);
	BoundCollision = Collision;
	bBound = true;
	UE_LOG(LogRPGHitIntake, Log, TEXT("%s: hit intake bound to %s.OnHit"), *GetOwner()->GetName(), *Collision->GetName());
	return true;
}

void URPGHitIntake::Unbind()
{
	UObject* Collision = BoundCollision.Get();
	if (!bBound || !Collision)
	{
		bBound = false;
		return;
	}
	if (const FMulticastDelegateProperty* OnHit = CastField<FMulticastDelegateProperty>(Collision->GetClass()->FindPropertyByName(TEXT("OnHit"))))
	{
		FScriptDelegate Delegate;
		Delegate.BindUFunction(this, GET_FUNCTION_NAME_CHECKED(URPGHitIntake, HandlePackHit));
		OnHit->RemoveDelegate(Delegate, Collision);
	}
	bBound = false;
	BoundCollision.Reset();
}

FRPGHitRecord URPGHitIntake::BuildRecord(const FHitResult& HitResult, AActor* Target, UObject*& OutActiveTarget) const
{
	FRPGHitRecord Record;
	Record.Time = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
	Record.Target = Target;
	Record.HitBone = HitResult.BoneName;
	Record.Source = TEXT("none");

	// The weapon: the combat style the pack's combat component holds now.
	if (UObject* Combat = FindComponentByClassName(GetOwner(), TEXT("BP_CombatComponent_C")))
	{
		if (const UObject* Style = ReadObject(Combat, TEXT("CurrentCombatStyle")))
		{
			Record.Weapon = Style->GetFName();
		}
	}
	// The trace target that is swinging now: its hit data is read one frame later (FinalizePending).
	OutActiveTarget = BoundCollision.IsValid() ? FindActiveTarget(BoundCollision.Get()) : nullptr;
	if (const ACharacter* Character = Cast<ACharacter>(GetOwner()))
	{
		Record.bAirborne = Character->GetCharacterMovement() && Character->GetCharacterMovement()->IsFalling();
		if (const USkeletalMeshComponent* Mesh = Character->GetMesh())
		{
			if (const UAnimInstance* Anim = Mesh->GetAnimInstance())
			{
				if (const UAnimMontage* Montage = Anim->GetCurrentActiveMontage())
				{
					Record.Montage = Montage->GetFName();
					Record.bAirborneAtStart = Montage->GetFName() == TrackedMontage && bTrackedAirborneAtStart;
				}
			}
		}
	}
	return Record;
}

void URPGHitIntake::HandlePackHit(FHitResult HitResult)
{
	AActor* Target = HitResult.GetActor();
	if (!Target || !URPGPlayerMovesSubsystem::IsPackBoss(Target))
	{
		++OtherHitCount;
		return;
	}
	if (GetWorld())
	{
		HotUntil = GetWorld()->GetTimeSeconds() + FRPGDamageScaler::Window + 0.1;
	}
	FPending Entry;
	UObject* ActiveTarget = nullptr;
	Entry.Record = BuildRecord(HitResult, Target, ActiveTarget);
	Entry.ActiveTarget = ActiveTarget;
	Pending.Add(MoveTemp(Entry));
	if (!bFinalizeScheduled && GetWorld())
	{
		bFinalizeScheduled = true;
		GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateUObject(this, &URPGHitIntake::FinalizePending));
	}
}

void URPGHitIntake::FinalizePending()
{
	bFinalizeScheduled = false;
	const bool bShared = Pending.Num() > 1;
	TArray<FPending> Batch = MoveTemp(Pending);
	Pending.Reset();
	// Hits of one swing on one target in one frame are ONE hit for the table (the dual swords' two blades strike together; the pack deals its health damage for EACH blade, 32 instead of 16 per swing in the probe of 2026-10-22, KI-092, while posture and bleed are applied once here): the first entry is the record, the others are merged into it and counted apart.
	TArray<FName> SeenMontages;
	for (FPending& Entry : Batch)
	{
		FRPGHitRecord& Record = Entry.Record;
		if (Record.Montage != NAME_None && SeenMontages.Contains(Record.Montage))
		{
			++MergedHitCount;
			UE_LOG(LogRPGHitIntake, Log, TEXT("a second hit of the same swing (montage %s) in the same frame on the boss is merged into the first one (merged so far %d)"), *Record.Montage.ToString(), MergedHitCount);
			continue;
		}
		SeenMontages.Add(Record.Montage);
		// The data of the attack that hit: the pack builds the hit data right after it raises OnHit, so one frame later the active target's HitData is this hit's.
		const UObject* Data = nullptr;
		if (const UObject* Active = Entry.ActiveTarget.Get())
		{
			if (const UObject* HitData = ReadObject(Active, TEXT("HitData")))
			{
				Data = ReadObject(HitData, TEXT("AttackData"));
				if (Data)
				{
					Record.Source = TEXT("HitData");
				}
			}
			if (!Data)
			{
				Data = ReadObject(Active, TEXT("Attack Data"));
				if (Data)
				{
					Record.Source = TEXT("TargetAttackData");
				}
			}
		}
		if (Data)
		{
			Record.AttackData = Data->GetFName();
			Record.AttackPower = ReadByte(Data, TEXT("AttackPower"));
			Record.PackPoiseDamage = ReadFloat(Data, TEXT("PoiseDamage"));
		}
		Record.Kind = RPGClassifyAttack(Record.AttackData, Record.bAirborne || Record.bAirborneAtStart);
		// The dual swords' strong and jump heavy swings carry the generic Default attack data (the data says Light): when the hit's montage is the montage of the current (or last) swing and the swing tracker found it in the ability's strong or charged array, the swing's kind stands (M13).
		if (Record.Kind == ERPGAttackKind::Light || Record.Kind == ERPGAttackKind::JumpLight)
		{
			if (const URPGSwingTracker* Swings = GetOwner() ? GetOwner()->FindComponentByClass<URPGSwingTracker>() : nullptr)
			{
				const FRPGSwing& Swing = Swings->GetCurrentSwing().IsAttack() ? Swings->GetCurrentSwing() : Swings->GetLastAttackSwing();
				if (Swing.IsAttack() && Swing.Montage == Record.Montage && (Swing.Kind == ERPGAttackKind::Strong || Swing.Kind == ERPGAttackKind::Charged || Swing.Kind == ERPGAttackKind::JumpHeavy))
				{
					Record.Kind = Swing.Kind;
					++SwingKindOverrideCount;
				}
			}
		}
		if (Table)
		{
			Record.bRowFound = Table->Find(Record.Weapon, Record.Kind, Record.Row);
			if (!Record.bRowFound)
			{
				const FString Key = FString::Printf(TEXT("%s/%s"), *Record.Weapon.ToString(), RPGAttackKindName(Record.Kind));
				if (!WarnedRows.Contains(Key))
				{
					WarnedRows.Add(Key);
					UE_LOG(LogRPGHitIntake, Warning, TEXT("no weapon attack table row for %s: the fallback row is used (posture %.0f)"), *Key, Record.Row.PostureDamage);
				}
			}
		}
		Record.HealthMultiplier = Record.Row.HealthDamageMultiplier;
		if (AActor* ScaledBoss = Record.Target.Get())
		{
			const double Adjust = Scaler.OnHit(GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0, Record.HealthMultiplier);
			if (FMath::Abs(Adjust) > 0.01)
			{
				AdjustBossHealth(ScaledBoss, Adjust, TEXT("record first"));
			}
		}
		Record.bAmbiguous = bShared;
		Record.Id = ++BossHitCount;
		LastRecord = Record;
		Lines.Add(Record.ToString());
		if (Lines.Num() > 64)
		{
			Lines.RemoveAt(0);
		}
		UE_LOG(LogRPGHitIntake, Log, TEXT("%s"), *Record.ToString());
		// The posture damage of the hit's table row goes into the boss's own pool; the stance break follows when it reaches zero (M9).
		if (AActor* Boss = Record.Target.Get())
		{
			if (URPGBossPosture* Posture = Boss->FindComponentByClass<URPGBossPosture>())
			{
				Posture->ApplyPostureDamage(Record.Row.PostureDamage, *FString::Printf(TEXT("%s %s"), *Record.Weapon.ToString(), RPGAttackKindName(Record.Kind)));
			}
		}
		// The bleed buildup of the hit's table row (the dexterity weapons build the status, M12).
		if (AActor* Boss = Record.Target.Get())
		{
			if (URPGBossBleed* Bleed = Boss->FindComponentByClass<URPGBossBleed>())
			{
				Bleed->AddBuildup(BleedOverride >= 0.f ? BleedOverride : Record.Row.BleedBuildup, *FString::Printf(TEXT("%s %s"), *Record.Weapon.ToString(), RPGAttackKindName(Record.Kind)));
			}
		}
		OnBossHit.Broadcast(Record);
	}
}

TArray<FString> URPGHitIntake::GetRecordLines() const
{
	return Lines;
}

void URPGHitIntake::ResetCounters()
{
	Pending.Reset();
	MergedHitCount = 0;
	SwingKindOverrideCount = 0;
	ScaledHitCount = 0;
	HealthAdjustTotal = 0.0;
	Scaler.Reset();
	BossHitCount = 0;
	OtherHitCount = 0;
	LastRecord = FRPGHitRecord();
	Lines.Reset();
}
