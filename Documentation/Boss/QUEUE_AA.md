# Queue AA — 100 tasks (Codex AA-C01…AA-C50, Antigravity AA-A01…AA-A50)

Written by the lead (Claude), 2026-11-07, on the owner's instruction to resume the task pattern for both agents. Supersedes HOLD MODE
(C-936) for the tasks below. State: commit 21dbcb18, BUILD-240 GREEN 481/481, offline 377/1 skip, data route is the default
(legacy only as non-Shipping parity control), ER controls (no double-tap long roll; R1 light, R2 tap strong, R2 hold charged)
live, Round 6 Phase 1 intaken (TSR 26.66 / DLSS P 35.19 fps), Phase 2 (DLSS Performance base) running on the benchmark PC.

## Binding pattern (both lanes)
5-task batches; one post per batch (or per Source change, flagged "Source changed"/"PRODUCTION CHANGE"); read the mailbox tail
before every batch; a lead HOTFIX outranks everything (C-829); no status-only or re-check tasks (C-820): blocked -> one line
"WAITING ON LEAD/OWNER: <item>" and take the next unblocked task; at task 45 of a lane write that lane's Queue AB (50) and continue.
C-871 compile checklist (names, includes, access, captures, #if/#endif, Shipping paths). C-883 file safety (no deletes except
approved git rm; never untracked files). New data fields OPTIONAL with today's defaults. Codex never builds; the lead builds, runs
PIE and packages. Antigravity is the only committer, after the lead's verdict, never staging *.webm, Saved/, build_raw.log, kits,
zips, or anything from C:\UnrealProject\Ref. Look-changing asset edits and Tier 2 art need the owner's yes. Bench kits only on D:.

## Lane C — Codex
| ID | Task | Acceptance |
|---|---|---|
| AA-C01 | Finish C-949 Phase 1 receipt (record) | receipt validates |
| AA-C02 | Phase 2 intake tooling ready for the DLSS-Performance base (expected 16 rows, mode witness per run, build ID check) | fixtures from Phase 1 shape |
| AA-C03 | Phase 2 intake doc template (Boss/ROUND6_PHASE2_INTAKE.md skeleton, no numbers) | template |
| AA-C04 | Decision table for the owner: what Phase 2 numbers imply for the DLSS shipped default (60 fps / p99 / image quality) | one page, filled after intake |
| AA-C05 | X- batch | — |
| AA-C06 | Block probe v4 follow-up: classify why the gamepad guard key never produced a block (input mapping, ability activation, tag, state gate) from probe logs + Source | cited finding |
| AA-C07 | Fix proposal for the block finding (test-first, flagged) | proposal / PRODUCTION CHANGE |
| AA-C08 | Guard counter integration plan once blocking works (C-948 open item) | plan |
| AA-C09 | ER hand-test sheet v2 with the block finding | sheet |
| AA-C10 | X- batch | — |
| AA-C11 | Backstep integration readiness: what the code needs from AG's ER-A1 clip (notify names, root motion, length) | checklist |
| AA-C12 | Backstep wiring as an OPTIONAL clip field, current behaviour default | PRODUCTION CHANGE, tests |
| AA-C13 | Guard counter clip wiring readiness (ER-A4) | checklist |
| AA-C14 | Air light / air heavy plunge wiring readiness (ER-A2/A3) | checklist |
| AA-C15 | X- batch | — |
| AA-C16 | DLSS player setting: implementation ready for the owner's default (Off/DLAA/Q/B/P, TSR fallback, persistence) | PRODUCTION CHANGE, tests |
| AA-C17 | Settings menu hook design (where the option lives; no UI asset edits) | design |
| AA-C18 | Non-NVIDIA fallback test (DLSS unsupported path) | test |
| AA-C19 | Shipping behaviour of the setting (no console, ini only) | test |
| AA-C20 | X- batch | — |
| AA-C21 | Phase 2 follow-up experiment set if 60 fps not met (next levers from Phase 2 data) | JSON + dry-run |
| AA-C22 | Shadow/lighting cvar profile as a shippable scalability option (proposal, owner-gated) | proposal |
| AA-C23 | Hitch: PSO precache feasibility from Round 4/5/6 hitch frames | proposal |
| AA-C24 | GPU budget table refresh with Round 6 data | table |
| AA-C25 | X- batch | — |
| AA-C26 | Legacy route: code paths still reachable only via the parity control (list, A7-B removal later) | table |
| AA-C27 | Parity nightly one-command run (31 pairs) refresh for the data-default world | dry-run |
| AA-C28 | Default-route regression tests (data route default, legacy control non-Shipping) | tests |
| AA-C29 | Selection setter caller design (J049-A) for the owner | design |
| AA-C30 | X- batch | — |
| AA-C31 | Input latency driver for the new ER controls (press to montage start) | driver + lead run |
| AA-C32 | Charged attack timing audit (R2 hold threshold vs montage) | table |
| AA-C33 | Dodge feel audit after removing double-tap long roll | table |
| AA-C34 | Proposals from AA-C31..33 | list |
| AA-C35 | X- batch | — |
| AA-C36 | Test-gap audit round 3 (new ER code) | table |
| AA-C37 | Tests for the top gaps | lead build |
| AA-C38 | UE 5.5 deprecation fixes from the latest build log | lead build |
| AA-C39 | Offline suite timing guard (< 10 s) | measured |
| AA-C40 | X- batch | — |
| AA-C41 | Packaged smoke sheet for the data-default Shipping build | sheet |
| AA-C42 | Cook check for any new optional assets (ER clips, Tier 2) | CookCoverage |
| AA-C43 | KNOWN_ISSUES sweep (ER, Round 6) | rows |
| AA-C44 | DECISIONS index C-923..C-95x | lines |
| AA-C45 | Write Queue AB (Codex, 50) | 50 IDs |
| AA-C46 | Docs consistency pass | no contradictions |
| AA-C47 | Owner engineering summary (plain language) | half page |
| AA-C48 | Second review of AG tool/Source outputs | notes |
| AA-C49 | Handover note | one page |
| AA-C50 | Lane close; continue at AB | X- line |

