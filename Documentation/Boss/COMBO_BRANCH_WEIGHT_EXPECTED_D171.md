# Opt-in combo branch weighting expected sheet (Queue D171)

Status: protocol only. No branch weights or selector behavior are implemented/enabled. Owner must approve exact balance weights before implementation. Lead owns live Editor/packaged verification.

## Claim and boundary

The proposed opt-in weights affect only deterministic selection among branches already eligible under the combo graph. With the feature off, the existing deterministic branch choice remains unchanged. A weight must not make an ineligible branch eligible, bypass refusal validation, change candidate identity, exceed attack budget/depth, or produce nondeterministic results for the same graph, seed and inputs. No weight values, probability targets, or balance preference are approved here.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, logs and hashes | **Expected:** unique IDs, immutable logs and post-run hash. **Observed:** pending. |
| Build/map/profile/graph | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, profile, graph version/root and resolved MoveIds. **Observed:** pending. |
| Candidate eligibility | **Expected:** for every trial, capture eligible branches, refusal reasons, source state and graph node before weighting. **Observed:** pending. |
| Seed and weight config | **Expected:** fixed seed matrix, exact owner-approved weights and feature default-off readback. **Observed:** UNKNOWN until approval. |
| Trial protocol | **Expected:** repeated identical trials with same seed/input, then a declared set of seeds; reset selector state between independent trials. **Observed:** pending. |

## Paired cases

Use the same graph/profile and eligible inputs with weighting off and on; change only the reviewed weighting toggle/config. Do not infer balance from one playthrough.

| Row | Required evidence | Pass condition |
|---|---|---|
| Default branch control | Record deterministic branch choice per seed with feature off, plus graph node, eligibility and selector state. | Same seed and same input reproduce the existing branch exactly. This remains the default behavior. |
| Enabled fixed-seed replay | Repeat each approved seed/input with weights enabled. Record branch and all eligible/ineligible candidates. | Same seed/input/weight table yields the same branch; only eligible candidates participate. |
| Seed-set distribution | Run the owner-approved seed set and report counts per eligible branch with exact denominator and weights. | Observed distribution is compared with the approved expectation using a reviewed tolerance; no fairness/balance claim without agreed sample plan. |
| Invalid branch/refusal | Include a graph with a refused/ineligible branch and verify whether another eligible branch can be selected according to existing fallback policy. | Weight never selects an invalid branch or suppresses required refusal when no branch is eligible. |
| Budget/depth guard | Capture accepted hits, combo depth, attack count and generation throughout each sequence. | Weighting changes neither attack budget nor depth/terminal rules. |

## Evidence interpretation and limits

- **Measured:** per-trial seed, graph/node, eligible set, selected MoveId, counts, budget/depth and timestamps with raw references.
- **Inferred:** distribution only from a declared number of independent seeds/resets and approved statistical tolerance. Fixed-seed repeatability is not proof of desired balance.
- **Manual:** whether branch variety and pacing feel acceptable; owner determines balance.
- No weight values, sample count, tolerance, or probability target is approved. Leave balance acceptance UNKNOWN until the owner decision exists.

## Failure and stop conditions

Do not implement before the owner approves a concrete weight table and acceptance tolerance. Fail if default behavior changes, same-seed replay diverges, an ineligible branch is selected, required refusal is bypassed, or budget/depth semantics change. Stop if eligibility or selector reset cannot be observed. Missing evidence is UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No weight selection, source/profile changes, tests/build/Editor execution, or runtime claim. Implementation is not authorized before owner approval and review.
