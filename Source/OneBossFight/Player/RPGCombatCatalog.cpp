// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGCombatCatalog.h"
#include "Player/RPGBuildRules.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "Engine/Texture2D.h"
#include "GameFramework/Actor.h"
#include "HAL/IConsoleManager.h"
#include "Misc/ConfigCacheIni.h"
#include "Misc/Parse.h"
#include "UObject/UnrealType.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGCatalog, Log, All);
#if !UE_BUILD_SHIPPING
static TAutoConsoleVariable<FString> CVarCatalogSource(TEXT("rpg.CatalogSource"), TEXT("auto"), TEXT("Startup only: auto, legacy, data. Changes affect NEXT session only."));
static TAutoConsoleVariable<int32> CVarCatalogFourth(TEXT("rpg.CatalogTestFourth"), 0, TEXT("Development startup fixture: add a fourth build sharing the existing sword. No asset written."));
static TAutoConsoleVariable<int32> CVarCatalogInvalid(TEXT("rpg.CatalogTestInvalid"), 0, TEXT("Development startup-only isolated invalid-input fixture; no asset changed."));
#endif

namespace RPGCombatRegistry
{
	FString Normalize(const FString& Text) { return Text.TrimStartAndEnd().TrimQuotes().TrimStartAndEnd().ToLower(); }
	const FRPGCatalogBuild* FEpoch::Find(FName Key) const { return Builds.FindByPredicate([Key](const FRPGCatalogBuild& B) { return B.BuildId == Key; }); }
	const FRPGCatalogWeapon* FEpoch::Weapon(FName Key) const { return Weapons.FindByPredicate([Key](const FRPGCatalogWeapon& W) { return W.WeaponId == Key; }); }
	const FRPGCatalogBuild* FEpoch::LegacySlot(int32 Slot) const { return Builds.FindByPredicate([Slot](const FRPGCatalogBuild& B) { return B.LegacySlot == Slot; }); }
	EResolve FEpoch::Parse(const FString& Text, FName& OutId) const
	{
		const FString Key = Normalize(Text);
		if (Key.IsEmpty() || Key == TEXT("none") || Key == TEXT("off")) return EResolve::Empty;
		for (const FRPGCatalogBuild& B : Builds)
		{
			if (Normalize(B.ConsoleName) == Key || Normalize(B.BuildId.ToString()) == Key) { OutId = B.BuildId; return EResolve::Found; }
			for (const FString& Alias : B.Aliases) if (Normalize(Alias) == Key) { OutId = B.BuildId; return EResolve::Found; }
		}
		return EResolve::UnknownId;
	}
	bool FEpoch::Matches(FName Style, FName BuildId) const
	{
		const FRPGCatalogBuild* B = Find(BuildId);
		const FRPGCatalogWeapon* W = B ? Weapon(B->WeaponId) : nullptr;
		return W && !Style.IsNone() && (W->StyleName == Style || W->StyleAliases.Contains(Style));
	}
	EResolve FEpoch::StyleToBuild(FName Style, FName& OutId) const
	{
		FName Candidate;
		for (const FRPGCatalogBuild& B : Builds) if (Matches(Style, B.BuildId))
		{
			if (!Candidate.IsNone()) return EResolve::Ambiguous;
			Candidate = B.BuildId;
		}
		if (Candidate.IsNone()) return EResolve::UnknownId;
		OutId = Candidate;
		return EResolve::Found;
	}
	FString FEpoch::Describe(FName Style, FName VerifiedBuild) const
	{
		if (Style.IsNone()) return TEXT("Unknown");
		FName IdToDescribe = VerifiedBuild;
		if (!Matches(Style, IdToDescribe) && StyleToBuild(Style, IdToDescribe) != EResolve::Found) return RPGBuildRules::DescribeStyle(Style);
		const FRPGCatalogBuild* B = Find(IdToDescribe);
		const FRPGCatalogWeapon* W = B ? Weapon(B->WeaponId) : nullptr;
		if (!B || !W) return RPGBuildRules::DescribeStyle(Style);
		const FString* AliasWord = W->AliasHudWords.Find(Style);
		return FString::Printf(TEXT("%s (%s)"), *B->DisplayName, AliasWord ? **AliasWord : *W->HudWeaponWord);
	}

