# Queue D132 — executor hit acceptance ordering audit

Date: 2026-11-03  
Method: static comparison of direct/ring hit paths, resolver outcome handling and test coverage; no tests run.

## Outcome and counter order

Both direct-window and ring-window paths share the same ordering: build the hit payload/key; read Blocking before damage; apply the configured guarded chip amount to the payload; call `Resolver->Resolve`; classify guard using the pre-contact Blocking snapshot plus whether resolver returned Parried; then update counters and boss state based on resolver outcome.

- `Accepted`: increments global and per-card accepted counts and accumulates actual `HPApplied`; increments guarded count only when classified Guarded; calls `NoteDamageApplied`.
- `Parried`: increments global/per-card parried counts and calls `RecordParriedContact` (grade/recovery/posture path).
- All other resolver outcomes: no accepted/guarded/parried count and no damage-applied/parry reaction update.

Thus Guarded is a classification of an Accepted contact (including zero-damage chip configuration if still Accepted); it is not an alternate resolver outcome. Parried is exclusive from accepted damage counters. The direct and ring paths duplicate this same block, so parity is source-visible but not factored into one shared C++ helper.

## Evidence gap

The existing pure damage/guard tests cover resolver precedence and classification. Source search found no focused assertion on `URPGFrameworkMoveExecutor` global/per-card counters for Accepted, Guarded, Parried, and rejected outcomes, or a direct-vs-ring parity fixture. Earlier arena proof may show logs but does not serve as a deterministic automation contract for these counters.

## Limits

No source-order defect found. Exact accepted/parried counter integration remains unverified by focused automation; static only.
