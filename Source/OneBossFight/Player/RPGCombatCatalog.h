// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Player/RPGAttackKind.h"
#include "Player/RPGWeaponAttackTable.h"
#include "UObject/StrongObjectPtr.h"
#include "RPGCombatCatalog.generated.h"

USTRUCT(BlueprintType)
struct ONEBOSSFIGHT_API FRPGCatalogWeapon
{
	GENERATED_BODY()
	UPROPERTY(EditAnywhere, BlueprintReadWrite) FName WeaponId;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) FName StyleName;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) FSoftObjectPath StyleAsset;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) FSoftObjectPath ItemPath;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) FSoftObjectPath ItemBaseClass;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) FSoftObjectPath ActorClass;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) FSoftObjectPath AbilityClass;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) FString HudWeaponWord;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) TArray<FName> StyleAliases;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) TMap<FName, FString> AliasHudWords;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) FSoftObjectPath Icon;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) TArray<ERPGAttackKind> Actions;
	/** Compatibility fixtures may report missing rows; required authored content must reject them. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite) bool bRequireExactRows = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) FString ReferenceProvenance = TEXT("legacy placeholder, unresolved");
};

USTRUCT(BlueprintType)
struct ONEBOSSFIGHT_API FRPGCatalogBuild
{
	GENERATED_BODY()
	UPROPERTY(EditAnywhere, BlueprintReadWrite) FName BuildId;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) FString ConsoleName;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) TArray<FString> Aliases;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) FString DisplayName;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 UiOrder = 0;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 LegacySlot = INDEX_NONE;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) FName WeaponId;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) FSoftObjectPath Icon;
};

UCLASS(BlueprintType)
class ONEBOSSFIGHT_API URPGWeaponDefinition : public UPrimaryDataAsset
{
	GENERATED_BODY()
public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite) FRPGCatalogWeapon Definition;
};

UCLASS(BlueprintType)
class ONEBOSSFIGHT_API URPGBuildDefinition : public UPrimaryDataAsset
{
	GENERATED_BODY()
public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite) FRPGCatalogBuild Definition;
};

UCLASS(BlueprintType)
class ONEBOSSFIGHT_API URPGCombatCatalog : public UPrimaryDataAsset
{
	GENERATED_BODY()
public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 SchemaVersion = 1;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) TArray<TSoftObjectPtr<URPGWeaponDefinition>> Weapons;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) TArray<TSoftObjectPtr<URPGBuildDefinition>> Builds;
};

namespace RPGCombatRegistry
{
	enum class EResolve : uint8 { Found, Empty, UnknownId, Ambiguous };
	enum class ESource : uint8 { Auto, Legacy, Data };
	struct FCoverage
	{
		FName WeaponId;
		ERPGAttackKind Kind = ERPGAttackKind::Unknown;
		FString Route;
		FRPGWeaponAttackRow Effective;
	};
	/** Immutable after publication. Leases are distinct from value-copied metadata. */
	struct ONEBOSSFIGHT_API FEpoch
	{
		FGuid Id;
		FString Source;
		FString Reason;
		TArray<FRPGCatalogBuild> Builds;
		TArray<FRPGCatalogWeapon> Weapons;
		TArray<FCoverage> Coverage;
		TArray<TStrongObjectPtr<UObject>> Leases;
		const FRPGCatalogBuild* Find(FName IdToFind) const;
		const FRPGCatalogWeapon* Weapon(FName IdToFind) const;
		EResolve Parse(const FString& Text, FName& OutId) const;
		EResolve StyleToBuild(FName Style, FName& OutId) const;
		bool Matches(FName Style, FName BuildId) const;
		FString Describe(FName Style, FName VerifiedBuild = NAME_None) const;
		const FRPGCatalogBuild* LegacySlot(int32 Slot) const;
	};
	ONEBOSSFIGHT_API FString Normalize(const FString& Text);
	ONEBOSSFIGHT_API TSharedPtr<const FEpoch> Legacy();
	/** Pure structural validation first; production additionally resolves/cook-checks references. */
	ONEBOSSFIGHT_API TSharedPtr<const FEpoch> Compile(const TArray<FRPGCatalogBuild>& Builds,
		const TArray<FRPGCatalogWeapon>& Weapons, FString& Error, bool bResolveAssets = true);
	/** Independent single-publication context; not a process-global stack. */
	class ONEBOSSFIGHT_API FContext
	{
	public:
		bool Publish(ESource Source, TSharedPtr<const FEpoch> Candidate, const FString& Failure);
		TSharedPtr<const FEpoch> Get() const { return Epoch; }
		bool IsPublished() const { return bAttempted; }
	private:
		bool bAttempted = false;
		TSharedPtr<const FEpoch> Epoch;
	};
	ONEBOSSFIGHT_API TSharedPtr<const FEpoch> ForWorld(const UWorld* World);
	/** Same geometry for paint, click, focus and keys; first three keep legacy geometry. */
	ONEBOSSFIGHT_API bool RowVisible(int32 Row, int32 Count, float Height);
	ONEBOSSFIGHT_API int32 VisibleRows(int32 Count, float Height);
}

UCLASS()
class ONEBOSSFIGHT_API URPGCombatCatalogSubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()
public:
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;
	virtual void Deinitialize() override;
	TSharedPtr<const RPGCombatRegistry::FEpoch> GetEpoch() const;
	UFUNCTION(BlueprintPure, Category="Combat Catalog") FString GetDiagnostic() const;
	UFUNCTION(BlueprintPure, Category="Combat Catalog") int32 GetBuildCount() const;
	UFUNCTION(BlueprintPure, Category="Combat Catalog") TArray<FString> GetCoverageLines() const;
private:
	RPGCombatRegistry::FContext Context;
	FString LatchedSource;
	mutable bool bLateChangeReported = false;
};
