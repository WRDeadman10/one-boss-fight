# M13 plan: the two builds (Gate 3, rows G3-2, G3-3, G3-5)

Status: complete plan, written by a read-only helper on 2026-10-21/22 (no existing file was edited; only this file and the two probes were created). Nothing here was run: no editor, no build, no PIE, no probe. Every statement is marked KNOWN (with the source) or UNKNOWN (needs a probe). The probes are `Scripts/Editor/g3_probe_equip.py` and `Scripts/Editor/g3_probe_montages.py` (written, syntax-checked, not run); they answer most UNKNOWN lines. Table of contents: 0 order of work, 1 how the pack gives a weapon, 2 the build model, 3 the selector and the HUD line, 4 hyperarmor windows, 5 the PIE driver and the pure tests, 6 risks and five questions, 7 the probes.

Source tags used below: [dump1] = `g3_probe_dump.txt`, [dump2] = `g3_probe_dump2.txt`, [abil] = `abilities_dump.txt` (all three in the session scratchpad: pie_g3_probe.py and pie_dump_abilities.py output), [DEC] = `DECISIONS.md`, [MS] = `MILESTONE_GATE3_CODE.md`, [Freeze] = `Master_Design_Freeze_v1_2_AI_Implementation_Ready.md`, [code] = this project's C++, [names] = a name read from the pack asset's name table with a byte-level string extraction (read only, signature and behaviour NOT read: treat as a lead, not as a fact).

## 0. Order of work for the next session (fast path)

1. Open the editor on `L_SevarogArena`, run the two probes (section 7), paste the answers over the UNKNOWN lines of sections 1.2 and 4.
2. Pure header `Player/RPGBuildRules.h` + automation test `Build.Rules` (section 5), then `URPGBuildSubsystem` + `URPGBuildLoadout` (section 2), attach in `URPGPlayerMovesSubsystem::Attach`, `rpg.Build` + keys + HUD line (section 3), `pie_builds.py` (section 5).
3. Measure the hyperarmor windows with `g3_probe_montages.py`, write them into `DA_WeaponAttacks` (section 4), run `pie_builds.py` again.
4. Docs: `TASKS.md` G3-2, G3-3, G3-5, `MILESTONE_GATE3_CODE.md` M13 row, `DECISIONS.md` (the build model), `KNOWN_ISSUES.md`, `TEST_PLAN.md` (rows `BUILD-01`, `BUILD-02`), `RunDrivers.ps1` table.

## 1. How the pack gives the player a weapon today

### 1.1 What is known

| # | Statement | Status |
|---|---|---|
| 1 | The player is `BP_CombatPlayerCharacter_C` (pack mannequin). Its `CombatComponent` (`BP_CombatComponent_C`) holds `CurrentCombatStyle` (a `BP_CombatStyle_C` data asset), `DefaultCombatStyle` (= `UnarmedCombatStyle`), `CurrentCombatType`, `bIsCombatEnabled?`, `CombatWeaponActors` (map keyed by a `E_WeaponHandType` enumerator: 0 = the sword actor `BP_ToughSword_C`, 1 = another actor, text cut off), `AttackCount`, `Current Attack Index`. | KNOWN [dump1 l.140-175, dump2 l.141-183] |
| 2 | At the first PIE tick `CurrentCombatStyle` is `SwordCombatStyle` (`CombatStyleType` enumerator 11, anim layer `ABP_SwordLayer`). The player starts with the sword. | KNOWN [dump1 l.158-165, MS "What the pack gives"] |
| 3 | Event dispatchers on the combat component with signatures: `OnCombatStyleBegin(CombatStyleType:Byte)`, `OnCombatStyleEnd(CombatStyleType:Byte)`, `OnCombatToggled(bCombatEnabled?:Bool)` (the sword actor is bound to it: `BP_ToughSword_C_0.OnCombatToggled_Event`), `OnCombatTypeBegin/End(CombatType:Byte)`. | KNOWN [dump2 l.154-164] |
| 4 | A combat style asset holds `CombatStyleType`, `CombatType`, `Camera Mode Class`, `Anim Layer Class`, `AbilitiesSet` (array of `{InputTags, Abilities[]}`), `Granted Gameplay Effects`. The dual sword style lists `GA_DualSword_EnterCombat`, `GA_DualSword_ExitCombat`, `GA_DualSword_QuickSlot`, `GA_DuaSword_Melee`, `GA_SwitchToTwinblades` with the input tags `InputTag.NormalAttack`, `ChargedAttack`, `StrongAttack`, `ToggleCombat`, `TogglePunisherMode`, `Quickslot.CycleRight`. So a style brings its own abilities. | KNOWN [dump1 l.143-165; strings of `DualSwordCombatStyle.uasset`] |
| 5 | Style assets on disk: `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/` + `Sword/SwordCombatStyle`, `Sword/SwordAndShieldCombatStyle`, `Claymore/ClaymoreCombatStyle`, `DualSwords/DualSwordCombatStyle`, `Twinblades/TwinbladeCombatStyle`, `Polearms/PolearmCombatStyle`, `Unarmed/UnarmedCombatStyle`, `Unarmed/UnarmedCombatnShieldStyle`. Weapon abilities in the same folders: `Claymore/GA_Claymore_Melee`, `DualSwords/GA_DuaSword_Melee`, `Twinblades/GA_Twinblades_Melee`, `Sword/GA_Sword_Melee` (plus `_EnterCombat`, `_ExitCombat`, `_QuickSlot`: `GA_QuickSlot_Claymore`, `GA_DualSword_QuickSlot`, `GA_Twinblades_QuickSlot`, `GA_Sword_QuickSlot`). | KNOWN [file names on disk, `g3_dump_attack_data.py` paths] |
| 6 | The weapon abilities have the arrays `AttackMontages`, `StrongAttackMontages`, `ChargedAttackMontages`, `FallingAttackMontages`, `SprintAttackMontages`, `DodgeAttackMontages`, `BackstabAttackMontages`, `FatalityAttackMontages`, `PunisherModeAttackMontages`; the sword has strong = `Ability_E_Anim_Montage`, charged = `ChargedAttack_Montage`, falling = `Attack_PrimaryA_Montage` (copied by `air_light_attacks.py`), light = `Attack_PrimaryA`, `B`, `C`...; cost effect `GE_MeleeAttackCost` (-15 `Attribute.Stamina`); attack data `DefaultMeleeAttackData`. `GetAbilities` in `RPGSwingTracker.cpp` already reads these arrays for any weapon ability through `CreatedAbilities`. | KNOWN [abil l.936-994, code] |
| 7 | The claymore, dual sword and twinblade ability arrays (which montages are in strong, charged, falling) were NOT dumped. Montage files on disk: claymore `2handed/PrimaryAttack_A..D_Slow`, `2handed/Ability_R_Anim_Montage`; dual swords `DualSwords/Attacking/Attack01`, `Attack_Melee_A/B/C`, `Attack_Melee_C_Dash`, `Attack_Melee_Air`, `Attack_GuardBreak_A`, `Attack_GuardBreak_C`; twinblades `Twinblades/Attacking/Primary_Melee_A..E_Slow`, `Primary_Melee_Air`. Which file sits in which array: UNKNOWN. | file names KNOWN, array content UNKNOWN (probe `g3_probe_montages.py`) |
| 8 | `Scripts/air_heavy_selector.py` gives a jump heavy only to a weapon whose ability returns a non-empty `StrongAttackMontages`; the note in DECISIONS says twinblades and polearm have none. Whether the claymore and the dual swords have one: UNKNOWN. If the dual swords have none, the Dex build has no jump heavy (its jump press plays the jump light). | UNKNOWN |

### 1.2 Weapons are inventory items; the equipment component drives the style

