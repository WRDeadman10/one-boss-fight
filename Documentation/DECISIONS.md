# Decisions

| Date | Decision | Reason | Status |
|---|---|---|---|
| 2026-10-18 | UE **5.5.4**, pinned | User choice; stable release with Enhanced Input, StateTree | Locked |
| 2026-10-18 | C++ module name `OneBossFight` | Matches project name; single primary game module | Locked |
| 2026-10-18 | Custom C++ combat, **no GAS** | Souls-style frame-data combat (animation-owned windows); GAS adds overhead and fights that model | Locked |
| 2026-10-18 | Boss AI = weighted C++ selector in `UBossCombatComponent` + thin StateTree for top-level states; no Behavior Tree | Mirrors distance-gated weighted action selection used by Souls-style bosses | Locked |
| 2026-10-18 | Win64 only, 1920x1080, 120 FPS target on RTX 2060 Super | Per `Idea/IDEA.md` | Locked |
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

## Open

- Boss concept (dragon? `CuteDragon.blend` exists in project root).
- Player and boss asset packs (free Paragon/Epic first; paid melee animation pack only if needed).
- Lighting strategy: baked first; Lumen benchmarked separately.
