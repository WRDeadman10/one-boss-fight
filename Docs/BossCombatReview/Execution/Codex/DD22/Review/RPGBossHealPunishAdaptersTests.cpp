// Copyright One Boss Fight. All Rights Reserved.
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "Components/SceneComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "Player/RPGBossBleed.h"
#include "Player/RPGBossHealPunish.h"
#include "Player/RPGBossHealPunishAdapters.h"
#include "Player/RPGBossPosture.h"
#include "UObject/Package.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UnrealType.h"
#include <limits>
#include <cmath>

// SOURCE-ONLY until the lead releases execution. No HealPunish BeginPlay, Tick,
// NotifyHealStartedForTest or CancelAll is invoked. No tracker or damage resolver is created.
// These fixtures cannot prove a tracker entry/window, collision, damage, authored
// asset/Details value, projectile traversal, or an operational projectile. The only begun
// actor is a plain fixture owner BEFORE it receives an unregistered component.
namespace
{
namespace HealPunishTests
{
	struct FWorldScope
	{
		UWorld* World = nullptr;
		FWorldScope()
		{
			if (GEngine)
			{
				World = UWorld::CreateWorld(EWorldType::Game, false);
				if (World)
				{
					GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
					World->InitializeActorsForPlay(FURL());
				}
			}
		}
		~FWorldScope()
		{
			if (World)
			{
				GEngine->DestroyWorldContext(World);
				World->DestroyWorld(false);
			}
		}
		FWorldScope(const FWorldScope&) = delete;
		FWorldScope& operator=(const FWorldScope&) = delete;
		AActor* Spawn() const { return World ? World->SpawnActor<AActor>() : nullptr; }
	};



	FRPGHealPunishConfig RecordA()
	{
		FRPGHealPunishConfig R;
		R.bEnabled=false; R.MinRange=0.f; R.MaxRange=0.5f; R.Cooldown=0.f; R.Damage=0.f;
		R.FlightTime=0.05f; R.MinSpeed=0.25f; R.MaxSpeed=0.25f; R.JavelinRadius=0.125f; R.JavelinMaxRange=0.5f;
		R.SpawnSockets={TEXT("Javelin.Emit"),TEXT("hand-l")}; R.AimHeight=-1.0e6f; R.bRespondToHeal=false; R.bCancelJavelinsOnInterrupt=false;
		return R;
	}
	FRPGHealPunishConfig RecordB()
	{
		FRPGHealPunishConfig R;
		R.bEnabled=true; R.MinRange=17.5f; R.MaxRange=1150.f; R.Cooldown=2.5f; R.Damage=23.5f;
		R.FlightTime=1.5f; R.MinSpeed=110.f; R.MaxSpeed=200.f; R.JavelinRadius=15.5f; R.JavelinMaxRange=4444.f;
		R.SpawnSockets={TEXT("CustomEmit"),TEXT("hand_r")}; R.AimHeight=-25.f; R.bRespondToHeal=true; R.bCancelJavelinsOnInterrupt=true;
		return R;
	}
	FRPGParticipantConfig Config(const FRPGHealPunishConfig& R) { FRPGParticipantConfig C; C.HealPunish=R; return C; }
	FRPGHealPunishConfig Read(const URPGBossHealPunish& C)
	{
		FRPGHealPunishConfig R;
		R.bEnabled=C.bEnabled;
		R.MinRange=C.MinRange;
		R.MaxRange=C.MaxRange;
		R.Cooldown=C.Cooldown;
		R.Damage=C.Damage;
		R.FlightTime=C.FlightTime;
		R.MinSpeed=C.MinSpeed;
		R.MaxSpeed=C.MaxSpeed;
		R.JavelinRadius=C.JavelinRadius;
		R.JavelinMaxRange=C.JavelinMaxRange;
		R.SpawnSockets=C.SpawnSockets;
		R.AimHeight=C.AimHeight;
		R.bRespondToHeal=C.bRespondToHeal;
		R.bCancelJavelinsOnInterrupt=C.bCancelJavelinsOnInterrupt;
		return R;
	}
	bool Same(const FRPGHealPunishConfig& A,const FRPGHealPunishConfig& B)
	{
		return A.bEnabled==B.bEnabled && A.MinRange==B.MinRange && A.MaxRange==B.MaxRange && A.Cooldown==B.Cooldown && A.Damage==B.Damage && A.FlightTime==B.FlightTime && A.MinSpeed==B.MinSpeed && A.MaxSpeed==B.MaxSpeed && A.JavelinRadius==B.JavelinRadius && A.JavelinMaxRange==B.JavelinMaxRange && A.SpawnSockets==B.SpawnSockets && A.AimHeight==B.AimHeight && A.bRespondToHeal==B.bRespondToHeal && A.bCancelJavelinsOnInterrupt==B.bCancelJavelinsOnInterrupt;
	}