| # | Statement | Status |
|---|---|---|
| 9 | Weapons are `WeaponItem_C` data assets (children of `BP_ItemBase`) under `.../MeleeCombatSystem/Blueprints/Items/Weapons/`: `ToughSword` (style `SwordCombatStyle`, actor `BP_ToughSword_C`, sockets `WeaponSocket_R` / `HipSheath_L`, has `Granted Gameplay Effects` = `GE_ToughSwordAttributeModifiers`, `MergableWeapons` with a shield gives `SwordAndShieldCombatStyle`), `KwangSword` (item name "Heavy Sword", style `ClaymoreCombatStyle`, actor `BP_KwangSword_C`, sockets `HeavySwordSheath_Back` (sheath) and `HeavySwordSocket_R` (hand), which is default and which is active is assumed from the names, no granted effects in the name table), `DualSteelSwords` (item name "Dual Steel Swords", a `DualWeaponItem_C`, style `DualSwordCombatStyle`, actor `BP_DualSteelSwords_C`, sockets `WeaponSocket_R` and `DualSwordSheath_R`; the second sword is attached by `BP_BaseDualWeapon`). Fields of `WeaponItem`: `Combat Style`, `Equipable Actor Class`, `EquipSlot` (default enumerator 11), `MergableWeapons`, `MaxCount`, `ItemPanel`, function `GetWeaponType`. | KNOWN as names read from the asset name tables [names] |
| 10 | The player's `PlayerInfo` asset (`.../Blueprints/DataAssets/PlayerInfo`, class `BP_PlayerInfo_C`) has `Default Combat Style`, `Default Equipment` (array of `F_EquipmentSlot`), `Default Inventory` (array of `F_InventorySlot`), `Default Ability Sets`, `Default UI Widgets`, `Input Mapping Context`. Its import table references the items `ToughSword`, `DualSteelSwords`, `FengMaoWeapon` (polearm), `ElvenBow`, `ExampleMagicStaff`, nine spells, three armour pieces, accessories, `HealthPotion`, two arrow items. It does NOT reference `KwangSword` (the claymore item) and no shield item. A text search of the pack's `.uasset` and `.umap` files for the item paths finds `KwangSword` referenced only by the demo map `MeleeCombatSystem/Maps/GreyboxLevels/CombatSystemTestLevel` (a world pickup or chest, probably), and `DualSteelSwords` by `PlayerInfo` and the same map. So: the dual swords are probably in the starting loadout, the claymore is not. | KNOWN as import table names and file search [names]; what sits in which slot UNKNOWN |
| 11 | `E_EquipSlots` has 12 enumerators (0, 1, 2, 4, 9, 11, 12, 20, 21, 25, 26, 27). The quickslot ability maps `InputTag.Quickslot.CycleUp` to 27, `CycleDown` to 21, `CycleLeft` to 25, `CycleRight` to 11; the weapon item's default `EquipSlot` is 11 and the sword's quickslot ability is the `CycleRight` one, so enumerator 11 is the weapon slot. The display names ("Weapon Slot", "Off-hand Weapon Slot", "Shield Slot", "Tools Slot"...) are listed in the enum but the order against the enumerators was not read. | enumerator 11 = weapon slot KNOWN by two sources [abil l.770, names]; the others UNKNOWN |
| 12 | `BP_EquipmentComponent_C` (named `EquipmentComponent` on the pawn: `GA_Quickslot_C.EquipmentComponent` points at `BP_CombatPlayerCharacter_C_0.EquipmentComponent`) has the variable `EquipmentSlots` (array of `F_EquipmentSlot`: `EquipSlot_13_...`, `EquipSpawnSetting_28_...` (Spawn Active Item / Spawn All Items), `Disabled?_21_...`, `ActiveItemIndex_20_...`, `Items_17_...` (array of `F_ItemSlot`: `Item_10_...`, `Amount_5_...`, `Index_29_...`, `IsEquipped?_14_...`), `EquippedActors_29_...`; the struct field names carry GUID suffixes, so C++ must match them by prefix). Functions by name: `Update Equip Slot Item`, `Update Equipped Actor`, `Get Active Equipped Actor`, `Get Active Equipped Item`, `Get Equipped Actor`, `Get Equipped Slot Item`, `Get Equipped Slots Items`, `Find Next Valid Equipped Item`, `Set Equip Slot Disabled`, `Set Equip Slot Disabled At Index`, `Is Equip Slot Enabled?`, `IsWeaponEquipped?`, `UseEquipable`, `Use Slot Item`, `Build Equipment`, `InitializeEquipmentComponent`, `GetEquipSlotIndex`, `GetEquipmentSlot`, `GetAllEquipmentSlots`, `GetAllEquippedActors`, `GetEquippedActors`, `GetEquippedActorsByTag`. Events: `OnEquipSlotUpdated`, `OnActiveItemChanged`, `OnSwitchEquipSlotItems`, `OnItemUsed`, `OnEquipSlotDisabledUpdated`. `E_EquipUpdateType` has four values shown as Update, Replace, Internal Update, Unequip (enumerator order unread). | names KNOWN [names]; parameters, behaviour and which component the pack calls from where UNKNOWN |
| 13 | `BP_PlayerInventoryComponent_C` (which actor owns it, pawn or controller: UNKNOWN) has `Add Item`, `Remove Item`, `Update Equip Slot Item`, `UpdateEquippedItemAtIndex`, `Set Item Equipped`, `Drop Item at Index`, `InitializeInventory`; its parent `BP_InventoryComponent_C` has `AddItem`, `AddItemsFromArray`, `Find Item By Data`, `Find Item by ID`, `GetInventoryItem`, `Set Item Equipped` and the events `OnItemAdded`, `OnInventoryRefreshed`. The pack's own pickup actor `BP_BasePickUp` (a `BP_Interactable`: `Interact`, `GetInventoryComponent`, `ItemsToAdd`, `AddItemsFromArray` / `Add Item`) puts items into the player's inventory with these same functions, so a run-time `Add Item` is the pack's own pick-up path. | names KNOWN [names]; signatures UNKNOWN |
| 14 | The weapon actor does the style work: `BP_BaseWeapon` has `InitializeEquipable`, `UseEquipable`, `GrantWeaponAbilities` (`GiveAbilitySet`), `Clear Weapon Abilities`, `Set Curent Combat Style` (sic, one `r`), `Merge Combat Styles`, `ResetToDefaultCombatStyle`, `LinkAnimClassLayer`, `UnlinkAnimClassLayer`, `AttachWeaponActor`, `Add Collision Target Type`, `Remove Collision Target Types By Tag` and the interface events `OnEquipped`, `OnUnEquipped`. `BP_BaseDualWeapon` adds `AttachSecondWeapon` and a second trace target tagged `TargetType.Off-handWeapon` (so the dual swords have TWO weapon trace targets next to `TargetType.MainWeapon`). The combat component has `Set Curent Combat Style`, `ResetToDefaultCombatStyle`, `GetCurrentCombatStyle`, `GetCurrentCombatStyleType`, `AddCombatWeaponActor`, `GetCombatWeaponActor`, `SetCombatEnabled`, `SetCombatType`. | names KNOWN [names]; the order of events when a weapon is equipped (actor spawn, style set, abilities granted) is deduced from the names, UNKNOWN as logic |
| 15 | Switching in play: the arrow keys / D-pad (`IA_QuickSlotRight`, `Up`, `Down`, `Left`; 4 input actions exist) activate the ability with the matching `InputTag.Quickslot.Cycle*` tag. For the weapon slot it is the current style's quickslot ability, a child of `GA_Weapon_QuickSlot` (state `Character.State.UsingItem`, it plays montages from its two arrays `SwitchWeapon(Equip)` and `SwitchWeapon(UnEquip)`, e.g. `SwitchtoLightSword_Equip_Montage`, `Quickslot_Claymore_Equip_Montage`; `GA_Quickslot` asks the equipment component for `Get Active Item Index`, `Get Equipped Slots Items` and `GetNextValidItemIndex`). The equip montages carry the pack notify `AN_SwitchEquipSlotItems`, whose event is `OnSwitchEquipSlotItems` on the equipment component; presumably the swap happens at that notify. | names and tags KNOWN [abil l.767-796, l.1053-1086, names]; that the swap happens at the notify and whether it works out of combat: UNKNOWN |
| 16 | The pack HUD (`MainHUD`): player bars top left (health, stamina, mana, with an icon row under them), the four quickslot icons bottom left (the weapon icon sits in the right slot), "SOULS" counter top right; our boss HUD uses the bottom centre and the screen centre. | KNOWN [picture `Documentation/Art/sevarog_pack_parity.png` (taken with the retired Sevarog boss, the pack HUD is the same), `RPGBossHud.cpp`; DECISIONS stage 2: "HUD, quick slots and souls counter show"] |

### 1.3 The reflection calls the loadout code needs

