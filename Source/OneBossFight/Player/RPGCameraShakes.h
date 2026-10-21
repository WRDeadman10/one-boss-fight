// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Camera/CameraShakeBase.h"
#include "RPGCameraShakes.generated.h"

class UCameraShakeBase;

/**
 * The numbers of one camera shake (Freeze tenet 4: values are properties, never literals inside logic). They are written into the shake's wave oscillator pattern every time the shake plays,
 * so a change in the editor needs no rebuild. Location values are in cm, rotation values in degrees, frequencies in Hz.
 */
USTRUCT(BlueprintType)
struct ONEBOSSFIGHT_API FRPGShakeSettings
{
	GENERATED_BODY()

	/** Seconds the shake lasts, including its blends. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Shake", meta = (ClampMin = "0.05"))
	float Duration = 0.55f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Shake", meta = (ClampMin = "0"))
	float BlendIn = 0.02f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Shake", meta = (ClampMin = "0"))
	float BlendOut = 0.45f;

	/** Location amplitude on X, Y, Z (cm). Keep it far under the camera spring arm's probe (34 cm): a shake is applied after the arm has resolved the view. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Shake")
	FVector LocationAmplitude = FVector(0.0, 2.0, 5.0);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Shake")
	FVector LocationFrequency = FVector(0.0, 11.0, 14.0);

	/** Rotation amplitude (degrees): pitch, yaw, roll. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Shake")
	FRotator RotationAmplitude = FRotator(1.4, 0.6, 0.8);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Shake")
	FRotator RotationFrequency = FRotator(16.0, 12.0, 9.0);

	/** Full strength inside this distance from the epicentre to the camera (cm). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Falloff", meta = (ClampMin = "0"))
	float InnerRadius = 500.f;

	/** No shake at all beyond this distance (cm). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Falloff", meta = (ClampMin = "0"))
	float OuterRadius = 2500.f;

	/** Exponent of the radial curve between the two radii (1 linear, 2 faster fall off). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Falloff", meta = (ClampMin = "0.1"))
	float Falloff = 1.5f;
};

/** The thump of a heavy slam (A2 overhead, A6 landing): instant onset, linear decay. A single instance: a second slam restarts it, shakes never stack. */
UCLASS()
class ONEBOSSFIGHT_API URPGSlamCameraShake : public UCameraShakeBase
{
	GENERATED_BODY()

public:
	URPGSlamCameraShake(const FObjectInitializer& ObjInit);
};

/** The rumble of the phase two roar: it swells and ends with the roar. */
UCLASS()
class ONEBOSSFIGHT_API URPGRoarCameraShake : public UCameraShakeBase
{
	GENERATED_BODY()

public:
	URPGRoarCameraShake(const FObjectInitializer& ObjInit);
};

namespace RPGLegend
{
	/**
	 * The same radial scale the engine uses for world camera shakes (APlayerCameraManager::CalcRadialShakeScale is protected, so it is repeated here as a pure function):
	 * 1 inside Inner, 0 beyond Outer, (1 - t) ^ Falloff between. Outer <= Inner is a cliff: 1 inside Inner, else 0.
	 */
	ONEBOSSFIGHT_API float ShakeScale(float Distance, float Inner, float Outer, float Falloff);

	/** Writes the settings into the wave oscillator root pattern of a shake of one of the classes above. Returns false when the shake has another pattern. */
	ONEBOSSFIGHT_API bool ApplyShakeSettings(UCameraShakeBase* Shake, const FRPGShakeSettings& Settings);
}
