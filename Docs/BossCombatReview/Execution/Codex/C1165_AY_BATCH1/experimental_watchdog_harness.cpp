// Copyright One Boss Fight. All Rights Reserved.
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Boss/RPGFrameworkBossCharacter.h"
#include "Boss/RPGFrameworkMoveExecutor.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "HAL/IConsoleManager.h"
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
	// Exercise the runtime watchdog in this engine-backed world. Pausing the active montage
	// models the dropped-end/stuck-playback condition without relying on animation completion.
	UAnimInstance* Anim = Boss->GetMesh()->GetAnimInstance();
	UAnimMontage* ActiveMontage = Anim ? Anim->GetCurrentActiveMontage() : nullptr;
	if (!TestNotNull(TEXT("started card exposes its active montage to the watchdog fixture"), ActiveMontage)) return false;
	IConsoleVariable* SuppressMontageEnd = IConsoleManager::Get().FindConsoleVariable(TEXT("rpg.BossProofSuppressMontageEnd"));
	if (!TestNotNull(TEXT("development watchdog end-suppression hook is registered"), SuppressMontageEnd)) return false;
	const int32 PreviousSuppressValue = SuppressMontageEnd->GetInt();
	SuppressMontageEnd->Set(1, ECVF_SetByCode);
	const double WatchdogSeconds = RPGBossTrack::WatchdogTimeoutSeconds(AcceptedCard->Spec().RecoveryEndSeconds, AcceptedCard->Spec().PlayRate)
		+ double(AcceptedCard->Spec().HoldMaxSeconds);
	const int32 MaxTicks = FMath::CeilToInt((WatchdogSeconds + 1.0) / 0.05);
	const double TimeBeforeWatchdogTicks = Scope.World->GetTimeSeconds();
	for (int32 Index = 0; Index < MaxTicks && !Executor->WatchdogFired(); ++Index)
	{
		Scope.World->Tick(LEVELTICK_All, 0.05f);
		Executor->TickComponent(0.05f, LEVELTICK_All, &Executor->PrimaryComponentTick);
	}
	SuppressMontageEnd->Set(PreviousSuppressValue, ECVF_SetByCode);
	TestTrue(TEXT("transient world ticks advance game time"), Scope.World->GetTimeSeconds() > TimeBeforeWatchdogTicks);
	TestTrue(TEXT("world ticks advance the production watchdog past its bounded timeout"), Executor->WatchdogFired());
	TestTrue(TEXT("watchdog abort leaves executor idle"), Executor->IsIdle());
	TestTrue(TEXT("watchdog abort releases the active card"), Executor->ActiveCard()==nullptr);
	Boss->Destroy();
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossParryRecoveryLifecycleHarness,
	"OneBossFight.Framework.ParryRecovery.StanceBreakPendingState",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FBossParryRecoveryLifecycleHarness::RunTest(const FString&)
{
	FExecutorHarnessWorld Scope;
	if (!TestNotNull(TEXT("engine-backed transient world is available"), Scope.World)) return false;
	TStrongObjectPtr<URPGBossFrameworkProfile> Profile(LoadObject<URPGBossFrameworkProfile>(nullptr,
		TEXT("/Game/OneBossFight/FrameworkProof/DA_Sevarog_SelectorProof_F5.DA_Sevarog_SelectorProof_F5")));
	if (!TestNotNull(TEXT("authored F5 hittable posture profile is available"), Profile.Get())) return false;
	TStrongObjectPtr<URPGBossFrameworkProfile> TestProfile(DuplicateObject<URPGBossFrameworkProfile>(Profile.Get(), GetTransientPackage()));
	if (!TestNotNull(TEXT("transient posture profile copy is available"), TestProfile.Get())) return false;
	// Keep the cloned authored profile's posture tuple internally complete and make it hittable.
	// ValidateProfile requires an F5 boss health/damage pair plus all five posture values in range.
	TestProfile->BossMaxHealth=100.f; TestProfile->PlayerHitDamage=10.f;
	TestProfile->PostureMax=1.f; TestProfile->PlayerPostureHitAmount=1.f; TestProfile->StaggerSeconds=1.f;
	TestProfile->PostureRegenDelaySeconds=0.f; TestProfile->PostureRegenPerSecond=0.f;
	TestProfile->ParryPostureAmount=1.f;
	TUniquePtr<FRPGFrameworkDependencies> Dependencies;
	FString Error;
	if (!RPGFramework::ResolveProfile(TestProfile.Get(), Dependencies, Error))
	{
		AddError(FString::Printf(TEXT("parry recovery fixture dependency setup failed: %s"), *Error));
		return false;
	}
	ARPGFrameworkBossCharacter* Boss = Scope.World->SpawnActor<ARPGFrameworkBossCharacter>(FVector(0, 0, 300), FRotator::ZeroRotator);
	APawn* Target = Scope.World->SpawnActor<APawn>(FVector(300, 0, 300), FRotator::ZeroRotator);
	if (!TestNotNull(TEXT("boss actor setup succeeds"), Boss) || !TestNotNull(TEXT("explicit target setup succeeds"), Target)) return false;
	Scope.World->BeginPlay();
	Boss->GetMesh()->SetSkeletalMesh(Dependencies->Mesh.Get());
	Boss->GetMesh()->SetAnimInstanceClass(Dependencies->AnimClass.Get());
	Boss->GetMesh()->InitAnim(true);
	Boss->Dependencies = MoveTemp(Dependencies);
	Boss->Target = Target;
	Boss->bInitialized = true; Boss->bHittable=true; Boss->Health=Boss->MaxHealth=100.; Boss->Posture=1.;
	Boss->GenerationId = 7;
	Boss->bArrived = true; // Keep this lifecycle fixture independent of map navigation.
	if (Boss->Dependencies->StaggerStart.IsValid()) Boss->Dependencies->StaggerStart.Reset();
	for (auto& Candidate : Boss->Dependencies->Candidates) Candidate.bHyperArmor=false;
	URPGFrameworkMoveExecutor* Executor = Boss->FindComponentByClass<URPGFrameworkMoveExecutor>();
	if (!TestNotNull(TEXT("boss owns the production executor component"), Executor)) return false;
	if (!Executor->Initialize(Boss, *Boss->Dependencies, Target, 41, 7, Error))
	{
		AddError(FString::Printf(TEXT("parry recovery executor setup failed: %s"), *Error));
		return false;
	}
	FRPGBossDecisionSnapshot Snapshot;
	Snapshot.EncounterId=41; Snapshot.Generation=7; Snapshot.TargetId=1; Snapshot.FrameId=1;
	Snapshot.PhaseId=Boss->Dependencies->FirstCard()->Spec().PhaseId; Snapshot.ClockSeconds=0.;
	Snapshot.RangeCm=(Boss->Dependencies->FirstCard()->Spec().MinRangeCm+Boss->Dependencies->FirstCard()->Spec().MaxRangeCm)*.5;
	Snapshot.bTargetValid=true; Snapshot.bNeutral=true;
	if (!Executor->StartCard(Boss->Dependencies->FirstCard(), Snapshot, Error))
	{
		AddError(FString::Printf(TEXT("parried attack start failed: %s"), *Error));
		return false;
	}
	Boss->bStartedMove=true;
	Boss->NoteParried(1., 1.25, 2);
	TestEqual(TEXT("parry initially queues its grade recovery"), Boss->PendingParryRecoverySeconds, 1.25);

	// Apply the queued reaction through the production posture-damage path while the parried move is active.
	Boss->bParryReactionPending=false;
	Boss->PendingParryReactionScale=0.;
	Boss->ApplyHit(0., Boss->Dependencies->Profile->ParryPostureAmount, 0.);
	TestTrue(TEXT("parry posture reaction causes a posture break"), Boss->bStaggered);
	TestTrue(TEXT("posture break aborts the active move"), Executor->IsIdle());
	TestEqual(TEXT("pending recovery remains queued at the break boundary"), Boss->PendingParryRecoverySeconds, 1.25);
	TestEqual(TEXT("pending recovery grade remains queued at the break boundary"), Boss->PendingParryRecoveryGrade, 2);
	Boss->EndStagger();
	TestFalse(TEXT("stagger ends after executor recovery"), Boss->bStaggered);
	TestFalse(TEXT("aborted move is not left marked as started"), Boss->bStartedMove);
	TestEqual(TEXT("deferred recovery remains pending after the aborted move is rearmed"), Boss->PendingParryRecoverySeconds, 1.25);
	TestEqual(TEXT("the aborted move did not consume the deferred recovery deadline"), Boss->ParryRecoveryUntil, 0.);
	Boss->Destroy();
	return true;
}

#endif
