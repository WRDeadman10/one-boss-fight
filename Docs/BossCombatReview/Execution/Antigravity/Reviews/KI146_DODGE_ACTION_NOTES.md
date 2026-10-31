# KI-146 Dodge Action Notes

**Task:** C-487 -- offline read-only investigation into the KI-146 dodge i-frame proof mechanism for the new `drive_pie.py` `-DodgeAction` option.
**Status:** OFFLINE ONLY -- no Source/Content edits, no PIE run, no commit.
**Evidence:** All line references cite files read in this session; marks UNKNOWN where not provable offline.

---

## 1. How pie_iframes.py Triggers the Dodge

**File:** `Scripts/Editor/pie_iframes.py`

### Mechanism: `set_key_down` -- NOT `inject_action`

```python
# pie_iframes.py
DODGE = "Gamepad_FaceButton_Right"   # line 12

def key(p, down):                     # line 43
    if S["keys"].get(DODGE, False) != down:
        S["keys"][DODGE] = down
        unreal.RPGInputTestUtils.set_key_down(p["pc"], DODGE, down)
```

> **IMPORTANT:** `pie_iframes.py` uses `set_key_down(pc, "Gamepad_FaceButton_Right", True/False)`.
> This is a raw keycode injection, NOT Enhanced Input Action injection.

### What `drive_pie.py` does (the new `-DodgeAction` option, added for C-488)

**File:** `Docs/BossCombatReview/Execution/Claude/F4/drive_pie.py` (line 151)

```python
unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset(IA_PATH + 'IA_Dodge'), unreal.Vector(1, 0, 0))
```

This injects `IA_Dodge` as an Enhanced Input Action every tick while `pie_t < DODGE_A['hold_until']`
(hold = 0.12 s per press, line 147). The timing for each press is read from
`current_dodge_action.txt` (comma-separated seconds after `playback_start`).

### What `pie_hit_intake.py` does (the proven attack pattern)

**File:** `Scripts/Editor/pie_hit_intake.py` (line ~109)

```python
unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset(IA + c["action"]), unreal.Vector(1, 0, 0))
```

Uses `inject_action` every tick for `IA_NormalAttack`, `IA_StrongAttack`, `IA_ChargedAttack` -- same pattern.
IA path prefix: `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/`

---

## 2. ANS_iFrames Window and Dodge Montage Names

### Montage Names (from `pie_iframes.py` lines 13-14)

```python
QUICK = "Dodge_Small_Forward_Roll_Montage"   # single tap
FULL  = "Dodge_To_Idle_Montage"              # double tap (full roll)
```

### ANS_iFrames Windows (from `pie_iframes.py` lines 15-16)

```python
QUICK_WINDOW = (0.10718, 0.48975)   # montage seconds: start, end
FULL_WINDOW  = (0.0001,  0.69987)   # montage seconds: start, end
```

These are the expected values the test reads from the `ANS_iFrames` notify state embedded in each montage.
They are read at runtime via `RPGIFrameMonitor.ReadWindow()` which walks `Montage->Notifies` and finds
the `ANS_iFrames_C` notify state class.

**Source:** `Source/OneBossFight/Player/RPGIFrameMonitor.h` (line ~51)

```cpp
FName NotifyStateClassName = TEXT("ANS_iFrames_C");   // default, editable UPROPERTY
```

**Source:** `Source/OneBossFight/Player/RPGIFrameMonitor.cpp` -- `ReadWindow()` walks
`Montage->Notifies`, matches `Event.NotifyStateClass->GetClass()->GetFName() == NotifyStateClassName`.

### Double-tap window (from `RPGDodgeTiming.h`)

`DoubleTapWindow = 0.30f` seconds -- second press within 0.30 s gives full roll.
Confirmed in log: `LogRPGDodge: BP_CombatPlayerCharacter_C_0: dodge timing bound to IA_Dodge (double tap window 0.30 s)`

**Source:** `Source/OneBossFight/Player/RPGDodgeTiming.cpp` line 131.

The `IA_Dodge` asset path (from `RPGDodgeTiming.cpp` line 28):
`/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_Dodge`
(confirmed on disk; a local copy at `/Game/OneBossFight/Input/IA_Dodge` also exists -- use the pack path).

---

## 3. Invulnerable Hit Rejection -- Log Tokens

### Log token for an invulnerable hit

**File:** `Source/OneBossFight/Player/RPGDamageResolver.cpp`

```cpp
case ERPGDamageOutcome::RejectedInvulnerable:
    Reason = TEXT("Status.Invulnerable");
    break;
// then falls to:
Record(Payload, Result.Outcome, Reason, Result.HealthBefore, Result.HealthAfter);
```

The `Record()` call emits (UE_LOG format, ~line 78):

```
LogRPGDamage: Log: <BossName>: <MoveId> instance <N> generation <G>: RejectedInvulnerable (Status.Invulnerable) (health <A> -> <B>, asked <C>)
```

**Key tokens to grep in the editor log:**
- `RejectedInvulnerable` -- the outcome name
- `Status.Invulnerable`  -- the reason string
- `LogRPGDamage`         -- the log category

**Where printed:** `RPGDamageResolver.cpp::Record()` -- the `UE_LOG(LogRPGDamage, Log, TEXT("%s: %s instance %d generation %d: %s%s (health %.1f -> %.1f, asked %.1f)"), ...)` call.

### How the resolver checks invulnerability

```cpp
// RPGDamageResolver.cpp, Resolve()
const bool bInvulnerable = bTargetAlive && bAttackerAlive && bCurrent && !bDuplicate
    && RPGBossDamage::IsInvulnerable(Target);
```

