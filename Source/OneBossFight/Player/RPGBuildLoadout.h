// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Player/RPGBuildRules.h"
#include "RPGBuildLoadout.generated.h"

/**
 * Build loadout (Gate 3, M13): gives the pack player the weapon of the chosen build before the fight and keeps the weapon slot locked during it. The choice is the console variable rpg.Build (Starter, Strength, Dex;
 * empty = no choice: nothing is ever called and the pack's sword stays, so every older driver is unchanged). It is process wide, so it survives a respawn (the pack gives a new pawn the default sword; the new pawn's loadout
 * applies the choice again) and a PIE session. Strength is the pack's claymore (ClaymoreCombatStyle), Dex the dual swords (DualSwordCombatStyle), Starter the sword (SwordCombatStyle); the numbers of each build
 * stay in the weapon attack table, keyed by that style name, so posture, stamina and bleed follow the weapon with no other change (RPGSwingTracker, RPGHitIntake read CurrentCombatStyle).
 * The weapon is equipped through the pack's own flow: the pawn's BP_EquipmentComponent_C.Update Equip Slot Item for the weapon slot (enumerator 11), with an item struct copied from the slot's current item and its
 * Item_ field set to the build's weapon item asset (loaded by path, no asset is edited). The apply runs only while the boss sleeps (a choice made in the fight waits: Defer); while the boss is awake the weapon slot is
 * disabled (Set Equip Slot Disabled) so a quickslot press cannot leave the build. If the style does not change within VerifySeconds the call is repeated up to MaxAttempts times, then the loadout gives up, logs it once
 * and the line of the HUD says what is really equipped (the truth rule: it names the weapon held, never the choice alone).
 * Every pack call is a reflection call that fails soft: a missing name or struct is logged once, counted and never crashes. Attached to the pack player by RPGPlayerMovesSubsystem.
 */
