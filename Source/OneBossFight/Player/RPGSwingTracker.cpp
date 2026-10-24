// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGSwingTracker.h"
#include "Pack/RPGBlueprintCall.h"
#include "Pack/RPGPackReflect.h"
#include "Player/RPGBossStagger.h"
#include "Player/RPGSwingRules.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "UObject/UnrealType.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGSwing, Log, All);

using namespace RPGPack;

namespace
{
	constexpr const TCHAR* StaminaTag = TEXT("Attribute.Stamina");

	/** The abilities the pack created for the actor (CreatedAbilities of its ability system component). */
	void GetAbilities(const AActor* Actor, TArray<UObject*>& Out)
	{
		UObject* Asc = FindComponentByClassName(Actor, TEXT("BP_AdvancedAbilitySystemComponent_C"));
		const FArrayProperty* Created = Asc ? FindFProperty<FArrayProperty>(Asc->GetClass(), TEXT("CreatedAbilities")) : nullptr;
		const FObjectProperty* Inner = Created ? CastField<FObjectProperty>(Created->Inner) : nullptr;
		if (!Inner)
		{
			return;
		}
		FScriptArrayHelper Abilities(Created, Created->ContainerPtrToValuePtr<void>(Asc));
		for (int32 Index = 0; Index < Abilities.Num(); ++Index)
		{
			if (UObject* Ability = Inner->GetObjectPropertyValue(Abilities.GetRawPtr(Index)))
			{
				Out.Add(Ability);
			}
		}
	}
}

FString FRPGSwing::ToString() const
{
	return FString::Printf(TEXT("swing %d at %.2f s: weapon %s, kind %s, %s, montage %s, row posture %.0f stamina %.0f%s, stamina extra %+.1f, hyperarmor %.2f to %.2f"), Id, StartTime, *Weapon.ToString(), RPGAttackKindName(Kind), bAirborneAtStart ? TEXT("started airborne") : TEXT("started grounded"),
		*Montage.ToString(), Row.PostureDamage, Row.StaminaCost, bRowFound ? TEXT("") : TEXT(" (no row)"), StaminaExtra, HyperArmorStart, HyperArmorEnd);
}

URPGSwingTracker::URPGSwingTracker()
{
	PrimaryComponentTick.bCanEverTick = true; // every frame: the start of an attack montage is found at the frame it starts
}

void URPGSwingTracker::BeginPlay()
{
	Super::BeginPlay();
	OriginalTable = URPGWeaponAttackTable::LoadOrDefault();
	Table = OriginalTable;
}

void URPGSwingTracker::ClearCostOverrides()
{
#if !UE_BUILD_SHIPPING
	CostOverrides.Reset();
	HyperArmorOverrides.Reset();
	Table = OriginalTable;
	TestTable = nullptr;
#endif
}

void URPGSwingTracker::SetRowHyperArmorForTest(FName Weapon, ERPGAttackKind Kind, float Start, float End)
{
#if !UE_BUILD_SHIPPING
	if (!OriginalTable)
	{
		return;
	}
	if (!TestTable)
	{
		TestTable = DuplicateObject<URPGWeaponAttackTable>(OriginalTable, GetTransientPackage());
	}
	Table = TestTable;
	for (FRPGWeaponAttackRow& Row : TestTable->Rows)
	{
		if (Row.Weapon == Weapon && Row.Kind == Kind)
		{
			Row.HyperArmorStart = Start;
			Row.HyperArmorEnd = End;
			return;
		}
	}
	FRPGWeaponAttackRow Row;
	OriginalTable->Find(Weapon, Kind, Row); // the any-weapon row or the fallback as the base of the new row
	Row.Weapon = Weapon;
	Row.Kind = Kind;
	Row.HyperArmorStart = Start;
	Row.HyperArmorEnd = End;
	TestTable->Rows.Add(Row);
#endif
}

