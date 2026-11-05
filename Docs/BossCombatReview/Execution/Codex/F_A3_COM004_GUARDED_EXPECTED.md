# F-A3 — BOSS-COM-004 live Guarded combo branch

Requirement source: ledger v3.36 `BOSS-COM-004` is PARTIAL. Existing live COM3 proof covers Hit and Whiff, but ledger predates the Nov 2 B_GUARD run. This package refreshes the REAL block-input path and verifies its live combo branch. Lead must decide whether the retained B_GUARD evidence already closes this row before spending a duplicate run.

## Setup

Use `/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofCOM`, whose authored combo graph maps Guarded at node A to node B. The proof hook injects the pack player's real `IA_ToggleCombat` and `IA_Block`; do not set guard tags directly. From `Docs/BossCombatReview/Execution/Claude/F4`:

```powershell
.\run_pie.ps1 -Map /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofCOM -OutDir "$PWD\..\..\Codex\F_A3_COM004\guarded" -Task F-A3_COM004_guarded -Console "rpg.BossProofPlayerGuard 3;rpg.BossProofPlayerGuardSeconds 12"
```

The expected route is recorded in the existing successful `B_GUARD/pie_block3` proof. Keep the full log and command. No new content script or asset is needed.

## Control

Use the existing `B_COMBO3/pie_normal` Hit/Whiff run as the branch control, or run the COM map with the guard hook disabled. Confirm the combo graph reaches its ordinary Hit/Whiff branches and the guard-specific input is off in control.

## PASS

- `guard_hook_armed mode=3` is logged; `guard_tags` shows `statusBlocking=1` before the active contact that resolves Guarded.
- Contact log shows guard/block outcome without health loss for that contact.
- `[FrameworkProof] combo_gate ... outcome=Guarded ... result=Continue next=B` follows completion of the guarded card.
- `combo_step node=B` (or the profile's named next node) proves the edge was actually followed; final result and target health invariant are consistent with all resolved contacts.
- Hit/Whiff control branches remain distinct. This package proves Guarded only; Parried is F-A4.

## FAIL

Fail if the hook does not produce live `Status.Blocking`, the contact resolves Hit/Whiff/Parried instead of Guarded, health is charged for a blocked contact, the combo gate selects the wrong edge, or execution ends before branch follow-up. Missing player ability/input readiness is a setup failure, not proof the rule is absent.

## Token checks

- `[FrameworkProof] guard_hook_armed` and `[FrameworkProof] guard_tags`.
- Contact outcome and health before/after lines.
- `[FrameworkProof] combo_gate ... outcome=Guarded ... next=B`.
- `[FrameworkProof] combo_step` and terminal `[FrameworkProof] RESULT`.
