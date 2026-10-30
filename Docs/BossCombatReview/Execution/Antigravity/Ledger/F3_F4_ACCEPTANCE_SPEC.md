# F3/F4 Acceptance Test Specifications & PIE Driver Telemetry (A-257)

> **Document Status**: Certified Offline Specification  
> **Source Plan**: [`WITNESS_PLAN_82.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Ledger/WITNESS_PLAN_82.md)  
> **Target Proof Map**: `L_SevarogFrameworkProof`  
> **Driver Scope**: F3 (Walk / Single MoveCard Playback) and F4 (Central Damage Resolver & Hit Windows)  
> **Audience**: Lead & Implementer (Claude)

---

## 1. Governance & Verification Standards

To guarantee reproducible, non-flaky test runs in CI and PIE automation:
1. **Tagged Grep Lines**: Every test assertion must emit a structured log line matching:
   ```text
   [FrameworkProof] <STATUS> test=<TEST_ID> req=<BOSS-REQ-ID> <KEY=VALUE ...>
   ```
   Where `<STATUS>` is strictly `PASS` or `FAIL`.
2. **Deterministic Invariant Checks**: No fuzzy sleep delays; state transitions must be verified by explicit model events (`Committed`, `ActiveStart`, `ActiveEnd`, `RecoveryEnd`, `Idle`, `Aborted`).
3. **Strict Zero-Tolerance Failures**: The presence of any defined **Failure Token** in the log stream immediately fails the test suite.

---

## 2. F3 Acceptance Test Specifications (Walk / One Card Slice)

F3 proves navigation to an authored band, single MoveCard execution via dynamic montage in `FullBody` slot, timeline tracking, and clean lifecycle shutdown without damage resolution.

| Req ID | Requirement Title | Exact Log Line to Grep | Measurable Numeric Tolerance | Explicit Failure Tokens |
| :--- | :--- | :--- | :--- | :--- |
| **`BOSS-AWR-001`** | Target Validity | `[FrameworkProof] PASS test=TargetValidity req=BOSS-AWR-001 targetState=Invalidated bossState=Idle` | Time to abort $\le 50.0\text{ ms}$ upon player destruction / despawn | `[FrameworkProof] ERROR`, `DanglingTarget`, `MoveToCrash` |
| **`BOSS-SEL-001`** | Legal Decision Gates | `[FrameworkProof] PASS test=LegalGates req=BOSS-SEL-001 state=Neutral eligible=1` | Refusal rate $= 100\%$ if current state $\ne \text{Idle}$ | `MoveModel.DoubleStart`, `IllegalStateTransition` |
| **`BOSS-SEL-008`** | No-Candidate Fallback | `[FrameworkProof] PASS test=Fallback req=BOSS-SEL-008 candidates=0 fallback=StrafeReset` | Boss velocity $\ge 100.0\text{ cm/s}$ (no animation freeze) | `AIController.Stall`, `ZeroCandidatesFrozen` |
| **`BOSS-EXE-001`** | Single Execution Authority | `[FrameworkProof] PASS test=ExecutionAuthority req=BOSS-EXE-001 concurrentRequests=3 granted=1` | Active attack instances $\equiv 1$ strictly | `ConcurrentAttackLeak`, `InstanceCollision` |
| **`BOSS-EXE-002`** | Instance Before Montage | `[FrameworkProof] PASS test=InstanceBeforeMontage req=BOSS-EXE-002 token=Valid instanceId>0 montageDispatched=1` | $t_{\text{token\_reserve}} < t_{\text{montage\_play}}$ (strictly ordered) | `BOSS-EXE-002`, `MontageBeforeInstance` |
| **`BOSS-EXE-003`** | Start Rollback | `[FrameworkProof] PASS test=StartRollback req=BOSS-EXE-003 montagePlayResult=0 bossState=Idle tokenRevoked=1` | State reset time $= 0.0\text{ s}$ (same-frame rollback) | `HangingCommittedState`, `OrphanToken` |
| **`BOSS-EXE-007`** | Watchdog Abort | `[FrameworkProof] PASS test=Watchdog req=BOSS-EXE-007 timeoutElapsed=2.15s bossInactive=1` | $|\Delta t - (t_{\text{rec\_e}} + 0.50\text{ s})| \le 16.67\text{ ms}$ | `WatchdogTimeoutMissed`, `PermanentMotionLock` |
| **`BOSS-COM-007`** | Default Recovery | `[FrameworkProof] PASS test=DefaultRecovery req=BOSS-COM-007 branch=None recoveryCompleted=1` | Recovery duration $= t_{\text{clip}} - t_{\text{act\_e}} \pm 10\text{ ms}$ | `AbruptCutToIdle`, `RecoverySkip` |
| **`BOSS-ANM-001`** | Montage Timeline Authority | `[FrameworkProof] PASS test=TimelineAuthority req=BOSS-ANM-001 playRate=0.5 eventDeltaRatio=2.00` | $|\Delta t_{\text{scaled}} / \Delta t_{\text{base}} - (1.0 / \text{PlayRate})| \le 0.02$ | `WallClockDesync`, `PlayRateIgnored` |
| **`BOSS-ANM-004`** | Staged Rotation Cap | `[FrameworkProof] PASS test=RotationCap req=BOSS-ANM-004 preCommitRate<=90 postCommitRate=0.00` | Post-commit yaw rate $= 0.00^\circ/\text{s}$ ($\pm 0.01^\circ/\text{s}$) | `PostCommitTrackingLeak`, `YawRateExceeded` |
| **`BOSS-ANM-005`** | Exclusive Motion Authority | `[FrameworkProof] PASS test=MotionAuthority req=BOSS-ANM-005 navVelocity=0.00 rootMotionActive=0` | Character translation velocity $= 0.00\text{ cm/s}$ | `NavMeshTranslationDrift`, `PathDriftDuringAttack` |
| **`BOSS-PAC-006`** | Neutral is Purposeful | `[FrameworkProof] PASS test=NeutralPurpose req=BOSS-PAC-006 state=Idle activeWindows=0` | Active collision trace count $\equiv 0$ | `ActiveHitWindowInNeutral`, `LingeringHitbox` |

---

## 3. F4 Acceptance Test Specifications (Damage Windows & Resolver)

F4 integrates multi-sphere swept collision traces, player defense arbitration (blocks, iframes), victim deduplication, and frame-rate invariance.

| Req ID | Requirement Title | Exact Log Line to Grep | Measurable Numeric Tolerance | Explicit Failure Tokens |
| :--- | :--- | :--- | :--- | :--- |
| **`BOSS-EXE-004`** | Stale Event Rejection | `[FrameworkProof] PASS test=StaleEvent req=BOSS-EXE-004 oldGenEventDropped=1 currentAttackIntact=1` | Stale event processing count $\equiv 0$ | `MoveModel.StaleCallback`, `OldGenCorruptedNew` |
| **`BOSS-EXE-008`** | Cleanup-Before-Unlock | `[FrameworkProof] PASS test=CleanupBeforeUnlock req=BOSS-EXE-008 windowsClosed=1 locksReleased=1` | Hitbox deactivation time $\le t_{\text{decision\_unlock}}$ | `HitboxLeakPostRecovery`, `LateUnlock` |
| **`BOSS-COM-002`** | Gate After Damage | `[FrameworkProof] PASS test=GateAfterDamage req=BOSS-COM-002 tEndWindow<=tComboOpen` | $t_{\text{combo\_open}} - t_{\text{win\_end}} \ge 0.000\text{ s}$ | `ComboOpenBeforeDamageEnd`, `PreHitBranch` |
| **`BOSS-COM-004`** | Explicit Hit-Confirm Policy | `[FrameworkProof] PASS test=HitConfirm req=BOSS-COM-004 outcome=Whiff followUp=Recovery` | Hit outcome resolution latency $\le 16.67\text{ ms}$ | `UnresolvedHitOutcome`, `WhiffBranchFailure` |
| **`BOSS-ANM-007`** | Notify-End Independence | `[FrameworkProof] PASS test=NotifyEndIndep req=BOSS-ANM-007 earlyMontageStop=1 windowForceClosed=1` | Window closure latency $\le 0.0\text{ s}$ (same-frame) | `DanglingTraceWindow`, `OrphanNotify` |
| **`BOSS-HIT-002`** | Swept Temporal Sampling | `[FrameworkProof] PASS test=SweptSampling req=BOSS-HIT-002 tunnelCheck=Pass hitRegistered=1` | Sub-step gap distance $\le 5.0\text{ cm}$ | `TunnelingDetected`, `WhiffAtHighSpeed` |
| **`BOSS-HIT-003`** | Blade Interior Samples | `[FrameworkProof] PASS test=BladeInterior req=BOSS-HIT-003 hiltHit=1 midHit=1 tipHit=1` | Interpolated sample density $\ge 3\text{ spheres/meter}$ | `HiltBlindSpot`, `HollowBladeMiss` |
| **`BOSS-HIT-004`** | Adaptive Substeps | `[FrameworkProof] PASS test=AdaptiveSubsteps req=BOSS-HIT-004 simulatedHitch=100ms subSteps=6 hit=1` | Substep count $= \lceil \Delta t / \Delta t_{\text{base}} \rceil$ | `HitchDropMiss`, `MaxSubstepsExceeded` |
| **`BOSS-HIT-005`** | Query Filtering | `[FrameworkProof] PASS test=QueryFiltering req=BOSS-HIT-005 selfCollision=0 corpseCollision=0 playerHit=1` | Self/Corpse hit count $\equiv 0$ | `BossSelfDamage`, `CorpseHitAbsorbed` |
| **`BOSS-HIT-006`** | Logical-Victim Dedupe | `[FrameworkProof] PASS test=VictimDedupe req=BOSS-HIT-006 victimOverlapCount=4 damageInstances=1` | Damage instances per victim per window $\equiv 1$ strictly | `MultiHitSpam`, `DuplicateDamageInstance` |
| **`BOSS-HIT-008`** | Central Defense Order | `[FrameworkProof] PASS test=CentralDefense req=BOSS-HIT-008 playerDefending=1 hpDamage=0 poiseDamage=15` | Player HP delta $= 0.0\text{ HP}$ on clean block | `DamageThroughBlock`, `DefenseBypass` |
| **`BOSS-HIT-009`** | Iframe Completeness | `[FrameworkProof] PASS test=IframeCompleteness req=BOSS-HIT-009 dodgeState=IframeActive hpDamage=0` | Player HP delta $= 0.0\text{ HP}$ across all iframe frames | `IframeBleedThrough`, `FalseHitDuringDodge` |
| **`BOSS-QA-004`** | FPS & Time-Scale Parity | `[FrameworkProof] PASS test=FPSParity req=BOSS-QA-004 rates=[30,60,120] damageDeltas=0.00` | Damage variance between 30, 60, 120 FPS $\equiv 0.00\%$ | `FPSDamageDrift`, `RateDependentHits` |

---

## 4. Master PIE Driver Log Filter & Grep Commands

To evaluate PIE test logs programmatically, run the following PowerShell parser commands:

### 4.1 Check All F3 Assertions Passed
```powershell
# Must return exactly 12 PASS lines and 0 FAIL/ERROR lines
$f3Pass = Select-String -Path "Saved/Logs/OneBossFight.log" -Pattern "\[FrameworkProof\] PASS test=\w+ req=BOSS-(AWR|SEL|EXE|COM|ANM|PAC)-\d+"
if ($f3Pass.Count -lt 12) { Write-Error "F3 suite incomplete: $($f3Pass.Count)/12 passed." }
```

### 4.2 Check All F4 Assertions Passed
```powershell
# Must return exactly 13 PASS lines and 0 FAIL/ERROR lines
$f4Pass = Select-String -Path "Saved/Logs/OneBossFight.log" -Pattern "\[FrameworkProof\] PASS test=\w+ req=BOSS-(EXE|COM|ANM|HIT|QA)-\d+"
if ($f4Pass.Count -lt 13) { Write-Error "F4 suite incomplete: $($f4Pass.Count)/13 passed." }
```

### 4.3 Check Zero Failure Tokens Emitted
```powershell
$badTokens = @(
    "\[FrameworkProof\] ERROR",
    "MoveModel.StaleCallback",
    "MoveCard.Timeline",
    "BOSS-EXE-002",
    "TunnelingDetected",
    "MultiHitSpam",
    "DamageThroughBlock",
    "IframeBleedThrough"
)
$fails = Select-String -Path "Saved/Logs/OneBossFight.log" -Pattern ($badTokens -join "|")
if ($fails) { Write-Error "Critical failure tokens detected in log stream!"; $fails }
```
