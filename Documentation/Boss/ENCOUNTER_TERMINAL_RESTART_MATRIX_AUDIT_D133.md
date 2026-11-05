# Queue D133 — encounter completion/restart matrix audit

Date: 2026-11-03  
Method: static read of boss terminal flags/restart code and current automation references; no tests run.

## State matrix from source

| State | Tick behavior | Restart eligibility |
|---|---|---|
| Active / aborted card recovery | encounter continues unless terminal failure is set; executor same-generation recovery exists for the stance-break path | refused (`bSucceeded` and `bDead` false) |
| Succeeded | `bSucceeded=true`; tick returns early | allowed only when initialized, not failed, and generation strictly increases |
| Dead | `bDead=true`; executor aborts; tick returns early | allowed under the same newer-generation condition |
| Failed | `bFailed=true`; executor aborts; tick returns early | always refused; failure is sticky and is not cleared by restart |

`RestartEncounter` validates state/thread/target health before rearming the executor, then advances generation and clears run-scoped flags and histories (`bSucceeded`, `bDead`, `bStartedMove`, attack count, combo/parry/phase/posture/selector/LOS/dodge/bleed and related evidence state), restores boss health when hittable, resets location/rotation/movement, and starts the walk. `bFailed` is intentionally not reset because `CanRestart` disallows a failed boss.

## Test coverage / limit

`RPGBossMoveModelTests.cpp` covers model generation reset and stale-token rejection. `RPGFrameworkProofFixture::RestartEncounterForTest` guards before mutating target health and calls the actor restart, but repository search found no actor-level matrix asserting success/death restart acceptance, failure refusal, and clear flags across the next generation. Model tests cannot prove actor outcome flags. No actor-level restart behavior is claimed here.
