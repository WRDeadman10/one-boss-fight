#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
#include "Player/RPGEncounterBinding.h"
#include "Player/RPGBossEncounter.h"
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
	if (!TestTrue(TEXT("compile fixture"), Compiled.IsReady() && Config.IsValid())) { return false; }
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
	const TArray<FRPGComponentPlan> Plans = {Plan};
	TestTrue(TEXT("hydrate all A before play"), CA->CreateConfigureRegister(*BossA, Plans).IsReady() && CA->CreateConfigureRegister(*PlayerA, Plans).IsReady());
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
