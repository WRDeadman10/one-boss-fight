# Domain Proposal Sheet: URPGBossLook (v2)

## 1. Component Overview & Source Locations
- **Header:** `Source/OneBossFight/Player/RPGBossLook.h:22` (`class ONEBOSSFIGHT_API URPGBossLook : public UActorComponent`)
- **Implementation:** `Source/OneBossFight/Player/RPGBossLook.cpp`
- **Class Group:** `ClassGroup = (Boss)` (`RPGBossLook.h:21`)
- **Primary Function:** Implements the boss's visual override (G2-15). Replaces the rendered appearance of the boss with Antigravity's body mesh (`SK_Boss01_Body`), modular accessories (`Pieces`: crown, mantle, brazier gauntlet), and weapon (`Sword`: `SM_Boss01_Greatsword` on `SwordSocket`). The original pack skeletal mesh (`Leader`) remains active, hidden in game, and continues driving animations, montages, hitboxes, collision, weapon trace sockets, and physics (`RPGBossLook.h:16-19`, `RPGBossLook.cpp:84-86`).

---

## 2. Real Authored Header Declarations (5 Authored Fields)
Directly extracted from `Source/OneBossFight/Player/RPGBossLook.h`:

```cpp
// Source/OneBossFight/Player/RPGBossLook.h:29-30
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Look")
bool bEnabled = true;

// Source/OneBossFight/Player/RPGBossLook.h:32-33
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Look")
TSoftObjectPtr<USkeletalMesh> Body;

// Source/OneBossFight/Player/RPGBossLook.h:35-37
/** Crown, mantle and gauntlet: skeletal pieces on the same skeleton that follow the pack mesh's pose. */
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Look")
TArray<TSoftObjectPtr<USkeletalMesh>> Pieces;

// Source/OneBossFight/Player/RPGBossLook.h:39-40
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Look")
TSoftObjectPtr<UStaticMesh> Sword;

// Source/OneBossFight/Player/RPGBossLook.h:42-44
/** The socket of the body mesh the sword is attached to (HeavySwordSocket_R on hand_r: relative location (-13.9, 2.6, 4.9), rotation pitch -28, yaw 168.8, roll 12.8). */
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Look")
FName SwordSocket = TEXT("HeavySwordSocket_R");
```

### Editor Metadata Note:
- `ClampMin` and `ClampMax` are editor metadata specifiers that apply strictly to numeric properties (floats, integers).
- None of the 5 authored properties of `URPGBossLook` declare `meta = (ClampMin = ...)` in `Source/OneBossFight/Player/RPGBossLook.h`.
- Any reference to `ClampMin` for this component is an erratum.

---

## 3. Native Implementation & Execution Semantics (`RPGBossLook.cpp`)

### 3.1 Lifecycle & Loading Architecture
- **No Tick:** `PrimaryComponentTick.bCanEverTick = false;` (`RPGBossLook.cpp:16`).
- **Deferred Execution in `BeginPlay`:**
  - `Super::BeginPlay();` (`RPGBossLook.cpp:28`).
  - If `bEnabled && GetWorld()`, schedules `Apply()` for the next tick via `GetWorld()->GetTimerManager().SetTimerForNextTick(...)` (`RPGBossLook.cpp:29-32`).
- **Game-Thread Synchronous Asset Loading in `Apply()`:**
  - `Body.LoadSynchronous()` (`RPGBossLook.cpp:64`).
  - Loop over pieces: `Piece.LoadSynchronous()` for each element (`RPGBossLook.cpp:109`).
  - `Sword.LoadSynchronous()` (`RPGBossLook.cpp:119`).
- **Teardown in `EndPlay`:**
  - Calls `Revert()` (`RPGBossLook.cpp:37`), which destroys `SwordComponent` (`:150-154`), destroys all `PieceComponents` (`:155-162`), destroys `BodyComponent` (`:164-168`), unhides pack weapons (`:169-177`), and restores leader mesh visibility and tick option (`:178-185`).

