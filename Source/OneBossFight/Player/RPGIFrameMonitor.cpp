// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGIFrameMonitor.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Animation/AnimNotifies/AnimNotifyState.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "Kismet/GameplayStatics.h"
#include "Pack/RPGBlueprintCall.h"
#include "Player/RPGBossDamage.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGIFrame, Log, All);

using namespace RPGPack;

URPGIFrameMonitor::URPGIFrameMonitor()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickGroup = TG_PostUpdateWork; // after the animation update and its notify dispatch of the frame
}

URPGIFrameMonitor* URPGIFrameMonitor::Find(const UObject* WorldContext)
{
	const APawn* Player = UGameplayStatics::GetPlayerPawn(WorldContext, 0);
	return Player ? Player->FindComponentByClass<URPGIFrameMonitor>() : nullptr;
}

bool URPGIFrameMonitor::ReadWindow(const UAnimMontage* Montage, float& OutStart, float& OutEnd) const
{
	OutStart = OutEnd = -1.f;
	if (!Montage)
	{
		return false;
	}
	for (const FAnimNotifyEvent& Event : Montage->Notifies)
	{
		if (Event.NotifyStateClass && Event.NotifyStateClass->GetClass()->GetFName() == NotifyStateClassName)
		{
			OutStart = Event.GetTriggerTime();
			OutEnd = Event.GetEndTriggerTime();
			return true;
		}
	}
	return false;
}

const URPGIFrameMonitor::FRecord* URPGIFrameMonitor::Get(int32 Index) const
{
	if (Index < 0)
	{
		Index = Records.Num() + Index;
	}
	return Records.IsValidIndex(Index) ? &Records[Index] : nullptr;
}

double URPGIFrameMonitor::GetRecordNumber(int32 Index, const FString& Field) const
{
	const FRecord* R = Get(Index);
	if (!R)
	{
		return -9999.0;
	}
	if (Field == TEXT("Rate")) { return R->Rate; }
	if (Field == TEXT("ExpectedStart")) { return R->ExpectedStart; }
	if (Field == TEXT("ExpectedEnd")) { return R->ExpectedEnd; }
	if (Field == TEXT("StartPos")) { return R->StartPos; }
	if (Field == TEXT("EndPos")) { return R->EndPos; }
	if (Field == TEXT("StartTime")) { return R->StartTime; }
	if (Field == TEXT("EndTime")) { return R->EndTime; }
	if (Field == TEXT("StartDelta")) { return R->StartPos - R->ExpectedStart; }
	if (Field == TEXT("EndExpected")) { return R->EndExpectedEnd >= 0.f ? R->EndExpectedEnd : R->ExpectedEnd; }
	if (Field == TEXT("EndDelta")) { return R->EndPos - (R->EndExpectedEnd >= 0.f ? R->EndExpectedEnd : R->ExpectedEnd); }
	if (Field == TEXT("Owned")) { return R->bOwned ? 1.0 : 0.0; }
	if (Field == TEXT("Closed")) { return R->bClosed ? 1.0 : 0.0; }
	if (Field == TEXT("FrameStep")) { return R->FrameStep; }
	return -9999.0;
}

FString URPGIFrameMonitor::GetRecordText(int32 Index, const FString& Field) const
{
	const FRecord* R = Get(Index);
	if (!R)
	{
		return FString();
	}
	return Field == TEXT("Montage") ? R->Montage : (Field == TEXT("Reason") ? R->Reason : (Field == TEXT("EndMontage") ? R->EndMontage : FString()));
}

void URPGIFrameMonitor::ClearRecords()
{
	Records.Reset();
	bOpen = false;
}

FString URPGIFrameMonitor::GetSourceText() const
{
	if (!bTag)
	{
		return TEXT("none");
	}
	if (!bOwnedNow || Records.Num() == 0)
	{
		return TEXT("Status.Invulnerable (not set by a dodge montage)");
	}
	const FRecord& R = Records.Last();
	return FString::Printf(TEXT("Status.Invulnerable via %s at %.3f of window %.3f to %.3f, rate %.2f"), *R.Montage, LastPos, R.ExpectedStart, R.ExpectedEnd, R.Rate);
}

