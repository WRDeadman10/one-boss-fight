# Selector tie-band determinism audit (Queue D D7, 2026-11-03)

## Source behavior

`FRPGBossMoveSelector::Initialize` accepts finite `TieBand` in `[0, 0.5]`. With `TieBand == 0`, highest score wins and equal scores keep the lowest candidate index. With positive band, the tier threshold is `bestScore * (1 - TieBand)` and eligible scores at or above it enter the tier; when tier size exceeds one, `FRandomStream(TieSeed + StartedCount)` chooses a member. `StartedCount` advances only on valid `NoteStarted` calls and `Reset` returns it to zero.

## Existing tests inspected

`FBossMoveSelectorPolicy` checks deterministic lowest-index ties at zero band. `FBossMoveSelectorBoundedTie` checks that seed 12345 repeats the same 50-pick prefix, seed 54321 gives another sequence, the card below a 10% tier never wins, a narrow 2% band leaves the best card, zero band stays deterministic over 100 picks, and invalid bands (-0.1, 0.51, infinity, NaN) refuse initialization. Its repeated loop records each chosen card with `NoteStarted`, so each subsequent pick uses the incremented seed offset.

## Coverage result

| Property | Current evidence | Gap / limit |
|---|---|---|
| Zero-band stable lowest-index tie | Selector policy test. | Covered. |
| Same seed and same start sequence | 50-pick prefix comparison. | Covered for the chosen fixture and run length. |
| Different seed changes sequence | Different-seed prefix comparison. | Covered for the chosen fixture; not a distribution-quality proof. |
| Below-tier card excluded | Score 0.5 card absent from 10% tier. | Covered away from exact threshold. |
| Inclusive tier threshold | Source uses `Score >= Threshold`. | No candidate sits exactly on the threshold; adjacent-below/at/above test would lock down floating-point boundary behavior. |
| Zero/one member tier | Zero-band and narrow band leave one deterministic top candidate. | No explicit positive-band single-member tier assertion separate from narrow-band fixture. |
| `TieBand` endpoints | Zero is exercised; 0.5 is used by property test configuration. | Exact maximum endpoint acceptance is indirect; config-init assertion would be clearer. |
| StartedCount and Reset interaction | Source adds count to seed and Reset clears it. | D6 identifies no isolated post-reset sequence-vs-fresh-selector assertion. |

## Bounded fixture proposal

Use three eligible candidates with scores engineered to best, exactly `best*(1-band)`, and just below threshold; assert tier membership directly via selection outcomes with fixed seed and confirm the below-threshold candidate never wins. Add an exact `TieBand=0.5` initialization case, a positive-band one-member tier, and reset-vs-fresh-selector sequence equality. Avoid claiming statistical quality from a fixed sample. No test or code change is authorized by this audit.

## Verification boundary

Inspected selector source and test code read-only; no C++ or test file changed, and no test/build/Editor/PIE/package run occurred. The report records deterministic fixture evidence, not runtime randomness quality.
