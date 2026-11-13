# BN-16..20: manual check of the heuristic-O KIs (lane BN, batch 4 of 10, per X-2213)

C (implementer), 2026-11-12. The X-2219 correction is carried forward: the Greystone child is a Development-only opt-in test path (`rpg.GreystonePlayerTestPawn` defaults to 0) and is not the active default.

**Not done:** no code, asset, engine, build, PIE or test work. No KNOWN_ISSUES status changes and no commits.

| Task | KI | Row | Evidence checked | Manual class | Offline follow-up? |
|---|---|---|---|---|---|
| BN-16 | KI-035 | `KNOWN_ISSUES.md:102`: weapon socket transforms were copied from the mannequin. Twin blades, claymore, dual swords, polearm, bow and quiver were not checked on Greystone | Needs a visual check per weapon and socket edits in the Editor | **E** (visual + asset) | No |
| BN-17 | KI-036 | `:103`: stage 3 edits 60 pack Blueprints and adds 389 assets; a re-import removes the re-pointing. The action is to re-run `repoint_player_refs.py` | A recorded re-import hazard with a procedure (same shape as KI-033) | **L** (hazard + procedure) | No |
| BN-18 | KI-039 | `:106`: Sevarog hit tracing covers a 67 cm socket span plus a 50 cm radius; the blade beyond `root_weapon_end_r` may be uncovered | Needs a hit-feel check in play; lengthening the span is an asset edit | **E** (play + asset) | No |
| BN-19 | KI-040 | `:107`: several retargeted Greystone layer Blueprints reference a missing `/Game/ABP_CombatAnimLayersBase_Grey` and log `CreateExport: Failed to load` | Re-parenting is Blueprint asset work, and testing each weapon style needs PIE | **E** (asset + PIE) | No |
| BN-20 | KI-045 | `:112`: eight retargeted enemy montages point at missing root-level assets; `/Game/RMB_Cast_Grey1` is a keep-alive copy. "Not used by Greystone" | Rebuilding montages and deleting the copy are asset operations | **E** (asset) + L (unused) | No |

**Batch 4 result:** 0 true O. Running total: 1 O (KI-026) out of 19.

**Limits:** row reads only. No asset was opened.