	TSharedPtr<const FEpoch> Legacy()
	{
		TSharedPtr<FEpoch> E = MakeShared<FEpoch>();
		E->Id = FGuid::NewGuid(); E->Source = TEXT("legacy");
		for (int32 I = 0; I < RPGBuildRules::BuildCount; ++I)
		{
			const auto& L = RPGBuildRules::Entry(static_cast<ERPGBuild>(I));
			FRPGCatalogWeapon W; W.WeaponId = FName(L.Name); W.StyleName = FName(L.Style); W.ItemPath = FSoftObjectPath(L.ItemPath); W.HudWeaponWord = L.Weapon;
			const FString Root = TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/");
			const FString Folder = I == 0 ? TEXT("Sword/") : I == 1 ? TEXT("Claymore/") : TEXT("DualSwords/");
			const FString Instance = I == 0 ? TEXT("SwordInstances/") : I == 1 ? TEXT("ClaymoreInstances/") : TEXT("DualSwordInstances/");
			W.ActorClass = FSoftObjectPath(Root + Folder + Instance + FString(L.ActorClass).LeftChop(2) + TEXT(".") + L.ActorClass);
			W.AbilityClass = FSoftObjectPath(Root + Folder + FString(L.AbilityClass).LeftChop(2) + TEXT(".") + L.AbilityClass);
			W.StyleAsset = FSoftObjectPath(Root + Folder + L.Style + TEXT(".") + L.Style);
			W.Actions = {ERPGAttackKind::Light, ERPGAttackKind::Strong, ERPGAttackKind::Charged, ERPGAttackKind::JumpLight, ERPGAttackKind::JumpHeavy, ERPGAttackKind::Knockdown};
			// Full dependency identities for data authoring come from loaded item references, not base-name searches.
			FRPGCatalogBuild B; B.BuildId = FName(L.Name); B.ConsoleName = L.Name; B.DisplayName = L.Name; B.UiOrder = I; B.LegacySlot = I; B.WeaponId = W.WeaponId;
			B.Aliases.Add(I == 0 ? TEXT("sword") : I == 1 ? TEXT("str") : TEXT("dexterity"));
			if (I == 0) { W.StyleAliases.Add(TEXT("SwordAndShieldCombatStyle")); W.AliasHudWords.Add(TEXT("SwordAndShieldCombatStyle"), TEXT("Sword and Shield")); }
			if (I == 2) { W.StyleAliases.Add(TEXT("TwinbladeCombatStyle")); W.AliasHudWords.Add(TEXT("TwinbladeCombatStyle"), TEXT("Twinblades")); }
			const FString Icon = FString::Printf(TEXT("/Game/OneBossFight/UI/Art/T_Boss01_Icon_%s.T_Boss01_Icon_%s"), L.Name, L.Name);
			B.Icon = FSoftObjectPath(Icon); W.Icon = B.Icon;
			E->Weapons.Add(MoveTemp(W)); E->Builds.Add(MoveTemp(B));
		}
		return E;
	}

