# Queue V — 200 tasks (Codex lane V-C001…V-C100, Antigravity lane V-A001…V-A100)

Written by the lead (Claude), 2026-11-05, after BUILD-228 (476/476), A5 parity complete on 31 drivers, D5 legacy defaults,
parry slow motion witnessed live on both routes, DLSS 4.5 SR integrated (Round 5: best 38 fps, DLSS-active proof pending),
owner decisions J049 = A, A7 = B (retire legacy later), performance UN-PARKED, art Tier 1 created (Tier 2 needs owner review).

## Binding pattern (both lanes)
- C-797: batches of 5; one post per batch (or per Source change, flagged "Source changed" / "PRODUCTION CHANGE"); never wait for
  a verdict between batches; at task 90 of a lane write that lane's next queue (Queue W) and continue.
- C-829: a lead HOTFIX outranks everything; read the mailbox tail before every batch.
- C-820: no status-only, re-check or reconciliation tasks; blocked on the lead or owner -> one line "WAITING ON LEAD/OWNER: <item>"
  then the next unblocked task.
- C-871 compile checklist for C++: grep every class/include/member against its declaration, count #if/#endif, check access
  specifiers and lambda captures, Shipping-only paths compile; Codex never builds, the lead builds.
- C-883 file safety: no deletes under the repo except approved `git rm`; never delete untracked files; back up docs > 50 KB;
  targeted edits only.
- Parity contract: any new data field is OPTIONAL with native defaults equal to today's behaviour (F1-R lesson); default visuals
  unchanged; Development-only switches for previews.
- Commits: Antigravity only, after the lead's verdict, never staging *.webm or Saved/; never commit a red Source tree.
- Look-changing asset edits (lights, materials, level, Tier 2 art) need the owner's yes; cvar/scalability experiments and DLSS are approved.
- Offline suite (`python -m unittest discover -s Scripts/Tools`) green before every post that touches tools.

