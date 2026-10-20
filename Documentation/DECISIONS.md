# Decisions

| Date | Decision | Reason | Status |
|---|---|---|---|
| 2026-10-18 | UE **5.5.4**, pinned | User choice; stable release with Enhanced Input, StateTree | Locked |
| 2026-10-18 | C++ module name `OneBossFight` | Matches project name; single primary game module | Locked |
| 2026-10-18 | Custom C++ combat, **no GAS** | Souls-style frame-data combat (animation-owned windows); GAS adds overhead and fights that model | Locked |
| 2026-10-18 | Boss AI = weighted C++ selector in `UBossCombatComponent` + thin StateTree for top-level states; no Behavior Tree | Mirrors distance-gated weighted action selection used by Souls-style bosses | Locked |
| 2026-10-18 | Win64 only, 1920x1080, 120 FPS target on RTX 2060 Super | Per `Idea/IDEA.md` | Superseded 2026-10-20: user said 60 FPS is fine and look comes first (best-looking, detailed, alive arena); the 150k triangle budget no longer binds |
| 2026-10-18 | Git LFS for `.uasset`, `.umap`, art, audio | Binary assets | Done |
| 2026-10-18 | Editor MCP: UnrealClaude plugin via node bridge (`localhost:3000`); Blender MCP connected | Lets Claude edit Blueprints, assets, scenes | Done |
| 2026-10-18 | codex-aider-bridge pipeline waived for this project; Claude writes C++ directly | User decision | Locked |
| 2026-10-18 | Module headers are included as `"Folder/File.h"`; module root added to include paths in `OneBossFight.Build.cs` | Feature folders (Characters/, Arena/, Benchmark/, Core/) without Public/Private split | Done |
| 2026-10-18 | `bEnableLegacyInputScales=False` in `DefaultInput.ini` | Legacy scales multiply pitch by a negative factor and flip look direction; we map raw mouse/stick values | Done |
| 2026-10-18 | Look sign convention: IA_Look Y positive = look up; mouse mapped raw (no Negate) | Pairs with the setting above; `LookSensitivity` tunes feel | Provisional, confirm in playtest |
| 2026-10-18 | Input assets under `/Game/OneBossFight/Input/` (IA_Move, IA_Look, IA_Jump, IA_Sprint, IMC_Default) | Keyboard/mouse + gamepad, created via Unreal MCP | Done |
| 2026-10-18 | Benchmark runner (`ARPGBenchmarkRunner`) writes `Saved/Benchmark/<label>_<time>/frames.csv` + `summary.json`; run with `-RPGBenchmark -RPGBenchmarkQuit -RPGBenchmarkLabel=<name>` | Repeatable, comparable frame-time capture | Done |
| 2026-10-18 | PythonScriptPlugin + EditorScriptingUtilities enabled; content built by `Scripts/Editor/setup_m1_content.py` run headless | Reproducible, reviewable content setup without a GUI session | Done |
| 2026-10-18 | Benchmark records game/render/GPU thread ms alongside frame time | Identify the bottleneck, not just FPS | Done |

## Provisional

| Item | Note |
|---|---|
| Toolchain | Visual Studio 2026 (18.x), MSVC 14.51, Windows SDK 10.0.26100. UE 5.5 prefers MSVC 14.38 and warns "not a preferred version". M0 module compiled with 0 errors. Revisit if a later build fails: install MSVC 14.38 (17.8) from the VS Installer. |
| Target PC | RTX 2060 Super 8 GB. CPU, RAM, driver to be recorded at first baseline (M1). |

## M2 asset inspection (2026-10-18, reports in `Documentation/AssetReports/`)

| Pack | Height cm | Skeleton bones | Anims | Fits |
|---|---|---|---|---|
| Greystone | ~206 | 180 | 154 seq, 4 montages | Player: A/B/C/D light chain with Fast/Med/Slow + recovery, Deflect (parry), jump set, hit react, stun, death. No dodge, no block idle. |
| Steel | ~355 (needs scaling) | 178 | 186 seq, 5 montages | Shield block set, guard break, dash with root motion (Test_FullDash). Oversized. |
| Grux | ~222-256 | 176 | 108 seq, 6 montages | Boss: PrimaryAttack LA/RA/LB/RB, FourStrikes combo montage, Stampede, Ultimate_Roar, LevelStart. Only a stun idle. |
| Sevarog | ~311 | 155 | 144 seq, 3 montages | Boss: Swing1-3 each Fast/Medium/Slow with Return2Idle, Ultimate_Swing, Swing_In_Air, Cast, Stun start/loop/end, LevelStart, knockback. One death. |

All four use their own non-Mannequin skeleton, in-place animation (root motion only on 2 Steel clips), and no dodge-roll. Provisional picks: **player Greystone, boss Sevarog** (Grux is the fallback). No retargeting is needed to run each character with its own AnimBP; one is needed only to borrow animations across skeletons (e.g. a dash or roll). The inspection script found no anim notifies; treat that as unconfirmed until viewed in the editor.

## M2 visual proof (2026-10-18)

`L_AssetProof` (built by `Scripts/Editor/build_asset_proof_map.py`) plays 12 Greystone and 12 Sevarog animations in a row, each on its own skeleton. Screenshots in `Documentation/AssetProof/`.

- Confirmed visually: Greystone wields a **sword and a shield** (Deflect raises the shield: usable as the parry/guard animation). Light A to D attack poses play on the Greystone mesh. Sevarog plays Swing 2/3, Ultimate Swing (hammer raised), Cast, Hit Front, Stun Loop, Death (collapsing) and Level Start (intro), all on the Sevarog mesh with correct proportions (about 3.1 m).
- Not yet viewed: Greystone Death/Hit/Jump and Sevarog Idle/Jog/Swing In Air (they are in the map; run it to check).
- Both characters work with their own skeleton and no retargeting. Confirmed gaps: **dodge roll** (neither pack), a guard-idle for Greystone, a boss phase-transition roar (Sevarog), a boss lunge (use Swing_In_Air or Speedburst, to be checked).
- Authoring note: single-node animation persists only through `AnimationData.AnimToPlay`; `play_animation` is runtime-only. The editor skips animating skeletal meshes unless `bUpdateAnimationInEditor` is set, and the viewport throttles when the editor is not the foreground window (captures then show stale frames).
- The Paragon `*PlayerCharacter` Blueprints log compile errors (missing VR function). They are unused; delete them with the unused packs.

## M3 player combat (2026-10-18)

| Decision | Reason |
|---|---|
| All combat state lives in C++ components: `URPGAttributeComponent`, `URPGCombatComponent`, `URPGMeleeTraceComponent`, `URPGTargetLockComponent`; data in `URPGWeaponData` (Data Asset) | Testable headlessly; new weapons and bosses are data |
| Single damage path: `URPGCombatComponent::ProcessIncomingHit` | One place for i-frames, block, poise, stagger, death |
| Windows come from anim notify states (`RPGANS_HitWindow`, `ComboWindow`, `IFrames`, `CancelWindow`); without a montage the same windows run from fallback times | Animation owns timing like Souls games; combat is testable without animations |
| Melee trace sweeps each sample point from its previous to current position every frame, once per swing per target | Frame-rate independent hits; verified from 1 to 480 frames per crossing |
| Hit windows in the montages were placed from the sword tip speed (peak above 40 %), `Scripts/Editor/setup_m3_content.py` | First pass matches the visible swing; tune in the montage editor |
| Montages are built from Greystone sequences and play in slot `UpperBody` (the only slot in its AnimBP) | The factory default `DefaultSlot` does not exist there |
| Input: LMB light, RMB heavy, Space dodge, Q or MMB lock-on, Jump moved to F (Elden Ring style); gamepad RB, RT, B, R3; gamepad sprint moves to L3 | Space is the Souls dodge key |
| Dodge: stamina 25 once, 0.05 to 0.35 s i-frames, dash 900 cm/s, no animation yet (KI-007) | No roll in any pack |
| Combat: team ids (player 0, enemies 1), early inputs buffered 0.4 s, attacks need stamina above zero and may empty it | Souls-like rules |

## M4 boss and encounter (2026-10-18)

| Decision | Reason |
|---|---|
| Boss brain is `URPGBossCombatComponent`: weighted selection (distance, facing arc, phase, cooldown, repeat limit) with the random roll passed in | Distribution and rules are unit-tested |
| Boss attacks are `URPGBossAttackData` assets wrapping an `FRPGAttackData`; performing them reuses `URPGCombatComponent` (windows, hit trace, poise, death) | Same damage path as the player; no second combat system |
| Top-level boss flow (Dormant, Entrance, Combat, PhaseTransition, Dead) is owned by the C++ boss component and mirrored by a **StateTree asset** (`ST_Boss`, schema StateTree Component) | As originally locked. Thin mirror: custom condition `RPG Boss State Is` and task `RPG Boss Mirror`; each state has the task, every state transitions on tick to any state the component is in. The tree is built and compiled by `URPGBossStateTreeBuilder` (`Scripts/Editor/setup_m4_statetree.py`), so it is reproducible. StateTree and GameplayStateTree plugins enabled; modules StateTreeModule, GameplayStateTreeModule, AIModule, GameplayTasks added |
| Phase changes once per threshold: the first hit across it makes the boss untouchable, so same-frame hits cannot start a second transition | Test `Boss.PhaseAndFlow` |
| Boss is untouchable while Dormant, in Entrance and during PhaseTransition (`SetExternalInvulnerable`, independent of i-frames) | No cheese during roars |
| `URPGEncounterSubsystem` (world subsystem) runs start, victory, defeat, auto-retry after 4 s, and `VerifyResetInvariants` after every reset; `ARPGEncounterTrigger` starts it | Reset leaves no stale state: 10 cycles in `Boss.Encounter.ResetCycles` |
| Boss moves by direct steering (no navmesh), turns toward the player until the first hit window, then commits | Greybox arena; tracking cutoff is the fairness rule |
| `ARPGHUD` canvas HUD: player bars, boss bar, YOU DIED / ENEMY FELLED | No asset dependency; UMG in polish |
| Boss attacks use Sevarog montages in the `FullBody` slot; `AM_Sevarog_PhaseRoar` reuses `Ultimate_Targeting`, `Lightning` is a radial placeholder using `Cast` | No roar or lightning animation in the pack |