UCLASS(ClassGroup = (Player))
class ONEBOSSFIGHT_API URPGBuildLoadout : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGBuildLoadout();
	FString SetBuild(const FString& Name);

	/** Calls of the pack's equip function per request before the loadout gives up. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build", meta = (ClampMin = "1"))
	int32 MaxAttempts = 3;

	/** Seconds the style gets to change after a call (the pack may swap the weapon at an animation notify) before the call counts as failed. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build", meta = (ClampMin = "0.5"))
	float VerifySeconds = 4.f;

	/** The pack needs a moment at the start (it builds the equipment and sets the sword): nothing is called before this many seconds after the component began to play. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build", meta = (ClampMin = "0.0"))
	float StartupDelaySeconds = 1.f;

	/** Q2: disable the weapon slot from the moment the boss is awake until it sleeps again or is gone. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	bool bLockWeaponSlotInFight = true; // blocks the quickslot ability (Ability.Quickslot) while the boss is awake; the equipment slot's own disabled flags are never used (the whole-slot flag switches the weapon's hits off, the per item flag does not stop the cycle)

	/** On: the equip waits until the pack's combat mode is off (weapon sheathed). Off by default: the pack's own quickslot works in combat mode too (probe 2026-10-22). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	bool bApplyOnlyOutOfCombat = false;

	/** The build of the weapon the player really holds: Starter, Strength, Dex, OffBuild (any other combat style) or Unknown (the pack has not answered yet). */
	UFUNCTION(BlueprintPure, Category = "Build")
	FString GetBuildName() const;

	/** The build that was chosen with rpg.Build; Starter when nothing was chosen (the default). */
	UFUNCTION(BlueprintPure, Category = "Build")
	FString GetChosenBuildName() const;

	/** True when a build was chosen (rpg.Build is not empty or a test hook set it). False: the loadout never calls the pack. */
	UFUNCTION(BlueprintPure, Category = "Build")
	bool HasChoice() const { return bExplicit; }

	/** The line of the HUD, for example "Build: Strength (Claymore)": the weapon really held, with a suffix while the loadout equips, waits for the next fight or has given up. */
	UFUNCTION(BlueprintPure, Category = "Build")
	FString GetBuildLine() const;
	UFUNCTION(BlueprintPure, Category = "Build")
	FString GetCatalogDiagnostic() const;
	UFUNCTION(BlueprintPure, Category = "Build")
	TArray<FString> GetCatalogCoverageLines() const;

	/** The asset name of the combat style the player holds (SwordCombatStyle, ClaymoreCombatStyle, DualSwordCombatStyle, ...), None before the pack has answered. */
	UFUNCTION(BlueprintPure, Category = "Build")
	FString GetActualStyleName() const { return ActualStyle.ToString(); }

	/** Idle (nothing to do), Waiting, Applying, Deferred (the boss is awake) or Failed (the attempts are used). */
	UFUNCTION(BlueprintPure, Category = "Build")
	FString GetStateName() const;

	/** What the loadout did last, in words (the call it made, why it waits, why it failed). */
	UFUNCTION(BlueprintPure, Category = "Build")
	FString GetLastResult() const { return LastResult; }

	/** Calls of the pack's equip function this session (0 while no build was ever chosen). */
	UFUNCTION(BlueprintPure, Category = "Build")
	int32 GetApplyAttemptCount() const { return ApplyCallCount; }

	/** Requests whose style change was seen after the call. */
	UFUNCTION(BlueprintPure, Category = "Build")
	int32 GetApplySuccessCount() const { return ApplySuccessCount; }

	/** Calls that could not be made (a pack name is missing, the item did not load) plus requests the loadout gave up on. */
	UFUNCTION(BlueprintPure, Category = "Build")
	int32 GetApplyFailureCount() const { return ApplyFailureCount; }

	/** Times a choice was held back because the boss was awake. */
	UFUNCTION(BlueprintPure, Category = "Build")
	int32 GetDeferredCount() const { return DeferredCount; }

	/** Console texts that are not a build (rpg.Build Banana): ignored and counted. */
	UFUNCTION(BlueprintPure, Category = "Build")
	int32 GetInvalidRequestCount() const { return InvalidRequestCount; }

	/** Times the weapon slot was locked and unlocked. */
	UFUNCTION(BlueprintPure, Category = "Build")
	int32 GetLockCount() const { return LockCount; }

	UFUNCTION(BlueprintPure, Category = "Build")
	int32 GetUnlockCount() const { return UnlockCount; }

	/** Times the combat style changed while the slot was locked (the lock did not hold: the HUD line then says what is held). */
	UFUNCTION(BlueprintPure, Category = "Build")
	int32 GetLockBreachCount() const { return LockBreachCount; }

	/** True while the pack reports the weapon slot disabled (read from the pack; our own flag when the read fails). */
	UFUNCTION(BlueprintPure, Category = "Build")
	bool IsWeaponSlotLocked() const;

	/** The pack's combat mode (weapon drawn). */
	UFUNCTION(BlueprintPure, Category = "Build")
	bool IsCombatEnabled() const;

	/** The class name of the weapon actor the pack holds in the weapon slot (BP_ToughSword_C, BP_KwangSword_C, BP_DualSteelSwords_C), empty when none. */
	UFUNCTION(BlueprintPure, Category = "Build")
	FString GetEquippedActorClassName() const;

	/** True when the pawn's ability system has an ability of this class (GA_Claymore_Melee_C, GA_DuaSword_Melee_C, GA_Sword_Melee_C). */
	UFUNCTION(BlueprintPure, Category = "Build")
	bool HasWeaponAbilityForTest(const FString& ClassName) const;

	/** "ok" when every pack name the loadout calls was found on the live pack classes, else the list of what is missing, "not checked" before the first check. */
	UFUNCTION(BlueprintPure, Category = "Build")
	FString GetWiringReport() const { return WiringReport; }

	/** The last 32 events of the loadout (choices, calls, style changes, locks), for tests and logs. */
	UFUNCTION(BlueprintCallable, Category = "Build")
	TArray<FString> GetEventLines() const { return Events; }

	/** Test drivers only: sets the choice as the console would (rpg.Build <Name>) and polls at once. Returns Accepted, Deferred (the boss is awake), Same, Cleared (empty text) or Invalid. Python must not set component properties in PIE (KI-083): hooks like this one do it. */
	UFUNCTION(BlueprintCallable, Category = "Build")
	FString SetBuildForTest(const FString& Name);

	/** Test drivers only: polls now instead of at the next tick and returns the decision (Wait, Apply, Done, Defer, GiveUp). Every rule still holds: an awake boss, a busy player and the verify time are not bypassed. */
	UFUNCTION(BlueprintCallable, Category = "Build")
	FString ApplyNowForTest();

	/** Test drivers only: the equip waits for the combat mode to end (true) or not (false). */
	UFUNCTION(BlueprintCallable, Category = "Build")
	void SetApplyOnlyOutOfCombatForTest(bool bOnlyOutOfCombat);

	/** Test drivers only: whether the quickslot ability is blocked while the boss is awake. */
	UFUNCTION(BlueprintCallable, Category = "Build")
	void SetLockWeaponSlotForTest(bool bLock);

	/** Test drivers only: forgets the counters and the events (the choice and the lock stay). */
	UFUNCTION(BlueprintCallable, Category = "Build")
	void ResetCountersForTest();

	/**
	 * The pack names the loadout calls, looked up on the live pack classes (the combat component's CurrentCombatStyle, the equipment component's EquipmentSlots with its struct fields, and the parameters of Update Equip Slot Item,
	 * Set Equip Slot Disabled, Is Equip Slot Disabled? and Get Active Equipped Actor): a pack update that renames one is reported once instead of failing silently in a fight. Returns true when all are found.
	 */
	static bool CheckPackSignatures(const UClass* CombatClass, const UClass* EquipmentClass, FString& OutMissing);