## Lane C — Codex (engineering, performance, feel)
| ID | Task | Acceptance |
|---|---|---|
| V-C001 | Finish X-1287 follow-ups from the lead's review (T1 receipt mapping, P2a upscaler/screen-percentage telemetry) | lead build green, pie_legend receipts written |
| V-C002 | Round 6 experiment JSON (C-921 P2b): TSR anchor at explicit screen %, DLSS Q/B/P, best DLSS + FireShadows 4/0, FireRadiusScale 0.65, SkyLight capture 0 | dry-run rows, offline test |
| V-C003 | Round 6 pre-flight: every DLSS run must log the active upscaler = DLSS (from P2a), every cvar must exist | guard test |
| V-C004 | Round 6 README prompt (owner Claude) incl. the "no -ExecCmds quoting" lesson from Round 5 | lead review |
| V-C005 | Round 6 intake: per-mode table, delta vs anchor, upscaler proof column, predicted vs measured savings | fixtures |
| V-C006 | DLSS player setting implementation (U-C05p design): Off/DLAA/Quality/Balanced/Performance, TSR fallback on non-NVIDIA, default chosen after Round 6 | PRODUCTION CHANGE, tests |
| V-C007 | Settings persistence for the upscaler choice (GameUserSettings), safe default on load failure | tests |
| V-C008 | NVIDIA Reflex evaluation plan (StreamlineReflex plugin): latency benefit, Shipping redistributables, owner decision brief | brief |
| V-C009 | PSO precache / shader warm-up proposal from the Round 4 hitch analysis (310 ms, 699 ms) | proposal with evidence |
| V-C010 | X- batch | — |
| V-C011 | Scalability "Performance" preset proposal file (not applied) built from Round 5/6 data | diff + ms table |
| V-C012 | Opt-in switch to load that preset for A/B runs (Development) | test |
| V-C013 | Frame-time budget table per system (game thread, render, GPU passes) from Round 5 game logs | table |
| V-C014 | GPU pass breakdown capture plan (ProfileGPU in Development runs) for Round 6 | sheet |
| V-C015 | Shadow cost model: VSM page pool stats per light count (rpg.Perf.FireShadows 0..12) offline from logs | table |
| V-C016 | Cloud/sky: find the real UE 5.5 cvars for volumetric cloud cost (from help output) and propose a test | cited list |
| V-C017 | TSR vs DLSS image-quality checklist (what the owner should look at) | checklist |
| V-C018 | Dynamic resolution feasibility note (UE 5.5 + DLSS) | note |
| V-C019 | Round 6 kit dependency list update + MakeBenchKit test | test green |
| V-C020 | X- batch | — |
| V-C021 | A7-B retirement implementation plan as patch series (from H3), each step behind bUseLegacyStartup | plan |
| V-C022 | Replacement tests for legacy-route-only tests (run on the data route) | suite green (lead) |
| V-C023 | Default-route config design: data route default with legacy fallback key | design only |
| V-C024 | Selection setter caller design for J049-A (menu/level option), asset list for owner approval | list |
| V-C025 | Packaged recovery procedure for the setter route | sheet |
| V-C026 | Parity nightly script: 31 pairs in one command, one report (S23) | dry-run + test |
| V-C027 | Parity report diff tool (two nightly reports) | fixtures |
| V-C028 | Determinism run sheet refresh (U-C07) + comparator edge cases | fixtures |
| V-C029 | Memory soak 50 resets with GC (U-C05 ext) interpretation tool | tool + test |
| V-C030 | X- batch | — |
| V-C031 | A2 montage wiring plan: AM_Boss01_A2 as an OPTIONAL tracker clip with the current montage as default; telegraph pair plan | plan |
| V-C032 | Implement V-C031 (data field + Development preview switch) | PRODUCTION CHANGE, tests |
| V-C033 | Parry slow-motion post-process hook: material parameter collection trigger driven by the Legend scope (no asset change; AG supplies the material) | PRODUCTION CHANGE, tests |
| V-C034 | Phase-two aura hook: optional Niagara + material parameter on phase two (default none) | PRODUCTION CHANGE, tests |
| V-C035 | Boss parry recoil hook: optional montage on parried contact (default none, current hit stop kept) | PRODUCTION CHANGE, tests |
| V-C036 | Audio low-pass/duck hook during parry slow motion (default off) | tests |
| V-C037 | Tier-1 visual preview switch documentation for the owner | one page |
| V-C038 | Cook coverage for every new optional asset path | CookCoverage green |
| V-C039 | Parity check that all new hooks default to no change (31 drivers, sample 5) | lead-run pairs |
| V-C040 | X- batch | — |
| V-C041 | Input latency driver: press-to-montage-start for attack/dodge/parry, both routes | driver + lead run |
| V-C042 | Hit-feel audit (hit stop, shake, sound per hit type) vs design freeze | table |
| V-C043 | Telegraph readability audit: telegraph time vs reaction window per attack | table |
| V-C044 | Phase-two transition audit (60 %, roar, buffs, HUD) | driver checks cited |
| V-C045 | Death/restart flow audit (boss death to victory, player death to respawn) | driver checks cited |
| V-C046 | Camera audit (lock-on distance, collision, boss framing) | table |
| V-C047 | Stamina/poise tuning audit vs design freeze values | table |
| V-C048 | Proposals from V-C041..047 (proposals only) | list |
| V-C049 | KNOWN_ISSUES rows for confirmed defects from V-C041..047 | rows |
| V-C050 | X- batch | — |
| V-C051 | Test-gap audit round 2 (remaining untested surfaces from U-C02/U-C08) | table |
| V-C052 | Tests for the top 5 remaining gaps | lead build green |
| V-C053 | Tests for gaps 6-10 | same |
| V-C054 | Error-path coverage: every HardError/refusal token has a producing test (finish U-C08) | table + tests |
| V-C055 | UE 5.5 deprecation list from the build log and fixes per warning class | lead build |
| V-C056 | Logging verbosity proposal for per-tick LogRPG* (Development only) | table |
| V-C057 | Gate.ps1 full run support for the lead (one JSON receipt) | lead runs once |
| V-C058 | Native suite runtime: slowest 20 tests and cuts | table |
| V-C059 | Test ownership index for the 476 native tests | index |
| V-C060 | X- batch | — |
| V-C061 | Shipping smoke receipt checker on a real Shipping package (lead-run) | sheet |
| V-C062 | Packaged recovery smoke for missing/invalid definition in Development package | sheet |
| V-C063 | Cook manifest check automation in the package script (G044 closure + VFX folder) | test |
| V-C064 | Package size report and top-50 assets | table |
| V-C065 | Proposals to cut package size (list only) | list |
| V-C066 | Crash reporter/symbols plan for owner builds (pdb retention) | plan |
| V-C067 | Build version stamp in the game (build id on screen in Development) | PRODUCTION CHANGE (Dev only) |
| V-C068 | Log retention for packaged runs (game.log per run outside benchmarks too) | test |
| V-C069 | Bench kit rebuild checklist automation | test |
| V-C070 | X- batch | — |
| V-C071 | Data route authoring: second encounter from the legacy baseline (repeatability) | dry-run 0 MISMATCH |
| V-C072 | Intentional-tuning worked example (one field) through validation | example validates |
| V-C073 | D5 audit for the seven ParrySlowMotion leaves (rows in legacy_defaults_g044.json) | audit MATCH |
| V-C074 | Manifest validator rules for optional groups (all-or-none) | tests |
| V-C075 | Encounter definition doc refresh (fields added since D5) | doc |
| V-C076 | Comparator rule audit after AG's U-A04 finding (bracketed state values) — regression set | fixtures |
| V-C077 | Receipt writer: every typed observable label checked against the live log by a test (T1 lesson) | test |
| V-C078 | Driver registration audit refresh (31 + legend L8 + soak + refusal) | table |
| V-C079 | Mailbox digest tool (decisions between two C- ids) | tool + test |
| V-C080 | X- batch | — |
| V-C081 | Round 6 results intake (WAITING ON OWNER until the zip arrives) | report |
| V-C082 | Performance decision brief for the owner from Rounds 1-6 | one page |
| V-C083 | Apply the owner-approved performance settings as data/config (after the owner's yes) | PRODUCTION CHANGE |
| V-C084 | Round 7 confirmation plan (RTX 2060 Super target if available) | sheet |
| V-C085 | Final parity spot-check after performance settings (5 drivers) | lead-run |
| V-C086 | KNOWN_ISSUES sweep after performance work | rows |
| V-C087 | DECISIONS index C-878..C-9xx | lines |
| V-C088 | TEST_PLAN index BUILD-223..23x | links resolve |
| V-C089 | Tools README refresh | links resolve |
| V-C090 | Write Queue W (Codex lane, 50) from what is left | 50 IDs |
| V-C091 | Handover note for the next session (Codex view) | one page |
| V-C092 | Docs consistency pass (PROJECT_STATE, TASKS, TEST_PLAN, KNOWN_ISSUES, DECISIONS) | no contradictions |
| V-C093 | Offline suite timing guard (< 10 s) | measured |
| V-C094 | Review AG lane outputs that touch tools/Source (second reviewer) | per-batch notes |
| V-C095 | Cross-check AG ledger updates against evidence | tool run |
| V-C096 | Bench kit dry-run on the dev PC (no GPU claim) | lead-run log |
| V-C097 | Owner engineering summary (plain language) | half page |
| V-C098 | Risk register refresh (A7-B, performance, art hooks) | table |
| V-C099 | Lane close-out | X- line |
| V-C100 | Continue at Queue W | — |

## Lane A — Antigravity (review, art, content, ledger, commits)
| ID | Task | Acceptance |
|---|---|---|
| V-A001 | Review X-1287 artifacts (T1 receipt fix, P2a telemetry) as second reviewer | notes |
| V-A002 | Ledger: add BUILD-225..228 witnesses (parry slow motion live, H8 rebind, memory soak, W1/H10) | JSON validates |
| V-A003 | Commit the lead-reviewed state after each green verdict | hash |
| V-A004 | Round 6 kit build when the lead says go (DLSS dll check, dependency test) | kit + sha256 |
| V-A005 | A- batch | — |
| V-A006 | Tier 2 art brief for the owner: parry slow-motion post-process, phase-two aura, boss parry recoil, with mock screenshots/mock clips | brief, WAITING ON OWNER for go |
| V-A007 | PPM_ParryDistortion material (NEW asset, after owner go) | asset + log |
| V-A008 | Material parameter collection for the parry effect (NEW asset) | asset + log |
| V-A009 | NS_Boss_PhaseTwoAura (NEW asset, after owner go) | asset + log |
| V-A010 | A- batch | — |
| V-A011 | Boss parry recoil animation via Blender MCP on SK_CombatMannequin (NEW asset, after owner go), 0.6 s | clip + import log |
| V-A012 | Recoil montage asset (NEW) | asset |
| V-A013 | A2 montage notify review (AM_Boss01_A2 commit/active notifies match the tracker row) | table |
| V-A014 | Tier 1 shockwave ring tuning pass (radius 1200 cm, 40 cm band readability) in the preview switch | captures |
| V-A015 | A- batch | — |
| V-A016 | Parry spark tuning pass (direction, count, lifetime) | captures |
| V-A017 | Sword trail proposal (boss + player) with cost estimate | proposal |
| V-A018 | Death dissolve polish proposal | proposal |
| V-A019 | Lateral dodge clips proposal (left/right rolls) | proposal |
| V-A020 | A- batch | — |
| V-A021 | Lighting proposal implementation as cvar profiles only (FireShadows 4 / radius 0.65 / sky capture) for Round 6 | profiles in the experiment JSON (with Codex) |
| V-A022 | Visual diff capture set for each lighting profile (owner-session captures where agent captures are black) | capture list |
| V-A023 | Brazier shadow selection: which 4 braziers keep shadows (gameplay readability) | map + reasoning |
| V-A024 | Light baking feasibility study (static braziers) — proposal only | proposal |
| V-A025 | A- batch | — |
| V-A026 | Material cost audit (shader complexity, overdraw) arena + boss | table |
| V-A027 | Nanite/LOD audit for arena meshes and boss pieces | table |
| V-A028 | VFX cost audit (Niagara systems in the fight) | table |
| V-A029 | Proposals from V-A026..028 with predicted savings | list |
| V-A030 | A- batch | — |
| V-A031 | Owner play-test intake: convert notes into reproducible scenarios | scenario list (WAITING ON OWNER) |
| V-A032 | Animation feel audit: boss anticipation frames vs the 5 measured reference moves | table |
| V-A033 | Player responsiveness audit (cancel windows, blends) | table |
| V-A034 | Audio mix audit (cues, footsteps, music levels) | table |
| V-A035 | A- batch | — |
| V-A036 | Content-script safety fixes for risky writers (U-A12/U-A13 follow-up) | offline tests |
| V-A037 | Map/asset reference integrity census (redirectors, broken soft refs) | report |
| V-A038 | Fix redirectors (after lead approval of the list) | log |
| V-A039 | Unreferenced asset list for owner cleanup (incl. FAG23/SEL008 leftovers) | list |
| V-A040 | A- batch | — |
| V-A041 | Config audit: dead keys in Default*.ini | table |
| V-A042 | Input mapping audit (actions bound/handled) | table |
| V-A043 | Git LFS health check | report |
| V-A044 | .gitignore review (build logs, scratch) | proposal |
| V-A045 | A- batch | — |
| V-A046 | Docs link checker run + fixes | broken_links=0 |
| V-A047 | Onboarding page refresh (DLSS engine plugin install, gate, packaging) | page |
| V-A048 | Release checklist final form | checklist |
| V-A049 | Mailbox archive split (move old months to Documentation/Archive, index, no message edits) | index, lead approves |
| V-A050 | A- batch | — |
| V-A051 | Second review of V-C006/007 (DLSS setting) | notes |
| V-A052 | Second review of V-C031..036 (art hooks) | notes |
| V-A053 | Second review of V-C041..047 (feel audits) | notes |
| V-A054 | Coverage matrix: native tests to the 82 requirements | CSV + validator |
| V-A055 | A- batch | — |
| V-A056 | Tier 2 asset integration check in preview switches (after Codex hooks) | captures |
| V-A057 | Phase-two aura timing vs roar clip | table |
| V-A058 | Recoil clip timing vs parry slow motion window | table |
| V-A059 | Owner review package for Tier 2 (captures + how to toggle) | page |
| V-A060 | A- batch | — |
| V-A061 | Round 6 owner session support (prompt clarifications, intake with Codex) | WAITING ON OWNER |
| V-A062 | Performance summary for the owner (plain language, rounds 1-6) | half page |
| V-A063 | Apply owner-approved lighting changes as assets (only after owner yes) | log + captures |
| V-A064 | Post-change visual diff set | captures |
| V-A065 | A- batch | — |
| V-A066 | Package size proposals review (with V-C064/065) | notes |
| V-A067 | Content folder structure review (/Game/OneBossFight) | proposal |
| V-A068 | Asset naming audit | table |
| V-A069 | Proposals from V-A066..068 | list |
| V-A070 | A- batch | — |
| V-A071 | Ledger final pass for the release candidate | JSON validates |
| V-A072 | Release candidate tag proposal | proposal |
| V-A073 | Commit hygiene check across today's commits (no scratch, no media) | report |
| V-A074 | Witness evidence index (paths per requirement) | index |
| V-A075 | A- batch | — |
| V-A076 | Reference footage: any new measurable clip (only with real frames) | ledger rows or none |
| V-A077 | Reference vs Ember Warden comparison refresh after art changes | table |
| V-A078 | Feel proposals from V-A076/077 | list |
| V-A079 | D5 track doc refresh | links resolve |
| V-A080 | A- batch | — |
| V-A081 | Docs consistency pass with Codex | joint note |
| V-A082 | Archive superseded Boss docs (git mv, index, lead approves the list) | index |
| V-A083 | PROJECT_STATE structure review (KI-186 recovery copies vs current) | diff report |
| V-A084 | Newcomer README (build, run, test, package) | one page |
| V-A085 | A- batch | — |
| V-A086 | Second review of Queue W drafts | notes |
| V-A087 | Owner-facing art summary (what changed, how to see it) | half page |
| V-A088 | Risk register (art/content side) | table |
| V-A089 | Handover note (AG view) | one page |
| V-A090 | Write Queue W (AG lane, 50) | 50 IDs |
| V-A091 | Commit of the lane close-out state | hash |
| V-A092 | LFS/size re-check after art assets | report |
| V-A093 | Captures archive index | index |
| V-A094 | Tier 3 backlog list (post-slice) | list |
| V-A095 | A- batch | — |
| V-A096 | Cross-check Codex docs outputs | notes |
| V-A097 | Final link check | broken_links=0 |
| V-A098 | Final ledger validation | JSON validates |
| V-A099 | Lane close-out | A- line |
| V-A100 | Continue at Queue W | — |
