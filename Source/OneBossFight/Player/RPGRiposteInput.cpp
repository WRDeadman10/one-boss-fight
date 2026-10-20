// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGRiposteInput.h"
#include "Player/RPGBossStagger.h"
#include "Player/RPGPlayerMovesSubsystem.h"
#include "EnhancedInputComponent.h"
#include "EngineUtils.h"
#include "GameFramework/Pawn.h"
#include "InputAction.h"
#include "Engine/World.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGRiposte, Log, All);

URPGRiposteInput::URPGRiposteInput()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickInterval = 0.2f;
	LightAttackAction = TSoftObjectPtr<UInputAction>(FSoftObjectPath(TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_NormalAttack.IA_NormalAttack")));
}

void URPGRiposteInput::BeginPlay()
{
	Super::BeginPlay();
	TryBind();
}

void URPGRiposteInput::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	if (!bBound)
	{
		TryBind(); // the pawn's input component exists once it is possessed
	}
}

bool URPGRiposteInput::TryBind()
{
	const APawn* Pawn = Cast<APawn>(GetOwner());
	UEnhancedInputComponent* Input = Pawn ? Cast<UEnhancedInputComponent>(Pawn->InputComponent) : nullptr;
	UInputAction* Action = LightAttackAction.LoadSynchronous();
	if (!Input || !Action)
	{
		return false;
	}
	Input->BindAction(Action, ETriggerEvent::Started, this, &URPGRiposteInput::OnLightAttack);
	bBound = true;
	UE_LOG(LogRPGRiposte, Log, TEXT("%s: riposte input bound to %s"), *GetOwner()->GetName(), *Action->GetName());
	return true;
}

void URPGRiposteInput::OnLightAttack(const FInputActionInstance& Instance)
{
	++PressCount;
	const UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}
	for (TActorIterator<APawn> It(World); It; ++It)
	{
		if (URPGPlayerMovesSubsystem::IsPackBoss(*It))
		{
			if (URPGBossStagger* Stagger = It->FindComponentByClass<URPGBossStagger>())
			{
				if (Stagger->IsStaggered() && Stagger->TryRiposte(GetOwner()))
				{
					++AcceptedCount;
				}
			}
		}
	}
}
