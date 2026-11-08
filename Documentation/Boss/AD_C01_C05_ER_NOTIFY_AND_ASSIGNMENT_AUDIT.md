# Queue AD AD-C01–C05 — ER review, montage fields, and package boundary

Date: 2026-11-07. Static Source/config/test/mailbox review. No asset edits, Editor, Unreal, build, cook, package, or PIE operation by Codex. Status note: this was written at the C-986 zero-notify point. A-596 later reported authoring; C-988's Lead readback partly rejects that post and assigns four corrections to Antigravity. Fresh Lead verification and owner review/assignment remain open.

## AD-C01 — owner review state

GATE-07 records all four ER clips as delivered for owner review; C-977 sends the four clips to the owner, and no later owner approval appears in the reviewed mailbox through C-986. C-985 is specifically Claude acceptance **for owner review** of A-594's Tier 2 recoil/aura previews, not the owner's final judgment. Aura reads salmon/coral in the unlit preview; final appearance is for owner review in engine. Keep the ER/Tier 2 owner approval gate open.

## AD-C02 — optional fields and assignment paths

| Field | Source and path | Current default/assignment evidence |
|---|---|---|
| `BackstepMontage` | `RPGDodgeTiming.h:99`; tap path `RPGDodgeTiming.cpp:347` | Soft montage reference. `RPGAutomationTests.cpp:1192` asserts null by default. No checked-in content default assignment found in Source, config, or editor scripts. |
| `GuardCounterMontage` | `RPGDodgeTiming.h:106`; successful guarded-contact counter path `RPGDodgeTiming.cpp:497-501` | Soft reference; `RPGAutomationTests.cpp:1193` asserts null. Runtime temporary array override is implementation behavior, not saved field assignment. |
| `AirLightMontage` | `RPGDodgeTiming.h:110`; load/route `RPGDodgeTiming.cpp:54-56,477-481` | Soft reference; `RPGAutomationTests.cpp:1194` asserts null. Startup resolution occurs only when non-null; no checked-in content assignment found. |
| `AirHeavyMontage` | `RPGDodgeTiming.h:114`; load/route `RPGDodgeTiming.cpp:58-60,510-515` | Soft reference; `RPGAutomationTests.cpp:1195` asserts null. Startup resolution occurs only when non-null; no checked-in content assignment found. |

The scan covered `Source/OneBossFight`, `Config`, `Scripts/Editor`, and `Scripts/Tools`. It cannot see unsaved Editor state, so C-985's runtime asset check is separate evidence. C-986 confirms the current five montage assets are present but all have zero notifies; no authoring/assignment is authorized by this source audit.

## AD-C03 — accepted source ranges and montage slices

| Clip | Source / accepted span | Reported montage length | Notify/runtime condition |
|---|---|---|---|
| ER-A1 Backstep | accepted 15 f, 0.4667 s | 0.4667 s | C-986 reports zero notifies; i-frame/cancel behavior unverified |
| ER-A4 GuardCounter | source 50 f / 1.6667 s; F10..F34 = 0.8000 s | 0.8000 s | zero notifies; Lead says no `ANS_CollisionTrace`, so damage is absent until corrected/rechecked |
| ER-A2 AirLight | source 42 f / 1.4000 s; F18..F35 = 0.5667 s | 0.5667 s | zero notifies; current trim does not prove airborne hit attribution |
| ER-A3 AirHeavyPlunge | source 42 f / 1.4000 s; F12..F38 = 0.8667 s | 0.8667 s | zero notifies; current trim does not prove airborne hit attribution |

Range and length evidence is A-584/A-589/A-590 and `GATE07_ANIMATION_REVIEW.md`. These durations are content/readback receipts, not functional acceptance. Lead's C-986 asset check is the present notify baseline.

## AD-C04 — cook coverage

`Config/DefaultGame.ini` includes `/Game/OneBossFight/Player/Animations` in `DirectoriesToAlwaysCook`. This is broad root configuration, not evidence that the current staged package includes each exact assigned montage. BUILD-246 CookCoverage predates the latest animation content, and C-985's null-RHI asset check proves editor loading/class/skeleton/length only, not package contents. After owner approval and saved assignment, Lead must rebuild with Editor closed, run current `OneBossFight.Content.CookCoverage`, inspect staged files/package identity, and exercise each assigned route. No root change is justified by this audit.

## AD-C05 — post-approval checklist

1. Record owner review by exact clip/preview and mailbox ID; keep fields empty until assignment is authorized.
2. Resolve missing C-986 template timelines from Lead `RPGMontageUtils.describe_notifies` output for `Ability_E_Anim_Montage`, chosen hit-react montage, and the Dodge cancel-state template. Use the corrected `AA_A08_NOTIFY_FRAMES_TABLE.md`; do not invent class names or positions.
3. Antigravity authors verified real notify classes under `ENGINE_LOCK`, refuses unexpected asset state, saves, and posts per-montage readbacks.
4. Lead repeats asset validation and PIE: accepted hit/damage on held boss, Backstep iframe and cancel behavior, air-route hit attribution, and safe player fallback. Record build ID, route, logs, montage positions, and outcomes.
5. After approved assignment, Lead captures current cook/package identity and proves the staged build includes and plays the selected montages. Update GATE-07/KI-193 only to the observed scope.

Source/evidence: `RPGDodgeTiming.h/.cpp`; `RPGAutomationTests.cpp:1192-1195`; `Config/DefaultGame.ini`; GATE-07; `Docs/BossCombatReview/Execution/Claude/P_C985_ASSETCHECK/check_lines.txt`; mailbox C-985/C-986; `AA_A08_NOTIFY_FRAMES_TABLE.md`.

## Later readback addendum — A-597

C-986/C-988 content above is the earlier snapshot. A-597 supplies five new Lead montage lines in `Docs/BossCombatReview/Execution/Antigravity/LEAD_CHECK_READBACK.txt`; the C-988 repair criteria now appear in all five. GuardCounter's proposed FootStep row from AA-A08 remains absent, so exact full-table closure is not claimed. Owner review/assignment, PIE, and current cook/package checks remain separate.
