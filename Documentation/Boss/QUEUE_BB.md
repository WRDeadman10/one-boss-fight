# Queue BB: 50 + 50 tasks (owner order 2026-11-10: "do the 50 task pattern with both")

Two lanes: Codex `BB-X01..X50`, Antigravity `BB-A01..A50`.

**Rules (same as earlier queues)**
- Work in 5-task batches and post one `X-`/`A-` message per batch.
- Do NOT wait for review: after posting a batch, start the next one immediately. At the next post, first read the Lead verdict on the previous batch and fix any HOTFIX items first.
- A task that is blocked is marked `BLOCKED (reason)` and skipped. "PAUSED" only if everything left is blocked.
- At task 45, each lane writes its own next 50 (`QUEUE_BC.md`, same format) and continues after task 50 without waiting.
- Audits report file:line with BUG / RISK / OK plus a failing scenario.
- Standing rules still apply:
  - C-1155 engine lock;
  - UE 5.5 Python calls must be proven in this repo or guarded;
  - never write pack assets;
  - new data fields are optional with today's defaults;
  - Shipping-excluded test hooks only;
  - Antigravity commits locally after a Lead verdict, never pushes, and never stages media.
- The Lead runs every live PIE run, acceptance build and asset-authoring run.

## Codex lane (engineering)

| ID | Task | Acceptance |
|---|---|---|
| X01 | C-1265a: finish `author_greystone_player.py` in real-asset mode under `/Game/OneBossFight/Player/Greystone/` (readback after save/reload; on failure delete only the assets this run created) | READY + script; the Lead runs it |
| X02 | Decision 1: update SWITCH_PLAN Phase 3 and `pie_greystone_root_motion.py` to a single-tap directional quick roll (215–290 cm) and backstep (84–98 cm), paired within 10% | Driver + doc diff |
| X03 | C-1265b: test-only per-frame trace log of `weapon_r`→`root_weapon_end_r` for Swing1/2_Medium over the whole clip, with distance to the player capsule | Self-test log |
| X04 | From X03: propose S1/S2 `MaxRangeCm` (and windows if needed); recompute punish margins with the bridge | Numbers + validator output |
| X05 | Apply the Lead-approved S1/S2 values in `author_sevarog_draft_cards.py` (dry-run PASS) | Dry-run log |
| X06 | Teardown fix: `RPGIFrameMonitor` EndPlay leaves `Status.Invulnerable` on a failed removal (X-1784 item 14) | Fix + native test |
| X07 | Teardown fix: `RPGPlayerParry` EndPlay leaves `Status.ParryActive` after 5 retries (item 15) | Fix + native test |
| X08 | KNOWN_ISSUES entry for proof-hook state not reset (X-1783 item 7), dev-only | Doc |
| X09 | Root-cause `Framework.Nav.MoveFailed` on path completion (out-of-band approach) | Diagnosis doc with file:line |
| X10 | Fix X09, behind a test where possible; no map edit without the Lead | Fix + test, or BLOCKED with reason |
| X11 | Sevarog S6 Ultimate_Swing_120fps card (marks C1242: tell 0–0.6, active 0.667–0.867); provisional values; dry-run | Dry-run PASS |
| X12 | Design doc: reusable data-driven **area-effect add-on** (ground AoE at a card time: radius, delay, damage, snare) for Subjugation | Doc |
| X13 | Design doc: reusable **channel/drain add-on** (cone, tick damage, heal-to-boss, interrupt rules) for Soul Siphon | Doc |
| X14 | Plan: Sevarog phase pools (which cards per phase) on the existing selector, with no new code | Doc |
| X15 | Plan: map Sevarog Stun_Start/Loop/End onto the existing stagger profile driver (X-1763 says it exists) | Doc with file:line |
| X16–X20 | Implement the area-effect add-on test-first: struct (optional, default off), executor hook, validator rules, native tests, doc | Build + suite |
| X21–X25 | Implement the channel/drain add-on test-first: same five steps | Build + suite |
| X26 | Sevarog S7 Subjugation and S8 Soul_Siphon card rows using the add-ons; dry-run | Dry-run PASS |
| X27 | Test-only selection of a Sevarog encounter on the data route (CVar, default off; default encounter unchanged) | Build + suite |
| X28 | Autonomous fight driver: Sevarog's selector chooses cards against a scripted player (no forced StartCard); logs selections, hits, punish windows | Driver; the Lead runs it |
| X29 | Sevarog boss HUD / health bar binding check for the framework boss | Audit or fix |
| X30 | Sevarog death: framework boss death → encounter end path audit | Audit |
| X31 | Greystone: automated readback test of the saved wrappers' notifies (vs the source table) | Test |
| X32 | Greystone: sword trace sockets on the child (mesh sockets from `copy_sockets_to_greystone.py`) → hit + parry check driver | Driver |
| X33 | Greystone: flask, hit-react and death routes check driver (no new behaviour) | Driver |
| X34 | Greystone: rollback test, `rpg.GreystonePlayerTestPawn 0` returns to the mannequin cleanly | Test |
| X35 | Greystone: CookCoverage for the child and wrappers once they exist | Suite |
| X36 | Audit: parry on Sevarog swings (pack parry contact route vs framework boss) | Audit |
| X37 | Audit: damage resolver parity, framework boss vs pack boss (block/parry/i-frames) | Audit |
| X38 | Audit: Shipping exclusion of every `...ForTest` hook added since C-1229 | Audit + test |
| X39 | Executor tick cost sanity (no per-tick allocations in hot paths) | Audit |
| X40 | NEW_BOSS_CHECKLIST: annotate with the real Sevarog evidence path (C-1239..C-1266) | Doc |
| X41–X44 | Test hardening: property sweeps for both add-ons and the forward-defense rule | Suite |
| X45 | Write `QUEUE_BC.md` (Codex lane, next 50) | Posted |
| X46–X50 | Closeout: TASKS/TEST_PLAN/KNOWN_ISSUES sync; open-issue digest | Docs |

