// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGCameraShakes.h"
#include "Shakes/WaveOscillatorCameraShakePattern.h"

URPGSlamCameraShake::URPGSlamCameraShake(const FObjectInitializer& ObjInit)
	: Super(ObjInit.SetDefaultSubobjectClass<UWaveOscillatorCameraShakePattern>(TEXT("RootShakePattern")))
{
	bSingleInstance = true;
}

URPGRoarCameraShake::URPGRoarCameraShake(const FObjectInitializer& ObjInit)
	: Super(ObjInit.SetDefaultSubobjectClass<UWaveOscillatorCameraShakePattern>(TEXT("RootShakePattern")))
{
	bSingleInstance = true;
}

float RPGLegend::ShakeScale(float Distance, float Inner, float Outer, float Falloff)
{
	Distance = FMath::Max(Distance, 0.f);
	if (Outer <= Inner)
	{
		return Distance <= Inner ? 1.f : 0.f;
	}
	const float T = FMath::Clamp((Distance - Inner) / (Outer - Inner), 0.f, 1.f);
	return FMath::Pow(1.f - T, FMath::Max(Falloff, 0.01f));
}

bool RPGLegend::ApplyShakeSettings(UCameraShakeBase* Shake, const FRPGShakeSettings& Settings)
{
	UWaveOscillatorCameraShakePattern* Pattern = Shake ? Cast<UWaveOscillatorCameraShakePattern>(Shake->GetRootShakePattern()) : nullptr;
	if (!Pattern)
	{
		return false;
	}
	Pattern->Duration = Settings.Duration;
	Pattern->BlendInTime = Settings.BlendIn;
	Pattern->BlendOutTime = Settings.BlendOut;
	Pattern->LocationAmplitudeMultiplier = 1.f;
	Pattern->LocationFrequencyMultiplier = 1.f;
	Pattern->RotationAmplitudeMultiplier = 1.f;
	Pattern->RotationFrequencyMultiplier = 1.f;
	Pattern->X.Amplitude = static_cast<float>(Settings.LocationAmplitude.X);
	Pattern->Y.Amplitude = static_cast<float>(Settings.LocationAmplitude.Y);
	Pattern->Z.Amplitude = static_cast<float>(Settings.LocationAmplitude.Z);
	Pattern->X.Frequency = static_cast<float>(Settings.LocationFrequency.X);
	Pattern->Y.Frequency = static_cast<float>(Settings.LocationFrequency.Y);
	Pattern->Z.Frequency = static_cast<float>(Settings.LocationFrequency.Z);
	Pattern->Pitch.Amplitude = static_cast<float>(Settings.RotationAmplitude.Pitch);
	Pattern->Yaw.Amplitude = static_cast<float>(Settings.RotationAmplitude.Yaw);
	Pattern->Roll.Amplitude = static_cast<float>(Settings.RotationAmplitude.Roll);
	Pattern->Pitch.Frequency = static_cast<float>(Settings.RotationFrequency.Pitch);
	Pattern->Yaw.Frequency = static_cast<float>(Settings.RotationFrequency.Yaw);
	Pattern->Roll.Frequency = static_cast<float>(Settings.RotationFrequency.Roll);
	Pattern->FOV.Amplitude = 0.f; // no field of view change: a shake is never a zoom
	return true;
}
