// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "UObject/SoftObjectPtr.h"
#include "RPGBossDeath.generated.h"

class AActor;
class ACharacter;
class UAnimMontage;
class UAnimSequence;
class USceneComponent;

/** Who plays the boss's death animation (URPGBossDeath). */
UENUM(BlueprintType)
enum class ERPGBossDeathMode : uint8
{
	/** The pack's own death ability (GA_EnemyRagdollDeath_C) plays AM_Boss01_DeathLegend: this component only fills the ability's DeathMontages array and watches. */
	PackMontage,
	/** This component plays AN_Boss01_DeathLegend itself on the boss mesh, freezes its last pose and keeps the pack's ragdoll off the mesh. */
	OwnClip
};

/**
 * The boss's death clip (G2-9, A-12): Antigravity's AN_Boss01_DeathLegend (3.5 s, the boss collapses to its knees by 2.5 s and the last second is the same slumped pose). The pack kills the boss with its ragdoll death
 * ability (GA_EnemyRagdollDeath_C, tag Ability.Dead) and destroys the actor a few seconds later (KI-083). Which of the two designs fits is decided by the probes (pie_death_probe.py, see Documentation/DEATH_CLIP_NOTES.md):
 *   PackMontage: one frame after BeginPlay, and again one frame after every encounter reset (and every PackPollSeconds, in case the ability instance is a new one), the live ability's DeathMontages array is set to
 *                the montage AM_Boss01_DeathLegend (Scripts/Editor/make_death_montage.py). The pack plays it and does the rest. The array holds either montages or the pack's F_AbilityMontage structs; both are handled by reflection.
 *   OwnClip:     on the first frame the boss's health is 0 the clip plays through RPGBossClips (as the stagger clips do), is paused at HoldAtSeconds so the kneeling pose stays, and every tick while dead the mesh is kept
 *                out of physics simulation so the pack's ragdoll cannot throw the body over (the mesh is also put back at its place on the capsule). Nothing is done once the actor is being destroyed (EndPlay).
 * Both modes only observe the health attribute for the state (alive, dying, dead) and count what they did. The death flow of the pack is never delayed or cancelled and the victory (polls health) is not touched.
 * No pack asset is edited. Attached to the pack boss by RPGPlayerMovesSubsystem (URPGBossDeath::Attach).
 */
UCLASS(ClassGroup = (Boss))
class ONEBOSSFIGHT_API URPGBossDeath : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGBossDeath();

	/** The one-line attach: adds the component to the boss when it has none (returns the existing one otherwise) and sets its mode. Call it from the subsystem where the other boss components are added. */
	static URPGBossDeath* Attach(AActor* Boss, ERPGBossDeathMode Mode);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death")
	ERPGBossDeathMode DeathMode = ERPGBossDeathMode::PackMontage;

	/** The clip of OwnClip mode (Antigravity, on the mannequin skeleton). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death")
	TSoftObjectPtr<UAnimSequence> DeathClip;

	/** The montage of PackMontage mode, made from the clip by Scripts/Editor/make_death_montage.py. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death")
	TSoftObjectPtr<UAnimMontage> DeathMontage;

	/** Class name of the pack's death ability instance (a Blueprint instance in the boss's ability system component) and the name of its montage array. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death")
	FName PackDeathAbilityClassName = TEXT("GA_EnemyRagdollDeath_C");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death")
	FName PackDeathMontagesName = TEXT("DeathMontages");

	/** PackMontage: seconds between two looks at the ability's array (a pack that rebuilt its ability instances is caught here); the first look is one frame after BeginPlay and one frame after every encounter reset. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death", meta = (ClampMin = "0.1"))
	float PackPollSeconds = 1.f;

	/** PackMontage: above 0 it is written into the EndTimeMultiplier field of the DeathMontages entry (the pack ends the ability at that fraction of the montage); 0 leaves the pack struct's own default. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death", meta = (ClampMin = "0.0"))
	float PackEndTimeMultiplier = 0.f;

	/** Clip position (seconds) where the final pose is frozen: the clip is 3.5 s long and its frames are identical from 2.5 s on, so the pause shows the same pose as the end. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death", meta = (ClampMin = "0.1"))
	float HoldAtSeconds = 3.f;

	/** Seconds from the death until the collapse is over (the clip is on its knees at 2.5 s): the state is "dying" until then and "dead" after. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death", meta = (ClampMin = "0.1"))
	float DyingSeconds = 2.5f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death", meta = (ClampMin = "0.0"))
	float BlendInSeconds = 0.1f;

	/** OwnClip: how many times the clip is started again when something stops the montage (the pack's death flow, another clip) before the component gives up (it does not fight the pack for ever). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death", meta = (ClampMin = "0"))
	int32 MaxClipRestarts = 8;

	/** PackMontage only: the death montage is paused at HoldAtSeconds and the ragdoll kept off, as in OwnClip. Off by default: the pack's ability may wait for the montage to end before it destroys the boss, and a paused montage would then keep the boss for ever. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death")
	bool bGuardPackDeath = false;

	/** "alive", "dying" (from the first frame of health 0 until DyingSeconds have passed) or "dead". */
	UFUNCTION(BlueprintPure, Category = "Death")
	FString GetDeathStateName() const;

	/** True from the frame the boss's health reads 0 until the health is back (the pack destroys a dead boss about 4.35 s later: KI-083). The encounter does not reset a boss in this state. */
	bool IsDeathActive() const { return State != EState::Alive; }

	/** "pack_montage" or "own_clip". */
	UFUNCTION(BlueprintPure, Category = "Death")
	FString GetDeathModeName() const;

	/** Seconds since the death was seen, -1 while the boss is alive. */
	UFUNCTION(BlueprintPure, Category = "Death")
	double GetDeathAge() const;

	/** Death edges seen (health went to 0), clips started (OwnClip, restarts included), clips started again because something stopped the montage, times the pose was frozen, ticks in which the mesh had to be taken out of physics simulation. */
	UFUNCTION(BlueprintPure, Category = "Death")
	int32 GetDeathCount() const { return DeathCount; }

	UFUNCTION(BlueprintPure, Category = "Death")
	int32 GetClipPlayCount() const { return ClipPlayCount; }

	UFUNCTION(BlueprintPure, Category = "Death")
	int32 GetClipRestartCount() const { return ClipRestartCount; }

	UFUNCTION(BlueprintPure, Category = "Death")
	int32 GetPoseHoldCount() const { return PoseHoldCount; }

	UFUNCTION(BlueprintPure, Category = "Death")
	int32 GetPhysicsOffCount() const { return PhysicsOffCount; }

	/** PackMontage: times the DeathMontages array was written, and what the last look at the ability found ("set ...", "already set", or why it could not be set). */
	UFUNCTION(BlueprintPure, Category = "Death")
	int32 GetPackSetCount() const { return PackSetCount; }

	UFUNCTION(BlueprintPure, Category = "Death")
	FString GetLastPackResult() const { return LastPackResult; }

	/** True while the clip's last pose is frozen (paused). */
	UFUNCTION(BlueprintPure, Category = "Death")
	bool IsPoseHeld() const { return bPoseHeld; }

	/** Test drivers only. Python must not change a component property in PIE (KI-083: set_editor_property re-runs the owner's construction scripts): these functions change the same values without that side effect.
	 *  The mode is "own" (OwnClip) or anything else (PackMontage); change it before the kill. */
	UFUNCTION(BlueprintCallable, Category = "Death")
	void SetDeathModeForTest(const FString& Mode);

	UFUNCTION(BlueprintCallable, Category = "Death")
	void SetGuardPackDeathForTest(bool bOn) { bGuardPackDeath = bOn; }

	/** Tests: looks at the pack's death ability now (PackMontage) and returns what it found, the same text as GetLastPackResult. */
	UFUNCTION(BlueprintCallable, Category = "Death")
	FString ApplyPackMontageNow();

