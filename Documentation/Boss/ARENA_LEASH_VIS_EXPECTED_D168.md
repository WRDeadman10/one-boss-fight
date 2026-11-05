# Opt-in arena leash visualization expected sheet (Queue D168)

Status: protocol only. No visualization is implemented/enabled. Review the displayed bounds and default-off behavior before implementation. Live Editor/packaged verification is Lead-owned; this is a visualization protocol, not authorization to alter collision or leash behavior.

## Claim and boundary

The proposed opt-in view visualizes the same arena-leash bounds used by the gameplay rule. Enabling it must not change collision, navigation, target position, leash response, movement, damage or encounter state. Visualization must neither create nor remove collision and must not be used as the sole proof of the active gameplay bounds. The approved coordinate frame, bounds source, colors and drawing lifetime remain to be reviewed.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, logs/video/screens and hashes | **Expected:** unique ID and immutable evidence/hash. **Observed:** pending. |
| Build/map/actors | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, boss/player and generation. **Observed:** pending. |
| Bound source | **Expected:** exact authoritative center/radius/shape/coordinate frame from runtime readback, plus source identity. **Observed:** pending. |
| Feature state | **Expected:** visualization off by default/read-back; enabled only for paired view. **Observed:** pending. |
| Collision/gameplay baseline | **Expected:** relevant collision channels/responses, movement and leash outcomes read back identically for both views. **Observed:** pending. |

## Paired cases

Capture the same encounter position and leash configuration with visualization disabled and enabled. Change only the drawing toggle.

| Row | Required evidence | Pass condition |
|---|---|---|
| Hidden control | Record authoritative bounds values, actor positions, collision settings and leash response with drawing off; capture screen. | Establishes gameplay/bounds baseline without visualization. |
| Enabled view | Repeat at same transform; capture bounds values and view from matched camera plus collision settings and gameplay outcomes. | Drawn geometry corresponds to the same measured runtime bounds and coordinate frame. Collision responses and all gameplay outcomes match control. |
| Boundary probes | At approved inside/on/outside positions, compare actual leash classification and drawn relation; record exact coordinates and inequalities. | Visualization communicates the actual rule boundary without changing the rule. Exact equality semantics match source/readback. |
| Toggle-off regression | Disable visualization and repeat baseline probe. | Bound identity, collision, and leash response still match initial control. |

## Evidence interpretation and limits

- **Measured:** runtime bounds values, coordinate frame, collision channels, actor transforms and leash decisions with raw references; screenshots from the same camera and transform.
- **Inferred:** drawing accuracy only when rendered points are compared against the authoritative runtime bound values in the same coordinate frame.
- **Manual:** visibility, occlusion and readability of the visualization.
- A debug drawing does not prove the gameplay rule consumed those bounds. Screenshots cannot establish unchanged collision; compare actual channel/behavior readback and contact outcomes. No collision operation is authorized.

## Failure and stop conditions

Fail if default-on, drawn bounds differ from runtime source, any collision/gameplay field changes, or visualization placement alters physics. Stop if bounds source/coordinate frame is unknown, paired transforms differ, or visual measurements cannot be made. Missing evidence is UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No collision/bounds/assets/source changes, tests/build/Editor execution, or runtime claim. Implementation is not authorized before review.
