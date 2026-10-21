// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RPGCombatDebug.generated.h"

/**
 * Combat debug overlay (Master Design Freeze section 22). Attached to the pack boss; shows the boss and the first player together.
 * Console variable rpg.Debug: 0 off (default), 1 on-screen overlay, 2 overlay and one log line per second in the category LogRPGDebug.
 * Shows: encounter (dormant, generation, resets), phase, stagger, health and poise, the boss's active montage with position, length and effective play rate, distance to the player,
 * the player's dodge stage with press counters and the last press gap, stamina and the player's montage. Does nothing in Shipping builds.
 */
UCLASS(ClassGroup = (Boss))
class ONEBOSSFIGHT_API URPGCombatDebug : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGCombatDebug();

	/** The lines the overlay shows right now (tests and logs use it too). Works in every build; only the overlay is stripped from Shipping. */
	UFUNCTION(BlueprintCallable, Category = "Debug")
	TArray<FString> BuildLines() const;

	/** Logs every ability the owner's pack ability system created: class, and the value of every Blueprint variable (montages, play rates, ranges, tags). For reading the pack's setup, not for play. */
	UFUNCTION(BlueprintCallable, Category = "Debug")
	void DumpAbilities() const;

	/** Same as DumpAbilities for the first player pawn (what abilities the pack gave the player, with their variables). */
	UFUNCTION(BlueprintCallable, Category = "Debug")
	void DumpPlayerAbilities() const;

	/** Logs the Blueprint variables of every object held in the owner's attribute component arrays (extended attributes such as poise: regen delay, rate). */
	UFUNCTION(BlueprintCallable, Category = "Debug")
	void DumpAttributes() const;

	/** Logs the Blueprint functions of the first player's pawn and its components (names and parameters), to find the pack's damage entry points. */
	UFUNCTION(BlueprintCallable, Category = "Debug")
	void DumpPlayerFunctions() const;

	UFUNCTION(BlueprintCallable, Category = "Debug")
	void DumpBossFunctions() const;

	/** Test drivers only: sets the boss's posture (poise attribute) to a value, as a hit would leave it. */
	UFUNCTION(BlueprintCallable, Category = "Debug")
	void DebugSetBossPosture(float Value) const;

	/** Test drivers only: lowers the boss's posture by Amount through the pack's Modify Attribute (the path a hit takes, so the pack's regeneration timer restarts like in a fight). */
	UFUNCTION(BlueprintCallable, Category = "Debug")
	void DebugDrainBossPosture(float Amount) const;

	/** Test drivers only: sets the boss's health to a fraction of its maximum (0 to 1) through the attribute, as damage would leave it. */
	UFUNCTION(BlueprintCallable, Category = "Debug")
	void DebugSetBossHealthFraction(float Fraction) const;

	/** Test drivers only: sets the boss's health to zero through the pack's attribute (its own death logic then runs). */
	UFUNCTION(BlueprintCallable, Category = "Debug")
	void DebugKillBoss() const;

	/** Test drivers only: fills the first player's health and stamina so a long series of dodges is not stopped by the stamina cost. Does nothing in Shipping builds. */
	UFUNCTION(BlueprintCallable, Category = "Debug")
	void DebugRefillPlayer() const;

	/** Test drivers only: sets the first player's health to Value (to stand in for damage from another source). */
	UFUNCTION(BlueprintCallable, Category = "Debug")
	void DebugSetPlayerHealth(float Value) const;

	/** Test drivers only: attaches a static mesh (a candidate weapon) to a socket of the boss mesh so a delivery can be looked at in a pose. Replaces the previous test mesh. */
	/** Test drivers only: adds a skeletal piece (crown, mantle, gauntlet) that follows the boss mesh's pose (leader pose component). */
	UFUNCTION(BlueprintCallable, Category = "Debug")
	void DebugAddSkeletalPiece(USkeletalMesh* Piece);

	UFUNCTION(BlueprintCallable, Category = "Debug")
	void DebugAttachTestMesh(UStaticMesh* Mesh, FName Socket, FRotator RelativeRotation, FVector RelativeLocation);

	/** Test drivers only: spawns a movable engine cube (100 cm edge, scaled by Scale) that blocks sight and projectiles, to test line of sight rules. DebugClearWalls removes all of them. */
	UFUNCTION(BlueprintCallable, Category = "Debug")
	void DebugSpawnWall(FVector Location, FRotator Rotation, FVector Scale);

	UFUNCTION(BlueprintCallable, Category = "Debug")
	void DebugClearWalls();

private:
	void DumpFunctionsOf(const AActor* Actor) const;

	UPROPERTY(Transient)
	TArray<TObjectPtr<AActor>> TestWalls;

	UPROPERTY(Transient)
	TObjectPtr<class UStaticMeshComponent> TestMeshComponent;

protected:
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	double NextLog = 0.0;
};