bool URPGSwingTracker::IsPlayerHitStunBlockedByImmunity() const
{
	const UObject* Stun = FindAbilityByClassName(GetOwner(), TEXT("GA_PlayerHitStun_C"));
	const FStructProperty* Blocked = Stun ? CastField<FStructProperty>(Stun->GetClass()->FindPropertyByName(TEXT("ActivationBlockedTags"))) : nullptr;
	const FGameplayTag Immune = FGameplayTag::RequestGameplayTag(TEXT("Status.HitStunImmune"), false);
	if (!Blocked || !Immune.IsValid() || Blocked->Struct != TBaseStructure<FGameplayTagContainer>::Get())
	{
		return false;
	}
	return Blocked->ContainerPtrToValuePtr<FGameplayTagContainer>(Stun)->HasTagExact(Immune);
}

void URPGSwingTracker::ResetCounters()
{
	Current = FRPGSwing();
	LastAttack = FRPGSwing();
	SwingCount = 0;
	AttackSwingCount = 0;
	StaminaExtraTotal = 0.f;
	ApplyFailedSwing = -1;
	Lines.Reset();
}

void URPGSwingTracker::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if (bHyperArmor)
	{
		SetHyperArmor(false);
	}
	Super::EndPlay(EndPlayReason);
}

void URPGSwingTracker::SetHyperArmorOverrideForTest(ERPGAttackKind Kind, float Start, float End)
{
#if !UE_BUILD_SHIPPING
	HyperArmorOverrides.Add(Kind, FVector2D(Start, End));
#endif
}

void URPGSwingTracker::SetCostOverrideForTest(ERPGAttackKind Kind, float Cost)
{
#if !UE_BUILD_SHIPPING
	CostOverrides.Add(Kind, Cost);
#endif
}

void URPGSwingTracker::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	const ACharacter* Character = Cast<ACharacter>(GetOwner());
	const USkeletalMeshComponent* Mesh = Character ? Character->GetMesh() : nullptr;
	const UAnimInstance* Anim = Mesh ? Mesh->GetAnimInstance() : nullptr;
	const UAnimMontage* Montage = Anim ? Anim->GetCurrentActiveMontage() : nullptr;
	if (!Montage)
	{
		TrackedMontage = NAME_None;
		LastMontagePosition = 0.f;
		UpdateHyperArmor(nullptr, 0.f);
		return;
	}
	const float Position = Anim->Montage_GetPosition(Montage);
	// A new montage, or the same one started again (its position went back): a new swing starts now, in the stance the player is in.
	if (Montage->GetFName() != TrackedMontage || Position + KINDA_SMALL_NUMBER < LastMontagePosition)
	{
		TrackedMontage = Montage->GetFName();
		const bool bAirborne = Character->GetCharacterMovement() && Character->GetCharacterMovement()->IsFalling();
		OnMontageStarted(Montage, bAirborne);
	}
	LastMontagePosition = Position;
	UpdateHyperArmor(Montage, Position);
}

ERPGAttackKind URPGSwingTracker::ClassifyMontage(const FString& MontageName, bool bAirborne) const
{
	TArray<UObject*> Abilities;
	GetAbilities(GetOwner(), Abilities);
	for (const UObject* Ability : Abilities)
	{
		if (!RPGPackReflect::Find(Ability, TEXT("AttackMontages")))
		{
			continue; // not a weapon ability
		}
		// The strong and charged arrays first: the falling attack of a weapon may reuse its first light montage.
		if (RPGPackReflect::ArrayMentions(Ability, TEXT("StrongAttackMontages"), MontageName))
		{
			return bAirborne ? ERPGAttackKind::JumpHeavy : ERPGAttackKind::Strong;
		}
		if (RPGPackReflect::ArrayMentions(Ability, TEXT("ChargedAttackMontages"), MontageName))
		{
			return ERPGAttackKind::Charged;
		}
		if (RPGPackReflect::ArrayMentions(Ability, TEXT("AttackMontages"), MontageName) || RPGPackReflect::ArrayMentions(Ability, TEXT("FallingAttackMontages"), MontageName)
			|| RPGPackReflect::ArrayMentions(Ability, TEXT("SprintAttackMontages"), MontageName) || RPGPackReflect::ArrayMentions(Ability, TEXT("DodgeAttackMontages"), MontageName))
		{
			return bAirborne ? ERPGAttackKind::JumpLight : ERPGAttackKind::Light;
		}
	}
	return ERPGAttackKind::Unknown;
}

