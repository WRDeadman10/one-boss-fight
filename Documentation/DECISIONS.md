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

## Provisional

| Item | Note |
|---|---|
| Toolchain | Visual Studio 2026 (18.x), MSVC 14.51, Windows SDK 10.0.26100. UE 5.5 prefers MSVC 14.38 and warns "not a preferred version". M0 module compiled with 0 errors. Revisit if a later build fails: install MSVC 14.38 (17.8) from the VS Installer. |
| Target PC | RTX 2060 Super 8 GB. CPU, RAM, driver to be recorded at first baseline (M1). |

## Open

- Boss concept (dragon? `CuteDragon.blend` exists in project root).
- Player and boss asset packs (free Paragon/Epic first; paid melee animation pack only if needed).
- Lighting strategy: baked first; Lumen benchmarked separately.