`RPGBossDamage::IsInvulnerable(Target)` reads the `Status.Invulnerable` Gameplay Tag from the player
actor (set/cleared by the `ANS_iFrames` notify state during a dodge montage).

Additionally, `pie_a4_low_sweep.py` reads the counter:
```python
sw.get_invulnerable_count()  # RPGBossLowSweep component; 1 = blade hit was invulnerable
```

---

## 4. Crash in Claude/F4/dodge_run1 -- Root Cause

**File:** `Docs/BossCombatReview/Execution/Claude/F4/dodge_run1/editor_raw.log`

### Sequence of events

1. **BP_AdvancedPlayerController compile errors at load** (frame 0):
   ```
   LogBlueprint: Error: [AssetLog] BP_AdvancedPlayerController.uasset:
     [Compiler] Invalid pin connection ... This cast has an invalid target type
     (was the class deleted without a redirect?)
   ```
   Also: `DeactivateWidget`, `ActivateWidget`, `IsActivated` functions not found.
   `UCommonActivatableWidget` (CommonUI plugin) was deleted/removed; the BP's redirect is stale.
   `BP_AdvancedPlayerController` fails to compile -- its CDO is null/corrupt.

2. **Dodge bound successfully** -- `RPGDodgeTiming` component binds on the pawn (not PlayerController):
   ```
   LogRPGDodge: BP_CombatPlayerCharacter_C_0: dodge timing bound to IA_Dodge (double tap window 0.30 s)
   ```

3. **Drive script pressed the key** (`set_key_down` via the old F3D driver, not inject_action):
   ```
   [F3D] dodge key down since_playback_start=0.159
   [F3D] dodge key up since_playback_start=0.240
   ```

4. **Handled ensure `ClassDefaultObject != nullptr`** (Class.cpp line 5849) ~1 s after the key press:
   - Callstack: `UnrealEditor-UMG.dll` -> `UnrealEditor-CoreUObject.dll` x many frames
   - The key press activated the dodge ability, which attempted to call `ActivateWidget`/`DeactivateWidget`
     on a `CommonActivatableWidget` managed by `BP_AdvancedPlayerController` -- whose CDO is corrupt.
   - `ClassDefaultObject == nullptr` ensure fires.

5. **Access violation** `EXCEPTION_ACCESS_VIOLATION reading address 0x0000000000000008` ~8 s later:
   The ensure left a partially invalid state; a subsequent CDO walk deref'd null+8 (first member offset).
   Callstack: `UnrealEditor-CoreUObject.dll` x many frames -> `UnrealEditor-UnrealEd.dll` -> `UnrealEditor.exe`.

### Root cause (VERIFIED from log)

> `BP_AdvancedPlayerController` failed to compile because CommonUI's `UCommonActivatableWidget`
> was deleted or has a missing redirect. The dodge key press (via `set_key_down`) routed through
> the raw key path, which woke the UI widget stack managed by the broken BP. The
> `ClassDefaultObject != nullptr` ensure fired; the resulting corrupt state caused an access violation.

### Pack function in callstack

**UNKNOWN** -- all callstack frames show `UnknownFunction` (no PDB symbols). The `UnrealEditor-UMG.dll`
frame indicates a UMG/widget call, consistent with `ActivateWidget`/`DeactivateWidget` in the BP.

### Why `inject_action` is safer

- `inject_action(pc, IA_Dodge, ...)` submits an `FInputActionValue` directly via the Enhanced Input
  subsystem through the Input Mapping Context -- does NOT route through the PlayerController BP widget stack.
- `set_key_down` routes through the PlayerController's key dispatch, which can wake UI widgets managed
  by the broken `BP_AdvancedPlayerController`.
- The existing `pie_iframes.py` uses `set_key_down` and **would also crash** in the same environment.
  The new `-DodgeAction` approach in `drive_pie.py` is the correct path.

---

## 5. Summary Table

| Question | Answer | Source |
|---|---|---|
| pie_iframes.py trigger method | `set_key_down(pc, 'Gamepad_FaceButton_Right', ...)` | pie_iframes.py L43 |
| drive_pie.py new method | `inject_action(pc, IA_Dodge, Vector(1,0,0))` 0.12 s hold | drive_pie.py L151 |
| Quick dash montage | `Dodge_Small_Forward_Roll_Montage` | pie_iframes.py L13 |
| Full roll montage | `Dodge_To_Idle_Montage` | pie_iframes.py L14 |
| Quick ANS_iFrames window | 0.10718 -- 0.48975 montage-s | pie_iframes.py L15 |
| Full ANS_iFrames window | 0.0001 -- 0.69987 montage-s | pie_iframes.py L16 |
| Notify state class name | `ANS_iFrames_C` | RPGIFrameMonitor.h L51 |
| Invulnerable rejection log token | `RejectedInvulnerable (Status.Invulnerable)` on `LogRPGDamage` | RPGDamageResolver.cpp Record() |
| Resolver log format | `<Boss>: <MoveId> instance N gen G: RejectedInvulnerable (Status.Invulnerable) (health A -> B, asked C)` | RPGDamageResolver.cpp ~L78 |
| Low sweep invulnerable counter | `RPGBossLowSweep::get_invulnerable_count()` | pie_a4_low_sweep.py counters() |
| Crash root cause | BP_AdvancedPlayerController CDO null (CommonUI missing); set_key_down woke broken widget stack | dodge_run1/editor_raw.log |
| Crash pack function in callstack | UNKNOWN (no PDB symbols; UMG frame consistent with ActivateWidget call) | dodge_run1/editor_raw.log |
