# Codex Brief 13: build selector (G3-5), a C++ UI feature

From Claude via the owner. Engineering, C++ allowed. Claude reviews every line, builds, writes the PIE driver and runs it. You cannot build or run the game. This brief starts after Brief 12 (its report is accepted; the three findings are fixed by Claude).

## 1. Goal
Today the player's build is the console variable `rpg.Build` (Starter, Strength, Dex; `Source/OneBossFight/Player/RPGBuildLoadout.h/.cpp`, `RPGBuildRules.h`). G3-5 (`Documentation/TASKS.md`) asks for a selector the player can reach in the game without a console: before the boss wakes (the encounter is dormant, `URPGBossEncounter::IsDormant()`), the player opens a small panel, sees the three builds with their one-line summary, picks one, and the loadout is applied exactly as `rpg.Build <name>` does it today. The art for a shrine does not exist yet, so the trigger is input based, not a placed actor.

## 2. Requirements
1. New files `Source/OneBossFight/UI/RPGBuildSelect.h/.cpp` (a player component `URPGBuildSelect`, plus a small widget or Slate panel; follow `UI/RPGBossHud.h/.cpp` and `UI/RPGBossHudWidget` for how this project draws UI, the Cinzel font and the colour style).
2. Open and close: the key `B` (raw key binding on the owning player controller's `InputComponent`, no change to the pack's input mapping assets, no `Config/` edit). The panel opens only while the boss encounter is dormant (before the fight) and the player is alive and on the ground; it closes by `B`, `Escape`, a pick, or when the boss wakes. While open, the game is NOT paused and the player cannot attack or roll (use the same quickslot/ability block mechanism `RPGBuildLoadout` uses for the weapon lock if it fits; if you need a new block, say so in the report instead of inventing one).
3. Content: three rows, keys `1`, `2`, `3` and mouse click, each with the build name and one line. Take the one-line text from `RPGBuildRules.h` or the HUD build line if it already exists (`pie_build_hud.py` checks it); do not invent new numbers in the text.
4. A pick calls the same C++ path as the console command (`RPGBuildLoadout`'s apply function) so that the weapon, the table rows and the HUD build line follow; the panel must not duplicate loadout logic. Picking the build already active does nothing but close.
5. Creation: one registration line in `Player/RPGPlayerMovesSubsystem.cpp` where the other player components are created (claim the file in `TEAM_MAILBOX.md` first; touch only that line and the include). Shipping behaviour: the selector stays (it is a game feature), but no debug code.
6. Testability for Claude's PIE driver (`Scripts/Editor/pie_build_select.py`, which Claude writes): UFUNCTION snake_case getters/setters `IsOpen`, `OpenForTest`, `CloseForTest`, `PickForTest(FName Build)`, `GetLastPickResult`, and the row texts as `GetRowText(int32)`. Declarations unconditional (UHT rejects UFUNCTION inside `#if`); do not put test hooks behind `#if`.
7. Pure logic (when to allow opening: dormant, alive, grounded, not in a transition; mapping key to build) in a header with no Unreal object (`UI/RPGBuildSelectRules.h`, like `Player/RPGBuildRules.h`) so Claude can write an automation test.

## 3. Rules
No commit or push; no git command that changes the working tree (about 240 uncommitted changes must survive); no editor, build or game run; never edit a pack asset; never delete and recreate a referenced asset; no secrets. Claim files in `Documentation/TEAM_MAILBOX.md` (append only). Match the surrounding comment density and naming. You cannot compile: re-read every edit twice and list in the report every symbol you used with its declaration file and line. Do not touch `RPGHitIntake`, `RPGBossEncounter`, `RPGBossBleed`, `RPGWeaponAttackTable`, `RPGDamageScale.h` (Claude is editing them) except to read.

## 4. Acceptance (Claude checks)
`Documentation/Codex/REPORT_13.md`: files changed, symbol table, design notes, what is not verified. Claude builds, writes `pie_build_select.py` and an automation test for the rules, and runs them. Tell the owner "Report 13 is ready".
