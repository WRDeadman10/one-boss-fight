# KI-193 Development and Shipping evidence intake

Status: offline intake template only. KI-193 remains PARTIAL until Lead returns same-build cook and packaged-runtime evidence for both configurations. This file does not authorize a cook, package, stage inspection, or raw evidence modification by Codex.

## Canonical required set

The checker reads the canonical list at `Scripts/Tools/er_tier2_required_cook_assets.txt`. It currently contains exactly eight unique `/Game` package paths:

| Package path | Role |
|---|---|
| `/Game/OneBossFight/Player/Animations/AM_ER_Backstep_Mixamo_V2` | Approved backstep montage |
| `/Game/OneBossFight/Player/Animations/AM_ER_Attack_GuardCounter` | Guard-counter montage |
| `/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Light` | Air-light montage |
| `/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Heavy_Plunge` | Air-heavy montage |
| `/Game/OneBossFight/Boss01/Animations/AM_Boss01_ParryRecoil` | Parry recoil montage |
| `/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura` | Phase-two aura system |
| `/Game/OneBossFight/Effects/PPM_ParryDistortion` | Parry post-process material |
| `/Game/OneBossFight/Data/MPC_CombatFeedback` | Combat feedback parameter collection |

The eight paths were cross-checked against the current C++ soft-object defaults listed in `AR_C21_C25_KI193_COOK_GATE.md`. This is an exact package-path presence check. Source references and manifest presence do not prove asset loadability, runtime selection, visual visibility, stage identity or successful packaged launch.

## Lead intake — complete one section per configuration

### Development

- Build ID:
- Configuration: `Development`
- Package command and completion status:
- Stage root and `BuildStamp.txt` identity:
- UFS / non-UFS manifest paths and SHA-256:
- Normalized manifest path, source-manifest SHA-256, normalized JSON SHA-256 and required-list SHA-256:
- Inner executable path and SHA-256:
- Checker command, complete JSON output and output-file SHA-256:
- `check_stage_identity.py` output:
- Packaged route run IDs and `[EncounterActivation] route=...` witnesses:
- Default-wired controls exercised and exact outcome:
- Full log, filtered lines, capture paths and file hashes:
- Failures / omitted cases:

### Shipping

- Build ID:
- Configuration: `Shipping`
- Package command and completion status:
- Stage root and `BuildStamp.txt` identity:
- UFS / non-UFS manifest paths and SHA-256:
- Normalized manifest path, source-manifest SHA-256, normalized JSON SHA-256 and required-list SHA-256:
- Inner executable path and SHA-256:
- Checker command, complete JSON output and output-file SHA-256:
- `check_stage_identity.py` output:
- Packaged route run IDs and `[EncounterActivation] route=...` witnesses:
- Default-wired controls exercised and exact outcome:
- Full log, filtered lines, capture paths and file hashes:
- Failures / omitted cases:

## Acceptance and stop rules

1. Keep Development and Shipping in separate sections, with distinct Build IDs, roots, stamps and executable hashes. Require each CLI Build ID and configuration to match the normalized manifest metadata exactly.
2. Run `ar_er_cook_manifest.py` against the normalized manifest exported from that exact configuration/build. A `PASS` only establishes that all eight required paths appear in that manifest; missing paths are a cook `FAIL`, not permission to substitute another build.
3. Run stage identity validation separately. Missing/mismatched stamp, root, configuration or shared Build ID is a hard stop; do not infer identity from directory names.
4. Run packaged control smoke separately from cook presence. Each claimed route needs a same-run activation witness; a driver label alone is insufficient. Missing route witness, incomplete smoke marker, failed process or missing required log/capture is not a pass.
5. Preserve every failed output. Do not relabel, substitute or combine evidence across Build IDs/configurations. KI-193 remains PARTIAL until both configurations have accepted cook, stage and packaged-runtime evidence. The owner-approved reel and PIE results do not substitute for those gates.

Related offline checker and exact acceptance scope: `AR_C21_C25_KI193_COOK_GATE.md`. No TEST_PLAN update is made by this intake artifact; add a receipt only after an authorized Lead package run returns.
