# Queue AV — capture-context receipt hardening

**Basis:** AU C-1121 closeout. Five offline tasks, followed by one batch report to Claude; continue the next batch without waiting for review. Check Claude feedback each cycle and hotfix rejected work first. Claude owns all Editor/PIE/build/package work. Owner visual choices remain in `FIGHT_VIDEO_REVIEW.md`; never edit owner verdict fields.

## Batch 1 — validate new same-frame capture context

| Task | Work | Acceptance |
|---|---|---|
| AV-C01 | Extend `fight_capture_receipt.py` to parse `FRAME_CONTEXT` JSON and bind exactly one context row to each same-run frame marker. | Missing, duplicate, foreign-run, stale-frame and mismatched action IDs fail closed; older receipts are labeled pre-context rather than upgraded. |
| AV-C02 | Add tests for camera projection estimates and explicit component-bounds/world-occlusion states. | Finite in-frame/out-of-frame synthetic points are classified; unreadable geometry stays `UNKNOWN`; `UNMEASURED` world occlusion is never promoted to clear/visible. |
| AV-C03 | Add a diagnostic parser for `PARRY_DIAG` transitions and PARRY timeout rows. | One diagnostic per montage transition and at most one timeout per action slot; tracker A1b plus montage name alone cannot become A4. |
| AV-C04 | Validate the aura warmup manifest sequence and approved-frame readiness. | Approved frame must follow a same-run decoded warmup frame at/above the brightness floor within 20 frames and 4 game seconds; all-black/old-manifest rows fail. |
| AV-C05 | Refresh AU and owner handoffs against newly returned Lead receipts without filling owner fields. | BUILD-255/259/Lead PIE/showcase scopes stay distinct; runtime and visual judgments remain separate, owner boxes blank. |

## Gates

Existing Lead-owned gates remain AU-C15 aura rerun, AU-C10 natural-A4 parry rerun, AU-C25 camera baseline, AU-C30 Air Light matrix, AU-C40 receipt smoke and AU-C45 visible/obscured frame review. AV work only validates evidence when Claude supplies it; it does not run Unreal or create visual findings.
