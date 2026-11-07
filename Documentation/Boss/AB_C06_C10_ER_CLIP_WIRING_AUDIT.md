# AB-C06–C10 — ER clip wiring audit

Date: 2026-11-07. Static review only. Engine lock remains Antigravity-owned; no imports, asset edits, Editor, build, or PIE.

## C06 — optional fields and redirects

Current player component exposes optional `TSoftObjectPtr<UAnimMontage>` fields for `BackstepMontage` and `GuardCounterMontage`; both are asserted empty by `Content.PackWiring`. No dedicated ER air-light or air-heavy montage fields were found. No class/property redirect for these fields appears in project config. Backstep empty defaults to existing pack dodge behavior; GuardCounter empty/missing keeps the pack strong attack. Air actions are not yet wired to the delivered ER clips.

## C07 — clip metadata versus runtime contract

| Clip | Metadata timing | Code integration | Status from C-968 |
|---|---|---|---|
| Backstep_Back | 0.467 s; RecoverEnd frame 14; backward root motion | Optional montage field exists; no new notify-name consumer. | Rejected; R4 must remove roll/keep feet under pelvis. |
| Attack_GuardCounter | 0.800 s; windup 0.300; hit 0.333–0.533; impact 0.433; recover 0.800 | Optional montage field exists. Counter opportunity is driven by successful-block timestamp and proposed 0.60 s input window, not clip notifies. | Import permitted only; owner video review and Lead build/PIE still gate acceptance. |
| Attack_Air_Heavy_Plunge | 0.867 s; airborne windup 0.200; hit 0.367–0.533; landing impact 0.500; recover 0.867 | No dedicated optional field or airborne notify consumer found. | Rejected; R4 required. |
| Attack_Air_Light | 0.567 s; airborne windup 0.133; hit 0.200–0.333; impact 0.233; recover 0.567 | No dedicated optional field or airborne notify consumer found. | Rejected; R4 required. |

The authored timings are metadata values, not proof of UE montage notify tracks. Current code applies pack attack/dodge montages; no code maps these clip milestones into hitbox windows. The control spec and GATE-07 must distinguish author metadata from runtime behavior.

## C08 — fail-closed behavior

- Backstep field null/unloadable: continue existing pack dodge route.
- GuardCounter field null/unloadable or reflection/array match fails: still inject normal pack strong attack; no dedicated counter montage is claimed.
- Air clips: no optional route exists yet, so current jump actions remain on existing pack behavior.
- Importer: refuses existing assets and checks class/skeleton/duration before save, but imports only `AnimSequence` assets. Current runtime fields accept `UAnimMontage`, so the output cannot be assigned to either optional montage field as written. An explicit, new-only AnimSequence-to-Montage creation/verification step or an approved Source type change is required before wiring. Do not infer that import success equals runtime readiness.
- Importer also defaults to all four clips when `IMPORT_CLIP_FILTER` is unset. Since three are rejected by C-968, use an allowlist/fail-closed guard before any broad import.

## C09 — buffering and airborne route

The inspected component binds only the ER light and heavy ground actions, then injects the pack light/strong actions for a short authored interval. It does not bind jump-light/heavy actions, inspect airborne state, or clear an airborne attack buffer; current airborne attacks are not established by this component. Existing pack buffering and aerial eligibility are outside this component and need a Lead runtime trace before making behavior claims. Hand-test rows correctly remain pending clip approval/wiring.

## C10 — offline metadata validator proposal

Schema per clip: `clip_id`, `asset_name`, `source_fbx`, `skeleton_path`, `asset_kind_expected`, `duration_seconds`, `frame_rate`, `frame_count`, `looping`, `root_motion_mode`, `root_delta_cm`, `notify_events[]` (`name`, `frame`, `seconds`), `review_video`, `strip_image`, `lead_verdict`, `owner_video_review`, and `runtime_field`. Validator should reject duplicate clip IDs/assets/events, unsafe/nonexistent paths, duration/frame mismatch beyond one frame, notify frames outside `0..frame_count-1`, and any `lead_verdict` other than import-authorized before an import manifest is generated. Fixtures: valid GuardCounter manifest; rejected Backstep; unknown notify; duplicate asset name; duration/frame mismatch; wrong expected asset kind; missing video; traversal path; and broad-import request with rejected clips. It must not invoke Unreal or write Content.

## Current registry correction

`GATE07_ANIMATION_REVIEW.md` labels all four rows “DELIVERED (R3)” but omits C-968's subsequent acceptance/rejection. Row labels were corrected to reflect the Lead verdict and to separate delivery from acceptance. Owner video review remains a required gate for all clips.
