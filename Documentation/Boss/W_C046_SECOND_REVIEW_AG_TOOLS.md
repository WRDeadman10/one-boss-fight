# Queue W Codex second review: Antigravity tools and source

Read-only review of selected Lane A deliverables that affect project tools/content. No asset was opened or saved; no source or Antigravity-owned file was edited.

## Findings

### BUG — the A2 montage writer reports a three-clip composite but creates only from the raise clip

`create_tier1_art_assets.py:69-87` loads and measures Raise, ApexHold, and Slam, then initializes `AnimMontageFactory.source_animation` with only `raise_clip` and creates the montage. Lines 94-105 set blending and save, but do not add montage segments/sections for `hold_clip` or `slam_clip`; the log nevertheless reports `total_len` as the “Composite length.” Unless the factory or an external callback adds those clips (none is visible in this script), the generated montage cannot be assumed to contain the documented three-clip sequence. This is a source-level discrepancy, not a claim that the asset exists or was generated. Keep it unwired and have the Lead correct/inspect the authoring API and resulting asset before use.

UE 5.5 API cross-check confirms the concern: `Engine/Source/Editor/UnrealEd/Classes/Factories/AnimMontageFactory.h:23-28` documents `SourceAnimation` as “the only AnimSequence contained”; `Engine/Source/Editor/UnrealEd/Private/Factories/AnimMontageFactory.cpp:83-90` creates one `FAnimSegment`, adds it to the first slot track, and sets composite length from that one sequence. `Engine/Source/Runtime/Engine/Classes/Animation/AnimCompositeBase.h:67-81,107-137,246-257` defines the segment reference/timing fields and segment array; `AnimMontage.h:673-679,881-887` defines montage section data and its add-section API. These installed declarations/source establish what the current factory call does, but do not prescribe a complete correct Unreal Python authoring sequence.

### BUG — the documented content-writer safety guard does not require dry-run or explicit execution

`V_A036_CONTENT_SCRIPT_SAFETY.md:14-20` calls dry-run default a required safety principle and its matrix says GUARD-02 validates properties before save. The reviewed Tier 1 writer's `main()` directly calls both asset-writing functions (`create_tier1_art_assets.py:108-116`); there is no dry-run flag or explicit `--execute` check. The pre-save checks are only non-null assertions for templates/clips and successful asset creation (`:38-56,69-87`), not validation of Niagara geometry/emitter settings, montage segment membership, or resulting timing. `test_content_script_safety.py:28-39` checks text order (`assert` occurs before `save_loaded_asset`) and a path literal; it does not enforce an execution gate, validate the documented properties, or prove the assertions cover each save. The report's universal guard claim is therefore too broad for this script.

## Scope and limits

The test does inspect the designated files, but its source-text checks are narrow and do not prove runtime asset safety. The Tier 1 creator is labeled Lead-run and was not executed during this review. No claim is made about saved asset content, package references, VFX appearance, or runtime wiring. Do not wire or ship the generated A2 montage until the sequence and timing are confirmed in Editor and the writer's guard behavior is corrected/re-reviewed.

## Follow-up

Queue X X-C001–X-C005 added a default dry-run gate and made the A2 writer fail closed rather than creating the incomplete montage. The source no longer makes the three-clip composite claim. Focused offline guard tests pass 7/7; Editor asset validation and Lead review remain open.
