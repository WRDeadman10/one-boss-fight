// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/WeakObjectPtrTemplates.h"

class AActor;
class UPrimitiveComponent;

/**
 * A read and control facade over the pack's live weapon trace object on the boss (SPEC M1). The pack's trace is Blueprint only: the boss's BP_CollisionComponent_C owns a list of target types (CreatedTargetTypes), and the one
 * tagged TargetType.MainWeapon (a BP_EnemyAbilitySweepingTraceTarget_C) holds the active flag, the hit set, the sockets and the radius. Every name below is read by reflection; a name that is not found is logged once
 * (LogRPGTrace, Warning) and the facade reports failure, so nothing in the game depends on it: the callers switch themselves off. Nothing here edits a pack asset.
 */
namespace RPGPackTrace
{
	struct FTarget
	{
		TWeakObjectPtr<UObject> Collision;
		TWeakObjectPtr<UObject> Object;

		/** Finds the collision component of the boss and its target type with this tag. Cheap when already valid. */
		bool Resolve(const AActor* Boss, FName Tag = TEXT("TargetType.MainWeapon"));

		bool IsValid() const { return Object.IsValid() && Collision.IsValid(); }
		bool IsActive() const;
		int32 GetHitSetNum() const;
		bool HitSetContains(const AActor* Actor) const;
		/** Appends the actor when it is not in the hit set yet. Returns true when it was added. */
		bool HitSetAdd(AActor* Actor);
		/** Removes one occurrence. Returns true when something was removed. */
		bool HitSetRemove(AActor* Actor);
		void GetHitSet(TArray<AActor*>& Out) const;
		UPrimitiveComponent* GetMesh() const;
		void GetSockets(TArray<FName>& Out) const;
		double GetBaseRadius() const;
		double GetRadiusModifier() const;
		bool HasAbility() const;
		/** The stored previous position of a socket (the pack's LastSocketLocations, key ends with the socket name). */
		bool GetStoredLocation(FName Socket, FVector& Out) const;
		/** The pack's own trace-object channels as ECollisionChannel values (via the object type query conversion). */
		void GetObjectChannels(TArray<TEnumAsByte<ECollisionChannel>>& Out) const;
		void GetActorsToIgnore(TArray<AActor*>& Out) const;
		/** Calls the pack's DeactivateCollisionByTag on the collision component. Idempotent. */
		bool Deactivate(FName Tag = TEXT("TargetType.MainWeapon"));
		/** Calls the pack's ClearHitActors custom event on the target. */
		void ClearHitSet();
		/** Calls the pack's UpdateTraceLocations on the target (previous positions = current positions). */
		void RefreshPrevious();
	};

	/** Names the facade needs that are not found on the live objects, for the PackWiring check and the log. Empty when everything resolves. */
	bool CheckLiveNames(const AActor* Boss, FString& OutMissing);

	/** The same names looked up on the pack's Blueprint classes (BP_EnemyAbilitySweepingTraceTarget_C and BP_CollisionComponent_C), with no world: for the automation test that guards against a pack update. */
	bool CheckClassNames(FString& OutMissing);
}
