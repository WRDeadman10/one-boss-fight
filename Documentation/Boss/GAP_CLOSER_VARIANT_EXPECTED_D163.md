# Opt-in gap-closer variant selector expected sheet (Queue D163)

Status: protocol only. No selector, route, or asset change is implemented. Review the exact variant list, selection policy and default-off behavior before implementation. Lead owns live Editor/packaged verification; asset edits or destructive replacement are outside this task.

## Claim and boundary

The proposed opt-in selector may choose only among owner/Lead-approved existing gap-closer assets/routes. The default route and its selection behavior must remain unchanged when the feature is off. No new, renamed, duplicated, deleted, or recreated assets are authorized. Selection must not alter eligibility, range/exit rules, target, hit outcomes, attack timing or cleanup. The current queue text does not supply approved variant identities; leave that list UNKNOWN until reviewed.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, raw logs/video and hashes | **Expected:** unique IDs and immutable evidence hashes. **Observed:** pending. |
| Build/map/profile | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, profile and generation. **Observed:** pending. |
| Existing asset inventory | **Expected:** exact package/object paths and referencer status for every reviewed existing variant, plus baseline default asset. **Observed:** pending; no asset is approved by this sheet. |
| Feature state and selector inputs | **Expected:** default-off readback; record variant list, seed, selector config and selected identity. **Observed:** pending. |
| Gap-close scenario | **Expected:** same target, distance, geometry, movement budget and eligibility state across runs. **Observed:** pending. |

## Paired cases

After approval, compare the default route with the feature off to each approved opt-in variant. Change only the reviewed selector mode/seed; reset to the same state before each case.

| Row | Required evidence | Pass condition |
|---|---|---|
| Default route control | Capture selected asset/route, movement start/end, target, distance, exit/refusal reason and attack outcome with feature off. | Existing default route remains selected and behavior is unchanged; no alternate asset is silently substituted. |
| Each approved variant | Record selected package/object identity, loaded/used state, transform/path result, target identity and movement/attack telemetry. | Actual selected route matches one approved existing asset; no unreviewed path or asset is used; eligibility, target, and terminal semantics remain valid. |
| Invalid/unavailable variant | If an approved variant is deliberately made unavailable through safe test configuration, record refusal/fallback and default state. Do not alter or delete the asset. | Failure follows reviewed fail-closed/fallback policy and never silently changes the default asset or partially publishes a selection. |
| Feature-off regression | Re-run baseline after opt-in tests with feature still read back off. | Default route identity and behavior match the initial control. |

## Evidence interpretation and limits

- **Measured:** selected route/package/object identity, eligibility/refusal, movement/attack outcome and timestamps from raw logs; relevant asset registry/referencer evidence.
- **Inferred:** variant use only when telemetry identity matches the loaded/played asset, not from a candidate label alone.
- **Manual:** animation/movement quality and visible clipping/path safety in the authored arena.
- Static asset paths do not prove a package is loaded or that the route looks correct. No candidate asset is approved in this protocol; owner/Lead must review a concrete list and referencer evidence first.

## Failure and stop conditions

Stop before implementation if the variant list is absent, an asset is not approved/existing, referencer status is unknown, or acceptance would require delete/recreate/rename. Fail if feature-off changes the default route, an unapproved asset loads, selection changes target/eligibility/combat semantics, or unavailable dependencies produce an unreviewed fallback. Missing runtime evidence is UNKNOWN.

## Verification boundary

Expected protocol only. No asset operation, source/UI change, tests/build/Editor execution, or runtime claim. Implementation is not authorized before variant and behavior review.
