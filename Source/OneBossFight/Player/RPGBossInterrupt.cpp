// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossInterrupt.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/Character.h"
#include "Player/RPGAttackTracker.h"
#include "Player/RPGBossHealPunish.h"
#include "Player/RPGBossLowSweep.h"
#include "Player/RPGBossShockwave.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGInterrupt, Log, All);

void RPGBossInterrupt::CancelOffence(AActor* Boss, const TCHAR* Reason)
{
	if (!Boss)
	{
		return;
	}
	URPGBossLowSweep* Sweep = Boss->FindComponentByClass<URPGBossLowSweep>();
	URPGBossShockwave* Wave = Boss->FindComponentByClass<URPGBossShockwave>();
	URPGBossHealPunish* Punish = Boss->FindComponentByClass<URPGBossHealPunish>();
	const URPGAttackTracker* Tracker = Boss->FindComponentByClass<URPGAttackTracker>();
	const bool bBlade = Sweep && Sweep->IsBladeActive();
	const bool bWave = Wave && Wave->IsWaveActive();
	const bool bPending = Punish && Punish->IsPending();
	const bool bMove = Tracker && Tracker->GetCurrentMove() != NAME_None;
	if (bBlade || bWave || bPending || bMove)
	{
		// What was cancelled (Freeze 724). The tracker's own move ends by itself when the montage is replaced.
		FString Montage = TEXT("none");
		float Position = -1.f;
		if (const ACharacter* Character = Cast<ACharacter>(Boss))
		{
			if (const UAnimInstance* Anim = Character->GetMesh() ? Character->GetMesh()->GetAnimInstance() : nullptr)
			{
				if (const UAnimMontage* Active = Anim->GetCurrentActiveMontage())
				{
					Montage = Active->GetName();
					Position = Anim->Montage_GetPosition(Active);
				}
			}
		}
		UE_LOG(LogRPGInterrupt, Log, TEXT("%s: offence cancelled (%s): move %s (%s), blade %d, wave %d, pending punish %d, montage %s at %.2f s"), *Boss->GetName(), Reason,
			Tracker ? *Tracker->GetCurrentMove().ToString() : TEXT("-"), Tracker ? *Tracker->GetPhaseName() : TEXT("-"), bBlade ? 1 : 0, bWave ? 1 : 0, bPending ? 1 : 0, *Montage, Position);
	}
	if (Sweep)
	{
		Sweep->Cancel(Reason);
	}
	if (Wave)
	{
		Wave->Cancel(Reason);
	}
	if (Punish)
	{
		Punish->CancelAll(Reason);
	}
}