## M5 content and weapons (2026-10-18, partly done: needs assets from you)

| Decision | Reason |
|---|---|
| A weapon is a `URPGWeaponData` asset only: attacks, trace sockets, swing sound, impact sound and effect, hit-stop. Three exist (Sword, Quick Blade, Greatblade), all from Greystone's own animations; no code per weapon | Proves the data pipeline. Play rate makes them feel different (1.3 / 1.0 / 0.8 lights) |
| `EquipWeapon` only while free to act; player cycles with R or D-pad up; a retry re-equips the first weapon | No weapon swap mid-attack; reset invariants |
| `URPGCombatFeedbackData` (pain, heavy pain, block, dodge, death sounds; block effect) per character; weapon impact feedback lives on the weapon | Sounds follow who is hit, effects follow what hit them |
| Hit-stop: both fighters' `CustomTimeDilation` drops to 0.05 for the weapon's real-time `HitStopSeconds`, ticked on the real-time ticker, cleared on reset and EndPlay | World time stays normal; no fighter can be left frozen |
| Victory slow motion: world time 0.25 for 2.5 real seconds, cleared on reset | Presentation of the kill |
| Audio from the packs is voice only (efforts, pain, death); particle effects are Paragon Cascade systems | The packs contain no weapon impact, whoosh or footstep sounds, and no Niagara |
| Heavy attacks now use the `Attack_*_Slow` sequences (0.8 s) instead of the 3 s `Attack_RMB` | KI-008 |
| Radial notify (`RPG Radial Hit`) carries an optional effect and sound; Sevarog's Shockwave uses `P_UltMeshArc_Expanding`, Lightning uses `P_Sevarog_Subjugate_Blast` | Placeholders until lightning VFX is authored |

## Playtest fixes (2026-10-18)

| Decision | Reason |
|---|---|
| Move and Look mappings are rebuilt natively by `URPGInputAuthoring::ConfigureMoveAndLook` (`Scripts/Editor/setup_input_fix.py`) | The modifiers made through the editor MCP were saved empty: W, S and A all moved right, and the sticks had no dead zone (camera drift) |
| Stick look is degrees per second (dead zone 0.25, 150 deg/s, scaled by frame time); mouse stays raw | Same turn speed at any frame rate |
| While a gamepad is in use (stick, face button, shoulder or trigger active) and the right stick is idle, mouse movement under 20 counts per frame is ignored | A mouse on the desk must not turn the camera while playing on the pad |
| Block (hold LCtrl / LB) and parry: the first 0.25 s after a fresh press is a parry (no damage, no stamina, attacker staggered 1.5 s). A guard resumed after an action is a plain block | Souls-style guard and riposte window |
| Dodge speed is driven every tick (1100 cm/s easing out over 0.6 s, about 3.5 m) instead of one launch that friction ate | The dash was too short to read as a dodge |
| Greystone guard uses `Deflect_InPlace` (1.1 s) as a one-shot when the guard rises | Only shield animation in the pack |

## Camera and M6 start (2026-10-18)

| Decision | Reason |
|---|---|
| Look pitch limited to -45..+35 degrees, eases back to -12 after 1.5 s without look input (not while locked on); boom does a collision probe | Playtest: the camera ended up looking at the ground too often |
| Fight benchmark: `-RPGBenchmark -RPGBenchmarkFight` on `L_Greybox` runs the real encounter with an invulnerable bot player; boss forced into phase 2 at 30 s and healed so it never dies | M6 measures the worst case (boss, effects, hit-stop, HUD), not an empty arena |

## Performance deferred (2026-10-18)

| Decision | Reason |
|---|---|
| M6 optimization is parked until mechanics, engineering and environment integration are complete; first fight captures are recorded in `PERFORMANCE_LOG.md` and no render setting was changed | User decision: measure once the content is final |

## UI, settings and boss combo (2026-10-18)

| Decision | Reason |
|---|---|
| HUD (`URPGHUDWidget`) and pause menu (`URPGPauseMenuWidget`) are UMG widgets whose trees are built in C++; the canvas `ARPGHUD` was deleted | No Widget Blueprint to keep in sync; behavior is code-reviewable. Screenshots in `Documentation/UI/` |
| `ARPGPlayerController` creates the HUD and menu; Escape, P or gamepad Start toggles the menu (plain key bindings that run while paused) | Works without extra input assets; Escape also stops Play in the editor, so use P there |
| Settings: look sensitivity (0.2 to 3), invert Y, master volume, saved to `Saved/SaveGames/RPGSettings.sav` by `URPGSettingsSubsystem` and applied at startup | Player options survive restarts; values are clamped on save and load |
| Boss combos: `URPGBossAttackData::FollowUps` run back to back after the first hit if the target is within `FollowUpMaxRange` and arc; a stagger or an escaped target ends the chain. Sevarog has a Triple Combo (Sweep, Backhand, Overhead) | Boss 3-hit combo (KI-013) |

## M7 asset integration (2026-10-18)

| Decision | Reason |
|---|---|
| Third-party packs are imported with `Scripts/ImportAssetClosure.py`, which copies an asset plus everything it references and keeps the original `/Game/...` paths. The brief's plan to copy folders into `Content/OneBossFight/...` was not followed | Packages reference each other by absolute path; a moved copy loads with every reference broken. Closure import also keeps the imports small (about 235 MB, the bulk is the Deadly Ruins textures) |
| New packs are git-ignored like the Paragon packs; `ASSET_LICENSES.md` lists them with `to be filled` where the creator and licence are unknown | The packs were downloaded without their listing pages; licences are not guessed |
| Weapon sounds: `SwingSoundVariants` and `ImpactSoundVariants` (random pick) are layered with the existing single sounds, so the Paragon voice effort still plays with the new whoosh | One data field set per weapon, no code per sound; voice stays |
| Niagara slots added next to the Cascade ones (`ImpactNiagara`, `BlockNiagara`, `ParryNiagara`, `RPGAN_RadialHit::NiagaraEffect`) and a new `RPGAN_SpawnEffect` notify for ground telegraphs | Existing assets keep working; Cascade is the fallback |
| Dodge roll: Mage pack roll retargeted with an IK rig auto-generated for Greystone. One forward roll serves every direction because the character turns to the dodge direction first; a no-input dodge plays the backward roll. The roll's travel is root motion in the root bone (`fix_roll_root_motion.py`, 3.2 m; the retarget had left it in the pelvis, which made the mesh drift off the capsule); the code dash only runs for montages without root motion. The montage is squeezed to `DodgeDuration` with short blends and i-frames stay on the timed fallback | Four directional rolls would never be seen; i-frames independent of notifies in a retargeted asset |
| Boss lightning: Niagara bolt `NS_Thunder_Beam7` after a 0.45 s `NS_Free_Spells_Circle` telegraph; attack renamed `Lightning Strike` | The telegraph makes the attack fair; the bolt pack needed stand-in materials (KI-023) |
| Arena art pass lives in `ARPGGreyboxArena` as optional mesh and material properties; the pillar that would stand in the arch's doorway is skipped | The greybox and its tests keep working; the doorway stays walkable (`OneBossFight.Arena.ArtPass` checks it) |
| Arena stone uses UV-tiled instances of the Deadly Ruins detail master with box-projected UVs on the Blender meshes (one repeat per 4 m) | The Blender unwrap stretched every tiling texture; the pack's trim-sheet materials need atlas UVs |
| Display font Cinzel for the HUD and menus through `RPGUIStyle::MakeFont` (engine font when the asset is missing) | One place to change the look |
| `OneBossFight.Content.Wiring` test fails when a required boss asset, weapon sound, feedback or dodge montage is missing | A boss data asset had silently disappeared once |

## Advanced ARPG pack as the backbone (2026-10-19)

The earlier "custom C++ combat, no GAS" decision is superseded by the user's instruction to use the Advanced ARPG Combat
System V3 pack fully, in stages. Our C++ combat stays in the project and keeps its tests until the pack path shows parity.
Pack details: `ARPG_PACK_INSPECTION.md`.

| Stage | What | State |
|---|---|---|
| 1 | Import the whole pack at its original paths (`Content/AdvancedARPGCombat`, 2,506 files, 2.9 GB, git-ignored) with `Scripts/ImportAssetClosure.py` | Done |
| 1b | Merge its config: gameplay tag tables (`Config/DefaultGameplayTags.ini`), `Interactable` trace channel, `Character` surface type, camera-ignore on the Pawn profiles, CommonUI and EnhancedInput plugins | Done |
| 2 | Project defaults switched to the pack: `BP_AdvancedGameMode`, `BP_AdvancedGameInstance`, default map `CombatSystemTestLevel`. `L_Greybox` overrides the game mode back to our `BP_RPGGameMode` in its World Settings so our boss fight still runs | Done. The pack's demo level plays inside this project (its player, 24 AI controllers, bosses, vendor, bonfires and loot spawn; HUD, quick slots and souls counter show) |
| 3 | Greystone as the player and Sevarog as the boss on the pack's framework | Greystone and Sevarog done (2026-10-19): see "Stage 3 as built" and "Sevarog on the pack as built" |
| 4 | Poise on the pack's attributes | Done on the stock mannequin (2026-10-19), see "Stage 4 as built" |
| 5 | Parity check, then retire the C++ combat and its tests | Done (2026-10-19), see "Stage 5" |