bool URPGSwingTracker::AddStamina(double Delta)
{
	double Now = 0.0, Max = 0.0;
	if (!ReadAttribute(GetOwner(), StaminaTag, false, Now) || !ReadAttribute(GetOwner(), StaminaTag, true, Max))
	{
		return false;
	}
	return WriteAttribute(GetOwner(), StaminaTag, FMath::Clamp(Now + Delta, 0.0, FMath::Max(Max, 0.0)));
}

void URPGSwingTracker::OnMontageStarted(const UAnimMontage* Montage, bool bAirborne)
{
	FRPGSwing Swing;
	Swing.Id = ++SwingCount;
	Swing.StartTime = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
	Swing.Montage = Montage->GetFName();
	Swing.bAirborneAtStart = bAirborne;
	if (UObject* Combat = FindComponentByClassName(GetOwner(), TEXT("BP_CombatComponent_C")))
	{
		if (const UObject* Style = RPGPackReflect::ReadObject(Combat, TEXT("CurrentCombatStyle")))
		{
			Swing.Weapon = Style->GetFName();
		}
	}
	Swing.Kind = ClassifyMontage(Montage->GetName(), bAirborne);
	Current = Swing;
	if (!Swing.IsAttack())
	{
		return; // a dodge, a jump, a drink: nothing of the weapon table applies
	}
	++AttackSwingCount;
	if (Table)
	{
		Swing.bRowFound = Table->Find(Swing.Weapon, Swing.Kind, Swing.Row);
		if (!Swing.bRowFound)
		{
			const FString Key = FString::Printf(TEXT("%s/%s"), *Swing.Weapon.ToString(), RPGAttackKindName(Swing.Kind));
			if (!WarnedRows.Contains(Key))
			{
				WarnedRows.Add(Key);
				UE_LOG(LogRPGSwing, Warning, TEXT("no weapon attack table row for %s: the pack's stamina cost stands"), *Key);
			}
		}
	}
	// The hyperarmor window of the swing: a test override first, else the row's.
	RPGSwingRules::ResolveWindow(Swing.Row, HyperArmorOverrides.Find(Swing.Kind), Swing.HyperArmorStart, Swing.HyperArmorEnd);
	// The cost the swing should have (an override of a test first, else the row's), against the pack's own 15 that has just been paid.
	float Wanted = Swing.Row.StaminaCost;
	if (const float* Override = CostOverrides.Find(Swing.Kind))
	{
		Wanted = *Override;
	}
	if (bApplyStaminaCosts && Wanted >= 0.f)
	{
		double Now = 0.0;
		ReadAttribute(GetOwner(), StaminaTag, false, Now);
		const float Extra = RPGSwingRules::StaminaExtra(Wanted, PackStaminaCost, Now); // never below zero
		if (!FMath::IsNearlyZero(Extra) && AddStamina(-static_cast<double>(Extra)))
		{
			Swing.StaminaExtra = Extra;
			StaminaExtraTotal += Extra;
		}
	}
	Current = Swing;
	LastAttack = Swing;
	Lines.Add(Swing.ToString());
	if (Lines.Num() > 64)
	{
		Lines.RemoveAt(0);
	}
	UE_LOG(LogRPGSwing, Log, TEXT("%s"), *Swing.ToString());
}

