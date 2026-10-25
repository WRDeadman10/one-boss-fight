// Copyright One Boss Fight. All Rights Reserved.
#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
#include "Player/RPGCombatCatalog.h"
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
#endif
