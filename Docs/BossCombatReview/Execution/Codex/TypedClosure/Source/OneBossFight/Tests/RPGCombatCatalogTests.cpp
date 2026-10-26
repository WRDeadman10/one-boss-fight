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
	Outside.StyleAliases.Reset(); Outside.AliasHudWords.Reset(); Outside.ItemPath = FSoftObjectPath(FString(TEXT("/Game/")) + TEXT("UncookedABIFixture/Absent.Absent")); // Deliberately absent test input, not a cook dependency.
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
#endif
