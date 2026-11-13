# BN-11..15: manual check of the heuristic-O KIs (lane BN, batch 3 of 10, per X-2213)

C (implementer), 2026-11-12.

**Not done:** no code, asset, engine, build, PIE or test work. No KNOWN_ISSUES status changes and no commits.

| Task | KI | Row | Evidence checked | Manual class | Offline follow-up? |
|---|---|---|---|---|---|
| BN-11 | KI-024 | `KNOWN_ISSUES.md:91`: the Realistic Blood VFX pack spawns nothing (`MI_BloodDirection` is missing); weapon `ImpactNiagara` is empty. The action is to delete `Content/BloodPack` or find a replacement | `Content/BloodPack` still exists locally and is git-ignored (`.gitignore:90`). Deleting it is a content change, and the replacement VFX is art work | **D** (content/art choice; art is parked) | No (deletion is an asset operation) |
| BN-12 | KI-026 | `:93`: `pie_combat_smoke.py` expects a training dummy that is no longer in the level. The action is "Use the boss and weapons drivers" | `Scripts/Editor/pie_combat_smoke.py` still exists. Its non-archive references include `Scripts/Editor/README.md:224` and the historical, explicitly retired `Documentation/TEST_PLAN.md:938`, plus old `Content/UnrealClaude/Scripts/*` session scripts and two 2026-10-29 status snapshots. No current runbook was found that calls it | **O** (tooling hygiene) | **Yes:** retire the driver or mark it obsolete in its docstring/README, with the lead's approval. This is a script/doc edit, so it is outside this read-only lane |
| BN-13 | KI-029 | `:96`: about 25 pack assets referenced but missing from the download; they load as empty references. The action is to replace them in the widgets if a blank icon shows | Confirming a blank icon needs the Editor or UI to be seen | **E** (visual check) + L | No |
| BN-14 | KI-030 | `:97`: the pack has no poise, crafting, dialogue or quests. The action is "Decide whether they are wanted" | This is explicitly a scope decision | **D** (owner scope) | No |
| BN-15 | KI-033 | `:100`: the poise edits live inside the git-ignored pack (`.gitignore:92`, `Content/AdvancedARPGCombat/`); a re-import removes them. The action is to re-run `Scripts/install_poise.py` and `Scripts/Editor/poise_data.py` | Both scripts exist. Re-running them is Editor/asset work, and only needed after a re-import | **L** (recorded hazard with a procedure) | No |

**Batch 3 result:** 1 true O (KI-026). Running total: 1 O out of 14.

**Limits:** row, file-existence and grep reads only. Whether KI-026's driver is safe to remove is the lead's call.
