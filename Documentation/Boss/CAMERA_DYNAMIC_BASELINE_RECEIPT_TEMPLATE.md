# Dynamic melee camera baseline receipt

Use one copy per DATA-default capture stage. Lead owns PIE and fills the fields from the actual run; Codex has not run or pre-populated measurements. Use the C-1105 DATA-default result to inform owner choice; capture any requested baseline before implementation, then repeat the selected scenario after the owner-selected option is implemented and reviewed. Do not schedule true-legacy parity reruns solely to restore route wording; legacy remains a parity control under the C-1104 policy.

## Run identity

- Stage: `[PRE-CHOICE BASELINE | POST-CHOICE COMPARISON]`
- Effective route witness: `[route=data; exact same-run activation line]`
- Project revision / working tree identifier: `[fill from run]`
- Build ID and target: `[fill from run]`
- Configuration and stage root: `[Development | Shipping; exact root]`
- Same-run DATA activation witness for acceptance: `[EncounterActivation] route=data; exact line or missing`
- Camera CVar requests and effective readback for every option: `[explicit values + source]`
- Engine version / device / display mode: `[fill from run]`
- PIE driver and command: `[fill from run]`
- Run ID, date/time, log path, capture/video path: `[fill from run]`
- Raw log SHA-256 and process exit/terminal status: `[fill from run]`
- Camera option selected by owner (post-choice only): `[A | B | C | pending]`

## Scenario and observations

- Arena and combat state: `[fill; keep identical between comparison runs]`
- Boss circling direction / trial: `[left | right | repeat number]`
- Player-to-boss distance at start and during orbit: `[150–250 cm target; record actual range]`
- Named segments: `[standing | attack recovery | dodge | phase-two aura | wall | floor]`
- Per-tick sample count and interval: `[fill from log]`
- Camera-inside-visible-boss-bounds: `[count / total; identify unavailable bounds samples]`
- Actual spring-arm length: `[min / median / max cm from trace]`
- Sweep hit component and hit distance: `[counts / identities / unknowns]`
- Boss capsule `ECC_Camera` response: `[readback per route]`
- Camera and player/boss silhouettes: `[capture references; describe only observed clipping/occlusion]`
- Wall/floor safety evidence: `[capture/log reference and observed result]`
- Post-run option reset / cleanup readback: `[all selected CVars returned to zero; evidence or not run]`

## Comparison and disposition

- Same scenario/build/configuration across before/after: `[yes/no; explain differences]`
- Difference in intrusion rate, arm length, hit identity, and readability: `[report measured values; do not infer from AABB alone]`
- Attack, dodge-direction, aura and wall/floor checks: `[pass/fail/not run with evidence]`
- Limitations, unreadable samples, and deviations: `[fill]`
- Lead reviewer / date: `[fill]`
- Owner decision or review reference: `[fill; no option is implied by this template]`

The camera probe's world AABB occupancy is an approximation of visible-mesh bounds, and its sweep-hit estimate omits unavailable socket offsets. Neither establishes rendered-pixel visibility by itself. Keep raw route logs and video/screenshots with this receipt.
