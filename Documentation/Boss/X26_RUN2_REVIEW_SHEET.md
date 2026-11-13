# X26 Run-2 One-Pass Review Sheet (`P_C1292_X26` Baseline vs Run-2 Acceptance)

**Authority:** [`C-1294`] (`2026-11-11 07:32`), [`C1278_X26_LIVE_CHECK_ACCEPTANCE_TABLE.md`](C1278_X26_LIVE_CHECK_ACCEPTANCE_TABLE.md), [`test_c1278_x26_acceptance_contract.py`](../../Scripts/Tools/test_c1278_x26_acceptance_contract.py)  
**Verifier:** [`Scripts/Tools/verify_c1278_x26_live_log.py`](../../Scripts/Tools/verify_c1278_x26_live_log.py)  
**Applied Pre-Run-2 Fixes (Pending Codex Locked Build + Self-Test):**
1. **`X-1945` (`[A-827]`):** Standalone test actors run the shared neutral phase gate (`!bArrived` vs autonomous selection guard), preserve `TestBossHealthFraction` across card/combo start until restart, and trace candidates/refusals in `StartSelectedCardForTest`.
2. **`X-1949` (`[A-828]` / `KI-150`):** `Scripts/Editor/pie_sevarog_framework_live.py` polls `BP_CombatComponent_C.CurrentCombatStyle` (`PACK_STYLE_READY`, 30 s bounded timeout) before spawning/initializing the standalone framework boss.
3. **`X-1943`:** `verify_c1278_x26_live_log.py` accepts both bare and scoped `ERPGDamageOutcome::*` strings (`2/7` -> clean parsing).

---

## 1. Five-Arm Expectations (`Run 1 Baseline` -> `Run 2 Target`)

| Arm | Exercise Scope | Run 1 (`P_C1292_X26_*`) Result | Verifier Flags | Run 2 Expected `PASS` Rows (`[C-1294]`) | Run 2 Hard-Fail / Hold Checks |
|---|---|---|---|---|---|
| **Arm A** | S1–S3 standalone, S4->S5 combo, S7 stationary (`Subjugation`) | `finished=True`; S1/S2/S3/S5 hit, S7 released (`0.815 s`), then aborted `actual=100 expected=800` (`0/7 PASS`) | `--s7-case stationary --s8-case inside` | **`X26-S7a`**, **`X26-S7b`** | `PACK_STYLE_READY` logged before spawn; `TargetLifeOrHealthChanged` absent; `inside=1`, `outcome=Accepted hpApplied=35`, snare `scale=0.55 seconds=2.5` -> `restored=1`; standalone S1–S5 cleanly completed. |
| **Arm B** | Half-HP (`0.5`) Phase-2 cards: S6 (`Ultimate_Swing_120fps`) + S8 (`Soul_Siphon`) inside cone | `finished=False` (7m timeout); health hook reset `0.5 -> 250/250`, stayed in `Phase_1`, timed out requesting S6 (`0/7 PASS`) | `--s7-case stationary --s8-case inside` | **`X26-S6`**, **`X26-S8a`**, **`X26-S8b`** | `PACK_STYLE_READY` present; `test_boss_health_fraction=0.5` survives into `Phase_2`; S6 `actualDistanceCm` in `110..130 cm`, single `HitGroup_ScytheBlade` hit `hpApplied=65` (no double hit); S8 `trackFacing=0`, exactly 5 ticks at `0.467, 0.667, 0.867, 1.067, 1.267`, `hpApplied=8`, `0 < bossHealed <= 4.05`, sum `<= 20.05`. |
| **Arm C** | S7 `dodge-out` (`Subjugation`, `500 cm` roll after `release + 0.3 s`) | `finished=True`, **`2/7 PASS`** (`X26-S7a`, `X26-S7-dodge-out`; `release=0.819`, `resolve=1.5796`, `distanceCm=594.6 inside=0`) | `--s7-case dodge-out --s8-case inside` | **`X26-S7a`**, **`X26-S7-dodge-out`** | Confirm Run-1 `2/7` parity holds after `PACK_STYLE_READY` ordering (`center` within `<= 10 cm` of `playerGround` at release, `inside=0`, 0 `area_effect_damage`, 0 `area_effect_snare`). |
| **Arm D** | `Phase_1` autonomous selection (`> 60%` HP) | `finished=True`; chose `Swing3_Slow` (`55` dmg), no phase gate trace, aborted `actual=100 expected=745` (`0/7 PASS`) | `--s7-case stationary --s8-case inside` | **`X26-P1`** | `PACK_STYLE_READY` present; `TargetLifeOrHealthChanged` absent; `refusal ... reason=MoveModel.Phase` emitted for BOTH `S6` and `S8`; 0 `candidate` or `CARD accepted` lines for `S6`/`S8` prior to `Phase_2`. |
| **Arm E** | `Phase_2` unlock (`0.5` HP) + autonomous selection | `finished=True`; card-start reset `0.5` -> max HP, no `phase_transition`, picked `Swing3_Slow` in `Phase_1`, aborted `actual=100 expected=745` (`0/7 PASS`) | `--s7-case stationary --s8-case inside` | **`X26-P2`** (plus **`X26-P1`** if pre-transition `Phase_1` traces are in log, or `X26-P2` if starts at `0.5` HP) | `PACK_STYLE_READY` present; `TargetLifeOrHealthChanged` absent; `test_boss_health_fraction=0.5` latches exactly 1 `phase_transition ... from=Phase_1 to=Phase_2` (`PhaseTwoFraction=0.6`); post-transition `candidate` traces contain `S6`, `S8`, and `>= 3` unique candidates (`StartSelectedCardForTest` traces active). |

