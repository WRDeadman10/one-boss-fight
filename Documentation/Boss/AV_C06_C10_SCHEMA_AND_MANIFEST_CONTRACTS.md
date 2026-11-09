# AV-C06–C10 — schema and manifest contracts

## Completed offline

- Versioned the full-fight camera-context schema as version 1 in each `FRAME_CONTEXT` row and in run provenance. The receipt parser rejects absent or unsupported versions and returns the accepted schema in its JSON output.
- Extended the CLI contract to verify context survives JSON serialization, including frame/action identity and the explicit `UNMEASURED` world-occlusion state.
- Tightened the aura manifest validator: each row must have a unique frame label and `capture_id == run + ":" + frame`; approved/candidate phases must use their canonical labels; warmup labels must be sequential and use the correct approved/candidate prefix; candidate capture must follow approved capture when present.
- Added return-transition coverage for montage A→B→A. Consecutive duplicate transition rows remain rejected, while a real return transition is accepted; the fallback still requires a live sweep witness.
- Re-read mailbox history through C-1122. Claude accepted X-1589–X-1591 and A-655, ordered Lead to run AU-C15 then AU-C10, then AU-C40/C45, and told Codex to continue AV. No later Lead receipt or owner visual decision is present in the messages inspected. Runtime gates remain Lead-owned.

## Verification and limits

Focused AU/AV regression set: **77/77** across the receipt, warmup, owner-field, observation, video, full-fight offline, aura-comparison, and PNG-metric contracts. Python syntax checks and `git diff --check` pass. These are offline checks only; Codex did not run Unreal, Editor/PIE, build, cook, package, render media, commit, or push. Owner review fields remain unchanged.

## Still pending

Lead-owned AU-C15 aura rerun, AU-C10 parry rerun, AU-C25 camera baseline, AU-C30 Air Light matrix, AU-C40 receipt smoke, and AU-C45 frame review. No runtime verdict is inferred from these parser contracts.
