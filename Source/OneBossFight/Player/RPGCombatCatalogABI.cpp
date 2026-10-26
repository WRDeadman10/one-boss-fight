#include "Player/RPGCombatCatalogABI.h"
#include "GameFramework/Actor.h"
#include "UObject/UnrealType.h"

namespace RPGCombatRegistry
{
namespace
{
// E011: root class identities are trusted native adapter constants, NOT catalog inputs.
constexpr const TCHAR* WeaponRoot = TEXT("/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/DataAssets/Items/WeaponItem.WeaponItem_C");
constexpr const TCHAR* ItemOwner = TEXT("/Game/AdvancedARPGCombat/AdvancedCombatFramework/InventorySystem/Items/BP_ItemBase.BP_ItemBase_C");
constexpr const TCHAR* ActorRoot = TEXT("/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/Actors/Weapons/BP_BaseWeapon.BP_BaseWeapon_C");
constexpr const TCHAR* StyleRoot = TEXT("/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/DataAssets/BP_CombatStyle.BP_CombatStyle_C");
constexpr const TCHAR* AbilityRoot = TEXT("/Game/AdvancedARPGCombat/AdvancedCombatFramework/AbilitySystem/Abilities/BP_AdvancedGameplayAbility.BP_AdvancedGameplayAbility_C");
constexpr const TCHAR* SetOwner = TEXT("/Game/AdvancedARPGCombat/AdvancedCombatFramework/AbilitySystem/BP_AbilitySet.BP_AbilitySet_C");
constexpr const TCHAR* SetStruct = TEXT("/Game/AdvancedARPGCombat/AdvancedCombatFramework/AbilitySystem/Structs/F_AbilitySet.F_AbilitySet");
constexpr const TCHAR* AbilityMember = TEXT("Abilities_6_F0CDCA79498EAB06225ED39B4E383935");

bool OwnedBy(const FProperty* Property, const TCHAR* FullClass)
{
	return Property && Property->GetOwnerStruct() && Property->GetOwnerStruct()->GetPathName() == FullClass;
}
}

bool ValidateWeaponReferences(const FRPGCatalogWeapon& W, const FWeaponReferences& R,
	TArray<TStrongObjectPtr<UObject>>& Leases, FString& Error)
{
	Error.Reset();
	auto Fail = [&](const TCHAR* Role) { Error = W.WeaponId.ToString() + TEXT(".References.") + Role; return false; };
	if (!IsValid(R.Item)) return Fail(TEXT("Item.Missing"));
	if (!IsValid(R.ActorClass)) return Fail(TEXT("Actor.Missing"));
	if (!IsValid(R.AbilityClass)) return Fail(TEXT("Ability.Missing"));
	if (!IsValid(R.Style)) return Fail(TEXT("Style.Missing"));
	UClass* ItemBase = Cast<UClass>(FSoftObjectPath(WeaponRoot).TryLoad());
	UClass* ActorBase = Cast<UClass>(FSoftObjectPath(ActorRoot).TryLoad());
	UClass* AbilityBase = Cast<UClass>(FSoftObjectPath(AbilityRoot).TryLoad());
	UClass* StyleBase = Cast<UClass>(FSoftObjectPath(StyleRoot).TryLoad());
	if (!ItemBase || !ActorBase || !AbilityBase || !StyleBase) return Fail(TEXT("Adapter.RequiredRootMissing"));
	Leases.Emplace(ItemBase); Leases.Emplace(ActorBase); Leases.Emplace(AbilityBase); Leases.Emplace(StyleBase);
	// A caller-supplied broad UObject class cannot bless a non-weapon or bypass native ABI.
	if (!R.Item->IsA(ItemBase)) return Fail(TEXT("Item.ExpectedABI"));
	if (!IsValid(R.DeclaredItemBase) || !R.DeclaredItemBase->IsChildOf(ItemBase) || !R.Item->IsA(R.DeclaredItemBase))
		return Fail(TEXT("Item.DeclaredBaseExpectedABI"));
	if (!R.ActorClass->IsChildOf(ActorBase)) return Fail(TEXT("Actor.ExpectedABI"));
	if (!R.AbilityClass->IsChildOf(AbilityBase)) return Fail(TEXT("Ability.ExpectedABI"));
	if (!R.Style->IsA(StyleBase)) return Fail(TEXT("Style.ExpectedABI"));
	// Require the actual full object identity, not just its short name or an unrelated path string.
	if (FSoftObjectPath(R.Item) != W.ItemPath) return Fail(TEXT("Item.Identity"));
	if (FSoftObjectPath(R.ActorClass) != W.ActorClass) return Fail(TEXT("Actor.Identity"));
	if (FSoftObjectPath(R.AbilityClass) != W.AbilityClass) return Fail(TEXT("Ability.Identity"));
	if (FSoftObjectPath(R.Style) != W.StyleAsset || R.Style->GetFName() != W.StyleName) return Fail(TEXT("Style.Identity"));
	if (FSoftObjectPath(R.DeclaredItemBase) != W.ItemBaseClass) return Fail(TEXT("Item.DeclaredBaseIdentity"));

	// PR5 Item: BP_ItemBase.Equipable Actor Class is only constrained to Actor by the pack.
	// Native ActorBase check above adds the required weapon capability restriction.
	const FClassProperty* ActorProperty = FindFProperty<FClassProperty>(R.Item->GetClass(), TEXT("Equipable Actor Class"));
	if (!OwnedBy(ActorProperty, ItemOwner) || ActorProperty->MetaClass != AActor::StaticClass())
		return Fail(TEXT("Item.ActorBinding.Schema"));
	if (ActorProperty->GetObjectPropertyValue_InContainer(R.Item) != R.ActorClass) return Fail(TEXT("Item.ActorBinding"));
	const FObjectProperty* StyleProperty = FindFProperty<FObjectProperty>(R.Item->GetClass(), TEXT("Combat Style"));
	if (!OwnedBy(StyleProperty, WeaponRoot) || StyleProperty->PropertyClass != StyleBase)
		return Fail(TEXT("Item.StyleBinding.Schema"));
	if (StyleProperty->GetObjectPropertyValue_InContainer(R.Item) != R.Style) return Fail(TEXT("Item.StyleBinding"));

	const FArrayProperty* Sets = FindFProperty<FArrayProperty>(R.Style->GetClass(), TEXT("AbilitiesSet"));
	const FStructProperty* Row = Sets ? CastField<FStructProperty>(Sets->Inner) : nullptr;
	if (!OwnedBy(Sets, SetOwner) || !Row || !Row->Struct || Row->Struct->GetPathName() != SetStruct)
		return Fail(TEXT("Style.AbilityGrant.Schema"));
	// GUID-qualified member is observed in PR4. Runtime reflection verifies nested kinds;
	// no value-text parsing and no assumption about the unexpanded PR5 nested MetaClass.
	const FArrayProperty* Abilities = FindFProperty<FArrayProperty>(Row->Struct, AbilityMember);
	const FClassProperty* Element = Abilities ? CastField<FClassProperty>(Abilities->Inner) : nullptr;
	if (!Abilities || !Element || !Element->MetaClass || !R.AbilityClass->IsChildOf(Element->MetaClass))
		return Fail(TEXT("Style.AbilityGrant.ElementSchema"));
	FScriptArrayHelper SetValues(Sets, Sets->ContainerPtrToValuePtr<void>(R.Style));
	bool Found = false;
	for (int32 SetIndex = 0; SetIndex < SetValues.Num(); ++SetIndex)
	{
		FScriptArrayHelper Classes(Abilities, Abilities->ContainerPtrToValuePtr<void>(SetValues.GetRawPtr(SetIndex)));
		for (int32 Index = 0; Index < Classes.Num(); ++Index)
		{
			if (Element->GetObjectPropertyValue(Classes.GetRawPtr(Index)) == R.AbilityClass) { Found = true; }
		}
	}
	return Found ? true : Fail(TEXT("Style.AbilityGrant"));
}
}