### 3.2 Failure Modes & Warning Logging (Failures are NOT Silent)
Soft asset loading failures in `RPGBossLook.cpp` are explicitly logged with `UE_LOG(LogRPGBossLook, Warning, ...)`:
1. **`Body` Failure:**
   - If `BodyMesh == nullptr` (`RPGBossLook.cpp:65`):
     - Logs Warning: `UE_LOG(LogRPGBossLook, Warning, TEXT("%s: the boss body %s did not load: the pack's mesh stays"), *GetOwner()->GetName(), *Body.ToString());` (`RPGBossLook.cpp:67`).
     - Returns immediately (`:68`).
     - **Native Outcome:** The entire look application aborts. The original pack mesh is NOT hidden, no followers are created, and no sword is attached.
2. **`Pieces` Failure:**
   - If `Pieces` array is empty: The loop (`:107`) executes zero times, `PieceCount` is set to 0 (`:118`). Safe and valid natively.
   - If an individual piece fails to load (`Piece.LoadSynchronous() == nullptr`):
     - Logs Warning: `UE_LOG(LogRPGBossLook, Warning, TEXT("%s: the piece %s did not load and is missing from the look"), *GetOwner()->GetName(), *Piece.ToString());` (`RPGBossLook.cpp:115`).
     - Continues to next piece.
     - **Native Outcome:** The failing piece is omitted; valid pieces, the body, and the sword still spawn and attach.
3. **`Sword` Failure:**
   - If `SwordMesh == nullptr`:
     - Logs Warning: `UE_LOG(LogRPGBossLook, Warning, TEXT("%s: the sword %s did not load: the boss has no sword"), *GetOwner()->GetName(), *Sword.ToString());` (`RPGBossLook.cpp:137`).
     - **Native Outcome:** `SwordComponent` remains `nullptr`. The boss spawns without a replacement sword mesh, while the body and pieces remain attached and visible.
4. **`SwordSocket` Missing / Fallback:**
   - Checked via `BodyComponent->DoesSocketExist(AttachName)` (`RPGBossLook.cpp:128`).
   - If missing:
     - Logs Warning: `UE_LOG(LogRPGBossLook, Warning, TEXT("%s: the body has no socket %s: the sword goes on the bone hand_r (wrong grip)"), *GetOwner()->GetName(), *SwordSocket.ToString());` (`RPGBossLook.cpp:130`).
     - Falls back to bone: `AttachName = TEXT("hand_r");` (`RPGBossLook.cpp:131`).
     - **Native Outcome:** Sword attaches directly to bone `hand_r` instead of failing or attaching to root origin.

---

## 4. Unresolved Items & Technical Constraints
The following items are hardcoded or unmanaged in the native source code and represent known architectural boundaries:
1. **Game-Thread Synchronous Loading:**
   - `Body.LoadSynchronous()` (`:64`), `Piece.LoadSynchronous()` (`:109`), and `Sword.LoadSynchronous()` (`:119`) block the Game Thread synchronously during `Apply()`.
2. **Hardcoded Fallback Bone:**
   - Socket failure falls back to string literal `TEXT("hand_r")` (`RPGBossLook.cpp:131`).
3. **Hardcoded Component Instance Names:**
   - Follower body component instance is hardcoded as `TEXT("RPGLookBody")` (`RPGBossLook.cpp:105`).
   - Follower piece components are hardcoded as `TEXT("RPGLookPiece_<MeshName>")` (`RPGBossLook.cpp:111`).
   - Follower sword component is hardcoded as `TEXT("RPGLookSword")` (`RPGBossLook.cpp:121`).
4. **Hardcoded Pack Weapon Filter Substring:**
   - Detection of the pack's default sword relies on child static meshes matching `Candidate->GetName().Contains(TEXT("Weapon"))` (`RPGBossLook.cpp:93`). If not found, logs Warning at `:102`.
5. **Hardcoded Constructor Paths:**
   - Constructor defaults (`RPGBossLook.cpp:17-23`) hardcode asset package paths under `/Game/OneBossFight/Boss01/...`.