void URPGIFrameMonitor::DebugForceOwned(bool bOwned)
{
#if !UE_BUILD_SHIPPING
	bForceOwned = bOwned;
	if (bOwned && bTag)
	{
		bOwnedNow = true;
	}
#endif
}

void URPGIFrameMonitor::RemoveTag(const TCHAR* Reason)
{
	AActor* Owner = GetOwner();
	const FGameplayTag Tag = FGameplayTag::RequestGameplayTag(TEXT("Status.Invulnerable"), false);
	const bool bCalled = CallBlueprintFunction(Owner, TEXT("RemoveOwnedGameplayTag"), [&Tag](UFunction& F, uint8* P) { SetTag(F, P, TEXT("TagToRemove"), Tag); }, [](UFunction&, uint8*) {});
	UE_LOG(LogRPGIFrame, Log, TEXT("%s: Status.Invulnerable removed (%s), call %s"), *Owner->GetName(), Reason, bCalled ? TEXT("ok") : TEXT("failed"));
}

void URPGIFrameMonitor::CloseRecord(const TCHAR* Reason, float EndPos)
{
	if (bOpen && Records.Num() > 0)
	{
		FRecord& R = Records.Last();
		R.bClosed = true;
		R.EndPos = EndPos;
		R.EndTime = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
		R.Reason = Reason;
		R.EndMontage = LastMontage;
		R.EndExpectedEnd = LastWindowEnd;
	}
	bOpen = false;
}

void URPGIFrameMonitor::OnEncounterReset()
{
	if (bTag && bOwnedNow)
	{
		RemoveTag(TEXT("encounter reset"));
		++ResetCleared;
		CloseRecord(TEXT("EncounterReset"), LastPos);
		bTag = false;
		bOwnedNow = false;
	}
}

void URPGIFrameMonitor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	CloseRecord(TEXT("EndPlay"), LastPos);
	Super::EndPlay(EndPlayReason);
}

