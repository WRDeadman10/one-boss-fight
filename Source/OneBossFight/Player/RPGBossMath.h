// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

/**
 * The deterministic geometry and timing rules of the boss (Freeze 17.2 posture regeneration, 18 riposte geometry, B09 low sweep), in one place so the components and the automation tests share them (G2-16).
 * Header only, no Unreal object is touched, so each rule can be tested without a world.
 */
namespace RPGBossMath
{
	/** Posture after one regeneration tick (Freeze 17.2): nothing at the maximum, nothing until Delay seconds after the last drain (LastDrainTime < 0: never drained), else PerSecond * Dt, never above Max.
	 *  A pool at zero stays there unless bFromZero: the caller says that nothing holds it (a stance break holds the pool at zero itself; a request for a break that was dropped does not hold it and must not leave the pool stuck). */
	inline float RegenStep(float Posture, float Max, double WorldTime, double LastDrainTime, float Delay, float PerSecond, float Dt, bool bFromZero = false)
	{
		if ((Posture <= 0.f && !bFromZero) || Posture >= Max)
		{
			return Posture;
		}
		if (LastDrainTime >= 0.0 && WorldTime - LastDrainTime < Delay)
		{
			return Posture;
		}
		return FMath::Min(Max, Posture + PerSecond * Dt);
	}

	/** Why a riposte press is refused, in the order the checks are made. */
	enum class ERiposteVerdict : uint8 { Accept, TooFar, NotInFront, NotFacing };

	/**
	 * The riposte geometry in the floor plane (height is ignored): the player is within Range (equal is in), inside the boss's front cone of ConeDegrees (full angle), and the player faces the boss within FacingDegrees (full angle).
	 * The forward vectors need not be normalised or flat.
	 */
	inline ERiposteVerdict RiposteGeometry(const FVector& BossLocation, const FVector& BossForward, const FVector& PlayerLocation, const FVector& PlayerForward, float Range, float ConeDegrees, float FacingDegrees)
	{
		const FVector ToPlayer = (PlayerLocation - BossLocation) * FVector(1.f, 1.f, 0.f);
		if (ToPlayer.Size() > Range)
		{
			return ERiposteVerdict::TooFar;
		}
		const FVector Direction = ToPlayer.GetSafeNormal();
		const FVector BossFlat = (BossForward * FVector(1.f, 1.f, 0.f)).GetSafeNormal();
		if (FVector::DotProduct(BossFlat, Direction) < FMath::Cos(FMath::DegreesToRadians(ConeDegrees * 0.5f)))
		{
			return ERiposteVerdict::NotInFront;
		}
		const FVector PlayerFlat = (PlayerForward * FVector(1.f, 1.f, 0.f)).GetSafeNormal();
		if (FVector::DotProduct(PlayerFlat, -Direction) < FMath::Cos(FMath::DegreesToRadians(FacingDegrees * 0.5f)))
		{
			return ERiposteVerdict::NotFacing;
		}
		return ERiposteVerdict::Accept;
	}

	/** The text the riposte check returns for a verdict (nullptr: accepted); the drivers read these. */
	inline const TCHAR* RiposteReason(ERiposteVerdict Verdict)
	{
		switch (Verdict)
		{
		case ERiposteVerdict::TooFar: return TEXT("too far");
		case ERiposteVerdict::NotInFront: return TEXT("not in front of the boss");
		case ERiposteVerdict::NotFacing: return TEXT("player not facing the boss");
		default: return nullptr;
		}
	}

	/**
	 * Does the low sweep blade, moving from FromAngle to ToAngle (degrees, in the order it moved), touch a player capsule of PlayerRadius at Distance (floor plane) and PlayerAngle (degrees from the committed heading)?
	 * Radial test: the capsule overlaps the ring between InnerRadius and Reach. Angular test: the blade's arc widened by how wide the capsule looks from the boss (asin(Radius / Distance)).
	 */
	inline bool SweepTouches(float Distance, float PlayerRadius, float Reach, float InnerRadius, float PlayerAngle, float FromAngle, float ToAngle)
	{
		if (Distance - PlayerRadius > Reach || Distance + PlayerRadius < InnerRadius || Distance < KINDA_SMALL_NUMBER)
		{
			return false;
		}
		const float Tolerance = FMath::RadiansToDegrees(FMath::Asin(FMath::Clamp(PlayerRadius / FMath::Max(Distance, 1.f), 0.f, 1.f)));
		return PlayerAngle >= FMath::Min(FromAngle, ToAngle) - Tolerance && PlayerAngle <= FMath::Max(FromAngle, ToAngle) + Tolerance;
	}
}