*(Note on `X26-S8-cone-escape`: not listed in `[C-1294]` five-arm set; flag explicitly if an additional `cone-escape` arm is run, otherwise record `S8-cone-escape` coverage status separately.)*

---

## 2. One-Pass Diff Commands (Read-Only When Run-2 Logs Land)

Run read-only against the Run-2 arm folders without editing Lead receipts:

```powershell
Set-Location "C:\UnrealProject\OneBossFight"
$runRoot = "Docs\BossCombatReview\Execution\Claude\<RUN2_PREFIX>"
foreach ($spec in @(
    @{ Arm = "A"; S7 = "stationary"; S8 = "inside" },
    @{ Arm = "B"; S7 = "stationary"; S8 = "inside" },
    @{ Arm = "C"; S7 = "dodge-out";  S8 = "inside" },
    @{ Arm = "D"; S7 = "stationary"; S8 = "inside" },
    @{ Arm = "E"; S7 = "stationary"; S8 = "inside" }
)) {
    $dir = "${runRoot}_$($spec.Arm)"
    Write-Output "=== Arm $($spec.Arm) ==="
    Get-Content "$dir\status.txt" -TotalCount 5
    Select-String -Path "$dir\data.log" -Pattern "PACK_STYLE_READY|TargetLifeOrHealthChanged|phase_transition|candidate|refusal|test_boss_health_fraction" | ForEach-Object { $_.Line }
    python "Scripts\Tools\verify_c1278_x26_live_log.py" "$dir\data.log" --s7-case $spec.S7 --s8-case $spec.S8
}
```

---

## 3. Sign-Off Diff Checklist

1. **Five-arm matrix aggregate:** Union across Arms `A..E` achieves **`PASS`** on all 7 `[C-1294]` target checks: `X26-P1` (`D`), `X26-P2` (`E`), `X26-S6` (`B`), `X26-S7a` (`A`, `C`), `X26-S7b` (`A`), `X26-S7-dodge-out` (`C`), `X26-S8a` (`B`), `X26-S8b` (`B`). *(If `StartSelectedCardForTest` does not emit `Phase_1` refusals when spawned already at `0.5` HP in Arm E, Arm D alone supplies `X26-P1` and Arm E supplies `X26-P2`.)*
2. **No `KI-150` recurrence:** `0` occurrences of `TargetLifeOrHealthChanged` / `target_health_mismatch` across all 5 arms; `PACK_STYLE_READY` appears before boss spawn/init in all 5 arms.
3. **Standalone S1–S5 regression:** Verify Arm A still completes `S1`, `S2`, `S3`, and `S4->S5` combo cleanly alongside `S7`.
4. **Post-run follow-up check:** Update `KNOWN_ISSUES.md` `KI-150` status line and sync `COMMIT_PLAN_C1286.md` holdouts/accepted files once `[C-1294]` Lead acceptance posts.
