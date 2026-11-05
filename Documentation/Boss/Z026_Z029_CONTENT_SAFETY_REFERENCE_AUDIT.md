# Queue Z Batch 6 — content safety, loads, namespace, references

**Scope:** Z026–Z030 read-only repository/source review. No Editor writer, asset operation, test, build, package or editor process was run.

## Z026 — Editor writer gates

The existing static inventory `Documentation/Boss/X_C006_ASSET_WRITER_INVENTORY.md` records 361 Python files under `Scripts/Editor`: 30 create, 69 modify, 42 map setup, 220 read-only. The source classifier (`Scripts/Tools/inventory_editor_asset_writers.py`) is literal-marker based; map operations and dynamically called helpers can be misclassified. The paired save-site heuristic reports 141 non-read-only candidates, 80 with a literal save API, 61 without one, and 34 with an assertion/guard marker before first save. A marker is not proof that every property, destination, reference, or save path is guarded.

Concrete writer hazards already identified in `X_C006_C009_ASSET_WRITER_AUDIT.md`: `Scripts/Editor/rpg_content_lib.py:23–28` can delete/recreate via a dynamic path without referencer validation; `sevarog_pack_02_montages_abilities.py` and `import_boss01.py` delete existing targets before replacement; `air_jump_tuning.py` and `boss_poise_armor.py` save under third-party `/Game/AdvancedARPGCombat`; `setup_m7_beam_materials.py` deletes/recreates under `/Game/BeamPack`. Existence checks do not establish referencer clearance or authorization. These remain candidates to audit by invocation context; no execution or edit was made.

Dry-run/control tests are scoped, not global. The cited `test_content_script_safety.py` checks specific scripts and text markers; it does not prove all 361 scripts obey a shared dry-run, project-root, reference or no-delete policy. A literal-save inventory can also miss wrapper saves. Do not infer every writer is safe from the inventory header.

## Z027 — synchronous soft-reference loads

Static `LoadSynchronous()` call sites include early/setup paths and combat-time fallbacks:

| Source | Load context | Timing risk class; measurement |
|---|---|---|
| `RPGEncounterSelectionSubsystem.cpp:209–210`, `RPGEncounterBinding.cpp:221–225` | selected definition/binding build and participant hydration | startup/rebind synchronous dependency load; no hitch measurement in this audit |
| `RPGBossPhases.cpp:65–67` | BeginPlay preloads immunity/roar assets; later phase path also has fallback loads (`:271,301–307,471`) | mostly setup plus event fallback; no cold first-use latency bound |
| `RPGBossStagger.cpp:92–93,179–182` | setup loads fall/down/riposte clips; later immunity/fall/riposte paths retain synchronous fallbacks | combat event cold-load risk if cache/preload assumptions fail; no hitch measurement |
| `RPGBossBleed.cpp:35–36`, `RPGPlayerParry.cpp:57`, `RPGDodgeTiming.cpp:124,305–306` | component setup/input path and montage access | can occur near interaction/input unless already resident; no cold-load trace cited here |
| `RPGBossDeath.cpp:137,151`, `RPGBossRemains.cpp:56–58`, `RPGSevarogDirector.cpp:205` | death/remains/phase-two visual fallback events | event-time synchronous load possibility; no cold first-use measurement |
| `RPGBuildSelect.cpp:210` | build selection row icon resolution | selection UI load; no UI hitch measurement |
| `RPGFrameworkMoveExecutor.cpp:482`, `RPGBossFrameworkProfile.cpp:*` | framework card cue preload and test/profile compilation | proof/profile path; not evidence about the shipped legacy boss path |

This inventory identifies code locations and potential timing context only. It does not prove assets are cold, that a hitch occurs, or that shipping cook includes each object. Current first-use hitch measurements remain UNKNOWN.

## Z028 — mount and naming boundaries

`Config/DefaultGame.ini` explicitly cook-lists project `/Game/OneBossFight/...` roots and selected external vendor roots, including `/Game/ParagonSevarog`, portions of `/Game/AdvancedARPGCombat`, `/Game/BloodPack`, footsteps and StarterContent (lines 23–51). This is a selected cook-root list, not permission to modify vendor assets. `Content/` also contains separate marketplace/vendor namespaces (AdvancedARPGCombat, BeamPack, BloodPack, Paragon* and others) alongside project-owned `/Game/OneBossFight`.

Historical `V_A067_CONTENT_FOLDER_STRUCTURE_REVIEW.md` proposes moving/excluding proof/scratch folders; `V_A068_ASSET_NAMING_AUDIT.md` also notes namespace collisions and recommends avoiding in-place renames where redirects/references may result. These are proposals, not authorization. Vendor package names and the cooked framework dependencies must remain intact absent explicit owner decisions. Asset counts in those reports are treated as dated Editor censuses, not refreshed filesystem counts.

## Z029 — redirector/reference evidence reconciliation

`V_A037_REFERENCE_INTEGRITY_CENSUS.md` (dated 2026-11-06) reports 743 project assets and zero project redirectors/broken soft references, plus three third-party BeamPack redirectors. `V_A068_ASSET_NAMING_AUDIT.md` (also 2026-11-06) reports 827 project assets. Current filesystem query sees 396 files under `Content/OneBossFight` (mixed package/file types); it cannot identify `ObjectRedirector` classes or resolve Blueprint soft references. These counts have different inventory methods and do not establish current referencer integrity. Treat 743 vs 827 as an unresolved census discrepancy, not a finding that either count is authoritative.

No current independent Editor Asset Registry receipt or raw run identity was cross-checked in this task. The prior V-A037 zero-redirector claim is historical/source-documented; third-party redirectors remain out of project cleanup scope. `report_owner_cleanup_referencers.py` produces direct referencer evidence for its specific targets; it does not by itself prove transitive closure or authorize cleanup. No rename, fixup, deletion, move or asset load was performed.

## Z030 — receipt

The content safety baseline is conservative: static inventories guide review; they do not grant write authorization. Existing concrete writer hazards, synchronous load sites, external mount dependencies and conflicting historical census counts are reported with their limits. No content changes were made. `git diff --check` is the only validation of this documentation update.
