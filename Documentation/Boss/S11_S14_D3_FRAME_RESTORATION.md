# Queue S S11–S14: D3 source-frame evidence

Date: 2026-11-05. Source used for canonical measurements: `Documentation/Boss/Morgott_82_Point_Combat_Reference/Elden Ring - Morgott, The Omen King Boss Fight.webm` (3840×2160, nominal 59.9401 fps), not the companion MP4 (29.97 fps). The D3 template metadata says 59.9401 fps, combat zero 105.0 s. Source SHA-256 and each restored frame hash are recorded in `Docs/BossCombatReview/Execution/Claude/D3/evidence/S12_S14_evidence_sha256.txt`; extraction details are in `S12_S14_frame_manifest.json`.

## S11 — priority 7 Bloodflame grab

An initial full combat survey (105–335.5 s at 2 samples/s) plus focused inspection of candidate phase-two intervals did not positively identify the ledger's `REF_BloodflameGrab_Skewer` as a distinct completed grab/skewer. The close-up around 190.8–194.5 s is the phase transition, not a confirmed grab; it must not be reused as one. No W/C/A/E/R/RE values or evidence paths were written to the ledger. Priority 7 remains null pending a clearly visible instance or a suitable source clip. This finding is an inconclusive identification, not proof the attack is absent from the full footage.

## S12–S14 — restore already-recorded priorities 8–10

The D3 ledger already contained six measured frame IDs for each of priorities 8–10; their 18 canonical PNG references were missing. Codex restored only those missing paths from the registered 59.9401 fps WebM using the ledger formula `t = 105 + (frame − 1) / 59.9401`. The existing ledger values were not edited.

| Priority | Clip | Frames (W/C/A/E/R/RE) | Verification |
|---:|---|---|---|
| 8 | `REF_OmenCurseBurst_Phase2` | 5189 / 5270 / 5347 / 5612 / 5624 / 5732 | six PNGs restored; source-time contact sheet and per-file hashes retained |
| 9 | `REF_MaceSlam_Sweep` | 1703 / 1787 / 1796 / 1801 / 1835 / 1871 | six PNGs restored; source-time contact sheet and per-file hashes retained |
| 10 | `REF_GapPounce_Close` | 3951 / 3981 / 4005 / 4023 / 4047 / 4065 | six PNGs restored; source-time contact sheet and per-file hashes retained |

Contact sheets: `S8_verified_contact_sheet.jpg`, `S9_verified_contact_sheet.jpg`, and `S10_verified_contact_sheet.jpg` in the same evidence folder. Validation: P8–P10 ledger references checked: 18 expected, 0 missing; `D3_findings_table.py` renders the existing five measured rows; `test_fill_ledger.py` passes 14/14. Priority 7 remains null. No gameplay assets or runtime values were changed.

## C-881 follow-through — restore P1 and P6 references

Restored the remaining twelve ledger-referenced PNGs: P1 frames 447/456/465/472/479/500 and P6 frames 2381/2423/2566/2602/2620/2818. Source time is `105 + (frame - 1) / 59.9401` seconds. The timestamp seek method was checked against already restored P8 frame 5189; decoded pixels match exactly. New file byte hashes/sizes and source times are appended to `S12_S14_frame_manifest.json` and `S12_S14_evidence_sha256.txt`. Ledger timing and confidence values were retained. All 30 measured-row image references are now present; this does not upgrade P6's low confidence or make its hazard observation a boss animation measurement.

S15 is completed in `Documentation/Boss/S15_D3_CLIP_AUDIT.md`. The priority 2–5 rows remain unmeasured, with priorities 3–5 explicitly withdrawn after evidence-first review; no timing/frame values were fabricated.
