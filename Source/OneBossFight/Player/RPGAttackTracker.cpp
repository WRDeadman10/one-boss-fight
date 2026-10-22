// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGAttackTracker.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossPhases.h"
#include "Player/RPGBossStagger.h"
#include "Pack/RPGBlueprintCall.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "Kismet/GameplayStatics.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGAttack, Log, All);

using namespace RPGPack;

URPGAttackTracker::URPGAttackTracker()
{
	PrimaryComponentTick.bCanEverTick = true;
	// A2, the delayed overhead slam (Freeze 16). Stand-in: the pack boss's rare close attack (GS_ChargedAttack). Measured in PIE (pie_a2_scenarios.py): it has two trace windows, 1.57 to 1.76 s and 1.93 to 2.11 s,
	// and only the second one hurt a player at 140 to 220 cm (health -36 at 2.00 s, three of three; nothing at 260 cm). It behaves as a ground slam with a radius of about 330 cm, not as a directional swing.
	// The heading therefore locks 0.25 s before the damaging window (Freeze 30.2 item 1). The pack clip has no rotation notify, so the boss does not turn during it unless this component turns it.
	FRPGAttackTiming A2;
	A2.MoveId = TEXT("A2");
	A2.MontageName = TEXT("GS_ChargedAttack_Montage");
	A2.CommitTime = 1.68f;
	A2.ActiveStartTime = 1.93f;
	A2.ActiveEndTime = 2.11f;
	A2.RecoveryEndTime = 3.14f; // the ability ends (montage blends out) at 3.14 s of the 3.40 s clip
	A2.TrackTurnRate = 120.f;
	Attacks.Add(A2);

	// Close attacks (A1 and A3), stand-ins from the pack's GS_Attack01 to 04 (DELTA_AUDIT: rotation window 0 to about 0.3 s, trace 0.12 to 0.47 s). The pack chains Attack01 to Attack02 at its follow-up
	// notify (0.54 s) and Attack03 to Attack04 at once (observed in PIE with pie_close_combo_watch.py). Mapping: A1 = Attack03 (single quick slash), A1b = Attack04 (its chained follow-up),
	// A3a and A3b = Attack01 and Attack02 (the two-hit combo). Each stage has its own commitment point. The pack tracks the player only for the first 0.3 s, so the heading locks 0.04 to 0.07 s before the
	// trace opens. These pack clips have a 0.12 to 0.17 s windup against the Freeze's 0.35 to 0.40 s: the readable tell comes with the authored clips (TASKS A-xx), this is the stand-in.
	auto AddClose = [this](const TCHAR* Move, const TCHAR* Montage, float Commit, float ActiveStart, float ActiveEnd, float RecoveryEnd, bool bBranch)
	{
		FRPGAttackTiming T;
		T.MoveId = Move;
		T.MontageName = Montage;
		T.CommitTime = Commit;
		T.ActiveStartTime = ActiveStart;
		T.ActiveEndTime = ActiveEnd;
		T.RecoveryEndTime = RecoveryEnd;
		T.TrackTurnRate = 360.f;
		T.bBranchStage = bBranch;
		Attacks.Add(T);
	};
	AddClose(TEXT("A1"), TEXT("GS_Attack03_Montage"), 0.08f, 0.12f, 0.42f, 1.04f, false);
	AddClose(TEXT("A1b"), TEXT("GS_Attack04_Montage"), 0.12f, 0.16f, 0.46f, 1.25f, true);
	AddClose(TEXT("A3a"), TEXT("GS_Attack01_Montage"), 0.13f, 0.17f, 0.47f, 0.54f, false);
	AddClose(TEXT("A3b"), TEXT("GS_Attack02_Montage"), 0.10f, 0.14f, 0.44f, 1.20f, true);

	// A6, the phase two leap (Freeze 16). Stand-in: the pack's GS_LeapAttack (1.87 s): the pack turns the boss only in 0 to 0.16 s and again in 0.69 to 0.83 s, and its trace (the central hit) runs 0.75 to 1.17 s.
	// The heading locks at 0.16 s (end of the first rotation window) and stays locked through the landing, so the boss does not steer in flight (Freeze 16: no aimbot rotation); the wave component starts at
	// the active window. Recovery 1.87 s is the clip length.
	FRPGAttackTiming A6;
	A6.MoveId = TEXT("A6");
	A6.MontageName = TEXT("GS_LeapAttack_Montage");
	A6.CommitTime = 0.16f;
	A6.ActiveStartTime = 0.75f;
	A6.ActiveEndTime = 1.17f;
	A6.RecoveryEndTime = 1.80f;
	A6.TrackTurnRate = 120.f;
	Attacks.Add(A6);

	// A4, the low sweep (Freeze 16: windup 0.60 s, commitment 0.20 s before the hit, active 0.30 s, recovery 0.85 s). There is no pack clip for it: the boss plays Antigravity's A4 clip (1.767 s, the same total)
	// as a dynamic montage. The hit is not a pack trace but URPGBossLowSweep, so the active window below is the time the blade crosses the floor. The clip's own poses are still under review (BRIEF_08).
	FRPGAttackTiming A4;
	A4.MoveId = TEXT("A4");
	A4.MontageName = TEXT("AN_Boss01_A4_LowSweep");
	A4.ClipPath = TEXT("/Game/OneBossFight/Boss01/Animations/AN_Boss01_A4_LowSweep.AN_Boss01_A4_LowSweep");
	A4.CommitTime = 0.40f;
	A4.ActiveStartTime = 0.60f;
	A4.ActiveEndTime = 0.90f;
	A4.RecoveryEndTime = 1.75f;
	A4.TrackTurnRate = 180.f;
	Attacks.Add(A4);

	// A5, the javelin throw (Freeze 16: telegraph 0.40 s, commitment at the release, then the flight, recovery 0.60 s). Antigravity's A5 clip is 1.0 s. The release happens in the short "active" window below
	// (the heading is locked from 0.45 s, the javelin leaves the hand when the window opens); the flight itself belongs to the projectile (URPGBossHealPunish, ARPGBossJavelin).
	FRPGAttackTiming A5;
	A5.MoveId = TEXT("A5");
	A5.MontageName = TEXT("AN_Boss01_A5_JavelinThrow");
	A5.ClipPath = TEXT("/Game/OneBossFight/Boss01/Animations/AN_Boss01_A5_JavelinThrow.AN_Boss01_A5_JavelinThrow");
	A5.CommitTime = 0.45f;
	A5.ActiveStartTime = 0.45f;
	A5.ActiveEndTime = 0.50f;
	A5.RecoveryEndTime = 0.95f;
	A5.TrackTurnRate = 240.f;
	Attacks.Add(A5);
}

