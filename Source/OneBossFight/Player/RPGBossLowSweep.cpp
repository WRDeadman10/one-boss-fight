// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossLowSweep.h"
#include "Components/CapsuleComponent.h"
#include "DrawDebugHelpers.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "Kismet/GameplayStatics.h"
#include "Pack/RPGBlueprintCall.h"
#include "Player/RPGAttackTracker.h"
#include "Player/RPGBossDamage.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGDamageResolver.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGSweep, Log, All);

using namespace RPGPack;

URPGBossLowSweep::URPGBossLowSweep()
{
	PrimaryComponentTick.bCanEverTick = true;
}

bool URPGBossLowSweep::StartForTest(bool bForce)
{
	URPGAttackTracker* Tracker = GetOwner() ? GetOwner()->FindComponentByClass<URPGAttackTracker>() : nullptr;
	return Tracker && Tracker->StartMove(MoveId, bForce);
}

void URPGBossLowSweep::Begin(float InForwardYaw)
{
	const ACharacter* Boss = Cast<ACharacter>(GetOwner());
	if (!Boss)
	{
		return;
	}
	ForwardYaw = InForwardYaw;
	GroundZ = RPGBossDamage::FeetZ(Boss);
	BladeAngle = SweepFromDegrees;
	PreviousAngle = SweepFromDegrees;
	bActive = true;
	bDamaged = false;
	bJumpCounted = false;
	bInvulnerableCounted = false;
	bBlockedCounted = false;
	++SweepCount;
	const URPGBossEncounter* Encounter = GetOwner()->FindComponentByClass<URPGBossEncounter>();
	SweepGeneration = Encounter ? Encounter->GetGeneration() : 0;
	UE_LOG(LogRPGSweep, Log, TEXT("%s: sweep %d begins, heading %.1f, blade %.0f cm high, reach %.0f cm, from %.0f to %.0f deg"), *GetOwner()->GetName(), SweepCount, ForwardYaw, BladeHeight, Reach, SweepFromDegrees, SweepToDegrees);
}

void URPGBossLowSweep::End(const TCHAR* Reason)
{
	if (bActive)
	{
		UE_LOG(LogRPGSweep, Log, TEXT("%s: sweep ended (%s) at blade angle %.0f deg, damaged %d"), *GetOwner()->GetName(), Reason, BladeAngle, bDamaged ? 1 : 0);
	}
	bActive = false;
}

void URPGBossLowSweep::Test(float FromAngle, float ToAngle)
{
	const ACharacter* Boss = Cast<ACharacter>(GetOwner());
	const ACharacter* Player = Cast<ACharacter>(UGameplayStatics::GetPlayerPawn(this, 0));
	if (!Boss || !Player || bDamaged)
	{
		return;
	}
	const FVector ToPlayer = (Player->GetActorLocation() - Boss->GetActorLocation()) * FVector(1.f, 1.f, 0.f);
	const float Distance = ToPlayer.Size();
	const float Radius = Player->GetCapsuleComponent() ? Player->GetCapsuleComponent()->GetScaledCapsuleRadius() : 34.f;
	if (Distance - Radius > Reach || Distance + Radius < InnerRadius || Distance < KINDA_SMALL_NUMBER)
	{
		return;
	}
	// Angle of the player from the committed forward direction, positive to the boss's right, and how wide the player's capsule looks from the boss.
	const float PlayerYaw = FMath::RadiansToDegrees(FMath::Atan2(ToPlayer.Y, ToPlayer.X));
	const float Angle = FMath::FindDeltaAngleDegrees(ForwardYaw, PlayerYaw);
	const float Tolerance = FMath::RadiansToDegrees(FMath::Asin(FMath::Clamp(Radius / FMath::Max(Distance, 1.f), 0.f, 1.f)));
	const float Low = FMath::Min(FromAngle, ToAngle) - Tolerance;
	const float High = FMath::Max(FromAngle, ToAngle) + Tolerance;
	if (Angle < Low || Angle > High)
	{
		return;
	}

	// The blade touches the player's capsule in the plane: now decide what it does.
	FRPGDamagePayload Payload;
	Payload.MoveId = MoveId;
	Payload.AttackInstance = LastInstance;
	Payload.Generation = SweepGeneration;
	Payload.HPDamage = Damage;
	URPGDamageResolver* Resolver = URPGDamageResolver::FindOrAdd(GetOwner());
	const float FeetHeight = RPGBossDamage::FeetZ(Player) - GroundZ;
	if (FeetHeight >= BladeHeight)
	{
		if (!bJumpCounted)
		{
			bJumpCounted = true;
			++JumpedCount;
			UE_LOG(LogRPGSweep, Log, TEXT("blade passed under the player (feet %.0f cm above the floor, blade %.0f cm)"), FeetHeight, BladeHeight);
			Resolver->NoteMiss(Payload, ERPGDamageOutcome::MissJumped, TEXT("feet above the blade"));
		}
		return;
	}
	// Arena geometry between the boss and the player stops the blade (a low line at floor height, pawns ignored).
	{
		FCollisionQueryParams Params(SCENE_QUERY_STAT(RPGLowSweepLos), false);
		Params.AddIgnoredActor(Boss);
		Params.AddIgnoredActor(Player);
		FHitResult Hit;
		const FVector From(Boss->GetActorLocation().X, Boss->GetActorLocation().Y, GroundZ + 20.f);
		const FVector To(Player->GetActorLocation().X, Player->GetActorLocation().Y, GroundZ + 20.f);
		if (GetWorld()->LineTraceSingleByObjectType(Hit, From, To, RPGBossDamage::WorldBlockers(), Params))
		{
			if (!bBlockedCounted)
			{
				bBlockedCounted = true;
				++BlockedCount;
				UE_LOG(LogRPGSweep, Log, TEXT("blade blocked by %s"), *GetNameSafe(Hit.GetActor()));
				Resolver->NoteMiss(Payload, ERPGDamageOutcome::MissWorld, *GetNameSafe(Hit.GetActor()));
			}
			return;
		}
	}
	// The blade really touches the player: the resolver decides (invulnerability at this moment, dead, stale, duplicate) and applies the health once.
	Resolver->NoteOverlap(Payload);
	const FRPGDamageResult Result = Resolver->Resolve(const_cast<ACharacter*>(Player), Payload);
	switch (Result.Outcome)
	{
	case ERPGDamageOutcome::Accepted:
		bDamaged = true;
		++HitCount;
		UE_LOG(LogRPGSweep, Log, TEXT("blade hit the player at %.0f cm, angle %.0f deg, feet %.0f cm above the floor: health %.0f -> %.0f"), Distance, Angle, FeetHeight, Result.HealthBefore, Result.HealthAfter);
		break;
	case ERPGDamageOutcome::RejectedInvulnerable:
		if (!bInvulnerableCounted)
		{
			bInvulnerableCounted = true;
			++InvulnerableCount;
			UE_LOG(LogRPGSweep, Log, TEXT("blade ignored: player invulnerable (dodge i-frames) at blade angle %.0f"), BladeAngle);
		}
		break; // the blade can still catch the player if the i-frames end while it is touching
	default:
		break; // dead player, stale generation: nothing happens, no hit is counted
	}
}

