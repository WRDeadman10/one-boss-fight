# SPEC M3: Legend pass (TASKS G2-14, AU-1; DELTA_AUDIT AUD-01)

Written 2026-10-21 by a read-only research agent. CHECKPOINT DRAFT: all findings so far, design complete in outline, a few verifications still open (listed in section 8 as "unverified").
Line numbers are file-relative as read on 2026-10-21. Re-grep before editing: other milestones (M1, M2, M4) touch the same files.
Nothing under Source/, Content/, Config/, Scripts/ was changed by this research.

## 1. Goal and Freeze requirements

Goal: the presentation layer that makes the fight feel finished, with no gameplay change.
Five effects:
1. Camera shake on the boss's heavy slam impact (A2 overhead, A6 leap landing).
2. Camera shake on the phase-two roar.
3. Hit stop on the riposte hit.
4. Slow motion on the kill.
5. Music swap from the Phase 1 track to the Phase 2 track at the phase-two threshold, by crossfade.

Freeze (Documentation/Master_Design_Freeze_v1_2_AI_Implementation_Ready.md):
- Line 247: "Dynamic Audio: Hook URPGBossMusic to transition dynamically from Phase 1 battle theme to Phase 2 choral climax upon threshold trigger."
- Line 289: "Add camera shake on the boss's heavy slam impact and phase-transition roar."
- Line 311: orchestral battle music begins at first contact (already built, one track).
- Line 318: victory stinger (no sting asset exists; open question).
- Line 692: camera shake and audio must not substitute for a visible telegraph (A6). The shake is only an impact accent, never the only cue.
- Lines 765 to 771: transition is evaluated only while alive; after the transition "resume audio blend".
- Line 783 (18.2 item 6): on death "Fade or transition music ... without restarting combat music".
- Lines 448 and 801 (18.3): a reset restores "Audio state and music phase".
- Lines 885 to 896 (section 21): priority table; item 8 "Cosmetic feedback" is the lowest. Dead, reset and phase transition outrank every effect here.
- Lines 1263 to 1265 (32.2): every delayed callback must carry the encounter generation and drop itself when it changed.
- Line 28 (tenet 4): values are UPROPERTYs, never literals inside logic.
- Line 926: debug and logs must not be noisy in normal play.
- Line 1186 (30.1): do not treat a 0.05x play rate as an animation hold. Not related to hit stop (0.08 s), noted so nobody mixes them.
- TASKS.md:63 (G2-14, done when "U look review"), TASKS.md:91 (AU-1), TASKS.md:188, DELTA_AUDIT.md:103 (AUD-01 "Partial: fades one track in and out, Phase swap open").

## 2. Current state (verified by reading)

### Music
- `Source/OneBossFight/Audio/RPGBossMusic.h`: one `Music` (line 30), `Volume` 0.55 (33), `FadeInSeconds` 2.5 (36), `FadeOutSeconds` 4.0 (39), `IsPlaying()` returns `bPlaying` (42), one `Player` audio component (46), `bPlaying` (51).
- `RPGBossMusic.cpp`: tick interval 0.25 s (13). `Start()` (31): returns if no `Music` or already playing; creates the component once with `UGameplayStatics::CreateSound2D(..., bPersistAcrossLevelTransition=false, bAutoDestroy=false)` (39) and calls `FadeIn` (43). `Stop()` (48) calls `FadeOut(FadeOutSeconds, 0)` (52). `TickComponent` (57): starts when `!Encounter->IsDormant()` and health > 0 (71 to 72), else stops. `EndPlay` stops the component hard.
- Under `-nosound` `CreateSound2D` returns null (engine GameplayStatics.cpp:1640, `GEngine->UseSound()`), the code guards it, state flags still change. Consequence: PIE drivers can test music LOGIC only, never audibility.
- Attached by `URPGPlayerMovesSubsystem::Attach` (RPGPlayerMovesSubsystem.cpp:129 to 135) with the placeholder `/Game/StarterContent/Audio/Starter_Music_Cue` (133).
- `Tests/RPGAutomationTests.cpp` PackWiring test lists `Starter_Music_Cue` as a required asset (about line 473).
- Files exist, git-ignored (`.gitignore:130 Import/Audio/`), not imported: `Import/Audio/MX_Boss01_Phase1.wav|ogg`, `MX_Boss01_Phase2.wav|ogg`, `SOURCES.txt`.
  Measured today (read-only, python wave module): Phase1 WAV 48000 Hz, 16 bit, stereo, 171.49 s, RMS -19.0 dBFS, peak -1.6 dBFS. Phase2 WAV 48000 Hz, 16 bit, stereo, 271.62 s, RMS -14.3 dBFS, peak 0.0 dBFS.
  Phase 2 is 4.7 dB louder than Phase 1 on average, so it needs a lower volume to sit right.
  Phase 2 per-second RMS: about -24 to -20 dBFS from 0 to 36 s (quiet intro), -16 to -14 dBFS from 37 s on (the climax). Phase 1 is steady at -16 to -21 dBFS.
  Both tracks end in a fade to silence (last 3 s: Phase1 -34, -58, -83 dBFS; Phase2 -54, -99, -130 dBFS). A looping file therefore dips to silence once per loop.
  File sizes: WAV 33 MB and 52 MB, OGG 3.9 MB and 6.6 MB. `.gitattributes` sends `*.uasset` to Git LFS. An imported WAV would store its source PCM in the .uasset (about 85 MB); an OGG import stores the OGG (about 10 MB). Prefer OGG (open question 1).
- Engine: `USoundFactory` accepts wav always and ogg when `WITH_SNDFILE_IO` (Engine/Source/Editor/AudioEditor/Private/Factories/SoundFactory.cpp:148 to 157). Whether OGG import works in this editor is unverified.