int32 URPGAttackTracker::FindTimingIndex(const UAnimMontage* Montage) const
{
	if (!Montage)
	{
		return INDEX_NONE;
	}
	// A pack montage is found by its own name; a dynamic montage (A4, A5) has a generated name, so it is found by the animation its first segment plays.
	const FString Name = Montage->GetName();
	FString ClipName;
	if (Montage->SlotAnimTracks.Num() > 0 && Montage->SlotAnimTracks[0].AnimTrack.AnimSegments.Num() > 0)
	{
		if (const UAnimSequenceBase* Clip = Montage->SlotAnimTracks[0].AnimTrack.AnimSegments[0].GetAnimReference())
		{
			ClipName = Clip->GetName();
		}
	}
	return Attacks.IndexOfByPredicate([&Name, &ClipName](const FRPGAttackTiming& T) { return T.MontageName == Name || (!T.ClipPath.IsEmpty() && T.MontageName == ClipName); });
}

bool URPGAttackTracker::GetTiming(FName MoveId, FRPGAttackTiming& OutTiming) const
{
	if (const FRPGAttackTiming* Timing = Attacks.FindByPredicate([MoveId](const FRPGAttackTiming& T) { return T.MoveId == MoveId; }))
	{
		OutTiming = *Timing;
		return true;
	}
	return false;
}

bool URPGAttackTracker::IsNeutral() const
{
	const ACharacter* Boss = Cast<ACharacter>(GetOwner());
	const UAnimInstance* Anim = Boss && Boss->GetMesh() ? Boss->GetMesh()->GetAnimInstance() : nullptr;
	if (!Anim || bDead || Phase != EPhase::None || Anim->GetCurrentActiveMontage())
	{
		return false;
	}
	const URPGBossStagger* Stagger = GetOwner()->FindComponentByClass<URPGBossStagger>();
	const URPGBossPhases* Phases = GetOwner()->FindComponentByClass<URPGBossPhases>();
	const URPGBossEncounter* Encounter = GetOwner()->FindComponentByClass<URPGBossEncounter>();
	return !(Stagger && Stagger->IsStaggered()) && !(Phases && Phases->IsInTransition()) && !(Encounter && Encounter->IsDormant());
}