| Need | Call or property | Status |
|---|---|---|
| Find the combat component | `RPGPack::FindComponentByClassName(Pawn, TEXT("BP_CombatComponent_C"))` | KNOWN (`RPGSwingTracker.cpp` l.213) |
| Read the current style (the weapon) | `RPGPackReflect::ReadObject(Combat, TEXT("CurrentCombatStyle"))` then `GetFName()` = asset name | KNOWN (`RPGSwingTracker.cpp` l.215, `RPGHitIntake.cpp` l.287) |
| Hear a style change | bind `BP_CombatComponent_C.OnCombatStyleBegin(CombatStyleType:Byte)` / `OnCombatStyleEnd`, as `URPGHitIntake::TryBind` binds `OnHit` (`FMulticastDelegateProperty`, refuse when the signature differs) | signature KNOWN [dump2 l.161-164]; whether the pack broadcasts it on every weapon change UNKNOWN (poll `CurrentCombatStyle` as a fallback) |
| Find the equipment component | `FindComponentByClassName(Pawn, TEXT("BP_EquipmentComponent_C"))` | KNOWN name [abil l.769] |
| Read the weapon slot | array property `EquipmentSlots` of the equipment component, struct fields matched by prefix (`EquipSlot_`, `ActiveItemIndex_`, `Items_`, `Disabled?_`, `EquippedActors_`) | names KNOWN [names]; the slot whose `EquipSlot` is enumerator 11 is the weapon slot |
| Put a weapon item into the weapon slot and make it active | `Update Equip Slot Item` (equipment component and/or player inventory component), parameter names seen: `In Equip Slot Type` / `InEquipSlotType`, `Item`, `New Item`, `Old Item`, `ItemIndex`, `UpdateType` (`E_EquipUpdateType`), delegate `EquipSlotUpdated` | name KNOWN, signature and owner UNKNOWN |
| Put the claymore item into the inventory | `BP_PlayerInventoryComponent_C.Add Item` with the `KwangSword` item asset loaded from `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Items/Weapons/KwangSword` | name KNOWN, signature UNKNOWN |
| Cycle the pack's own way (fallback for items already in the quickslot list) | `URPGInputTestUtils::InjectAction` with `IA_QuickSlotRight` (project helper, usable from C++), or `TryActivateByTag(Pawn, "InputTag.Quickslot.CycleRight")` (`RPGBlueprintCall.h`, tag is an ability tag of the quickslot ability) | helpers KNOWN; effect UNKNOWN |
| Lock the weapon slot during the fight | `Set Equip Slot Disabled` / `Set Equip Slot Disabled At Index` on the equipment component | name KNOWN, effect on the quickslot cycle UNKNOWN |
| Set the style directly (last resort, NOT recommended) | `BP_CombatComponent_C.Set Curent Combat Style(Combat Style)` | name KNOWN; it does not grant abilities, link the anim layer or add the trace target (names of those live on the weapon actor), so the swing would run on the old sword's setup |

The probe `g3_probe_equip.py` prints, in one PIE: the pawn's and the controller's components, the combat component and style, the equipment slots with their items, the inventory, the three weapon item assets and five combat style assets, the player's Blueprint functions (parameter names, through `DumpPlayerFunctions`), and then presses `IA_QuickSlotRight` twice out of combat, enters combat, presses twice more, and logs the style, the combat flag and the slots after each step. Its output answers every UNKNOWN of 1.2 and 1.3 except the signatures of functions on the controller's components (see risk R2).

## 2. The build model

### 2.1 What the build is (no new numbers, only a choice of weapon)

The numbers already live in the weapon attack table (`RPGWeaponAttackTable.cpp` `FillDefaults`, asset `/Game/OneBossFight/Data/DA_WeaponAttacks`), keyed by the pack's combat style asset name. The swing tracker and the hit intake read `CurrentCombatStyle` at the swing start and at every hit (`RPGSwingTracker.cpp` l.215, `RPGHitIntake.cpp` l.287), so equipping the right weapon is all a build has to do: posture, stamina, bleed and hyperarmor follow with no change to M7-M12. KNOWN [code].

| Build | Style asset (table key) | Item asset to equip | Rows now (posture / stamina, -1 = the pack's 15) |
|---|---|---|---|
| Strength | `ClaymoreCombatStyle` | `.../Blueprints/Items/Weapons/KwangSword` ("Heavy Sword", actor `BP_KwangSword_C`) | Light 18 / -1, Strong 30 / 35, Charged 38 / 35, JumpLight 18 / -1, JumpHeavy 38 / 35, Knockdown 38 / 35, bleed 0, hyperarmor none yet |
| Dex | `DualSwordCombatStyle` (spare: `TwinbladeCombatStyle`, same rows) | `.../Blueprints/Items/Weapons/DualSteelSwords` (actor `BP_DualSteelSwords_C`) | Light 6 / 10, Strong 10 / 10, Charged 14 / 10, JumpLight 6 / 10, JumpHeavy 14 / 10, Knockdown 14 / 10, bleed 20 on every kind |
| Starter (default, no choice) | `SwordCombatStyle` | `.../Items/Weapons/ToughSword` (what the pack gives) | the Strength posture numbers, the pack's stamina on every kind (the sword keeps the pack's cost), bleed 0 |