protected:
	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
	enum class EState : uint8 { Alive, Dying, Dead };

	/** First tick: loads what the mode needs, so the frame of the death never waits for the disk. */
	void Preload();
	UAnimSequence* GetClip();
	UAnimMontage* GetMontage();
	/** Remembers where the mesh sits on the capsule while the boss lives: the pack's ragdoll moves it. */
	void CaptureMeshPlacement(const ACharacter* Character);
	void PollPack(double Now);
	/** Sets the pack's DeathMontages array to [the montage]; true when the array holds it (written now or already). */
	bool ApplyPackMontage();
	bool NotePackMiss(const FString& Why);
	void BeginDeath(ACharacter* Character, double Now);
	/** The health came back (an encounter reset of a boss that was not destroyed): stand the state down and stop the clip. */
	void EndDeathState(ACharacter* Character, const TCHAR* Why);
	void TickDeath(ACharacter* Character, double Now);
	/** Plays the clip from StartAt (clip seconds); a start at or after HoldAtSeconds is frozen at once. */
	bool StartOwnClip(ACharacter* Character, float StartAt);
	/** Keeps the mesh out of physics simulation (and back on the capsule) while the pose is guarded. */
	void KeepPhysicsOff(ACharacter* Character);
	/** Freezes the clip at HoldAtSeconds; OwnClip also starts it again when something stopped it. */
	void KeepClip(ACharacter* Character, double Age);

	bool bEnding = false;
	bool bSeenAlive = false;
	bool bPreloaded = false;
	bool bClipTried = false;
	bool bMontageTried = false;
	EState State = EState::Alive;
	double DeathTime = -1.0;
	double NextPackPoll = 0.0;
	int32 LastResetCount = -1;
	int32 DeathCount = 0;
	int32 ClipPlayCount = 0;
	int32 ClipRestartCount = 0;
	int32 RestartsThisDeath = 0;
	int32 PoseHoldCount = 0;
	int32 PhysicsOffCount = 0;
	int32 PackSetCount = 0;
	int32 PackMissCount = 0;
	bool bPoseHeld = false;
	/** True from the death edge when this component guards the pose (OwnClip with a clip that played, or PackMontage with bGuardPackDeath): physics kept off, the clip frozen (and restarted). */
	bool bGuardActive = false;
	FString LastPackResult;
	TWeakObjectPtr<UAnimMontage> ClipMontage;

	/** Where the pack's mesh sits on its parent (the capsule) while the boss lives. */
	bool bMeshPlacementKnown = false;
	TWeakObjectPtr<USceneComponent> MeshParent;
	FName MeshSocket;
	FVector MeshRelativeLocation = FVector::ZeroVector;
	FRotator MeshRelativeRotation = FRotator::ZeroRotator;

	UPROPERTY(Transient)
	TObjectPtr<UAnimSequence> LoadedClip;

	UPROPERTY(Transient)
	TObjectPtr<UAnimMontage> LoadedMontage;
};
