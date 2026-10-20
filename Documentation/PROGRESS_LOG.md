# Progress log

Short chronology. Reasons and details are in `DECISIONS.md`; open work in `TASKS.md`.

## 2026-10-18 first build (own C++ combat)
- M0 repo and build, M1 benchmark stats, arena and player defaults (5 tests), M2 asset inspection and proof level, M3 player combat (attributes, melee trace, state machine, lock-on), M4 Sevarog boss (7 attacks, phases, StateTree mirror, encounter reset), M5 weapons and feedback, UI, settings, pause menu, boss combo, playtest fixes, camera, performance deferred. 70 automation tests at peak.
- M7 asset integration: Niagara VFX, sound variants, Blender arena meshes with Deadly Ruins stone, Cinzel font, licences; roll animation retargeted and fixed (root motion moved from pelvis to root).

## 2026-10-19 switch to the Advanced ARPG pack
- User decision: use the pack as the backbone, staged. Stage 1 import (2,506 files), 1b config merge, 2 pack game mode default, 4 poise on the pack's attributes, 3 Greystone and Sevarog on the pack.
- Stage 3: IK retarget of all 389 pack animation assets to Greystone, 60 player-side assets re-pointed, 40 sockets copied (first on the skeleton, which silently failed; later on the mesh), `BP_GreystonePlayer`.
- Sevarog as a pack boss: pawn from the great-sword boss, hidden scythe proxy mesh for hit traces, `GA_Sev_*` abilities, pack-format montages, director component for gate, phase two, lightning and reset, `L_SevarogArena`, turn in place, death montage.
- Greystone polish: all eight layer Blueprints failed to load (stale parent path), fixed with a temporary base copy and re-parenting; four blend spaces repaired; default unarmed layer consolidated.
- Stage 5: parity table in `DECISIONS.md`, C++ combat and 23 tests archived and removed, start map set to the Sevarog arena. 5 tests remain, `Content.PackWiring` added.

## 2026-10-20 open items and polish
- KI-049: controller present from BeginPlay, behaviour held by the director, entrance then resume. KI-047: `URPGANS_ChargeToTarget` and `AM_SevPack_Charge`. KI-048: benchmark runner ported (fight bot through pack abilities); first baseline 79 FPS unpackaged.
- Found and fixed: entrance, exit and death abilities had empty montage references (assets deleted and recreated; CDO edits need `modify()` before save).
- Smaller items and differences: `URPGHideBones`, weapon fit check, triple combo through `AN_PerformFollowUp`, shockwave ring, lightning strike at the player (projectile moved above a marked spot, thunder beam on impact).
- Docs: `PROJECT_STATE.md`, `TASKS.md`, this log, `CLAUDE.md` for fast start.