void URPGIFrameMonitor::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	const ACharacter* Character = Cast<ACharacter>(GetOwner());
	const UWorld* World = GetWorld();
	if (!bEnabled || !Character || !World)
	{
		return;
	}
	const double Now = World->GetTimeSeconds();
	const bool bNow = RPGBossDamage::IsInvulnerable(GetOwner());
	const bool bAlive = RPGBossDamage::IsAlive(GetOwner());

	UAnimInstance* Anim = Character->GetMesh() ? Character->GetMesh()->GetAnimInstance() : nullptr;
	const UAnimMontage* Montage = Anim ? Anim->GetCurrentActiveMontage() : nullptr;
	float Position = 0.f, Rate = 1.f, WindowStart = -1.f, WindowEnd = -1.f;
	bool bHasWindow = false;
	if (Montage)
	{
		Position = Anim->Montage_GetPosition(Montage);
		Rate = Anim->Montage_GetEffectivePlayRate(Montage);
		if (const FVector2D* Cached = WindowCache.Find(Montage))
		{
			WindowStart = Cached->X;
			WindowEnd = Cached->Y;
			bHasWindow = WindowStart >= 0.f;
		}
		else
		{
			bHasWindow = ReadWindow(Montage, WindowStart, WindowEnd);
			WindowCache.Add(Montage, FVector2D(WindowStart, WindowEnd));
		}
		LastPos = Position;
		LastRate = Rate;
		LastMontage = Montage->GetName();
		LastWindowEnd = bHasWindow ? WindowEnd : -1.f;
		LastPosTime = Now;
	}
	// Where the montage would be now: the quick dash's montage leaves GetCurrentActiveMontage when it starts to blend out, before its window ends.
	const float GonePosition = LastPos + static_cast<float>(Now - LastPosTime) * LastRate;
	const float Step = DeltaTime * FMath::Abs(Rate);
	LastStep = Step;

	if (bNow && !bTag)
	{
		// Rising edge: owned when a dodge montage is inside its window (within one frame and a small margin), else foreign.
		const float Tolerance = Step + 0.004f;
		const bool bInside = bHasWindow && Position >= WindowStart - Tolerance && Position <= WindowEnd + Tolerance;
		bOwnedNow = bInside || bForceOwned;
		TagSince = Now;
		MontageGoneSince = -1.0;
		FRecord R;
		R.Montage = Montage ? Montage->GetName() : FString(TEXT("none"));
		R.Rate = Rate;
		R.ExpectedStart = bHasWindow ? WindowStart : -1.f;
		R.ExpectedEnd = bHasWindow ? WindowEnd : -1.f;
		R.StartPos = Position;
		R.StartTime = Now;
		R.FrameStep = Step;
		R.bOwned = bOwnedNow;
		Records.Add(R);
		while (Records.Num() > MaxRecords)
		{
			Records.RemoveAt(0);
		}
		bOpen = true;
		UE_LOG(LogRPGIFrame, Log, TEXT("%s: invulnerable on (%s) at %.3f s of %s, rate %.2f, window %.3f to %.3f"), *GetOwner()->GetName(), bOwnedNow ? TEXT("dodge montage") : TEXT("foreign"), Position, *R.Montage, Rate, R.ExpectedStart, R.ExpectedEnd);
	}
	else if (!bNow && bTag)
	{
		// Falling edge. Natural when the position is at the end of the window; early when it is clearly inside it (something removed the tag). The quick dash's window ends with its montage, so the edge
		// can be seen after the montage is gone: the last position and window seen stand in for it.
		const float Tolerance = Step + 0.004f;
		const float EndPosition = Montage ? Position : GonePosition;
		const float EndWindowEnd = Montage ? (bHasWindow ? WindowEnd : -1.f) : LastWindowEnd;
		const float EndTolerance = Montage ? Tolerance : LastStep + 0.004f;
		const bool bNatural = EndWindowEnd >= 0.f && EndPosition >= EndWindowEnd - EndTolerance;
		const TCHAR* Reason = !bAlive ? TEXT("Death") : (bNatural ? TEXT("Natural") : (!Montage ? TEXT("Interrupted") : TEXT("Unknown")));
		if (bOwnedNow && Montage && bHasWindow && Position > WindowStart + Tolerance && Position < WindowEnd - Tolerance)
		{
			++UnexpectedDrops;
			Reason = TEXT("EarlyDrop");
			UE_LOG(LogRPGIFrame, Warning, TEXT("%s: invulnerability dropped early at %.3f of window %.3f to %.3f (%s)"), *GetOwner()->GetName(), Position, WindowStart, WindowEnd, *LastMontage);
		}
		CloseRecord(Reason, EndPosition);
		bOwnedNow = false;
		UE_LOG(LogRPGIFrame, Log, TEXT("%s: invulnerable off (%s) at %.3f"), *GetOwner()->GetName(), Reason, EndPosition);
	}
	bTag = bNow;

	if (bTag && bOwnedNow)
	{
		// Watchdog (Freeze 491 to 493): the dodge's montage is gone or its window is over, yet the tag is still up.
		const bool bMontageGone = !Montage;
		const bool bPastWindow = Montage && bHasWindow && Position > WindowEnd + Step;
		if (bMontageGone || bPastWindow)
		{
			if (MontageGoneSince < 0.0)
			{
				MontageGoneSince = Now;
			}
			if (Now - MontageGoneSince >= StaleGraceSeconds)
			{
				RemoveTag(TEXT("stale"));
				++StaleCleared;
				CloseRecord(TEXT("StaleCleared"), Montage ? Position : GonePosition);
				bTag = false;
				bOwnedNow = false;
				bForceOwned = false;
				MontageGoneSince = -1.0;
			}
		}
		else
		{
			MontageGoneSince = -1.0;
		}
		// Death: the tag goes at once.
		if (!bAlive && bWasAlive)
		{
			RemoveTag(TEXT("player died"));
			++DeathCleared;
			CloseRecord(TEXT("Death"), Position);
			bTag = false;
			bOwnedNow = false;
		}
	}
	bWasAlive = bAlive;
}
