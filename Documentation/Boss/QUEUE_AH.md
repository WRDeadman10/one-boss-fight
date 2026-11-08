# Queue AH — zero-damage ER air attack source audit

Scope: explain the post-A-598 zero-damage result from current source and evidence, and prepare a minimal Lead verification request. Static review only; no code, asset, Editor, build, cook, package, PIE or benchmark work by Codex.

## Batch 1 — five tasks

| ID | Task | Acceptance |
|---|---|---|
| AH-C01 | Trace ER air montage notify execution into collision trace | Source paths and conditions cited; distinguish notify serialization, weapon/socket setup and target filtering; no causal claim without proof. |
| AH-C02 | Trace attack-data assignment and fallback for ability-driven air attacks | Document exact producer/consumer path and whether an unset notify property is expected to obtain data from ability/HitData. |
| AH-C03 | Audit the `StoredInputTags` empty-array warning path | Identify emitting function and whether it can affect montage execution/hit intake; if static evidence cannot establish causation, mark unproven. |
| AH-C04 | Define a minimal Lead discriminator matrix for the remaining zero-damage failure | Separate notify activation, trace/socket overlap, hit candidate/filter, AttackData attribution and health delta; state observable/log needed for each. |
| AH-C05 | Refresh status and stage the next five-task lane | Preserve exact AG findings, list any outstanding external evidence, validate five unique IDs, and do not infer product/release approval. |

## Progress note — 2026-11-07

Queue AG closed locally with AG-C01 partial (AirHeavy full t3d missing), AG-C02 runtime failure (both ER air attacks deal 0 HP on both routes, controls work), and AG-C03/C04 complete. AH-C01–C04 source/evidence findings are recorded in `AH_C01_C04_ZERO_DAMAGE_SOURCE_AUDIT.md`; AH-C05 closeout is complete in the accompanying C-995 follow-through. The driver sets player X to boss+160 cm but logs 900 cm, and the observed hand-to-boss distance during air trace windows exceeds 240 cm. This is a likely range confound to check, not a proven cause. C-995 additionally assigns a reusable Lead reach probe and re-slice notify mapping; those are documented in `C995_AIR_REACH_FOLLOWTHROUGH.md`.

## Batch 1 closeout — AH-C01–C05

AH-C01–C04 are documented in `AH_C01_C04_ZERO_DAMAGE_SOURCE_AUDIT.md`. AH-C05 reconciles those findings with C-995, preserves the confirmed zero-damage runtime result and unproven range hypothesis, and stages the next five-task lane in `QUEUE_AI.md`. No engine run or asset edit was performed by Codex.