	static bool CookedDependency(const FSoftObjectPath& Path)
	{
		// Packaging settings are an editor/cook preflight, not shipped runtime configuration.
#if !WITH_EDITOR
		return Path.IsAsset(); // actual cooked availability/type is established by TryLoad below
#else
		if (Path.GetLongPackageName().StartsWith(TEXT("/Script/"))) return true;
		TArray<FString> Dirs;
		GConfig->GetArray(TEXT("/Script/UnrealEd.ProjectPackagingSettings"), TEXT("DirectoriesToAlwaysCook"), Dirs, GGameIni);
		for (const FString& Dir : Dirs)
		{
			FString Prefix;
			if (FParse::Value(*Dir, TEXT("Path="), Prefix))
			{
				Prefix = Prefix.TrimQuotes(); Prefix.RemoveFromEnd(TEXT(")")); Prefix = Prefix.TrimQuotes();
				if (Path.GetLongPackageName() == Prefix || Path.GetLongPackageName().StartsWith(Prefix + TEXT("/"))) return true;
			}
		}
		return false;
#endif
	}
	TSharedPtr<const FEpoch> Compile(const TArray<FRPGCatalogBuild>& Builds, const TArray<FRPGCatalogWeapon>& Weapons, FString& Error, bool bResolveAssets)
	{
		Error.Reset();
		TSharedPtr<FEpoch> E = MakeShared<FEpoch>(); E->Id = FGuid::NewGuid(); E->Source = TEXT("data"); E->Builds = Builds; E->Weapons = Weapons;
		auto Fail = [&](const FString& Field) -> TSharedPtr<const FEpoch> { Error = Field; return nullptr; };
		if (Builds.IsEmpty() || Weapons.IsEmpty()) return Fail(TEXT("Catalog.Builds/Weapons: empty"));
		TSet<FName> WeaponIds; TMap<FName, FName> Styles;
		for (const auto& W : Weapons)
		{
			if (W.WeaponId.IsNone() || WeaponIds.Contains(W.WeaponId)) return Fail(TEXT("Weapons.WeaponId: empty/duplicate"));
			WeaponIds.Add(W.WeaponId);
			if (W.StyleName.IsNone() || W.ItemPath.IsNull() || W.HudWeaponWord.IsEmpty() || W.Actions.IsEmpty()) return Fail(W.WeaponId.ToString() + TEXT(".Style/Item/HudWord/Actions: required"));
			TArray<FName> AllStyles = W.StyleAliases; AllStyles.Add(W.StyleName);
			for (FName Style : AllStyles)
			{
				if (Style.IsNone() || (Styles.Contains(Style) && Styles[Style] != W.WeaponId)) return Fail(W.WeaponId.ToString() + TEXT(".StyleAliases: empty/conflict"));
				Styles.Add(Style, W.WeaponId);
			}
		}
		TSet<FName> BuildIds; TMap<FString, FName> Names; TSet<int32> Slots;
		for (const auto& B : Builds)
		{
			if (B.BuildId.IsNone() || BuildIds.Contains(B.BuildId) || !WeaponIds.Contains(B.WeaponId) || B.DisplayName.IsEmpty()) return Fail(TEXT("Builds.Id/WeaponId/DisplayName: invalid"));
			BuildIds.Add(B.BuildId);
			if (B.LegacySlot != INDEX_NONE && (B.LegacySlot < 0 || B.LegacySlot > 2 || Slots.Contains(B.LegacySlot))) return Fail(B.BuildId.ToString() + TEXT(".LegacySlot: invalid/duplicate"));
			if (B.LegacySlot != INDEX_NONE) Slots.Add(B.LegacySlot);
			TArray<FString> Keys = B.Aliases; Keys.Add(B.ConsoleName); Keys.Add(B.BuildId.ToString());
			for (const auto& Raw : Keys)
			{
				FString Key = Normalize(Raw);
				if (Key.IsEmpty() || Key == TEXT("none") || Key == TEXT("off") || (Names.Contains(Key) && Names[Key] != B.BuildId)) return Fail(B.BuildId.ToString() + TEXT(".Aliases: empty/reserved/collision"));
				Names.Add(Key, B.BuildId);
			}
		}
		if (Slots.Num() != 3) return Fail(TEXT("Builds.LegacySlot: three compatibility slots required"));
		const auto LegacyContract = Legacy();
		for (int32 I = 0; I < 3; ++I)
		{
			const auto* B = E->LegacySlot(I); const auto& L = RPGBuildRules::Entry(static_cast<ERPGBuild>(I));
			const auto* W = B ? E->Weapon(B->WeaponId) : nullptr;
			if (!B || !W || B->BuildId != FName(L.Name) || B->ConsoleName != L.Name || B->DisplayName != L.Name || B->UiOrder != I || W->StyleName != FName(L.Style) || W->ItemPath.ToString() != L.ItemPath || W->HudWeaponWord != L.Weapon || W->ActorClass.GetAssetName() != L.ActorClass || W->AbilityClass.GetAssetName() != L.AbilityClass) return Fail(TEXT("Builds.LegacySlot: pinned three-build contract changed"));
			const auto* LB = LegacyContract->LegacySlot(I); const auto* LW = LegacyContract->Weapon(LB->WeaponId);
			if (B->WeaponId != LB->WeaponId || B->Aliases != LB->Aliases || B->Icon != LB->Icon || W->StyleAliases != LW->StyleAliases || W->Actions != LW->Actions || W->ActorClass != LW->ActorClass || W->AbilityClass != LW->AbilityClass || W->StyleAsset != LW->StyleAsset || W->AliasHudWords.Num() != LW->AliasHudWords.Num()) return Fail(TEXT("Builds.LegacySlot: alias/icon/reference/action contract changed"));
			for (const auto& Pair : LW->AliasHudWords)
			{
				const FString* Word = W->AliasHudWords.Find(Pair.Key);
				if (!Word || *Word != Pair.Value) return Fail(TEXT("Builds.LegacySlot: special HUD alias changed"));
			}
		}
		if (bResolveAssets)
		{
			URPGWeaponAttackTable* Table = URPGWeaponAttackTable::LoadOrDefault(); E->Leases.Emplace(Table);
			for (const auto& W : Weapons)
			{
				auto Resolve = [&](const FSoftObjectPath& P) -> UObject*
				{
					if (P.IsNull() || !CookedDependency(P)) return nullptr;
					UObject* O = P.TryLoad(); if (O) E->Leases.Emplace(O); return O;
				};
				UObject* Item = Resolve(W.ItemPath);
				// A loaded item's ancestry is an implicit cooker dependency, not an always-cook directory.
				UClass* ItemBase = Cast<UClass>(W.ItemBaseClass.TryLoad()); if (ItemBase) E->Leases.Emplace(ItemBase);
				UClass* ActorClass = Cast<UClass>(Resolve(W.ActorClass)); UClass* AbilityClass = Cast<UClass>(Resolve(W.AbilityClass)); UObject* Style = Resolve(W.StyleAsset);
				if (!Item || !ItemBase || !Item->IsA(ItemBase) || !ActorClass || !ActorClass->IsChildOf(AActor::StaticClass()) || !AbilityClass || !Style || Style->GetFName() != W.StyleName) return Fail(W.WeaponId.ToString() + TEXT(".References: unresolved/wrong type/cook policy"));
				// Validate that the item actually references the declared actor/ability/style. Never find by base name.
				FString Wiring;
				for (UObject* Owner : {Item, ActorClass->GetDefaultObject(), Style})
					for (TFieldIterator<FProperty> It(Owner->GetClass()); It; ++It)
					{
						FString Value; It->ExportText_InContainer(0, Value, Owner, nullptr, Owner, PPF_None); Wiring += Value;
					}
				if (!Wiring.Contains(W.ActorClass.ToString()) || !Wiring.Contains(W.AbilityClass.ToString()) || !Wiring.Contains(W.StyleAsset.ToString())) return Fail(W.WeaponId.ToString() + TEXT(".References: item/actor/ability/style wiring not established"));
				if (auto* Resolved = E->Weapons.FindByPredicate([&W](const FRPGCatalogWeapon& Value) { return Value.WeaponId == W.WeaponId; })) Resolved->ReferenceProvenance = TEXT("loaded/type/wiring-text checked; live equip not yet observed");
				for (ERPGAttackKind Kind : W.Actions)
				{
					FCoverage C; C.WeaponId = W.WeaponId; C.Kind = Kind; Table->Find(W.StyleName, Kind, C.Effective); C.Route = TEXT("fallback");
					for (const auto& R : Table->Rows) if (R.Kind == Kind && R.Weapon.IsNone()) C.Route = TEXT("any");
					for (const auto& R : Table->Rows) if (R.Kind == Kind && R.Weapon == W.StyleName) C.Route = TEXT("exact");
					if (W.bRequireExactRows && C.Route != TEXT("exact")) return Fail(W.WeaponId.ToString() + TEXT(".Actions: required exact row missing"));
					if (C.Route != TEXT("exact")) UE_LOG(LogRPGCatalog, Warning, TEXT("%s/%s coverage=%s posture=%g stamina=%g bleed=%g health=%g"), *W.WeaponId.ToString(), RPGAttackKindName(Kind), *C.Route, C.Effective.PostureDamage, C.Effective.StaminaCost, C.Effective.BleedBuildup, C.Effective.HealthDamageMultiplier);
					E->Coverage.Add(MoveTemp(C));
				}
			}
			for (const auto& B : Builds) if (!B.Icon.IsNull())
			{
				UTexture2D* Icon = CookedDependency(B.Icon) ? Cast<UTexture2D>(B.Icon.TryLoad()) : nullptr;
				if (Icon) E->Leases.Emplace(Icon); else UE_LOG(LogRPGCatalog, Warning, TEXT("%s.Icon: broken/wrong-type/uncooked optional icon; text-only"), *B.BuildId.ToString());
			}
		}
		E->Builds.Sort([](const FRPGCatalogBuild& A, const FRPGCatalogBuild& B) { return A.UiOrder != B.UiOrder ? A.UiOrder < B.UiOrder : A.BuildId.LexicalLess(B.BuildId); });
		return E;
	}
	bool FContext::Publish(ESource Source, TSharedPtr<const FEpoch> Candidate, const FString& Failure)
	{
		if (bAttempted) return false;
		bAttempted = true;
		if (Source == ESource::Legacy) Epoch = Legacy();
		else if (Candidate) Epoch = Candidate;
		else if (Source == ESource::Auto) Epoch = Legacy();
		if (Source == ESource::Auto && !Candidate) UE_LOG(LogRPGCatalog, Warning, TEXT("catalog unavailable; COMPLETE legacy compatibility fallback: %s"), *Failure);
		// Data is strict. A null epoch disables its consumers, never falls back per lookup.
		if (Epoch)
		{
			UE_LOG(LogRPGCatalog, Display, TEXT("epoch=%s source=%s reason=%s"), *Epoch->Id.ToString(), *Epoch->Source, *Failure);
		}
		else
		{
			UE_LOG(LogRPGCatalog, Error, TEXT("data required: initialization failed: %s"), *Failure);
		}
		return Epoch.IsValid();
	}
	TSharedPtr<const FEpoch> ForWorld(const UWorld* World)
	{
		const UGameInstance* GI = World ? World->GetGameInstance() : nullptr;
		const auto* S = GI ? GI->GetSubsystem<URPGCombatCatalogSubsystem>() : nullptr;
		return S ? S->GetEpoch() : nullptr;
	}
	bool RowVisible(int32 Row, int32 Count, float Height) { return Row >= 0 && Row < Count && Height > 0.f && Height * .25f + 52.f + Row * 42.f + 42.f <= Height; }
	int32 VisibleRows(int32 Count, float Height) { int32 N = 0; while (RowVisible(N, Count, Height)) ++N; return N; }
}

void URPGCombatCatalogSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);
	using namespace RPGCombatRegistry;
	LatchedSource = TEXT("auto");
#if !UE_BUILD_SHIPPING
	LatchedSource = Normalize(CVarCatalogSource.GetValueOnGameThread());
#endif
	ESource Mode = LatchedSource == TEXT("legacy") ? ESource::Legacy : LatchedSource == TEXT("data") ? ESource::Data : ESource::Auto;
	TSharedPtr<const FEpoch> Candidate; FString Error;
	if (LatchedSource != TEXT("auto") && LatchedSource != TEXT("legacy") && LatchedSource != TEXT("data")) { Error = TEXT("CatalogSource: unknown mode"); Mode = ESource::Data; }
	else if (Mode != ESource::Legacy)
	{
		const FSoftObjectPath Path(TEXT("/Game/OneBossFight/Data/Catalog/DA_CombatCatalog.DA_CombatCatalog"));
		TStrongObjectPtr<URPGCombatCatalog> Catalog(Cast<URPGCombatCatalog>(Path.TryLoad()));
		if (!Catalog.IsValid() || Catalog->SchemaVersion != 1) Error = TEXT("Catalog.SchemaVersion/path: absent or unsupported");
		else
		{
			TArray<FRPGCatalogBuild> Builds; TArray<FRPGCatalogWeapon> Weapons;
			TArray<TStrongObjectPtr<UObject>> DefinitionLeases;
			for (const auto& Ref : Catalog->Builds) { auto* D = Ref.LoadSynchronous(); if (D) { DefinitionLeases.Emplace(D); Builds.Add(D->Definition); } else Error = TEXT("Catalog.Builds: missing definition"); }
			for (const auto& Ref : Catalog->Weapons) { auto* D = Ref.LoadSynchronous(); if (D) { DefinitionLeases.Emplace(D); Weapons.Add(D->Definition); } else Error = TEXT("Catalog.Weapons: missing definition"); }
			if (Error.IsEmpty()) Candidate = Compile(Builds, Weapons, Error);
		}
	}
