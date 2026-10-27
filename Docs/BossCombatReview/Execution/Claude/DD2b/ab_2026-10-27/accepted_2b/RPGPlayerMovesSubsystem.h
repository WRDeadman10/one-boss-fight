// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "RPGPlayerMovesSubsystem.generated.h"

/**
 * Adds this project's moves to the Advanced ARPG pack's pawns without editing the pack: when the pack player pawn (BP_CombatPlayerCharacter or a child) spawns, in any
 * game world, it gets a URPGDodgeTiming component (a new pawn after a respawn gets its own); the pack great-sword boss (BP_ExampleGreatSwordBoss) gets a
 * URPGBossStagger component (stance break and critical window).
 */
UCLASS()
class ONEBOSSFIGHT_API URPGPlayerMovesSubsystem : public UWorldSubsystem
{
	GENERATED_BODY()

public:
	virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
	virtual void PostInitialize() override;
	virtual void OnWorldBeginPlay(UWorld& InWorld) override;
	virtual void Deinitialize() override;

	static bool IsPackPlayer(const AActor* Actor);
	static bool IsPackBoss(const AActor* Actor);

private:
	void OnActorSpawned(AActor* Actor);
	void Attach(AActor* Pawn) const;
	void AttachLegacyBossPrelude(AActor* Pawn) const; // boss footsteps and music, called from the boss branch ahead of the player components
	void AttachLegacyBossBundle(AActor* Pawn) const; // the guarded boss component registrations, called after the player components

	FDelegateHandle SpawnHandle;
};
