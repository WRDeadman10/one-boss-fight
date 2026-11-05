// Copyright One Boss Fight. All Rights Reserved.
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Boss/RPGFrameworkBossCharacter.h"
#include "Boss/RPGFrameworkMoveExecutor.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "Player/RPGBossFrameworkProfile.h"
#include "UObject/StrongObjectPtr.h"

namespace
{
struct FExecutorHarnessWorld
{
	UWorld* World = nullptr;
	FExecutorHarnessWorld()
	{
		if (!GEngine) return;
		World = UWorld::CreateWorld(EWorldType::Game, false);
		if (World)
		{
			FWorldContext& Context = GEngine->CreateNewWorldContext(EWorldType::Game);
			Context.SetCurrentWorld(World);
			World->InitializeActorsForPlay(FURL());
		}
	}
	~FExecutorHarnessWorld()
	{
		if (World)
		{
			GEngine->DestroyWorldContext(World);
			World->DestroyWorld(false);
		}
	}
	FExecutorHarnessWorld(const FExecutorHarnessWorld&) = delete;
	FExecutorHarnessWorld& operator=(const FExecutorHarnessWorld&) = delete;
};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossExecutorLifecycleHarness,
	"OneBossFight.Framework.Executor.StatefulLifecycleHarness",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FBossExecutorLifecycleHarness::RunTest(const FString&)
{
	FExecutorHarnessWorld Scope;
	if (!TestNotNull(TEXT("engine-backed transient world is available"), Scope.World)) return false;
	TStrongObjectPtr<URPGBossFrameworkProfile> Profile(LoadObject<URPGBossFrameworkProfile>(nullptr,
		TEXT("/Game/OneBossFight/FrameworkProof/DA_Sevarog_SwingProof.DA_Sevarog_SwingProof")));
	if (!TestNotNull(TEXT("authored executor profile is available"), Profile.Get())) return false;
	TUniquePtr<FRPGFrameworkDependencies> Dependencies;
	FString Error;
	if (!RPGFramework::ResolveProfile(Profile.Get(), Dependencies, Error))
	{
		AddError(FString::Printf(TEXT("executor harness dependency setup failed: %s"), *Error));
		return false;
	}
	// UE 5.5 has no SpawnActor<T>(FTransform) overload; use the location + rotation form.
	ARPGFrameworkBossCharacter* Boss = Scope.World->SpawnActor<ARPGFrameworkBossCharacter>(FVector(0, 0, 300), FRotator::ZeroRotator);
	APawn* Target = Scope.World->SpawnActor<APawn>(FVector(300, 0, 300), FRotator::ZeroRotator);
	if (!TestNotNull(TEXT("boss actor setup succeeds"), Boss) || !TestNotNull(TEXT("explicit player target setup succeeds"), Target)) return false;
	Scope.World->BeginPlay();
	Boss->GetMesh()->SetSkeletalMesh(Dependencies->Mesh.Get());
	Boss->GetMesh()->SetAnimInstanceClass(Dependencies->AnimClass.Get());
	Boss->GetMesh()->InitAnim(true);
	URPGFrameworkMoveExecutor* Executor = Boss->FindComponentByClass<URPGFrameworkMoveExecutor>();
	if (!TestNotNull(TEXT("boss owns the production executor component"), Executor)) return false;
	if (!Executor->Initialize(Boss, *Dependencies, Target, 41, 7, Error))
	{
		AddError(FString::Printf(TEXT("executor initialization/setup failed: %s"), *Error));
		return false;
	}
	TestFalse(TEXT("recovery before an abort is refused"), Executor->RecoverAfterAbort());
	TestTrue(TEXT("pre-abort recovery refusal preserves idle state"), Executor->IsIdle());
	FRPGBossDecisionSnapshot Snapshot;
	Snapshot.EncounterId=41; Snapshot.Generation=7; Snapshot.TargetId=1; Snapshot.FrameId=1;
	Snapshot.PhaseId=Dependencies->FirstCard()->Spec().PhaseId; Snapshot.ClockSeconds=0.;
	Snapshot.RangeCm=(Dependencies->FirstCard()->Spec().MinRangeCm+Dependencies->FirstCard()->Spec().MaxRangeCm)*.5;
	Snapshot.bTargetValid=true; Snapshot.bNeutral=true;
	if (!Executor->StartCard(Dependencies->FirstCard(), Snapshot, Error))
	{
		AddError(FString::Printf(TEXT("authored card start/setup failed: %s"), *Error));
		return false;
	}
	const TSharedPtr<const FRPGCompiledBossMoveCard> AcceptedCard=Dependencies->FirstCard();
	const FRPGBossAttackToken FirstToken=Executor->Model().ActiveToken();
	FRPGBossMoveCardSpec AlternateSpec=AcceptedCard->Spec();
	AlternateSpec.MoveId=TEXT("ExecutorHarnessAlternate");
	TSharedPtr<const FRPGCompiledBossMoveCard> AlternatePreview;
	if (!RPGBossMoveCards::CompileMetadata(AlternateSpec, AcceptedCard->Metadata(), AlternatePreview).IsValid() || !AlternatePreview)
	{
		AddError(TEXT("alternate-card refusal fixture setup failed"));
		return false;
	}
	Error.Reset();
	TestFalse(TEXT("D8 refuses replacement while active"), Executor->StartCard(AlternatePreview, Snapshot, Error));
	TestEqual(TEXT("D8 refusal token"), Error, FString(TEXT("Framework.Playback.State")));
	TestTrue(TEXT("D8 keeps the accepted card active"), Executor->ActiveCard()==AcceptedCard.Get());
	TestTrue(TEXT("D8 retains the accepted token"), Executor->Model().AcceptsCallback(FirstToken));
	Executor->Abort(TEXT("D13 harness abort"));
	TestTrue(TEXT("abort leaves model and owned montage idle"), Executor->IsIdle());
	TestTrue(TEXT("abort releases active card"), Executor->ActiveCard()==nullptr);
	TestTrue(TEXT("same-generation recovery succeeds"), Executor->RecoverAfterAbort());
	TestTrue(TEXT("recovery leaves no active card and stays idle"), Executor->IsIdle()&&Executor->ActiveCard()==nullptr);
	TestFalse(TEXT("recovery consumes the abort marker only once"), Executor->RecoverAfterAbort());
	TestTrue(TEXT("repeated recovery refusal preserves idle state and no active card"), Executor->IsIdle()&&Executor->ActiveCard()==nullptr);
	Snapshot.FrameId=2; Snapshot.ClockSeconds=1.; Error.Reset();
	if (!Executor->Start(Snapshot, Error))
	{
		AddError(FString::Printf(TEXT("retry through the accepted-card Start path failed: %s"), *Error));
		return false;
	}
	const FRPGBossAttackToken SecondToken=Executor->Model().ActiveToken();
	TestTrue(TEXT("same-generation retry receives a newer instance token"), SecondToken.InstanceId>FirstToken.InstanceId);
	TestTrue(TEXT("D8 convenience Start reuses the accepted card"), Executor->ActiveCard()==AcceptedCard.Get());
	// The executor exposes only a const model view, so stale-token refusal is checked through the const callback gate.
	TestFalse(TEXT("stale token is refused by the callback gate"), Executor->Model().AcceptsCallback(FirstToken));
	TestTrue(TEXT("stale callback leaves current token accepted"), Executor->Model().AcceptsCallback(SecondToken));
	TestTrue(TEXT("stale callback leaves the current card active"), Executor->ActiveCard()==AcceptedCard.Get());
	Error.Reset();
	TestFalse(TEXT("equal-generation refusal leaves executor non-idle"), Executor->IsIdle());
	TestFalse(TEXT("D9 rejects equal-generation rearm"), Executor->Rearm(7, Error));
	TestEqual(TEXT("equal-generation refusal token"), Error, FString(TEXT("MoveModel.Generation")));
	TestTrue(TEXT("equal-generation refusal preserves active card identity"), Executor->ActiveCard()==AcceptedCard.Get());
	TestFalse(TEXT("D9 rejects older-generation rearm"), Executor->Rearm(6, Error));
	TestEqual(TEXT("older-generation refusal token"), Error, FString(TEXT("MoveModel.Generation")));
	TestFalse(TEXT("older-generation refusal leaves executor non-idle"), Executor->IsIdle());
	TestTrue(TEXT("rejected rearm preserves active token"), Executor->Model().AcceptsCallback(SecondToken));
	TestTrue(TEXT("older-generation refusal preserves active card identity"), Executor->ActiveCard()==AcceptedCard.Get());
	Error.Reset();
	TestTrue(TEXT("D9 accepts newer-generation rearm"), Executor->Rearm(8, Error));
	TestTrue(TEXT("new-generation rearm leaves executor idle"), Executor->IsIdle());
	TestTrue(TEXT("new-generation rearm clears active card"), Executor->ActiveCard()==nullptr);
	TestFalse(TEXT("new-generation rearm rejects prior token"), Executor->Model().AcceptsCallback(SecondToken));
	Snapshot.Generation=8; Snapshot.FrameId=3; Snapshot.ClockSeconds=2.; Error.Reset();
	if (!Executor->Start(Snapshot, Error))
	{
		AddError(FString::Printf(TEXT("repeated-abort card start/setup failed: %s"), *Error));
		return false;
	}
	// BUILD-185 did not observe WatchdogFired() in this transient-world fixture. TickComponent is the watchdog observer;
	// keep the harness source-only here and leave watchdog execution to a fixture whose component/world tick is verified.
	Executor->Abort(TEXT("repeated cleanup after recovery"));
	Executor->Abort(TEXT("idempotence check"));
	TestTrue(TEXT("repeated abort remains idle"), Executor->IsIdle());
	TestTrue(TEXT("repeated abort leaves no active card"), Executor->ActiveCard()==nullptr);
	Boss->Destroy();
	return true;
}

#endif
