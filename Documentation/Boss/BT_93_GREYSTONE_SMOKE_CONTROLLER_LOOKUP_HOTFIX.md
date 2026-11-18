# BT-93: Greystone Visual Smoke Driver PlayerController Lookup Hotfix

**Author:** Antigravity (Implementer)
**Date:** 2026-11-18
**Scope:** Source-only hotfix of player controller and pawn lookup in `Scripts/Editor/pie_greystone_visual_smoke.py` following Run 2 failure (`Saved/GreystoneVisualSmoke/Run_20261117_213058_ae4289f2`).
**Constraint:** Strict source-only hotfix; 0 tests, 0 builds, 0 Unreal Editor launches, 0 PIE runs, 0 asset/config mutations, 0 git commits/pushes. Any retry requires separate fresh C-1155 approval provenance and is NOT launched here.

---

## 1. Problem Statement & Failure Analysis (Run 2)

In Run 2 (`Run_20261117_213058_ae4289f2`), the driver reached `phase == "waiting_for_possession"`, discovered the PIE game world `L_SevarogArena`, and attempted to resolve the PlayerController:
```python
pc = world.get_first_player_controller()
```
The Unreal Engine 5.5.4 Python runtime failed closed with an unhandled exception:
```text
unhandled driver exception: 'World' object has no attribute 'get_first_player_controller'
```
As verified by the Run 2 receipt and report (`Documentation/Boss/BT_83_GREYSTONE_SMOKE_RUN_2.md`):
- Receipt emitted `result: FAIL`, `accepted: false`.
- CVar `rpg.GreystonePlayerTestPawn` was restored to `0` and verified by readback.
- `DefaultGame.ini` SHA256 was unchanged.
- Both C-1155 locks were cleanly cleared upon Editor exit.
- Possession and visual criteria were not evaluated due to the runtime error.

---

## 2. API Evidence & Supported Pattern

1. **Native Unreal Engine 5.5.4 C++ Declaration:**
   In `Engine/Source/Runtime/Engine/Classes/Kismet/GameplayStatics.h` (Line 192):
   ```cpp
   UFUNCTION(BlueprintPure, Category="Game", meta=(WorldContext="WorldContextObject", UnsafeDuringActorConstruction="true"))
   static APlayerController* GetPlayerController(const UObject* WorldContextObject, int32 PlayerIndex);
   ```
2. **Project-Wide Python Convention:**
   Over 40 existing PIE automation scripts across `Scripts/Editor/` (e.g., `pie_grey_check.py:81`, `pie_greystone_root_motion.py:170`, `pie_boss_encounter.py:83`) consistently utilize:
   ```python
   pc = unreal.GameplayStatics.get_player_controller(world, 0)
   pawn = pc.get_controlled_pawn() if hasattr(pc, "get_controlled_pawn") else (pc.get_pawn() if hasattr(pc, "get_pawn") else None)
   ```

---

## 3. Implementation of Hotfix

In `Scripts/Editor/pie_greystone_visual_smoke.py`, lines 494-505 were updated from:
```python
            pc = world.get_first_player_controller()
            if not pc:
                if now - STATE["started_at"] >= 15.0:
                    fail("timeout waiting for PlayerController 0")
                return

            pawn = pc.get_pawn()
            if not pawn:
                if now - STATE["started_at"] >= 15.0:
                    fail("timeout waiting for pawn possession")
                return
```
to the robust, fail-closed supported pattern:
```python
            pc = unreal.GameplayStatics.get_player_controller(world, 0)
            if not pc:
                if now - STATE["started_at"] >= 15.0:
                    fail("timeout waiting for PlayerController 0")
                return

            pawn = pc.get_controlled_pawn() if hasattr(pc, "get_controlled_pawn") else (pc.get_pawn() if hasattr(pc, "get_pawn") else None)
            if not pawn:
                if now - STATE["started_at"] >= 15.0:
                    fail("timeout waiting for pawn possession")
                return
```

### Safety & Invariants Preserved:
1. **Bounded Polling:** If either `pc` or `pawn` is `None` during early spawn frames, the callback returns to allow next-tick polling until the 15.0-second deadline expires.
2. **Next-Tick Replacement Compatibility:** If `pawn` is possessed but has not yet been replaced with `BP_GreystoneERPlayer_C`, the driver polls until replacement or 15.0s timeout.
3. **Fail-Closed Guarantees:** Strict CVar restoration to `0`, exact receipt writing (`accepted=False` on error), and unregistering the Slate callback are 100% preserved.
4. **Zero Asset/Config Changes:** `Config/DefaultGame.ini` and Content assets remain untouched.

---

## 4. Verification & Updated Canonical Hashes

1. **Python Syntax Compilation:**
   ```bash
   python -m py_compile c:\UnrealProject\OneBossFight\Scripts\Editor\pie_greystone_visual_smoke.py
   ```
   Result: Exit code 0 (clean compilation, 0 errors).

2. **Doc Link Verification:**
   ```bash
   python c:\UnrealProject\OneBossFight\Scripts\Tools\check_doc_links.py
   ```
   Result: `broken_links=0`.

3. **Current Four-Way Source Hashes (SHA256):**
   - `runner`: `FAB7A89AC4710F9F955F8A3E9DDA18C97F0882BC973132E210213B070B14DB1F`
   - `driver`: `89ED8BF38C5C2A70289E71C24AB1DC6D09A10E248BE7D8266BEA0BFCE6F703F0` *(Updated)*
   - `retarget_cpp`: `22A04C1A5B12AAC1A045EC33AB2E346064D55FBABA83FA5E25FA2E749C5778AF`
   - `moves_cpp`: `60097589BA1FAF3C12827ECDF6AC0FD32651EA3AA292EF25C17AB1878D7FB838`

---

## 5. Next Steps

- `BT-93` is moved to `review` on the Kanban board.
- The implementer does **not** launch or retry PIE.
- A future Run 3 retry will require Lead Codex to issue an approval envelope bound to the updated driver hash `89ED8BF38C5C2A70289E71C24AB1DC6D09A10E248BE7D8266BEA0BFCE6F703F0`.
