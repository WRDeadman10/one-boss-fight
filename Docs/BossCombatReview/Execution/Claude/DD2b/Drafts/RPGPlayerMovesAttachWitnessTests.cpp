// Copyright One Boss Fight. All Rights Reserved.

// DRAFT for Codex review (X-239). NOT in Source, NOT compiled, NOT run. If accepted it is copied to
// Source/OneBossFight/Tests/RPGPlayerMovesAttachWitnessTests.cpp and built twice (A/B, see 2B_WITNESS_PROPOSAL.md): once against the preimage
// RPGPlayerMovesSubsystem.cpp/.h and once against the accepted 2b files. It uses only public engine behaviour and the public
// URPGPlayerMovesSubsystem::IsPackPlayer/IsPackBoss, so the identical file compiles against both sources.
//
// What it observes: the creation order of the objects whose outer is the pawn (a UObject create listener), the components the pawn owns afterwards
// (identities and counts per class, not name suffixes), and their registered / begun-play flags. What it does NOT observe: registration or BeginPlay
// chronology. A bare test world has no GameMode, so UWorld::BeginPlay broadcasts the world subsystems' OnWorldBeginPlay but never calls
// GameMode->StartPlay(), and the actors never receive BeginPlay here (World.cpp 5429-5441). HasBegunPlay is therefore only LOGGED, never asserted.
// Hybrid (player and boss) classes, a null pawn, a deferred-construction spawn and a pawn that only gets the world-begin trigger have no public route here
// and are NOT exercised: they remain source reasoning (2B_DELIVERY.md).

#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Player/RPGPlayerMovesSubsystem.h"
#include "Components/ActorComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "HAL/CriticalSection.h"
#include "Misc/ScopeLock.h"
#include "UObject/Package.h"
#include "UObject/UObjectArray.h"
#include "UObject/UObjectGlobals.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGAttachWitness, Log, All);

namespace
{
namespace AttachWitness
{
	// The pack is Blueprint only: both classes are loaded by path, as everywhere else in the project.
	const TCHAR* const BossClassPath = TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss.BP_ExampleGreatSwordBoss_C");
	const TCHAR* const PlayerClassPath = TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.BP_CombatPlayerCharacter_C");

	// The creation order the PREIMAGE Attach produced, read from its statement order (not from the new code): boss prelude, then the bundle, 21 steps.
	TArray<FString> ExpectedBossSequence()
	{
		return TArray<FString>{
			TEXT("RPGFootsteps"), TEXT("RPGBossMusic"), TEXT("RPGBossStagger"), TEXT("RPGBossPhases"), TEXT("RPGBossEncounter"), TEXT("RPGBossDormantWake"),
			TEXT("RPGBossPosture"), TEXT("RPGBossDeath"), TEXT("RPGBossLook"), TEXT("RPGBossBleed"), TEXT("RPGAttackTracker"), TEXT("RPGBossCloseClipSwap"),
			TEXT("RPGBossShockwave"), TEXT("RPGBossLowSweep"), TEXT("RPGBossHealPunish"), TEXT("RPGDamageResolver"), TEXT("RPGTraceGuard"), TEXT("RPGTraceAudit"),
			TEXT("RPGBossHud"), TEXT("RPGCombatDebug"), TEXT("RPGBossLegend")};
	}

	// The player statements, in the order of the preimage.
	TArray<FString> ExpectedPlayerSequence()
	{
		return TArray<FString>{
			TEXT("RPGFootsteps"), TEXT("RPGCameraRig"), TEXT("RPGRiposteInput"), TEXT("RPGDodgeTiming"), TEXT("RPGSwingTracker"), TEXT("RPGHitIntake"),
			TEXT("RPGBuildLoadout"), TEXT("RPGBuildSelect"), TEXT("RPGFlaskHud"), TEXT("RPGIFrameMonitor")};
	}

	bool IsRpgComponentClass(const UClass* Class)
	{
		static const FName RpgPackage(TEXT("/Script/OneBossFight"));
		return Class && Class->IsChildOf(UActorComponent::StaticClass()) && Class->GetOutermost()->GetFName() == RpgPackage;
	}

