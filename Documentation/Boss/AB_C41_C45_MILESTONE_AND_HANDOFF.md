# Queue AB AB-C41–C45 — current gates, receipts, issue dispositions and next lane

Mailbox reviewed through A-591 and Codex X-1384. Snapshot is 2026-11-07; mailbox receipts remain authoritative if later evidence changes.

## AB-C41 — milestone gate matrix

| Gate | Status | Owner | Evidence | Next action |
|---|---|---|---|---|
| Round 6 Phase 2 / shipped DLSS default | PARKED by owner (C-954); no Phase 2 return bundle is recorded | Owner/benchmark operator | `ROUND6_PHASE2_INTAKE.md`; owner decision indexed in `DECISIONS.md` | Resume only when owner un-parks testing and bundle returns; keep TSR shipped default |
| Tier 2 art Option A | Owner-selected; A-591 reports assets created; A-592 supplied preview evidence, acceptance review and Lead runtime verification pending | Claude, then Lead | C-980/A-591/A-592; empty-default Development hooks in BUILD-242/C-978 gate record | Claude reviews preview evidence; Lead verifies opt-in visuals after acceptance; keep default references empty |
| ER-A1 Backstep | Delivery accepted for owner review; montage trimmed/read back to 0.4667 s; owner video review and field assignment pending | Owner, then Lead | C-977, A-589/C-979; GATE-07 | Owner reviews video; if approved, Lead assigns optional field and runs standing/moving/repeat cases |
| ER-A2/A3 air attacks | Delivery accepted for owner review; A-590 reports both montage trims match accepted lengths (0.5667/0.8667 s); owner video review and field assignment pending | Owner, then Lead | C-972/C-977/C-979, A-590 | Owner reviews; Lead assigns only after approval and verifies routes |
| ER-A4 GuardCounter | Import-only acceptance; montage trimmed/read back to 0.8000 s; owner review/field assignment pending | Owner, then Lead | C-968, A-589/C-979; BUILD-248 484/484 | Owner reviews video; Lead assigns optional field and runs actual block-contact counter test |
| Air montage array restoration | VERIFIED by Lead for tested routes | Lead | C-978 / `P_C978_AIRRESTORE/`: legacy and data; air R1/R2 followed by grounded routes | Retain route receipts; scope excludes death/reset teardown and saved-asset assignment |
| Guard control input | Owner-confirmed working; old three probes invalid | Lead for corrected probe; owner for clip review | C-953; AA-C06 classification | Repair probe starting state/weapon evidence; no change to game guard behavior from old probes |
| Player death/reset with attack montage active | UNVERIFIED coverage gap | Lead | Source/test map in AB-C36–C39 report | Capture death/reset live path or add lifecycle test before claiming cancellation/cleanup |

## AB-C42 — test/build receipt reconciliation

| Receipt | Count/result | Scope |
|---|---|---|
| BUILD-246 | 482/482; CookCoverage success | C-973, accepted importer/cook-root work |
| BUILD-247 | 483/483 | C-975, optional AirLight/AirHeavy source routes |
| BUILD-248 | 484/484; Shipping target compiles | C-978, editor-only montage segment helper and corrected native authoring fixture |
| PIE ER-AIR-FIELDS | Both routes; runtime-only optional air assignment played air montages, grounded baseline routes remained | C-975; not saved-field assignment |
| PIE ER-AIR-RESTORE | Both routes; after each air route, grounded R1=Attack_PrimaryA and R2=Ability_E | C-978; verifies array restoration for tested sequence |
| Antigravity offline suite | 417 OK, 1 skipped, broken_links=0 | A-589; separate from native BUILD-248 count |
| Antigravity offline suite (newer report) | 419 OK, 1 skipped, broken_links=0 | A-590; supersedes A-589's earlier suite count, separate from native BUILD-248 count |
| Codex importer fixture | 9/9 pass | X-1383; includes affirmative-prefix and NOT/PENDING/UN- rejection cases |
| Tier 2 asset creation | MPC_CombatFeedback, PPM_ParryDistortion, NS_Boss_PhaseTwoAura, AN/AM_Boss01_ParryRecoil saved under lock | A-591; creation receipt only, no runtime acceptance |
| Offline suite wall-time | 9.2 s during a build against the former 10 s budget | C-978; Codex raised default budget to 20 s; no post-change full-suite timing claimed |

The 482→483→484 counts are successive native build receipts, not competing baselines. A-590's 419/1 figure is the newest Antigravity offline Python suite receipt; it supersedes A-589's 417/1 and is not native automation. Codex did not run the Unreal build or PIE.

## AB-C43 — KNOWN_ISSUES ER/settings sweep

- **KI-192:** replaced stale “no adjacent sample” claim with C-971's measured 0.36 s route split (legacy charged vs data strong, tick-quantized); keep open without changing the mapping.
- **KI-193:** replaced pre-BUILD-248 state with current C-978/A-589/C-979 montage/build receipts. Keep open only for owner video review and saved-field assignment.
- **KI-194:** close for the tested post-air R1/R2 restoration sequence after C-978. Scope explicitly excludes death/reset teardown and saved field assignment.
- **KI-191:** remain open; Tier 2 parry material load/application remains unverified. Owner selected Option A, but selection is not delivery or runtime acceptance.
- **KI-190:** remain open pending stamina design clarification; no guess from asset/control work.
- **KI-195:** remain open; 20 s suite budget reduces timing false failures but does not add subprocess timeouts.

The ER entries are distinct: KI-193 is owner review/assignment; KI-194 was post-air route restoration and is now resolved within C-978's tested boundary. No duplicate issue was deleted.

## AB-C44 — DECISIONS index refresh

The Claude mailbox decision index in `Documentation/DECISIONS.md` now extends through C-979. New concise entries record:

- **C-976:** accept R6 legs, reject its upper body; request R7 upper-body revision; continue GuardCounter trim/Tier 2 and commits.
- **C-977:** accept Backstep R7 for owner review; send all four clips for owner video review; correct the sword observation to straight up/out of frame; import/create unassigned Backstep montage.
- **C-978:** accept X-1380/X-1381/A-588; BUILD-248 484/484 and Shipping compile; Lead confirms post-air array restoration; require 20 s offline-suite budget; Antigravity to trim Backstep and GuardCounter montages.
- **C-979:** accept A-589 trim readbacks; request air montage sequence/range trims; identify importer status-prefix weakness and direct Codex hotfix then continue AB-C36+.
- **A-590/A-591:** A-590 reports accepted AirLight/AirHeavy trim ranges and offline suite 419/1; A-591 reports remaining Tier 2 assets created and lock released. Neither receipt is Lead runtime verification or owner video approval.

X-1382 records AB-C36–C40, and X-1383 records the C-979 importer hotfix; both are cross-referenced in `TASKS.md` and the mailbox.

