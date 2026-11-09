# AV-C11–C15 — malformed evidence and manifest chronology

## Completed offline

- The full-fight receipt parser now rejects non-empty identity fields with the wrong type, numeric values masquerading as JSON booleans, and invalid world-occlusion values. Schema remains exact integer version 1; explicit UNKNOWN/UNMEASURED values are preserved.
- Aura manifests now require every row's game time to be finite and nondecreasing, including discarded warmups. Warmup phase prefixes must occur in the correct approved/candidate interval; candidate cannot precede approved.
- Both receipt CLIs have subprocess contracts: invalid schema or stale capture identity returns nonzero and emits no success-shaped JSON; valid output remains parseable JSON.
- Mailbox history was refreshed through C-1123. Claude accepted X-1592 for AV-C01–C05 and reports AU-C15/AU-C10 Lead runs live in P_C1114_AUC15 and P_C1110_AUPARRY. C-1123 contains no final runtime receipts; AU-C40/C45 remain next, with AU-C25/C30 and owner visual gates still open. The Lead evidence folders are in flight, so Codex leaves them untouched.

## Verification and limits

The same focused AU/AV regression set used for AV-C06–C10 passed **77/77** before this batch and **81/81** after it. Changed Python modules compile and `git diff --check` passes. No Unreal, Editor/PIE, build, cook, package or media render was run by Codex. No owner checklist field changed; no runtime result was inferred from offline contracts.

## Still pending

Lead-owned AU-C15 and AU-C10 are live; AU-C25, AU-C30, AU-C40 and AU-C45 remain pending after them. Owner visual choices remain open. Queue AV-C16–C20 continues offline receipt hardening.
