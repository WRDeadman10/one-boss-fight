# F-AG4 — BOSS-HIT-008 framework blocking integration

## Scope

This package targets the ledger observable as written: the framework damage path must read the player's blocking/parrying state before health is applied. It does not test the third-party pack boss Blueprint. It also does not claim a resolver `Guarded` outcome: `ERPGDamageOutcome` has no such outcome. In the framework move executor, guard is read before `URPGDamageResolver::Resolve`; when `GuardChipFraction` is enabled, the executor scales the requested HP damage before calling the resolver. The resolver can then return `Accepted` with nonzero chip. Therefore a zero-HP `resolver Guarded` expectation would contradict the current implementation. If the owner intends a zero-damage block, that is a separate policy/change request.

## Setup

Use the isolated existing `DA_Sevarog_GuardChip_R7` / `L_SevarogFrameworkProofGuardChipR7` proof content. Its profile has `GuardChipFraction=0.25`, so use the *same authored profile/map* for both fresh runs. Lead runs from `Docs/BossCombatReview/Execution/Claude/F4`:

```powershell
$base = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\F4'
$root = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Codex\F_AG4_HIT008_BLOCK'
& "$base\run_pie.ps1" -Map /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofGuardChipR7 -OutDir "$root\control" -Task F-AG4_HIT008_control
& "$base\run_pie.ps1" -Map /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofGuardChipR7 -OutDir "$root\guarded" -Task F-AG4_HIT008_guarded -Console 'rpg.BossProofPlayerGuard 3;rpg.BossProofPlayerGuardSeconds 12'
```

The first run leaves the test hook off. The second uses the framework's real IA_ToggleCombat/IA_Block hook from the first attack. Compare the first accepted contact for the same card/window/key under each arm; ignore duplicate-contact callbacks. Keep command, raw log, run result, and hashes. No runtime variable may be changed between contacts within a run.

## Control

The unblocked and guarded commands above are the paired control and treatment. Validate that the first matching accepted contact for the same card/window/key has the expected guard and damage telemetry before comparing totals.

## PASS

- Both fresh runs use the expected proof map, profile and card; source-content hashes are unchanged.
- Control logs a non-blocking `guard_state`, an accepted hit, and exact `incoming` / `hpApplied` / `healthBefore` / `healthAfter` values.
- Guarded arm logs `guard_hook_armed`, `guard_tags ... statusBlocking=1`, and for the *same first-contact identity* (`instance`, `window`, `key`) a `guard_state ... guard=Guarded` followed by `guard_chip incoming=... applied=...` and `hit ... outcome=Accepted hpApplied=...` with matching health delta.
- At 0.25 fraction, the matching contact should apply 25% of incoming damage (rounding per implementation). This demonstrates guard state was observed and damage scaled before resolver application. A zero delta is not expected for this profile.
- Raw logs are complete and parse with `validate_framework_proof_logs.py`; retain runner result and hashes.

## FAIL

If blocking is not active on the first accepted contact, the contact identity cannot be paired, only later duplicate callbacks show Guarded, control and guarded runs do not use the same profile/card, or telemetry lacks the pre-resolution guard and applied-damage values, the package is inconclusive. A resolver outcome named `Guarded` or zero `hpApplied` is not a valid expected token under the current source. Do not infer blocking from unchanged periodic health samples or unrelated resolver rejections.

## Token checks

- `[FrameworkProof] guard_hook_armed` and `guard_tags`.
- `[FrameworkProof] guard_state` for the paired first contact.
- `[FrameworkProof] guard_chip` and `[FrameworkProof] hit` with consistent HP values.
- `[FrameworkProof] RESULT` and successful runner result in both arms.
