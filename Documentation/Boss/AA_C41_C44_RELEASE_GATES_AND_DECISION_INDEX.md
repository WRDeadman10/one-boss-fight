# AA-C41–C44 — package smoke, cook coverage, issue sweep, decision index

Date: 2026-11-07. Static review only. Codex did not launch Unreal, cook, package, or build.

## AA-C41 — data-default Shipping smoke sheet

Run only against a Lead-produced Shipping stage after the Source build and package identity are recorded. `Scripts/PackagedSmoke.ps1 -Configuration Shipping -ExePath <staged-exe>` launches with `-nosound`, checks that the process remains alive for its configured interval, terminates the process tree, and checks the staged Shipping binary for debug-name leakage. A PASS means **alive + scanner clean**; Shipping logging is compiled out, so this does not prove arena load, data-default route selection, controller input, boss combat, or a 60 FPS / p99 target. Preserve the script output, executable hash, package/build ID, route witness, and a separate gameplay capture. Development smoke uses `CheckPackagedLog.ps1`; it is a different check.

Prerequisites: ENGINE_LOCK absent; Lead confirms Editor closed before packaging; use the same staged build ID for smoke and gameplay evidence. The owner/Lead must run the game-level checks. No stage or executable was created by this audit.

## AA-C42 — cook coverage

`DefaultGame.ini` already includes `/Game/OneBossFight/VFX` and `/Game/OneBossFight/Boss`, matching the Tier 2 distortion and boss aura/recoil content roots documented by AA-C20. The ER import target is `/Game/OneBossFight/Player/Animations`, which is not an explicit always-cook root. At review time the import lock is held for `AN_ER_Attack_GuardCounter`; therefore no CookCoverage result can be claimed here. Native `OneBossFight.Content.CookCoverage` scans hard-coded Source `/Game` paths; it does not itself prove that future optional soft-reference assets are present in a package. After accepted clips are imported and assigned, Lead should build/run CookCoverage and verify the staged package includes each assigned optional asset. Do not broaden the cook root before clip acceptance and a package-size review.

Evidence: `Config/DefaultGame.ini:25-38`; `Source/OneBossFight/Tests/RPGAutomationTests.cpp:1326-1348`; `Documentation/Boss/AA_C20_TIER2_PRESENTATION_HOOKS.md`; `Scripts/Editor/import_er_clips.py`.

## AA-C43 — current issue sweep

- KI-191 remains open: Tier 2 material preloads only when the Development switch is enabled at BeginPlay; authored-asset startup and visual checks await Lead PIE.
- KI-192 remains open: Lead's two-route 0.34/0.35/0.36/0.70 s input probe is pending; the result is game-tick bounded, not physical device latency.
- KI-193 added below: ER clip acceptance/import is partial. C-968 permits only GuardCounter import; Backstep and both air clips require R4 motion fixes/review. ENGINE_LOCK is currently owned by Antigravity for the GuardCounter import.
- Round 6 Phase 2 and benchmark-dependent DLSS default remain parked by the owner (C-954/C-956); Phase 1 numbers are historical intake, not completion of GATE-04.

## AA-C44 — Claude decision index

This is a navigation index, not a replacement for mailbox evidence. Earlier C-923–C-934 entries are indexed in `Documentation/DECISIONS.md` under “Claude mailbox decision index C-878–C-929” and the following C-931–C-934 bullets. New entries:

| Mailbox | Decision / order |
|---|---|
| C-935 | Review W lane batches and reconcile HOLD status. |
| C-936 | Clarify 80 witnessed / 2 partial; owner-closed decisions are not witnesses. |
| C-937 | Accept X-1350 parity validator hotfix after retained-pair checks. |
| C-938 | End HOLD for work on ER-style controls. |
| C-939–C-940 | ER-C1 optional backstep plumbing; BUILD-235 green. |
| C-941–C-942 | Retire legacy startup by owner decision; ER-C2 dodge rules and BUILD-237. |
| C-943 | Study owner reference videos and inform control design. |
| C-944–C-945 | Owner chooses guard counter, charged hold, and no double-tap long roll; records control mapping/PIE evidence. |
| C-946 | ER-C5 guard-counter rule acceptance and source/content wiring. |
| C-947 | Accept commit 21dbcb18; BUILD-240 green. |
| C-948 | R6b kit delivery and control/block-probe follow-up. |
| C-949–C-951 | Phase 1 evidence, intake/build identity, and owner-selected Phase 2 Performance/50% treatment. |
| C-952 | Owner's Option A Tier 2 art decision; opt-in Development preview with empty defaults. |
| C-953 | Owner confirms guard works; probe defect, 14 asset handling direction, video review requirement for animation. |
| C-954 | Bench testing parked; do not choose shipped DLSS default pending resumed measurement. |
| C-955 | Queue AA and Tier 2 hook order; guard-counter integration unblocked. |

Source: `Documentation/TEAM_MAILBOX.md` entries C-935–C-955. Queue and implementation status may evolve; this index records the mailbox order, not later acceptance.