	/** One notification of the create listener. Only identity values are kept: the object is still being constructed when it is reported. */
	struct FCreation
	{
		uint32 Ordinal = 0;
		const UClass* Class = nullptr;
		const UObject* Outer = nullptr; // compared as a pointer value only, never dereferenced
		bool bGameThread = true;
	};

	/**
	 * Records every UObject created while it is alive. The listener array of the engine is not locked (UObjectArray.cpp 301 "@todo: threading"), so it is
	 * added and removed only on the game thread, after pending async loads were flushed; the recorder itself is guarded by a mutex because a notification
	 * can still arrive from another thread. Only GetClass()/GetOuter(), which the UObjectBase constructor sets before the listeners run (UObjectBase.cpp 128-135),
	 * are read in the callback: nothing derived, registered or BeginPlay-dependent is called while an object is under construction.
	 */
	class FCreationRecorder final : public FUObjectArray::FUObjectCreateListener
	{
	public:
		FCreationRecorder()
		{
			Records.Reserve(65536);
			GUObjectArray.AddUObjectCreateListener(this);
			bRegistered = true;
		}

		virtual ~FCreationRecorder() override { Stop(); }

		void Stop()
		{
			if (bRegistered)
			{
				bRegistered = false;
				GUObjectArray.RemoveUObjectCreateListener(this);
			}
		}

		virtual void NotifyUObjectCreated(const UObjectBase* Object, int32 /*Index*/) override
		{
			FScopeLock Lock(&Mutex);
			++Ordinal;
			if (Records.Num() >= MaxRecords)
			{
				bTruncated = true;
				return;
			}
			FCreation Record;
			Record.Ordinal = Ordinal;
			Record.Class = Object->GetClass();
			Record.Outer = Object->GetOuter();
			Record.bGameThread = IsInGameThread();
			Records.Add(Record);
		}

		virtual void OnUObjectArrayShutdown() override
		{
			if (bRegistered)
			{
				bRegistered = false;
				GUObjectArray.RemoveUObjectCreateListener(this);
			}
		}

		uint32 Mark() const
		{
			FScopeLock Lock(&Mutex);
			return Ordinal;
		}

		bool Truncated() const
		{
			FScopeLock Lock(&Mutex);
			return bTruncated;
		}

		/** Everything created after Mark whose outer is Outer, in creation order. Call only after the spawn returned, when Outer is known. */
		TArray<FCreation> Since(uint32 MarkOrdinal, const UObject* Outer) const
		{
			FScopeLock Lock(&Mutex);
			TArray<FCreation> Out;
			for (const FCreation& Record : Records)
			{
				if (Record.Ordinal > MarkOrdinal && Record.Outer == Outer)
				{
					Out.Add(Record);
				}
			}
			return Out;
		}

	private:
		static constexpr int32 MaxRecords = 600000;
		mutable FCriticalSection Mutex;
		TArray<FCreation> Records;
		uint32 Ordinal = 0;
		bool bTruncated = false;
		bool bRegistered = false;
	};

	/** Test-local game world (the project's RPGTests::FScopedTestWorld is local to RPGAutomationTests.cpp and cannot be reused). Destroyed with the scope. */
	struct FWitnessWorld
	{
		UWorld* World = nullptr;

		FWitnessWorld()
		{
			if (!GEngine)
			{
				return;
			}
			World = UWorld::CreateWorld(EWorldType::Game, /*bInformEngineOfWorld=*/false);
			if (World)
			{
				FWorldContext& Context = GEngine->CreateNewWorldContext(EWorldType::Game);
				Context.SetCurrentWorld(World);
				World->InitializeActorsForPlay(FURL());
			}
		}

		~FWitnessWorld()
		{
			if (World)
			{
				GEngine->DestroyWorldContext(World);
				World->DestroyWorld(/*bInformEngineOfWorld=*/false);
			}
		}

		FWitnessWorld(const FWitnessWorld&) = delete;
		FWitnessWorld& operator=(const FWitnessWorld&) = delete;
	};

