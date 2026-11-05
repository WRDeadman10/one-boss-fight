# Player attach guide spot audit — D114

**Scope:** recheck subsystem creation, preexisting and spawned actor routes, and parry binding retry against source. Static source review only; no controller/runtime readiness test.

1. **World scope and callback:** guide says subsystem is limited to game worlds and `PostInitialize` registers `AddOnActorSpawnedHandler`; source confirms both at `RPGPlayerMovesSubsystem.cpp:42-55`.
2. **Actors already present:** guide says `OnWorldBeginPlay` invokes superclass then enumerates existing pawns and calls `Attach`; source confirms this at `:57-66`.
3. **Actors spawned later / teardown:** callback forwards each actor to `Attach` (`:78-81`); deinitialization removes the spawn handler (`:68-75`). The guide's routes and cleanup match.
4. **Recognition and player parry component:** class ancestry matching is exact-name based (`:83-105`); `Attach` registers `URPGPlayerParry` behind a find-or-add guard (`:254-283`). This proves component registration path, not successful controller input binding.
5. **Binding retry:** `BeginPlay` calls `TryBind` once, and component tick retries while `bBound` is false (`RPGPlayerParry.cpp:24-36`). `TryBind` requires an owning pawn with an `UEnhancedInputComponent` and a synchronously loaded `IA_Parry`; it returns false if either is absent and binds `Started` only after both exist (`:49-61`). There is no fixed retry deadline or exact-frame guarantee in this code.

**Acceptance result:** the five sampled route/timing claims remain accurate. The guide correctly says readiness is conditional and gives no runtime-ready guarantee; no correction indicated.