void URPGBossLowSweep::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	AActor* Boss = GetOwner();
	if (!bEnabled || !Boss)
	{
		return;
	}
	DeathCheck += DeltaTime;
	if (DeathCheck >= 0.1f)
	{
		DeathCheck = 0.f;
		double Health = 1.0;
		if (ReadAttribute(Boss, TEXT("Attribute.Health"), false, Health))
		{
			bDead = Health <= 0.0;
		}
	}
	const URPGBossEncounter* Encounter = Boss->FindComponentByClass<URPGBossEncounter>();
	if (bActive && (bDead || (Encounter && Encounter->GetGeneration() != SweepGeneration)))
	{
		End(bDead ? TEXT("boss dead") : TEXT("encounter reset"));
	}
	const URPGAttackTracker* Tracker = Boss->FindComponentByClass<URPGAttackTracker>();
	if (!Tracker)
	{
		return;
	}
	const bool bTrackerActive = !bDead && Tracker->GetCurrentMove() == MoveId && Tracker->IsActiveWindow();
	if (!bActive && bTrackerActive && Tracker->GetAttackInstance() != LastInstance)
	{
		LastInstance = Tracker->GetAttackInstance();
		Begin(Tracker->GetCommittedYaw());
	}
	if (!bActive)
	{
		return;
	}
	if (bTrackerActive)
	{
		FRPGAttackTiming Timing;
		if (Tracker->GetTiming(MoveId, Timing) && Timing.ActiveEndTime > Timing.ActiveStartTime)
		{
			const float Progress = FMath::Clamp((Tracker->GetPosition() - Timing.ActiveStartTime) / (Timing.ActiveEndTime - Timing.ActiveStartTime), 0.f, 1.f);
			BladeAngle = FMath::Lerp(SweepFromDegrees, SweepToDegrees, Progress);
		}
		Test(PreviousAngle, BladeAngle);
		PreviousAngle = BladeAngle;
#if !UE_BUILD_SHIPPING
		const FVector Origin(Boss->GetActorLocation().X, Boss->GetActorLocation().Y, GroundZ + 6.f);
		const FVector Direction = FRotator(0.f, ForwardYaw + BladeAngle, 0.f).Vector();
		DrawDebugLine(GetWorld(), Origin + Direction * InnerRadius, Origin + Direction * Reach, FColor(255, 60, 40), false, -1.f, 0, 6.f);
#endif
	}
	else
	{
		// The tracker's window closed (the move ended, was interrupted, or the montage left the active part): finish the arc to its end if it was cut short only by the window closing normally,
		// then stop. An interrupt (stagger, death, reset) leaves the blade where it was and ends it.
		const bool bNormalEnd = Tracker->GetCurrentMove() == MoveId && Tracker->GetPhaseName() == TEXT("Recovery");
		if (bNormalEnd)
		{
			BladeAngle = SweepToDegrees;
			Test(PreviousAngle, BladeAngle);
		}
		End(bNormalEnd ? TEXT("arc complete") : TEXT("move interrupted"));
	}
}
