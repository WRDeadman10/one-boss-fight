# Opt-in arena color-contrast profile expected sheet (Queue D197)

Status: protocol only. No palette, art, or feature is selected/changed. Owner chooses the approved art/palette. Review default-off behavior before implementation. Live Editor/packaged screenshot verification remains Lead-owned; no asset replacement or recreation is authorized.

## Claim and art boundary

The proposed opt-in contrast profile changes only the approved visual palette for arena elements within its reviewed scope. Default art/colors remain unchanged when off. Contrast changes must not alter collision, navigation, telegraph/attack timing, hitboxes, damage, targeting or asset identity. No target elements, palette values, color-vision model or accessibility standard is selected here.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, screenshots/video and hashes | **Expected:** unique immutable capture and post-capture hash. **Observed:** pending. |
| Build/map/profile | **Expected:** exact packaged build/hash, `/Game/OneBossFight/Levels/L_SevarogArena`, profile and rendering config. **Observed:** pending. |
| Approved palette | **Expected:** owner decision/reference with exact existing or reviewed palette/art identity and named affected elements. **Observed:** UNKNOWN pending choice. |
| Display conditions | **Expected:** fixed resolution, brightness, HDR/color mode, capture method and camera positions recorded. **Observed:** pending. |
| Gameplay baseline | **Expected:** same attacks, telegraph phases, hitboxes, collision and encounter state under both profiles. **Observed:** pending. |

## Paired cases

Capture the same arena views and combat states with default palette and approved contrast palette; change only the profile selection.

| Row | Required evidence | Pass condition |
|---|---|---|
| Default control | Capture key arena/combat views with default profile and exact build/display settings. | Existing visual baseline remains unchanged when option is off. |
| Enabled approved palette | Repeat same camera/state views with approved palette; record changed elements and profile readback. | Intended elements visibly differ per approved art decision; no unrelated elements/assets are replaced. |
| Gameplay/telegraph guard | Capture same telegraph frames, attack phases, collision and gameplay outcomes under both profiles. | Contrast change is visual only; telegraph timing, geometry and combat semantics are identical. |
| Default regression | Disable profile and recapture baseline. | Original visual identity and effective values return. |
| Asset integrity | Compare exact asset/package identity and hash/referencer state before/after. | No replacement/recreate or unintended mutation occurred. |

## Evidence interpretation and limits

- **Measured:** build/profile identity, effective visual settings, screenshots, affected asset identities and gameplay state with references.
- **Inferred:** palette-only effect from matched camera/display/game state; screenshots from different brightness/HDR settings are not directly comparable.
- **Manual:** color distinction/readability for named users/viewing conditions and whether contrast harms art intent or obscures other cues.
- No formal accessibility standard, palette, supported vision profile or universal readability claim is approved. Owner chooses art and scope; screenshot evidence alone cannot prove accessibility for all users.

## Failure and stop conditions

Do not implement before owner chooses palette/art scope. Fail if default changes, unapproved assets/colors change, gameplay geometry/timing changes, or the profile does not match the approved palette. Stop if display conditions are unmatched, asset identity is unknown, or target elements have not been approved. Missing evidence remains UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No palette/art/assets/source changes, tests/build/Editor execution, or runtime claim. Implementation is not authorized before owner choice and review.