## Antigravity lane (offline: review, content specs, docs, commits)

| ID | Task | Acceptance |
|---|---|---|
| A01 | C-1265c: hammer direction at the strike frames, Swing1/2_Medium (frame-cited) | Doc |
| A02 | C-1265d: owner review-clip plan for Sevarog's live moves + ffmpeg stitch command (output on D:) | Doc |
| A03 | Greystone owner review-clip storyboard (8 slots from C1257C), with the capture list for the Lead | Doc |
| A04 | Local commit of everything accepted up to C-1266 (no media, no push) | Commit receipt |
| A05 | SFX: Batch 8/9 kept ready; list exactly what is blocked on the owner's reel picks | Doc |
| A06–A08 | From the frame sheets: refine Ultimate / Subjugation / Soul_Siphon marks (tell, release, recovery), frame-cited | Doc |
| A09 | Stun_Start/Loop/End frame notes (vulnerable window candidates) | Doc |
| A10 | LevelStart intro + Death_front frame notes | Doc |
| A11–A13 | SFX spec for Sevarog cards from `/Game/ParagonSevarog/.../Sounds` (whoosh/impact per card, cue names verified on disk); contract test | Spec + test |
| A14 | Sevarog voice-bark candidates (Dialogue waves on disk) per event (intro, phase, kill); spec only | Spec |
| A15 | Read-only guarded probe spec for the Greystone materials/textures the child uses (the Lead runs it) | Script + test |
| A16–A18 | DECISIONS entries for today: C-1250 values, C-1251 forward-defense rule, C-1265 roll gate + real-asset wrappers, C-1261 G0 policy | Doc |
| A19 | KNOWN_ISSUES sync with X-1783..X-1806 findings | Doc |
| A20 | Local commit of A06–A19 | Commit receipt |
| A21–A23 | Ember A2 full composite montage plan (Raise+ApexHold+Slam): sections, notify plan, timings. PLAN ONLY (a look change needs the owner's yes) | Doc |
| A24 | Sevarog phase-2 aura candidates (per-boss `PhaseTwoAuraEffect`), spec only | Doc |
| A25 | Arena space review for the Sevarog fight (nav coverage, dash lanes 3–6.5 m), using the X09 findings | Doc |
| A26–A30 | Evidence index: one table of every Lead/Codex evidence folder since C-1227 with its verdict and TEST_PLAN row | Doc |
| A31–A35 | Owner progress digest draft (short bullets, decision-first, per the owner email format); held for the Lead to send | Draft |
| A36–A40 | TEST_PLAN hygiene: dedupe and index; link check | Doc |
| A41–A44 | Commits of accepted work (receipts) | Receipts |
| A45 | Write `QUEUE_BC_AG.md` (next 50) | Posted |
| A46–A50 | Closeout docs | Docs |