void URPGSwingTracker::UpdateHyperArmor(const UAnimMontage* Montage, float Position)
{
	bool bWant = false;
	if (Montage && Current.IsAttack() && Montage->GetFName() == Current.Montage)
	{
		bWant = RPGSwingRules::WindowOpen(Current.HyperArmorStart, Current.HyperArmorEnd, Position);
	}
	if (bWant != bHyperArmor)
	{
		if (bWant && ApplyFailedSwing == Current.Id)
		{
			return; // applying the pack's effect failed for this swing: not tried again in every frame of its window
		}
		SetHyperArmor(bWant);
		return;
	}
	// The pack's effect lasts 4 s and is not applied again while it is active: a window that stays open longer gets it applied again before it runs out.
	const double Now = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
	if (bWant && RPGSwingRules::NeedsRefresh(Now, HyperArmorAppliedAt, HyperArmorRefreshSeconds))
	{
		RemoveImmunity();
		if (ApplyImmunity())
		{
			HyperArmorAppliedAt = Now;
			++HyperArmorRefreshes;
			UE_LOG(LogRPGSwing, Log, TEXT("%s: hyperarmor applied again (swing %d, window still open)"), *GetOwner()->GetName(), Current.Id);
		}
		else
		{
			bHyperArmor = false;
			ApplyFailedSwing = Current.Id;
			UE_LOG(LogRPGSwing, Warning, TEXT("%s: the hyperarmor effect could not be applied again (swing %d): the rest of the window has none"), *GetOwner()->GetName(), Current.Id);
		}
	}
}

bool URPGSwingTracker::ApplyImmunity()
{
	UObject* Asc = FindComponentByClassName(GetOwner(), TEXT("BP_AdvancedAbilitySystemComponent_C"));
	UClass* Effect = GetDefault<URPGBossStagger>()->ImmunityEffect.LoadSynchronous();
	if (!Asc || !Effect)
	{
		return false;
	}
	return CallBlueprintFunction(Asc, TEXT("Apply Gameplay Effect by Class"),
		[&](UFunction& F, uint8* P)
		{
			if (const FClassProperty* ClassProp = CastField<FClassProperty>(F.FindPropertyByName(TEXT("GameplayEffectClass"))))
			{
				ClassProp->SetPropertyValue_InContainer(P, Effect);
			}
			if (const FNumericProperty* Level = CastField<FNumericProperty>(F.FindPropertyByName(TEXT("Level"))))
			{
				Level->SetIntPropertyValue(Level->ContainerPtrToValuePtr<void>(P), static_cast<int64>(1));
			}
		},
		[](UFunction&, uint8*) {}); // false when the pack has no function of that name (a renamed pack function must not look like a working hyperarmor)
}

void URPGSwingTracker::RemoveImmunity()
{
	UObject* Asc = FindComponentByClassName(GetOwner(), TEXT("BP_AdvancedAbilitySystemComponent_C"));
	UClass* Effect = GetDefault<URPGBossStagger>()->ImmunityEffect.LoadSynchronous();
	if (!Asc || !Effect)
	{
		return;
	}
	CallBlueprintFunction(Asc, TEXT("Remove Active Gameplay Effect By Class"),
		[&](UFunction& F, uint8* P)
		{
			if (const FClassProperty* ClassProp = CastField<FClassProperty>(F.FindPropertyByName(TEXT("GameplayEffectClass"))))
			{
				ClassProp->SetPropertyValue_InContainer(P, Effect);
			}
		},
		[](UFunction&, uint8*) {});
}

void URPGSwingTracker::SetHyperArmor(bool bOn)
{
	if (bOn)
	{
		if (!ApplyImmunity())
		{
			bHyperArmor = false;
			ApplyFailedSwing = Current.Id;
			UE_LOG(LogRPGSwing, Warning, TEXT("%s: the hyperarmor effect could not be applied (swing %d): no hyperarmor in this swing"), *GetOwner()->GetName(), Current.Id);
			return;
		}
		HyperArmorAppliedAt = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
		++HyperArmorWindows;
		UE_LOG(LogRPGSwing, Log, TEXT("%s: hyperarmor on (swing %d, %s)"), *GetOwner()->GetName(), Current.Id, RPGAttackKindName(Current.Kind));
	}
	else
	{
		RemoveImmunity();
		UE_LOG(LogRPGSwing, Log, TEXT("%s: hyperarmor off"), *GetOwner()->GetName());
	}
	bHyperArmor = bOn;
}