#if !UE_BUILD_SHIPPING
	if (CVarCatalogInvalid.GetValueOnGameThread() != 0) { Candidate.Reset(); Error = TEXT("Catalog.SchemaVersion: deliberately invalid startup fixture"); }
	if (CVarCatalogFourth.GetValueOnGameThread() != 0 && Candidate)
	{
		// Startup-scoped fixture belongs to this GI; no global override or live mutation.
		auto Base = Candidate; auto Builds = Base->Builds;
		FRPGCatalogBuild B = Builds[0]; B.BuildId = TEXT("CatalogFourth"); B.ConsoleName = TEXT("CatalogFourth"); B.DisplayName = TEXT("Catalog Fourth"); B.Aliases.Reset(); B.LegacySlot = INDEX_NONE; B.UiOrder = 3; B.Icon.Reset(); Builds.Add(B);
		Candidate = Compile(Builds, Base->Weapons, Error, true);
		Mode = ESource::Data; // fixture cannot be mistaken for a legacy fallback success
	}
	else if (CVarCatalogFourth.GetValueOnGameThread() != 0) { Mode = ESource::Data; Error += TEXT("; fourth fixture requires a valid resolved data catalog"); }
#endif
	Context.Publish(Mode, Candidate, Error);
}
void URPGCombatCatalogSubsystem::Deinitialize() { Context = RPGCombatRegistry::FContext(); Super::Deinitialize(); }
TSharedPtr<const RPGCombatRegistry::FEpoch> URPGCombatCatalogSubsystem::GetEpoch() const
{
#if !UE_BUILD_SHIPPING
	if (!bLateChangeReported && RPGCombatRegistry::Normalize(CVarCatalogSource.GetValueOnGameThread()) != LatchedSource)
	{
		bLateChangeReported = true; UE_LOG(LogRPGCatalog, Warning, TEXT("CatalogSource changed: next session only"));
	}
#endif
	return Context.Get();
}
FString URPGCombatCatalogSubsystem::GetDiagnostic() const { auto E = GetEpoch(); return E ? FString::Printf(TEXT("%s:%s"), *E->Source, *E->Id.ToString()) : TEXT("unavailable:data required"); }
int32 URPGCombatCatalogSubsystem::GetBuildCount() const { auto E = GetEpoch(); return E ? E->Builds.Num() : 0; }
TArray<FString> URPGCombatCatalogSubsystem::GetCoverageLines() const
{
	TArray<FString> Lines; auto E = GetEpoch(); if (E) for (const auto& C : E->Coverage) Lines.Add(FString::Printf(TEXT("%s/%s=%s posture=%g stamina=%g bleed=%g health=%g"), *C.WeaponId.ToString(), RPGAttackKindName(C.Kind), *C.Route, C.Effective.PostureDamage, C.Effective.StaminaCost, C.Effective.BleedBuildup, C.Effective.HealthDamageMultiplier)); return Lines;
}
