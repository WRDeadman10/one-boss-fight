# BN-21..25: manual check of the heuristic-O KIs (lane BN, batch 5 of 10, per X-2213)

C (implementer), 2026-11-12.

**Not done:** no code, asset, engine, build, PIE or test work. No KNOWN_ISSUES status changes and no commits.

| Task | KI | Row | Evidence checked | Manual class | Offline follow-up? |
|---|---|---|---|---|---|
| BN-21 | KI-050 | `KNOWN_ISSUES.md:117`: the retired test and playtest rows are marked RETIRED in TEST_PLAN; the pack's menus, input and HUD have had no controller playtest | Needs a controller playtest (same gate as KI-020/022) | **E** (playtest) | No |
| BN-22 | KI-055 | `:121`: the UnrealClaude plugin can crash the editor after a script ends. The action is "Save work before scripts…" | A recorded tooling hazard with a workaround | **L** (hazard + workaround) | No |
| BN-23 | KI-057 | `:124`: HEAVY poise scaling (50 per hit) is unverified on a victim | Needs a PIE hit on a non-blocking pack enemy | **E** (PIE) | No |
| BN-24 | KI-059 | `:126`: a neutral dodge turns and rolls away (not a backstep); a double tap pays stamina twice (not measured); the full roll restarts from the quick-dodge position | Later work added a Mixamo backstep asset (`AM_ER_Backstep_Mixamo_V2_Fit_Greystone`, plus the owner's 2026-11-08 Mixamo decision). Which backstep the default mannequin route uses, and the stamina cost, need a PIE measurement. **The row text may be partly stale.** A row refresh needs the lead's check against the runtime, so it is not done here | **E** (PIE measurement) | No (a row refresh first needs runtime evidence) |
| BN-25 | KI-063 | `:130`: the A1/A3 stand-ins have a 0.12-0.17 s windup and 0.30 s trace windows, against the Freeze target of 0.35-0.40 s windup and 0.15-0.20 s active | Needs authored clips (art) or a play-rate trial (PIE) | **E** (PIE) + D (art is parked) | No |

**Batch 5 result:** 0 true O. Running total: 1 O (KI-026) out of 24.

**Limits:** row reads and one asset-name check (git status) only.
