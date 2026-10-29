# Native Derivation Dossier: RPGBossLook

## 1. Component Overview & File Locations
- **Header:** `Source/OneBossFight/Player/RPGBossLook.h`
- **Source:** `Source/OneBossFight/Player/RPGBossLook.cpp`
- **Class:** `URPGBossLook` (`UActorComponent`)
- **Primary Function:** Implements the boss's visual override (G2-15). Replaces the visual appearance of the boss with Antigravity's body mesh (`SK_Boss01_Body`), modular accessories (`Pieces`: crown, mantle, brazier gauntlet), and weapon (`Sword`: `SM_Boss01_Greatsword` on `SwordSocket`). The original pack skeletal mesh remains the animation leader pose component, collision root, and weapon trace source, but is hidden in game.

---

## 2. Exact Public Authored Fields
Directly extracted from `Source/OneBossFight/Player/RPGBossLook.h`:

```cpp
// Source/OneBossFight/Player/RPGBossLook.h:30
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Look")
bool bEnabled = true;

// Source/OneBossFight/Player/RPGBossLook.h:33
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Look")
TSoftObjectPtr<USkeletalMesh> Body;

// Source/OneBossFight/Player/RPGBossLook.h:37
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Look")
TArray<TSoftObjectPtr<USkeletalMesh>> Pieces;

// Source/OneBossFight/Player/RPGBossLook.h:40
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Look")
TSoftObjectPtr<UStaticMesh> Sword;

// Source/OneBossFight/Player/RPGBossLook.h:44
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Look")
FName SwordSocket = TEXT("HeavySwordSocket_R");
```

*Constructor Soft Path Initializers (`Source/OneBossFight/Player/RPGBossLook.cpp:17-23`):*
```cpp
Body = TSoftObjectPtr<USkeletalMesh>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Body/SK_Boss01_Body.SK_Boss01_Body")));
Pieces = {
    TSoftObjectPtr<USkeletalMesh>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Body/SK_Boss01_Crown.SK_Boss01_Crown"))),
    TSoftObjectPtr<USkeletalMesh>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Body/SK_Boss01_Mantle.SK_Boss01_Mantle"))),
    TSoftObjectPtr<USkeletalMesh>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Body/SK_Boss01_BrazierGauntlet.SK_Boss01_BrazierGauntlet"))),
};
Sword = TSoftObjectPtr<UStaticMesh>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Weapons/SM_Boss01_Greatsword.SM_Boss01_Greatsword")));
```

Total authored fields: **5**.

---

## 3. Code Readings & Extreme Handling (Read From Code)

### `bEnabled` (`bool`, default `true`)
- **Read Locations:**
  - `Source/OneBossFight/Player/RPGBossLook.cpp:29`: `if (bEnabled && GetWorld()) { GetWorld()->GetTimerManager().SetTimerForNextTick(...); }` in `BeginPlay()`.
  - `Source/OneBossFight/Player/RPGBossLook.cpp:60`: `if (bApplied || !bEnabled || !Leader) { return; }` in `Apply()`.
- **Extremes (Read From Code):**
  - `false`: `Apply()` aborts. The replacement body, pieces, and sword are never spawned; the pack's original Kwang mesh and weapon remain visible and active.
  - `true`: Schedules `Apply()` for the next tick after `BeginPlay()`.

### `Body` (`TSoftObjectPtr<USkeletalMesh>`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossLook.cpp:64`: `USkeletalMesh* BodyMesh = Body.LoadSynchronous();` in `Apply()`.
- **Extremes (Read From Code):**
  - Invalid / Empty Path: `LoadSynchronous()` returns `nullptr`. Line 67 logs warning (`the boss body %s did not load: the pack's mesh stays`) and returns immediately. No follower components are created; the pack mesh remains unhidden.

### `Pieces` (`TArray<TSoftObjectPtr<USkeletalMesh>>`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossLook.cpp:107`: `for (const TSoftObjectPtr<USkeletalMesh>& Piece : Pieces)` in `Apply()`.
- **Extremes (Read From Code):**
  - Empty Array: Loop does not execute; `PieceComponents` is empty; `PieceCount = 0`. Body and sword still apply normally.
  - Array containing unresolvable / missing soft path: `Piece.LoadSynchronous()` returns `nullptr`. Line 115 logs warning; that specific piece is skipped, while valid pieces and body still spawn.

### `Sword` (`TSoftObjectPtr<UStaticMesh>`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossLook.cpp:119`: `if (UStaticMesh* SwordMesh = Sword.LoadSynchronous())` in `Apply()`.
- **Extremes (Read From Code):**
  - Invalid / Empty Path: Returns `nullptr`. Line 137 logs warning (`the sword %s did not load: the boss has no sword`); `SwordComponent` is not spawned; boss body and pieces remain attached without a weapon mesh.

### `SwordSocket` (`FName`, default `TEXT("HeavySwordSocket_R")`)
- **Read Locations:**
  - `Source/OneBossFight/Player/RPGBossLook.cpp:127`: `FName AttachName = SwordSocket;` in `Apply()`.
  - `Source/OneBossFight/Player/RPGBossLook.cpp:128`: `if (!BodyComponent->DoesSocketExist(AttachName))` in `Apply()`.
