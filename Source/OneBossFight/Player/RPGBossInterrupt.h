// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

/** What a stance break or a phase transition does to the boss's own offence (Freeze 17.3 items 2 and 3, 18.1 line 766). */
namespace RPGBossInterrupt
{
	/**
	 * Cancels what the boss's own code has in the air: the A4 blade, the A6 wave, the A5 pending request and javelins in flight. It logs one line first (Freeze 724: record what was cancelled).
	 * It does not touch the attack tracker, montages or pack abilities: the montage that replaces the attack (the fall clip, the roar) ends them, as the A2 interruption tests proved. Idempotent and cheap when nothing runs.
	 */
	void CancelOffence(AActor* Boss, const TCHAR* Reason);
}