bool URPGAttackTracker::PlayClip(const FRPGAttackTiming& Timing)
{
	const ACharacter* Boss = Cast<ACharacter>(GetOwner());
	UAnimInstance* Anim = Boss && Boss->GetMesh() ? Boss->GetMesh()->GetAnimInstance() : nullptr;
	UAnimSequenceBase* Clip = LoadObject<UAnimSequenceBase>(nullptr, *Timing.ClipPath);
	if (!Anim || !Clip)
	{
		UE_LOG(LogRPGAttack, Warning, TEXT("%s: move %s cannot play: clip '%s' or the anim instance is missing"), *GetOwner()->GetName(), *Timing.MoveId.ToString(), *Timing.ClipPath);
		return false;
	}
	// The slot the pack's own boss montages play in (read from one of them, so the name is not guessed).
	static FName SlotName;
	if (SlotName.IsNone())
	{
		SlotName = TEXT("DefaultSlot");
		const UAnimMontage* Reference = LoadObject<UAnimMontage>(nullptr, TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_Attack01_Montage.GS_Attack01_Montage"));
		if (Reference && Reference->SlotAnimTracks.Num() > 0)
		{
			SlotName = Reference->SlotAnimTracks[0].SlotName;
		}
	}
	return Anim->PlaySlotAnimationAsDynamicMontage(Clip, SlotName, 0.1f, 0.2f, 1.f, 1, -1.f, 0.f) != nullptr;
}

bool URPGAttackTracker::BranchAllowedNow() const
{
	const AActor* Boss = GetOwner();
	const APawn* Player = UGameplayStatics::GetPlayerPawn(this, 0);
	if (!Boss || !Player)
	{
		return false;
	}
	const FVector ToPlayer = (Player->GetActorLocation() - Boss->GetActorLocation()) * FVector(1.f, 1.f, 0.f);
	if (ToPlayer.Size() > BranchRange)
	{
		return false;
	}
	const FVector Forward = (Boss->GetActorForwardVector() * FVector(1.f, 1.f, 0.f)).GetSafeNormal();
	return FVector::DotProduct(Forward, ToPlayer.GetSafeNormal()) >= FMath::Cos(FMath::DegreesToRadians(BranchConeDegrees * 0.5f));
}

bool URPGAttackTracker::PlayMoveMontageForTest(FName MoveId)
{
	const FRPGAttackTiming* Timing = Attacks.FindByPredicate([MoveId](const FRPGAttackTiming& T) { return T.MoveId == MoveId; });
	const ACharacter* Boss = Cast<ACharacter>(GetOwner());
	UAnimInstance* Anim = Boss && Boss->GetMesh() ? Boss->GetMesh()->GetAnimInstance() : nullptr;
	if (!Timing || !Anim)
	{
		return false;
	}
	if (!Timing->ClipPath.IsEmpty())
	{
		return PlayClip(*Timing);
	}
	UAnimMontage* Montage = LoadObject<UAnimMontage>(nullptr, *FString::Printf(TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/%s.%s"), *Timing->MontageName, *Timing->MontageName));
	return Montage && Anim->Montage_Play(Montage) > 0.f;
}

FString URPGAttackTracker::GetPhaseName() const
{
	switch (Phase)
	{
	case EPhase::Windup: return TEXT("Windup");
	case EPhase::Committed: return TEXT("Committed");
	case EPhase::Active: return TEXT("Active");
	case EPhase::Recovery: return TEXT("Recovery");
	default: return TEXT("None");
	}
}

bool URPGAttackTracker::EnterCombat()
{
	return TryActivateByTag(GetOwner(), TEXT("Ability.EnterCombat"), true);
}

bool URPGAttackTracker::StartMove(FName MoveId, bool bForce)
{
	// The pack ability that plays each tracked move, by tag. "Close" is the pack's own close attack pick (Attack01 to 04, chained by the pack): the pack ability sets the attack data the damage trace needs, a bare montage does not hurt.
	static const TMap<FName, const TCHAR*> AbilityByMove = {{TEXT("A2"), TEXT("Ability.Melee.CloseRare")}, {TEXT("Close"), TEXT("Ability.Melee.Close")}, {TEXT("A6"), TEXT("Ability.Melee.LeapAttack")}};
	if (const FRPGAttackTiming* Timing = Attacks.FindByPredicate([MoveId](const FRPGAttackTiming& T) { return T.MoveId == MoveId && !T.ClipPath.IsEmpty(); }))
	{
		// A4 and A5 have no pack ability: play the clip. The tracker's own priority veto still applies to a forced start; an unforced one waits for a neutral boss.
		return (bForce || IsNeutral()) && PlayClip(*Timing);
	}
	const TCHAR* const* Tag = AbilityByMove.Find(MoveId);
	return Tag && TryActivateByTag(GetOwner(), *Tag, bForce);
}

void URPGAttackTracker::End(const TCHAR* Reason, float Position)
{
	const FRPGAttackTiming* Timing = Attacks.IsValidIndex(TimingIndex) ? &Attacks[TimingIndex] : nullptr;
	if (Timing && Position < Timing->RecoveryEndTime - 0.1f)
	{
		++InterruptedCount;
	}
	if (Phase == EPhase::Windup)
	{
		// The pack stopped the move before its commit point: the instance was counted but could never commit (KI-069).
		++EndedBeforeCommitCount;
	}
	UE_LOG(LogRPGAttack, Log, TEXT("%s: attack %s instance %d ended (%s) at %.2f s, phase was %s, yaw drift after commit %.1f deg"), *GetOwner()->GetName(), *CurrentMove.ToString(), AttackInstance, Reason, Position, *GetPhaseName(), MaxYawDrift);
	Phase = EPhase::None;
	TimingIndex = INDEX_NONE;
}

void URPGAttackTracker::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	ACharacter* Boss = Cast<ACharacter>(GetOwner());
	UAnimInstance* Anim = Boss && Boss->GetMesh() ? Boss->GetMesh()->GetAnimInstance() : nullptr;
	if (!bEnabled || !Anim)
	{
		return;
	}
	// Death wins over everything (Freeze 21): a boss at zero health ends its attack instance and the heading lock at once, whatever the pack's death ability does with the montage.
	DeathCheckTimer += DeltaTime;
	if (DeathCheckTimer >= 0.1f)
	{
		DeathCheckTimer = 0.f;
		double Health = 1.0;
		if (ReadAttribute(GetOwner(), TEXT("Attribute.Health"), false, Health))
		{
			bDead = Health <= 0.0;
		}
	}
	if (bDead)
	{
		if (Phase != EPhase::None)
		{
			End(TEXT("boss dead"), LastPosition);
		}
		return;
	}
	const UAnimMontage* Montage = Anim->GetCurrentActiveMontage();
	const int32 Index = FindTimingIndex(Montage);

	if (Phase != EPhase::None && (Index != TimingIndex))
	{
		if (Index != INDEX_NONE && !Attacks[Index].bBranchStage && (Phase == EPhase::Windup || Phase == EPhase::Committed || Phase == EPhase::Active))
		{
			++DoubleLaunches;
			UE_LOG(LogRPGAttack, Warning, TEXT("%s: double launch: %s began while %s was still %s"), *GetOwner()->GetName(), *Attacks[Index].MoveId.ToString(), *CurrentMove.ToString(), *GetPhaseName());
		}
		End(Index == INDEX_NONE ? TEXT("montage stopped") : TEXT("replaced by another attack"), LastPosition);
	}
	if (Index == INDEX_NONE)
	{
		DeniedMontage = nullptr;
		return;
	}
	if (Montage == DeniedMontage)
	{
		return; // a stage the branch check stopped is still blending out
	}
	const FRPGAttackTiming& Timing = Attacks[Index];
	const float Position = Anim->Montage_GetPosition(Montage);
	LastPosition = Position;

	if (Phase == EPhase::None)
	{
		TimingIndex = Index;
		CurrentMove = Timing.MoveId;
		Phase = EPhase::Windup;
		++AttackInstance;
		MaxYawDrift = 0.f;
		if (bVetoIllegalStarts)
		{
			// Freeze 21: stance break, phase transition and dormancy outrank a new attack.
			const URPGBossStagger* Stagger = GetOwner()->FindComponentByClass<URPGBossStagger>();
			const URPGBossPhases* Phases = GetOwner()->FindComponentByClass<URPGBossPhases>();
			const URPGBossEncounter* Encounter = GetOwner()->FindComponentByClass<URPGBossEncounter>();
			const TCHAR* Reason = (Stagger && Stagger->IsStaggered()) ? TEXT("the boss is staggered") : (Phases && Phases->IsInTransition()) ? TEXT("a phase transition is running") : (Encounter && Encounter->IsDormant()) ? TEXT("the boss is dormant") : nullptr;
			if (Reason)
			{
				++IllegalStarts;
				UE_LOG(LogRPGAttack, Log, TEXT("%s: attack %s vetoed: %s, montage stopped"), *GetOwner()->GetName(), *CurrentMove.ToString(), Reason);
				Anim->Montage_Stop(0.05f, Montage);
				DeniedMontage = Montage;
				--AttackInstance;
				Phase = EPhase::None;
				TimingIndex = INDEX_NONE;
				return;
			}
		}
		if (Timing.bBranchStage)
		{
			// Freeze 16 A3: slash 2 only when the player is in the frontal cone and in range at the branch check (the start of this stage). A failed check stops the stage before it can hurt.
			if (BranchAllowedNow())
			{
				++BranchAllowed;
			}
			else
			{
				++BranchDenied;
				UE_LOG(LogRPGAttack, Log, TEXT("%s: attack %s denied by the branch check (range %.0f, cone %.0f deg), montage stopped"), *GetOwner()->GetName(), *CurrentMove.ToString(), BranchRange, BranchConeDegrees);
				Anim->Montage_Stop(0.15f, Montage);
				DeniedMontage = Montage;
				--AttackInstance;
				Phase = EPhase::None;
				TimingIndex = INDEX_NONE;
				return;
			}
		}
		UE_LOG(LogRPGAttack, Log, TEXT("%s: attack %s instance %d begins (generation %d)"), *GetOwner()->GetName(), *CurrentMove.ToString(), AttackInstance, GetOwner()->FindComponentByClass<URPGBossEncounter>() ? GetOwner()->FindComponentByClass<URPGBossEncounter>()->GetGeneration() : 0);
	}

	// Heading: turn towards the player before the commitment point, hold the committed heading until the last active moment.
	if (Phase == EPhase::Windup)
	{
		if (Position >= Timing.CommitTime)
		{
			Phase = EPhase::Committed;
			CommittedYaw = Boss->GetActorRotation().Yaw;
			LastCommitPosition = Position;
			++CommitCount;
			UE_LOG(LogRPGAttack, Log, TEXT("%s: attack %s committed at %.2f s, heading %.1f deg"), *GetOwner()->GetName(), *CurrentMove.ToString(), Position, CommittedYaw);
		}
		else if (Timing.TrackTurnRate > 0.f)
		{
			if (const APawn* Player = UGameplayStatics::GetPlayerPawn(this, 0))
			{
				const FVector ToPlayer = Player->GetActorLocation() - Boss->GetActorLocation();
				const float TargetYaw = FMath::RadiansToDegrees(FMath::Atan2(ToPlayer.Y, ToPlayer.X));
				FRotator Rotation = Boss->GetActorRotation();
				Rotation.Yaw = FMath::FixedTurn(Rotation.Yaw, TargetYaw, Timing.TrackTurnRate * DeltaTime);
				Boss->SetActorRotation(Rotation);
			}
		}
	}
	if (Phase == EPhase::Committed || Phase == EPhase::Active)
	{
		FRotator Rotation = Boss->GetActorRotation();
		MaxYawDrift = FMath::Max(MaxYawDrift, FMath::Abs(FMath::FindDeltaAngleDegrees(CommittedYaw, Rotation.Yaw)));
		Rotation.Yaw = CommittedYaw;
		Boss->SetActorRotation(Rotation);
	}

	if (Position >= Timing.ActiveEndTime && (Phase == EPhase::Committed || Phase == EPhase::Active))
	{
		Phase = EPhase::Recovery;
		UE_LOG(LogRPGAttack, Log, TEXT("%s: attack %s recovery from %.2f s (heading lock released)"), *GetOwner()->GetName(), *CurrentMove.ToString(), Position);
	}
	else if (Position >= Timing.ActiveStartTime && Phase == EPhase::Committed)
	{
		Phase = EPhase::Active;
		LastActiveStartPosition = Position;
		UE_LOG(LogRPGAttack, Log, TEXT("%s: attack %s active window opens at %.2f s"), *GetOwner()->GetName(), *CurrentMove.ToString(), Position);
	}
}
