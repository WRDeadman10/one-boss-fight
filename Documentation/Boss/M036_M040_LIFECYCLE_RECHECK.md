# Queue M Batch 8 — lifecycle and recovery recheck

## Task disposition

| Task | Status | Evidence / boundary |
|---|---|---|
| M036 | **PARTIAL — native map only** | Existing startup refusal tests cover malformed selection, empty/duplicate census, unavailable epoch and injected activation failure. There are no G044 PIE refusal results to reconcile. |
| M037 | **LEAD-PIE BLOCKED** | Native generation/reset coverage exists, but no selected repeated live-session telemetry is available. |
| M038 | **LEAD-PIE BLOCKED** | Transient subsystem shutdown/restart automation exists; no live PIE teardown chronology exists. |
| M039 | **LEAD-PIE BLOCKED** | Native unsafe-release retention coverage exists; no safely reproduced live refusal/recovery is available. |
| M040 | **NO CHANGE PROPOSED** | No witnessed live defect supports a new behavior proposal. |

## Recheck result

The existing `L036_L040_LIFECYCLE_AUDIT.md` remains accurate. Claude-reported
native automation is not promoted into PIE/session evidence. No runtime
behavior change is justified, and no tests, build, Editor, PIE or Unreal
execution was performed.
