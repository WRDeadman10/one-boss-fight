# AV-C16–C20 — aura asset identity and PNG receipts

## Completed offline

- Approved and candidate target records must identify their canonical Niagara assets and report the active state as `True`. Warmup rows are scoped to the appropriate target asset and must remain active; readiness cannot transfer across the approved/candidate swap.
- Added opt-in `--verify-png-files` support to `aura_warmup_receipt.py`. When enabled, every referenced image must exist and its recorded lowercase SHA-256 must match the file. The default mode remains usable without local image files and does not claim pixel verification.
- Added fixtures for approved-only and full approved-plus-candidate manifest shapes, wrong target asset, inactive target, cross-phase warmup borrowing, missing PNG, hash mismatch, and opt-in behavior.
- Refreshed mailbox through C-1123: Claude accepted X-1592 and reports AU-C15/AU-C10 Lead runs live in `P_C1114_AUC15` and `P_C1110_AUPARRY`; no final runtime receipt was present. Those in-flight folders are left untouched; AU-C40/C45 follow and AU-C25/C30 plus owner choices remain open.

## Verification and limits

Focused AU/AV regression set: **85/85**. Python syntax checks and `git diff --check` pass. No Unreal, Editor/PIE, build, cook, package or media render was run by Codex. Optional file hashing was verified only against synthetic temporary PNG-like byte fixtures, not Lead capture files. Owner review fields remain untouched.

## Still pending

Lead-owned AU-C15/AU-C10 runtime receipts, then AU-C40/C45; AU-C25/AU-C30 and owner visual gates remain open. Continue AV-C21–C25 offline.
