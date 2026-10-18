// Copyright One Boss Fight. All Rights Reserved.

#include "Combat/RPGAttributeComponent.h"

URPGAttributeComponent::URPGAttributeComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.bStartWithTickEnabled = false;
}

void URPGAttributeComponent::EnsureInitialized() const
{
	if (!bInitialized)
	{
		bInitialized = true;
		Health = MaxHealth;
		Stamina = MaxStamina;
		Poise = MaxPoise;
	}
}

float URPGAttributeComponent::GetHealth() const
{
	EnsureInitialized();
	return Health;
}

float URPGAttributeComponent::GetStamina() const
{
	EnsureInitialized();
	return Stamina;
}

float URPGAttributeComponent::GetPoise() const
{
	EnsureInitialized();
	return Poise;
}

float URPGAttributeComponent::ApplyDamage(float Amount)
{
	EnsureInitialized();
	if (bDead || Amount <= 0.f)
	{
		return 0.f;
	}

	const float Applied = FMath::Min(Amount, Health);
	Health -= Applied;
	OnHealthChanged.Broadcast(Health, MaxHealth, -Applied);

	if (Health <= 0.f)
	{
		bDead = true;
		StaminaDrainPerSecond = 0.f;
		RefreshTickState();
		OnDeath.Broadcast();
	}
	return Applied;
}

void URPGAttributeComponent::Heal(float Amount)
{
	EnsureInitialized();
	if (bDead || Amount <= 0.f)
	{
		return;
	}

	const float NewHealth = FMath::Min(Health + Amount, MaxHealth);
	const float Delta = NewHealth - Health;
	Health = NewHealth;
	if (Delta > 0.f)
	{
		OnHealthChanged.Broadcast(Health, MaxHealth, Delta);
	}
}

void URPGAttributeComponent::SetStamina(float NewValue)
{
	const float Clamped = FMath::Clamp(NewValue, 0.f, MaxStamina);
	const float Delta = Clamped - Stamina;
	Stamina = Clamped;
	if (!FMath::IsNearlyZero(Delta))
	{
		OnStaminaChanged.Broadcast(Stamina, MaxStamina, Delta);
	}
}

void URPGAttributeComponent::SetPoise(float NewValue)
{
	const float Clamped = FMath::Clamp(NewValue, 0.f, MaxPoise);
	const float Delta = Clamped - Poise;
	Poise = Clamped;
	if (!FMath::IsNearlyZero(Delta))
	{
		OnPoiseChanged.Broadcast(Poise, MaxPoise, Delta);
	}
}

bool URPGAttributeComponent::TryConsumeStamina(float Cost)
{
	EnsureInitialized();
	if (bDead)
	{
		return false;
	}
	if (Cost <= 0.f)
	{
		return true;
	}
	if (Stamina <= 0.f)
	{
		return false;
	}

	SetStamina(Stamina - Cost);
	TimeSinceStaminaUse = 0.f;
	RefreshTickState();
	return true;
}

bool URPGAttributeComponent::ForceConsumeStamina(float Amount)
{
	EnsureInitialized();
	if (Amount > 0.f)
	{
		SetStamina(Stamina - Amount);
		TimeSinceStaminaUse = 0.f;
		RefreshTickState();
	}
	return Stamina <= 0.f;
}

bool URPGAttributeComponent::ApplyPoiseDamage(float Amount)
{
	EnsureInitialized();
	if (bDead || Amount <= 0.f)
	{
		return false;
	}

	TimeSincePoiseDamage = 0.f;
	SetPoise(Poise - Amount);
	RefreshTickState();

	if (Poise <= 0.f)
	{
		// Broken: refill so the next stagger needs a fresh build-up instead of chain-staggering.
		SetPoise(MaxPoise);
		return true;
	}
	return false;
}

void URPGAttributeComponent::SetStaminaDrain(float PerSecond)
{
	StaminaDrainPerSecond = FMath::Max(0.f, PerSecond);
	RefreshTickState();
}

void URPGAttributeComponent::ResetAttributes()
{
	EnsureInitialized();
	bDead = false;
	StaminaDrainPerSecond = 0.f;
	TimeSinceStaminaUse = 0.f;
	TimeSincePoiseDamage = 0.f;

	const float HealthDelta = MaxHealth - Health;
	Health = MaxHealth;
	Stamina = MaxStamina;
	Poise = MaxPoise;
	OnHealthChanged.Broadcast(Health, MaxHealth, HealthDelta);
	OnStaminaChanged.Broadcast(Stamina, MaxStamina, 0.f);
	OnPoiseChanged.Broadcast(Poise, MaxPoise, 0.f);
	RefreshTickState();
}

void URPGAttributeComponent::TickAttributes(float DeltaTime)
{
	EnsureInitialized();
	if (bDead || DeltaTime <= 0.f)
	{
		return;
	}

	// Drain wins over regeneration while it is active.
	if (StaminaDrainPerSecond > 0.f)
	{
		TimeSinceStaminaUse = 0.f;
		if (Stamina > 0.f)
		{
			SetStamina(Stamina - StaminaDrainPerSecond * DeltaTime);
			if (Stamina <= 0.f)
			{
				StaminaDrainPerSecond = 0.f;
				OnStaminaDepleted.Broadcast();
			}
		}
	}
	else
	{
		TimeSinceStaminaUse += DeltaTime;
		if (Stamina < MaxStamina && TimeSinceStaminaUse >= StaminaRegenDelay)
		{
			SetStamina(Stamina + StaminaRegenPerSecond * DeltaTime);
		}
	}

	if (Poise < MaxPoise)
	{
		TimeSincePoiseDamage += DeltaTime;
		if (TimeSincePoiseDamage >= PoiseResetDelay)
		{
			SetPoise(MaxPoise);
		}
	}

	RefreshTickState();
}

void URPGAttributeComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	TickAttributes(DeltaTime);
}

bool URPGAttributeComponent::NeedsTick() const
{
	EnsureInitialized();
	return !bDead && (StaminaDrainPerSecond > 0.f || Stamina < MaxStamina || Poise < MaxPoise);
}

void URPGAttributeComponent::RefreshTickState()
{
	if (IsRegistered())
	{
		SetComponentTickEnabled(NeedsTick());
	}
}
