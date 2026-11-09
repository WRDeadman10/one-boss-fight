#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
#include "Player/RPGEncounterBinding.h"
#include "Player/RPGBossAttackTrackerAdapters.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGLegend.h"
#include "Player/RPGAttackTracker.h"
#include "Engine/World.h"
#include "Misc/ScopeExit.h"
#include "UObject/GarbageCollection.h"
#include "UObject/StrongObjectPtr.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGEncounterBindingDraftTest, "OneBossFight.Binding.DraftWorldIsolation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGEncounterBindingDraftTest::RunTest(const FString& Parameters)
{
	UWorld* A = UWorld::CreateWorld(EWorldType::Game, false);
	UWorld* B = UWorld::CreateWorld(EWorldType::Game, false);
	ON_SCOPE_EXIT { if (B) { B->DestroyWorld(false); } if (A) { A->DestroyWorld(false); } };
	if (!TestNotNull(TEXT("world A"), A) || !TestNotNull(TEXT("world B"), B)) { return false; }
	auto* CA = A->GetSubsystem<URPGCombatContextSubsystem>(); auto* CB = B->GetSubsystem<URPGCombatContextSubsystem>();
	if (!TestNotNull(TEXT("context A"), CA) || !TestNotNull(TEXT("context B"), CB)) { return false; }
	TestNotEqual(TEXT("world identities differ"), CA->GetSessionId(), CB->GetSessionId());
	TStrongObjectPtr<URPGBossDefinition> Def(NewObject<URPGBossDefinition>());
	Def->DefinitionId = TEXT("Synthetic"); Def->PresentationId = TEXT("SyntheticLook");
	Def->Stats.MaxHealth = 2000.f; Def->Stats.MaxPosture = 100.f;
	Def->Stats.PostureRegenDelay = 6.f; Def->Stats.PostureRegenRate = 13.f;
	FRPGParityField Field; Field.FieldPath = TEXT("Stats.MaxHealth"); Field.Type = TEXT("float");
	Field.Value = TEXT("2000"); Field.SourcePath = TEXT("synthetic fixture, not live provenance");
	Field.SourceSHA256 = FString::ChrN(64, TEXT('a')); Field.SourceSite = TEXT("fixture");
	Field.Origin = TEXT("harness"); Field.Precedence = TEXT("fixture"); Field.Destination = TEXT("BossMaxHealth");
	Field.FirstRead = TEXT("BeginPlay"); Field.Witness = TEXT("synthetic only"); Def->Fields.Add(Field);
	TSharedPtr<const FRPGParticipantConfig> Config;
	auto Compiled = RPGCombatHydration::CompileSyntheticParticipant(*Def, RPGCombatRegistry::Legacy(), FString::ChrN(64, TEXT('b')), Config);
	if (!TestTrue(TEXT("legacy definition without new parry fields compiles using additive defaults"), Compiled.IsReady() && Config.IsValid())) { return false; }
	TestTrue(TEXT("proposal defaults are carried into the participant snapshot"), Config->ParrySlowMotion.bPerfectEnabled
		&& FMath::IsNearlyEqual(Config->ParrySlowMotion.PerfectScale, 0.30f) && FMath::IsNearlyEqual(Config->ParrySlowMotion.PerfectSeconds, 0.35f)
		&& !Config->ParrySlowMotion.bNormalEnabled && FMath::IsNearlyEqual(Config->ParrySlowMotion.CooldownSeconds, 0.60f));
	TestFalse(TEXT("existing boss definitions default to legacy attack timing"), Def->bUseMontageNotifyTimings);
	TestFalse(TEXT("compiled existing definition carries timing opt-in as false"), Config->bUseMontageNotifyTimings);
	TestTrue(TEXT("default-off timing mode receives additive provenance"), Config->Fields.ContainsByPredicate([](const FRPGParityField& Entry)
		{ return Entry.FieldPath == RPGBossAttackTrackerAdapters::FieldUseMontageNotifyTimings; }));
	Def->bUseMontageNotifyTimings = true;
	FRPGParityField TimingOptIn = Field;
	TimingOptIn.FieldPath = RPGBossAttackTrackerAdapters::FieldUseMontageNotifyTimings;
	TimingOptIn.Type = TEXT("bool"); TimingOptIn.Value = TEXT("true");
	TimingOptIn.Destination = TEXT("URPGAttackTracker.bUseMontageNotifyTimings");
	Def->Fields.Add(TimingOptIn);
	TSharedPtr<const FRPGParticipantConfig> EnabledConfig;
	const FRPGHydrationResult EnabledCompiled = RPGCombatHydration::CompileSyntheticParticipant(*Def, RPGCombatRegistry::Legacy(), FString::ChrN(64, TEXT('b')), EnabledConfig);
	TestTrue(TEXT("source-backed boss timing opt-in compiles into the participant snapshot"), EnabledCompiled.IsReady()
		&& EnabledConfig.IsValid() && EnabledConfig->bUseMontageNotifyTimings);
	if (EnabledConfig.IsValid())
	{
		AActor* TrackerOwner = NewObject<AActor>(GetTransientPackage());
		URPGAttackTracker* Tracker = TrackerOwner ? NewObject<URPGAttackTracker>(TrackerOwner) : nullptr;
		FString TrackerError;
		TestTrue(TEXT("enabled definition configures the tracker before encounter component registration"), Tracker
			&& RPGBossAttackTrackerAdapters::ConfigureAttackTracker(*Tracker, *EnabledConfig, TrackerError) && TrackerError.IsEmpty());
		TestTrue(TEXT("tracker receives the explicitly enabled definition value"), Tracker && Tracker->bUseMontageNotifyTimings);
	}
	TSharedPtr<const FRPGParticipantConfig> MissingTimingProvenance;
	Def->Fields.RemoveAll([&](const FRPGParityField& Entry) { return Entry.FieldPath == RPGBossAttackTrackerAdapters::FieldUseMontageNotifyTimings; });
	const FRPGHydrationResult MissingTimingSource = RPGCombatHydration::CompileSyntheticParticipant(*Def, RPGCombatRegistry::Legacy(), FString::ChrN(64, TEXT('b')), MissingTimingProvenance);
	TestTrue(TEXT("enabled timing mode without explicit source provenance is rejected"), !MissingTimingSource.IsReady()
		&& !MissingTimingProvenance.IsValid() && MissingTimingSource.Errors.ContainsByPredicate([](const FString& Error)
		{ return Error.StartsWith(TEXT("MontageNotifyTimings.ProvenanceMissing:")); }));
	Def->bUseMontageNotifyTimings = false;
	Def->Fields.RemoveAll([&](const FRPGParityField& Entry) { return Entry.FieldPath == RPGBossAttackTrackerAdapters::FieldUseMontageNotifyTimings; });
	TestTrue(TEXT("typed default membership carries the complete parry policy"), Config->Fields.ContainsByPredicate([](const FRPGParityField& Entry) { return Entry.FieldPath == RPGParrySlowMotionConfigRules::FieldCooldownSeconds; }));
	Def->AttackTracker.bEnabled = false;
	TSharedPtr<const FRPGParticipantConfig> MissingTrackerFields;
	const FRPGHydrationResult MissingTracker = RPGCombatHydration::CompileSyntheticParticipant(*Def, RPGCombatRegistry::Legacy(), FString::ChrN(64, TEXT('b')), MissingTrackerFields);
	TestTrue(TEXT("a non-default tracker config without its five typed source fields is rejected with its exact refusal token"), !MissingTracker.IsReady()
		&& !MissingTrackerFields.IsValid() && MissingTracker.Errors.ContainsByPredicate([](const FString& Error)
		{ return Error.StartsWith(TEXT("AttackTracker.ProvenanceMissing:")); }));
	Def->AttackTracker = FRPGAttackTrackerConfig();
	Def->ParrySlowMotion.bNormalEnabled = true;
	Def->ParrySlowMotion.NormalScale = 0.55f;
	TSharedPtr<const FRPGParticipantConfig> MissingPolicyFields;
	const auto MissingPolicy = RPGCombatHydration::CompileSyntheticParticipant(*Def, RPGCombatRegistry::Legacy(), FString::ChrN(64, TEXT('b')), MissingPolicyFields);
	TestTrue(TEXT("a customized typed policy without matching source fields is rejected"), !MissingPolicy.IsReady() && MissingPolicyFields.IsValid() == false
		&& MissingPolicy.Errors.ContainsByPredicate([](const FString& Error) { return Error.Contains(TEXT("ParrySlowMotion.ProvenanceMissing")); }));
	const TCHAR* PolicyPaths[] = {RPGParrySlowMotionConfigRules::FieldPerfectEnabled, RPGParrySlowMotionConfigRules::FieldPerfectScale,
		RPGParrySlowMotionConfigRules::FieldPerfectSeconds, RPGParrySlowMotionConfigRules::FieldNormalEnabled,
		RPGParrySlowMotionConfigRules::FieldNormalScale, RPGParrySlowMotionConfigRules::FieldNormalSeconds,
		RPGParrySlowMotionConfigRules::FieldCooldownSeconds};
	FRPGParityField PartialPolicySource = Field;
	PartialPolicySource.FieldPath = PolicyPaths[0];
	Def->Fields.Add(PartialPolicySource);
	TSharedPtr<const FRPGParticipantConfig> PartialPolicy;
	const auto PartialPolicyResult = RPGCombatHydration::CompileSyntheticParticipant(*Def, RPGCombatRegistry::Legacy(), FString::ChrN(64, TEXT('b')), PartialPolicy);
	TestTrue(TEXT("a partially authored optional policy group is refused"), !PartialPolicyResult.IsReady() && !PartialPolicy.IsValid()
		&& PartialPolicyResult.Errors.ContainsByPredicate([](const FString& Error) { return Error.Contains(TEXT("ParrySlowMotion.ProvenanceIncomplete")); }));
	Def->Fields.RemoveAll([&](const FRPGParityField& Entry) { return Entry.FieldPath == PolicyPaths[0]; });
	for (const TCHAR* Path : PolicyPaths)
	{
		FRPGParityField Source; Source.FieldPath = Path; Source.Type = TEXT("typed-config"); Source.Value = TEXT("fixture");
		Source.SourcePath = TEXT("fixture"); Source.SourceSHA256 = FString::ChrN(64, TEXT('c')); Source.SourceSite = TEXT("test");
		Source.Origin = TEXT("test"); Source.Precedence = TEXT("test"); Source.Destination = TEXT("URPGBossLegend.ParrySlowMotion");
		Source.FirstRead = TEXT("preflight"); Source.Witness = TEXT("synthetic"); Def->Fields.Add(Source);
	}
	TSharedPtr<const FRPGParticipantConfig> CustomPolicy;
	const auto CustomPolicyResult = RPGCombatHydration::CompileSyntheticParticipant(*Def, RPGCombatRegistry::Legacy(), FString::ChrN(64, TEXT('b')), CustomPolicy);
	TestTrue(TEXT("a source-backed player policy is copied into the data route"), CustomPolicyResult.IsReady() && CustomPolicy.IsValid()
		&& CustomPolicy->ParrySlowMotion.bNormalEnabled && FMath::IsNearlyEqual(CustomPolicy->ParrySlowMotion.NormalScale, 0.55f));
	Def->ParrySlowMotion.PerfectScale = 1.f;
	TSharedPtr<const FRPGParticipantConfig> InvalidPolicy;
	const auto InvalidPolicyResult = RPGCombatHydration::CompileSyntheticParticipant(*Def, RPGCombatRegistry::Legacy(), FString::ChrN(64, TEXT('b')), InvalidPolicy);
	TestTrue(TEXT("an enabled parry policy at normal speed fails closed"), !InvalidPolicyResult.IsReady() && !InvalidPolicy.IsValid()
		&& InvalidPolicyResult.Errors.ContainsByPredicate([](const FString& Error) { return Error.Contains(TEXT("ParrySlowMotion.InvalidPerfectScale")); }));
	Def->Stats.MaxHealth = 1.f; TestEqual(TEXT("value snapshot independent"), Config->Stats.MaxHealth, 2000.f);
	TSharedPtr<const FRPGParticipantConfig> Invalid = Config;
	TestFalse(TEXT("strict missing content rejects"), RPGCombatHydration::CompileParticipant(*Def, nullptr, TEXT(""), Invalid).IsReady());
	TestFalse(TEXT("no legacy substitute on missing content"), Invalid.IsValid());
	auto Bind = [&](UWorld* World, URPGCombatContextSubsystem* Context, FGuid Id, AActor*& Boss, AActor*& Target)
	{
		auto* Binding = World->SpawnActor<ARPGEncounterBinding>(); Boss = World->SpawnActor<AActor>(); Target = World->SpawnActor<AActor>();
		if (!Binding || !Boss || !Target) { return false; }
		Binding->EncounterInstance = Id;
		FRPGPlacedParticipantBinding First; First.Slot = TEXT("Boss"); First.TargetSlot = TEXT("Player"); First.Actor = Boss;
		FRPGPlacedParticipantBinding Second; Second.Slot = TEXT("Player"); Second.TargetSlot = TEXT("Boss"); Second.Actor = Target;
		Binding->Participants = {First, Second};
		TMap<FName, TSharedPtr<const FRPGParticipantConfig>> Configs; Configs.Add(TEXT("Boss"), Config); Configs.Add(TEXT("Player"), Config);
		return Context->BindEncounter(*Binding, Configs).IsReady();
	};
	AActor *BossA = nullptr, *PlayerA = nullptr, *BossB = nullptr, *PlayerB = nullptr;
	const FGuid Encounter = FGuid::NewGuid();
	TestTrue(TEXT("bind A"), Bind(A, CA, Encounter, BossA, PlayerA));
	TestTrue(TEXT("same content/id separate world"), Bind(B, CB, Encounter, BossB, PlayerB));
	if (!BossA || !PlayerA || !BossB || !PlayerB) { return false; }
	auto KA = CA->FindParticipant(*BossA); auto KB = CB->FindParticipant(*BossB);
	if (!KA || !KB) { return false; }
	TestFalse(TEXT("foreign key cannot resolve"), CB->IsCurrent(KA.GetValue()));
	TestNull(TEXT("not hydrated target unavailable"), CA->ResolveTarget(KA.GetValue(), TEXT("Player")));
	FRPGComponentPlan Plan; Plan.Class = URPGBossEncounter::StaticClass(); Plan.InstanceName = TEXT("FixtureEncounter");
	Plan.RequiredFields = {TEXT("Stats.MaxHealth")};
	Plan.Configure = [](UActorComponent& Component, const FRPGParticipantConfig& C, FString& Error)
	{
		auto* E = Cast<URPGBossEncounter>(&Component); if (!E) { Error = TEXT("wrong type"); return false; }
		E->BossMaxHealth = C.Stats.MaxHealth; E->GateRadius = 0.f;
		return !E->IsRegistered() && !E->HasBegunPlay();
	};
	FRPGComponentPlan LegendPlan; LegendPlan.Class = URPGBossLegend::StaticClass(); LegendPlan.InstanceName = TEXT("FixtureLegend");
	LegendPlan.bConfigurationIndependent = true; // optional policy defaults keep old definitions usable
	LegendPlan.Configure = [](UActorComponent& Component, const FRPGParticipantConfig& C, FString& Error)
	{
		auto* Legend = Cast<URPGBossLegend>(&Component); if (!Legend) { Error = TEXT("wrong type"); return false; }
		Legend->ParrySlowMotion = C.ParrySlowMotion;
		return true;
	};
	const TArray<FRPGComponentPlan> Plans = {Plan, LegendPlan};
	TestTrue(TEXT("hydrate all A before play"), CA->CreateConfigureRegister(*BossA, Plans).IsReady() && CA->CreateConfigureRegister(*PlayerA, Plans).IsReady());
	const URPGBossLegend* HydratedLegacyLegend = BossA->FindComponentByClass<URPGBossLegend>();
	TestTrue(TEXT("legacy definition without parry fields prepares and activates with native proposal defaults"), HydratedLegacyLegend
		&& HydratedLegacyLegend->ParrySlowMotion.bPerfectEnabled && !HydratedLegacyLegend->ParrySlowMotion.bNormalEnabled
		&& FMath::IsNearlyEqual(HydratedLegacyLegend->ParrySlowMotion.PerfectScale, 0.30f)
		&& FMath::IsNearlyEqual(HydratedLegacyLegend->ParrySlowMotion.PerfectSeconds, 0.35f));
	TestEqual(TEXT("own target only"), CA->ResolveTarget(KA.GetValue(), TEXT("Player")), PlayerA);
	TestFalse(TEXT("repeat attach rejected"), CA->CreateConfigureRegister(*BossA, Plans).IsReady());
	CollectGarbage(RF_NoFlags);
	TestTrue(TEXT("real GC retains world-owned participant"), CA->IsCurrent(KA.GetValue()));
	TestTrue(TEXT("reset generation notification"), CA->OnGenerationChanged(*BossA, 2));
	TestFalse(TEXT("old handle invalid"), CA->IsCurrent(KA.GetValue()));
	TestFalse(TEXT("repeat generation refused"), CA->OnGenerationChanged(*BossA, 2));
	TestFalse(TEXT("decremented generation refused"), CA->OnGenerationChanged(*BossA, 1));
	TestFalse(TEXT("zero generation refused"), CA->OnGenerationChanged(*BossA, 0));
	TestTrue(TEXT("other world unaffected by reset"), CB->IsCurrent(KB.GetValue()));
	CA->UnbindActor(*BossA);
	TestEqual(TEXT("whole A encounter unbound"), CA->GetBoundCount(), 0);
	TestEqual(TEXT("B retains two"), CB->GetBoundCount(), 2);
	const FString OldSession = CA->GetSessionId();
	A->DestroyWorld(false); A = nullptr; CollectGarbage(RF_NoFlags);
	TestTrue(TEXT("B survives A teardown and GC"), CB->IsCurrent(KB.GetValue()));
	A = UWorld::CreateWorld(EWorldType::Game, false);
	if (!A || !A->GetSubsystem<URPGCombatContextSubsystem>()) { return false; }
	TestNotEqual(TEXT("recreated world has new session"), A->GetSubsystem<URPGCombatContextSubsystem>()->GetSessionId(), OldSession);
	TestFalse(TEXT("old key invalid after recreation"), A->GetSubsystem<URPGCombatContextSubsystem>()->IsCurrent(KA.GetValue()));
	AddInfo(TEXT("Synthetic standalone worlds; NOT seamless travel or two real pack duels. Typed full-field hydration remains unproved."));
	return true;
}
#endif
