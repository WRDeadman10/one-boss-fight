// Copyright One Boss Fight. All Rights Reserved.

#include "Combat/RPGInputTestUtils.h"
#include "EnhancedInputSubsystems.h"
#include "GameFramework/PlayerController.h"
#include "Engine/LocalPlayer.h"
#include "InputAction.h"
#include "InputCoreTypes.h"
#include "Engine/Engine.h"
#include "HAL/IConsoleManager.h"

namespace
{
#if !UE_BUILD_SHIPPING
	bool bFixedActive = false;
	bool bSavedFixed = false;
	bool bSavedSmooth = false;
	float SavedFixedRate = 30.f;
	int32 SavedVSync = 0;
#endif
}

bool URPGInputTestUtils::InjectAction(APlayerController* Controller, UInputAction* Action, FVector Value)
{
#if UE_BUILD_SHIPPING
	return false;
#else
	const ULocalPlayer* LocalPlayer = Controller ? Controller->GetLocalPlayer() : nullptr;
	UEnhancedInputLocalPlayerSubsystem* Subsystem = LocalPlayer ? LocalPlayer->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>() : nullptr;
	if (!Subsystem || !Action)
	{
		return false;
	}
	Subsystem->InjectInputForAction(Action, FInputActionValue(Value), {}, {});
	return true;
#endif
}

bool URPGInputTestUtils::SetKeyDown(APlayerController* Controller, FName KeyName, bool bDown)
{
#if UE_BUILD_SHIPPING
	return false;
#else
	const FKey Key(KeyName);
	if (!Controller || !Key.IsValid())
	{
		return false;
	}
	return Controller->InputKey(FInputKeyParams(Key, bDown ? IE_Pressed : IE_Released, bDown ? 1.0 : 0.0, /*bIsGamepadOverride=*/false));
#endif
}

bool URPGInputTestUtils::SetFixedFrameRate(float Fps)
{
#if UE_BUILD_SHIPPING
	return false;
#else
	if (!GEngine)
	{
		return false;
	}
	if (Fps <= 0.f)
	{
		RestoreFixedFrameRate();
		return true;
	}
	if (!bFixedActive)
	{
		bSavedFixed = GEngine->bUseFixedFrameRate;
		bSavedSmooth = GEngine->bSmoothFrameRate;
		SavedFixedRate = GEngine->FixedFrameRate;
		if (const IConsoleVariable* VSync = IConsoleManager::Get().FindConsoleVariable(TEXT("r.VSync")))
		{
			SavedVSync = VSync->GetInt();
		}
		bFixedActive = true;
	}
	GEngine->bSmoothFrameRate = false;
	GEngine->bUseFixedFrameRate = true;
	GEngine->FixedFrameRate = FMath::Max(15.f, Fps); // the engine property has a minimum of 15
	if (IConsoleVariable* VSync = IConsoleManager::Get().FindConsoleVariable(TEXT("r.VSync")))
	{
		VSync->Set(0, ECVF_SetByConsole);
	}
	return true;
#endif
}

float URPGInputTestUtils::GetFixedFrameRate()
{
#if UE_BUILD_SHIPPING
	return 0.f;
#else
	return (bFixedActive && GEngine && GEngine->bUseFixedFrameRate) ? GEngine->FixedFrameRate : 0.f;
#endif
}

void URPGInputTestUtils::RestoreFixedFrameRate()
{
#if !UE_BUILD_SHIPPING
	if (!bFixedActive || !GEngine)
	{
		return;
	}
	GEngine->bUseFixedFrameRate = bSavedFixed;
	GEngine->bSmoothFrameRate = bSavedSmooth;
	GEngine->FixedFrameRate = SavedFixedRate;
	if (IConsoleVariable* VSync = IConsoleManager::Get().FindConsoleVariable(TEXT("r.VSync")))
	{
		VSync->Set(SavedVSync, ECVF_SetByConsole);
	}
	bFixedActive = false;
#endif
}