	/** What the pawn owns afterwards: identities and counts of the project's components. Names are NOT used as a duplicate proof (a numeric suffix could be absent for other reasons). */
	struct FOwned
	{
		TSet<const UActorComponent*> Identities;
		TMap<FString, int32> CountByClass;
		TArray<FString> StateLines; // sorted: the owned-component array order is not creation order
		bool bAllRegistered = true;
	};

	FOwned ReadOwned(const AActor* Pawn)
	{
		FOwned Out;
		TArray<UActorComponent*> Components;
		Pawn->GetComponents(Components);
		for (const UActorComponent* Component : Components)
		{
			if (!IsRpgComponentClass(Component->GetClass()))
			{
				continue;
			}
			const FString ClassName = Component->GetClass()->GetName();
			Out.Identities.Add(Component);
			Out.CountByClass.FindOrAdd(ClassName) += 1;
			Out.bAllRegistered &= Component->IsRegistered();
			Out.StateLines.Add(FString::Printf(TEXT("%s registered=%d begunplay=%d"), *ClassName, Component->IsRegistered() ? 1 : 0, Component->HasBegunPlay() ? 1 : 0));
		}
		Out.StateLines.Sort();
		return Out;
	}

	TArray<FString> RpgSequence(const TArray<FCreation>& Created)
	{
		TArray<FString> Out;
		for (const FCreation& Record : Created)
		{
			if (IsRpgComponentClass(Record.Class))
			{
				Out.Add(Record.Class->GetName());
			}
		}
		return Out;
	}

	/** Every object created on the pawn, as class path names in creation order: interleaving of other objects shows here. */
	FString FullSequence(const TArray<FCreation>& Created)
	{
		TArray<FString> Names;
		for (const FCreation& Record : Created)
		{
			Names.Add(Record.Class->GetPathName());
		}
		return FString::Join(Names, TEXT(";"));
	}

	/** Lines of the form RPGATTACHWITNESS|label|scenario|kind|value are what the A/B run compares; no pointers, ordinals or timestamps in them. */
	void Emit(const TCHAR* Label, const TCHAR* Scenario, const TCHAR* Kind, const FString& Value)
	{
		UE_LOG(LogRPGAttachWitness, Display, TEXT("RPGATTACHWITNESS|%s|%s|%s|%s"), Label, Scenario, Kind, *Value);
	}

	bool AnyOffThread(const TArray<FCreation>& Created)
	{
		for (const FCreation& Record : Created)
		{
			if (!Record.bGameThread)
			{
				return true;
			}
		}
		return false;
	}

	AActor* SpawnPack(UWorld* World, UClass* Class, const FVector& Location)
	{
		FActorSpawnParameters Params;
		Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
		const FTransform Transform(Location);
		return World->SpawnActor(Class, &Transform, Params);
	}

	/** Checks one spawn: the creation sequence equals the expected one, every expected class is owned exactly once, all are registered. */
	void CheckSpawn(FAutomationTestBase& Test, const TCHAR* Label, const TCHAR* Scenario, const TArray<FCreation>& Created, const FOwned& Owned, const TArray<FString>& Expected)
	{
		const TArray<FString> Sequence = RpgSequence(Created);
		Emit(Label, Scenario, TEXT("RPG"), FString::Join(Sequence, TEXT(",")));
		Emit(Label, Scenario, TEXT("FULL"), FullSequence(Created));
		Emit(Label, Scenario, TEXT("STATE"), FString::Join(Owned.StateLines, TEXT(",")));
		if (Sequence != Expected)
		{
			Test.AddError(FString::Printf(TEXT("%s %s: creation sequence differs from the preimage order. expected [%s] got [%s]"), Label, Scenario, *FString::Join(Expected, TEXT(",")), *FString::Join(Sequence, TEXT(","))));
		}
		if (Owned.Identities.Num() != Expected.Num())
		{
			Test.AddError(FString::Printf(TEXT("%s %s: pawn owns %d project components, expected %d"), Label, Scenario, Owned.Identities.Num(), Expected.Num()));
		}
		for (const FString& Name : Expected)
		{
			const int32* Count = Owned.CountByClass.Find(Name);
			if (!Count || *Count != 1)
			{
				Test.AddError(FString::Printf(TEXT("%s %s: class %s owned %d times, expected exactly once"), Label, Scenario, *Name, Count ? *Count : 0));
			}
		}
		if (!Owned.bAllRegistered)
		{
			Test.AddError(FString::Printf(TEXT("%s %s: a project component is not registered"), Label, Scenario));
		}
		if (AnyOffThread(Created))
		{
			Test.AddError(FString::Printf(TEXT("%s %s: an object with the pawn as outer was created off the game thread"), Label, Scenario));
		}
	}

