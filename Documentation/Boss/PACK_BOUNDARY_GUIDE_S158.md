# Pack boundary guide (S158)

This map separates four evidence layers that often appear together in one fight. A source reference can show native logic; it cannot by itself prove a third-party Blueprint graph or an authored asset's contents in the loaded build.

| Layer | What belongs here | Example and evidence | What the evidence establishes |
|---|---|---|---|
| Native C++ | Rules, orchestration, state and framework proof actors implemented in this module | `ARPGFrameworkBossCharacter` initializes a resolved profile and owns native combat state (`RPGFrameworkBossCharacter.h:23-60`; `RPGFrameworkBossCharacter.cpp:57-80`) | The source implementation and its authority boundary, not that a map spawned it or that a particular profile asset loaded. |
| Reflected pack integration | Native adapters that inspect or call third-party reflected properties/functions, plus native components attached to pack actors | Reflection access validates reflected identities (`RPGPackReflect.h:12-72`); `URPGBossEncounter` is a native `UActorComponent` (`RPGBossEncounter.h:18-19`) | Adapter behavior and expected reflected contract. It does not prove the third-party graph's runtime response. |
| Blueprint behavior | Pack player/boss classes, controller graphs, combat-component behavior and animation/state-machine graphs | The subsystem identifies pack actors by Blueprint-generated class names (`RPGPlayerMovesSubsystem.cpp:83-105`) | The class-name route in C++ only. Graph logic, inheritance at runtime and actual pawn possession need Blueprint inspection or runtime evidence. |
| Authored assets | Profiles, move cards, montages, sounds, maps and other content references | The boss resolves its configured profile (`RPGFrameworkBossCharacter.cpp:57-80`); pack audio is loaded from explicit content paths (`RPGPlayerMovesSubsystem.cpp:142-156`) | The source-level path or load request. Confirming the asset exists, has expected authored values, was cooked, or loaded successfully requires asset inspection/readback or runtime/package evidence. |

## How to report a mixed claim

Name the layer for each behavior and keep its evidence attached. For example: “Native: the subsystem attempts to load the phase-one cue from this path (`RPGPlayerMovesSubsystem.cpp:145-156`). Asset: the referenced cue must be inspected/read back to verify its authored content. Runtime: a log or capture is needed to prove it played.” Avoid turning a native call site into a claim about a Blueprint graph or an asset's contents.

## Framework and pack boundary

The legacy attachment subsystem recognizes the pack's generated player and great-sword boss class names. The framework proof fixture instead spawns `ARPGFrameworkBossCharacter` natively (`RPGPlayerMovesSubsystem.cpp:83-105`; `RPGFrameworkProofFixture.cpp:87`). Keep those two boss implementations distinct in source summaries. A fixture profile can still target a pack player, so identify the actor whose behavior is being claimed before assigning the evidence layer (`RPGFrameworkRuntimeTests.cpp:24`).

## Evidence limits

Source and header lines below support implementation and declared class type. For Blueprint behavior use the actual Blueprint asset or runtime evidence. For authored values use asset readback or the generator/import source and its output evidence. For presence in a packaged build use cook/package reports. For behavior in a live run use retained logs/captures with the corresponding expected sheet. A hash establishes file identity, not behavior.
