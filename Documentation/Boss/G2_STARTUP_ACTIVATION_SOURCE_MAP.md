# G2 — Startup activation source map (post C-800 integration)

## Observed call order

`URPGPlayerMovesSubsystem` is a `UWorldSubsystem`. `PostInitialize()` installs `OnActorSpawned` (`Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:36-53`). At `OnWorldBeginPlay`, the subsystem probes chronology and checks the GameInstance selection store. With no selection it retains the original `Attach` loop; with a selection it builds the strict census/binding and calls `ActivateWorld`, failing closed without the legacy boss bundle on any refusal (`:57-113`). Later selected-mode pack participant spawns are observed by `OnActorSpawned`; after world BeginPlay they still fail closed, release the current activation and report `EncounterActivation.LateSpawnUnsupported` (`:157-203`). C-804 Step A adds timestamped lifecycle logs and a post-reset delegate only; it does not add rebind behavior. The DD30 PIE chronology evidence (`DD30ChronologyRun1/chronology_raw.log:1271-1275`) proves an initial pre-BeginPlay window only, not respawn order.

## Existing branch behavior

When no selection is present, the legacy `Attach` branch and its side effects remain unchanged. When a selection is present, the strict selection route removes only owned legacy boss components before activation, uses the transient binding/typed definitions, and on failure destroys the binding, disables the boss and preserves independent player-side setup. The current selected-route policy is interim: late same-world respawn fails closed; begun components may remain present but inactive when cleanup refuses (KI-182). These source facts are not runtime PIE proof.

The pack player branch currently attaches Footsteps, CameraRig, RiposteInput, DodgeTiming, PlayerParry, SwingTracker, HitIntake, BuildLoadout, BuildSelect, FlaskHud and IFrameMonitor. They are player-owned behaviors; whether each remains on the target in the first data-driven boss increment must be checked against the accepted typed component plan rather than removed as a side effect of boss fail-closed policy.

## Integration constraints

1. The initial selected data-path census and definition/selection resolution happen before any framework boss component attaches. A missing/ambiguous census or failed activation must not fall through to `AttachLegacyBossPrelude` or any member of `AttachLegacyBossBundle`.
2. Preserve only explicitly approved player-side behavior on the target. Review the target role's typed plans and avoid creating duplicate components already registered by the native activation batch.
3. On a successful activation, the activation lease must be owned by a subsystem whose teardown is on the game thread and releases only its own native registrations.
4. `OnActorSpawned` can execute after world BeginPlay; the startup compiler/census still rejects begun worlds (`RPGBossWorldInputCompiler.h:17-21`, `RPGEncounterSelectionSubsystem.cpp:72-119`). C-804 approved a native post-reset multicast on `URPGBossEncounter`; subscribers must use `AddUObject` and unbind in their subsystem `Deinitialize`. Before Step B rebind code, Claude measures spawn/reset/broadcast/release order in live pack PIE. Keep the current fail-closed behavior until that measured order is accepted.
5. This map is source-only analysis. C-800's opt-in integration does not authorize switching the production default, retiring legacy code, editing a map asset, or claiming activation runtime proof.

## C-800/C-804 implementation boundary

C-800 accepted typed selection, strict initial census, transient binding, opt-in selector, and no-fallback failure behavior. C-804 approves only instrumentation now: multicast after successful reset state update with new generation/reset count, plus timestamped spawn/reset/broadcast/binding-release tokens. Do not implement rebind until Claude measures the live ordering and gives the next step. G044 asset creation remains blocked on typed boss/player definition assets and a canonical manifest receipt.
