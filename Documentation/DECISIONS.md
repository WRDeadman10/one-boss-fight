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

## Open

- Boss concept (dragon? `CuteDragon.blend` exists in project root).
- Player and boss asset packs (free Paragon/Epic first; paid melee animation pack only if needed).
- Lighting strategy: baked first; Lumen benchmarked separately.
