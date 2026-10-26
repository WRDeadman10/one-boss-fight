// STAGED X-T10. Native installed-pack contract; not an author-controlled property map.
#pragma once
#include "CoreMinimal.h"
#include "Player/RPGCombatCatalog.h"

namespace RPGCombatRegistry
{
struct FWeaponReferences
{
	UObject* Item = nullptr;
	UClass* DeclaredItemBase = nullptr;
	UClass* ActorClass = nullptr;
	UClass* AbilityClass = nullptr;
	UObject* Style = nullptr;
};
/** Read-only validation of already-resolved objects. Compile owns cook-policy checks.
 * Fixed ancestry/typed role edges from E011 PR5 + PR4; no ExportText/substrings.
 * Leases retain trusted roots alongside the caller's already-resolved dependencies.
 */
ONEBOSSFIGHT_API bool ValidateWeaponReferences(const FRPGCatalogWeapon& Definition,
	const FWeaponReferences& References, TArray<TStrongObjectPtr<UObject>>& Leases, FString& Error);
}