protected:
	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	/** One look at the world and one decision; calls the pack when the decision is Apply. */
	void Poll();
	/** Reads rpg.Build and starts a new request when the text changed. */
	void ReadChoice();
	/** A new request or a new fight: the attempts start again. */
	void ResetRequest();

public:
	/** The weapon slot byte and the update type bytes the loadout found in the pack's enums (logged once; "not read yet" before the pack's equipment component was seen); tests and the wiring triage. */
	UFUNCTION(BlueprintPure, Category = "Build")
	FString GetPackEnumReport() const;

	/** The weapon slot as the pack holds it: the active index, the items (the Item_ asset of each) and the exported text of the slot struct (what its disabled flags say); tests and the lock triage. */
	UFUNCTION(BlueprintPure, Category = "Build")
	FString GetWeaponSlotReport() const;

private:
	/** Locks or unlocks the weapon slot by the boss's state. True when the lock state changed in this poll. */
	bool SyncLock(bool bBossPresent, bool bBossDormant);
	/** Calls the pack's equip function for the build. False (with a reason in OutResult) when the call could not be made. */
	bool CallEquip(FName Build, int32 UpdateType, FString& OutResult);
	const TCHAR* ChosenName() const;
	bool CallSetSlotDisabled(bool bDisable);
	/** The pack's combat style asset name of the player now, None when the pack has not answered. */
	FName ReadStyle() const;
	bool IsPlayerDead() const;
	bool IsPlayerBusy() const;
	/** The encounter component of the boss in the world, null when there is no boss (the pack destroys a dead one). Looked for twice a second at most. */
	class URPGBossEncounter* FindEncounter(double Now);
	/** Logs a failure once per key, counts nothing by itself, and keeps the text as the last result. */
	void NoteFailure(const FString& Key, const FString& Message);
	void AddEvent(const FString& Text);

	TWeakObjectPtr<AActor> BossActor;
	double NextBossSearch = 0.0;
	double StartTime = 0.0;

	FString ChoiceText;
	bool bChoiceRead = false;
	bool bExplicit = false;
	FName ChosenId = TEXT("Starter");
	FName VerifiedBuildId;
	TSharedPtr<const RPGCombatRegistry::FEpoch> Epoch;

	FName ActualStyle;
	RPGBuildRules::EDecision LastDecision = RPGBuildRules::EDecision::Done;
	int32 Attempts = 0;
	double LastAttemptTime = -1.0;
	int32 LastGeneration = 0;

	bool bLocked = false;
	int32 LockFailureStreak = 0;
	/** Polls in a row in which the equip call could not be made at all (the pack not ready); CallFailureLimit of them use one attempt. */
	int32 CallFailureStreak = 0;
	static constexpr int32 CallFailureLimit = 20;
	bool bWiringChecked = false;
	FString WiringReport = TEXT("not checked");

	int32 ApplyCallCount = 0;
	int32 ApplySuccessCount = 0;
	int32 ApplyFailureCount = 0;
	int32 DeferredCount = 0;
	int32 InvalidRequestCount = 0;
	int32 LockCount = 0;
	int32 UnlockCount = 0;
	int32 LockBreachCount = 0;

	FString LastResult = TEXT("no build chosen");
	TSet<FString> Warned;
	TArray<FString> Events;
};