- **Extremes (Read From Code):**
  - `NAME_None` or Socket does not exist on `BodyComponent`: Line 130 logs warning (`the body has no socket %s: the sword goes on the bone hand_r (wrong grip)`). Line 131 sets fallback `AttachName = TEXT("hand_r")`. Does not crash; sword attaches to the right hand bone directly.

---

## 4. External Dependencies
Directly cited from `Source/OneBossFight/Player/RPGBossLook.cpp`:

1. **Owner Character & Leader Mesh:**
   - Lookup: `Source/OneBossFight/Player/RPGBossLook.cpp:58-59`:
     ```cpp
     ACharacter* Character = Cast<ACharacter>(GetOwner());
     USkeletalMeshComponent* Leader = Character ? Character->GetMesh() : nullptr;
     ```
   - Purpose: Source for leader pose component (`SetLeaderPoseComponent(Leader)`). Mesh is configured to `EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones` so it ticks poses while hidden (`:84`).

2. **Pack Static Weapon Components:**
   - Lookup: `Source/OneBossFight/Player/RPGBossLook.cpp:90-99`:
     ```cpp
     TInlineComponentArray<UStaticMeshComponent*> StaticMeshes(GetOwner());
     for (UStaticMeshComponent* Candidate : StaticMeshes) {
         if (Candidate && Candidate->GetAttachParent() == Leader && Candidate->GetName().Contains(TEXT("Weapon"))) {
             HiddenPackWeapons.Add(Candidate);
             ...
         }
     }
     ```
   - Purpose: Hides the pack's default Kwang sword mesh so the character does not render two swords simultaneously.

3. **Timer Manager (Next Tick Schedule):**
   - Call: `Source/OneBossFight/Player/RPGBossLook.cpp:31`: `GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateUObject(this, &URPGBossLook::Apply));`

4. **Authored Soft Paths:**
   - `Body`: `TSoftObjectPtr<USkeletalMesh>`
   - `Pieces`: `TArray<TSoftObjectPtr<USkeletalMesh>>`
   - `Sword`: `TSoftObjectPtr<UStaticMesh>`
   - All provable structurally offline via soft path validation against game asset packages.

---

## 5. Proposed Typed Domain

| Field | Type | Domain / Constraints | Label | Derivation Reason |
|---|---|---|---|---|
| `bEnabled` | `bool` | `{true, false}` | **NATIVE-DERIVED** | Direct toggle in `BeginPlay()` and `Apply()` (`RPGBossLook.cpp:29, 60`). |
| `Body` | `TSoftObjectPtr<USkeletalMesh>` | Valid soft path, non-empty, ends with `.SK_Boss01_Body` or matching object name | **NATIVE-DERIVED** | Synchronously loaded; required for look to apply (`RPGBossLook.cpp:64-68`). |
| `Pieces` | `TArray<TSoftObjectPtr<USkeletalMesh>>` | Array of valid soft paths; empty array allowed; non-empty entries must be valid soft object paths | **NATIVE-DERIVED** | Iterated and synchronously loaded (`RPGBossLook.cpp:107-117`). |
| `Sword` | `TSoftObjectPtr<UStaticMesh>` | Valid soft path, non-empty, ends with `.SM_Boss01_Greatsword` or matching object name | **NATIVE-DERIVED** | Synchronously loaded for sword component (`RPGBossLook.cpp:119`). |
| `SwordSocket` | `FName` | Non-empty `FName`, matches `^[A-Za-z0-9_]+$` | **NATIVE-DERIVED** | Socket verified via `DoesSocketExist()` (`RPGBossLook.cpp:128`). Fallback to `hand_r` on failure. |

*Unresolved Items:*
- Fallback socket name `hand_r` is hardcoded in `.cpp:131`.
- Search substring `TEXT("Weapon")` for pack weapon hiding is hardcoded in `.cpp:93`.

---

## 6. Lifecycle Facts & Configure Guard Rules
- **Component Tick:** `PrimaryComponentTick.bCanEverTick = false;` (`RPGBossLook.cpp:16`). Component does not tick.
- **BeginPlay (`RPGBossLook.cpp:26-33`):**
  - Defers `Apply()` to next tick via `SetTimerForNextTick`.
- **EndPlay (`RPGBossLook.cpp:35-39`):**
  - Calls `Revert()` to destroy spawned components and unhide original meshes.
- **Side Effects on Leader Mesh:**
  - Modifies `Leader->VisibilityBasedAnimTickOption` (`RPGBossLook.cpp:84`).
  - Modifies `Leader->bHiddenInGame` (`RPGBossLook.cpp:86`).
  - Hides attached static meshes containing `Weapon` in their name (`RPGBossLook.cpp:97`).
- **Runtime Components Spawned by Component:**
  - `USkeletalMeshComponent* BodyComponent` (`RPGBossLook.h:84`)
  - `UStaticMeshComponent* SwordComponent` (`RPGBossLook.h:87`)
  - `TArray<USkeletalMeshComponent*> PieceComponents` (`RPGBossLook.h:90`)
- **Configure Guard Constraint:** If re-configured at runtime, `Revert()` MUST be called before modifying paths or toggling `bEnabled`, followed by `Apply()`. Modifying properties while `bApplied == true` without `Revert()` will leak old components or leave the leader mesh hidden.
