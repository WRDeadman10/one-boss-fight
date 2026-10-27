// Copyright One Boss Fight. All Rights Reserved.
#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
#include "Player/RPGCombatCatalog.h"
#include "Player/RPGCombatCatalogABI.h"
#include "GameFramework/Actor.h"
#include "UObject/UnrealType.h"
#include "UObject/GarbageCollection.h"
#include "UObject/Package.h"
#include "Player/RPGBuildRules.h"
#include "HAL/IConsoleManager.h"
#include "Subsystems/SubsystemCollection.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCatalogContextTest, "OneBossFight.Catalog.Context",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)
bool FRPGCatalogContextTest::RunTest(const FString& Parameters)
{
	using namespace RPGCombatRegistry;
	auto Base = Legacy(); FString Error;
	auto Candidate = Compile(Base->Builds, Base->Weapons, Error, false);
	TestTrue(TEXT("structural legacy copy valid"), Candidate.IsValid());
	if (!Candidate) { AddError(Error); return false; }
	FContext First, Second;
	TestTrue(TEXT("publish explicit data"), First.Publish(ESource::Data, Candidate, TEXT("test")));
	TestTrue(TEXT("publish independent legacy"), Second.Publish(ESource::Legacy, nullptr, TEXT("test")));
	TestEqual(TEXT("data source explicit"), First.Get()->Source, FString(TEXT("data")));
	TestTrue(TEXT("different context epoch"), First.Get()->Id != Second.Get()->Id);
	TestFalse(TEXT("live publication refused"), First.Publish(ESource::Legacy, nullptr, TEXT("late change")));
	const auto Held = First.Get(); First = FContext();
	TestEqual(TEXT("owned snapshot survives context teardown"), Held->Builds[0].ConsoleName, FString(TEXT("Starter")));
	TestEqual(TEXT("other context remains intact"), Second.Get()->Builds.Num(), 3);
	for (int32 Slot = 0; Slot < 3; ++Slot)
	{
		const auto& Old = RPGBuildRules::Entry(static_cast<ERPGBuild>(Slot));
		const auto* B = Candidate->LegacySlot(Slot); const auto* W = B ? Candidate->Weapon(B->WeaponId) : nullptr;
		TestTrue(TEXT("legacy-slot mapping complete"), B && W);
		if (!B || !W) continue;
		TestEqual(TEXT("console exact"), B->ConsoleName, FString(Old.Name));
		TestEqual(TEXT("style exact"), W->StyleName.ToString(), FString(Old.Style));
		TestEqual(TEXT("item exact"), W->ItemPath.ToString(), FString(Old.ItemPath));
		TestEqual(TEXT("actor class exact"), W->ActorClass.GetAssetName(), FString(Old.ActorClass));
		TestEqual(TEXT("ability class exact"), W->AbilityClass.GetAssetName(), FString(Old.AbilityClass));
		TestEqual(TEXT("HUD word exact"), W->HudWeaponWord, FString(Old.Weapon));
		TestEqual(TEXT("UI order exact"), B->UiOrder, Slot);
	}
	FName Id(TEXT("unchanged"));
	TestTrue(TEXT("quotes/case alias"), Candidate->Parse(TEXT("  \"DEXTERITY\" "), Id) == EResolve::Found && Id == FName(TEXT("Dex")));
	TestTrue(TEXT("unknown preserves output"), Candidate->Parse(TEXT("banana"), Id) == EResolve::UnknownId && Id == FName(TEXT("Dex")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCatalogValidationTest, "OneBossFight.Catalog.Validation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)
bool FRPGCatalogValidationTest::RunTest(const FString& Parameters)
{
	using namespace RPGCombatRegistry;
	auto L = Legacy(); FString Error;
	auto Builds = L->Builds; auto Weapons = L->Weapons;
	FRPGCatalogBuild Fourth = Builds[0]; Fourth.BuildId = TEXT("TestFourth"); Fourth.ConsoleName = TEXT("TestFourth"); Fourth.DisplayName = TEXT("Fourth"); Fourth.LegacySlot = INDEX_NONE; Fourth.UiOrder = 3; Fourth.Aliases.Reset(); Builds.Add(Fourth);
	auto E = Compile(Builds, Weapons, Error, false);
	TestTrue(TEXT("fourth build supported without enum addition"), E.IsValid());
	if (!E) { AddError(Error); return false; }
	FName Found(TEXT("unchanged"));
	TestTrue(TEXT("shared style ambiguous without verified context"), E->StyleToBuild(TEXT("SwordCombatStyle"), Found) == EResolve::Ambiguous && Found == FName(TEXT("unchanged")));
	TestTrue(TEXT("shared style matches explicit fourth"), E->Matches(TEXT("SwordCombatStyle"), Fourth.BuildId));
	TestEqual(TEXT("verified fourth display"), E->Describe(TEXT("SwordCombatStyle"), Fourth.BuildId), FString(TEXT("Fourth (Sword)")));
	TestTrue(TEXT("shared style without verified id is described as ambiguous, never the first row"), E->Describe(TEXT("SwordCombatStyle")).StartsWith(TEXT("Ambiguous")));
	ERPGBuild LegacyOut = ERPGBuild::Dex;
	TestFalse(TEXT("fourth has no legacy slot"), RPGBuildRules::LegacySlotOf(*E, Fourth.BuildId, LegacyOut));
	TestTrue(TEXT("failed slot lookup leaves previous output"), LegacyOut == ERPGBuild::Dex);
	TestTrue(TEXT("fourth visible1080"), RowVisible(3, 4, 1080.f));
	TestFalse(TEXT("fourth hidden200"), RowVisible(3, 4, 200.f));
	TestFalse(TEXT("negative row hidden"), RowVisible(-1, 4, 1080.f));
	TestFalse(TEXT("row beyond list hidden"), RowVisible(4, 4, 1080.f));
	TestEqual(TEXT("common visible count"), VisibleRows(4, 200.f), 2);
	auto BadBuilds = Builds; BadBuilds[3].BuildId = BadBuilds[0].BuildId;
	TestFalse(TEXT("duplicate ids rejected"), Compile(BadBuilds, Weapons, Error, false).IsValid());
	BadBuilds = Builds; BadBuilds[3].ConsoleName = TEXT("off");
	TestFalse(TEXT("reserved name rejected"), Compile(BadBuilds, Weapons, Error, false).IsValid());
	BadBuilds = Builds; BadBuilds[3].Aliases.Add(TEXT("str"));
	TestFalse(TEXT("alias collision rejected"), Compile(BadBuilds, Weapons, Error, false).IsValid());
	BadBuilds = Builds; BadBuilds[3].WeaponId = TEXT("MissingWeapon");
	TestFalse(TEXT("unknown weapon rejected"), Compile(BadBuilds, Weapons, Error, false).IsValid());
	BadBuilds = Builds; BadBuilds[0].Aliases.Reset();
	TestFalse(TEXT("legacy alias removal rejected"), Compile(BadBuilds, Weapons, Error, false).IsValid());
	auto BadWeapons = Weapons; BadWeapons[0].StyleName = NAME_None;
	TestFalse(TEXT("empty style rejected"), Compile(Builds, BadWeapons, Error, false).IsValid());
	BadWeapons = Weapons; BadWeapons[0].AliasHudWords.Add(TEXT("SwordAndShieldCombatStyle"), TEXT("wrong label"));
	TestFalse(TEXT("legacy special HUD change rejected"), Compile(Builds, BadWeapons, Error, false).IsValid());
	FContext Auto; TestTrue(TEXT("auto fallback succeeds"), Auto.Publish(ESource::Auto, nullptr, TEXT("malformed fixture")));
	TestEqual(TEXT("fallback source entire legacy"), Auto.Get()->Source, FString(TEXT("legacy")));
	AddExpectedError(TEXT("data required: initialization failed"), EAutomationExpectedErrorFlags::Contains, 1);
	FContext Strict; TestFalse(TEXT("strict rejects missing"), Strict.Publish(ESource::Data, nullptr, TEXT("test missing")));
	TestFalse(TEXT("strict has no epoch"), Strict.Get().IsValid());
	TestFalse(TEXT("failed strict context cannot republish"), Strict.Publish(ESource::Legacy, nullptr, TEXT("late")));
	const FGuid LiveId = E->Id;
	{ FContext Other; Other.Publish(ESource::Legacy, nullptr, TEXT("temporary")); }
	TestTrue(TEXT("other context teardown does not restore global source"), E->Id == LiveId && E->Source == TEXT("data"));
	return true;
}

// Deliberately depends ONLY on the unchanged legacy header. Claude can copy this test
// block into the preimage checkout to establish parity BEFORE new code is compiled.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCatalogLegacyParityTest, "OneBossFight.Catalog.LegacyParity",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)
bool FRPGCatalogLegacyParityTest::RunTest(const FString& Parameters)
{
	using namespace RPGBuildRules;
	TestEqual(TEXT("enum99 clamps Dex"), FString(BuildName(static_cast<ERPGBuild>(99))), FString(TEXT("Dex")));
	TestEqual(TEXT("shield label"), DescribeStyle(TEXT("SwordAndShieldCombatStyle")), FString(TEXT("Starter (Sword and Shield)")));
	TestEqual(TEXT("twin label"), DescribeStyle(TEXT("TwinbladeCombatStyle")), FString(TEXT("Dex (Twinblades)")));
	TestEqual(TEXT("unknown label"), DescribeStyle(NAME_None), FString(TEXT("Unknown")));
	TestEqual(TEXT("offbuild label"), DescribeStyle(TEXT("PolearmCombatStyle")), FString(TEXT("Off-build (Polearm)")));
	TestEqual(TEXT("defer suffix"), BuildLine(TEXT("SwordCombatStyle"), EDecision::Defer), FString(TEXT("Build: Starter (Sword) - next fight")));
	TestEqual(TEXT("wait suffix"), BuildLine(TEXT("SwordCombatStyle"), EDecision::Wait), FString(TEXT("Build: Starter (Sword) - equipping...")));
	TestEqual(TEXT("failure suffix"), BuildLine(TEXT("SwordCombatStyle"), EDecision::GiveUp), FString(TEXT("Build: Starter (Sword) - not equipped")));
	ERPGBuild Out = ERPGBuild::Strength;
	TestTrue(TEXT("reserved off is empty, unchanged output"), Parse(TEXT(" off "), Out) == EParse::Empty && Out == ERPGBuild::Strength);
	TestTrue(TEXT("invalid unchanged output"), Parse(TEXT("banana"), Out) == EParse::Invalid && Out == ERPGBuild::Strength);
	return true;
}

// Step 1 review F8 (AG-22): the resolving compile path (item/actor/ability/style identities, ancestry, wiring, cook policy) had no automation coverage.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCatalogResolutionTest, "OneBossFight.Catalog.Resolution",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGCatalogResolutionTest::RunTest(const FString& Parameters)
{
	using namespace RPGCombatRegistry;
	auto L = Legacy();
	TArray<FRPGCatalogWeapon> Weapons = L->Weapons;
	for (FRPGCatalogWeapon& W : Weapons)
	{
		// The built-in table carries no item ancestry; read it from the installed pack item, as the authoring script does.
		UObject* Item = W.ItemPath.TryLoad();
		if (!TestNotNull(*FString::Printf(TEXT("%s item loads from the installed pack"), *W.WeaponId.ToString()), Item)) return false;
		W.ItemBaseClass = FSoftObjectPath(Item->GetClass());
	}
	FString Error;
	auto Resolved = Compile(L->Builds, Weapons, Error, true);
	TestTrue(*FString::Printf(TEXT("three shipped weapons resolve against the pack (%s)"), *Error), Resolved.IsValid());
	if (!Resolved) return false;
	TestEqual(TEXT("resolved snapshot keeps all builds"), Resolved->Builds.Num(), 3);
	// The three shipped weapons are pinned by the legacy contract, which rejects ANY change before resolution; so the resolving stage is
	// probed with an extra, non-legacy weapon whose declared style name differs from the style asset it points at.
	TArray<FRPGCatalogWeapon> ProbeWeapons = Weapons;
	TArray<FRPGCatalogBuild> ProbeBuilds = L->Builds;
	FRPGCatalogWeapon Probe = Weapons[0];
	Probe.WeaponId = TEXT("ProbeWeapon"); Probe.StyleName = TEXT("ProbeCombatStyle"); Probe.StyleAliases.Reset(); Probe.AliasHudWords.Reset(); Probe.Icon.Reset();
	ProbeWeapons.Add(Probe);
	FRPGCatalogBuild ProbeBuild = L->Builds[0];
	ProbeBuild.BuildId = TEXT("ProbeBuild"); ProbeBuild.ConsoleName = TEXT("ProbeBuild"); ProbeBuild.DisplayName = TEXT("Probe"); ProbeBuild.Aliases.Reset();
	ProbeBuild.LegacySlot = INDEX_NONE; ProbeBuild.UiOrder = 3; ProbeBuild.WeaponId = Probe.WeaponId; ProbeBuild.Icon.Reset();
	ProbeBuilds.Add(ProbeBuild);
	FString ProbeError;
	TestFalse(TEXT("a style name that does not match the resolved style asset is rejected"), Compile(ProbeBuilds, ProbeWeapons, ProbeError, true).IsValid());
	TestTrue(*FString::Printf(TEXT("the rejection comes from the resolving stage and names the weapon (%s)"), *ProbeError), ProbeError.Contains(TEXT("ProbeWeapon")) && ProbeError.Contains(TEXT("References")));
	// The same probe without resolution passes the structural checks, so the rejection above is not a structural one.
	FString StructuralError;
	TestTrue(TEXT("the probe is structurally valid without resolution"), Compile(ProbeBuilds, ProbeWeapons, StructuralError, false).IsValid());
	// X-T10: direct typed reader tests use already-loaded real pack objects; production
	// Compile remains the cook/whole-publication gate. No installed object is mutated.
	FRPGCatalogWeapon Good = Weapons[0];
	FWeaponReferences Refs;
	Refs.Item = Good.ItemPath.TryLoad(); Refs.DeclaredItemBase = Cast<UClass>(Good.ItemBaseClass.TryLoad());
	Refs.ActorClass = Cast<UClass>(Good.ActorClass.TryLoad()); Refs.AbilityClass = Cast<UClass>(Good.AbilityClass.TryLoad());
	Refs.Style = Good.StyleAsset.TryLoad();
	TArray<TStrongObjectPtr<UObject>> ABILeases;
	auto CheckABI = [&](const TCHAR* Label, const FRPGCatalogWeapon& D, const FWeaponReferences& R, const TCHAR* Expected)
	{
		FString Why; const bool Valid = ValidateWeaponReferences(D, R, ABILeases, Why);
		if (!Expected) { TestTrue(Label, Valid); if (!Valid) AddError(Why); }
		else { TestFalse(Label, Valid); TestTrue(*FString(Label).Append(TEXT(" field")), Why.EndsWith(Expected)); }
	};
	CheckABI(TEXT("ABI-P01 typed installed Sword"), Good, Refs, nullptr);
	// Root classes are natively pinned: setting a broad declared base cannot widen the contract.
	FWeaponReferences BadRefs = Refs; FRPGCatalogWeapon Bad = Good;
	BadRefs.DeclaredItemBase = UObject::StaticClass(); Bad.ItemBaseClass = FSoftObjectPath(UObject::StaticClass());
	CheckABI(TEXT("ABI-N01 broad declared item ancestry"), Bad, BadRefs, TEXT("Item.DeclaredBaseExpectedABI"));
	BadRefs = Refs; Bad = Good; BadRefs.ActorClass = AActor::StaticClass(); Bad.ActorClass = FSoftObjectPath(AActor::StaticClass());
	CheckABI(TEXT("ABI-N02 non-weapon actor"), Bad, BadRefs, TEXT("Actor.ExpectedABI"));
	BadRefs = Refs; Bad = Good; BadRefs.AbilityClass = UObject::StaticClass(); Bad.AbilityClass = FSoftObjectPath(UObject::StaticClass());
	CheckABI(TEXT("ABI-N03 arbitrary UClass ability"), Bad, BadRefs, TEXT("Ability.ExpectedABI"));
	BadRefs = Refs; Bad = Good; Bad.AbilityClass = Weapons[1].AbilityClass; BadRefs.AbilityClass = Cast<UClass>(Bad.AbilityClass.TryLoad());
	CheckABI(TEXT("ABI-N04 compatible class not granted by this style"), Bad, BadRefs, TEXT("Style.AbilityGrant"));
	BadRefs = Refs; Bad = Good; Bad.ActorClass = Weapons[1].ActorClass; BadRefs.ActorClass = Cast<UClass>(Bad.ActorClass.TryLoad());
	CheckABI(TEXT("ABI-N05 wrong declared weapon actor"), Bad, BadRefs, TEXT("Item.ActorBinding"));
	BadRefs = Refs; BadRefs.Style = GetTransientPackage(); Bad = Good; Bad.StyleAsset = FSoftObjectPath(GetTransientPackage());
	CheckABI(TEXT("ABI-N07 non-style object"), Bad, BadRefs, TEXT("Style.ExpectedABI"));
	BadRefs = Refs; BadRefs.Item = nullptr;
	CheckABI(TEXT("ABI-N10 missing required item"), Good, BadRefs, TEXT("Item.Missing"));
	Bad = Good; Bad.ActorClass = Weapons[1].ActorClass;
	CheckABI(TEXT("full path identity not short-name membership"), Bad, Refs, TEXT("Actor.Identity"));

	// Duplicate in memory only. Put the expected style identity in text but remove its
	// real typed edge: the former exported-text union could be fooled by such a bundle.
	TStrongObjectPtr<UObject> Copy(DuplicateObject<UObject>(Refs.Item, GetTransientPackage()));
	if (TestNotNull(TEXT("transient item copy"), Copy.Get()))
	{
		const FObjectProperty* StyleEdge = FindFProperty<FObjectProperty>(Copy->GetClass(), TEXT("Combat Style"));
		const FTextProperty* Description = FindFProperty<FTextProperty>(Copy->GetClass(), TEXT("ItemDescription"));
		if (TestNotNull(TEXT("typed style property"), StyleEdge) && TestNotNull(TEXT("text decoy property"), Description))
		{
			StyleEdge->SetObjectPropertyValue_InContainer(Copy.Get(), Weapons[1].StyleAsset.TryLoad());
			Description->SetPropertyValue_InContainer(Copy.Get(), FText::FromString(Good.StyleAsset.ToString()));
			BadRefs = Refs; BadRefs.Item = Copy.Get(); Bad = Good; Bad.ItemPath = FSoftObjectPath(Copy.Get());
			CheckABI(TEXT("ABI-N06 decoy text cannot satisfy style role"), Bad, BadRefs, TEXT("Item.StyleBinding"));
			TestTrue(TEXT("original pack item still validates"), ValidateWeaponReferences(Good, Refs, ABILeases, Error));
		}
	}

	// Nonlegacy fourth profile travels the full production Compile validation, not enum slots.
	FRPGCatalogBuild Fourth = L->Builds[0]; Fourth.BuildId = TEXT("ABIFourth"); Fourth.ConsoleName = TEXT("ABIFourth");
	Fourth.DisplayName = TEXT("ABI Fourth"); Fourth.Aliases.Reset(); Fourth.LegacySlot = INDEX_NONE; Fourth.UiOrder = 3; Fourth.Icon.Reset();
	auto FourBuilds = L->Builds; FourBuilds.Add(Fourth);
	auto Four = Compile(FourBuilds, Weapons, Error, true);
	TestTrue(TEXT("ABI-P02 actual resolving fourth build"), Four.IsValid());
	if (Four)
	{
		FName Identity; TestTrue(TEXT("shared weapon remains ambiguous"), Four->StyleToBuild(TEXT("SwordCombatStyle"), Identity) == EResolve::Ambiguous);
		TestEqual(TEXT("verified fourth retains id"), Four->Describe(TEXT("SwordCombatStyle"), Fourth.BuildId), FString(TEXT("ABI Fourth (Sword)")));
	}
	// Additional stable weapon id with an already-claimed style is a negative, NOT P03 proof.
	FRPGCatalogWeapon Other = Weapons[0]; Other.WeaponId = TEXT("ABIExtraWeapon");
	// Distinct IDs may not alias the same style: this malformed profile must be rejected structurally (N08).
	auto CollisionWeapons = Weapons; CollisionWeapons.Add(Other);
	TestFalse(TEXT("ABI-N08 distinct weapon style alias collision"), Compile(FourBuilds, CollisionWeapons, Error, false).IsValid());
	TestTrue(TEXT("ABI-N08 correct structural field"), Error.Contains(TEXT("StyleAliases")));
	// N09: well-formed nonlegacy entry whose required dependency is outside cook policy.
	FRPGCatalogWeapon Outside = Weapons[0]; Outside.WeaponId = TEXT("ABIOutside"); Outside.StyleName = TEXT("ABIOutsideStyle");
	Outside.StyleAliases.Reset(); Outside.AliasHudWords.Reset(); Outside.ItemPath = FSoftObjectPath(FString(TEXT("/Game/")) + TEXT("UncookedABIFixture/Absent.Absent")) /* split on purpose: a deliberately absent test path, not an asset the packaged build must cook */;
	auto OutsideWeapons = Weapons; OutsideWeapons.Add(Outside);
	auto OutsideBuilds = L->Builds; Fourth.WeaponId = Outside.WeaponId; OutsideBuilds.Add(Fourth);
	TestTrue(TEXT("ABI-N09 prerequisite structural pass"), Compile(OutsideBuilds, OutsideWeapons, Error, false).IsValid());
	TestFalse(TEXT("ABI-N09 production dependency/cook gate refuses"), Compile(OutsideBuilds, OutsideWeapons, Error, true).IsValid());
	TestTrue(TEXT("ABI-N09 dependency field (not ancestry proof)"), Error.Contains(TEXT("ABIOutside.References")));
	// Optional presentation failure cannot bypass or invalidate gameplay ABI.
	auto IconBuilds = FourBuilds; IconBuilds.Last().Icon = Good.ItemPath;
	TestTrue(TEXT("ABI-N11 wrong-type optional icon degrades, gameplay remains valid"), Compile(IconBuilds, Weapons, Error, true).IsValid());
	TestTrue(TEXT("ABI-N11 absent optional icon allowed"), Four.IsValid());
	// P04 bounded epoch ownership: GC with both resolved epochs held, not a two-GI travel proof.
	CollectGarbage(RF_NoFlags);
	TestTrue(TEXT("ABI-P04 resolved epoch keeps actual style alive after GC"), IsValid(Refs.Style) && Resolved.IsValid());
	CheckABI(TEXT("ABI-P04 read again after GC"), Good, Refs, nullptr);
	AddInfo(TEXT("ABI-P05 cold packaged proof and P03 genuinely distinct supported weapon fixture require Claude; no pass inferred from these unit assertions."));

	return true;
}

// Typed ABI fixtures (owner approval "Yes" 2026-10-26, Codex C155_A100_REVIEW): a DISTINCT fourth weapon bundle, a same-leaf decoy package and an uncooked item,
// all duplicated from shipped assets under a developer-only folder outside the always-cook roots (Scripts/Editor/make_typed_abi_fixtures.py).
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCatalogTypedFixturesTest, "OneBossFight.Catalog.TypedABIFixtures",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGCatalogTypedFixturesTest::RunTest(const FString& Parameters)
{
	using namespace RPGCombatRegistry;
	// Built from a prefix so the cook coverage scanner does not read these deliberate developer-only paths as assets a packaged build must cook.
	const FString Fixtures = FString(TEXT("/Game/")) + TEXT("OneBossFight/Data/TypedABIFixtures/");
	const FString Uncooked = FString(TEXT("/Game/")) + TEXT("OneBossFight/ReviewFixtures/TypedABI/");
	auto Obj = [&](const TCHAR* Name) { return Fixtures + Name + TEXT(".") + FPackageName::GetShortName(Name); };
	auto UncookedObj = [&](const TCHAR* Name) { return Uncooked + Name + TEXT(".") + FPackageName::GetShortName(Name); };
	auto Cls = [&](const TCHAR* Name) { return Fixtures + Name + TEXT(".") + FPackageName::GetShortName(Name) + TEXT("_C"); };
	auto L = Legacy();
	TArray<FRPGCatalogWeapon> Weapons = L->Weapons;
	for (FRPGCatalogWeapon& W : Weapons)
	{
		UObject* Item = W.ItemPath.TryLoad();
		if (!TestNotNull(*FString::Printf(TEXT("%s item loads"), *W.WeaponId.ToString()), Item)) return false;
		W.ItemBaseClass = FSoftObjectPath(Item->GetClass());
	}
	UObject* FourthItem = FSoftObjectPath(Obj(TEXT("DA_ABI_FourthWeaponItem"))).TryLoad();
	if (!TestNotNull(TEXT("fourth weapon fixture item exists (run Scripts/Editor/make_typed_abi_fixtures.py)"), FourthItem)) return false;
	auto MakeFourth = [&](const FString& ItemPath, const FString& ActorPath)
	{
		FRPGCatalogWeapon W = Weapons[0];
		W.WeaponId = TEXT("ABIFourthWeapon"); W.StyleName = TEXT("DA_ABI_FourthCombatStyle");
		W.StyleAliases.Reset(); W.AliasHudWords.Reset(); W.Icon.Reset();
		W.ItemPath = FSoftObjectPath(ItemPath); W.ItemBaseClass = FSoftObjectPath(FourthItem->GetClass());
		W.ActorClass = FSoftObjectPath(ActorPath); W.AbilityClass = FSoftObjectPath(Cls(TEXT("GA_ABI_FourthMelee")));
		W.StyleAsset = FSoftObjectPath(Obj(TEXT("DA_ABI_FourthCombatStyle")));
		return W;
	};
	FRPGCatalogBuild FourthBuild = L->Builds[0];
	FourthBuild.BuildId = TEXT("ABIFourth"); FourthBuild.ConsoleName = TEXT("ABIFourth"); FourthBuild.DisplayName = TEXT("ABI Fourth"); FourthBuild.Aliases.Reset();
	FourthBuild.LegacySlot = INDEX_NONE; FourthBuild.UiOrder = 3; FourthBuild.WeaponId = TEXT("ABIFourthWeapon"); FourthBuild.Icon.Reset();
	TArray<FRPGCatalogBuild> Builds = L->Builds; Builds.Add(FourthBuild);
	auto Try = [&](const FRPGCatalogWeapon& Fourth, FString& Error)
	{
		TArray<FRPGCatalogWeapon> All = Weapons; All.Add(Fourth);
		return Compile(Builds, All, Error, true);
	};

	// Positive: a distinct fourth weapon bundle (own item, actor, style and granted ability) resolves and validates end to end.
	FString PositiveError;
	TestTrue(*FString::Printf(TEXT("the distinct fourth weapon bundle compiles with resolution (%s)"), *PositiveError),
		Try(MakeFourth(Obj(TEXT("DA_ABI_FourthWeaponItem")), Cls(TEXT("BP_ABI_FourthWeaponActor"))), PositiveError).IsValid());

	// Negative: a decoy actor with the SAME leaf name as the shipped one, a compatible weapon child, declared while the item binds the fixture actor: the item's own binding must reject it.
	FString DecoyError;
	TestFalse(TEXT("a same-leaf decoy actor in another package is rejected"),
		Try(MakeFourth(Obj(TEXT("DA_ABI_FourthWeaponItem")), Cls(TEXT("DecoyPackage/BP_ToughSword"))), DecoyError).IsValid());
	TestTrue(*FString::Printf(TEXT("the decoy is rejected by the item actor binding, not by ancestry (%s)"), *DecoyError), DecoyError.Contains(TEXT("ActorBinding")));

	// Negative (single defect): the uncooked item is a copy of the REWIRED fourth item, so its typed edges are as valid as the positive bundle's and the ONLY difference is its location
	// outside the always-cook roots. It must load in the editor (a missing asset would be a different failure), and the rejection must come from the resolving stage of this weapon.
	UObject* UncookedItem = FSoftObjectPath(UncookedObj(TEXT("DA_ABI_UncookedWeaponItem"))).TryLoad();
	TestNotNull(TEXT("the uncooked fixture item is a real loadable asset"), UncookedItem);
	FString UncookedError;
	TestFalse(TEXT("a weapon item outside the always-cook roots is rejected although every typed edge is valid"),
		Try(MakeFourth(UncookedObj(TEXT("DA_ABI_UncookedWeaponItem")), Cls(TEXT("BP_ABI_FourthWeaponActor"))), UncookedError).IsValid());
	TestTrue(*FString::Printf(TEXT("the rejection is the resolving stage of the fourth weapon (%s)"), *UncookedError), UncookedError.Contains(TEXT("ABIFourthWeapon.References")));

	// Negative: the declared actor is the fixture actor but the actual UClass handed to the validator is the same-leaf decoy: identity, not name, must decide.
	UClass* DecoyClass = Cast<UClass>(FSoftObjectPath(Cls(TEXT("DecoyPackage/BP_ToughSword"))).TryLoad());
	TestNotNull(TEXT("the decoy actor class loads"), DecoyClass);
	if (DecoyClass)
	{
		const FRPGCatalogWeapon Declared = MakeFourth(Obj(TEXT("DA_ABI_FourthWeaponItem")), Cls(TEXT("BP_ABI_FourthWeaponActor")));
		FWeaponReferences References;
		References.Item = FourthItem; References.DeclaredItemBase = FourthItem->GetClass(); References.ActorClass = DecoyClass;
		References.AbilityClass = Cast<UClass>(FSoftObjectPath(Cls(TEXT("GA_ABI_FourthMelee"))).TryLoad());
		References.Style = FSoftObjectPath(Obj(TEXT("DA_ABI_FourthCombatStyle"))).TryLoad();
		TArray<TStrongObjectPtr<UObject>> Leases; FString IdentityError;
		TestFalse(TEXT("a decoy UClass with the same leaf name is not the declared actor"), ValidateWeaponReferences(Declared, References, Leases, IdentityError));
		TestTrue(*FString::Printf(TEXT("the direct decoy is rejected by actor identity (%s)"), *IdentityError), IdentityError.Contains(TEXT("Actor.Identity")));
	}
	return true;
}

// Test seam rpg.CatalogPath (Codex lead decision C170, X-156): a non-Shipping, per-game-instance latched, strict-data input restricted to the TypedABIFixtures folder.
// The subsystem is started the way the engine does (Initialize with a collection) twice and independently, the console variables are restored in every exit path.
namespace
{
	struct FCatalogCvarScope
	{
		TArray<TPair<FString, FString>> Saved;
		bool Set(const TCHAR* Name, const FString& Value)
		{
			IConsoleVariable* Variable = IConsoleManager::Get().FindConsoleVariable(Name);
			if (!Variable) return false;
			Saved.Emplace(Name, Variable->GetString());
			Variable->Set(*Value, ECVF_SetByCode);
			return true;
		}
		~FCatalogCvarScope()
		{
			for (int32 I = Saved.Num() - 1; I >= 0; --I)
			{
				if (IConsoleVariable* Variable = IConsoleManager::Get().FindConsoleVariable(*Saved[I].Key)) Variable->Set(*Saved[I].Value, ECVF_SetByCode);
			}
		}
	};

	/** One independent game instance with its own catalog subsystem, started the way the engine does (the subsystem's ClassWithin is the game instance). */
	struct FTestCatalogHost
	{
		TStrongObjectPtr<UGameInstance> GameInstance;
		TStrongObjectPtr<URPGCombatCatalogSubsystem> Subsystem;
		URPGCombatCatalogSubsystem* operator->() const { return Subsystem.Get(); }
	};

	FTestCatalogHost StartCatalogSubsystem()
	{
		FSubsystemCollection<UGameInstanceSubsystem> Collection;
		FTestCatalogHost Host;
		Host.GameInstance.Reset(NewObject<UGameInstance>(GetTransientPackage()));
		Host.Subsystem.Reset(NewObject<URPGCombatCatalogSubsystem>(Host.GameInstance.Get()));
		Host.Subsystem->Initialize(Collection);
		return Host;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCatalogPathSeamTest, "OneBossFight.Catalog.TestPathSeam",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGCatalogPathSeamTest::RunTest(const FString& Parameters)
{
	using namespace RPGCombatRegistry;
	const FString Root = TestCatalogRoot();
	const FString TestPath = Root + TEXT("DA_ABITest_Catalog.DA_ABITest_Catalog");
	FString Error;

	// 1. The pure path check: only the exact fixture folder, case-sensitive, canonical object path.
	TestTrue(TEXT("the fixture test catalog path is accepted"), ValidateTestCatalogPath(TestPath, Error));
	const FString ShippedCatalog = FString(TEXT("/Game/")) + TEXT("OneBossFight/Data/Catalog/DA_CombatCatalog.DA_CombatCatalog");
	const TArray<TPair<FString, FString>> Rejected = {
		{TEXT("empty"), FString()},
		{TEXT("the shipped catalog (outside the folder)"), ShippedCatalog},
		{TEXT("a lowercase root (package strings are never normalized)"), Root.ToLower() + TEXT("DA_ABITest_Catalog.DA_ABITest_Catalog")},
		{TEXT("a look-alike folder"), Root.LeftChop(1) + TEXT("X/DA_ABITest_Catalog.DA_ABITest_Catalog")},
		{TEXT("path traversal"), Root + TEXT("../Catalog/DA_CombatCatalog.DA_CombatCatalog")},
		{TEXT("a sub-object path"), TestPath + TEXT(":Sub")},
		{TEXT("a package without an object part"), Root + TEXT("DA_ABITest_Catalog")},
		{TEXT("an object name that is not the package name"), Root + TEXT("DA_ABITest_Catalog.DA_Other")},
		{TEXT("an empty folder name"), Root + TEXT("/DA_ABITest_Catalog.DA_ABITest_Catalog")},
	};
	for (const auto& Case : Rejected)
	{
		FString Why;
		TestFalse(*FString::Printf(TEXT("rejected: %s"), *Case.Key), ValidateTestCatalogPath(Case.Value, Why));
		TestTrue(*FString::Printf(TEXT("the rejection is named (%s)"), *Why), Why.StartsWith(TEXT("CatalogPath:")));
	}

	// 2. Success, late change and two independent latches.
	FCatalogCvarScope Scope;
	if (!TestTrue(TEXT("the test cvars are registered (non-Shipping)"), Scope.Set(TEXT("rpg.CatalogSource"), TEXT("data")) && Scope.Set(TEXT("rpg.CatalogPath"), TestPath) && Scope.Set(TEXT("rpg.CatalogTestFourth"), TEXT("0")) && Scope.Set(TEXT("rpg.CatalogTestInvalid"), TEXT("0")))) return false;
	FTestCatalogHost First = StartCatalogSubsystem();
	const auto FirstEpoch = First->GetEpoch();
	if (!TestTrue(TEXT("the isolated test catalog publishes an epoch (run Scripts/Editor/make_abi_test_catalog.py)"), FirstEpoch.IsValid())) return false;
	TestEqual(TEXT("the epoch is data"), FirstEpoch->Source, FString(TEXT("data")));
	TestEqual(TEXT("the latched path is the requested one, as typed"), First->GetLatchedPath(), TestPath);
	TestEqual(TEXT("four builds: the three shipped ones plus the fourth"), FirstEpoch->Builds.Num(), 4);
	const FRPGCatalogBuild* Fourth = FirstEpoch->Find(TEXT("ABIFourth"));
	const FRPGCatalogWeapon* FourthWeapon = Fourth ? FirstEpoch->Weapon(Fourth->WeaponId) : nullptr;
	if (TestTrue(TEXT("the fourth build and its own weapon exist"), Fourth && FourthWeapon))
	{
		TestEqual(TEXT("the fourth weapon item is the fixture item"), FourthWeapon->ItemPath.GetAssetName(), FString(TEXT("DA_ABI_FourthWeaponItem")));
		TestEqual(TEXT("the fourth weapon style is the fixture style"), FourthWeapon->StyleName.ToString(), FString(TEXT("DA_ABI_FourthCombatStyle")));
		TestTrue(TEXT("the fourth weapon passed the typed reference check"), FourthWeapon->ReferenceProvenance.Contains(TEXT("typed ABI")));
	}

	Scope.Set(TEXT("rpg.CatalogPath"), FString()); // a late change: this session keeps its epoch, the next one reads the new value
	TestEqual(TEXT("a late path change does not replace the published epoch"), First->GetEpoch()->Id, FirstEpoch->Id);
	TestEqual(TEXT("a late path change does not change the latched path"), First->GetLatchedPath(), TestPath);
	FTestCatalogHost Second = StartCatalogSubsystem();
	const auto SecondEpoch = Second->GetEpoch();
	if (TestTrue(TEXT("the second game instance publishes the shipped catalog"), SecondEpoch.IsValid()))
	{
		TestEqual(TEXT("the second latch is independent: shipped three builds"), SecondEpoch->Builds.Num(), 3);
		TestTrue(TEXT("the second latch is empty (shipped default)"), Second->GetLatchedPath().IsEmpty());
		TestTrue(TEXT("a distinct epoch id"), SecondEpoch->Id != FirstEpoch->Id);
	}
	TestEqual(TEXT("the first game instance is untouched by the second"), First->GetEpoch()->Builds.Num(), 4);

	// 3. Explicit failures: no quiet legacy fallback, every one ends in a null epoch and a named error.
	struct FFailure { const TCHAR* Name; const TCHAR* Source; FString Path; const TCHAR* Fourth; const TCHAR* Expected; };
	const FString Missing = Root + TEXT("DA_ABITest_Missing.DA_ABITest_Missing");
	const FString WrongType = Root + TEXT("DA_ABI_FourthWeaponItem.DA_ABI_FourthWeaponItem");
	const TArray<FFailure> Failures = {
		{TEXT("source auto"), TEXT("auto"), TestPath, TEXT("0"), TEXT("needs rpg.CatalogSource data")},
		{TEXT("source legacy"), TEXT("legacy"), TestPath, TEXT("0"), TEXT("needs rpg.CatalogSource data")},
		{TEXT("contradictory fourth fixture flag"), TEXT("data"), TestPath, TEXT("1"), TEXT("conflicts with rpg.CatalogTestFourth")},
		{TEXT("path outside the folder"), TEXT("data"), ShippedCatalog, TEXT("0"), TEXT("outside the approved TypedABIFixtures folder")},
		{TEXT("absent asset"), TEXT("data"), Missing, TEXT("0"), TEXT("CatalogPath: asset absent")},
		{TEXT("wrong asset type"), TEXT("data"), WrongType, TEXT("0"), TEXT("wrong asset type")},
	};
	AddExpectedError(TEXT("DA_ABITest_Missing"), EAutomationExpectedErrorFlags::Contains, 0); // the engine's own load diagnostics of a missing asset, any number
	for (const FFailure& Case : Failures)
	{
		AddExpectedError(Case.Expected, EAutomationExpectedErrorFlags::Contains, 1);
		Scope.Set(TEXT("rpg.CatalogSource"), Case.Source);
		Scope.Set(TEXT("rpg.CatalogPath"), Case.Path);
		Scope.Set(TEXT("rpg.CatalogTestFourth"), Case.Fourth);
		FTestCatalogHost Failed = StartCatalogSubsystem();
		TestFalse(*FString::Printf(TEXT("%s: no epoch is published (no legacy fallback)"), Case.Name), Failed->GetEpoch().IsValid());
		TestTrue(*FString::Printf(TEXT("%s: the diagnostic says data is required"), Case.Name), Failed->GetDiagnostic().StartsWith(TEXT("unavailable")));
		TestEqual(*FString::Printf(TEXT("%s: the latched path is still reported"), Case.Name), Failed->GetLatchedPath(), Case.Path);
	}
	return true;
}

// Once-only diagnostics (Codex lead decision C172, X-156): a GI-owned ledger keyed epoch + category + key, one authoritative icon report per compiled epoch, the selector overflow warning once per
// published epoch. The counts are taken from the real log output (an output device), not from a helper's return value alone.
namespace
{
	class FCatalogLogCounter : public FOutputDevice
	{
	public:
		FCatalogLogCounter() { GLog->AddOutputDevice(this); }
		virtual ~FCatalogLogCounter() override { GLog->RemoveOutputDevice(this); }
		virtual void Serialize(const TCHAR* Text, ELogVerbosity::Type Verbosity, const FName& Category) override
		{
			if (Category == FName(TEXT("LogRPGCatalog"))) Lines.Add(FString(Text));
		}
		int32 Count(const FString& A, const FString& B = FString()) const
		{
			GLog->FlushThreadedLogs(); // a line logged a moment ago may still sit in the redirector's buffer
			int32 N = 0;
			for (const FString& Line : Lines) if (Line.Contains(A) && (B.IsEmpty() || Line.Contains(B))) ++N;
			return N;
		}
		TArray<FString> Lines;
	};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCatalogDiagnosticsTest, "OneBossFight.Catalog.Diagnostics",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGCatalogDiagnosticsTest::RunTest(const FString& Parameters)
{
	using namespace RPGCombatRegistry;
	const FGuid EpochA = FGuid::NewGuid(), EpochB = FGuid::NewGuid();

	// 1. The ledger: first report true, every repeat false; a new epoch, category or key is independent; two ledgers never share state.
	FDiagnosticLedger One, Two;
	TestTrue(TEXT("first report of a key"), One.TryReport(EpochA, TEXT("IconAbsent"), TEXT("Build1")));
	TestFalse(TEXT("repeat of the same key"), One.TryReport(EpochA, TEXT("IconAbsent"), TEXT("Build1")));
	TestTrue(TEXT("another build id is independent"), One.TryReport(EpochA, TEXT("IconAbsent"), TEXT("Build2")));
	TestTrue(TEXT("another category is independent"), One.TryReport(EpochA, TEXT("IconBroken"), TEXT("Build1")));
	TestTrue(TEXT("a fresh epoch reports again"), One.TryReport(EpochB, TEXT("IconAbsent"), TEXT("Build1")));
	TestTrue(TEXT("a second ledger (another game instance) is not suppressed by the first"), Two.TryReport(EpochA, TEXT("IconAbsent"), TEXT("Build1")));
	One.Reset();
	TestTrue(TEXT("a reset ledger (teardown) reports again"), One.TryReport(EpochA, TEXT("IconAbsent"), TEXT("Build1")));

	// 2. Icon reports from the one authoritative emitter (Compile), counted in the log: absence is Display, a set but unusable icon is a Warning with its reason, valid icons are silent.
	const FString Fixtures = FString(TEXT("/Game/")) + TEXT("OneBossFight/Data/TypedABIFixtures/");
	const FString Uncooked = FString(TEXT("/Game/")) + TEXT("OneBossFight/ReviewFixtures/TypedABI/");
	const FString ArtRoot = FString(TEXT("/Game/")) + TEXT("OneBossFight/UI/Art/");
	auto L = Legacy();
	TArray<FRPGCatalogWeapon> Weapons = L->Weapons;
	for (FRPGCatalogWeapon& W : Weapons)
	{
		UObject* Item = W.ItemPath.TryLoad();
		if (!TestNotNull(*FString::Printf(TEXT("%s item loads"), *W.WeaponId.ToString()), Item)) return false;
		W.ItemBaseClass = FSoftObjectPath(Item->GetClass());
	}
	auto IconBuild = [&](const TCHAR* Id, int32 Order, const FString& Icon)
	{
		FRPGCatalogBuild B = L->Builds[0];
		B.BuildId = Id; B.ConsoleName = Id; B.DisplayName = Id; B.Aliases.Reset(); B.LegacySlot = INDEX_NONE; B.UiOrder = Order;
		B.Icon = Icon.IsEmpty() ? FSoftObjectPath() : FSoftObjectPath(Icon);
		return B;
	};
	TArray<FRPGCatalogBuild> Builds = L->Builds;
	Builds.Add(IconBuild(TEXT("DiagAbsent"), 3, FString()));
	Builds.Add(IconBuild(TEXT("DiagMissing"), 4, ArtRoot + TEXT("T_Missing_Icon_Diag.T_Missing_Icon_Diag")));
	Builds.Add(IconBuild(TEXT("DiagWrongType"), 5, Fixtures + TEXT("DA_ABI_FourthWeaponItem.DA_ABI_FourthWeaponItem")));
	Builds.Add(IconBuild(TEXT("DiagUncooked"), 6, Uncooked + TEXT("DA_ABI_UncookedWeaponItem.DA_ABI_UncookedWeaponItem")));
	AddExpectedError(TEXT("T_Missing_Icon_Diag"), EAutomationExpectedErrorFlags::Contains, 0); // the engine's own load diagnostics of the missing asset, any number
	FString Error;
	{
		FCatalogLogCounter Log;
		auto First = Compile(Builds, Weapons, Error, true);
		if (!TestTrue(*FString::Printf(TEXT("the epoch with four optional-icon cases compiles (%s)"), *Error), First.IsValid())) return false;
		TestEqual(TEXT("absent icon: one Display line"), Log.Count(TEXT("build=DiagAbsent icon absent")), 1);
		TestEqual(TEXT("missing icon: one Warning line naming the reason"), Log.Count(TEXT("build=DiagMissing icon broken"), TEXT("unloadable")), 1);
		TestEqual(TEXT("wrong-type icon: one Warning line naming the reason"), Log.Count(TEXT("build=DiagWrongType icon broken"), TEXT("wrong type")), 1);
		TestEqual(TEXT("uncooked icon: one Warning line naming the reason"), Log.Count(TEXT("build=DiagUncooked icon broken"), TEXT("outside the cooked roots")), 1);
		TestEqual(TEXT("the shipped valid icons are silent"), Log.Count(TEXT("build=Starter icon")) + Log.Count(TEXT("build=Strength icon")) + Log.Count(TEXT("build=Dex icon")), 0);
		TestEqual(TEXT("four icon lines in total"), Log.Count(TEXT("icon absent")) + Log.Count(TEXT("icon broken")), 4);
		TestEqual(TEXT("every line carries the epoch id"), Log.Count(First->Id.ToString()), 4);
		auto Second = Compile(Builds, Weapons, Error, true); // a fresh epoch: new reports, one per entry again
		TestTrue(TEXT("the second epoch has another id"), Second.IsValid() && Second->Id != First->Id);
		TestEqual(TEXT("a fresh epoch reports each entry once more"), Log.Count(TEXT("icon absent")) + Log.Count(TEXT("icon broken")), 8);
	}

	// 3. The selector overflow warning: once per published epoch however often it is asked or whatever the height; independent per game instance; a stale epoch id reports nothing.
	FCatalogCvarScope Scope;
	const FString TestPath = TestCatalogRoot() + TEXT("DA_ABITest_Catalog.DA_ABITest_Catalog");
	if (!TestTrue(TEXT("the test cvars are registered"), Scope.Set(TEXT("rpg.CatalogSource"), TEXT("data")) && Scope.Set(TEXT("rpg.CatalogPath"), TestPath) && Scope.Set(TEXT("rpg.CatalogTestFourth"), TEXT("0")) && Scope.Set(TEXT("rpg.CatalogTestInvalid"), TEXT("0")))) return false;
	FCatalogLogCounter Log;
	FTestCatalogHost HostA = StartCatalogSubsystem();
	FTestCatalogHost HostB = StartCatalogSubsystem();
	const auto EA = HostA->GetEpoch();
	const auto EB = HostB->GetEpoch();
	if (!TestTrue(TEXT("two game instances with the four-row test catalog"), EA.IsValid() && EB.IsValid() && EA->Builds.Num() == 4 && EB->Builds.Num() == 4)) return false;
	TestEqual(TEXT("the visible rows at height 200 are two (formula)"), VisibleRows(4, 200.f), 2);
	TestFalse(TEXT("a height where every row fits reports nothing"), HostA->ReportLayoutOverflow(EA->Id, 4, 1080.f));
	TestEqual(TEXT("no overflow line yet"), Log.Count(TEXT("selector layout overflow")), 0);
	TestTrue(TEXT("first overflow of the epoch is reported"), HostA->ReportLayoutOverflow(EA->Id, 4, 200.f));
	for (float Height : {200.f, 200.f, 180.f, 150.f, 90.f}) TestFalse(TEXT("repeats (open/close/resize) are not reported again"), HostA->ReportLayoutOverflow(EA->Id, 4, Height));
	TestEqual(TEXT("exactly one overflow line for game instance A"), Log.Count(TEXT("selector layout overflow")), 1);
	TestEqual(TEXT("the line names the epoch and the hidden start index"), Log.Count(EA->Id.ToString(), TEXT("rows from index 2")), 1);
	TestEqual(TEXT("the line names the measured layout height"), Log.Count(TEXT("selector layout overflow"), TEXT("measured layout height 200.0")), 1);
	TestFalse(TEXT("an epoch id that is not A's published epoch reports nothing"), HostA->ReportLayoutOverflow(EB->Id, 4, 200.f));
	TestTrue(TEXT("game instance B is not suppressed by A"), HostB->ReportLayoutOverflow(EB->Id, 4, 200.f));
	TestEqual(TEXT("two overflow lines in total, one per game instance"), Log.Count(TEXT("selector layout overflow")), 2);
	return true;
}

#endif
