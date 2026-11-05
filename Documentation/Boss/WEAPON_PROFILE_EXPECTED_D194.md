# Opt-in alternate starter weapon profile expected sheet (Queue D194)

Status: protocol only. No profile or asset is changed/selected by this sheet. Owner/Lead must approve an exact existing profile before implementation. No asset creation, replacement, deletion, or recreation is authorized. Live Editor/packaged proof is Lead-owned.

## Claim and boundary

The proposed opt-in profile selects an already-existing approved starter weapon profile. Default loadout remains unaffected when the option is off. Damage and parry behavior must be measured as separate paired controls because weapon statistics and parry input/resource semantics are distinct. No profile identity, damage value, weapon asset or balance choice is approved here.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, logs/video and hashes | **Expected:** unique immutable evidence/hash. **Observed:** pending. |
| Build/map/player | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, player/controller identity. **Observed:** pending. |
| Existing profile identity | **Expected:** exact package/object path, source/config values and owner/Lead approval reference; verify it exists without modifying it. **Observed:** UNKNOWN pending selection. |
| Default weapon control | **Expected:** current starter weapon/profile and all damage/parry-relevant stats read back. **Observed:** pending. |
| Alternate profile state | **Expected:** option off by default/read-back; enabled run records every changed field and reset/persistence behavior. **Observed:** pending. |

## Paired cases

Use matched player build, target, attack, phase and input sequence. Compare default profile with approved alternate; change only weapon profile.

| Row | Required evidence | Pass condition |
|---|---|---|
| Default loadout control | Record weapon/profile identity, base stats, damage and parry inputs/outcomes with option off. | Existing starter loadout and behavior remain unchanged. |
| Alternate damage control | Use same approved weapon attack against same target/state; capture weapon identity, damage payload and actual health delta. | Values match the existing profile's approved definitions; only owner-approved weapon differences occur. |
| Alternate parry control | Perform the same manual parry input/attack contact and capture window, grade/outcome, stamina before/after, cooldown and recovery. | Parry semantics match the approved profile contract; no unintended input/resource side effect. |
| Reset/default regression | Disable/reset and read profile plus stats again. | Default profile is restored and no alternate values leak into later generation. |
| Asset integrity | Compare package path/object identity and approved source status before/after. | Existing asset remains intact and referenced; no asset mutation/recreate operation occurs. |

## Evidence interpretation and limits

- **Measured:** exact profile/package/object identity, stats, attack/event, damage/health delta and parry/resource outputs with raw references.
- **Inferred:** damage attribution only if target, attack, armor/resistance and other modifiers match; requested payload is not necessarily actual health removed.
- **Manual:** weapon feel/balance remains owner decision.
- No existing profile is approved in this document. Static path presence does not prove loaded runtime use; package identity and current asset integrity must be checked live before any claim.

## Failure and stop conditions

Do not implement before exact existing profile is approved. Fail if default changes, selected profile does not read back, unapproved fields change, damage/parry controls diverge beyond approved differences, or asset is modified/recreated. Stop if profile/package identity or referencer status is unknown. Missing evidence remains UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No profile/stat/asset/source changes, tests/build/Editor execution, or runtime claim. Implementation is not authorized before owner/Lead review.
