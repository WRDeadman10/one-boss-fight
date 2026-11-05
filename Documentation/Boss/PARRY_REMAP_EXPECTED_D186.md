# Opt-in remappable parry input expected sheet (Queue D186)

Status: protocol only. No remapping UI or behavior is implemented/enabled. Owner must approve key/controller UX and conflict policy before implementation. Live Editor/packaged proof remains Lead-owned.

## Claim and binding boundary

The proposed option lets the player remap the parry action while preserving the current default mapping and parry semantics. The remapped input must bind to the same reviewed action, fire once, and persist/read back as approved across controller replacement and restart. It must not change parry window, cooldown, grade, resource cost/refund, or unrelated actions. No key, interaction flow, persistence location, or conflict resolution is selected here.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, logs/screens and hashes | **Expected:** unique IDs and immutable evidence/hash. **Observed:** pending. |
| Build/map/player/controller | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, possessed player, controller/device identity. **Observed:** pending. |
| Default mapping | **Expected:** current parry action/key/device read back before any edit. **Observed:** pending. |
| Remap policy | **Expected:** owner-approved key UX, supported devices, duplicate/conflict handling, persistence and reset policy. **Observed:** UNKNOWN pending approval. |
| Input result | **Expected:** existing parry action callback/count, open/close, grade, stamina and other bound actions observed. **Observed:** pending. |

## Paired cases

Compare default mapping with remap disabled to an approved remapped key/device, changing only the mapping. Use existing manual input through the normal UI/action path; do not synthesize input or claim automated usability.

| Row | Required evidence | Pass condition |
|---|---|---|
| Default mapping control | Read back default key/device, exercise parry once and record action/count/window/resource outcome. | Current mapping remains unchanged when remapping is unused/reset; action fires once. |
| Remapped input | Apply owner-approved mapping and exercise once; capture stored mapping and same parry fields. | Readback matches selection; same parry action fires once with identical gameplay semantics. |
| Persistence/readback | Restart or replace controller/device according to policy; inspect mapping before input and exercise it. | Mapping persists or resets exactly as approved; no stale binding or duplicate callback. |
| Conflict/cancel/reset | Test reviewed conflicting key, cancel and restore-default flows. | Conflict resolution and cancellation match owner-approved UX; restore returns exact default mapping. |
| Unrelated actions | Exercise other bindings sharing relevant device/context. | Remap does not trigger or suppress unrelated actions outside approved conflict behavior. |

## Evidence interpretation and limits

- **Measured:** key/device mapping readback, action callback/event count, parry window/outcome and resource values with raw references.
- **Inferred:** persistence only when state is read back after the specified restart/controller change; current-process state is not persistence proof.
- **Manual:** clarity of remap flow, conflict UX, accessibility and discoverability.
- No key UX, key value, conflict policy, supported device matrix or persistence duration is approved. A written key value alone does not prove the runtime action is bound.

## Failure and stop conditions

Do not implement before owner approves key UX and conflict behavior. Fail if default changes, mapping readback differs, an action fires twice, remap alters parry semantics, unrelated input is broken, or persistence violates policy. Stop if input binding/readback cannot be observed or controller identity is ambiguous. Missing evidence is UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No input/UI/source changes, tests/build/Editor execution, or runtime claim. Implementation is not authorized before owner approval and review.
