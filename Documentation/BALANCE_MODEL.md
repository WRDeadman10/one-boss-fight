# Balance model

`Scripts/BalanceModel.py` is an empirical reporter for two separately read
2,000-health M14 bot calibration sets: nine raw-pacing records and six
`rpg.CloseTelegraph 0.4` records. It is not a game simulator, player model, or
prediction of PIE or packaged behavior.

## Parameters

| Parameter | Value | Status | Source |
|---|---:|---|---|
| Calibration boss health | 2000 | MEASURED | Nine collector records `Saved/BalanceRuns/20261023T1357*` through `20261023T1414*` |
| Raw-pacing calibration encounters | 9 | MEASURED | Flat records `20261023T135708*` through `20261023T141402*` |
| Telegraph 0.4 calibration encounters | 6 | MEASURED | Flat records `20261023T220426*` through `20261023T221742*` |
| Completed encounters | 7 raw / 6 telegraph | MEASURED | Raw set has the two recorded player deaths; telegraph set has six wins |
| Weapon / bleed / riposte loss | `METRIC boss_health` breakdown | MEASURED | Each flat driver JSON `metrics` array |
| Per-build DPS | Recorded loss / completed fight seconds | MEASURED | Calculated separately per set by `BalanceModel.py` |
| Mean hits taken per run | Top-level `hits_taken` | MEASURED | Printed beside mean fight seconds per set |
| Player survival | Not predicted | UNKNOWN | The model labels deaths but does not fit survival |
| Human input and skill | Not predicted | UNKNOWN | Bot-only records; owner feel test remains required |

The former 500-health recordings are history, not calibration for this model.

## Method

The driver JSON does not record a close-telegraph setting. The script therefore
uses the two explicit recorded run-ID lists in `SETS`, rather than guessing from
file contents. For each set and build, it pools completed runs and divides the
recorded weapon, bleed and riposte loss by their combined duration. It then
prints predicted versus measured duration for every record at 2,000 health,
plus per-record hits taken, riposte damage and bleed damage.

## Interpretation

Completed records should be near their own set's pooled rate because they
supply the calibration. Remaining error is cadence variation from openings,
posture breaks, ripostes, bleed procs and the killing hit. The model does not
predict survival, human skill, a different bot policy, another health value,
or another attack mix.

The model does not fit health, damage multipliers, stamina regeneration, dodge
timing, survival, or human skill. Those need repeat PIE data and owner hand
testing.
