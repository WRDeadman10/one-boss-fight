# Pack arena parry proof expected sheet (Queue D32)

Status: design-only expected sheet. A Lead-owned live run is required to fill the observed columns. No run/build/Editor/tests performed by Codex.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, raw log path, log SHA-256 | **Expected:** unique ID and immutable raw log/hash. **Observed:** pending. |
| Map package | **Expected:** `/Game/OneBossFight/Levels/L_SevarogArena`. **Observed:** pending; fail setup if another map is loaded. |
| Boss and player identity | **Expected:** actual pack boss and possessed player pawn, with actor/class identifiers and transforms recorded. **Observed:** pending. Do not substitute framework proof boss. |
| Combat style and parry route | **Expected:** style that grants `GA_PlayerParry`, real `IA_Parry` binding, `URPGPlayerParry`, and tag ownership/readback recorded. **Observed:** pending. |
| Profile, enabled/control state, test hooks | **Expected:** exact profile asset and all relevant CVar/input hooks with before/after values. **Observed:** pending; unknown values stay UNKNOWN. |

## Paired contact rows

| Row | Setup and contact | Required same-contact evidence | Pass condition |
|---|---|---|---|
| Control (no parry) | Reset to recorded baseline; allow one identified pack boss melee attack to contact with parry input absent and `Status.ParryActive=0`. | Attacker, attack/trace identity, contact time, target, health before/after, pack impact outcome, raw-log line references. | Valid control requires real pack contact and positive player health loss. No contact or no loss is inconclusive, not a negative parry. |
| Enabled parry | Repeat baseline; open through the real `IA_Parry` binding at the observed attack timing; capture the actual pack contact. | Same identity fields plus input action result, window open/close, tag value at contact, pack-owned parry response, health and stamina before/after, raw-log line references. | Valid parry requires same identified pack attack path, tag active at contact, pack-specific response, and zero health loss for that contact. Native resolver `Parried` or tag add alone does not pass. |

One row represents one contact. Keep misses, wrong attack types, setup errors, and ambiguous contacts as failed/inconclusive rows; do not combine them into positive sample counts. Use matched baseline/reset conditions for control and enabled rows and state any differences. Capture per-contact stamina change and configured cost/refund; missing attribute reads prevent resource claims.

## Unknowns and failure handling

- **UNKNOWN until reflected/runtime evidence:** which Blueprint impact state receives the pack boss weapon contact, the pack's response signal/token, exact montage/notify contact timing, tag readback at that instant, and whether player health changes on that branch.
- **UNKNOWN until setup inspection:** exact map actor instance, current player/style configuration, profile, and any inherited input hooks. Record actual values; do not infer from filenames or a prior framework proof run.
- **Setup invalid:** wrong map/boss, missing real input binding, or no readable actor/tag/health identity. **Contact inconclusive:** no real attack contact or ambiguous source. **Failed parry:** verified real contact but inactive tag, no pack response, or positive health loss.
- Cleanup must remove only objects, callbacks, and temporary state created by this run; end PIE normally; retain unique logs and hashes; verify content/project state unchanged. Existing `pie_sevarog_pack.py` cleanup is not approved for reuse without replacing its broad editor-level boss deletion.

## Evidence boundary

This sheet is an expected procedure, not observed evidence. BUILD-152 witnessed native tag plumbing on a framework proof map and does not satisfy either paired row. No pack Blueprint branch or real-arena parry result is claimed.

## Setup
## Control
## PASS
## FAIL
