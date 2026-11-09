# AX-C36–C40 — KI-189–193 evidence reconciliation

Status: offline source and documentation audit complete. No code, asset, package, test, Editor, or runtime changes were made.

## AX-C36 — KI-189 first-use soft loads

KI-189 tracks the W1 Tier 1 shockwave/parry spark hooks, not the separate Tier 2 aura/recoil component. W1's authored refs default empty; with an empty ref, Development-only `rpg.Art.Tier1` (default 0) selects the preview fallback, while authored refs take priority (`W1_TIER1_NIAGARA_WIRING.md:3-16`; `RPGBossShockwave.h:59-62`; `RPGPlayerParry.h:32-37`). `RPGTier1VisualRules.cpp:39-50` returns before loading when the selected path is null, otherwise synchronously loads it; callers are `RPGBossShockwave.cpp:64-68` and `RPGPlayerParry.cpp:166-170`. Thus an opted-in first event can synchronously load a fallback asset, but the default-empty/default-off path makes no extra spawn/load; no first-use hitch measurement is cited. The separate `RPGTier2BossPresentation` has its own `rpg.Art.Tier2` gate and a constructor-set aura path (`RPGTier2BossPresentation.cpp:15-19,26-50`); that is not evidence about W1's Tier 1 fallback. KI-189's status and suggested Lead timing check remain accurate (`KNOWN_ISSUES.md` KI-189). No preload change is proposed absent timing evidence.

## AX-C37 — KI-190 owner policy boundary

The bounded policy question and alternatives are in `AR_C26_C30_KI190_STAMINA_SCOPE.md:22-40`. Freeze v1.2 §20.1 specifies JumpHeavy=35, not a universal all-swing rule (`:7-11`). Current Claymore defaults use pack-base `-1` for Light/JumpLight and 35 on Strong/Charged/JumpHeavy/Knockdown; the retained Strength observations cover only their logged cases, not owner policy (`:9,17-20`). No owner answer or selected option appears in the mailbox through X-1652. KI-190 correctly remains open; do not change rows, elevate a proposal into a decision, or claim the prepared audit question was sent as an owner email.

## AX-C38 — KI-191 aura gates

The evidence layers remain distinct in `AN_C26_C30_TIER2_EVIDENCE.md:14-26`, `AO_C16_C20_AURA_COMPARISON_AUDIT.md` and `AS_C36_C40_KI191_FOLLOWUP.md`. C-1042 lifecycle checks concern the focused transient component; A-637/C-1053 says the aura was not visible in the retained full-fight video. C-1075 accepts A-646's candidate authoring readback but reports failed paired output (black data captures and inactive legacy candidate); C-1077 reports the hotfixed paired run also black on both routes, while a separate three-option showcase was sent to the owner. That showcase is not a successful paired comparison or an owner disposition. The static phase-order difference recorded in AO is explicitly a hypothesis, not a root cause. KI-191's PARTIAL status and distinct visual, first-use, and package gates remain supported; no capture rerun is needed for this audit.

## AX-C39 — KI-192 route provenance

C-1099 says an unset `H019_ENCOUNTER_DEFINITION` selects `route=data`; true legacy requires `RPG_LEGACY_STARTUP=1` or `-RPGLegacyStartup` and a same-run activation witness (`TEAM_MAILBOX.md:26633-26643`; `C1099_ROUTE_PROVENANCE_CORRECTION.md:5-9`). C-1100 reports DATA x10 and explicitly witnessed LEGACY x5; the ~0.36-second boundary is tick-quantized on both, with no threshold change (`TEAM_MAILBOX.md:26645-26646`; `AR_C31_C35_KI192_RERUN.md:49-63`). Current KI-192 status is accurately CLOSED for this bounded PIE timing check and OPEN for package proof (`KNOWN_ISSUES.md` KI-192). Do not call an unset-selection arm true legacy or infer package/device-latency evidence.

## AX-C40 — KI-193 defaults and package boundary

The four ER montage Source defaults and C-1042's no-runtime-assignment both-route hit observations are separated from older runtime-assigned C-1004 evidence in `AN_C16_C20_DEFAULT_ATTACKS_AUDIT.md:7-20`. `Scripts/Tools/er_tier2_required_cook_assets.txt` enumerates eight exact package IDs, while the checklist in `AN_C31_C35_PACKAGE_GATE.md:13-30` requires a same-build cooked manifest and separate packaged-runtime exercise. Source directory coverage and PIE do not prove staged asset inclusion or packaged behavior. KI-193's PARTIAL/package-open disposition in `KNOWN_ISSUES.md` is accurate; no manifest, cook, or package result was introduced by this audit.

## Validation and limits

Read-only reconciliation against current source, issue rows, existing reports, and mailbox posts through X-1652. No tests or engine operations were run. No owner option, runtime outcome, package result, or visual acceptance is inferred. The working tree contains concurrent changes outside this batch; this report and the AX queue/TASKS additions are additive.
