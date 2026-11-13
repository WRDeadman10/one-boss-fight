# BQ-91..95: Queue BQ batch 19, decision packages: legacy retirement, default player, camera

C (implementer), 2026-11-13. Queue: `QUEUE_BQ.md`.

**Documents only.** No source, config, asset or engine change. Each package states what is already decided, what is left, and the exact steps once the gate opens.

## BQ-91 (A19): legacy retirement package

**Already decided and done:**
- OWNER 2026-11-05: A7 = B, retire legacy later, after the release gates.
- OWNER 2026-11-06: "Yes, retire legacy". The **default startup is the data route** (BUILD-236; TASKS:1412-1413). Legacy remains reachable via non-Shipping parity opt-in (`-RPGLegacyStartup` or `RPG_LEGACY_STARTUP=1`, `RPGPlayerMovesSubsystem.cpp:1164`) and is also the automatic fallback if the default encounter definition fails to load (`:1173`).

**Left: removing the legacy path itself.** A7's release gates still apply:
1. packaged Shipping proof, including the setter route;
2. selected-route performance on the RTX 2060 Super (O6; performance parked);
3. content and cook closure (KI-080's missing `T_Water_N_2`, BQ-79).

**Removal steps, once all three close (Lead scope, then ENG):**
- (a) Keep the opt-in for one release as the rollback path, logged as deprecated.
- (b) Then delete the opt-in branch and the legacy-only startup code, guarded by the A5 parity matrix: 31/31 pairs must still pass on the data route alone before deletion.
- (c) Retire the legacy-only drivers and the parity comparator, and record it in DECISIONS.

**Risk:** the A5 parity evidence is the safety net. Once legacy is deleted it can no longer be re-run, so archive the last parity receipts first.

## BQ-92/93 (B10): default-player switch package, **O4, open**

**Mechanism today:**
- The project's GameMode is the pack's `BP_AdvancedGameMode` (`DefaultEngine.ini:6`), which spawns the mannequin.
- Greystone is reachable only through the Development switch `rpg.GreystonePlayerTestPawn`, which replaces the first spawned pack player with `BP_GreystoneERPlayer` (`RPGPlayerMovesSubsystem.cpp:111, 386, 435`; not in Shipping).
- A Shipping default switch therefore needs a **new production path**, either:
  - (i) a project GameMode override with Greystone as its pawn class, or
  - (ii) a non-Development config flag on the existing replacement. **Lead design choice.**

**Readiness, from this queue's own evidence. All must pass before asking the owner:**

| Gate | State | Source |
|---|---|---|
| Root-motion roll (RM4 quick roll 248-334 cm) | **OPEN.** `_RM` writer and repoint ready, Editor run is ENG | BQ-46..50 |
| Backstep root motion | PASS (99.35 cm, +2.75%) | C-1289 |
| Layer ABPs load (KI-040) and no GetMainAnimBP flood (KI-052) | **OPEN.** Guarded repair ready, ENG | BQ-56 |
| Hits and parry on the Greystone pawn | **OPEN.** Drivers wired and target-tagged; PIE pair is ENG | BQ-52/53 (X-2363) |
| Saved wrapper notifies | **OPEN.** Readback ready, ENG | BQ-51 |
| Weapon sockets (KI-035) | **OPEN.** Inventory ready, visual check is OWN | BQ-58 |
| Visual review (F4b-7) | **OPEN.** OWN | BQ-54 |

**Owner question when the gates pass:** "Make Greystone the default player in packaged builds? Yes/No (default: No)". The mannequin stays as the rollback, and Ember is kept, per the character switch plan.

## BQ-94 (C8): camera choice reconciliation, **O5 resolved**

DECISIONS 2026-11-09 (C-1168): the owner chose **option C only** (lock-on framing). Option B (hide the boss when the camera is inside) stays off; option A was dropped as measured worse (C-1081). It is **live**: `Config/DefaultGame.ini:24` sets `bDefaultLockOnFraming=True`. Nothing to package. **The stale O5 pending gate is removed from QUEUE_BQ.**

## BQ-95: this report

**Open gates after this batch:**
- O1 (Batch 17);
- O2 (SFX picks);
- O4 (default player, after the ENG gates above);
- O6 and O7;
- the A7 release gates for removing legacy.

**Stale:** O3 (removed) and O5 (proposed for removal).

## Lead review correction

Legacy is still the non-Shipping opt-in parity route, but code also retains it as the automatic fallback when the default data definition fails to load. The initial draft's “only by opt-in” wording was too narrow. O5 is resolved by C-1168 and live in `Config/DefaultGame.ini`; the stale queue gate is removed. Independent review A-982 accepted this package at documentation/planning level.
