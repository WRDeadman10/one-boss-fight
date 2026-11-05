# Opt-in arena lighting accessibility profile expected sheet (Queue D196)

Status: protocol only. No lighting profile, setting, or asset is changed/selected. Owner/Lead must approve the exact existing profile(s) before implementation. No asset replacement or recreation is authorized. Packaged readback and visual verification remain Lead-owned.

## Claim and asset boundary

The proposed opt-in accessibility profile selects among approved existing lighting configurations while leaving default arena lighting unchanged. It must not replace/reimport/recreate referenced assets or change collision, navigation, attack readability/timing, damage or gameplay. Any approved profile must be identified by exact package/object identity and its effective packaged values must be read back; editor defaults alone are insufficient. No brightness/contrast/exposure/color values are selected here.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, screenshots/video and hashes | **Expected:** unique immutable captures and post-capture hash. **Observed:** pending. |
| Build/map/profile | **Expected:** exact packaged build/hash, `/Game/OneBossFight/Levels/L_SevarogArena`, map and rendering config. **Observed:** pending. |
| Existing profile identity | **Expected:** exact package/object path for each owner-approved profile, current asset/referencer state and unchanged source identity. **Observed:** UNKNOWN pending approval. |
| Effective rendering state | **Expected:** packaged readback of relevant lighting/exposure/color settings, display mode, HDR/brightness and runtime overrides. **Observed:** pending. |
| Feature state | **Expected:** default profile off/read-back; enabled run records selected existing profile and all effective values. **Observed:** pending. |

## Paired cases

Capture the same map/time/weather/exposure and camera/player viewpoints under default and each approved existing profile. Change only profile selection.

| Row | Required evidence | Pass condition |
|---|---|---|
| Default packaged control | Record packaged build/config/readback and representative arena views with default profile. | Establishes unchanged baseline and confirms effective settings. |
| Each approved profile | Select exact existing profile; record package/object identity, packaged effective values and matched screenshots. | Readback matches approved profile; no asset replacement; intended accessibility comparison is documented under fixed display conditions. |
| Gameplay/readability guard | Capture telegraphs, arena edges, player/boss silhouettes and interactions under both profiles; compare combat state. | Profile does not obscure required cues or change gameplay/collision/navigation. Any accessibility claim stays limited to tested users/settings. |
| Asset integrity | Compare package/object paths and asset hashes/referencers before/after. | Same existing assets remain; no import replacement/recreate occurred. |

## Evidence interpretation and limits

- **Measured:** package/build hash, profile path, effective rendering values and fixed-camera screenshots.
- **Inferred:** profile effect only when display settings and capture are matched; screenshot appearance alone does not prove effective runtime configuration.
- **Manual:** contrast/readability/accessibility evaluation under stated display and viewing conditions.
- No accessibility standard or supported visual profile is claimed unless independently selected and tested. Editor-only readback cannot establish packaged behavior; package hash and runtime values are required.

## Failure and stop conditions

Do not implement before profile identities and values are approved. Fail if default changes, effective packaged values differ from approval, an asset is replaced/recreated, or gameplay/collision/navigation changes. Stop if package readback, asset identity/referencer evidence or matched display conditions are unavailable. Missing evidence remains UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No lighting/material/asset/source changes, tests/build/Editor execution, or runtime claim. Implementation is not authorized before owner/Lead review.