KNOWN: rows [code `RPGWeaponAttackTable.cpp` l.28-56, `RPGAutomationTests.cpp` l.418-451]; item paths [file names on disk]; the asset may hold values the owner tuned (UNKNOWN: read it with `make_weapon_table.py`, which only prints an existing asset). Styles without a row (`SwordAndShieldCombatStyle`, `PolearmCombatStyle`, `UnarmedCombatStyle`, bow, staff) get the table Fallback (20 posture, the pack's stamina, no bleed): see the lock in 2.4.

### 2.2 Where the choice lives

| Piece | Class | Why |
|---|---|---|
| Choice, source, counters | `URPGBuildSubsystem : UGameInstanceSubsystem` (new, `Player/RPGBuildLoadout.h/.cpp`) | The pack respawns the player as a NEW pawn (`RPGBossEncounter.h`: the reset happens "when the player has a new pawn") and the victory retry calls `OpenLevel` (`RPGBossHud.cpp` l.202), so a pawn component or a world subsystem would forget the choice. A game instance subsystem survives both (works with the pack's Blueprint `BP_AdvancedGameInstance`: engine behaviour, KNOWN). Not saved to disk (an editor restart starts with no choice); a `USaveGame` can come later. |
| Applying the build to a pawn | `URPGBuildLoadout : UActorComponent` on the pack player (new), added in `URPGPlayerMovesSubsystem::Attach` next to `URPGSwingTracker` with the same `IsPackPlayer(Pawn) && !FindComponentByClass` guard (`RPGPlayerMovesSubsystem.cpp` l.170-177) | Every new pawn gets its own loadout component, which reads the subsystem. |
| The rules | `Player/RPGBuildRules.h` (new, header only, like `RPGSwingRules.h`) | `ERPGBuild { Unchosen, Starter, Strength, Dex }` (UENUM, like `RPGAttackKind.h`), `Parse(FString)`, `StyleFor(build)`, `ItemPathFor(build)`, `BuildOfStyle(style)`, `Decide(input)` (the apply state machine), `BuildLine(chosen, actual style, state)` (HUD text). The mapping build to style and item is three constants in this header (identity, not a balance value; the balance values stay in the table, Freeze 20.3). |

### 2.3 Applying the loadout before the fight, resetting it after

The loadout ticks every 0.1 s (a frame is not needed; the HUD reads its state) and calls `RPGBuildRules::Decide`:

| Input | Output |
|---|---|
| Chosen is `Unchosen` | Idle: no pack function is ever called (counter `GetApplyAttemptCount() == 0`; this is the "no build chosen" guarantee) |
| Actual style already equals `StyleFor(Chosen)` and the build's weapon ability is granted (`FindAbilityByClassName(Pawn, "GA_Claymore_Melee_C")` / `GA_DuaSword_Melee_C` / `GA_Sword_Melee_C`, helper in `RPGBlueprintCall.h`) | Idle (done) |
| Actual style is None or the pawn has no equipment component yet (the pack is still initialising), or the player is dead | Wait |
| The boss exists and its `URPGBossEncounter::IsDormant()` is false | Defer: logged once per request, counted, shown on the HUD ("applies when the fight resets"); no boss in the world (it is destroyed about 3.5 s after its death) counts as dormant |
| The player is in a montage that is not ours (a dodge, a swing, a hit stun) | Wait |
| Apply running and younger than `VerifySeconds` (default 4 s) | Verify |
| Apply running and older, attempts below `MaxAttempts` (default 3) | Retry |
| Apply running, attempts used | GiveUp: logged once, the state stays Failed, the fight is playable with the old weapon, the HUD line says it |
| otherwise | Start: run the apply step (below) |

The apply step, in order of preference (which one works is decided by the probe):

1. Equipment path: make sure the build's item is in the player's inventory (`Find Item By Data`, else `Add Item`), then `Update Equip Slot Item` for the weapon slot (enumerator 11) with the item and `UpdateType` Replace, and wait for the pack to spawn the weapon actor and set the style. Everything stays the pack's own flow (actor, abilities, anim layer, trace targets). Signatures UNKNOWN.
2. Quickslot path (only for an item that is already in the weapon slot's list, probably the dual swords): activate the weapon quickslot ability (`TryActivateByTag(Pawn, "InputTag.Quickslot.CycleRight")` or `URPGInputTestUtils::InjectAction` with `IA_QuickSlotRight`) up to the number of items in the list, until the style matches. UNKNOWN whether it works out of combat.
3. NOT used: `Set Curent Combat Style` alone (see 1.3).

When does it run again (reset): a respawn creates a new pawn with the pack's default sword; the new `URPGBuildLoadout` starts with the subsystem's choice and applies it as soon as the boss is dormant again (the encounter resets on the new pawn; for one tick the loadout may see an awake boss and Defer once, which the driver must accept). An encounter reset without a respawn (`ResetForTest`) changes `GetGeneration()`: the loadout re-checks and applies a build that was chosen during the fight. A build chosen while the boss is awake is applied at the next reset or when the boss is gone.

What must NOT change when no build is chosen: the pack's starter sword stays equipped (nothing is called), the sword rows keep the Strength posture numbers and the pack's stamina cost, `pie_hit_intake.py` 36/36, `pie_stamina_cost.py` 17/17, `pie_hyperarmor.py` 23/23, `pie_posture_hits.py` 25/25, `pie_bleed.py` 19/19 still pass with `rpg.Build` empty. The console variable survives a PIE (like `rpg.Legend`): a `Scripts/Editor/build_off.py` (sets `rpg.Build` to empty) goes into the warm-up of `RunDrivers.ps1`, and `pie_builds.py` ends by resetting it.

### 2.4 Keeping the build true during the fight (needs the owner, Q2)

The pack's quickslot arrows stay live in the fight: the player can cycle to the polearm, the bow or the staff (these are probably in `Default Equipment`, UNKNOWN), which have no table rows (Fallback row), or from Strength to Dex, which makes "the build was chosen before the fight" false. Two defences, both cheap: (a) the HUD line and every number come from the weapon actually equipped (truth rule in 3.2), (b) while the boss is awake the loadout disables the weapon slot (`Set Equip Slot Disabled`, name KNOWN, effect on the cycle UNKNOWN) and enables it again when the boss sleeps or is gone. If (b) does not stop the cycle, the loadout re-equips the build's weapon when the style changes mid-fight (counted, logged) instead of fighting the pack.

### 2.5 G3-3 detail: the dex chain

The Freeze asks for a four-stage rapid chain with stage IDs (G3-3). The dual sword files `Attack01`, `Attack_Melee_A`, `Attack_Melee_B`, `Attack_Melee_C` (plus `Attack_Melee_C_Dash`) suggest four light stages; the twinblades have five (`Primary_Melee_A..E_Slow`). UNKNOWN until the probe prints the length and order of `GA_DuaSword_Melee.AttackMontages`. A stage ID is cheap: the index (plus 1) of the montage in the ability's `AttackMontages`, which `URPGSwingTracker::ClassifyMontage` already walks; add it to `FRPGSwing` as `ChainStage` and to the swing text.

## 3. The selector until the shrine exists

### 3.1 One entry point, three front ends

All selectors call `URPGBuildSubsystem::RequestBuild(ERPGBuild Build, const FString& Source)` (returns the state: Accepted, Deferred (boss awake), Same, Invalid). Nothing else changes the choice.

| Front end | How | Notes |
|---|---|---|
| Console variable `rpg.Build` | `static TAutoConsoleVariable<FString> CVarRPGBuild(TEXT("rpg.Build"), TEXT(""), ..., ECVF_Default);` in `RPGBuildLoadout.cpp`. `rpg.Build Strength`, `rpg.Build Dex`, `rpg.Build Starter`, `rpg.Build ""` (no choice). The loadout polls `CVarRPGBuild.GetValueOnGameThread()` each tick and calls `RequestBuild` when the text changed (no static callback, no world needed). `RPGBuildRules::Parse` accepts `strength`, `str`, `dex`, `dexterity`, `starter`, `sword`, `none`, empty, any case; anything else is logged as invalid and ignored. | Same pattern as `rpg.Legend` and `rpg.Debug` (the project has cvars only, `FAutoConsole*` is not used yet: KNOWN by grep). A string cvar gives exactly the requested `rpg.Build Strength|Dex` syntax. Process wide, survives a PIE (2.3). Packaged builds have no console in Shipping, so the keys and the shrine are the real selectors there. |
| Keys | In `URPGBuildLoadout::TickComponent`: `PC->WasInputKeyJustPressed(EKeys::F6)` Strength, `F7` Dex, `F8` Starter (the same call the retry in `RPGBossHud.cpp` l.198 uses). Pressed while the boss is awake: Deferred. | The name table of the pack's `IMC_AdvancedControls` lists no F-key (it lists Escape, SpaceBar, LeftShift, mouse buttons, scroll, arrows, gamepad keys; one-letter keys were not read); our retry uses R. Drivers press them with `URPGInputTestUtils::SetKeyDown` (KNOWN helper, PROJECT_STATE). |
| Shrine (later) | `ARPGBuildShrine` actor (below) calls the same function | Needs Brief 13 G3. |

### 3.2 The HUD build line

Read: `URPGBossHudWidget` (`UI/RPGBossHud.cpp`) builds its tree in C++ in `RebuildWidget` (a `UCanvasPanel`, `AddText` helper, Cinzel font via `MakeFont`), is created by the boss component `URPGBossHud::EnsureWidget` (viewport z-order 20) before the dormant check, so it exists while the boss sleeps, and it is removed when the boss is destroyed after its death (`Detach`, which lets only the banner and retry finish). `FRPGBossHudState` is what the component hands the widget each tick. KNOWN [code].

Decision: put the line in this widget, not in a second widget. One owner of our viewport UI, one z-order, the existing `Apply` path, the existing test accessors (`IsBarShown`, `GetBannerText`). Changes (all additive):

1. `FRPGBossHudState` gets `FText BuildLine; FText BuildHint; bool bShowBuild = false;`.
2. `RebuildWidget` adds two `AddText` blocks: `BuildText` anchored top centre (`FVector2D(0.5f, 0.f)`, alignment `(0.5f, 0.f)`, position `(0, 18)`, font size 18, gold `(0.93, 0.8, 0.45)`) and `BuildHintText` under it (`(0, 42)`, size 13, grey, only while the boss sleeps: "F6 STRENGTH   F7 DEX   F8 STARTER"). They are NOT in the bar parts list that `NativeTick` collapses when `bShowBar` is false.
3. `URPGBossHud::TickComponent` fills them from the player's `URPGBuildLoadout` (`FindComponentByClass` on the first player pawn): `GetBuildLine()`.
4. Test accessors `IsBuildLineShown()`, `GetBuildLineText()` as UFUNCTIONs next to `IsBarShown()`.

Why top centre: the pack's `MainHUD` owns top left (bars and icon row), top right (souls) and bottom left (quickslots); our boss HUD owns bottom centre and the screen centre (picture `Documentation/Art/sevarog_pack_parity.png`). The exact pixel extents of the pack's top-left widget at 1080p are UNKNOWN; top centre avoids the question. Check with `Shot ShowUI` in PIE after the build.

The truth rule (pure, `RPGBuildRules::BuildLine`): the line names the build of the weapon that is really equipped, never the choice alone.

| Actual style | Line | Suffix when Chosen differs or the loadout is not done |
|---|---|---|
| `ClaymoreCombatStyle` | `STRENGTH  -  HEAVY SWORD` | |
| `DualSwordCombatStyle` | `DEXTERITY  -  TWIN SWORDS` | |
| `TwinbladeCombatStyle` | `DEXTERITY  -  TWINBLADES` | |
| `SwordCombatStyle` | `STARTER SWORD` | |
| any other style | `OFF-BUILD WEAPON` | |
| (all) | | `  (EQUIPPING...)` while Applying, `  (NEXT FIGHT)` when Deferred, `  (NOT EQUIPPED)` when Failed |

### 3.3 The shrine hook (Brief 13 G3, M-07)

Asked of Antigravity (`AG/BRIEF_13.md` G3, only after G1 and G2 pass): `Import/Boss01/Props/SM_Boss01_BuildShrine.fbx`, one connected static mesh, 200 cm high (150 to 250), about 120 cm wide, origin at the centre of the base on the floor, slots `M_Boss01_Shrine_Stone`, `M_Boss01_Shrine_Metal`, `M_Boss01_Shrine_Glow`, one socket `Interact` at the front of the base at 100 cm height, under 8,000 triangles. Not delivered yet (KNOWN [Brief 13, TASKS M-07 "Brief 13 G3"]).

Our side, written now so only the mesh is missing: `Arena/RPGBuildShrine` (`AActor`, like `ARPGFogGate` which `dress_arena.py` places: KNOWN pattern, DECISIONS "Fog gate"): a `UStaticMeshComponent` that loads `/Game/OneBossFight/Boss01/Props/SM_Boss01_BuildShrine` (under the always-cooked `/Game/OneBossFight/Boss01`, `DefaultGame.ini` l.21; the automation test `Content.CookCoverage` checks the literal), falls back to an engine cube with a log line when the mesh is missing, and a `UStaticMeshComponent` socket lookup of `Interact`. While the player is within 250 cm of the socket and the boss sleeps it shows "E  CHOOSE BUILD" through the build line widget and cycles Strength, Dex, Starter on the key (which key is free is UNKNOWN: the name table of `IMC_AdvancedControls` shows no F-key, but one-letter keys such as the one of `IA_Interact` were not read; check it in the editor before choosing E). `Scripts/Editor/dress_arena.py` places it near the `PlayerStart` of `L_SevarogArena` (outside the 1200 cm gate radius of the boss). It calls `RequestBuild(..., "shrine")`. UNKNOWN: whether to use the pack's own interaction system (`InteractionSystem`, `IA_Interact`, `Interactable` trace channel, `GA_Interact`); recommendation: not for the first version, a distance check is enough and cannot break the pack (the pack's interactables implement the Blueprint interface `BP_InteractionInterface` with `Interact` and `EndInteraction`, which a C++ actor cannot implement without a Blueprint class in between).

## 4. Hyperarmor windows per weapon from measured montages

### 4.1 What is in place and which rows need a number

M11 is done: inside a table row's window `[HyperArmorStart, HyperArmorEnd]` (seconds of MONTAGE position, `Montage_GetPosition`) the player carries `GE_HitStunImmune`, refreshed every 3 s of its 4 s; health damage still lands; no shipped row has a window (all `-1`). KNOWN [MS M11, `RPGSwingTracker.cpp` `UpdateHyperArmor`, `RPGSwingRules.h`].

The Freeze gives hyperarmor to the Strength build only, "during the authored downswing" of the jumping heavy (Freeze 5, 20.1, M3 task list: "hyperarmor window during active frames of jumping heavy"). The pack plays the SAME montage for the ground strong and the jump heavy (`GetAttackMontages(StrongAttack)`; DECISIONS "Jump heavy (built)"), so one measurement fills two rows.

| Row (weapon, kind) | Montage source | Window |
|---|---|---|
| `ClaymoreCombatStyle`, `Strong` | each element of `GA_Claymore_Melee.StrongAttackMontages` | its `ANS_CollisionTrace` window, with the lead of 4.2 |
| `ClaymoreCombatStyle`, `JumpHeavy` | the same montage (the selector plays the strong montage while falling) | the same numbers |
| `ClaymoreCombatStyle`, `Charged` | each element of `ChargedAttackMontages` (hold, then the release strike) | the trace window of the release strike |
| Claymore `Light`, `JumpLight` (`AttackMontages`, `FallingAttackMontages`) | | none (Freeze: heavy only) |
| Dex rows (`DualSwordCombatStyle`, `TwinbladeCombatStyle`) | `GA_DuaSword_Melee`, `GA_Twinblades_Melee` arrays | none by the Freeze; the same measurement can fill them if the owner asks (Q4) |
| Starter `SwordCombatStyle` | `GA_Sword_Melee` | none (keeps what `pie_hyperarmor.py` proved with test windows) |

UNKNOWN: which montage sits in the claymore's strong, charged and falling arrays (the array contents were not dumped, see 1.1 #7), whether the claymore has a strong montage at all (if not, the selector never plays a jump heavy for it and the Freeze's jump heavy has to come from `FallingAttackMontages`, see risk R6), and whether any of these montages already carries the pack's own hyperarmor notify state `ANS_HitStunImmune` (the DELTA_AUDIT lists that class among the notifies "seen on boss and player montages"; where was not recorded). If a claymore montage has it, the pack already gives hyperarmor there and our table window should be set to the same span so the two do not disagree.

### 4.2 What to measure, per montage element

`g3_probe_montages.py` (section 7) loads the four weapon abilities' defaults (`GA_Sword_Melee`, `GA_Claymore_Melee`, `GA_DuaSword_Melee`, `GA_Twinblades_Melee`) the way `air_light_attacks.py` does (`bp.generated_class()`, `get_default_object`, `get_editor_property("StrongAttackMontages")` etc.) and, for every element of `AttackMontages`, `StrongAttackMontages`, `ChargedAttackMontages`, `FallingAttackMontages`:

| Item | How | Why |
|---|---|---|
| montage name, length | `get_play_length()` | the window must lie inside it |
| rate scale, struct `PlayRate`, `EndTimeMultiplier`, `InTimeToStartMontageAt` | `rate_scale`; the struct text of the `F_AbilityMontage` element (fields `PlayRate_4_...`, `EndTimeMultiplier_25_...`, `InTimeToStartMontageAt_26_...`, `StartSectionName_29_...`) | real seconds = montage seconds / (rate scale x PlayRate); the pack ends the ability at `EndTimeMultiplier` x length (the Sevarog notes say 80 %) |
| every `ANS_CollisionTrace` window | `unreal.RPGMontageUtils.describe_notifies(montage)` (the project's C++ helper; its header says Python cannot read a montage's notify times itself), one line per notify, parsed by the probe (`[state] ANS_CollisionTrace_C at 0.170 s for 0.300 s`). The Python call `unreal.AnimationLibrary.get_animation_notify_events` is used only for the properties below, paired with the C++ lines by index (same order) | the downswing is the trace window: start, end, number of windows, gaps |
| its properties | `Collision Target Tag`, `EventTag`, `AttackData`, `Swing Direction`, `TraceRadiusModifier` (names from `inspect_pack_notifies.py`, which read them through `get_editor_property("notify_state_class")`) | the attack data tells the kind the pack will record for a hit (`Strong...`, `Charged...`); the swing direction and radius are context |
| `ANS_HitStunImmune`, `ANS_iFrames`, `ANS_CancelFrames`, `ANS_InputBuffer`, `ANS_DisableMovement`, `AN_PerformFollowUp`, `AN_EndAnimatingAbility` | same event list | pack-native hyperarmor and the commit/cancel windows around the swing |
| the jump heavy's impact time | the first `ANS_CollisionTrace` start of the strong montage; with the measured air time of 0.72 to 0.82 s (DECISIONS, jump 680 z velocity) it says whether the strike lands before or after the player does | the window is in montage seconds and does not depend on landing, but the feel does |

The probe prints one summary line per element, in a fixed shape the next step can parse:
`[G3Montage] WIN <style> <array> <montage> len=<s> rate=<r> trace=<start>-<end> [<start>-<end> ...] immune=<start>-<end>|none propose=<start>,<end>|none`
with `propose` computed as `start = max(0, first trace start - Lead)`, `end = last trace end`, Lead = 0.08 s (variable at the top of the script; open question Q4).

### 4.3 Where the numbers go and how a row is updated

Into `HyperArmorStart` and `HyperArmorEnd` of the rows of `/Game/OneBossFight/Data/DA_WeaponAttacks` (class `RPGWeaponAttackTable`, array `Rows` of `FRPGWeaponAttackRow`). `make_weapon_table.py` creates the asset once and never overwrites it (it holds what the owner tunes), so the rows are changed in place by an editor script (no PIE; KI-083 is about components in PIE, not about a data asset). The Python property names follow the snake case of the UPROPERTYs, as `make_weapon_table.py` already reads `weapon`, `kind`, `posture_damage`, `stamina_cost`, `bleed_buildup`, `note`: so `hyper_armor_start`, `hyper_armor_end` (UNKNOWN until run once; print `dir(row)` if it fails).

```python
# Scripts/Editor/set_weapon_windows.py (next session; the core, run in the open editor, no PIE)
import unreal
T = unreal.load_asset("/Game/OneBossFight/Data/DA_WeaponAttacks")
WINDOWS = {("ClaymoreCombatStyle", "STRONG"): (0.45, 0.78), ...}   # numbers from the probe, kind names as unreal.RPGAttackKind.<NAME>
rows = list(T.get_editor_property("rows"))              # copies of the structs
for r in rows:
    key = (str(r.get_editor_property("weapon")), r.get_editor_property("kind").name)
    if key in WINDOWS:
        r.set_editor_property("hyper_armor_start", WINDOWS[key][0])
        r.set_editor_property("hyper_armor_end", WINDOWS[key][1])
        r.set_editor_property("note", "measured from <montage>: trace %.2f-%.2f" % ...)
T.modify()
T.set_editor_property("rows", rows)                      # write the array back (the loop edited copies)
unreal.EditorAssetLibrary.save_loaded_asset(T)
# verify: reload (unreal.EditorAssetLibrary.load_asset) and print the rows; restart the editor once and read again
```

A row that does not exist is added by appending `unreal.RPGWeaponAttackRow()` with `weapon` and `kind` set (the table lookup falls back to the any-weapon row or the Fallback, so a missing row would silently give no window). The swing tracker copies the table at `BeginPlay` (`OriginalTable = LoadOrDefault()`), so the numbers apply from the next PIE. Also write the measured numbers into `FillDefaults` (a fresh asset and the built-in fallback table used when the asset is missing then agree), and add one automation assertion to `Hit.WeaponTable` for it; the asset itself stays the owner's to tune. Packaging: the table lives under `/Game/OneBossFight/Data`, an always-cooked directory (`DefaultGame.ini` l.22, KI-084), no change.

A runtime sanity check for each authored window belongs in `pie_builds.py` (section 5, B4): sample the montage position, `Status.HitStunImmune` and the weapon trace target's `bCollisionEnabled?` every frame of a real jump heavy and check that the immunity covers the whole trace window and ends within 0.15 s after it. For that the intake needs one test accessor, `URPGHitIntake::IsWeaponTraceActive()` (it already has `FindActiveTarget`, `RPGHitIntake.cpp` l.63).

## 5. The PIE driver plan `pie_builds.py` and the pure tests

### 5.1 Test hooks to build first (Python must not set properties in PIE: KI-083)

All as `UFUNCTION(BlueprintCallable/BlueprintPure)` on `URPGBuildLoadout` (found as `comp(pawn, "RPGBuildLoadout")`, like `comp(pawn, "RPGSwingTracker")` in the other drivers): `RequestBuildForTest(FString Name)` returns `"Accepted"`, `"Deferred"`, `"Same"` or `"Invalid"`; `GetChosenBuildName()`, `GetActualStyleName()`, `GetEquippedBuildName()` (from the style: the truth), `GetStateName()` (`Idle`, `Applying`, `Deferred`, `Failed`), `GetApplyAttemptCount()`, `GetDeferredCount()`, `GetApplyFailureCount()`, `GetInvalidRequestCount()`, `GetLastApplyText()`, `HasWeaponAbilityForTest(FString ClassName)` (uses `FindAbilityByClassName`), `IsCombatEnabled()`, `IsWeaponSlotLocked()`, `GetBuildLine()`, `ResetCountersForTest()`. On the HUD: `URPGBossHud::GetBuildLineText()`, `IsBuildLineShown()`. On the intake: `IsWeaponTraceActive()`. On the swing tracker: the chain stage in the swing text (2.5).

### 5.2 Scaffold and rules

Copy the scaffold of `pie_stamina_cost.py` (log prefix `[Builds]`, `check()`, `comp()`, `attr()`, `tags()`, `actors()`, `P()`, `place()`, `until()`, `press()`, `swing_once()`, a generator `script()` driven by a slate post-tick callback, `RESULT n/m passed` at the end, `finish()` that also restores `rpg.Build`). Run `pie_debug_overlay.py` once after an editor start. The rules of KI-083 and PROJECT_STATE "Gotchas": no `set_editor_property` on components, only the hooks; the pack destroys a dead boss, so no scenario kills it and the player death scenario (B10) is the last; heal the boss before every swing scenario (`dbg.debug_set_boss_health_fraction(1.0)`, as `place()` does); the driver carries a heartbeat and a missing pawn or boss guard (a silent driver is usually a missing boss); expected check count goes into `RunDrivers.ps1` (`@{ N = 'pie_builds'; K = 'R'; Min = <n>; T = 1200 }`).

The scenarios discover the claymore's and dual swords' montages from the probe, so a small dict `CAPS = {"Claymore": {"Strong": <montage or None>, "Charged": ..., "Falling": ...}, ...}` sits at the top of the driver, filled after `g3_probe_montages.py`; a kind that the weapon does not have is skipped with a logged line, not failed.

### 5.3 Checks (expected values from the table as it is now)

| # | Scenario | Pass criteria | Real input |
|---|---|---|---|
| B0 | start: `rpg.Build` empty, boss asleep (`enc.reset_for_test()`, not woken) | pawn and boss exist, `intake.is_hit_intake_bound()`, loadout exists | no |
| B1 | no build chosen (the guarantee of 2.3) | after 3 s: state `Idle`, `get_apply_attempt_count() == 0`, style `SwordCombatStyle`, HUD line `STARTER SWORD`, no deferral | no |
| B2 | `request_build_for_test("Strength")` while dormant | returns `Accepted`; within 8 s style `ClaymoreCombatStyle`, state `Idle`; `has_weapon_ability_for_test("GA_Claymore_Melee_C")`, no `GA_Sword_Melee_C`; a `BP_KwangSword_C` actor is attached to the pawn; HUD line starts `STRENGTH`; intake still bound (`is_hit_intake_bound()`) and the swing tracker still counts swings (B3 shows `weapon ClaymoreCombatStyle` in its swing text) | no |
| B3 | Strength numbers, boss held 110 cm in front (`place()`, `hold_for_test(True)`, `debug_refill_player()`) | light: swing text `weapon ClaymoreCombatStyle, kind Light`, stamina drop 15 (row -1 keeps the pack's cost, tolerance 0.6), hit record posture 18 (pool 100 to 82); strong (if it exists): `kind Strong`, drop 35, pool minus 30; jump heavy: `kind JumpHeavy`, drop 35, pool minus 38, three jump heavies break the pool (114 against 100, as `pie_posture_hits.py` C); charged (if it exists): `kind Charged`, drop 35, pool minus 38; records equal the boss's health drops (M7 rule); informational line `INFO hp per hit <style> <kind> <n>` for the balance (R5) | yes (`IA_NormalAttack`, `IA_StrongAttack`, `IA_ChargedAttack`, jump key `Gamepad_FaceButton_Bottom`) |
| B4 | hyperarmor from the authored row (needs 4.3 done) | in a real jump heavy: `Status.HitStunImmune` and `is_hyper_armor_active()` on for the whole authored window (samples every frame as in `pie_hyperarmor.py`), off outside it and after the swing; `intake.is_weapon_trace_active()` is inside the window; strong and charged the same; negative controls: a claymore light and the starter sword's jump heavy have no tag | yes |
| B5 | `request_build_for_test("Dex")` while dormant (from Strength) | `Accepted`; style `DualSwordCombatStyle` within 8 s; `GA_DuaSword_Melee_C` present, `GA_Claymore_Melee_C` gone; a `BP_DualSteelSwords_C` actor attached; weapon trace targets logged (expect a `MainWeapon` and an `Off-handWeapon`, R4); HUD line starts `DEXTERITY` | no |
| B6 | Dex numbers | light: stamina drop 10 (pack 15, extra -5, swing text `extra -5.0`), posture 6 per hit (pool 100 to 94), bleed buildup +20 per hit (`bleed.get_buildup()`); five light hits proc once (`get_proc_count() == 1`, last proc 52.5 = 10.5 percent of 500, threshold 120 after it, M12 rules); a three or four tap combo gives one swing per montage with chain stages 1, 2, 3 (4), one intake record per boss health drop (no double record from the two blades, R4); jump press: `JumpLight` (or `JumpHeavy` when the dual swords have a strong montage: R6) with the row's posture 6 or 14 | yes |
| B7 | deferral and lock (2.3, 2.4) | boss awake (`wake()`, `hold_for_test(True)`): `request_build_for_test("Strength")` returns `Deferred`, the style stays `DualSwordCombatStyle` for 4 s, `get_deferred_count() == 1`; a real `IA_QuickSlotRight` press during the fight does not leave the build (the slot is locked or the loadout re-equips: style back to the build's within 4 s, counted); after `enc.reset_for_test()` (dormant) the Strength build applies within 8 s | yes (quickslot press) |
| B8 | `Starter` returns the sword | `Accepted`; style `SwordCombatStyle`; `GA_Sword_Melee_C` present, the dual or claymore ability gone; HUD `STARTER SWORD` | no |
| B9 | selectors | console `rpg.Build Dex` (`unreal.SystemLibrary.execute_console_command(world, ...)`) sets the choice within 1 s; `rpg.Build Banana` is ignored and counted (`get_invalid_request_count()`); keys `F6`, `F7`, `F8` pressed with `unreal.RPGInputTestUtils.set_key_down(pc, "F6", True)` then `False` set Strength, Dex, Starter; the cvar is reset to empty | keys |
| B10 | the choice survives a respawn (LAST scenario) | choose Strength, apply; `dbg.debug_set_player_health(0.0)` (as `pie_player_death_reset.py` l.154); a new pawn appears, the encounter generation goes up; the new pawn's loadout re-applies Strength within 10 s, HUD line shows it; no deferral stuck | no |

Regression after the build (with `rpg.Build` empty): `RunDrivers.ps1 -Only pie_hit_intake,pie_posture_hits,pie_stamina_cost,pie_hyperarmor,pie_bleed` (36, 25, 17, 23, 19 checks), then `pie_player_death_reset` (25), `pie_boss_hud` (29, the HUD got two text blocks) and the automation suite (19 tests today).

### 5.4 Pure automation tests (`Player/RPGBuildRules.h`, new test `OneBossFight.Build.Rules` in `Tests/RPGAutomationTests.cpp`, same style as `FRPGDamageDecideTest` which walks all 32 flag combinations)

1. `Parse`: `strength`, `Strength`, `STR`, `dex`, `Dexterity`, `starter`, `sword`, `none` and empty map as listed in 3.1; `banana` is invalid.
2. Style mapping round trip: Strength to `ClaymoreCombatStyle` and back; Dex to `DualSwordCombatStyle`, `TwinbladeCombatStyle` also gives Dex; Starter to `SwordCombatStyle`; `SwordAndShieldCombatStyle` counts as Starter (R8); `PolearmCombatStyle`, `UnarmedCombatStyle` give off-build.
3. `Decide`: every combination of {chosen is a build, style matches, style known, boss dormant, player dead, player busy, apply running, apply age below or above `VerifySeconds`, attempts below or at `MaxAttempts`}: the invariants are (a) Unchosen never starts anything, (b) an awake boss never gets a start, (c) a dead or busy player never gets a start, (d) a matching style never starts, (e) no start while an apply is younger than `VerifySeconds`, (f) after `MaxAttempts` the answer is GiveUp, never another Start.
4. `BuildLine`: for every pair (chosen, actual style) the line names the build of the ACTUAL style and never the chosen build's word unless they agree; the suffix is `(EQUIPPING...)`, `(NEXT FIGHT)` or `(NOT EQUIPPED)` exactly in the Applying, Deferred and Failed states.
5. Table: the three build styles have a row for all six kinds (no Fallback is reachable), Strength heavy kinds cost 35, Dex 10, Dex bleed 20 on every kind, Strength 0; (the arithmetic tests of `Hit.WeaponTable` stay).
6. Window rules: `ProposeWindow(TraceStart, TraceEnd, Lead, Length)` clamps to `[0, Length]` and answers none for an empty trace; `ValidWindow(Start, End, Length)`.
7. `PackWiring` (existing test): `URPGBuildLoadout::CheckPackNames` for the names the loadout reads (`BP_CombatComponent_C.CurrentCombatStyle`, `BP_EquipmentComponent_C.EquipmentSlots`, the functions it calls, the three item assets, the three style assets), exactly like `URPGHitIntake::CheckPackNames` (`RPGAutomationTests.cpp` l.1058). `Content.CookCoverage` checks the new `/Game` literals by itself.
8. A content check without a world: after 4.3, the asset's `ClaymoreCombatStyle` Strong, JumpHeavy and Charged rows have `HasHyperArmor()` and the window ends inside 5 s, so an overwrite of the asset cannot silently drop the numbers.

## 6. Risks and open design questions

### 6.1 Risks

| # | Risk | Evidence | Mitigation |
|---|---|---|---|
| R1 | The pack's equip path (signatures, which component, what it needs: the claymore item is not in the player's `PlayerInfo`, an inventory with `Max Slots`, `EquipSpawnSetting`) may not accept a runtime `Update Equip Slot Item` the way the plan assumes | names only [names] | Probe first (section 7). Fallback order in 2.3: equipment path, then the quickslot path for items already in the list. If neither works for the claymore, the last resort is spawning the pack's own flow by adding the item through `Add Item` and pressing the quickslot (real input, slow but pack-native); do not set the style by hand |
| R2 | The probe's `FUNCTION` dump covers the pawn's components only (`DumpFunctionsOf` is private and called with the player pawn). If the inventory component lives on the player controller, the signature of `Add Item` is not printed | `RPGCombatDebug.cpp` l.286-329 | Add `DumpControllerFunctions()` (one public UFUNCTION calling `DumpFunctionsOf(GetFirstPlayerController())`) in the same build as the loadout, rerun the probe. The probe already prints the controller's component class names and variables |
| R3 | A respawn creates a new pawn with the pack's default sword while the encounter reset also runs: for a tick or two the loadout sees an awake boss; the pack's equipment initialisation may still be running (style None) | `RPGBossEncounter.h` (reset on a new pawn), `Decide` Wait/Defer rows | `Decide` waits for a known style, counts the deferral, never gives up before `MaxAttempts`; B10 covers it |
| R4 | The dual swords have two weapon trace targets (`MainWeapon` and `Off-handWeapon`). `RPGHitIntake::FindActiveTarget` returns the first target with `bCollisionEnabled?`, and a swing may hit twice (one record per OnHit event) or read the hit data of the other blade | strings of `BP_BaseDualWeapon` [names], `RPGHitIntake.cpp` l.63-90 | B5 logs the targets, B6 counts intake records against boss health drops (the M7 criterion). If records double, de-duplicate per swing and target in the intake (the same hit set per attack instance) |
| R5 | HP per hit differs by weapon and nobody knows how: the starter sword item has `GE_ToughSwordAttributeModifiers`, the claymore item has no granted effect in its name table, so the claymore may hit weaker than the starter sword; the Freeze wants Strength to have higher HP and posture damage than Dex | strings of the item assets [names], Freeze 20.1 | `pie_builds.py` prints HP per hit per weapon and kind (informational); decide at M14 (Q5) |
| R6 | The claymore or the dual swords may have no `StrongAttackMontages` (the DECISIONS note names twinblades and polearm as having none; the claymore and the dual swords were never dumped). `air_heavy_selector.py` then plays the jump light and the Freeze's jump heavy does not exist for that weapon | DECISIONS "Jump heavy (built)", UNKNOWN | The montage probe answers it. If missing: put a heavy montage into the weapon's `StrongAttackMontages` at run time by reflection on the granted ability instance (no pack asset edit; candidates on disk: dual swords `Attack_GuardBreak_A` / `_C`), or ask the owner to accept a pack asset edit like `air_light_attacks.py` did |
| R7 | The pack's quickslot arrows stay live in the fight (polearm, bow, staff, spells, shield may be reachable): rows are missing (Fallback) and "build chosen before the fight" is not true | `GA_Quickslot_C` map [abil l.770], `PlayerInfo` import table [names] | 2.4: HUD truth rule now, slot lock or re-equip (Q2) |
| R8 | The starter sword with a shield equipped is `SwordAndShieldCombatStyle` (`ToughSword.MergableWeapons`), which has no table row (Fallback: 20 posture). The existing drivers all saw `SwordCombatStyle`, so the default player has no shield, but a Starter apply might merge | strings of `ToughSword` [names], `RPGWeaponAttackTable.cpp` | Treat it as Starter in `BuildOfStyle`; add rows for `SwordAndShieldCombatStyle` (copy of the sword rows) to `FillDefaults` and the asset |
| R9 | `rpg.Build` is process wide and survives a PIE (like `rpg.Legend`): a value left in an editor session changes the next test run | `DECISIONS` Legend pass | `Scripts/Editor/build_off.py` in the warm-up of `RunDrivers.ps1`; `pie_builds.py` resets it; the subsystem logs the value it starts with |
| R10 | The HUD line may overlap a pack widget; the pack's top-left extents at 1080p are not measured | picture only | top centre; `Shot ShowUI` in PIE after the build (as G2-12 did) |
| R11 | `OnCombatStyleBegin` may not be broadcast on every weapon change | signature known [dump2], behaviour not | The loadout polls `CurrentCombatStyle` every 0.1 s anyway; the event is an optimisation only |
| R12 | Tooling: the UnrealClaude plugin can crash the editor right after a script (KI-055); Python in PIE must not set component properties (KI-083); the first PIE on a cold shader cache fails timing drivers (KI-081) | KNOWN_ISSUES | save before scripts, hooks instead of properties, warm up and restart once |

### 6.2 Open questions for the owner (five, each with a recommendation)

| # | Question | Recommendation |
|---|---|---|
| Q1 | May the loadout add the claymore item to the player's inventory and equip it at run time by calling the pack's own functions (`Add Item`, `Update Equip Slot Item`)? It edits no asset, it is what picking the sword up in the pack's demo does, but it is a call into the pack's inventory that nobody tested. | Yes. If the probe shows the call cannot work, ask for permission to add `KwangSword` to `PlayerInfo.Default Equipment` as a pack asset edit (a git-ignored asset, like the poise edits), documented in PROJECT_STATE. |
| Q2 | Should the weapon slot be locked from the moment the boss wakes until it resets or is gone (no quickslot cycling mid-fight)? | Yes: the Freeze says the build is chosen before the fight, the other quickslot weapons have no table rows, and mixed builds would make M14 balance runs meaningless. Use `Set Equip Slot Disabled` if the probe shows it stops the cycle, else re-equip and count. |
| Q3 | Which weapon is Dex now: the pack's `DualSteelSwords` (style `DualSwordCombatStyle`) while Antigravity's curved dex sword meshes (M-05) wait for a visual swap, or the twinblades? | Dual swords. They have the block, air, dash and guard break clips and probably the four-stage chain the Freeze asks for; the table keeps `TwinbladeCombatStyle` rows as a spare. The M-05 meshes replace the pack sword meshes later as a visual task, with no code change. |
| Q4 | Which rows get a hyperarmor window, and how long before the first trace window may it start? | Strength `Strong`, `JumpHeavy` and `Charged` get the measured trace window with a lead of 0.08 s; Dex and the starter sword get none (Freeze 5 and 20.1 name the Strength downswing only). |
| Q5 | Do we need a per-weapon HP damage knob (a new table column applied through the pack's attack attributes), or do we accept the pack's HP per hit if the measured order is Strength above Dex? | Measure first (`pie_builds.py` prints HP per hit). No new column until the M14 balance runs show a problem; the posture, stamina and bleed columns already separate the builds. |

Also decided by default (say so if you disagree): the sword stays the default and the third choice ("Starter"), so every existing driver and the first minutes of the game are unchanged; the choice is kept per game instance only (not saved to disk); the shrine, when it exists, is a distance check plus a key, not the pack's interaction system.

## 7. The probe scripts (written, syntax-checked with `ast.parse` and `pyflakes`, NOT run)

Both follow the conventions of `pie_g3_probe.py` and `inspect_boss_montages.py`. Run in the open editor on `L_SevarogArena` (the plugin bridge on port 3000), nothing else running in the editor:

```
MSYS_NO_PATHCONV=1 python -I Scripts/run_in_editor.py Scripts/Editor/g3_probe_montages.py     # editor only, no PIE, seconds
MSYS_NO_PATHCONV=1 python -I Scripts/run_in_editor.py Scripts/Editor/pie_debug_overlay.py     # warm-up once after an editor start
MSYS_NO_PATHCONV=1 python -I Scripts/run_in_editor.py Scripts/Editor/g3_probe_equip.py        # starts a PIE, ends it itself after about 30 s
```

They use only what the current source already builds: `URPGCombatDebug::DumpObject` and `DumpPlayerFunctions`, `URPGMontageUtils::DescribeNotifies`, `URPGInputTestUtils::InjectAction` and `SetKeyDown`, `URPGWeaponAttackTable` (all in `Source/OneBossFight`, no new C++ needed for the probes).

Read the output in `Saved/Logs/OneBossFight.log` (lines `[G3Montage]`, `[G3Probe]`, and for the equip probe the `LogRPGDebug` `OBJECT` and `FUNCTION` lines between its `=== BEGIN` markers). Save the relevant part into `Documentation/` or the scratchpad before the next editor start (the log rotates).

| File | Lines | What it prints | Answers |
|---|---|---|---|
| `Scripts/Editor/g3_probe_montages.py` | 116 | for the sword, claymore, dual sword and twinblade abilities: the length of each array and, per element, the montage, length, rate scale, struct `PlayRate` and `EndTimeMultiplier`, every notify (class, time, duration) through `URPGMontageUtils::DescribeNotifies`, the `ANS_CollisionTrace` properties, `ANS_HitStunImmune` windows, the `WIN ...` summary line with the proposed `HyperArmorStart,End`; the claymore rows of `DA_WeaponAttacks` and any row that has a window | 1.1 #7 and #8 (which montage is in which array, does the claymore or the dual sword have a strong or a charged montage), 2.5 (length of the dual sword chain), 4.1 (does a montage already carry `ANS_HitStunImmune`), 4.2 (the numbers), R6 |
| `Scripts/Editor/g3_probe_equip.py` | 148 | before the PIE: `PlayerInfo.Default Combat Style`, `Default Equipment`, `Default Inventory` in full; in the PIE: the components of the pawn and of the controller, the combat, equipment and inventory components with variables (depth 2) and the `EquipmentSlots` structs in full, the three weapon items and five style assets, the pawn components' Blueprint functions with parameter names (`FUNCTION` lines), then four presses of `IA_QuickSlotRight` (two out of combat, `Ability.EnterCombat`, two in combat) with the style, the combat flag, the montage and the slots after each step | 1.1 #10 and #11 (what the player starts with, the slot of the weapon, is the dual sword in the list), 1.2 #12 to #15 (where the components live, parameter names of `Update Equip Slot Item`, `Add Item`, `Set Equip Slot Disabled`), 1.3 (does the quickslot cycle work out of combat, what changes: style, abilities, slots), R1, R2, R7, R8 |

What the equip probe does NOT cover (next steps if it leaves a gap): the functions of components on the player controller (R2), the effect of calling `Update Equip Slot Item` itself (a second probe or the first loadout prototype does that), the effect of `Set Equip Slot Disabled` on the cycle.

A note on how I read the pack: the .uasset files are binary, so the facts marked [names] come from a byte-level extraction of the printable strings (name table and import table) of a few assets, done read-only with a throw-away script in the session scratchpad (`uas_strings.py`, not part of the project). They give names of functions, variables and referenced assets, never behaviour or parameter order; they are leads for the probes, which is why none of them is marked as a settled fact about logic.

## Appendix: probe results (2026-10-22)

`g3_probe_montages.py` ran (no PIE, reads only). The weapon abilities' montages with the first and last trace window of `ANS_CollisionTrace` in montage seconds, and the proposed hyperarmor window (first trace start minus the 0.08 s lead, last trace end). **No montage carries the pack's own `ANS_HitStunImmune`.** The Claymore's strong, charged and falling montages are the SAME assets as the sword's (strong `Ability_E_Anim_Montage` trace 0.432 to 0.618 s, charged `ChargedAttack_Montage` 0.503 to 1.005 s); the dual swords have their own strong montages (`Attack_Melee_C_Montage` 0.161 to 0.336, `Attack_GuardBreak_C_Montage` 0.342 to 0.621) and a falling attack `Attack_Melee_Air_Montage` (two trace targets, 0.208 to 0.350 and 0.211 to 0.343: the off-hand blade, R4).

```
WIN ClaymoreCombatStyle StrongAttackMontages Ability_E_Anim_Montage len=1.267 trace=0.432-0.618 propose=0.352,0.618
WIN ClaymoreCombatStyle ChargedAttackMontages ChargedAttack_Montage len=2.700 trace=0.503-1.005 propose=0.423,1.005
WIN ClaymoreCombatStyle FallingAttackMontages PrimaryAttack_A_Slow_Montage len=1.200 trace=0.136-0.439 propose=0.056,0.439
WIN ClaymoreCombatStyle AttackMontages PrimaryAttack_A_Slow_Montage len=1.200 trace=0.136-0.439
WIN ClaymoreCombatStyle AttackMontages PrimaryAttack_B_Slow_Montage len=1.267 trace=0.143-0.446
WIN ClaymoreCombatStyle AttackMontages PrimaryAttack_C_Slow_Montage len=1.267 trace=0.143-0.446
WIN ClaymoreCombatStyle AttackMontages PrimaryAttack_D_Slow_Montage len=1.467 trace=0.143-0.446
WIN DualSwordCombatStyle AttackMontages Attack01_Montage len=0.733 trace=0.176-0.335
WIN DualSwordCombatStyle AttackMontages Attack_Melee_A_Montage len=1.167 trace=0.130-0.375
WIN DualSwordCombatStyle AttackMontages Attack_Melee_B_Montage len=1.267 trace=0.176-0.344
WIN DualSwordCombatStyle StrongAttackMontages Attack_Melee_C_Montage len=1.200 trace=0.161-0.336
WIN DualSwordCombatStyle StrongAttackMontages Attack_GuardBreak_C_Montage len=1.133 trace=0.342-0.621
WIN DualSwordCombatStyle FallingAttackMontages Attack_Melee_Air_Montage len=1.000 trace=0.208-0.350 and 0.211-0.343
WIN DualSwordCombatStyle SprintAttackMontages Attack_Melee_C_Dash_Montage len=0.933 trace=0.276-0.382 and 0.277-0.385
WIN SwordCombatStyle (the starter) StrongAttackMontages Ability_E_Anim_Montage len=1.267 trace=0.432-0.618
WIN SwordCombatStyle AttackMontages Attack_PrimaryA_Montage len=1.667 trace=0.350-0.536; B 1.400 s 0.350-0.536; C 1.867 s 0.597-0.783
WIN TwinbladeCombatStyle AttackMontages A 1.333 s 0.098-0.335; B 1.333 s 0.163-0.339; C 1.233 s 0.134-0.335; D 1.333 s 0.041-0.402 (two windows); E 1.233 s 0.127-0.342
```

`g3_probe_equip.py` ran in PIE. Facts: the player's pawn has `BP_CombatComponent_C`, `BP_EquipmentComponent_C`, `BP_AdvancedAbilitySystemComponent_C` and `BP_InputBufferComponent_C`; the **inventory component `BP_PlayerInventoryComponent_C` lives on the player controller** (`BP_AdvancedPlayerController_C`), so R2 applies (a controller function dump is needed before the loadout). `PlayerInfo` starts with `UnarmedCombatStyle` and the sword item. The pack's own quickslot press toggles between `SwordCombatStyle` and `MagicCombatStyle` (equipment slot `ActiveItemIndex` 0 and 1) both out of and in combat (Q2: the claymore and dual swords are not in the quickslot list). The full dump (variables, functions with parameter names) is in the editor log as `LogRPGDebug` lines of that run (not saved to a file: rerun the probe and redirect the log if needed).
