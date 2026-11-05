# Queue D135 — pack dependency loader fail-closed audit

Date: 2026-11-03  
Method: static trace of profile validation/resolution and failure propagation; no assets or tests run.

## Load boundaries

`ResolveProfile` clears `Out` and `Error` first, rejects invalid object/thread/profile before loading, and synchronously loads the configured mesh, AnimBP class, target pawn class, each selected card, card skeleton/sequence, optional stagger/phase clips, and optional player punish montages. Required null/wrong-type/abstract dependencies fail with named `Framework.Profile.*` tokens. Card compile/asset validation failures return the issue text or `Framework.Profile.ResolvedCard`; skeleton, clip, phase, combo-card, damage-budget and punish requirements each refuse with their own token. The final dependency object moves into `Out` only after all required validation completes, so an earlier failure leaves `Out` empty; no alternate actor/profile/card is substituted.

`ValidateProfile` also refuses missing required soft references before synchronous resolution. For F5, every candidate and every combo-node MoveId must resolve against the configured candidate set. Optional clips are skipped only when their soft reference is genuinely null; configured-but-unloadable clips fail.

## Findings / coverage

No fallback changing actor/profile identity was found in this loader. Grep found no targeted `Framework.Profile.Dependency`, `ResolvedCard`, optional-clip load, or punish-load failure automation cases; broad profile/preflight fixtures may test adjacent validation but do not pin each load failure token. Consequently the fail-closed behavior is source-traced, not proven by missing-asset runtime tests.

## Limits

The audit does not force package load failures or inspect asset registry state. It makes no claim that configured project assets currently load in Editor or a packaged build.
