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
	bool bFixedActive = false;
	bool bSavedFixed = false;
	bool bSavedSmooth = false;
	float SavedFixedRate = 30.f;
	int32 SavedVSync = 0;
}

bool URPGInputTestUtils::InjectAction(APlayerController* Controller, UInputAction* Action, FVector Value)
{
	const ULocalPlayer* LocalPlayer = Controller ? Controller->GetLocalPlayer() : nullptr;
	UEnhancedInputLocalPlayerSubsystem* Subsystem = LocalPlayer ? LocalPlayer->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>() : nullptr;
	if (!Subsystem || !Action)
	{
		return false;
	}
	Subsystem->InjectInputForAction(Action, FInputActionValue(Value), {}, {});
	return true;
}

bool URPGInputTestUtils::SetKeyDown(APlayerController* Controller, FName KeyName, bool bDown)
{
	const FKey Key(KeyName);
	if (!Controller || !Key.IsValid())
	{
		return false;
	}
	return Controller->InputKey(FInputKeyParams(Key, bDown ? IE_Pressed : IE_Released, bDown ? 1.0 : 0.0, /*bIsGamepadOverride=*/false));
}

bool URPGInputTestUtils::SetFixedFrameRate(float Fps)
{
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
}

float URPGInputTestUtils::GetFixedFrameRate()
{
	return (bFixedActive && GEngine && GEngine->bUseFixedFrameRate) ? GEngine->FixedFrameRate : 0.f;
}

void URPGInputTestUtils::RestoreFixedFrameRate()
{
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
}
