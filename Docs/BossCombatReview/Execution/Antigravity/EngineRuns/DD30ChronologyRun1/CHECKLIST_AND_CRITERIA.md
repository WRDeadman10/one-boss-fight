# DD30 Chronology PIE Run Success Criteria & Verification Checklist

**Task Order:** C-352 (Order A-234, Prepared Offline - NOT YET RELEASED)  
**Execution Packet:** `Docs/BossCombatReview/Execution/Antigravity/EngineRuns/DD30ChronologyRun1/`  
**Driver:** `dd30_chronology_pie.py` (Adapted from Codex `24b7a39e...` with bounded `QUIT_EDITOR` shutdown)  
**Launch Command:**
```powershell
& 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe' 'C:\UnrealProject\OneBossFight\OneBossFight.uproject' '/Game/OneBossFight/Levels/L_SevarogArena' -nosound -nosplash -unattended -nullrhi -DD30Chronology "-ExecutePythonScript=C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\EngineRuns\DD30ChronologyRun1\dd30_chronology_pie.py" "-abslog=C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\EngineRuns\DD30ChronologyRun1\chronology_raw.log"
```

---

## 1. Important Technical Limitation: `-nullrhi` Mode
- **Status:** Headless execution (`-nullrhi`) is **UNMEASURED** in this project's PIE environment.
- **Incomplete / Non-Pass Conditions:**
  * If the driver logs `FAIL wrong editor map; no map load/save performed`, the run is **INCOMPLETE**, not a pass.
  * If the driver fails to observe `PIE_WORLD` within the 10-second window, the run is **INCOMPLETE**, not a pass.
  * If the wrapper triggers a `TIMEOUT_KILL` (editor process killed after 180s hard timeout), the run is **FAILED / INCOMPLETE**.

---

## 2. Success Criteria & Required Raw Lines (Copied from `PROPOSAL_AND_RUN_PLAN.md` §3)

### Required Driver Lines:
- [ ] `[DD30_CHRONO_DRIVER] REQUEST freshPIE map=L_SevarogArena no gameplay input`
- [ ] `[DD30_CHRONO_DRIVER] PIE_WORLD /Game/OneBossFight/Levels/...`
- [ ] `[DD30_CHRONO_DRIVER] CAPTURE_END started=True; native chronology must be reviewed, not an automatic PASS`
- [ ] `[DD30_CHRONO_DRIVER] REQUEST QUIT_EDITOR (slate ticks=...)`

### Required Native Chronology Lines (`[DD30_CHRONO]`):
- [ ] Entry into `URPGPlayerMovesSubsystem::OnWorldBeginPlay`:
  `[DD30_CHRONO] callback=PlayerMoves.OnWorldBeginPlay`
- [ ] Pawn Census (at early callback):
  * Pawn count, plus one actor line per pawn with role/class/path/world + actor begun/beginning flags.
  * Separate boss and player counts.
- [ ] Inputs & State at Callback:
  * Catalog publication (`GetEpoch`).
  * Placed `ARPGEncounterBinding` slot/target/actor/definition enumeration.
  * Context bound/ready counts.
  * `selection_store=NOT_DEFINED` (honestly acknowledging absence of persisted subsystem selection store).
- [ ] First-Observed Component-Route Lines:
  * `URPGBossEncounter::BeginPlay` (Boss pawn).
  * `URPGDodgeTiming::BeginPlay` (Player pawn).
  * Records `IsActorBeginningPlay` flag for each actor.
  * Sequence numbers + monotonic seconds establishing chronological ordering.

### Criteria Notes:
- Missing native logger lines, wrong map, or no boss/player route within window => **INCOMPLETE** chronology for that actor, not a pass.
- A zero player/binding/epoch count at early callback is a **valid finding**, not a reason to spawn, default, or suppress failure.
- If first-component probe was late, exact actor-start timing remains **UNKNOWN**.
- All Error/Warning lines must be retained verbatim in run report.

---

## 3. Pre-Run Safety Invariants Checklist:
- [ ] Zero `UnrealEditor`, `UnrealBuildTool`, `UBT`, `cl`, `link` processes running before launch.
- [ ] `ENGINE_LOCK.json` acquired exclusively before launch, removed after evidence freeze.
- [ ] Git HEAD verified: `605c2dd81d4092e8f84aa7608651ed19d566423a`.
- [ ] Source files: exactly 219 files matching `promoted_source_manifest_sha256.txt`.
- [ ] DLL binary verified: `UnrealEditor-OneBossFight.dll` hash is `332afd497b68c01b556be9fd73682574e97c31ed868f46a382ee0cb301bdaacf`.
- [ ] Saved draft assets (`DA_Boss_AbyssalRevenant_Draft`, `DA_Boss_EmberWarden_Draft`, `DA_Player_Hero_Draft`) bit-identical.
- [ ] Execution monitored with hard 180s process-specific timeout killing ONLY the launched editor PID if exceeded.
