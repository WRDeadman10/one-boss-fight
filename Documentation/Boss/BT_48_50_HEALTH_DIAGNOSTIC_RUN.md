# BT-48..50 Health Diagnostic Run

Date: 2026-11-16 14:31 UTC
Lead: Codex; implementer: Antigravity

## Source review

Antigravity's A-1039 fix replaced zero-argument `FProperty::GetCPPType()` calls. The installed UE 5.5 header confirms `GetCPPType(FString*, uint32)`. Helper SHA-256: `49B414970CEFD4ADDACE2C6D48DE2E4B63CA14CBD235EFA83565A25B4DB8328A`. The fail-closed current-health gate remains finite and greater than zero; no health/style writes were added.

## Build and suite

C-1155 Development build: exit 0. DD27j suite: 573 started, 573 passed, 0 failed; manifest `cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec`. Run: `Saved/C1619RouteBuild/Run_20261116_142818_6ffa486f`. Five source hashes matched; both locks released.

## Smoke result

Run: `Saved/SevarogArenaRoute/Run_20261116_142947_460f96a6`. At retries 3–600 the log reported `hp=0 max_hp=1e+06 tag_bound=1 tag_param=AttributeTag style=None comp=BP_AttributesComponent_C`, output `Value`/`double`, flags `0x8001040000380`. The route refused at `PlayerHealthTimeout`; census was `BossCount=0 PlayerCount=1 CompetingPackBossCount=0`. The pack actor was suppressed before BeginPlay with no montage. No framework boss spawned, so route binding, live census acceptance, Sevarog health, HUD, production card, and boss-death criteria were not exercised.

Cleanup: `DefaultGame.ini` restored to SHA-256 `5DE691FCA4E0FA375F6F262FA6BA402FEFA7AB9A0B567AE2146E6823F69EDEC8`; Editor exited; both C-1155 locks released; no asset save, package, or commit.

## Interpretation and next step

`tag_bound=1` disproves the missing `AttributeTag` binding hypothesis for this run. Current health remains zero while style is None. `max_hp=1e+06` is a raw diagnostic and must not be treated as approved player tuning; a source comment elsewhere notes that a bare proof map can have the same 0/1,000,000 pair, but that is not proof of this arena's initialization cause. BT-51 asks Antigravity to trace the player attribute/style startup chain and recommend the smallest safe initialization fix, evidence-only. Do not write player health/style or rerun Smoke until the source path and decision are reviewed.

## Startup comparison lead (static, not yet confirmed for this arena)
The Smoke log identifies the active game class as `BP_AdvancedGameMode_C`. It proves the player is possessed and `AttributeTag` binds, while the style remains None and Health stays 0 through the 30-second wait. `RPGBuildLoadout.cpp` defines an empty `rpg.Build` as “no choice” and says no equip function is called; the active CVar value during this Smoke has not been read. Separately, `RPGFrameworkProofFixture.cpp` contains a KI-150 measured observation for its proof fixture: pack style transitions None→SwordCombatStyle at about 9.4 seconds and Health/Max reset to 100/120. That fixture observation does not establish expected behavior for the arena. BT-51 compares pawn/PlayerInfo/GameMode/loadout prerequisites without mutation.
