# BT-68 Full-Mode PIE Driver Teardown & Startup Bounding Hotfix Report

- **Date:** 2026-11-17
- **Task ID:** BT-68
- **Category:** Safety hotfix / PIE driver lifecycle hardening
- **Status:** Complete / Verified

## 1. Problem Statement
During the BT-67 Full-mode lifecycle audit (`Documentation/Boss/BT_67_FULL_MODE_BOSS_DEATH_LIFECYCLE_AUDIT.md`), safety and race defects were identified in `Scripts/Editor/pie_sevarog_arena_route_acceptance.py`:
- In Full mode, `tick()` runs via Slate post-tick callback (`unreal.register_slate_post_tick_callback(tick)`).
- When a user stops PIE prematurely (e.g. pressing Escape), `live_world()` returns `None`.
- The driver previously took no action when `live_world()` returned `None` during observation. In Full mode without `boss_defeated`, it simply returned without completing or cleaning up.
- Because `run_sevarog_arena_route_acceptance.ps1` runs without a timeout deadline in Full mode, pressing Escape caused the runner and driver to hang indefinitely, leaving C-1155 dual engine locks and temporary route config active on disk.
- Furthermore, if PIE failed to launch initially after `editor_request_begin_play()`, the driver would wait indefinitely for `live_world()` to appear.
- Additionally, Lead review identified a terminal-order race: if `boss_defeated` is observed in log text concurrently with PIE ending (or during the 2s world loss grace period), an un-ordered world-loss check could prematurely trigger failure before validating boss death and required evidence.

## 2. Implementation Details
In `Scripts/Editor/pie_sevarog_arena_route_acceptance.py`:
1. **Terminal Precedence for Boss Defeat:**
   - In `tick()` during the `observe` phase, `if MODE == "Full" and STATE["checks"].get("boss_defeated"):` is evaluated immediately before world loss checks.
   - If `boss_defeated` was parsed, required evidence is validated; if valid, `finish("PASS")` is called, ensuring defeat evidence takes precedence over any concurrent world teardown.
2. **PIE World Lifecycle Tracking:**
   - Added `"pie_world_observed": False` and `"pie_world_lost_at": None` to `STATE`.
   - When `live_world()` is first valid (`L_SevarogArena`), `STATE["pie_world_observed"]` is set to `True` and `STATE["pie_world_lost_at"]` is reset to `None`.
3. **Teardown / Premature Stop Detection:**
   - If `live_world()` returns `None` after `pie_world_observed` has become `True` (and no boss defeat occurred):
     - Sets `STATE["pie_world_lost_at"] = now` if not already set.
     - When `now - STATE["pie_world_lost_at"] >= 2.0` (2 consecutive seconds of lost world), driver triggers:
       `fail("PIE session ended prematurely without boss defeat (Escape or manual PIE stop observed)")`
     - This immediately generates `acceptance.json` with `result: "FAILED"`, calls `editor_request_end_play()`, resets keep-alive, unregisters Slate post-tick, and exits cleanly.
4. **Initial Startup Bounding:**
   - If `live_world()` has not been observed within 60.0 seconds of requesting `begin_play`, the driver triggers:
     `fail("PIE world not observed within 60 seconds of begin_play request")`
   - Active boss combat time remains completely unbounded once the world is live.
5. **Preserved Semantics:**
   - Raw BT tick count remains blocked (`"BLOCKED_NOT_INSTRUMENTED"`).
   - Receipt schema, exit codes, and Smoke mode behavior remain completely preserved.

## 3. Touched Paths & Hashes
- `Scripts/Editor/pie_sevarog_arena_route_acceptance.py`
  - SHA256: `6759E8296D56D0BAC1FFF9B97BAC7ED82FC8099C801F52A2EF52FDF9D55C50F6`
- `Scripts/Tools/test_c1619_sevarog_arena_route_contract.py`
  - SHA256: `68B0894338946C36F97D6487F04C5E9502C7AB91E466E857847812B91D3227D2`
- `Documentation/Boss/BT_68_PIE_TEARDOWN_SAFETY_HOTFIX.md`
  - This document.

## 4. Verification
- `python Scripts/Tools/test_c1619_sevarog_arena_route_contract.py`: **29/29 PASS**
- `python -m unittest Scripts/Tools/test_author_production_framework_profile_contract.py`: **15/15 PASS**
- `python Scripts/Tools/check_doc_links.py`: **broken_links=0**
- Strictly source-only: 0 builds, 0 Unreal Editor launches, 0 PIE runs, 0 asset edits, 0 git commits/pushes.