	bool SameIdentities(const FOwned& A, const FOwned& B)
	{
		if (A.Identities.Num() != B.Identities.Num())
		{
			return false;
		}
		for (const UActorComponent* Component : B.Identities)
		{
			if (!A.Identities.Contains(Component))
			{
				return false;
			}
		}
		return true;
	}

	bool RunScenario(FAutomationTestBase& Test, const TCHAR* Label, const TCHAR* ClassPath, const TArray<FString>& Expected, bool bExpectBoss)
	{
		// P0: unsupported preconditions are explicit errors, never a quietly passing test.
		if (!IsInGameThread() || !GEngine)
		{
			Test.AddError(FString::Printf(TEXT("%s: unsupported precondition: not on the game thread or no GEngine"), Label));
			return false;
		}
		UClass* PackClass = LoadClass<AActor>(nullptr, ClassPath);
		if (!PackClass)
		{
			Test.AddError(FString::Printf(TEXT("%s: unsupported precondition: pack class %s did not load"), Label, ClassPath));
			return false;
		}
		FlushAsyncLoading();
		if (!PackClass->IsChildOf(APawn::StaticClass()))
		{
			Test.AddError(FString::Printf(TEXT("%s: unsupported precondition: %s is not a pawn, so the world-begin loop (TActorIterator<APawn>) would not visit it"), Label, ClassPath));
			return false;
		}

		FWitnessWorld Scope; // declared before the recorder: the recorder is removed first
		if (!Scope.World)
		{
			Test.AddError(FString::Printf(TEXT("%s: unsupported precondition: the test world could not be created"), Label));
			return false;
		}
		if (!Scope.World->GetSubsystem<URPGPlayerMovesSubsystem>())
		{
			Test.AddError(FString::Printf(TEXT("%s: unsupported precondition: URPGPlayerMovesSubsystem does not exist on the test world, so no spawn hook can run"), Label));
			return false;
		}
		if (Scope.World->HasBegunPlay())
		{
			Test.AddError(FString::Printf(TEXT("%s: unsupported precondition: the fresh world already reports begun play"), Label));
			return false;
		}

		FCreationRecorder Recorder;

		// W1: the spawn trigger, the world-begin broadcast not yet run.
		const uint32 MarkW1 = Recorder.Mark();
		AActor* Pawn = SpawnPack(Scope.World, PackClass, FVector(0.f, 0.f, 150.f));
		if (!Pawn)
		{
			Test.AddError(FString::Printf(TEXT("%s: unsupported precondition: the pack class could not be spawned in the bare world"), Label));
			return false;
		}
		if (URPGPlayerMovesSubsystem::IsPackBoss(Pawn) != bExpectBoss || URPGPlayerMovesSubsystem::IsPackPlayer(Pawn) == bExpectBoss)
		{
			Test.AddError(FString::Printf(TEXT("%s: the spawned pawn does not have the expected pack identity (boss=%d player=%d)"), Label, URPGPlayerMovesSubsystem::IsPackBoss(Pawn) ? 1 : 0, URPGPlayerMovesSubsystem::IsPackPlayer(Pawn) ? 1 : 0));
			return false;
		}
		const TArray<FCreation> W1 = Recorder.Since(MarkW1, Pawn);
		const FOwned S1 = ReadOwned(Pawn);
		Emit(Label, TEXT("W1"), TEXT("WORLDBEGUN"), Scope.World->HasBegunPlay() ? TEXT("1") : TEXT("0"));
		Emit(Label, TEXT("W1"), TEXT("ACTORBEGUN"), Pawn->HasActorBegunPlay() ? TEXT("1") : TEXT("0"));
		if (W1.Num() == 0 || S1.Identities.Num() == 0)
		{
			Test.AddError(FString::Printf(TEXT("%s: the spawn hook attached nothing (no creation with the pawn as outer, no project component): spawn trigger not exercised"), Label));
			return false;
		}
		CheckSpawn(Test, Label, TEXT("W1"), W1, S1, Expected);

		// W2: the world-begin trigger on the pawn the spawn trigger already attached. Observed: nothing is created, the identities stay.
		// That the loop actually visited the pawn is source reasoning (OnWorldBeginPlay iterates TActorIterator<APawn>), NOT observed here.
		const uint32 MarkW2 = Recorder.Mark();
		Scope.World->BeginPlay();
		if (!IsValid(Pawn))
		{
			Test.AddError(FString::Printf(TEXT("%s: the pawn was destroyed by the world-begin step"), Label));
			return false;
		}
		const TArray<FCreation> W2 = Recorder.Since(MarkW2, Pawn);
		const FOwned S2 = ReadOwned(Pawn);
		Emit(Label, TEXT("W2"), TEXT("CREATED"), FullSequence(W2));
		Emit(Label, TEXT("W2"), TEXT("STATE"), FString::Join(S2.StateLines, TEXT(",")));
		Emit(Label, TEXT("W2"), TEXT("WORLDBEGUN"), Scope.World->HasBegunPlay() ? TEXT("1") : TEXT("0"));
		Emit(Label, TEXT("W2"), TEXT("ACTORBEGUN"), Pawn->HasActorBegunPlay() ? TEXT("1") : TEXT("0"));
		if (W2.Num() != 0)
		{
			Test.AddError(FString::Printf(TEXT("%s W2: the world-begin step created %d object(s) with the pawn as outer: %s"), Label, W2.Num(), *FullSequence(W2)));
		}
		if (!SameIdentities(S1, S2) || S1.CountByClass.Num() != S2.CountByClass.Num())
		{
			Test.AddError(FString::Printf(TEXT("%s W2: the set of project components changed across the world-begin step"), Label));
		}

		// W3: the spawn trigger again, after the world-begin broadcast: a second pawn gets the same sequence, the first is untouched.
		const uint32 MarkW3 = Recorder.Mark();
		AActor* SecondPawn = SpawnPack(Scope.World, PackClass, FVector(1500.f, 0.f, 150.f));
		if (!SecondPawn)
		{
			Test.AddError(FString::Printf(TEXT("%s W3: the second spawn failed"), Label));
			return false;
		}
		const TArray<FCreation> W3 = Recorder.Since(MarkW3, SecondPawn);
		const FOwned S3 = ReadOwned(SecondPawn);
		CheckSpawn(Test, Label, TEXT("W3"), W3, S3, Expected);
		if (RpgSequence(W1) != RpgSequence(W3))
		{
			Test.AddError(FString::Printf(TEXT("%s W3: the second pawn's creation sequence differs from the first pawn's"), Label));
		}
		if (!SameIdentities(S1, ReadOwned(Pawn)))
		{
			Test.AddError(FString::Printf(TEXT("%s W3: spawning the second pawn changed the first pawn's project components"), Label));
		}

		if (Recorder.Truncated())
		{
			Test.AddError(FString::Printf(TEXT("%s: the creation recorder ran out of room, the sequences are incomplete"), Label));
		}
		return !Test.HasAnyErrors();
	}
}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGAttachWitnessBossTest, "OneBossFight.Player.AttachWitness.Boss",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGAttachWitnessBossTest::RunTest(const FString& Parameters)
{
	return AttachWitness::RunScenario(*this, TEXT("boss"), AttachWitness::BossClassPath, AttachWitness::ExpectedBossSequence(), /*bExpectBoss=*/true);
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGAttachWitnessPlayerTest, "OneBossFight.Player.AttachWitness.Player",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGAttachWitnessPlayerTest::RunTest(const FString& Parameters)
{
	return AttachWitness::RunScenario(*this, TEXT("player"), AttachWitness::PlayerClassPath, AttachWitness::ExpectedPlayerSequence(), /*bExpectBoss=*/false);
}

#endif // WITH_DEV_AUTOMATION_TESTS