---

## 5. Domain Derivation & Validation Rules

| Field Name | C++ Type | Domain / Constraints | Derivation Label | Rationale & Native Enforcement |
| :--- | :--- | :--- | :--- | :--- |
| `bEnabled` | `bool` | `{true, false}` | **NATIVE-DERIVED** | Directly queried in `BeginPlay()` (`:29`) and `Apply()` (`:60`). Controls whether look application schedules and runs. |
| `Body` | `TSoftObjectPtr<USkeletalMesh>` | Non-empty soft object path; syntactically valid package and object path format; no whitespace/control characters. | **AUTHORED CHOICE / DD PROTOCOL** | Synchronously loaded (`:64`). Empty or invalid path causes `LoadSynchronous()` failure, logs Warning (`:67`), and aborts look. No invented regex or file suffix constraints. |
| `Pieces` | `TArray<TSoftObjectPtr<USkeletalMesh>>` | Empty array permitted (native-derived). Non-empty elements must each be non-empty, syntactically valid soft object paths; no duplicate paths within array. | **NATIVE-DERIVED** (empty array allowed) /<br>**AUTHORED CHOICE** (syntactic validity) | Empty array executes zero loop iterations and safely sets `PieceCount = 0` (`:118`). Failing elements log Warning (`:115`) and are skipped. No invented regex or fixed count constraints. |
| `Sword` | `TSoftObjectPtr<UStaticMesh>` | Non-empty soft object path; syntactically valid package and object path format; no whitespace/control characters. | **AUTHORED CHOICE / DD PROTOCOL** | Synchronously loaded (`:119`). Failure logs Warning (`:137`) and leaves `SwordComponent` null. No invented regex constraints. |
| `SwordSocket` | `FName` | Non-None `FName`; valid identifier syntax; no whitespace or control characters; max length 1024. | **AUTHORED CHOICE / DD PROTOCOL** | Checked via `DoesSocketExist()` (`:128`). Missing socket logs Warning (`:130`) and falls back natively to bone `hand_r` (`:131`). Standard identifier syntax; no invented regex. |

---

## 6. Proposed Validation Order & Diagnostic Tokens (DD19–DD22 Style)

### 6.1 Validation Order
1. **`bEnabled`**:
   - Standard boolean evaluation (always valid).
2. **`Body`**:
   - Checked for non-empty string.
   - Checked for valid long package name and valid object name syntax (using UE `FPackageName` / `FName` character validation rules without disk access).
3. **`Pieces`**:
   - Evaluated as an array. Empty array passes immediately.
   - Each entry evaluated: must be non-empty string, valid path syntax, and unique within the array.
4. **`Sword`**:
   - Checked for non-empty string.
   - Checked for valid long package name and valid object name syntax.
5. **`SwordSocket`**:
   - Checked for `!SocketName.IsNone()`.
   - Checked for illegal whitespace, control characters, and string length boundaries.

### 6.2 Proposed Diagnostic Tokens
In alignment with DD19 (`Bleed`), DD20 (`LowSweep`), DD21 (`Shockwave`), and DD22 (`HealPunish`), the following tokens are proposed:
- `Look.Body.Empty`: if `Body` path is empty.
- `Look.Body.Malformed`: if `Body` path contains invalid package/object syntax or illegal characters.
- `Look.Pieces.Malformed`: if any entry in `Pieces` is empty, duplicate, or contains invalid path syntax.
- `Look.Sword.Empty`: if `Sword` path is empty.
- `Look.Sword.Malformed`: if `Sword` path contains invalid package/object syntax or illegal characters.
- `Look.SwordSocket.None`: if `SwordSocket` is `NAME_None`.
- `Look.SwordSocket.Malformed`: if `SwordSocket` contains whitespace, control characters, or exceeds max identifier length.

### 6.3 Offline Validation Scope
- All validations are strictly syntactic (using character-level NameTypes macros and package rules).
- Zero asset loading (`LoadSynchronous` is NOT invoked during authoring validation).
- Zero disk IO or registry checks.
