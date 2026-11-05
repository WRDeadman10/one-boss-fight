# M13 code notes (builds loadout, written 2026-10-22 by the third helper)

Status 2026-10-22 (owner's session): compiled, attached (`RPGPlayerMovesSubsystem.cpp`), run: `pie_builds.py` 103/103, 22 of 22 automation tests. Changes after the helper's version: the weapon slot byte and the update type bytes are read from the pack's enums (the weapon slot is the byte 1, Update = 1, Replace = 0: KI-089); the lock is the quickslot ability blocked on the ability system component, not `Set Equip Slot Disabled` (KI-090); the equip replaces the slot's weapon item and cycles back from the magic staff first (KI-091); an Unarmed player is a known style; a call that could not be made does not burn an attempt; `GetPackEnumReport()`, `GetWeaponSlotReport()`, `SetLockWeaponSlotForTest`; the hit intake takes the swing's kind and merges two blade hits of one frame (DECISIONS). The HUD hook of section 3 is in (`RPGBossHud`, `pie_build_hud.py` 8/8) and the hyperarmor windows of B4 are authored (`pie_build_hyperarmor.py` 20/20). Sections 5 and 6 below are the helper's original unknown list: answered by the probes except the keys (KI-092).

Status of the helper's version: written, NOT compiled, NOT attached, NOT run (rules of the helper: no editor, no build, no PIE while the regression gate runs; no existing file was edited). Plan: `M13_BUILDS_PLAN.md` (with the probe appendix), `M13_PACK_FUNCTIONS.txt` (real signatures), row M13 of `MILESTONE_GATE3_CODE.md`. After a session reset: read this file, add the attach lines (section 2), build, then follow section 6.

## 1. What was written (six new files)

| File | What it is |
|---|---|
| `Source/OneBossFight/Player/RPGBuildRules.h` | Pure header, no Unreal object. `enum class ERPGBuild { Starter, Strength, Dex }`; namespace `RPGBuildRules`: the table of builds (`Entry(build)`: console name, combat style key of the weapon table, item asset path, weapon actor class, weapon ability class, HUD word), `BuildOfStyle(style, out)` (SwordAndShield counts as Starter, Twinblade as Dex, anything else is off-build), `StyleMatchesBuild`, `Parse(text, out)` (Empty / Build / Invalid), `Decide(FDecideInput)` (Wait / Apply / Done / Defer / GiveUp), `IsVerifying`, `UpdateTypeForAttempt` (0, 1, 0, ...), `ShouldLockSlot`, `DescribeStyle`, `BuildLine` (the HUD text). |
| `Source/OneBossFight/Player/RPGBuildLoadout.h/.cpp` | `URPGBuildLoadout : UActorComponent` for the pack player. Console variable `rpg.Build` (string), poll every 0.1 s of the combat component's `CurrentCombatStyle`, the equip call, the slot lock, getters, counters, test hooks, `CheckPackSignatures`. |
| `Source/OneBossFight/Tests/RPGBuildTests.cpp` | Three automation tests: `OneBossFight.Build.Rules`, `OneBossFight.Build.Decide` (6400 combinations against the invariants), `OneBossFight.Build.Assets` (item and style assets exist, defaults of the component, the wiring check on null classes). |
| `Scripts/Editor/pie_builds.py` | PIE driver, log prefix `[Builds]`, ends with `RESULT n/m passed`. Expected `RESULT 103/103` (the count stays 103 when a scenario fails: skipped checks fail instead of vanishing). |
| `Documentation/M13_CODE_NOTES.md` | this file |

### How the loadout behaves

- **The choice** is the console variable `rpg.Build`: `rpg.Build Strength`, `rpg.Build Dex`, `rpg.Build Starter`; empty (`rpg.Build ""`, `none`, `off`) means no choice. Any case, quotes and spaces are ignored; `str`, `dexterity`, `sword` are accepted; anything else is logged once, counted (`GetInvalidRequestCount`) and ignored. The variable is process wide, so it survives a respawn (the new pawn's loadout reads it and applies it again) and a PIE session (plan risk R9: a value left in an editor session changes the next test run; `pie_builds.py` sets it empty at its start and at its end).
- **No choice = nothing is called.** With `rpg.Build` empty the loadout only reads the combat component's style and the boss's encounter; it calls no pack function and never locks the slot, so every older driver and the first minutes of the game are unchanged (guarded by B1). Choosing `Starter` explicitly equips the sword if something else is held.
- **Apply** (`Decide` says Apply): the pawn's `BP_EquipmentComponent_C.Update Equip Slot Item(EquipSlotType=11, NewItem, ItemIndex=ActiveItemIndex, UpdateType, Success?)`. `NewItem` is built by copying the weapon slot's active item struct (`CopyScriptStruct`, only when the parameter's struct type equals the slot's item struct type) and setting its `Item_*` object field to the build's weapon item loaded by path (`ToughSword`, `KwangSword`, `DualSteelSwords`). `UpdateType` is 0 on the first call, 1 on the second, 0 on the third (the order of `E_EquipUpdateType` was not read; Unequip is never sent). Everything is checked before the call (function, `NewItem` struct, `Item_` field and its class, the weapon slot); a missing piece is a counted failure with a reason, not a half-built call. The pack's own flow does the rest (actor, abilities, anim layer): the loadout never sets the style by hand.
- **When**: only while the boss sleeps (no boss counts as asleep), the pack has answered (style known, not Unarmed, equipment component present, `StartupDelaySeconds` = 1 s after BeginPlay), the player is alive and not in a montage, and the last call is older than `VerifySeconds` (4 s) without the style having changed. After `MaxAttempts` (3) calls the loadout gives up (`GiveUp`: logged once, `GetApplyFailureCount`, state Failed, line `- not equipped`); a new request or a new fight (encounter generation) starts the attempts again. A style change later still counts as success.
- **Defer**: a choice made while the boss is awake is held (`Deferred`, counted, line `- next fight`) and applied after the reset (or when the boss is gone).
- **Lock** (Q2): while a build is chosen and the boss is awake the loadout calls `Set Equip Slot Disabled(11, true)`; it unlocks when the boss sleeps, is gone, or the choice is cleared. The equip waits one poll after an unlock. A style change while the slot is locked is counted (`GetLockBreachCount`) and logged: the lock did not hold. No re-equip is done in the fight (calling the pack in a fight is not worth the risk; if the lock does not stop the pack's cycle, see section 5, point 4).
- **HUD truth rule**: `GetBuildLine()` names the weapon really held, e.g. `Build: Strength (Claymore)`, `Build: Starter (Sword)`, `Build: Dex (Dual Swords)`, `Build: Off-build (Polearm)`, `Build: Unknown` before the pack answers; suffix ` - equipping...` while waiting or applying, ` - next fight` when deferred, ` - not equipped` after giving up.
- **Failures** never crash: every pack name is looked up by reflection and checked; `GetWiringReport()` is `ok` or the list of missing names (checked once, when both pack components exist); every failure text is logged once per distinct text (`LogRPGBuild`) and kept in `GetLastResult()`; the last 32 events are in `GetEventLines()`.

### Test hooks (UFUNCTIONs, found with `comp(pawn, "RPGBuildLoadout")`; Python never sets a property: KI-083)
`set_build_for_test(name)` (sets the same console variable with the console's priority and polls at once: returns `Accepted`, `Deferred`, `Same`, `Cleared`, `Invalid`), `apply_now_for_test()` (poll now, returns the decision), `reset_counters_for_test()`, `set_apply_only_out_of_combat_for_test(bool)`. Getters: `get_build_name`, `get_chosen_build_name` (Starter when nothing is chosen), `has_choice`, `get_build_line`, `get_actual_style_name`, `get_state_name` (Idle, Waiting, Applying, Deferred, Failed), `get_last_result`, `get_apply_attempt_count` (calls of the pack, 0 while no build was chosen), `get_apply_success_count`, `get_apply_failure_count`, `get_deferred_count`, `get_invalid_request_count`, `get_lock_count`, `get_unlock_count`, `get_lock_breach_count`, `is_weapon_slot_locked` (read from the pack), `is_combat_enabled`, `get_equipped_actor_class_name` (the pack's active weapon actor), `has_weapon_ability_for_test(class)`, `get_wiring_report`, `get_event_lines`.

## 2. The two attach lines (owner, `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp`)

1. Include, next to the other player includes (after `#include "Player/RPGSwingTracker.h"`, line 8):
```cpp
#include "Player/RPGBuildLoadout.h"
```
2. In `URPGPlayerMovesSubsystem::Attach`, after the `URPGHitIntake` block (line 175 to 178), same guard as the swing tracker:
```cpp
	if (IsPackPlayer(Pawn) && !Pawn->FindComponentByClass<URPGBuildLoadout>())
	{
		NewObject<URPGBuildLoadout>(Pawn, TEXT("RPGBuildLoadout"))->RegisterComponent(); // the weapon of the chosen build before the fight, the weapon slot locked in it (Gate 3, M13)
	}
```
Nothing else needs to change for the build to work (no `OneBossFight.Build.cs` change: only Core, CoreUObject and Engine are used; the new .cpp files are picked up by the module).

## 3. The HUD hook (owner, optional for the driver, needed for the build line on screen)

Read of `UI/RPGBossHud.h/.cpp`: the boss HUD widget `URPGBossHudWidget` builds its tree in C++ (`RebuildWidget`, `AddText`), `URPGBossHud::TickComponent` (on the boss) fills an `FRPGBossHudState` and calls `Widget->Apply(Hud)` (line 450 to 474); the widget exists while the boss sleeps. The line goes into this widget, top centre (the pack's `MainHUD` owns top left, top right and bottom left; our bar owns bottom centre), so five additive edits:

1. `RPGBossHud.h`, `struct FRPGBossHudState`: add `FText BuildLine;` and `bool bShowBuild = false;`.
2. `RPGBossHud.h`, class `URPGBossHudWidget`, next to `BannerTextBlock`: `UPROPERTY(Transient) TObjectPtr<UTextBlock> BuildTextBlock;` (and, optional, test accessors `IsBuildLineShown()` / `GetBuildLineText()` like `IsBarShown()`).
3. `RPGBossHud.cpp`, `RebuildWidget`, after the `RetryTextBlock` line (line 100), and add it to the `Hidden` list of the loop below:
```cpp
BuildTextBlock = AddText(Canvas, TEXT("BuildLine"), FVector2D(0.5f, 0.f), FVector2D(0.5f, 0.f), FVector2D(0.f, 18.f), 18, FLinearColor(0.93f, 0.8f, 0.45f));
```
4. `RPGBossHud.cpp`, `NativeTick`, after the `PromptText->SetVisibility(...)` line (line 213); NOT in the bar parts loop, so the line shows while the boss sleeps:
```cpp
BuildTextBlock->SetVisibility(Current.bShowBuild ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed);
BuildTextBlock->SetText(Current.BuildLine);
```
5. `RPGBossHud.cpp`, `URPGBossHud::TickComponent`, after the `Hud.bPrompt = ...` line (line 468) and before `Last = Hud;` (add `#include "Player/RPGBuildLoadout.h"` at the top):
```cpp
	if (const APawn* PlayerPawn = Controller ? Controller->GetPawn() : nullptr)
	{
		if (const URPGBuildLoadout* Loadout = PlayerPawn->FindComponentByClass<URPGBuildLoadout>())
		{
			Hud.BuildLine = FText::FromString(Loadout->GetBuildLine());
			Hud.bShowBuild = Loadout->HasChoice(); // a default run shows no extra text; drop HasChoice() to show the starter line too
		}
	}
```
Check the overlap with the pack's top-left widget with `Shot ShowUI` in PIE (plan R10). The widget is removed with the boss after its death (`Detach`), so the line disappears then.

## 4. Decisions taken (the owner did not answer the plan's five questions: the plan's recommendations were used)

- Q1 yes: the weapon is equipped at run time through the pack's own equipment function, no asset edit; the inventory component on the controller is NOT touched (its signatures are unknown, plan R2).
- Q2 yes: the weapon slot is locked from the moment the boss is awake until reset or death (only while a build is chosen, see section 1).
- Q3 Dex = `DualSwordCombatStyle` (the twinblades count as Dex in `BuildOfStyle` and the line; the table already has their rows).
- Q4 not part of this task (hyperarmor windows are data in `DA_WeaponAttacks`: Strength Strong, JumpHeavy, Charged with a lead of 0.08 s).
- Q5 no per-weapon HP column; `pie_builds.py` prints `INFO hp per hit <build> <kind>` for the balance run.
- The sword stays the default and the third choice `Starter`.

Deviations from the plan, because only the loadout files could be created: no `URPGBuildSubsystem` (the choice is the process-wide console variable, so it also survives a respawn and a PIE), no `Unchosen` enum value (`HasChoice()`), no F6/F7/F8 keys (a 0.1 s poll would miss a key press; a per-frame tick or an input binding is the way, owner's call), no `RequestBuild` API (the hook and the variable are the only entries), no chain stage in the swing text, no `build_off.py` warm-up script (`pie_builds.py` clears the variable itself; for the other drivers an `rpg.Build ""` line in the warm-up of `RunDrivers.ps1` is enough if a build was ever left set).

## 5. What is UNKNOWN and needs the editor

1. **Does `Update Equip Slot Item` equip?** With a struct copied from the active item, `Item_` replaced, update type 0 (then 1, then 0), does the pack replace the weapon, spawn the actor, set the style, grant `GA_Claymore_Melee_C`? The log line `call n of 3 for build X: Update Equip Slot Item(...) returned Success? ...; new item struct ...` and `style right after the call` answer it (`LogRPGBuild`, also `get_event_lines`). B2 and B5 of the driver are the test. If it does not: the next step is the controller dump of plan R2 (`BP_PlayerInventoryComponent_C` functions: `Add Item`, `Set Item Equipped`, `Update Equip Slot Item` of the inventory component), because the pack's own pick-up path goes through the inventory.
2. The order of `E_EquipUpdateType` (Update, Replace, Internal Update, Unequip are the display names) and what each type does to a slot that holds another item; the loadout sends 0, 1, 0.
3. Whether `NewItem` has the same struct type as the slot's item struct (then it is copied: amount, index and flags of the old item stay) or not (then it starts from the struct defaults with only `Item_` set); the struct text is in the log line. Whether `Item_` is a hard object field of a class the weapon item derives from (else the call is refused with a reason).
4. **Does `Set Equip Slot Disabled` stop the quickslot cycle (B7), and does a disabled slot break anything else** (the attack, enter combat, the HUD icon)? If swings or the combat toggle fail under the lock, set `bLockWeaponSlotInFight` to false (or `SetApplyOnlyOutOfCombat`...) and fall back to the plan's re-equip defence (2.4); if the press still changes the style the HUD line says what is held (truth rule) and `GetLockBreachCount()` counts it.
5. Whether the equip works in combat mode (B2 is out of combat, B5 and B7 are in combat mode: the check texts say which). Switch: `bApplyOnlyOutOfCombat` (hook `set_apply_only_out_of_combat_for_test`).
6. The replace targets the slot's active item index (0 at the start: the sword). If the pack's quickslot had made the staff (index 1) active when a re-equip runs, the staff entry would be replaced; the lock and the apply-only-while-the-boss-sleeps rule make this rare, but it is untested.
7. How long the pack needs for the swap (at an equip montage notify or at once): `VerifySeconds` 4 s, `MaxAttempts` 3; B2 prints the calls and successes.
8. The dual swords' two weapon trace targets (plan R4): whether one swing gives two intake records (B6 `records equal the boss's health drops` and the `INFO hp per hit` lines). Whether the dual swords have a jump heavy and a charged attack (`CAPS` at the top of the driver: Charged is off for Dex). Also which attack data the dual swords' strong montages carry: the swing tracker classifies a swing by the montage array, the hit intake classifies a hit by the attack data asset (`StrongMeleeAttackData` and so on); if the dual swords use `DefaultMeleeAttackData` for every attack, B6 shows a posture mismatch for Strong and JumpHeavy (the record says Light), and the fix is in the intake's classifier, not in the loadout.
9. HP per hit of the claymore against the sword (plan R5), printed by the driver, decision for M14.
10. The overlap of the HUD line with the pack's top-left widget (section 3).
11. Not covered by the driver and not written: B4 hyperarmor from authored rows (needs `set_weapon_windows.py`, plan 4.3), keys, the dex chain stage numbers, the shrine.
12. Compile risks I could not check (a build error is a one-line fix): `TAutoConsoleVariable<FString>` with `GetValueOnGameThread()`, `IConsoleVariable::Set(const TCHAR*, ECVF_SetByConsole)`, `FObjectPropertyBase::PropertyClass.Get()`, `UScriptStruct::CopyScriptStruct`, `FProperty::ExportTextItem_Direct` (same call as `RPGPackReflect.h`), `FString::TrimQuotes`, `FPackageName::ObjectPathToPackageName` / `GetShortName` in the asset test.

## 6. Order of the owner's steps after the build

1. Wait for the regression gate (`Saved/rundrivers_full.txt`) to end; close the editor (CLAUDE.md rule); add the two attach lines (section 2), optionally the HUD hook (section 3); build.
2. Start the editor with `-nosound`. Run the automation tests: the three new ones `OneBossFight.Build.Rules`, `.Decide`, `.Assets`, then the whole suite (19 + 3 = 22 tests). `Build.Assets` fails if a weapon item or style asset path is wrong: fix the path in `RPGBuildRules.h` (`Entry`).
3. Warm-up as always (`pie_debug_overlay.py`, `no_throttle.py`, `legend_off.py`). Regression with `rpg.Build` empty: `RunDrivers.ps1 -Only pie_hit_intake,pie_posture_hits,pie_stamina_cost,pie_hyperarmor,pie_bleed` (36, 25, 17, 23, 19), then `pie_player_death_reset` (25), `pie_boss_hud` (29; with the HUD hook).
4. `pie_builds.py` (add `@{ N = 'pie_builds'; K = 'R'; Min = 103; T = 1200 }` to `RunDrivers.ps1`): read the `[Builds]` lines and the `loadout event` lines. Triage by scenario: B0 `wiring report` not ok means a pack name changed (the report lists it); B2 failing means the equip path (section 5, point 1: read the call lines first); B7 failing means the lock (point 4); B3 and B6 failing numbers mean the table or the swing classification, not the loadout.
5. If B2 and B5 pass: the numbers of B3 and B6 are the M13 acceptance ("both builds can be selected, the weapon style, costs and posture numbers follow the table"); then hyperarmor windows (plan 4.3, `g3_probe_montages.py` numbers into `DA_WeaponAttacks`), then B4 of the plan.
6. Docs (CLAUDE.md rule): `TASKS.md` G3-2, G3-3, G3-5; the M13 row of `MILESTONE_GATE3_CODE.md`; `DECISIONS.md` (the build model: process-wide `rpg.Build`, loadout per pawn, lock only with a choice, Decide rules, update type 0/1/0); `KNOWN_ISSUES.md` (the UNKNOWN list above as it gets answered); `TEST_PLAN.md` rows `BUILD-01` (rules tests) and `BUILD-02` (`pie_builds.py`); `RunDrivers.ps1` table; the automation count in `PROJECT_STATE.md` (22).