### How the pack is configured (found so far)

- A character is data: `BP_PlayerInfo` data assets hold default attributes, `ExtendedAttributes`, ability sets, combat style, state classes, input mapping contexts, UI widgets, cues and target types. `BP_BaseCombatCharacter` only stores the PlayerInfo reference. Enemies use `BP_EnemyInfo`.
- Attributes are gameplay-tag keyed (`Attribute.Health`, `Attribute.HitCount`, ...) and extended attributes are Blueprint classes (`BP_BaseRegeneratableAttribute` for Stamina, Health and Mana). Poise fits as one more regenerating extended attribute.
- Damage runs through `BP_DamageExecution` (185 nodes) and `GE_DamageBase`; hit reactions are `GA_BaseHitReaction` and `GA_HitStun`, which already counts hits (`Hit Count Attribute Tag`). A poise break can drive the same hit-stun ability.
- Python cannot read Blueprint variables; the plugin server (`Scripts/mcp_call.py`, editor open) can query and modify Blueprints, CDOs, levels and world settings.

### Stage 3 as built: Greystone (option A, full retarget)

| Step | What | Where |
|---|---|---|
| Rig and retargeter | `IK_CombatMannequin` (auto-generated chains), `RTG_CombatMannequin_To_Greystone` | `Scripts/Editor/retarget_pack_to_greystone.py`, assets in `Content/OneBossFight/GreystonePack/` |
| Animations | 238 sequences, 130 montages, 9 blend spaces, 2 aim offsets and 10 animation Blueprints (`ABP_CombatCharacter`, the weapon layers) retargeted, names `*_Grey`, folders mirror the pack | `resolve_retarget_map.py`, `move_grey_abps.py`; map in `Saved/greystone_retarget_map.json` (389 entries) |
| Re-pointing | 60 player-side Blueprints and data assets rewritten to the `_Grey` copies: weapon abilities, enter and exit combat, quick slots, dodge, hit stun, knockdown, bonfire, potion, magic and bow abilities, all combat styles (layer classes) | `map_referencers.py` then `repoint_player_refs.py` (recursive rewrite of every variable) |
| Sockets | 40 sockets (weapon hands, sheaths, shield, quiver, consumable) copied from the pack mannequin to the Greystone skeleton | `RPGSkeletonUtils::CopySockets` (C++; Python cannot set a socket name), `copy_sockets_to_greystone.py` |
| Player | `BP_GreystonePack/BP_GreystonePlayer`: child of `BP_CombatPlayerCharacter`, Greystone mesh and `ABP_CombatCharacter_Grey`; `BP_AdvancedGameMode` spawns it | `setup_grey_player.py` |

Verified in PIE on the pack's demo level (`Scripts/Editor/pie_grey_check.py`): the pawn is `BP_GreystonePlayer_C` with the Greystone mesh; entering combat, three melee attacks (sword and shield combo) and a dodge play with the retargeted animations, sword in the right hand and shield on the left arm. Images in `Documentation/Art/`.

Consequences: the pack's own mannequin player (`BP_CombatPlayerCharacter`) now points at Greystone animations and no longer works with its mannequin; mannequin enemies keep their own (untouched) animations. The retarget adds nothing to the original pack assets except these re-pointed references.

### Greystone polish (after the Sevarog work)

Three faults found by loading everything in a fresh editor, all caused by how stage 3 was built:

| Fault | Cause | Fix |
|---|---|---|
| All eight retargeted weapon layers failed to load (no layer, so no weapon stance animation) | They were saved with their parent at `/Game/ABP_CombatAnimLayersBase_Grey`, where the base sat before it was moved | `fix_grey_layers_1.py` put a temporary copy of the base at that path so they load, `fix_grey_layers_2.py` re-parented all layers to the real base and saved; no file references the old path now and the copy is deleted |
| Four blend spaces (unarmed, one-handed, dual sword, magic locomotion) had lost their animations | Same stale paths for name-collision duplicates | `fix_grey_blendspaces.py` restores every sample from the pack's original blend space through `Saved/greystone_retarget_map.json` |
| The 40 pack sockets never existed on Greystone: the pack weapons were not attached, and what looked like the pack sword and shield in earlier captures was Paragon's built-in geometry (material slot 3) | `USkeletalMesh::AddSocket(..., bAddToSkeleton=true)` silently adds nothing | `copy_sockets_to_greystone.py` now copies to the mesh (70 sockets). The built-in sword, shield and fur geometry is hidden with `M_GreyHiddenSlot` as the override of slot 3 on `BP_GreystonePlayer` (`hide_grey_builtin_weapons.py`) |

Verified in PIE: every layer links and animates (`pie_grey_layers.py`: unarmed, sword, sword and shield, two-handed, dual sword, twinblade, magic staff); claymore, dual sword, sword and shield attach to their pack sockets in hand and sheath (`pie_grey_weapons.py`); Greystone hits Sevarog again with the pack weapons attached (boss health 1500 to 1377).

Control Rig: the animation Blueprint's only rig is `CR_Mannequin_BasicFootIK`; its hierarchy warnings concern clavicles, neck and fingers, which a foot rig does not touch. Left as is.

Also added: `AM_SevPack_Turn` and `GA_Sev_TurnInPlace`. The pack's behaviour tree calls turn in place when the target is behind the boss; without that ability Sevarog stood still while the player circled him.

### Sevarog on the pack as built

Sevarog is a pack boss: a child copy of `BP_ExampleGreatSwordBoss` with his own mesh and animation Blueprint, the pack's boss abilities and behaviour tree, and his own montages. Assets are in `Content/OneBossFight/SevarogPack/`, built by `Scripts/Editor/sevarog_pack_01..04*.py` (editor open, in order).