	struct FRuntime
	{
		bool Pending,Registered,Begun,TickRegistered,CanTick;
		float Cooldown;
		TArray<int32> Counters;
		explicit FRuntime(const URPGBossHealPunish& C)
			: Pending(C.IsPending()),Registered(C.IsRegistered()),Begun(C.HasBegunPlay()),
			  TickRegistered(C.PrimaryComponentTick.IsTickFunctionRegistered()),CanTick(C.PrimaryComponentTick.bCanEverTick),Cooldown(C.GetCooldownRemaining()),
			  Counters{C.GetHealEventCount(),C.GetAcceptedCount(),C.GetReleasedCount(),C.GetDiscardedBusyCount(),C.GetDiscardedRangeCount(),
				C.GetDiscardedSightCount(),C.GetDiscardedCooldownCount(),C.GetDiscardedPendingCount(),C.GetCancelledCount(),C.GetJavelinHitCount(),C.GetJavelinDodgedCount(),C.GetJavelinWorldCount()} {}
		bool SameAs(const FRuntime& O) const
		{
			return Pending==O.Pending&&Registered==O.Registered&&Begun==O.Begun&&TickRegistered==O.TickRegistered
				&&CanTick==O.CanTick&&Cooldown==O.Cooldown&&Counters==O.Counters;
		}
	};
	TArray<const UActorComponent*> Owned(const AActor* Owner)
	{
		TArray<const UActorComponent*> Result;
		for (const UActorComponent* C : Owner->GetComponents()) { Result.Add(C); }
		return Result;
	}
	bool SameOwned(const TArray<const UActorComponent*>& A, const TArray<const UActorComponent*>& B)
	{
		if (A.Num() != B.Num()) { return false; }
		for (const UActorComponent* C : A) { if (!B.Contains(C)) { return false; } }
		return true;
	}
	TArray<FString> Paths()
	{
		return {TEXT("HealPunish.bEnabled"),TEXT("HealPunish.MinRange"),TEXT("HealPunish.MaxRange"),TEXT("HealPunish.Cooldown"),TEXT("HealPunish.Damage"),TEXT("HealPunish.FlightTime"),TEXT("HealPunish.MinSpeed"),TEXT("HealPunish.MaxSpeed"),TEXT("HealPunish.JavelinRadius"),TEXT("HealPunish.JavelinMaxRange"),TEXT("HealPunish.SpawnSockets"),TEXT("HealPunish.AimHeight"),TEXT("HealPunish.bRespondToHeal"),TEXT("HealPunish.bCancelJavelinsOnInterrupt")};
	}

