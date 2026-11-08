# AC-C21–C25 — Tier 2 preview readiness audit

Date: 2026-11-07. Static Source, test, config, and mailbox review only. No asset assignment, Unreal run, build, cook, or commit.

## Current acceptance state

Mailbox C-982 accepts `PPM_ParryDistortion` as the visual look target, but requires Lead PIE verification of the Unreal material under `rpg.Art.Tier2` before wiring. C-983 accepts recoil R2 motion subject to full-body-and-sword framing and aura R2 shape subject to a fire-colour correction. C-985 accepts A-594's corrected recoil and aura previews **for owner review**; the aura reads salmon in the unlit preview and final appearance is for engine/owner judgment. C-986's Lead asset check finds zero notifies on all five new montages, so the recoil montage has no evidenced play contract yet; its notify template remains a separate hotfix. MPC evidence lists scalar `ParryPulse` with default 0.0; no separate runtime acceptance is recorded. C-953 Option A authorizes the empty-default Development preview scope; it does not establish asset assignment or runtime/package proof.

| Hook | Source/default/gate | Lifecycle or fallback | Evidence state and remaining gate |
|---|---|---|---|
| `rpg.Art.Tier2` | `RPGTier1VisualRules.cpp:9-18,29-35`: CVar declaration exists only under `UE_BUILD_DEVELOPMENT`, integer default 0; non-Development returns false via `IsTier2PreviewEnabledForBuild(false,0)`. | Pure predicate also requires Development and nonzero value (`RPGPresentationRules.h:9-12`). No Shipping runtime switch path. | Source guard and offline source contract exist; Lead BUILD/Shipping symbol verification is a separate receipt, not repeated here. |
| Parry distortion | `RPGLegend.h:228-232`: optional soft material and transient loaded pointer. `RPGLegend.cpp:360-366`: synchronous resolution only in BeginPlay when the switch is already on and the property is non-null. | Confirmed parry passes the preloaded pointer into subsystem; subsystem adds it to the parrying actor's camera, remembers any prior blendable weight, then restores that weight or removes its own entry (`RPGLegend.cpp:167-202,243-262`). Enabling CVar after BeginPlay cannot populate the loaded pointer; next play start is needed. | C-982 accepts PPM look only; Lead still verifies actual UE rendering. KI-191 remains open for measured cold-start/loading and runtime visual proof. |
| Phase-two aura/glow | `RPGSevarogDirector.h:48-56`: optional soft Niagara and null MPC pointer; glow parameter defaults to `PhaseTwoGlow`. `ApplyPhaseTwoVisuals` is Development-preview gated, loads/spawns aura attached to boss mesh and sets MPC scalar to 1 (`RPGSevarogDirector.cpp:195-221`). | `ClearPhaseTwoVisuals` destroys retained Niagara component and sets the applied scalar to 0 (`224-242`). Called by EndPlay, reset, and detected boss death (`54-61,453,557-562`). This resets the scalar to zero rather than preserving an earlier MPC value; whether another writer shares it is not established here. | C-985 accepts A-594's visual for owner review; it reads salmon in the unlit preview, with final look in engine. C-986 reports the aura is a Niagara system rather than montage, so the zero-notify finding concerns the other five montage assets. Owner review and Lead PIE remain pending. No dedicated native lifecycle test found in Tier 2 source contracts. |
| Boss recoil montage | `RPGSevarogDirector.h:58-62`: optional montage pointer defaults null. `PlayParryRecoil` returns false if preview is off, montage is null, owner/mesh/AnimInstance is absent, or `Montage_Play` fails (`RPGSevarogDirector.cpp:244-253`). | Triggered from successful parry notification (`RPGPlayerParry.cpp:142-168`); null/failure does not block the separate player parry and Legend path. It has no explicit slot check or fallback montage. | C-985 accepts the A-594 visual for owner review; C-986 reports the asset has zero notifies. Owner review, notify correction, Lead slot/runtime/cook checks remain pending. |
| Package/cook path | No hard-coded Tier 2 asset path in these hooks. Existing config roots `/Game/OneBossFight/VFX` and `/Game/OneBossFight/Boss` are documented by `AA_C20_TIER2_PRESENTATION_HOOKS.md`. | Soft and object properties remain unassigned by this audit. | Asset files/evidence delivery is not proof of assignment, successful load, cooked package presence, or PIE appearance. Lead CookCoverage/PIE gates remain open. |

## Test and review boundary

`Scripts/Tools/test_optional_tier2_hooks.py` and `test_optional_presentation_wiring_contract.py` are source-text contracts for defaults, guards, call paths, and cleanup callsites. They do not execute Unreal objects or prove asset appearance, montage slot compatibility, loaded/cooked assets, or teardown in a live world. No dedicated native runtime test for the optional aura/recoil/post-process lifecycle was found in the searched test tree. No source change is recommended from this static audit; keep references empty until the specific acceptance and Lead gates are recorded.

## AC-C25 acceptance sheet

| Gate | Owner / Lead | Status |
|---|---|---|
| Option A preview scope | Owner, C-953 | Selected; defaults remain empty/off. |
| Distortion look target | Claude, C-982 | Accepted as look target; not UE runtime acceptance. |
| Recoil preview R1 | Claude, C-982 | Rejected. |
| Recoil preview R3 | Claude, C-985 | A-594 visual accepted for owner review; owner review pending. C-986 separately reports zero notifies on the montage; notify correction and Lead slot/runtime/cook remain pending. |
| Aura preview R1 | Claude, C-982 | Rejected. |
| Aura preview R3 | Claude, C-985 | A-594 visual accepted for owner review; colour reads salmon in the unlit preview and final look is in engine. Owner review and Lead runtime/cook remain pending. |
| PPM look-target video | Antigravity, A-594 | Review MP4 delivered; C-982 look target accepted; Lead UE material PIE and owner review remain separate. |
| MPC parameter list | Antigravity, A-592 | `ParryPulse`, scalar, default 0.0; separate acceptance/runtime proof not recorded. |
| Assign references to production component | Owner/Lead | Not authorized/recorded in this audit; do not infer from preview-scope approval. |
| Compile, CookCoverage/package load, PIE | Lead | Pending; Codex did not run these. |

