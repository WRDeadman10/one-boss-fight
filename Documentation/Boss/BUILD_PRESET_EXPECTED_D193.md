# Opt-in player build selector preset expected sheet (Queue D193)

Status: protocol only. No preset or stat configuration is implemented/changed. The owner chooses the stats and preset values before implementation. Live Editor/packaged proof remains Lead-owned.

## Claim and ownership boundary

The proposed opt-in selector preset selects an owner-authored set of player stats, while default build behavior remains unchanged. Every changed stat must be named and read back exactly; the preset must not silently change unrelated stats, starting inventory, equipment, boss configuration or persistent profile data. This sheet does not select stat values, build balance or a default preset.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, logs/screens and hashes | **Expected:** unique ID and immutable evidence/hash. **Observed:** pending. |
| Build/map/player | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, player identity and generation. **Observed:** pending. |
| Baseline build | **Expected:** current default build selection and complete stat/inventory/equipment readback before preset change. **Observed:** pending. |
| Owner-approved preset | **Expected:** owner decision/reference with preset identity, each stat, type, value, allowed range and reset/persistence policy. **Observed:** UNKNOWN pending choice. |
| Feature state | **Expected:** preset option off by default/read-back; enabled only with exact approved preset. **Observed:** pending. |

## Paired cases

From matched new-character/build-selection state, compare unchanged default with the owner-approved preset. Change only the preset selection and record all resulting fields.

| Row | Required evidence | Pass condition |
|---|---|---|
| Default build control | Capture complete stats, starting equipment/inventory, ability state and build identity with preset unused. | Existing default build is unchanged. |
| Enabled preset | Select approved preset; read back every stat/config field and compare with decision table. | Each value matches approved selection; no unlisted field changes; invalid values refuse/fail safely. |
| Gameplay guard | Exercise the same bounded source/model checks or Lead-owned encounter sample with each build state. | Observed differences are attributable only to the approved stats; no unintended ability, inventory or boss changes. |
| Reset/new generation | Return to default/restart and read back all values. | Preset resets/persists exactly per owner policy; no leakage into default or next character. |

## Evidence interpretation and limits

- **Measured:** exact preset ID and full before/after stats/equipment/ability fields with raw references.
- **Inferred:** effect attribution only when all changed fields are enumerated and only approved fields differ.
- **Manual:** perceived playstyle/balance is owner judgment; this protocol does not rank builds.
- Without the owner decision table, no enabled preset can pass. A displayed preset label does not prove actual stat values.

## Failure and stop conditions

Do not implement before owner supplies exact stat values/ranges and persistence policy. Fail if default changes, readback mismatches, unrelated fields change, state leaks across reset, or an unapproved stat affects behavior. Stop if stat provenance or complete readback is unavailable. Missing evidence is UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No stat selection, source/profile/config changes, tests/build/Editor execution, or runtime claim. Implementation is not authorized before owner approval and review.
