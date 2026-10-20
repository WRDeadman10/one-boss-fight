// Copyright One Boss Fight. All Rights Reserved.

#include "Combat/RPGInputTestUtils.h"
#include "EnhancedInputSubsystems.h"
#include "GameFramework/PlayerController.h"
#include "Engine/LocalPlayer.h"
#include "InputAction.h"
#include "InputCoreTypes.h"

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