## Lane A — Antigravity
| ID | Task | Acceptance |
|---|---|---|
| AA-A01 | Commit the reviewed pending items of C-947, C-949, C-950 (Package.ps1, RunPerfExperiments.ps1, MakeBenchKit.ps1, Codex's X-1353 test files, the listed docs and evidence folders B_C946_A573, B_C947_R6KIT); post the hash | hash, no excluded files |
| AA-A02 | ER-A1 Backstep_Back clip (Blender; spec ER_PLAYER_CONTROLS_SPEC.md section 3): FBX + look render + notify frames | delivered under Docs/.../Antigravity/ER_ANIM/ |
| AA-A03 | ER-A4 Attack_GuardCounter clip | same |
| AA-A04 | ER-A3 Attack_Air_Heavy_Plunge clip | same |
| AA-A05 | A- batch | — |
| AA-A06 | ER-A2 Attack_Air_Light clip | same |
| AA-A07 | Import script for the ER clips into /Game/OneBossFight/Player/Animations (NEW assets, refuse-if-exists, assert-before-save) | script + log |
| AA-A08 | Notify frames table per clip vs the code's expected notify names (with Codex AA-C11..14) | table |
| AA-A09 | Look renders review set for the owner | page |
| AA-A10 | A- batch + commit | hash |
| AA-A11 | Tier 2 art option brief (A/B/C, lead recommends B) refresh with captures | brief, WAITING ON OWNER |
| AA-A12 | Tier 2 assets for the owner's chosen option (after the owner's yes) | assets + logs |
| AA-A13 | Parry slow-motion post-process material (Tier 2, after yes) | asset |
| AA-A14 | Phase-two aura (Tier 2, after yes) | asset |
| AA-A15 | A- batch | — |
| AA-A16 | Boss parry recoil clip (Tier 2, after yes) | clip |
| AA-A17 | Tier 1 effects tuning pass (shockwave ring, parry spark) in the preview switch | captures |
| AA-A18 | Visual diff capture set (owner-session where agent captures are black) | list |
| AA-A19 | 14 unreferenced assets list refresh for the owner | list, WAITING ON OWNER |
| AA-A20 | A- batch | — |
| AA-A21 | Round 6 Phase 2 kit support: verify the return zip's build IDs and mode witnesses with Codex's tool when it arrives | report |
| AA-A22 | Lighting profile captures for the Phase 2 combos | captures |
| AA-A23 | Brazier shadow selection rationale (which keep shadows) | map + reasoning |
| AA-A24 | Performance summary for the owner (rounds 1-6) | half page |
| AA-A25 | A- batch | — |
| AA-A26 | Ledger update for BUILD-235..240 witnesses (data default, ER controls) | JSON validates |
| AA-A27 | Coverage matrix: native tests to requirements (refresh) | CSV + validator |
| AA-A28 | Second review of Codex AA-C06..C16 (block finding, ER wiring, DLSS setting) | notes |
| AA-A29 | Content-script safety fixes (risky writers list) | offline tests |
| AA-A30 | A- batch + commit | hash |
| AA-A31 | Reference video study follow-up: ER control timing references (ER_REFERENCE_VIDEO_STUDY.md), measured only with frames | rows or none |
| AA-A32 | Animation feel audit for the new ER clips vs reference | table |
| AA-A33 | Audio for the new player moves (cue list, existing assets) | list |
| AA-A34 | Proposals from AA-A31..33 | list |
| AA-A35 | A- batch | — |
| AA-A36 | Map/asset reference integrity census | report |
| AA-A37 | Config/input mapping audit after the ER input mapping context | table |
| AA-A38 | Git LFS health check | report |
| AA-A39 | Docs link check + fixes | broken_links=0 |
| AA-A40 | A- batch + commit | hash |
| AA-A41 | Onboarding refresh (DLSS engine plugin, D: bench kits, data-default route) | page |
| AA-A42 | Release checklist update (GATE-04, GATE-07 status) | checklist |
| AA-A43 | Owner-facing art summary | half page |
| AA-A44 | Risk register (art/content) | table |
| AA-A45 | Write Queue AB (AG, 50) | 50 IDs |
| AA-A46 | Second review of Queue AB drafts | notes |
| AA-A47 | Final link check | broken_links=0 |
| AA-A48 | Ledger validation | JSON validates |
| AA-A49 | Handover note | one page |
| AA-A50 | Lane close; continue at AB | A- line |
