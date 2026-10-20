// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "RPGInputTestUtils.generated.h"

class APlayerController;
class UInputAction;

/**
 * Test helpers for PIE driver scripts. Python cannot reach the local player's Enhanced Input subsystem, so the scripts call this to press the
 * pack's real input actions (IA_Dodge, IA_StrongAttack, ...) and exercise the pack's input graph instead of calling its abilities directly.
 */
UCLASS()
class ONEBOSSFIGHT_API URPGInputTestUtils : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/** Injects the action as held for this frame (call every tick for as long as the key is down; stop calling to release). Returns false when the
	 *  controller has no Enhanced Input subsystem. */
	UFUNCTION(BlueprintCallable, Category = "RPG|Test")
	static bool InjectAction(APlayerController* Controller, UInputAction* Action, FVector Value = FVector(1.0, 0.0, 0.0));

	/** Presses or releases a keyboard or gamepad key (KeyName as in EKeys, e.g. "SpaceBar", "Gamepad_FaceButton_Right") through the whole input mapping, like a
	 *  real key: every action mapped to the key fires with its own triggers (a tap, a hold). Press once, call again with bDown false to release. */
	UFUNCTION(BlueprintCallable, Category = "RPG|Test")
	static bool SetKeyDown(APlayerController* Controller, FName KeyName, bool bDown);
};