| Piece | How |
|---|---|
| Pawn | `BP_SevarogBossPack`: capsule 90 x 155, mesh `Sevarog` (yaw -90, z -155), `EnemyInfo` and `EnemyInfoRef` (the copied pack boss defaults `EnemyInfoRef` to the sword mob's info, which silently made the first test a sword mob) both point to `SevarogEnemyInfo` |
| Hit traces | The pack traces a weapon static mesh's sockets. `SM_SevarogScytheProxy` is a copy of the pack sword mesh with six sockets `Trace_0..5` from bone `weapon_r` to `root_weapon_end_r` (67 cm), hidden in game. The component attaches to bone `weapon_r` (both attach socket choices in the BeginPlay graph changed to `weapon_r`, so no skeleton sockets are needed) |
| Animation | `Sevarog_AnimBlueprint` (Paragon) is the info's `Anim Class`: its speed comes from the pawn's velocity, so it works on a non-Paragon pawn; `FullBody` slot. The combat style has no `Anim Layer Class` |
| Montages | `AM_SevPack_Sweep/Backhand/Overhead/Lunge/Shockwave`: same Paragon sequences and scythe-speed hit windows as the C++ boss, with the pack's notifies: `ANS_DisableMovement`, `ANS_SetDesiredRotation` (face target, 520), `ANS_CollisionTrace` (tag `TargetType.MainWeapon`, event `GameplayEvent.AttackHit`; knockdown attack data on Lunge and Shockwave) and `AN_EndAnimatingAbility`. `AM_SevPack_Entrance` and `AM_SevPack_Exit` add `AN_ToggleCombat` (must come before the ability's end at 80 % of the montage, or combat never turns on and the entrance loops) |
| Abilities | `GA_Sev_*`, copies of `GA_GS_Boss_*`: CloseAttack = Sweep, Backhand, Overhead (random); CloseRare = Shockwave; MidRange and Sprint = Overhead; Leap = Lunge; Retaliation = Backhand; EnterCombat = Entrance; ExitCombat = Exit; HitStun = Sevarog's hit react in all four directions. Turn in place dropped (no Sevarog turn montages) |
| Data | `SevarogEnemyInfo`: 1500 health, 100 poise (poise gate from stage 4 applies), attack 35, 1000 souls, behaviour tree `BT_ExampleBoss`, name "Sevarog" |
| Level | `L_SevarogArena` (copy of `L_Greybox`, saved with `save_map`): pack game mode, art arena, `BP_SevarogBossPack` at the centre, a navmesh bounds volume (the pack's AI walks the navmesh). `L_Greybox` and the C++ boss are untouched until stage 5 |

Verified in PIE (`Scripts/Editor/pie_sevarog_pack.py`, pack demo level and `L_SevarogArena`): the boss plays the entrance, enters combat, walks to Greystone, and uses Sweep, Backhand, Overhead, Shockwave (knocks Greystone down) and Lunge; Greystone's attacks take his health down, and at zero he dies, disappears and awards 1000 souls. Evidence: `Documentation/Art/sevarog_pack_fight.png`.

### Sevarog parity features on the pack (built after the first pass)

| Feature | How it is built |
|---|---|
| Shockwave | `AM_SevPack_Shockwave`: `ANS_CollisionTrace` with `TraceRadiusModifier` 400 (a ~450 cm sphere along the scythe tip's slam path, knockdown attack data), `RPGAN_SpawnEffect` with the Niagara shockwave and Sevarog's ultimate sound at the slam peak |
| Lightning Strike | `GA_Sev_Lightning`: copy of the pack's magic-enemy fireball ability. Cast montage `AM_SevPack_Lightning` sends `GameplayEvent.FireProjectile.RightHand`, the ability fires `BP_SevBolt` (copy of the fireball projectile, particle `P_SevarogComet`) from bone `weapon_r`; `SevBoltAttackData` uses generic magic damage and a Sevarog blast as impact. Because it is the pack's projectile pipeline it can be blocked and parried like any spell |
| Phase change and roar | C++ `URPGSevarogDirector` (`Source/OneBossFight/Boss/`): reads health through the pack's `BP_AttributesComponent` by Blueprint function name, at 50 % plays `AM_Sevarog_PhaseRoar` directly on the mesh (the pack's enter-combat ability will not restart while in combat) and raises walk speed by 1.25 |
| Lightning scheduling | same component: in phase two, every 6 to 10 s when the player is 500 to 1500 cm away and no montage is playing, it activates `GA_Sev_Lightning` through the pack's `Try Activate Ability by Class` |
| Entrance trigger | same component: `AutoPossessAI` is off on the pawn, and the AI controller is created (`SpawnDefaultController`, then the controller's `InitializeController` event, which the pack's pawn BeginPlay normally calls) when the player comes within `GateRadius` (1000 cm) |
| Death animation | `GA_Sev_Death`: copy of the pack's `GA_EnemyDeath` with `AM_SevPack_Death` (last pose held), replacing the ragdoll death in `SevarogCombatStyle` |
| Respawn | the pack's player death task already respawns Greystone at the `PlayerStart` in `L_SevarogArena`; the director watches for the new player pawn and resets the encounter (boss home, full health, combat off, controller destroyed so he sleeps behind the gate again) |

Verified in PIE (`Scripts/Editor/pie_sevarog_pack.py`, flags `GATE_TEST`, `PHASE_AT`, `FORCE`, `PLAYER_KILL_AT`): gate opens at 1000 cm, entrance and attacks follow, phase two at 700 HP plays the roar, lightning strikes fire at 500 to 600 cm, forced Shockwave knocks Greystone down with the ring effect, a killed player respawns and the boss is back at 1500 HP and wakes at the gate again. Evidence: `Documentation/Art/sevarog_pack_parity.png`.

Still different from the C++ boss: the triple combo is not one move (the pack's close attack picks Sweep, Backhand or Overhead per activation), Shockwave has no ground telegraph, Lightning is a projectile instead of a strike at the player's feet, no boss music. The pack's own `GA_Sev_PhaseRoar` ability exists but is unused (it cannot start mid-combat).

### Stage 4 as built (poise)

Poise is a regenerating extended attribute, not a separate system, and it gates the pack's hit stun.

| Piece | What |
|---|---|
| Tag | `Attribute.Poise` in `Config/DefaultGameplayTags.ini` |
| Attribute | `/Game/OneBossFight/Poise/BP_PoiseExtendedAttribute`, a copy of the stamina attribute: regenerates 2 per 0.1 s after 4 s without a hit |
| Data | `Attribute.Poise` entry and the attribute class added to every `PlayerInfo` and `EnemyInfo` (`Scripts/Editor/poise_data.py`): player 40, enemies 30, bosses 100 |
| Gate | `GA_BaseHitReaction` "Can Activate Ability?": when the stock check passes and `bUsesPoise` is true, poise drops by 20. Above 0 the hit is absorbed (no hit reaction, damage still lands); at 0 poise refills and the hit stuns. A character without a poise attribute stuns on every hit as before |
| Switch | `bUsesPoise` is true on the hit stun abilities and false on block reactions, knockdowns and the no-hit-data stun. Subclass defaults do not follow a new parent variable, so each ability is set explicitly |
| Reproduce | `Scripts/install_poise.py` (editor open) after a re-import; the graph edit part has been run once by hand-equivalent calls and its skip path tested, not re-run from a clean import |

Verified in PIE on the demo level (`Scripts/Editor/pie_poise_test.py`): a sword enemy hitting the player (poise 40): first hit poise 40 to 20 and no hit reaction, second hit plays `HitReact_*` and poise returns to 40, then poise regenerates 2 per tick after the cooldown. The enemy side (player hits enemy) is the same code path but was not exercised: attacking by ability tag from a script did not fire the player's attack.

Known limits: the poise cost is a constant 20 per hit (the `PoiseDamage` variable added to `BP_AttackData` is not read: the Blueprint tool cannot read a variable of another Blueprint class). Per-attack poise needs a getter function on `BP_HitData` added in the editor. Hits that arrive at `ImpactDecision.Hit` are the only ones that drain poise; block and parry do not.

## Stage 5: the C++ combat is retired (2026-10-19)

The project's own combat is gone; the Advanced ARPG pack is the game. Greystone (player) and Sevarog (boss) run on the pack's abilities, hit detection, poise,
lock-on, dodge, block, HUD, boss bar, respawn and menus. A copy of everything removed is in `Archive/CppCombat_2026-10-19/` (README inside; delete it once the
removal is committed, git history keeps the committed versions).

Parity, feature by feature:

| C++ version | Pack version | Result |
|---|---|---|
| Player: light and heavy chains, dodge with i-frames, block, parry, stamina, lock-on, sprint, three weapons | The pack's player abilities on Greystone (retargeted), pack equipment and quick slots | Attacks, dodge, weapons verified in PIE (GREY-01, GREY-02); block, parry, lock-on, sprint are the pack's own and not re-tested on Greystone; gamepad still untested |
| Poise and stagger | Poise attribute and gate (stage 4) | Verified (POISE-01); the per-attack poise cost is still a constant 20 (KI-032) |
| Boss: seven attacks, weighted selection, cooldowns | Pack abilities and `BT_ExampleBoss` | Sweep, Backhand, Overhead, Lunge (leap), Shockwave work; selection is the pack tree's, not our weights; mid-range and sprint are filled with Overhead (KI-047) |
| Boss phase two at 50 % with roar | `URPGSevarogDirector` | Verified (SEV-02) |
| Lightning Strike, Shockwave effects | `GA_Sev_Lightning` projectile, ring effect and radial trace on the Shockwave montage | Verified; Lightning is a projectile, not a strike at the feet (KI-038) |
| Entrance trigger, dormant boss, entrance | Director gate at 1000 cm, pack enter-combat with `AM_SevPack_Entrance` | Verified |
| Death, retry loop, reset | Pack death ability and death task (souls, respawn), director resets the boss when the player respawns | Verified (SEV-02); the pack awards 1000 souls |
| Triple combo as one move | Close attack picks Sweep, Backhand or Overhead each time | Different by design |
| StateTree mirror of the boss state | None | Dropped (it only mirrored state) |
| HUD, pause menu, settings (volume, sensitivity, brightness), auto-retry | The pack's HUD and boss bar; its own menus | The pack's menus replace ours; our settings page is gone |
| Benchmark runner (scripted fight, frame capture, gate report) | `FRPGFrameStats` kept, runner removed | Open: PERF-01 needs a new capture path (KI-048) |

Kept in C++: `ARPGGreyboxArena` (the art arena), `URPGSevarogDirector`, `URPGAN_SpawnEffect` (the pack montages use it), `URPGSkeletonUtils` and `URPGMontageUtils` (editor authoring), `FRPGFrameStats`.
Kept tests (5, all pass headless): Benchmark.FrameStats.Percentiles and Gate, Arena.Collision, Arena.ArtPass, Content.PackWiring (new: Sevarog pawn with director, all `GA_Sev_*`, style, info, ten montages, the seven Greystone weapon layers, the pack sockets on Greystone's mesh).
Removed: the player, boss, combat, attribute, melee trace, target lock, weapon data, feedback, encounter, game mode, controller, settings, HUD and pause menu classes, the StateTree code, the benchmark runner and 23 tests; `L_Greybox`, `L_Benchmark`, `BP_PlayerCharacter`, `BP_SevarogBoss`, `BP_TrainingDummy`, `BP_RPGGameMode`, the boss and weapon data assets, feedback assets, the C++ attack montages and `ST_Boss`. The default and editor start map is now `L_SevarogArena`. Input assets in `Content/OneBossFight/Input` stay but nothing uses them.

### After stage 5: the three open items

| Item | Change |
|---|---|
| KI-049 ability grant | The AI controller now exists from BeginPlay again (`AutoPossessAI` back on) because the pack's abilities read it when they are granted. The director holds the behaviour instead: while the gate is closed it calls the behaviour manager's `StopBehaviorLogic`, at the gate it activates the entrance ability (`EntranceAbility`), keeps the behaviour held for `EntranceHoldSeconds` (4.2), then `SetBehaviorDisabled(false)` and `RestartLogic`. The reset after a player respawn keeps the controller too (clears the blackboard target, perception and combat targets, turns combat off) and holds again. No more `Accessed None` on the behaviour manager |
| KI-047 mid-range | `URPGANS_ChargeToTarget` (in `Pack/RPGPackNotifies`) drives the pawn to the player over the wind-up so the hit lands (speed chosen to arrive when the window ends, capped at 2400 cm/s, stops at 200 cm). `AM_SevPack_Charge` (Overhead swing plus the charge, played at 0.6 rate) replaces Overhead in `GA_Sev_MidRangeAttack`. The sprint ability needs no change: it runs to the target itself and follows up with Overhead, and now works because of KI-049 |
| KI-048 benchmark | `ARPGBenchmarkRunner` is back (same switches: `-RPGBenchmark`, `-RPGBenchmarkFight`, `-RPGBenchmarkQuit`, `-RPGBenchmarkLabel=`; same `Saved/Benchmark/<label>_<time>/` frames.csv and summary.json) and placed in `L_SevarogArena`. In fight mode a bot drives Greystone through the pack's abilities (enter combat, melee, dodge), walks up to Sevarog, keeps both alive, forces phase two at 30 s, and the view stays the player's camera. `Scripts/RunBenchmark.ps1` defaults to the arena fight (`-Empty` for the orbit camera). First reading, editor binary in game mode (not packaged), 1080p: 79 FPS average, p99 27 ms, over budget on 99 % of frames; this is the pre-optimisation baseline, not a gate result |

Shared by the director and the runner: `Pack/RPGBlueprintCall.h` (call a pack Blueprint function by name, read and write attributes, activate abilities by tag).

Lesson recorded: three abilities (entrance, exit, death) silently had no montage because their montages had been deleted and recreated at the same path, and a CDO-only edit of a Blueprint is not written by `save_loaded_asset` unless `asset.modify()` is called first. `check_sev_abilities.py` lists every ability's montages and `Content.PackWiring` now fails if any reference is empty.

### Polish after the open items (smaller items and known differences)

| Item | Result |
|---|---|
| Greystone's baked-in sword, shield and fur (KI-044) | `URPGHideBones` (Pack/) hides the vertices skinned to `sword_bottom` and `shield_inner` at BeginPlay; the material-slot override is removed, so the fur in slot 3 is visible again. Verified in PIE |
| Weapon fit (KI-046) | Polearm, twinblades, dual swords (left hand) and bow/quiver sockets checked with `pie_grey_weapons.py`: they attach in hand and sheath. Bow and quiver are small and hard to judge in the frames; the sockets exist and the actors attach |
| Triple combo | The pack's own follow-up: `AN_PerformFollowUp` on `AM_SevPack_Sweep` (70 % into the Backhand) and `AM_SevPack_Backhand` (60 % into the Overhead), within 450 cm. Verified: Sweep, Backhand, Overhead play back to back without a decision in between |
| Shockwave telegraph | Ground ring (`NS_Free_Spells_Circle`, scale 5, at the slam spot) 0.45 s before the slam |
| Lightning strike at the player | The director records the spot under the player when it starts the cast and shows a ground ring there; when the lightning ability spawns `BP_SevBolt` (about 0.65 s later) the director moves it 14 m above that spot, pointing straight down, and spawns the thunder beam `NS_Thunder_Beam7` when it lands. Still the pack's projectile pipeline, so block, parry and hit reactions apply. The player can step away during the cast. Test hook: `TriggerLightning()` on the director (the ability only starts when the boss is not busy) |
| Boss music | Not done: there is no music asset in the project (the optional music and ambience in the asset request were never supplied) |

## Back to the pack's own player and boss (2026-10-19, later)

The Greystone player and the Sevarog boss were dropped for now: the player stood on retargeted animations that logged `GetMainAnimBP` Accessed None errors every frame (`ABP_CombatAnimLayersBase_Grey`), and Sevarog stood and only turned. The game now uses the pack's mannequin player and the pack's great-sword boss, both unmodified apart from the poise data.

| Decision | Reason |
|---|---|
| Revert the 60 pack assets that stage 3 re-pointed to the `_Grey` copies (all weapon abilities, enter/exit combat, quick slots, dodge, hit stun, knockdown, potion, bonfire, magic and bow abilities, all combat styles) | The mannequin cannot play animations of another skeleton. A reverse of `repoint_player_refs.py` (same saved map, inverted) did it; backups of the files before the change were kept outside the project |
| Restore `ABP_CombatCharacter`, `ABP_UnarmedLayer` and `UnarmedCombatStyle` from the pack source (`Unreal Assets/Advanced ARPG Combat System V3 - Unreal Engine`) | The polish step had consolidated the unarmed layer into the Grey copy: the original path was a 3 KB redirector, so even loading the original class gave the Grey one. Found by comparing every pack file with the pristine source (92 differ: re-saved reverts, poise data, enemy infos, the game mode) |
| `BP_AdvancedGameMode.DefaultPawnClass` back to `BP_CombatPlayerCharacter` | It pointed at `BP_GreystonePlayer` |
| The arena boss is `BP_ExampleGreatSwordBoss` with `EnemyInfoRef` set on the placed instance to the `ExampleGreatSwordBoss` info | The pack boss Blueprint defaults `EnemyInfoRef` to the sword mob (sword mob montages, 100 HP), the same trap as in the Sevarog copy. Pack data: 500 HP, 100 poise (poise from stage 4). `Scripts/Editor/arena_use_pack_boss.py` rebuilds it |
| Boss entrance and phase two (director) are not used | The pack's boss wakes by perception, chases on the navmesh and uses its own tree: verified moving 1500 to 2000 cm in PIE. No gate, roar or lightning until the boss feel pass (TASKS.md) |
| Greystone and Sevarog folders and C++ (`URPGSevarogDirector`, `URPGHideBones`) stay on disk, unused | Deleting 100 MB of tracked assets is irreversible; waiting for the user's yes. Nothing in `Content/AdvancedARPGCombat` references them any more (`Content.PackWiring` checks every pack asset's dependencies) |
| `Content.PackWiring` rewritten | It now checks: pack game mode spawns the pack player, mannequin mesh, no pack asset depends on `GreystonePack` or `SevarogPack`, the arena has exactly one great-sword boss with the great-sword data and no Sevarog pawn |

Verified in PIE (`Scripts/Editor/pie_pack_fight.py`, log `[PackPie]`): the pack player spawns (mannequin), the boss runs at the player, plays `GS_LeapAttack`, `GS_ChargedAttack`, `GS_Attack01..04`, the player's `Attack_PrimaryA` lowers its health 500 to below 0, it dies; no Blueprint runtime errors in the log.

### Jump attacks (2026-10-19, user request)

| Item | Result |
|---|---|
| How the pack decides | `GA_Player_MeleeBase_Combined.Update Desired Attack Ability`: if the character `IsFalling` and `GetAttackMontages` is not empty it activates `Ability.Melee.FallingAttack` (`GA_Player_FallingAttack`); otherwise the ground chain. `GetAttackMontages(tag)` returns the weapon ability's array for that tag (`AttackMontages`, `StrongAttackMontages`, `FallingAttackMontages`, ...). Melee abilities cannot activate while falling (their `Can Activate` requires not falling), so airborne strong attack does nothing |
| Jump light, all weapons | Dual swords, twinblades and polearm already had an air clip. `Scripts/Editor/air_light_attacks.py` copies the first light attack into `FallingAttackMontages` of `GA_Sword_Melee`, `GA_Claymore_Melee` and `GA_Unarmed_Melee` (pack assets edited in place, like the poise edits). Verified in PIE (`pie_air_attack.py`, log `[AirPie]`): jump, trigger melee while falling, `Attack_PrimaryA_Montage` plays; no new Blueprint errors. Not verified after an editor restart (CDO edit, check `air_light_probe` style read next session) |
| Jump heavy (built) | No new ability: the combined melee ability plays whatever `GetAttackMontages(DesiredAttackAbilityTags)` returns, and `StrongAttack` already returns the weapon's own heavy montage (`StrongAttackMontages`). `Scripts/air_heavy_selector.py` adds one branch to `Update Desired Attack Ability`: when falling and `CanActivateStrongAttack?` (last buffered input is `InputTag.StrongAttack` and the weapon has heavy montages) it sets `Ability.Melee.StrongAttack` and returns true; otherwise the old light-air logic. Weapons without a heavy montage (twinblades, polearm) keep the light air attack. Landing: the montage keeps playing through the landing and the ability ends with it |
| Jump height | `Scripts/Editor/air_jump_tuning.py`: `JumpZVelocity` 600 to 680 on `BP_CombatPlayerCharacter` (air time about 0.72 s to 0.82 s, apex 108 to 139 cm); gravity scale 1.7 unchanged so the fall keeps its weight. Persisted across an editor restart (checked) |
| Poise damage by attack power | `GA_BaseHitReaction` "Can Activate Ability?": the constant -20 is now `-20 - 30 * (HitData.GetAttackPower >= 3)` (math nodes: `GetAttackPower` -> To Integer -> `>= 3` -> Bool to Double -> x -30 -> + -20). Light and none stay 20; heavy and above (strong, charged and knockdown attack data) cost 50. This also makes the grounded heavy attack cost 50 poise. The `PoiseDamage` field on the attack data is still unread (the tool could not build a `Select` on the enum or a function return pin, so power is the switch) |
| Verified | PIE with real input (`Scripts/Editor/pie_air_attack.py`, injects `IA_StrongAttack`/`IA_NormalAttack` through `URPGInputTestUtils`): grounded heavy plays `Ability_E_Anim_Montage` (sword), airborne heavy plays the same montage in the air and finishes after landing; light-air plays `Attack_PrimaryA_Montage`. Real hits on the boss: light 41 HP, heavy 57 HP. Player poise from boss attacks still drops 20 per hit (baseline unchanged) |
| Not verified | (1) A HEAVY-power hit on a poise-gated victim costing 50: the boss never loses poise (it takes damage but never staggers, KI-053) and the sword enemy test did not land hits (it blocks or is out of reach). (2) Claymore, unarmed and the weapons with no heavy montage in the air (only the sword was played). (3) Feel: timing of the swing against the fall, hit reaction, camera. (4) Gamepad |

### Dodge: tap quick, double tap full, hold sprint (2026-10-19, user request)

| Item | Result |
|---|---|
| What the pack already did (measured with real key presses, `Scripts/Editor/pie_dodge.py`) | The dodge starts on key release (about 20 ms later), holding Space for 0.5 s sprints and the sprint consumes the buffered dodge, so a hold never dodges first (moving: sprint, peak 800 cm/s, no dodge montage; standing: nothing). My earlier claim that holding dodged first was wrong (the first measurement only injected `IA_Dodge`, not the Sprint and Jump actions that share Space). What was missing: every tap played the same long dodge, `Dodge_To_Idle_Montage` (0.92 s, 511 cm; a higher play rate keeps 509 cm) |
| Clips | Quick dodge: the pack's unused `Dodge_Small_Forward_Roll_Montage` (0.43 s, 304 cm). Full dodge: the pack's `Dodge_To_Idle_Montage` (0.92 s, 511 cm) |
| Mechanism | C++ only, no pack Blueprint edit: `URPGDodgeTiming` (`Source/OneBossFight/Player/`) binds to `IA_Dodge` Started on the player's input component. A press within `DoubleTapWindow` (0.35 s) of the previous press writes the full clip into the montage map (`DodgeMontage`) of the player's dodge ability instance, any other press writes the quick clip; the ability reads the map when it activates, after the release, so the pack's stamina cost, cancel rules, buffer and direction logic still apply. `URPGPlayerMovesSubsystem` (world subsystem) attaches the component to `BP_CombatPlayerCharacter` (or a child) when it spawns, including after a respawn |
| Verified with real keys (`SpaceBar`, `W` through `URPGInputTestUtils::SetKeyDown`, about 80 fps) | Tap: quick clip, 329 cm. Hold 0.6 s standing: no dodge. Double tap (0.15 s gap): quick, then the full dodge (847 cm together). Two taps 0.9 s apart: quick, quick (669 cm). Hold 1.2 s moving: sprints, no dodge. Same on `Gamepad_FaceButton_Right` by construction (same action), not played |
| Known behaviour | A double tap plays the quick dodge to its end and then the full dodge about 0.1 s later (the pack queues the second dodge until the first ends; the quick clip has no cancel window), so one double tap travels about 8 m. Cancelling the quick dodge into the full one would need cancel-frame notifies on the quick clip. Window, clips and ability names are properties on the component |
| Test tooling | PIE at editor background speed ran at about 8 fps (`bThrottleCPUWhenNotForeground`), which made every timing look 0.2 s late; the drivers set it false for the session (`unreal.load_class(None, "/Script/UnrealEd.EditorPerformanceSettings")` default object). Keys: `unreal.RPGInputTestUtils.set_key_down(pc, "SpaceBar", True/False)` |

#### Dodge fix after the hand test (2026-10-19)

Report: on the controller the quick dodge was tiny and the full roll never played. Cause found by reading the user's own play log (`LogRPGDodge` lines of the 17:52 session) and reproducing the timing in PIE: the user's double taps were 0.14 s apart and every second press WAS detected as "full", but the roll never started. The pack accepts a queued dodge only inside the running dodge clip's `ANS_InputBuffer` window; the quick clip's window opens at 0.234 s, so a second press at 0.14 s was dropped (a 0.30 s gap worked, which is why the keyboard test with a 0.27 s gap passed). Pack clip data (`URPGMontageUtils::DescribeNotifies`): quick clip (0.667 s): `ANS_SetDesiredRotation` 0 to 0.285, `ANS_iFrames` 0.107 to 0.49, `ANS_InputBuffer` 0.234 to 0.502, no cancel frames; full clip (2.333 s at rate scale 2): rotation 0 to 0.25, `ANS_iFrames` 0 to 0.7, `ANS_InputBuffer` 0.485 to 1.677, `ANS_MovementCancel` 1.707 to 2.334.

| Change | Result |
|---|---|
| Second press within the window while a quick dodge runs | `URPGDodgeTiming::ForceFullRoll`: writes the full clip, marks `InputTag.Dodge` consumed in the pack's input buffer (what the pack's sprint does, so the key release does not dodge again), ends the running dodge ability (`End Ability`) and activates it again (`Try Activate Ability by Class`, forced), which plays the full clip from where the quick dodge has got to |
| Third press or key repeat while a full roll runs | ignored (one roll per double tap, logged "ignored") |
| Quick dodge feel | play rate 1.3 written with the clip: the slow wind-up is shorter (the clip moves 95 cm/s at its start and 976 at its peak), distance stays 3 m; lasts about 0.25 s, i-frames from the clip's `ANS_iFrames` (scaled with the rate). Window default 0.30 s, rates and clips are properties on the component |
| Verified with real gamepad B presses, PIE, about 80 fps (`pie_dodge.py`) | tap: quick, 285 cm, 0.25 s. Fast double tap (gap 0.14 s): quick, then the full roll starts at 0.15 s and lasts to 1.07 s (529 cm). Gap 0.25 s: full at 0.27 s. Gap 0.5 s (outside the window): quick, quick. Triple mash at 0.14 s: quick, roll, third ignored. Hold 1.2 s moving: sprint, no dodge. Attack pressed 0.40 s after a tap starts at 0.49 s; at 0.60 s starts at once; after a double tap, an attack at 0.9 s starts at 0.99 s (cutting the roll's recovery) and at 1.2 s at once |
| Not changed / not verified | No input still dodges forward (the pack's `DefaultDodgeDirection`; there is no backstep clip), not backward. The forced roll runs the pack's cost effect a second time (a double tap pays two dodges); stamina cost not measured. Collision during the roll uses the pack's root motion as before, not tested against walls. Mouse and keyboard use the same action, only B and Space were pressed |

#### Dodge backward without input (2026-10-20, user request)

With no direction input the pack dodges along the current facing (forward; locked on, that is into the target). `URPGDodgeTiming` now detects the dodge ability becoming active (it ticks every frame), and if `CharacterMovement->GetLastInputVector()` is below `NoInputThreshold` (0.1) it turns the pawn to the camera yaw + 180 at `BackwardTurnRate` (1800 deg/s, 0.1 s for 180 degrees) while the clip's root motion runs, so the dodge goes away from where the camera looks (away from the target when locked on). With input, nothing changes (the clip's own `ANS_SetDesiredRotation` turns towards the stick). A forced full roll does not cancel a turn in progress. There is no backstep clip in the pack, so this is a turn and a roll away, not a hop that keeps facing; `bBackwardWithoutInput` turns it off.

Verified with gamepad B and the stick in PIE (`pie_dodge.py`, camera yaw 0): no stick tap: heading -172 (8 degrees off straight back), 248 cm, final yaw -179; fast double tap, no stick: heading -177, 504 cm, final yaw 180; stick forward 0, left -90, right 92, fast double tap with stick forward 0; hold with stick: sprint, no dodge. A turn rate of 900 curved the path (heading -151, 207 cm), which is why 1800 is the default. Not tested: locked on to the boss, collision against walls, keyboard without a stick (same code path: no movement input).

### Boss poise break (2026-10-19, KI-056)

| Item | Result |
|---|---|
| Cause | Probes in PIE (`pie_boss_abilities.py`, `pie_boss_hitreact.py`): the boss has `GA_GS_Boss_HitStun_C` (tag `Ability.HitReaction`, `bUsesPoise` true) and poise 100/100, but `HasMatchingGameplayTag(Status.HitStunImmune)` was true on it: the pack boss Blueprint's `GameplayTags` default is `(Enemy.Character, Status.HitStunImmune)` and every hit stun ability lists that tag in `ActivationBlockedTags`. The poise gate (inside `Can Activate`) runs before the tag check, so poise drained but nothing could play. (An earlier run that showed poise never moving was taken before an editor restart; after it the gate drained as designed) |
| Fix | `Scripts/Editor/boss_poise_armor.py`: `BP_ExampleGreatSwordBoss.GameplayTags` = `(Enemy.Character)` (pack asset edited in place, original backed up outside the project; run after a pack re-import). Poise is now the boss's armor |
| Verified | Real input in PIE: light hits absorbed with no flinch (poise 100 to 60 to 20, a light press can land two hits so 40 per press), a heavy hit costs 46 to 50 (60 to 14 once), a break plays `HitReact_Front_Montage` with the hit stun ability active for about 0.5 s, poise refills (shows 50 right after a heavy break because the swing's second hit drains 50 again), boss HP still drops on every hit |
| Not like Elden Ring yet | The stagger is a 0.8 s flinch and the boss retaliates at once (pack `RetaliationAttack` also fired after one break). Elden Ring: long stance break (about 2 to 3 s) then a critical hit. Pack material for it: `GA_Knockdown` / `GA_EnemyKnockdown` with `KnockdownStart_Anim_Montage` and `Knockdown_Getup_Anim_Montage` (2handed folder), `GE_AllowFatality` (grants `Status.AllowFatality`), `GA_Player_FatalityAttack` and `GA_FatalityVictim` (execution pair). Options: (A) on a break hold the boss in a longer stagger and add a critical damage window (own C++ component, no pack edit), (B) route breaks to the pack knockdown plus fatality (needs the pack's victim/attacker montage pairs to fit this boss), (C) leave the flinch. Not started |

#### Boss stance break and critical window (2026-10-19, option A, KI-060)

`URPGBossStagger` (`Source/OneBossFight/Player/`, attached to `BP_ExampleGreatSwordBoss` by `URPGPlayerMovesSubsystem`, no pack edit) watches the boss's `GA_GS_Boss_HitStun`; when it becomes active (a poise break) it: ends that flinch ability, applies the pack's `GE_HitStunImmune` (4 s, covers the whole sequence) so later hits do not replay a flinch, holds the boss's behaviour (`BP_BehaviorManagerComponent` `StopBehaviorLogic`, as the Sevarog director did) and stops its movement, plays the pack knockdown clip `KnockdownStart_Anim_Montage` (1.92 s) and freezes it at 1.55 s so the boss stays down until `StaggerSeconds` (2.5) after the break, then plays `Knockdown_Getup_Anim_Montage` (1.4 s, first 1.03 s invulnerable in the clip), resumes the behaviour, removes the immunity, refills poise and starts a 5 s cooldown. While down, any health lost is multiplied by `CriticalMultiplier` (2.5): the extra is subtracted from the health attribute (the hit that causes the break does not count). All values are properties of the component.

Verified in PIE with real input (`pie_boss_stagger.py`, log `LogRPGStagger`): two heavy presses (57 HP each) break the poise; stance break lasts 3.66 s from the break to the end of the get-up (down for 2.5 s), the boss does not move (position fixed) or attack in that time; a light hit that costs 41 outside the window costs 102, a heavy 57 costs 143 (x2.5), health 385 to 139; poise 100 afterwards; the boss attacks again 2 to 3 s later (3 attacks in 6 s); a break 3.1 s and one 0.5 s after the end are ignored (cooldown), the next one after 8.4 s staggers again; second window: critical heavy 156 to 12. No Blueprint runtime errors.

Edge cases (`Scripts/Editor/pie_boss_stagger_edge.py`, modes `boss_dies`, `player_dies`, `boss_resets`, all PASS 2026-10-19): the boss dying during the stance break ends the component (log "died during the stance break", no resume, immunity removed, `Status.Dead` set, the pack's death flow destroys the boss, no errors); the player dying one second into the stance break (the pack respawns the player 4.0 s later, after the 3.66 s sequence has finished) leaves the sequence untouched, the boss resumes, and at the respawn the pack resets it (health 500, poise 100, no stuck hold or immunity; it does not walk back to its start position, it re-equips and fights where it stands); if the pack's reset ever lands while the boss is down, health rising during the stance break ends it at once (montages stopped, behaviour resumed, immunity removed, poise refilled), tested by setting the boss to 500 HP mid-stagger.

Limits: the look is fall and lie (the pack has no kneeling stance-break clip), not a kneel; the critical is a damage multiplier, not Elden Ring's riposte animation (the pack's execution, `GE_AllowFatality` with `GA_Player_FatalityAttack` and `GA_FatalityVictim`, needs paired clips and was not tried); any health loss while down is multiplied, whatever its source; the fall and get-up are untested by eye.

### Lock-on camera (2026-10-20, user hand test: "the camera goes to the ground too often")

Cause (measured with `Scripts/Editor/pie_camera_probe.py`, spring arm 370 cm, collision on, control rotation): the pack's `BP_TargetingComponent.UpdateTargetingControlRotation` aims the control rotation at `target actor location - (0,0,150)` with the pitch clamped to -25..+30, measured from the player's origin. The boss's origin is its capsule centre (149 cm up), so the aim point was the floor under it: lock-on pitch -17 to -25 degrees with the camera 264 to 309 cm up, most of the screen floor. Aiming at the chest was worse: pitch +23 swings the 3.7 m boom down and the camera sat 12 cm above the floor looking up. The fix (`Scripts/lockon_aim_height.py`, pack asset edited in place, original backed up outside the project): aim `target location - (0,0,40)` and clamp the pitch to -8..+12. Result at 250, 450 and 800 cm from the boss while locked on: camera height 130 to 154 cm, pitch +0.6 to +4.4 degrees, boss head 7 to 23 degrees above and feet 9 to 26 degrees below the screen centre (the view reaches 29 degrees), screenshot checked. Not changed: the free camera (pitch is the player's stick), spring arm length and lag. Not tested: smaller enemies, a boss right on top of the player, a controller stick during lock-on.

### Encounter flow: gate, reset and phase two (2026-10-20)

Three components on the pack boss (all attached by `URPGPlayerMovesSubsystem`, no pack edit; the old Sevarog director was not revived).

| Piece | Behaviour |
|---|---|
| `URPGBossEncounter` (`Player/RPGBossEncounter`) | The boss starts dormant: behaviour held (`BP_BehaviorManagerComponent.StopBehaviorLogic`, controller kept), standing at its level placement. It wakes when the player is within `GateRadius` (1200 cm, horizontal) or its health drops below the value read 1 s after BeginPlay (the attributes are not initialised at BeginPlay, which made it wake at once in the first version). Then the pack's tree runs and the boss equips its weapon and fights. A new player pawn (death and respawn) resets it: stance break aborted, phase two reset, behaviour held, blackboard `TargetActor` and `bCombatEnabled` cleared, perception forgotten, `ClearAllCombatTargets` and `SetCombatEnabled(false)`, montages and movement stopped, teleported to its start, health and poise full, dormant again. Properties: `GateRadius` (0 = no gate), `bResetOnPlayerRespawn` |
| `URPGBossPhases` (`Player/RPGBossPhases`) | At 50% health (once per fight, not while dormant or in a stance break): the behaviour is held, `GE_HitStunImmune` applied (4 s, so nothing interrupts it) and `Ability_R_Intro_Anim_Montage` (1.5 s, the two-handed power-up pose) plays as the roar for 1.8 s. Then: walk speed x1.2 (applied to every speed the pack's behaviour sets, since it rewrites `MaxWalkSpeed` on each state change: 600 to 720, sprint 800 to 960), the play rate of the 9 attack montage entries of the `GA_GS_Boss_*` abilities x1.2 (shorter telegraphs), the `Attribute.Attack` attribute x1.25 (35 to 43.75), and a fireball every 6 to 10 s when the player is 500 to 1800 cm away and the boss is not busy: the pack magic enemy's `GA_Fireball_Enemy` is granted at runtime (`Give Ability`) and activated (`Try Activate Ability by Class`, forced): cast clip `FireMagicProjectile_01_MagicEnemy_Montage`, 2 to 3 `BP_FireBallProjectile`. `ResetPhases` (called by the encounter reset) restores speed, rates and Attack |
| Order of an encounter | dormant, player walks in, wake (equip), phase one, a poise break gives a stance break (DECISIONS "Boss stance break"), 50%: transition and phase two, boss dies or the player dies and respawns: reset to dormant |

Verified in PIE (`pie_boss_encounter.py`, `pie_boss_phase_two.py`, logs `LogRPGEncounter`, `LogRPGPhases`; 8 plus 6 checks, all PASS): boss asleep at home for 8 s while the player is 1800 cm away; wakes at 1175 cm; fights and leaves home (1124 cm away); after the player's death and respawn it is 0.0 cm from home with health 500 and poise 100, dormant, stays asleep, wakes again at 1188 cm. Phase two: transition 1.8 s with the clip, speed 600 to 720 (960 sprinting), Attack 35 to 43.75, 3 to 4 fireball volleys in 28 s (the player at 844 cm took 21 damage from one), reset restores the speeds and Attack. Not tested: gamepad or keyboard hand play of the fight as a whole, the boss dying in phase two, a stance break exactly during the transition (the transition is not interrupted by hit stun, a stance break waits for it), `GateRadius` against a very fast player.

Limits: the roar is a power-up pose from the two-handed set, not a roar; no invulnerability during the transition (only hit stun immunity); the fireball is the pack's, with the pack's projectile look; no phase two music or arena change; the entrance is the pack's equip montage, not a dedicated entrance animation.

## Arena presentation: ruins, fire, night, audio (2026-10-20)

- **Priority change (user, 2026-10-20):** look first, 60 FPS is enough; the 150k triangle budget and the 120 FPS target no longer bind.
- **Art source:** the Dark Ruins Megascans sample project (`C:\Users\winss\Documents\Unreal Projects\DarkRuinsMegascansSample`). Only the needed closure was copied (702 packages, about 9.5 GB, same relative paths so every reference holds): church and brick ruin kits, columns, slabs, rubble, props, stone surfaces, decals, fog and flame materials, candles, lantern, the colossal bridge columns and the gate arch. The folders `Content/MS`, `MSPresets`, `CustomAssets`, `Smart`, `Materials`, `Blueprints`, `Effects`, `Textures` are git-ignored (third party). Tools: `Scripts/Editor/sample_deps.py` (dependency closure through the asset registry, run on the sample project) and `Scripts/copy_sample_assets.py`. The sample has no audio and no fire Niagara.
- **Meshes are placed by their bounds, not their pivots:** pivots in this pack are arbitrary (the gate arch pivot is 74 m from its geometry). `place()` in `Scripts/Editor/dress_arena.py` puts the bottom centre of the bounds where asked.
- **A dressing layer, not a rebuild of the arena:** `ARPGArenaDressing` (instanced meshes, no collision unless a set asks for it) is filled by `dress_arena.py`; the greybox arena actor keeps all collision (its wall and gate visuals are hidden, not removed), so tests and gameplay footprints are unchanged. The script clears its folder `Dressing` and rebuilds, so it can be rerun after tuning. Layout: front wall ring at the old wall, tall back ring with gaps, broken wall stubs, gate arch behind the player start, bridge columns far out, columns with lanterns, fallen columns, rubble, coffins, barrels, beams, skulls, swords, chains, mushrooms, flagstones (floor stone at one tile per slab, `MI_Arena_Slab`), dead trees outside. The floor is `MI_Arena_RomanFloor` (Roman stone, 26 tiles across the disc).
- **Fire:** `ARPGFireSource` (Cascade flame and smoke from the starter content, a point light whose intensity, colour and position flutter with Perlin noise, a looping crackle in the game only). The pack's menu fire `P_Fire_NeverEnding` is a wide ribbon, not a brazier flame; the starter `P_Fire` at 2.2x is. Starter sparks are blue and were dropped.
- **Mood:** twilight night. The sun sits just under the horizon (orange glow at the horizon only), a cool movable "moon" directional light (atmosphere light index 1, forward shading priority 1) gives readable shadows, volumetric fog plus a low mist layer, a cloud deck, bloom, vignette and grain in an unbound post process. `Scripts/Editor/atmosphere.py` holds the numbers (TUNING block). Learned the hard way: a sun with light shaft bloom at threshold 0 washes the whole screen, a ground mist layer at density 0.16 blinds the camera, `fog_inscattering_color` is `fog_inscattering_luminance` in 5.5, volumetric fog is `enable_volumetric_fog`.
- **Audio (all C++, no pack edit):** `URPGFootsteps` follows the foot bones (a step when a lifted foot comes down; the planted height of the ankle bone is learned because it differs between idle and walk), concrete boot cues from the Essential Footsteps pack, deeper and louder for the boss, plus a landing sound; `URPGBossMusic` (fades in when the encounter wakes, out on death or reset; placeholder track `Starter_Music_Cue`); `ARPGArenaAmbience` (wind bed, game only). Attached by `URPGPlayerMovesSubsystem`. The pack's own footstep notify exists on one animation and has no sounds.
- **Tooling:** `Scripts/shot.sh x y z pitch yaw name` moves the editor viewport and saves a picture (turn off throttling first with `Scripts/Editor/no_throttle.py`, or the viewport does not redraw); `Scripts/Editor/pie_look.py` takes player-camera screenshots in PIE (run twice, the first PIE after a start is black); `Scripts/Rebuild.ps1 [-Tests]` closes the editor, builds, tests and relaunches; Python cannot rerun construction scripts, so the arena actors expose `Rebuild()`.

- **Polish pass (2026-10-20):** `ARPGEmberField` (380 emissive spheres on one instanced mesh, moved on the CPU: most are born at the brazier flames, some drift as ash; ticks in the editor viewport too), banners (engine plane with `M_Banner`, crimson with gold trim, swung rigidly a few degrees by the dressing actor through `SwayDegrees` and `SwayPivot`; Python cannot reach world position offset in a material, so cloth bending is not possible this way), hanging chains (same sway), drifting mist (the sample's fog card material turned down, `MI_Arena_Mist`), the fog gate across the entrance (the same cards, brighter, `MI_Arena_FogGate`), stone for the greybox pillars (`MI_Arena_Pillar`), and a dark ground disc under and beyond the wall (`MI_Arena_Outside`: the bright void showed between the floor edge and the ruins; a first version looked like a sea, so wetness is off and roughness up). Slabs use the floor stone at one tile each (their own kit material turned mirror-like). Materials are made by `Scripts/Editor/make_polish_materials.py`. The sample's fog card material is self lit (emissive 2000): at night it glowed white until it was turned down.

## Direction: the Freeze is final (2026-10-20)

- `Master_Design_Freeze_v1_2_AI_Implementation_Ready.md` is the single source of truth for mechanics, numbers, gates and
  the test matrix. Where the project disagrees, the project changes (list in `TASKS.md` G0-5). `Master_Design_Freeze_v1.md`
  was deleted; v1.1 is folded into v1.2.
- Changes the Freeze forces on the current build: phase two at 0.60 (was 0.50), the legacy fireball grant is removed from
  phase two, (the double tap window was already 0.30 s), the x2.5 critical applies to the riposte hit only (was every hit during
  knockdown), a separate 100 point boss posture (the pack has no poise: the earlier poise rebuild stays as the stagger
  trigger until G2-5 replaces its input), a frontal riposte.
- Boss 01 is re-skinned while its mechanics stay as frozen (A1 to A6 roles, timings and counterplay unchanged): the cane
  becomes the great sword, the golden dagger becomes a thrown ember javelin, the hammer leap becomes the same sword driven
  into the floor. One weapon, a clearer identity, no Margit copy. Name and story come later. Pending U approval (`TASKS.md` section 6).
- Division of work: art (models, animation, VFX) by Antigravity from `ASSET_REQUEST_BOSS01.md`; code, data, tests and review
  by Claude; Antigravity also does in-editor content jobs (montages, data fill, materials, Niagara hookup) in `TASKS.md`
  section 3 after assets land, and Claude reviews the results.
- Process: lighter than the Freeze's literal text. One delta audit instead of a ten field table per item; the 20 trial rule
  applies to timing edges and deterministic logic (scripted); the 30 encounter run is a single soak at Gate 4.
- Third-party content is never committed: `.gitignore` covers every third-party folder, including the pack copies and
  retargets under `Content/OneBossFight` (`GreystonePack`, `SevarogPack`, `Characters/Greystone`) and the archived copies.
  Files left the git index only (still on disk); commits already made keep their history.

- **G0-5 done (2026-10-20):** `PhaseTwoHealthFraction` 0.60; `bFireballEnabled` false (the fireball code and asset stay); `bCriticalOnEveryHit` false (the 2.5x returns only with the riposte). The pack's `GS_ChargedAttack` (1.57 s windup) is the stand-in for A2.
- **A2 stand-in facts (2026-10-20):** the pack's rare close attack (`GA_GS_Boss_CloseRare`, tag `Ability.Melee.CloseRare`, montage `GS_ChargedAttack`, 3.40 s, ability ends at 3.14 s) is the A2 stand-in: its second trace window (1.93 to 2.11 s) hurts, its first (1.57 to 1.76 s) did not hurt anyone in the tests; reach about 230 to 330 cm like a ground slam. The pack boss has no weapon actor (its sword is part of the mesh), so tests do not need it to equip anything. The boss moves by tag: Close = `GS_Attack01/02`, CloseRare = charged, Far = `Mid01`, Leap (cooldown 15 s) and Sprint attack are Far Rare, Retaliation. `RPGBlueprintCall::TryActivateByTag` has a force option for scripted starts.
- **Boss 01 body (2026-10-20, owner):** the Paragon Sevarog mesh (312 cm native, in the project under `Content/ParagonSevarog`) is rigged to `SK_CombatMannequin` in Blender by Antigravity (skin weight transfer, material slot names kept), customised into the Ember Warden (crown or horn, crimson cloth, ember seams, new silhouette cue) and given a new AAA great sword. The original Paragon materials are re-attached inside Unreal. Reason: the Blender-only blockouts delivered in Report 01 were far below the AAA bar; an existing AAA body reaches it immediately. Fully custom body only if the rig proof (T1) fails.
- **Posture (2026-10-20):** Freeze Layer A is the pack's boss poise attribute (100 points, the pack gate already drains it per hit and starts the hit stun that `URPGBossStagger` turns into the stance break). `URPGBossPosture` owns the regeneration rule (the pack's own regen for this attribute is disabled at runtime) and the bookkeeping. Drain per hit is still 20 (light) and 50 (heavy, attack power 3 or more); per weapon values come with G3-1.
- **Riposte (2026-10-20):** the Freeze riposte is built as logic first. `URPGRiposteInput` (on the player) sends every Light Attack press to `URPGBossStagger::TryRiposte`; an accepted press (boss down, within 150 cm, in the 120 degree cone, player facing it, not used in this break) arms the critical for the first hit within 1.2 s, and that hit is multiplied by 2.5 once. The pack's own attack plays for the press (stand-in); the pack's fatality system was inspected and not used because the sword has no paired fatality montages (`GA_Sword_Melee.FatalityAttackMontages` is empty). The synchronized pair from the art list (A-11) replaces the stand-in later.
- **Fog gate (2026-10-20):** `ARPGFogGate` (Arena) replaces the static gate cards. It reads the boss every 0.2 s (encounter dormant flag, health attribute, only a boss seen alive can die) so a missed event cannot stick it. Idle size 0.35, closed 1.0 with a blocking box, cleared 0 after the boss dies; the mist cards grow from nothing (no material parameter). `dress_arena.py` places it. Stagger cooldown default is now 0 (Freeze 17.2).
- **Delivery verification (2026-10-20):** art deliveries are accepted only after an engine import (`Scripts/Editor/import_boss01.py`) and a checker run (`Scripts/check_boss01_delivery.py`: bone and node names, geometry nodes, texture detail, picture content by decoded pixels). A check that passes is not enough: the first checker was passed by renders of an empty grey scene. Reports must describe each picture in one sentence.
- **Boss HUD and victory (2026-10-20):** `URPGBossHud` (component) owns the encounter presentation state (Dormant, Fighting, Victory) and drives `URPGBossHudWidget` (tree built in C++, no Widget Blueprint). The pack boss creates its own bar (`BP_BossHUD`, Blueprint variable "Boss HUD") with the pack's name for it; ours replaces it and the pack's is collapsed by reflection every 0.2 s. `OnVictory` fires once per encounter generation (a reset opens a new one). The pack destroys the boss about 3.5 s after death, so the widget runs its own banner fade and outlives the boss. Name "Ember Warden" and subtitle "Embers Unbound" are provisional.
- **A1 and A3 stand-ins (2026-10-20):** the tracker maps the pack close attacks to stages: A1 = `GS_Attack03`, A1b = `GS_Attack04` (the pack chains it at once), A3a = `GS_Attack01`, A3b = `GS_Attack02` (the pack chains it at its 0.54 s follow-up notify). Commit points sit 0.04 to 0.07 s before each trace window. A chained stage (A1b, A3b) runs the branch check when its montage starts: player within `BranchRange` (400 cm) and inside a `BranchConeDegrees` (120) frontal cone, else the montage is stopped before its trace window. These clips have a 0.12 to 0.17 s windup, the Freeze wants 0.35 to 0.40 s: accepted for the stand-in, replaced by authored clips (TASKS A-xx).

## Open

Settled: player and boss are the pack's mannequin player and great-sword boss (2026-10-19). Greystone (Paragon) and Sevarog (Paragon) come back only on a pack that has been fixed for them.

- Lighting strategy: baked first; Lumen benchmarked separately (decide at the packaged performance milestone, `TASKS.md` G4-1).
- Whether pack crafting, dialogue and inventory screens stay reachable (KI-030).
- Whether a 3060 packaged result is an acceptable proxy for the 2060 Super target.
- Boss music: needs an asset from the user (a placeholder plays until then).