	struct FBad
	{
		FString Name;
		TFunction<void(FRPGHealPunishConfig&)> Mutate;
		const TCHAR* Token;
		const TCHAR* Path;
	};
	TArray<FBad> BadCases()
	{
		TArray<FBad> Cases;
		Cases.Add({TEXT("MinRange NaN"),[](FRPGHealPunishConfig& R){R.MinRange=std::numeric_limits<float>::quiet_NaN();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldMinRange});
		Cases.Add({TEXT("MinRange +Inf"),[](FRPGHealPunishConfig& R){R.MinRange=std::numeric_limits<float>::infinity();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldMinRange});
		Cases.Add({TEXT("MinRange -Inf"),[](FRPGHealPunishConfig& R){R.MinRange=-std::numeric_limits<float>::infinity();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldMinRange});
		Cases.Add({TEXT("MaxRange NaN"),[](FRPGHealPunishConfig& R){R.MaxRange=std::numeric_limits<float>::quiet_NaN();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldMaxRange});
		Cases.Add({TEXT("MaxRange +Inf"),[](FRPGHealPunishConfig& R){R.MaxRange=std::numeric_limits<float>::infinity();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldMaxRange});
		Cases.Add({TEXT("MaxRange -Inf"),[](FRPGHealPunishConfig& R){R.MaxRange=-std::numeric_limits<float>::infinity();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldMaxRange});
		Cases.Add({TEXT("Cooldown NaN"),[](FRPGHealPunishConfig& R){R.Cooldown=std::numeric_limits<float>::quiet_NaN();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldCooldown});
		Cases.Add({TEXT("Cooldown +Inf"),[](FRPGHealPunishConfig& R){R.Cooldown=std::numeric_limits<float>::infinity();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldCooldown});
		Cases.Add({TEXT("Cooldown -Inf"),[](FRPGHealPunishConfig& R){R.Cooldown=-std::numeric_limits<float>::infinity();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldCooldown});
		Cases.Add({TEXT("Damage NaN"),[](FRPGHealPunishConfig& R){R.Damage=std::numeric_limits<float>::quiet_NaN();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldDamage});
		Cases.Add({TEXT("Damage +Inf"),[](FRPGHealPunishConfig& R){R.Damage=std::numeric_limits<float>::infinity();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldDamage});
		Cases.Add({TEXT("Damage -Inf"),[](FRPGHealPunishConfig& R){R.Damage=-std::numeric_limits<float>::infinity();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldDamage});
		Cases.Add({TEXT("FlightTime NaN"),[](FRPGHealPunishConfig& R){R.FlightTime=std::numeric_limits<float>::quiet_NaN();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldFlightTime});
		Cases.Add({TEXT("FlightTime +Inf"),[](FRPGHealPunishConfig& R){R.FlightTime=std::numeric_limits<float>::infinity();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldFlightTime});
		Cases.Add({TEXT("FlightTime -Inf"),[](FRPGHealPunishConfig& R){R.FlightTime=-std::numeric_limits<float>::infinity();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldFlightTime});
		Cases.Add({TEXT("MinSpeed NaN"),[](FRPGHealPunishConfig& R){R.MinSpeed=std::numeric_limits<float>::quiet_NaN();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldMinSpeed});
		Cases.Add({TEXT("MinSpeed +Inf"),[](FRPGHealPunishConfig& R){R.MinSpeed=std::numeric_limits<float>::infinity();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldMinSpeed});
		Cases.Add({TEXT("MinSpeed -Inf"),[](FRPGHealPunishConfig& R){R.MinSpeed=-std::numeric_limits<float>::infinity();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldMinSpeed});
		Cases.Add({TEXT("MaxSpeed NaN"),[](FRPGHealPunishConfig& R){R.MaxSpeed=std::numeric_limits<float>::quiet_NaN();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldMaxSpeed});
		Cases.Add({TEXT("MaxSpeed +Inf"),[](FRPGHealPunishConfig& R){R.MaxSpeed=std::numeric_limits<float>::infinity();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldMaxSpeed});
		Cases.Add({TEXT("MaxSpeed -Inf"),[](FRPGHealPunishConfig& R){R.MaxSpeed=-std::numeric_limits<float>::infinity();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldMaxSpeed});
		Cases.Add({TEXT("JavelinRadius NaN"),[](FRPGHealPunishConfig& R){R.JavelinRadius=std::numeric_limits<float>::quiet_NaN();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldJavelinRadius});
		Cases.Add({TEXT("JavelinRadius +Inf"),[](FRPGHealPunishConfig& R){R.JavelinRadius=std::numeric_limits<float>::infinity();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldJavelinRadius});
		Cases.Add({TEXT("JavelinRadius -Inf"),[](FRPGHealPunishConfig& R){R.JavelinRadius=-std::numeric_limits<float>::infinity();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldJavelinRadius});
		Cases.Add({TEXT("JavelinMaxRange NaN"),[](FRPGHealPunishConfig& R){R.JavelinMaxRange=std::numeric_limits<float>::quiet_NaN();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldJavelinMaxRange});
		Cases.Add({TEXT("JavelinMaxRange +Inf"),[](FRPGHealPunishConfig& R){R.JavelinMaxRange=std::numeric_limits<float>::infinity();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldJavelinMaxRange});
		Cases.Add({TEXT("JavelinMaxRange -Inf"),[](FRPGHealPunishConfig& R){R.JavelinMaxRange=-std::numeric_limits<float>::infinity();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldJavelinMaxRange});
		Cases.Add({TEXT("AimHeight NaN"),[](FRPGHealPunishConfig& R){R.AimHeight=std::numeric_limits<float>::quiet_NaN();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldAimHeight});
		Cases.Add({TEXT("AimHeight +Inf"),[](FRPGHealPunishConfig& R){R.AimHeight=std::numeric_limits<float>::infinity();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldAimHeight});
		Cases.Add({TEXT("AimHeight -Inf"),[](FRPGHealPunishConfig& R){R.AimHeight=-std::numeric_limits<float>::infinity();},TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldAimHeight});
		Cases.Add({TEXT("negative min"),[](FRPGHealPunishConfig& R){R.MinRange=-1.f;},TEXT("InvalidPunish.Negative"),RPGBossHealPunishAdapters::FieldMinRange});
		Cases.Add({TEXT("zero max"),[](FRPGHealPunishConfig& R){R.MaxRange=0.f;},TEXT("InvalidPunish.NotPositive"),RPGBossHealPunishAdapters::FieldMaxRange});
		Cases.Add({TEXT("negative max"),[](FRPGHealPunishConfig& R){R.MaxRange=-1.f;},TEXT("InvalidPunish.NotPositive"),RPGBossHealPunishAdapters::FieldMaxRange});
		Cases.Add({TEXT("equal range"),[](FRPGHealPunishConfig& R){R.MinRange=1.f;R.MaxRange=1.f;},TEXT("InvalidPunish.MaxNotAboveMin"),RPGBossHealPunishAdapters::FieldMaxRange});
		Cases.Add({TEXT("inverted range"),[](FRPGHealPunishConfig& R){R.MinRange=2.f;R.MaxRange=1.f;},TEXT("InvalidPunish.MaxNotAboveMin"),RPGBossHealPunishAdapters::FieldMaxRange});
		Cases.Add({TEXT("negative cooldown"),[](FRPGHealPunishConfig& R){R.Cooldown=-1.f;},TEXT("InvalidPunish.Negative"),RPGBossHealPunishAdapters::FieldCooldown});
		Cases.Add({TEXT("negative damage"),[](FRPGHealPunishConfig& R){R.Damage=-1.f;},TEXT("InvalidPunish.Negative"),RPGBossHealPunishAdapters::FieldDamage});
		Cases.Add({TEXT("below flight floor"),[](FRPGHealPunishConfig& R){R.FlightTime=std::nextafter(RPGBossHealPunishAdapters::MinAuthoredFlightTime,0.f);},TEXT("InvalidPunish.BelowFlightTimeFloor"),RPGBossHealPunishAdapters::FieldFlightTime});
		Cases.Add({TEXT("zero flight"),[](FRPGHealPunishConfig& R){R.FlightTime=0.f;},TEXT("InvalidPunish.BelowFlightTimeFloor"),RPGBossHealPunishAdapters::FieldFlightTime});
		Cases.Add({TEXT("negative flight"),[](FRPGHealPunishConfig& R){R.FlightTime=-1.f;},TEXT("InvalidPunish.BelowFlightTimeFloor"),RPGBossHealPunishAdapters::FieldFlightTime});
		Cases.Add({TEXT("MinSpeed zero"),[](FRPGHealPunishConfig& R){R.MinSpeed=0.f;},TEXT("InvalidPunish.NotPositive"),RPGBossHealPunishAdapters::FieldMinSpeed});
		Cases.Add({TEXT("MinSpeed negative"),[](FRPGHealPunishConfig& R){R.MinSpeed=-0.5f;},TEXT("InvalidPunish.NotPositive"),RPGBossHealPunishAdapters::FieldMinSpeed});
		Cases.Add({TEXT("MaxSpeed zero"),[](FRPGHealPunishConfig& R){R.MaxSpeed=0.f;},TEXT("InvalidPunish.NotPositive"),RPGBossHealPunishAdapters::FieldMaxSpeed});
		Cases.Add({TEXT("MaxSpeed negative"),[](FRPGHealPunishConfig& R){R.MaxSpeed=-0.5f;},TEXT("InvalidPunish.NotPositive"),RPGBossHealPunishAdapters::FieldMaxSpeed});
		Cases.Add({TEXT("JavelinRadius zero"),[](FRPGHealPunishConfig& R){R.JavelinRadius=0.f;},TEXT("InvalidPunish.NotPositive"),RPGBossHealPunishAdapters::FieldJavelinRadius});
		Cases.Add({TEXT("JavelinRadius negative"),[](FRPGHealPunishConfig& R){R.JavelinRadius=-0.5f;},TEXT("InvalidPunish.NotPositive"),RPGBossHealPunishAdapters::FieldJavelinRadius});
		Cases.Add({TEXT("JavelinMaxRange zero"),[](FRPGHealPunishConfig& R){R.JavelinMaxRange=0.f;},TEXT("InvalidPunish.NotPositive"),RPGBossHealPunishAdapters::FieldJavelinMaxRange});
		Cases.Add({TEXT("JavelinMaxRange negative"),[](FRPGHealPunishConfig& R){R.JavelinMaxRange=-0.5f;},TEXT("InvalidPunish.NotPositive"),RPGBossHealPunishAdapters::FieldJavelinMaxRange});
		Cases.Add({TEXT("speed interval inverted"),[](FRPGHealPunishConfig& R){R.MinSpeed=2.f;R.MaxSpeed=1.f;},TEXT("InvalidPunish.MinSpeedAboveMax"),RPGBossHealPunishAdapters::FieldMinSpeed});
		Cases.Add({TEXT("MinRange next float above ceiling"),[](FRPGHealPunishConfig& R){R.MinRange=std::nextafter(RPGBossHealPunishAdapters::MaxAuthoredMagnitude,std::numeric_limits<float>::infinity());},TEXT("InvalidPunish.AboveCeiling"),RPGBossHealPunishAdapters::FieldMinRange});
		Cases.Add({TEXT("MaxRange next float above ceiling"),[](FRPGHealPunishConfig& R){R.MaxRange=std::nextafter(RPGBossHealPunishAdapters::MaxAuthoredMagnitude,std::numeric_limits<float>::infinity());},TEXT("InvalidPunish.AboveCeiling"),RPGBossHealPunishAdapters::FieldMaxRange});
		Cases.Add({TEXT("Cooldown next float above ceiling"),[](FRPGHealPunishConfig& R){R.Cooldown=std::nextafter(RPGBossHealPunishAdapters::MaxAuthoredMagnitude,std::numeric_limits<float>::infinity());},TEXT("InvalidPunish.AboveCeiling"),RPGBossHealPunishAdapters::FieldCooldown});
		Cases.Add({TEXT("FlightTime next float above ceiling"),[](FRPGHealPunishConfig& R){R.FlightTime=std::nextafter(RPGBossHealPunishAdapters::MaxAuthoredMagnitude,std::numeric_limits<float>::infinity());},TEXT("InvalidPunish.AboveCeiling"),RPGBossHealPunishAdapters::FieldFlightTime});
		Cases.Add({TEXT("MinSpeed next float above ceiling"),[](FRPGHealPunishConfig& R){R.MinSpeed=std::nextafter(RPGBossHealPunishAdapters::MaxAuthoredMagnitude,std::numeric_limits<float>::infinity());},TEXT("InvalidPunish.AboveCeiling"),RPGBossHealPunishAdapters::FieldMinSpeed});
		Cases.Add({TEXT("MaxSpeed next float above ceiling"),[](FRPGHealPunishConfig& R){R.MaxSpeed=std::nextafter(RPGBossHealPunishAdapters::MaxAuthoredMagnitude,std::numeric_limits<float>::infinity());},TEXT("InvalidPunish.AboveCeiling"),RPGBossHealPunishAdapters::FieldMaxSpeed});
		Cases.Add({TEXT("JavelinRadius next float above ceiling"),[](FRPGHealPunishConfig& R){R.JavelinRadius=std::nextafter(RPGBossHealPunishAdapters::MaxAuthoredMagnitude,std::numeric_limits<float>::infinity());},TEXT("InvalidPunish.AboveCeiling"),RPGBossHealPunishAdapters::FieldJavelinRadius});
		Cases.Add({TEXT("JavelinMaxRange next float above ceiling"),[](FRPGHealPunishConfig& R){R.JavelinMaxRange=std::nextafter(RPGBossHealPunishAdapters::MaxAuthoredMagnitude,std::numeric_limits<float>::infinity());},TEXT("InvalidPunish.AboveCeiling"),RPGBossHealPunishAdapters::FieldJavelinMaxRange});
		Cases.Add({TEXT("AimHeight next float above ceiling"),[](FRPGHealPunishConfig& R){R.AimHeight=std::nextafter(RPGBossHealPunishAdapters::MaxAuthoredMagnitude,std::numeric_limits<float>::infinity());},TEXT("InvalidPunish.AboveCeiling"),RPGBossHealPunishAdapters::FieldAimHeight});
		Cases.Add({TEXT("aim below signed floor"),[](FRPGHealPunishConfig& R){R.AimHeight=std::nextafter(-RPGBossHealPunishAdapters::MaxAuthoredMagnitude,-std::numeric_limits<float>::infinity());},TEXT("InvalidPunish.BelowFloor"),RPGBossHealPunishAdapters::FieldAimHeight});
		Cases.Add({TEXT("empty sockets"),[](FRPGHealPunishConfig& R){R.SpawnSockets.Reset();},TEXT("InvalidDependency.Missing"),RPGBossHealPunishAdapters::FieldSpawnSockets});
		Cases.Add({TEXT("late None socket"),[](FRPGHealPunishConfig& R){R.SpawnSockets[1]=NAME_None;},TEXT("InvalidDependency.Malformed"),RPGBossHealPunishAdapters::FieldSpawnSockets});
		Cases.Add({TEXT("space socket"),[](FRPGHealPunishConfig& R){R.SpawnSockets[0]=TEXT("hand left");},TEXT("InvalidDependency.Malformed"),RPGBossHealPunishAdapters::FieldSpawnSockets});
		Cases.Add({TEXT("tab socket"),[](FRPGHealPunishConfig& R){R.SpawnSockets[1]=TEXT("hand\tleft");},TEXT("InvalidDependency.Malformed"),RPGBossHealPunishAdapters::FieldSpawnSockets});
		Cases.Add({TEXT("control socket"),[](FRPGHealPunishConfig& R){R.SpawnSockets[1]=FName(*FString::Printf(TEXT("hand%cL"),static_cast<TCHAR>(0x7f)));},TEXT("InvalidDependency.Malformed"),RPGBossHealPunishAdapters::FieldSpawnSockets});
		return Cases;
	}

	bool HasError(const FRPGHydrationResult& R, const TCHAR* Token, const TCHAR* Path)
	{
		return R.Errors.ContainsByPredicate([Token, Path](const FString& E) { return E.Contains(Token) && E.Contains(Path); });
	}
	TStrongObjectPtr<URPGBossDefinition> Definition(const FRPGHealPunishConfig& R)
	{
		TStrongObjectPtr<URPGBossDefinition> D(NewObject<URPGBossDefinition>());
		D->Schema = 1; D->DefinitionId = TEXT("HealPunishFixture"); D->PresentationId = TEXT("FixtureLook");
		D->Stats.MaxHealth = 1234.f; D->Stats.MaxPosture = 87.f;
		D->Stats.PostureRegenDelay = 2.f; D->Stats.PostureRegenRate = 3.f;
		D->HealPunish = R;
		for (const FString& Path : Paths())
		{
			FRPGParityField Field;
			Field.FieldPath = Path; Field.Value = TEXT("not parsed as config"); Field.Type = TEXT("fixture");
			Field.SourcePath = TEXT("synthetic only"); Field.SourceSHA256 = FString::ChrN(64, TEXT('a'));
			Field.SourceSite = TEXT("fixture"); Field.Origin = TEXT("test"); Field.Precedence = TEXT("fixture");
			Field.Destination = TEXT("fixture"); Field.FirstRead = TEXT("not runtime"); Field.Witness = TEXT("none");
			D->Fields.Add(Field);
		}
		return D;
	}
}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGHealPunishAssignTest, "OneBossFight.Binding.HealPunish.Assign", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGHealPunishAssignTest::RunTest(const FString& Parameters)
{
	using namespace HealPunishTests;
	FWorldScope Scope;
	AActor* Owner = Scope.Spawn();
	if (!TestNotNull(TEXT("owner"), Owner)) { return false; }
	TStrongObjectPtr<URPGBossHealPunish> Punish(NewObject<URPGBossHealPunish>(Owner, TEXT("RPGBossHealPunish")));
	TStrongObjectPtr<URPGBossPosture> Other(NewObject<URPGBossPosture>(Owner));
	const float OtherBefore = Other->PostureMax;
	const auto Before = Owned(Owner);
	const FRuntime Runtime(*Punish);
	const FRPGComponentPlan Plan = RPGBossHealPunishAdapters::MakeHealPunishPlan();
	TestTrue(TEXT("exact class/name and fourteen exact paths, without duplicates"), Plan.Class == URPGBossHealPunish::StaticClass()
		&& Plan.InstanceName == FName(TEXT("RPGBossHealPunish")) && Plan.RequiredFields == Paths());
	if (!TestTrue(TEXT("plan callback exists"), static_cast<bool>(Plan.Configure))) { return false; }
	FString Error = TEXT("stale diagnostic");
	TestTrue(TEXT("callback copies all fourteen nondefault fields"), Plan.Configure(*Punish, Config(RecordA()), Error) && Error.IsEmpty() && Same(Read(*Punish), RecordA()));
	TestTrue(TEXT("runtime, lifecycle, owner component set and unrelated component unchanged"), Runtime.SameAs(FRuntime(*Punish))
		&& SameOwned(Before, Owned(Owner)) && Other->PostureMax == OtherBefore && Punish->GetOwner() == Owner && Punish->GetOuter() == Owner);
	TestTrue(TEXT("second call writes another complete record"), Plan.Configure(*Punish, Config(RecordB()), Error) && Same(Read(*Punish), RecordB()) && Runtime.SameAs(FRuntime(*Punish)));
	AddInfo(TEXT("Socket names copied by value; native A5/drink montage/socket resolution is unresolved."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGHealPunishValidationTest, "OneBossFight.Binding.HealPunish.Validation", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGHealPunishValidationTest::RunTest(const FString& Parameters)
{
	using namespace HealPunishTests;
	FWorldScope Scope;
	AActor* Owner = Scope.Spawn();
	if (!TestNotNull(TEXT("owner"), Owner)) { return false; }
	TStrongObjectPtr<URPGBossHealPunish> Punish(NewObject<URPGBossHealPunish>(Owner));
	const auto Before = Read(*Punish);
	const FRuntime Runtime(*Punish);
	const auto Components = Owned(Owner);
	for (const FBad& Case : BadCases())
	{
		auto R = RecordA(); // deliberately disabled; disabled must NOT bypass validation
		Case.Mutate(R);
		FString Error;
		TestFalse(Case.Name + TEXT(": validator rejects"), RPGBossHealPunishAdapters::ValidateHealPunish(R, Error));
		TestTrue(Case.Name + TEXT(": named validator field"), Error.StartsWith(Case.Token) && Error.Contains(Case.Path));
		TestFalse(Case.Name + TEXT(": callback rejects"), RPGBossHealPunishAdapters::ConfigureHealPunish(*Punish, Config(R), Error));
		TestTrue(Case.Name + TEXT(": complete no-write and matching reason"), Error.StartsWith(Case.Token) && Error.Contains(Case.Path)
			&& Same(Read(*Punish), Before) && Runtime.SameAs(FRuntime(*Punish)) && SameOwned(Components, Owned(Owner)));
	}


	TArray<FRPGHealPunishConfig> Valid{RecordA(),RecordB(),FRPGHealPunishConfig()};
	const float Ceiling=RPGBossHealPunishAdapters::MaxAuthoredMagnitude;
	auto Pair=RecordB();Pair.MinRange=std::nextafter(Ceiling,0.f);Pair.MaxRange=Ceiling;Valid.Add(Pair);
	auto EqualSpeed=RecordA();EqualSpeed.MinSpeed=Ceiling;EqualSpeed.MaxSpeed=Ceiling;Valid.Add(EqualSpeed);
	{auto R=RecordA();R.MaxRange=Ceiling;Valid.Add(R);}
	{auto R=RecordA();R.Cooldown=Ceiling;Valid.Add(R);}
	{auto R=RecordA();R.FlightTime=Ceiling;Valid.Add(R);}
	{auto R=RecordA();R.MaxSpeed=Ceiling;Valid.Add(R);}
	{auto R=RecordA();R.JavelinRadius=Ceiling;Valid.Add(R);}
	{auto R=RecordA();R.JavelinMaxRange=Ceiling;Valid.Add(R);}
	{auto R=RecordA();R.AimHeight=Ceiling;Valid.Add(R);}

	auto Damage=RecordA();Damage.Damage=std::numeric_limits<float>::max();Valid.Add(Damage);
	auto Duplicates=RecordA();Duplicates.SpawnSockets={TEXT("hand.l"),TEXT("hand.l")};Valid.Add(Duplicates); // no invented uniqueness/ASCII-only rule
	for(int32 I=0;I<3;++I)
	{
		auto R=RecordB(); if(I==0){R.bEnabled=false;}else if(I==1){R.bRespondToHeal=false;}else{R.bCancelJavelinsOnInterrupt=false;} Valid.Add(R);
	}
	for(const auto& R : Valid)
	{
		FString E=TEXT("stale");
		TestTrue(TEXT("valid zero/floor/fractional/ceiling/signed-aim/equal-speed/duplicate-socket record validates and assigns"),
			RPGBossHealPunishAdapters::ValidateHealPunish(R,E)&&E.IsEmpty()
			&&RPGBossHealPunishAdapters::ConfigureHealPunish(*Punish,Config(R),E)&&Same(Read(*Punish),R)&&Runtime.SameAs(FRuntime(*Punish)));
	}
	auto CheckFirst=[this](const FRPGHealPunishConfig& R,const TCHAR* Token,const TCHAR* Field)
	{
		FString E;RPGBossHealPunishAdapters::ValidateHealPunish(R,E);
		TestTrue(TEXT("validation order"),E.StartsWith(Token)&&E.Contains(Field));
	};
	auto R=RecordB();R.MinRange=-1.f;R.AimHeight=std::numeric_limits<float>::quiet_NaN();
	CheckFirst(R,TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldAimHeight);
	R=RecordB();R.MaxRange=std::numeric_limits<float>::infinity();R.Damage=std::numeric_limits<float>::quiet_NaN();
	CheckFirst(R,TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldMaxRange);
	R=RecordB();R.MinRange=Ceiling;R.MaxRange=Ceiling;
	CheckFirst(R,TEXT("InvalidPunish.MaxNotAboveMin"),RPGBossHealPunishAdapters::FieldMaxRange);
	R=RecordB();R.MinSpeed=1.f;R.MaxSpeed=0.f;
	CheckFirst(R,TEXT("InvalidPunish.NotPositive"),RPGBossHealPunishAdapters::FieldMaxSpeed);
	R=RecordB();R.SpawnSockets.Reset();R.AimHeight=Ceiling*2.f;
	CheckFirst(R,TEXT("InvalidDependency.Missing"),RPGBossHealPunishAdapters::FieldSpawnSockets);
	R=RecordB();R.SpawnSockets.Reset();R.AimHeight=std::numeric_limits<float>::quiet_NaN();
	CheckFirst(R,TEXT("InvalidPunish.NotFinite"),RPGBossHealPunishAdapters::FieldAimHeight);

	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGHealPunishIsolationTest, "OneBossFight.Binding.HealPunish.Isolation", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGHealPunishIsolationTest::RunTest(const FString& Parameters)
{
	using namespace HealPunishTests;
	FWorldScope Scope;
	AActor* OwnerA = Scope.Spawn(); AActor* OwnerB = Scope.Spawn();
	if (!TestTrue(TEXT("two owners"), OwnerA && OwnerB)) { return false; }
	TStrongObjectPtr<URPGBossHealPunish> A(NewObject<URPGBossHealPunish>(OwnerA));
	TStrongObjectPtr<URPGBossHealPunish> B(NewObject<URPGBossHealPunish>(OwnerB));
	TStrongObjectPtr<URPGBossHealPunish> Untouched(NewObject<URPGBossHealPunish>(OwnerB));
	TStrongObjectPtr<URPGBossBleed> Other(NewObject<URPGBossBleed>(OwnerA));
	const auto Original = Read(*Untouched); const auto Default = Read(*GetDefault<URPGBossHealPunish>());
	const FRuntime RuntimeA(*A), RuntimeB(*B);
	const auto OwnedA = Owned(OwnerA), OwnedB = Owned(OwnerB);
	const float BleedBefore = Other->InitialThreshold;
	auto Input = Config(RecordA()); FString Error;
	TestTrue(TEXT("A assignment"), RPGBossHealPunishAdapters::ConfigureHealPunish(*A, Input, Error));
	Input.HealPunish.SpawnSockets[0]=TEXT("ChangedAfterAssign"); Input.HealPunish.SpawnSockets.Add(TEXT("Extra"));
	TestTrue(TEXT("native socket array owns an independent copy"),Same(Read(*A),RecordA()));
	Input.HealPunish = RecordB();
	TestTrue(TEXT("input is a value snapshot"), Same(Read(*A), RecordA()));
	TestTrue(TEXT("B assignment"), RPGBossHealPunishAdapters::ConfigureHealPunish(*B, Input, Error));
	auto Invalid = RecordB(); Invalid.SpawnSockets.Reset();
	TestFalse(TEXT("late invalid input refuses on configured A"), RPGBossHealPunishAdapters::ConfigureHealPunish(*A, Config(Invalid), Error));
	TestTrue(TEXT("owners and unrelated values fully isolated"), Same(Read(*A), RecordA()) && Same(Read(*B), RecordB())
		&& Same(Read(*Untouched), Original) && Same(Read(*GetDefault<URPGBossHealPunish>()), Default)
		&& RuntimeA.SameAs(FRuntime(*A)) && RuntimeB.SameAs(FRuntime(*B))
		&& SameOwned(OwnedA, Owned(OwnerA)) && SameOwned(OwnedB, Owned(OwnerB)) && Other->InitialThreshold == BleedBefore);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGHealPunishRejectionsTest, "OneBossFight.Binding.HealPunish.Rejections", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGHealPunishRejectionsTest::RunTest(const FString& Parameters)
{
	using namespace HealPunishTests;
	FWorldScope Scope;
	AActor* Owner = Scope.Spawn();
	if (!TestNotNull(TEXT("owner"), Owner)) { return false; }
	auto Check = [this](UActorComponent& C, const TCHAR* Token)
	{
		const bool Registered = C.IsRegistered(), Begun = C.HasBegunPlay();
		const URPGBossHealPunish* Punish = Cast<URPGBossHealPunish>(&C);
		const auto Before = Punish ? Read(*Punish) : FRPGHealPunishConfig();
		FString Error;
		auto Bad = RecordA(); Bad.SpawnSockets.Reset();
		for (const auto& R : TArray<FRPGHealPunishConfig>{RecordA(), Bad})
		{
			TestFalse(TEXT("lifecycle/class rejection"), RPGBossHealPunishAdapters::ConfigureHealPunish(C, Config(R), Error));
			TestTrue(TEXT("lifecycle before invalid record; no lifecycle write"), Error.StartsWith(Token) && C.IsRegistered() == Registered && C.HasBegunPlay() == Begun);
			if (Punish) { TestTrue(TEXT("no partial configuration write on lifecycle refusal"), Same(Read(*Punish), Before)); }
		}
	};
	TStrongObjectPtr<USceneComponent> Wrong(NewObject<USceneComponent>(Owner));
	Check(*Wrong, TEXT("WrongComponentClass"));
	TStrongObjectPtr<URPGBossBleed> WrongNative(NewObject<URPGBossBleed>(Owner));
	Check(*WrongNative, TEXT("WrongComponentClass"));
	TStrongObjectPtr<URPGBossHealPunish> Registered(NewObject<URPGBossHealPunish>(Owner));
	Registered->RegisterComponent();
	if (!TestTrue(TEXT("fixture registered but not begun"), Registered->IsRegistered() && !Registered->HasBegunPlay())) { return false; }
	Check(*Registered, TEXT("ComponentAlreadyRegistered"));
	AActor* LateOwner = Scope.Spawn();
	if (!TestNotNull(TEXT("late owner"), LateOwner)) { return false; }
	LateOwner->DispatchBeginPlay(); // plain actor, NO HealPunish component yet
	if (!TestTrue(TEXT("plain owner began"), LateOwner->HasActorBegunPlay())) { return false; }
	TStrongObjectPtr<URPGBossHealPunish> Late(NewObject<URPGBossHealPunish>(LateOwner));
	Check(*Late, TEXT("OwnerBegunPlay"));
	TStrongObjectPtr<URPGBossHealPunish> Orphan(NewObject<URPGBossHealPunish>(GetTransientPackage()));
	Check(*Orphan, TEXT("InvalidOwner"));
	TStrongObjectPtr<URPGBossHealPunish> Destroyed(NewObject<URPGBossHealPunish>(Owner));
	Destroyed->DestroyComponent();
	Check(*Destroyed, TEXT("InvalidComponent")); // retained object, not freed memory
	AddInfo(TEXT("ComponentBegunPlay guard source-only: no HealPunish BeginPlay invoked. Registered and plain begun-owner fixtures do not start a sweep."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGHealPunishCompileTest, "OneBossFight.Binding.HealPunish.Compile", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGHealPunishCompileTest::RunTest(const FString& Parameters)
{
	using namespace HealPunishTests;
	const auto Content = RPGCombatRegistry::Legacy(); // accepted dev-only synthetic contract
	if (!TestTrue(TEXT("synthetic content lease exists"), Content.IsValid())) { return false; }
	TSharedPtr<const FRPGParticipantConfig> Out;
	auto D = Definition(RecordA());
	auto Compile = [&Content](const URPGBossDefinition& Def, TSharedPtr<const FRPGParticipantConfig>& Output)
	{
		return RPGCombatHydration::CompileSyntheticParticipant(Def, Content, FString::ChrN(64, TEXT('b')), Output);
	};
	if (!TestTrue(TEXT("synthetic compiler positive control"), Compile(*D, Out).IsReady() && Out.IsValid())) { return false; }
	TestTrue(TEXT("all fourteen typed values copied, dev-only flag, same epoch; manifest Value not parsed"), Same(Out->HealPunish, RecordA()) && Out->bSyntheticFixture && Out->Content.Get() == Content.Get());
	D->HealPunish = RecordB();
	TestTrue(TEXT("compiled config is immutable value snapshot"), Same(Out->HealPunish, RecordA()));
	TestTrue(TEXT("next compile copies independent record"),Compile(*D,Out).IsReady()&&Out.IsValid()&&Same(Out->HealPunish,RecordB()));
	D->HealPunish.SpawnSockets[0]=TEXT("ChangedAfterCompile");
	TestTrue(TEXT("compiled socket array owns an independent copy"),Out.IsValid()&&Same(Out->HealPunish,RecordB()));
	for (const FBad& Case : BadCases())
	{
		auto R = RecordA(); Case.Mutate(R);
		auto Broken = Definition(R);
		if (!Compile(*Definition(RecordA()), Out).IsReady() || !Out.IsValid()) { AddError(TEXT("valid sentinel failed")); return false; }
		auto Result = Compile(*Broken, Out);
		TestTrue(Case.Name + TEXT(": synthetic rejection clears old output with named field"), !Result.IsReady() && !Out.IsValid() && HasError(Result, Case.Token, Case.Path));
		if (!Compile(*Definition(RecordA()), Out).IsReady() || !Out.IsValid()) { AddError(TEXT("production sentinel failed")); return false; }
		Result = RPGCombatHydration::CompileParticipant(*Broken, Content, FString::ChrN(64, TEXT('b')), Out);
		TestTrue(Case.Name + TEXT(": production rejects before dependency loads, clears old output"), !Result.IsReady() && !Out.IsValid() && HasError(Result, Case.Token, Case.Path));
	}
	auto Defaults = Definition(FRPGHealPunishConfig());
	TestTrue(TEXT("additive defaults compile without substitution"), Compile(*Defaults, Out).IsReady() && Out.IsValid() && Same(Out->HealPunish, FRPGHealPunishConfig()));
	auto Retained = [this, &Compile, &Out](const TCHAR* Label, const TCHAR* Token, const TFunction<void(URPGBossDefinition&)>& Break)
	{
		if (!TestTrue(TEXT("fresh valid sentinel before retained rejection"), Compile(*Definition(RecordA()), Out).IsReady() && Out.IsValid())) { return; }
		auto Broken = Definition(RecordA()); Break(*Broken);
		const FRPGHydrationResult Result = Compile(*Broken, Out);
		TestTrue(Label, !Result.IsReady() && !Out.IsValid() && HasError(Result, Token, TEXT("")));
	};
	Retained(TEXT("existing Bleed validation retained"), TEXT("InvalidBleed.NotPositive"), [](URPGBossDefinition& D) { D.Bleed.InitialThreshold = 0.f; });
	Retained(TEXT("existing stats validation retained"), TEXT("invalid stats"), [](URPGBossDefinition& D) { D.Stats.MaxHealth = -1.f; });
	Retained(TEXT("existing manifest requirement retained"), TEXT("field manifest required"), [](URPGBossDefinition& D) { D.Fields.Reset(); });
	AddInfo(TEXT("Synthetic compiler/copy and early production refusal only; no positive real-asset compile or move-table resolution."));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGHealPunishAuthoringTest, "OneBossFight.Binding.HealPunish.Authoring", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FRPGHealPunishAuthoringTest::RunTest(const FString& Parameters)
{
	using namespace HealPunishTests;
	const UScriptStruct* Struct=FRPGHealPunishConfig::StaticStruct();
	int32 Count=0;for(TFieldIterator<FProperty> It(Struct);It;++It){++Count;TestTrue(TEXT("authored field editable"),It->HasAnyPropertyFlags(CPF_Edit));}
	TestEqual(TEXT("exact14 authored properties"),Count,14);
	for(const TCHAR* N : {TEXT("bEnabled"),TEXT("bRespondToHeal"),TEXT("bCancelJavelinsOnInterrupt")})
	{
		TestNotNull(N,CastField<FBoolProperty>(Struct->FindPropertyByName(N)));
		TestNotNull(FString(N)+TEXT(" native bool"),CastField<FBoolProperty>(URPGBossHealPunish::StaticClass()->FindPropertyByName(N)));
	}
	for(const TCHAR* N : {TEXT("MinRange"),TEXT("MaxRange"),TEXT("Cooldown"),TEXT("Damage"),TEXT("FlightTime"),TEXT("MinSpeed"),TEXT("MaxSpeed"),TEXT("JavelinRadius"),TEXT("JavelinMaxRange"),TEXT("AimHeight")})
	{
		TestNotNull(N,CastField<FFloatProperty>(Struct->FindPropertyByName(N)));
		TestNotNull(FString(N)+TEXT(" native float"),CastField<FFloatProperty>(URPGBossHealPunish::StaticClass()->FindPropertyByName(N)));
	}
	const FArrayProperty* Array=CastField<FArrayProperty>(Struct->FindPropertyByName(TEXT("SpawnSockets")));
	const FArrayProperty* NativeArray=CastField<FArrayProperty>(URPGBossHealPunish::StaticClass()->FindPropertyByName(TEXT("SpawnSockets")));
	TestTrue(TEXT("array of names, both record and native"),Array&&NativeArray&&CastField<FNameProperty>(Array->Inner)&&CastField<FNameProperty>(NativeArray->Inner));
	const FStructProperty* Property=CastField<FStructProperty>(URPGBossDefinition::StaticClass()->FindPropertyByName(TEXT("HealPunish")));
	TestTrue(TEXT("exact editable Data Asset struct"),Property&&Property->Struct==Struct&&Property->HasAnyPropertyFlags(CPF_Edit));
	const FRPGHealPunishConfig Default;
	TestTrue(TEXT("all14 defaults equal native declarations"),Same(Default,Read(*GetDefault<URPGBossHealPunish>())));
	TestTrue(TEXT("explicit default baseline"),Default.bEnabled&&Default.MinRange==400.f&&Default.MaxRange==1000.f&&Default.Cooldown==4.f&&Default.Damage==12.f
		&&Default.FlightTime==1.2f&&Default.MinSpeed==450.f&&Default.MaxSpeed==2500.f&&Default.JavelinRadius==25.f&&Default.JavelinMaxRange==3000.f
		&&Default.SpawnSockets==TArray<FName>{TEXT("JavelinSpawn"),TEXT("hand_l")}&&Default.AimHeight==100.f&&Default.bRespondToHeal&&Default.bCancelJavelinsOnInterrupt);
	auto D=Definition(Default);TestTrue(TEXT("additive default record"),Same(D->HealPunish,Default));
	for(const TCHAR* N : {TEXT("MoveId"),TEXT("DrinkMontage"),TEXT("Flying"),TEXT("bPending"),TEXT("CooldownEnd"),TEXT("PendingSince"),TEXT("SeenGeneration"),TEXT("Released")})
	{TestNull(FString(N)+TEXT(" not an authored field"),Struct->FindPropertyByName(N));}
	AddInfo(TEXT("Reflection/default declarations only. Native A5/drink montage and socket/bone resolution UNRESOLVED; no serialized authoring proof."));
	return true;
}
#endif