### Phases, stagger, tracker, HUD (the event sources)
- Phase two: `URPGBossPhases::TickComponent` starts the transition when `Health/Max <= PhaseTwoHealthFraction (0.6)` and not staggered (RPGBossPhases.cpp:103). `StartTransition` (157): `bPhaseTwo = true` (160), `++PhaseTwoCount` (162), plays `Ability_R_Intro_Anim_Montage` (194, 1.53 s clip per DELTA_AUDIT section 1), holds behaviour. `FinishTransition` (201) after `TransitionSeconds` 1.8 s (RPGBossPhases.h:33); it returns early on death (no buffs). `ResetPhases` (397) clears `bPhaseTwo` (416) but never resets `PhaseTwoCount`, so the counter is monotonic. Getters: `IsPhaseTwo` (h:83), `IsInTransition` (h:86), `GetPhaseTwoCount` (h:92).
- Riposte: `URPGBossStagger::ApplyCritical` (RPGBossStagger.cpp:323). The riposte branch (349 to 361) multiplies the one hit that follows an accepted press, sets `bRiposteUsed` (355) and does `++RiposteCount` (357). `RiposteCount` is never reset, so it is monotonic. `GetRiposteCount` (h:71). The synchronized riposte clips (G2-7) are not built; today the hit is the pack's normal attack, detected by the health drop. When G2-7 lands, the same branch must still be the single place that counts the riposte hit.
- Slam: `URPGAttackTracker` (RPGAttackTracker.cpp): A2 = GS_ChargedAttack, commit 1.68 s, active 1.93 to 2.11 s (28 to 30), the damaging window per the comment at 22 to 24. A6 = GS_LeapAttack, commit 0.16 s, active 0.75 to 1.17 s (63 to 65), the landing and central hit. Phase machine at 372 to 381: Committed -> Active at `ActiveStartTime`, Active/Committed -> Recovery at `ActiveEndTime`. If one tick spans the whole active window, Active is skipped (Committed jumps to Recovery). Accessors: `GetCurrentMove` (h:136), `IsActiveWindow` (h:143), `GetAttackInstance` (h:133, goes down again on a vetoed start, lines 313 and 332).
- `URPGBossShockwave` already launches the A6 wave once per attack instance with this exact condition (RPGBossShockwave.cpp:148 to 151: move == A6, `IsActiveWindow()`, instance != `LastInstance`). It is the pattern to copy.
- Victory: `URPGBossHud` fires `OnVictory` once per generation (RPGBossHud.cpp:414 to 433; `VictoryFiredGeneration`), disables player input (425), `GetVictoryCount()` (h:167, monotonic). HUD banners, retry delay (3 s) and the retry line use `GetRealTimeSeconds()` (cpp:125, 137, 147, 163, 364), so they already ignore time dilation. Retry reloads the level with `UGameplayStatics::OpenLevel` (cpp:202).
- Encounter: `URPGBossEncounter::ResetEncounter` (RPGBossEncounter.cpp:222) does `++Generation` (226), detection of a new player pawn at 93, ends with `Sleep()` (293). `GetGeneration()` (h:49), `IsDormant()` (h:39).
- Camera: `URPGCameraRig` (Player/RPGCameraRig.*) keeps the spring arm probe at 34 cm (h:33), collision on, boom on the capsule, tick group `TG_PrePhysics` (cpp:21). Camera shakes are applied by the camera manager AFTER the view target (PlayerCameraManager.cpp:455 `ApplyCameraModifiers`), so a shake can push the lens past the spring arm collision result. Keep the location amplitude well below the probe radius (see design).
- The project has NO camera shake class, no time dilation code (git history only: commit 53e88d0 had `CustomTimeDilation` hit stop and `SetGlobalTimeDilation` slow mo in the retired C++ combat, DECISIONS.md:84 and 85, "0.05 for 0.08 real s" and "world 0.25 for 2.5 real s"; that code is gone).
- The pack: `Content/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/CameraShakes/RegularAttackCameraShake.uasset` and `AdvancedCombatFramework/CameraSystem/AnimNotifies/PlayCameraShakeAN.uasset` exist (light-hit shakes used by impact cues). None of the boss GS_* montages or `Ability_R_Intro_Anim_Montage` references a camera shake (binary string search, 2026-10-21). The pack never calls `SetGlobalTimeDilation` (string search found none). `CustomTimeDilation` appears in the name tables of `BP_AdvancedAbilitySystemComponent` and `AE_FlameBlast` only; usage unverified (two read-only bridge queries of ASC graphs showed no use; likely cue actors copying the owner's dilation).

### Engine API (UE 5.5, verified in C:/Program Files/Epic Games/UE_5.5/Engine)
- `UGameplayStatics::GetGlobalTimeDilation` / `SetGlobalTimeDilation` (Source/Runtime/Engine/Classes/Kismet/GameplayStatics.h:387, 394). Implementation clamps to `AWorldSettings::MinGlobalTimeDilation` / `MaxGlobalTimeDilation` (WorldSettings.cpp:320 to 324). `TimeDilation` is `transient` (WorldSettings.h:694), so a new world starts at 1.
- `AActor::CustomTimeDilation` (Actor.h:716 to 718). Component ticks use the owner's value (Actor.h:4725, `ExecuteTickHelper`). World time passes: `UWorld::GetTimeSeconds` is dilated, `GetRealTimeSeconds` is not (World.h:2502 to 2516; LevelTick.cpp:1337 to 1346). Audio runs in real time regardless of dilation (LevelTick.cpp:1340 comment).
- Camera shake: `UCameraShakeBase` is Abstract (CameraShakeBase.h:446 to 447), `bSingleInstance` (540), `SetRootShakePattern` (552), `ChangeRootShakePattern<T>()` (555). `UDefaultCameraShakeBase` (plugin EngineCameras, ENGINECAMERAS_API) shows how a concrete shake picks its pattern: `Super(ObjInit.SetDefaultSubobjectClass<UPerlinNoiseCameraShakePattern>(TEXT("RootShakePattern")))` (DefaultCameraShakeBase.cpp:9 to 12; base constructor CameraShakeBase.cpp:23 to 38).
  Patterns (plugin `Engine/Plugins/Cameras/EngineCameras`, module `EngineCameras`, EnabledByDefault true): `UWaveOscillatorCameraShakePattern` (WaveOscillatorCameraShakePattern.h:54) with `FWaveOscillator {Amplitude, Frequency, InitialOffsetType}` (20 to 35) for X, Y, Z, Pitch, Yaw, Roll, FOV plus Location/Rotation amplitude and frequency multipliers; `UPerlinNoiseCameraShakePattern` (PerlinNoiseCameraShakePattern.h:36) with `FPerlinNoiseShaker {Amplitude, Frequency}`. Both derive from `USimpleCameraShakePattern` with `Duration`, `BlendInTime`, `BlendOutTime` (SimpleCameraShakePattern.h:24, 28, 32). Both default to location only (rotation multiplier 0, constructor in the .cpp).
  The oscillator offset is `Frequency * 2*PI` per second (WaveOscillatorCameraShakePattern.cpp:19 to 26), so `Frequency` is in Hz. Blend in and out are linear weights (CameraShakeBase.cpp, `FCameraShakeState::Update`).
- Play: `APlayerCameraManager::StartCameraShake(TSubclassOf<UCameraShakeBase>, const FAddCameraShakeParams&)` (PlayerCameraManager.cpp:1261 to 1267) returns the instance, or null when there is no `UCameraModifier_CameraShake` (cached at 661). `FAddCameraShakeParams {Scale, PlaySpace, UserPlaySpaceRot, SourceComponent, Initializer, DurationOverride}` (CameraModifier_CameraShake.h:104 to 128). A custom `Initializer` makes the instance non-recycled; with `bSingleInstance` an existing instance of the same class is stopped and replaced when either is custom initialized (CameraModifier_CameraShake.cpp:231 to 262), otherwise restarted in place. Either way shakes of one class never stack.
  `UGameplayStatics::PlayWorldCameraShake(World, Shake, Epicenter, Inner, Outer, Falloff, bOrient)` (GameplayStatics.h:520) scales by `CalcRadialShakeScale` (PlayerCameraManager.cpp:1311 to 1328): `scale = (1 - clamp((dist - Inner)/(Outer - Inner), 0, 1)) ^ Falloff`, `dist` measured from the CAMERA location, and calls `ClientStartCameraShake` even when the scale is 0 (1331 to 1351). `CalcRadialShakeScale` is protected, so the project reimplements the formula (pure function, testable).
  `StopAllInstancesOfCameraShake(Class, bImmediately)` and `StopAllCameraShakes` exist on the manager (PlayerCameraManager.h:~845 to 850). `UCameraModifier_CameraShake::GetActiveCameraShakes` (CameraModifier_CameraShake.h:163) lists active shakes (tests).
- Audio: `UAudioComponent::FadeIn(Duration, Level, StartTime, EAudioFaderCurve)` (AudioComponent.h:493), `FadeOut(Duration, Level, Curve)` (504), curves Linear, Logarithmic, SCurve, Sin (equal power) (111 to 126). A fade out to level 0 stops the sound at the end (AudioComponent.cpp:938 to 1010). `FadeIn` on a component that is already active restarts the sound (PlayInternal stops a looping active sound, AudioComponent.cpp:656 to 667), so there is never a second voice on one component.
- `USoundWave::bLooping` (SoundWave.h:464), `SoundGroup` (460).

## 3. Gaps
G1. No camera shake class, no shake trigger. Shake must be distance scaled and must never stack or leave residue.
G2. No hit stop, no slow motion, no owner that guarantees time is restored.
G3. `URPGBossMusic` plays one track; no phase swap, no crossfade, no loop, no per-track volume; the real tracks are not imported; the victory fade can be cut by the pack destroying the boss (about 3.5 s after death per HANDOVER.md section 4, unverified in code) before the 4 s fade ends.
G4. Nothing switches the layer off for the timing-based PIE drivers.
G5. No counters to prove "once per event" for any of this.
G6. Reset checklist item "audio state and music phase" (Freeze 801) is open (TASKS G2-10: "Open: HUD, audio state").

## 4. Design

### 4.1 Shape
No pack file changes. No change to the meaning of any existing component. Additions:
- `Source/OneBossFight/Player/RPGCameraShakes.h/.cpp` (new): `FRPGShakeSettings`, `URPGSlamCameraShake`, `URPGRoarCameraShake`, `RPGLegend::ShakeScale(...)`.
- `Source/OneBossFight/Player/RPGLegend.h/.cpp` (new): `FRPGDilationScope` (pure), `URPGLegendSubsystem` (world subsystem), `URPGBossLegend` (boss component).
- `Audio/RPGBossMusic.h/.cpp` (changed): two tracks, crossfade, state machine, counters.
- `Player/RPGAttackTracker.h` (one accessor added), `Player/RPGPlayerMovesSubsystem.cpp` (attach the component, load the music assets), `OneBossFight.Build.cs` and `OneBossFight.uproject` (EngineCameras).
- `Scripts/Editor/import_audio.py`, `legend_off.py`, `pie_legend.py` (new).

### 4.2 Console variables and enable switches
In RPGLegend.cpp (house style like `rpg.Debug` at RPGCombatDebug.cpp:31):
- `rpg.Legend` int, default 1, 0 or 1. 0 = hit stop, slow motion, camera shake and the music SWAP are suppressed (counted as suppressed, never started). Music itself (start and stop with the encounter) is NOT affected, so the old drivers still see the old music behaviour. Setting it to 0 while an effect runs cancels that effect at the next tick (restores time at once).
- `rpg.LegendShakeScale` float, default 1.0 (0 to 1): global multiplier of every shake, for accessibility and for U to tune without a build.
- `URPGBossLegend::bEnabled` (EditAnywhere, default true): per boss switch, ANDed with the cvar.
- The cvar is process-wide in the editor: it survives PIE sessions. Existing drivers are switched off once per editor start by `Scripts/Editor/legend_off.py` (`rpg.Legend 0`), added to the editor-start routine (HANDOVER section 4, PROJECT_STATE) next to `no_throttle.py`; `Scripts/RunDrivers.ps1` (M5) and `Scripts/Rebuild.ps1` relaunch must do the same. `pie_legend.py` sets `rpg.Legend 1` at its start and ALWAYS sets it back to 0 in its finish and error paths. Whether `-ExecCmds="rpg.Legend 0"` on the editor command line is honoured in the editor is unverified (open question 6).

### 4.3 Shake settings (all UPROPERTYs on `URPGBossLegend`, struct `FRPGShakeSettings`)
```
USTRUCT(BlueprintType) struct FRPGShakeSettings {
  float Duration;        // s
  float BlendIn;         // s
  float BlendOut;        // s
  FVector LocationAmplitude;   // cm, X Y Z
  FVector LocationFrequency;   // Hz
  FRotator RotationAmplitude;  // degrees, Pitch Yaw Roll
  FRotator RotationFrequency;  // Hz
  float InnerRadius;     // cm, full strength inside
  float OuterRadius;     // cm, zero strength outside
  float Falloff;         // exponent of the radial curve
};
```
Defaults (tunable; the reason is next to each; all unheard and unseen, U tunes):
Slam (A2, A6), property `Slam`:
- `Duration` 0.55, `BlendIn` 0.02, `BlendOut` 0.45. A thump: instant onset, linear decay. Short enough to be over before the recovery punish window starts.
- `LocationAmplitude` (0, 2, 5) cm, `LocationFrequency` (0, 11, 14) Hz. Vertical bump dominates. 5 cm is far under the 34 cm spring arm probe (RPGCameraRig.h:33), so the lens cannot reach a wall or the floor.
- `RotationAmplitude` (1.4, 0.6, 0.8) degrees pitch, yaw, roll; `RotationFrequency` (16, 12, 9) Hz. Rotation sells weight and does not move the lens.
- `InnerRadius` 500, `OuterRadius` 2500, `Falloff` 1.5 cm. The arena radius is 3000 cm (RPGGreyboxArena.h:43); A2 hits within about 330 cm of the boss (RPGAttackTracker.cpp:22 to 24); at 2500 cm and more the player feels nothing.
Roar (phase two), property `Roar`:
- `Duration` 1.5 (the clip is 1.53 s), `BlendIn` 0.25, `BlendOut` 0.5. A swelling rumble that ends with the roar.
- `LocationAmplitude` (1, 1.5, 2) cm at (17, 21, 24) Hz. A rumble, not a bump.
- `RotationAmplitude` (0.7, 0.5, 0.5) degrees at (19, 15, 13) Hz.
- `InnerRadius` 1500, `OuterRadius` 4500, `Falloff` 1.0. A roar is heard and felt across the arena.
Global: `GlobalShakeScale` 1.0 (multiplied with `rpg.LegendShakeScale`).
Shake classes: `URPGSlamCameraShake` and `URPGRoarCameraShake`, both `UCameraShakeBase` subclasses built like `UDefaultCameraShakeBase` but with `UWaveOscillatorCameraShakePattern` as the root pattern (`SetDefaultSubobjectClass`), `bSingleInstance = true`. The numbers are written into the pattern per play by an `FAddCameraShakeParams::Initializer` lambda that copies the component's `FRPGShakeSettings` (so every number lives in a UPROPERTY). Two distinct classes let a reset call `StopAllInstancesOfCameraShake(Class, true)` per effect and let tests list `GetActiveCameraShakes`.
Play: `APlayerController* PC = World->GetFirstPlayerController()` (local only; single player), `PC->PlayerCameraManager->StartCameraShake(Class, Params)` with `Params.Scale = Scale`, `PlaySpace = CameraLocal`. Scale = `RPGLegend::ShakeScale(Distance, Inner, Outer, Falloff) * GlobalShakeScale * cvar`, with `Distance` = horizontal-and-vertical distance from the epicenter to `PlayerCameraManager->GetCameraLocation()` (same as the engine). A scale below 0.02 starts nothing (counted as "too far").
Epicenter: the boss feet (actor location minus capsule half height), for the roar the boss location.
`RPGLegend::ShakeScale` is a pure free function (testable): `Outer <= Inner` gives a cliff (1 inside Inner, else 0); otherwise `pow(1 - clamp((D - Inner)/(Outer - Inner), 0, 1), Falloff)`.

### 4.4 Time effects: `URPGLegendSubsystem` (UWorldSubsystem, game worlds only, same `ShouldCreateSubsystem` rule as URPGPlayerMovesSubsystem.cpp)
Owns ALL time dilation. Nothing else in the project may call `SetGlobalTimeDilation` or write `CustomTimeDilation`.
- `FRPGDilationScope` (pure struct, no UObject, automation testable): fields `bActive`, `Saved`, `Applied`, `DeadlineReal` (double, `FPlatformTime::Seconds`), `Generation`. `Begin(Value, Now, Seconds, Saved)`: if inactive, store `Saved` and `Applied`; if active, DO NOT touch `Saved` (never capture an already dilated value) and set `DeadlineReal = max(old, Now + Seconds)`. `Expired(Now)`. `End()` returns the value to restore. Applied values are absolute (0.05, 0.25), never multiplied.
- Hit stop scope: two actors (`TWeakObjectPtr<AActor>` boss and player pawn), each with its own saved `CustomTimeDilation`. Apply `CustomTimeDilation = HitStopDilation` to both. Restore each to its saved value (log a warning when the current value is not the applied one: someone else changed it; restore anyway to the saved value, the guarantee wins).
- Slow motion scope: `GetGlobalTimeDilation` saved once, applied `SlowMotionScale`. Restore only if the current world value is still the applied one (nearly equal); if something else changed it (a console `slomo`), leave it and log.
- Real-time driver: one `FTSTicker` delegate, interval 0 (every frame), added only while a scope is active, removed when none is. Deadlines use `FPlatformTime::Seconds()`, never world time, so dilation cannot stretch them and a 30, 60 or 120 fps frame only delays the end by one frame. The ticker also checks every frame: (a) `rpg.Legend` is 0, (b) the registered encounter is gone or `GetGeneration()` differs from the request generation, (c) the world is tearing down. Any of these calls `CancelAll(reason)`.
- `CancelAll(reason)`: ends both scopes immediately, restores, removes the ticker, stops running shakes of both classes on the first player controller's camera manager, logs one line ("legend: cancelled (reason), hit stop %d slow motion %d") only when something was active.
- `Deinitialize()` (world teardown: PIE end, level reload by `OpenLevel`, editor quit) calls `CancelAll("world teardown")` and removes the ticker. Level reload also creates a new world whose `TimeDilation` is the default 1 (transient, WorldSettings.h:694).
- API (all return false and count a suppression when `rpg.Legend` is 0 or the pointer is stale): `RequestHitStop(AActor* A, AActor* B, float RealSeconds, float Dilation, const URPGBossEncounter* Enc, int32 Generation)`, `RequestSlowMotion(float Scale, float RealSeconds, const URPGBossEncounter*, int32 Generation)`, `CancelAll(const TCHAR*)`, getters `IsHitStopActive()`, `IsSlowMotionActive()`, `GetCancelCount()`, `GetRestoreCount()`.
- Priority (Freeze 21, item 8 is cosmetic): a request is refused when the encounter is dormant, the boss is dead (health <= 0) and the effect is not the kill slow motion, or the generation does not match. Hit stop is skipped when the riposte hit is lethal (the kill slow motion owns that moment; a ragdoll must never run while the animation is frozen).

### 4.5 Event detection and effects: `URPGBossLegend` (UActorComponent on the pack boss, added by `URPGPlayerMovesSubsystem::Attach` AFTER the Hud and Debug components, so lookups succeed; it also looks parts up lazily like URPGBossHud::FindParts)
Tick: every frame, `TickGroup = TG_PostUpdateWork` (after the tracker, phases, stagger and hud have ticked), cheap polls. Each event has an idempotency key; nothing fires twice per key even when polled for many frames.
1. Slam (A2, A6): key = tracker attack instance. Condition: `GetCurrentMove()` is `A2` or `A6` and `HasReachedActive()` (new accessor on `URPGAttackTracker`: true in phases Active and Recovery, so a frame hitch that skips Active cannot lose the event) and `GetAttackInstance() != LastSlamInstance`. Effects: slam shake. Counter `SlamCount` per move.
   A vetoed or interrupted attack never reaches Active, so it never fires (tests).
2. Roar: key = `Phases->GetPhaseTwoCount()` changed (set once per fight at `StartTransition`, RPGBossPhases.cpp:162; death during the roar does not undo it). Effects: roar shake (the music swap is the music component's own poll of `IsPhaseTwo()`, section 4.7). Counter `RoarCount`.
3. Riposte hit: key = `Stagger->GetRiposteCount()` changed (incremented at RPGBossStagger.cpp:357 in the stagger tick when the critical hit is applied; polled at most one frame later). Effect: hit stop on boss and player unless the boss health is <= 0 now. Counter `HitStopCount`. A normal hit during the stance break (no riposte) does not change the key, so no hit stop.
4. Kill: key = `Hud->GetVictoryCount()` changed (RPGBossHud.cpp:417; once per generation by the HUD's latch). Effect: slow motion. Counter `SlowMotionCount`. Also: stop the roar shake with blend out if it still runs (death priority, Freeze 18.2).
Generation: the component stores `LastGeneration`; when `Encounter->GetGeneration()` changes it calls `Subsystem->CancelAll("encounter reset")` once.
`EndPlay` (boss destroyed about 3.5 s after death, or PIE end) does nothing to running time scopes (the subsystem owns them); it only unregisters.
Test hooks (UFUNCTION(BlueprintCallable), "Tests: ..." doc comment like the existing hooks): `FireSlamForTest(FName Move)`, `FireRoarForTest()`, `FireHitStopForTest(bool bLethal)`, `FireSlowMotionForTest()`. They call the same internal handlers, obey the cvar and the generation rules, skip only the key check (so tests can fire twice in a row to prove no stacking).
Counters (BlueprintPure getters): `GetSlamShakeCount()`, `GetRoarShakeCount()`, `GetHitStopCount()`, `GetSlowMotionCount()`, `GetShakeTooFarCount()`, `GetSuppressedCount()`, `GetLastShakeScale()`, `GetLastShakeDistance()`.

### 4.6 Time-effect values (UPROPERTYs on `URPGBossLegend`)
- `HitStopSeconds` 0.08 (real seconds; Freeze range of the task 0.06 to 0.10): long enough to read as impact at 60 fps (five frames), short enough not to feel like a hitch.
- `HitStopDilation` 0.05 on the two combatants: nearly frozen but not zero, the same value the retired C++ combat used (DECISIONS.md:84); zero would stop animation notifies in the middle of an overlap.
- `SlowMotionScale` 0.25 global, `SlowMotionSeconds` 1.2 real seconds: the kill moment reads, and the victory banner (real-time) and the retry line (3 s real) are never delayed.
- `bSkipHitStopOnLethal` true.
- Minimum global dilation clamp: `AWorldSettings::MinGlobalTimeDilation` default is unverified (expected a tiny positive number, so 0.25 is fine); the code logs a warning when `SetGlobalTimeDilation` clamps (the call reports it).

### 4.7 Music: `URPGBossMusic` (changed)
Properties (EditAnywhere, BlueprintReadWrite, category "Music"):
- `Music` stays the Phase 1 track (name kept so existing code and the subsystem line stay valid). New: `PhaseTwoMusic` (USoundBase).
- `Volume` 0.55 stays (Phase 1). New `PhaseTwoVolume` 0.40: Phase 2 measures 4.7 dB louder (section 2); 0.40 / 0.55 is minus 2.8 dB, leaving the climax about 1.9 dB above Phase 1.
- `FadeInSeconds` 2.5, `FadeOutSeconds` 4.0 (reset and sleep) stay. New `VictoryFadeOutSeconds` 3.0: shorter than the roughly 3.5 s the pack waits before destroying the boss, so `EndPlay` does not cut the fade (unverified delay, see risks).
- New `CrossfadeSeconds` 2.0, curve `EAudioFaderCurve::Sin` (equal power): the two tracks have different tempos (73 and 112 BPM per TASKS.md:91), a short overlap hides the beat clash under the roar.
- New `PhaseTwoStartOffsetSeconds` 0.0: Phase 2 begins quietly (about 37 s of -24 to -20 dBFS, measured); set about 37 to enter on the climax if the intro is not wanted (U decides by ear).
- New `bSwapAtPhaseTwo` true (also ANDed with `rpg.Legend`; with the cvar at 0 the Phase 1 track simply continues).
- `bLoop` handled on the assets (`bLooping` true on the imported waves).
State machine (private): `enum class ETrack : uint8 { None, Phase1, Phase2 }`, `ActiveTrack`, two audio components `PlayerPhase1`, `PlayerPhase2` (each created at most once, `CreateSound2D`, `bAutoDestroy=false`, null-guarded for `-nosound`).
Desired track each tick (interval 0.25 s kept): None when the encounter is dormant or the boss is dead; else Phase 2 when `Phases->IsPhaseTwo()` and `PhaseTwoMusic` is set and swapping is enabled; else Phase 1.
Transitions (each guarded by `ActiveTrack != Desired`, so a repeated poll cannot repeat it):
- None -> Phase1: `PlayerPhase1->FadeIn(FadeInSeconds, Volume)`; `++StartCount[Phase1]`.
- None -> Phase2 (a boss woken already in phase two): fade in Phase 2.
- Phase1 -> Phase2: `PlayerPhase1->FadeOut(CrossfadeSeconds, 0, Sin)`, `PlayerPhase2->FadeIn(CrossfadeSeconds, PhaseTwoVolume, PhaseTwoStartOffsetSeconds, Sin)`; `++SwapCount`, `++StartCount[Phase2]`.
- Any -> None: `FadeOut` of every track that is not stopped, `FadeOutSeconds` normally, `VictoryFadeOutSeconds` when the boss is dead.
- Phase2 -> Phase1 cannot happen except through None (reset), which restarts Phase 1.
`IsPlaying()` keeps meaning "a track is requested" (`ActiveTrack != None`). New getters: `GetActiveTrackName()` ("None", "Phase1", "Phase2"), `GetStartCount(int32 Track)`, `GetSwapCount()`, `GetStopCount()`, `IsAnyComponentPlaying()` (reads `UAudioComponent::IsPlaying()`, always false under -nosound).
Never double-start: one component per track, `Start` guarded by the state, a restart of a track that is still fading out is a deliberate restart of the same component (engine stops the looping voice first, AudioComponent.cpp:656 to 667), so at most one voice per track exists.
Never music after reset or victory: reset puts the encounter to sleep, the next tick maps to None and fades out; death maps to None; `EndPlay` stops both components hard.
Subsystem change (RPGPlayerMovesSubsystem.cpp:133): `Music->Music = LoadObject<USoundBase>(nullptr, "/Game/OneBossFight/Audio/MX_Boss01_Phase1...")` with a fallback to `Starter_Music_Cue` and a Warning log when missing; same for `PhaseTwoMusic` (no fallback: empty means no swap).

### 4.8 Import: `Scripts/Editor/import_audio.py` (house style of Scripts/Editor/import_boss01.py)
- Header docstring, log prefix `[ImportAudio]`, `proj = unreal.SystemLibrary.get_project_directory()`, `run(task)` helper using `unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks`.
- For each of `MX_Boss01_Phase1`, `MX_Boss01_Phase2`: `unreal.AssetImportTask()` with `filename = Import/Audio/<name>.ogg`, `destination_path = "/Game/OneBossFight/Audio"`, `destination_name = name`, `automated = True`, `replace_existing = True`, `replace_existing_settings = True`, `save = False`. If the OGG import returns no object, retry with the `.wav` and log it. Then `unreal.load_asset(...)`, set `looping = True` and `sound_group = unreal.SoundGroup.SOUNDGROUP_MUSIC` (python property names unverified, each in try/except with a log), `unreal.EditorAssetLibrary.save_loaded_asset(asset)` (an unsaved import is lost on editor restart, as the existing script notes), log `duration`, `num_channels`, `sample_rate`, the saved package size on disk, and `looping`.
- Idempotent: re-running replaces in place; never deletes an asset (other assets may reference it; KI-043).
- Run: `MSYS_NO_PATHCONV=1 python -I Scripts/run_in_editor.py Scripts/Editor/import_audio.py`.
- Assets are own content under `Content/OneBossFight/Audio/` (tracked, LFS); `Import/Audio/` stays ignored. `SOURCES.txt` stays beside the source files.

## 5. Edge cases and failure modes
| Case | Behaviour |
|---|---|
| Second hit stop request during the first | Same scope: `Saved` kept, deadline = max, absolute 0.05 (never 0.0025). Ends 0.08 s after the second request. |
| Second slow motion request during the first | Same: scale stays 0.25 (not 0.0625), restore target stays the value captured on the FIRST activation (1.0), never 0.25. |
| Hit stop and slow motion at once | Independent scopes (per actor vs global); lethal riposte skips hit stop, so this only happens in tests. Effective speed is the product; both restore independently. |
| Encounter reset (generation token) | `CancelAll` on the next frame (ticker or component poll): time restored, shakes stopped, counters kept, "cancelled" counter up. Events from the old generation are refused at request time. |
| Boss or player destroyed during hit stop | `TWeakObjectPtr` skip; restore the live one. |
| Boss dies during a hit stop | Hit stop ends on its deadline (0.08 s); kill slow motion is an independent request. Death priority: new hit stop requests are refused when health <= 0. |
| Boss dies during the roar | Roar shake is stopped with blend out; phase transition code already skips buffs (RPGBossPhases.cpp:205 to 210). Music maps to None. |
| Player dies (generation +1 after respawn) | Reset path above. The player is dead during the effects only for a few frames. |
| Victory retry (level reload) during slow motion | World teardown: `Deinitialize` restores and removes the ticker; new world starts at dilation 1. Retry line appears after 3 s real, after the 1.2 s slow motion, so this only occurs when `SlowMotionSeconds` is raised (the test does that). |
| PIE end during an effect | `Deinitialize` restores; the PIE world is destroyed anyway; the next PIE starts at 1. |
| `rpg.Legend` set to 0 mid effect | Ticker sees it, `CancelAll("rpg.Legend 0")`. |
| `rpg.Legend` 0 | Nothing starts; suppressed counter goes up; time untouched; music swap off (Phase 1 continues). |
| Another writer changes global dilation (console `slomo`) | We restore only when the value is still ours; otherwise leave and log. |
| Frame rate 30, 60, 120 | Deadlines are real time; shake patterns are delta-time based. One frame of error at most. |
| Game paused | Real-time deadlines still run; effects end; nothing is left dilated. |
| A tick skips the whole A2 or A6 active window (hitch) | Fires from `HasReachedActive()` (Active or Recovery), once per instance. |
| Attack vetoed (stagger, transition, dormant) or interrupted before Active | Never fires (the instance counter goes back down on a veto; the key still only fires after Active). |
| Roar twice | Impossible by design (PhaseTwoCount increments once per fight until the next fight; reset then phase two again gives a new count, legitimate second fight). |
| Music: reset during the crossfade | Desired None; both fade out; no start of Phase 1 until the boss wakes again. |
| Music: boss wakes again within 4 s of a reset | Phase 1 restarts from the beginning on its own component; the old fade of Phase 2 may still be finishing (overlap of at most 4 s). Acceptable; noted. |
| Music: `-nosound` | No audio components; states and counters still correct; audibility is a hand test (AUD-02). |
| Music: tracks end (171 s and 271 s) | `bLooping` on the assets; each loop dips to silence for about 3 s (faded tails). Open question 3. |
| Music: boss destroyed 3.5 s after death | `VictoryFadeOutSeconds` 3.0 completes first; `EndPlay` stops any rest hard. |
| Shake: spring arm | Rotation-heavy; location 5 cm at most, under the 34 cm probe. Shake ignores the arm collision by design; amplitudes keep it safe. |
| Shake: no camera manager or no shake modifier | `StartCameraShake` returns null; counted as "not started", no crash. |
| Hit stop on the player with the camera | The spring arm ticks with the player's dilation: 0.08 s of arm lag freeze may be visible as a hitch. Feel check (hand test). |
| Dodge double tap window (0.30 s) | RPGDodgeTiming reads input times; hit stop does not dilate the world clock. Unverified which clock it uses; check before the PIE run (step 7). |

## 6. PIE test plan

### 6.1 Counters, read-backs and captures
- Counters per effect (section 4.5): fired once per event.
- Time dilation read back: `boss.get_editor_property("custom_time_dilation")` (Actor property is BlueprintReadWrite, so reflected; property name unverified in Python, fall back to `get_custom_time_dilation` style probing in the first step), `pawn...`, and `unreal.GameplayStatics.get_global_time_dilation(w)`.
- Shake capture: each tick sample `pc.player_camera_manager.get_camera_location()` and `get_camera_rotation()` (as pie_camera_scenarios.py line 43 does), player standing still, boss held. Metric: peak to peak (max minus min) of Z and pitch inside a window, because the oscillator start offset is random.
  Pass rule (derived from the UPROPERTYs at run time): during the shake window peak-to-peak Z >= 1.0 * `LocationAmplitude.Z` * scale (half of the theoretical 2 * A * scale, after the linear blend), pitch peak-to-peak >= 0.5 * `RotationAmplitude.Pitch` * scale; baseline window (2 s before, no shake) peak-to-peak Z <= 0.2 cm and pitch <= 0.1 degrees; recovery window (starts 1.0 s after the shake duration) <= the same baseline numbers.
- Frame captures for a human: `HighResShot 1280x720` 0.12 s after each slam, the roar peak (0.5 s into the roar), at the hit stop (first frame with dilation < 1), at the kill slow motion (0.3 s after the kill). Four pictures are looked at and named in the report. Shake itself is judged by feel (hand test).

### 6.2 Driver `Scripts/Editor/pie_legend.py` (log prefix `[Legend]`)
House style: `log`, `results`, `check(name, ok, detail)`, `S` state dict, STEPS list of `(delay_seconds, function)`, `_tick` with `register_slate_post_tick_callback`, `finish` unregisters the callback and ends PIE, final line `RESULT n/m passed`. Reads: `Scripts/Editor/pie_leap_wave.py` (steps, `parts`, `place`) and `pie_victory_lock.py` (input press helper, level reload check).
Start: `rpg.Legend 1` through `unreal.SystemLibrary.execute_console_command(w, ...)`. Every finish and error path executes `rpg.Legend 0`. Run after the warm-up PIE; the editor must have `legend_off.py` run for all other drivers.
Common setup: `enc.wake(); enc.hold_for_test(True); dbg.debug_refill_player()`, player placed with `place(pawn, boss, dist, ang)`, camera sampling started.

| ID | Scenario | Trials | Expected (numeric) |
|---|---|---|---|
| L0 | Gate off: `rpg.Legend 0`; fire `FireSlamForTest("A2")`, `FireRoarForTest`, `FireHitStopForTest(False)`, `FireSlowMotionForTest` | 1 each | all four counters +0; suppressed counter +4; global dilation == 1.0; both custom dilations == baseline; camera peak-to-peak Z <= 0.2 cm; music still follows the encounter (state not None after wake) |
| L1 | Real A2 slam with the player 600 cm away, 2.6 s after `start_move("A2")` | 5 | slam counter delta == exactly 1 per trial (5 of 5), total +5; `GetLastShakeScale` within 0.02 of `ShakeScale(dist)` (about 0.93); camera pass rule met in every trial |
| L1b | A2 interrupted before Active: `force_break_for_test` at 0.8 s after the start | 3 | slam counter delta 0 (3 of 3); camera peak-to-peak Z <= 0.2 cm |
| L1c | A2 with the player 2800 cm away (beyond Outer 2500) | 2 | slam fired is NOT counted as started: `GetShakeTooFarCount` +1 per trial, `GetSlamShakeCount` +0, camera peak-to-peak Z <= 0.2 cm |
| L1d | Distance scaling: player at 600 cm and at 1500 cm (A2) | 2 each | recorded scales equal the formula within 0.02 (0.93 and 0.30 for Inner 500, Outer 2500, Falloff 1.5); peak-to-peak Z ratio (1500 vs 600) in 0.15 to 0.55 |
| L2 | Phase two trigger by `debug_set_boss_health_fraction(0.5)` | 2 (second after a reset) | roar counter +1 per fight (never 2); camera pass rule (roar numbers) inside the 1.5 s; second `debug_set_boss_health_fraction(0.4)` in the same fight: roar counter +0, phase two count unchanged |
| L3 | A6 leap in phase two, player 600 cm away | 3 | slam counter +1 per leap (A6 stage active window opens at about 0.75 s); wave launch count also +1 (existing behaviour unchanged) |
| L4 | Riposte hit stop: `force_break_for_test`, player 110 cm in front facing the boss, injected Light Attack press (as `pie_riposte.py`) | 3 | hit stop counter +1 per trial; minimum `custom_time_dilation` read on boss and player == 0.05 (within 0.01); real duration below 1.0 measured by slate dt in 0.04 to 0.20 s (target 0.08); after: both exactly equal to the baseline read before (1.0); riposte count +1 |
| L4b | A second press in the same break (no riposte) | 3 | hit stop counter +0 |
| L4c | Lethal riposte (boss health set so the critical kills) | 1 | hit stop counter +0; slow motion counter +1 (kill) |
| L5 | No stacking, hit stop: `FireHitStopForTest(False)` twice, 20 ms apart | 5 | min dilation read >= 0.049 (never lower); total duration 0.08 + 0.02 = 0.10 s within +-0.06; restored exactly |
| L5b | No stacking, slow motion: `FireSlowMotionForTest` twice 100 ms apart | 3 | min global dilation == 0.25 (within 0.01, never 0.0625); total real duration 1.3 s within +-0.35; restored to exactly the value before the first call |
| L6 | Reset during hit stop and during slow motion (`enc.reset_for_test()` 0.03 s after the request, and 0.4 s after) | 3 each | global dilation and both custom dilations back to baseline within 0.15 s of the reset; cancel counter +1; generation +1 |
| L7 | Real kill: `debug_kill_boss()` | 1 | victory count 1; slow motion counter +1 exactly; min global dilation 0.25 (+-0.01); restored to 1.0 after 1.2 s real (+-0.35); music state None within 4 s; no component playing (when audio exists) |
| L8 | Victory retry during slow motion: set `slow_motion_seconds` = 8, kill, press R when the retry line shows (3.1 s) | 1 | new world global dilation == 1.0; new boss Dormant; new component counters all 0; old world teardown logged ("world teardown") |
| L9 | PIE end during an effect: `FireSlowMotionForTest` with `slow_motion_seconds` = 8, `editor_request_end_play()` | 1 | log line "legend: cancelled (world teardown)" present (read `Saved/Logs/OneBossFight.log`); the next PIE starts at global dilation 1.0 |
| M1 | Music wake: `enc.wake()` | 3 (wake, reset, wake again) | state "Phase1" within 0.5 s; `GetStartCount(Phase1)` delta == 1 per wake (never 2) |
| M2 | Music swap at phase two | 2 | state "Phase2" within 0.5 s of `IsPhaseTwo()`; swap count +1 per fight; second health drop in the same fight: swap count +0; start count Phase2 +1 |
| M3 | Music after reset | 3 | state "None" within 0.5 s of the reset; `IsAnyComponentPlaying` false after `FadeOutSeconds` + 0.5 s (when audio exists; skipped with a log line under -nosound) |
| M4 | Reset during the crossfade (0.5 s after phase two) | 2 | state "None"; no later start without a wake; start counts unchanged |
| M5 | Music after the kill | 1 | state "None" within 1 s; stop count +1 |
| M6 | Double start guard: `StartForTest` hook twice in a row on the music component | 3 | start count delta == 1 |
| M7 | cvar 0 with phase two | 1 | swap count +0; state stays "Phase1" |
| X1 | Regression: all existing drivers pass with `rpg.Legend 0` (listed in MILESTONE_GATE2_CODE.md regression section) | 1 run | same counts as before |
Total: about 50 checks. The driver prints `RESULT n/m passed`.

### 6.3 Automation tests (`Tests/RPGAutomationTests.cpp`, `OneBossFight.Legend.*`)
- `Legend.ShakeScale`: D=0, D=Inner, D=mid, D=Outer, D>Outer, Falloff 1 and 2, Outer<=Inner cliff.
- `Legend.DilationScope`: begin, second begin keeps `Saved`, deadline max, expiry, never stores an applied value as saved, 20 random begin/end sequences end restored.
- `Legend.Defaults`: `HitStopSeconds` in [0.06, 0.10], `SlowMotionScale` 0.25, `SlowMotionSeconds` 1.2, `CrossfadeSeconds` > 0, music assets exist (once imported).
- PackWiring test: add the two music asset paths (after the import step; before it, a Warning only).

### 6.4 What only a human can judge (hand test row LEG-02, owner U)
Feel of the shake amplitude and decay (comfort, nausea), the weight of the hit stop at 0.08 s, the kill slow motion, the music swap and crossfade by ear (also AUD-02, KI-061), the loop dip at the end of a track, whether the roar shake lines up with the roar pose, the camera hitch during the player's hit stop, and the Phase 2 start offset. U may tune `rpg.LegendShakeScale` and the UPROPERTYs from the editor without a build.

## 7. Ordered implementation steps (each leaves the project building)
1. Build.cs: add `"EngineCameras"` to `PrivateDependencyModuleNames`; `.uproject`: add `{"Name": "EngineCameras", "Enabled": true}`. New `Player/RPGCameraShakes.h/.cpp` (struct, two shake classes, `RPGLegend::ShakeScale`). Automation test `Legend.ShakeScale`. Build with `Scripts/Rebuild.ps1 -Tests`.
2. New `Player/RPGLegend.h/.cpp` part 1: `FRPGDilationScope`, `URPGLegendSubsystem` (cvars, ticker, requests, `CancelAll`, `Deinitialize`). Automation test `Legend.DilationScope`. Build.
3. `URPGAttackTracker::HasReachedActive()` accessor. `URPGBossLegend` component (polls, effects, counters, test hooks) and its attach line in `URPGPlayerMovesSubsystem::Attach`. `Legend.Defaults` test. Build.
4. `Scripts/Editor/legend_off.py`; update the editor-start routine in HANDOVER.md section 4 and PROJECT_STATE.md. Run the quick regression subset with the cvar at 0 (pie_a5_heal_punish 31, pie_leap_wave 17, pie_riposte, pie_phase_reset 14, pie_boss_hud 29, pie_victory_lock 9) to prove the layer is inert when off.
5. `Scripts/Editor/import_audio.py`; run it in the editor; read the log (duration 171.49 and 271.62 s, looping true, saved). If OGG fails, WAV fallback is used and the size is noted in KNOWN_ISSUES.
6. `URPGBossMusic` rewrite (two tracks, state machine, crossfade, counters, test hook `StartForTest`), subsystem music asset paths with fallback, PackWiring test paths. Build.
7. `Scripts/Editor/pie_legend.py` (first the L0 to L2 and M1 to M3 blocks, then the rest); check the clock used by RPGDodgeTiming before L4. Capture the four pictures and look at them.
8. Full regression (MILESTONE_GATE2_CODE.md list) with `rpg.Legend 0`, then `pie_legend.py`, then `Scripts/Rebuild.ps1 -Tests`.
9. Docs (section 9). Leave the editor open, PIE ended, `rpg.Legend` at 0 for the next session.

## 8. Risks and open questions

Risks:
- R1. `EngineCameras` module dependency: plugin is EnabledByDefault (EngineCameras.uplugin) but not listed in the .uproject; adding it explicitly is the intended fix. The build is the proof (unverified).
- R2. OGG import through the editor script (WITH_SNDFILE_IO) is unverified; WAV fallback costs about 85 MB of LFS.
- R3. Camera shake after the spring arm result can reach geometry only if amplitudes are raised above about 25 cm; the defaults are 5 cm.
- R4. Player `CustomTimeDilation` also slows the spring arm and the character movement for 0.08 s (visible hitch risk). Pack abilities using latent delays run on world time and may drift by up to 0.08 s against the frozen montage (iFrames are montage notify states, so they freeze with the clip).
- R5. The pack's use of `CustomTimeDilation` (name table of the ability system component) is unverified; if the pack copies the owner's dilation to cue actors, impact cues spawn slowed for 0.08 s, harmless.
- R6. `HANDOVER.md` says the pack destroys the boss about 3.5 s after death; the number is a note, not read from the pack. `VictoryFadeOutSeconds` 3.0 is chosen with margin; `EndPlay` hard stop is the net.
- R7. Other milestones edit the tracker, phases, stagger and HUD files; the hooks here are polls plus one accessor, to keep merge conflicts small.
- R8. Music tails fade to silence; loops dip.
- R9. Old drivers fail confusingly if `legend_off.py` was not run after an editor start. Mitigation: the first step of every future driver template and `RunDrivers.ps1` set the cvar.

Unverified (could not be verified in this research):
- Whether the roar clip has its loudest moment at the start or later (the shake uses a 0.25 s ramp, so it does not depend on this).
- Python property names for `custom_time_dilation`, `looping`, `sound_group` on the engine objects.
- That `-ExecCmds="rpg.Legend 0"` works on the editor command line.
- `MinGlobalTimeDilation` default value in this project.
- Exact clock used by RPGDodgeTiming.
- Pack boss destroy delay.
- Real feel of every default value.

Open questions for the owner:
1. Import OGG (small, about 10 MB of LFS) or WAV (lossless, about 85 MB)? Default in the script: OGG.
2. Crossfade 2.0 s (default) or a duck and cut under the roar? Decided by ear.
3. Loop tails: accept the 3 s dip, or trim the tails offline?
4. Victory stinger (Freeze 318): no asset exists; delivered later by AG or skipped?
5. Start Phase 2 at 0 s (quiet intro) or at about 37 s (climax)?
6. Should the editor launch (Rebuild.ps1) pass `-ExecCmds="rpg.Legend 0"` so the drivers are safe by default?
7. Accessibility cvar `rpg.LegendShakeScale` kept as a public setting?

## 9. Docs to update
- TASKS.md: G2-14 to Built or Verified with the driver result; AU-1 (files imported, candidates still unapproved); AU-3 and G2-10 note (audio state reset done).
- DECISIONS.md: "Legend pass" section with every default and reason, the ownership rule (only the legend subsystem dilates time), the cvar policy, the music state machine.
- KNOWN_ISSUES.md: new KI-071 (music tails dip, nothing heard yet, shake and hit stop unfelt), update KI-061.
- TEST_PLAN.md: LEG-01 (`pie_legend.py`), LEG-02 (U hand test), AUD-04 (music swap logic), AUT rows for the three automation tests; update AUD-03 with the two new assets.
- DELTA_AUDIT.md: AUD-01 row to Verified, a line in section 4 registry for the new values.
- PROJECT_STATE.md and HANDOVER.md: file layout (Player/RPGLegend, RPGCameraShakes, Audio), editor-start routine (`legend_off.py`), regression list.
- MILESTONE_GATE2_CODE.md: M3 row to Done with the driver count; regression note about `rpg.Legend 0`.
- ASSET_LICENSES.md: two music rows (credits from Import/Audio/SOURCES.txt).
- Freeze deviations: none expected.

STATUS: IMPLEMENTED 2026-10-21 (code, `pie_legend.py` 22/22, 3 automation tests). Deviations from this draft, all recorded in DECISIONS "Legend pass (M3)":
- The shake distance is camera to the boss's feet and the camera sits about 380 cm behind the player: scale 0.66 at a player distance of 600 cm (the draft said 0.93), 0.17 at 1500 cm.
- The camera proof is a high-pass measure (deviation from the line between neighbouring samples), not peak to peak: the camera is never still (settling after a placement, following the boss).
- `EngineCameras` is a public module dependency (the draft said private); the music component keeps `Music` for Phase 1; no `StartForTest` for Phase 2.
- L8 (victory retry during slow motion) and L9 (PIE end during an effect) were not driven; a `cap` group takes the four pictures.
- Phase 1 was imported from the WAV (the OGG import returned nothing), Phase 2 from the OGG.
