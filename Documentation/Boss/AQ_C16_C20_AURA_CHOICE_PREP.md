# AQ-C16–C20 — aura owner-choice preparation

## Owner choice boundary

The owner may compare three transient presentation choices: the approved current
`NS_Boss_PhaseTwoAura` at its existing attachment, the candidate
`NS_Boss_PhaseTwoAura_Boost` at the existing attachment, or that candidate at
`spine_03`. The last two choices are comparisons only; none is an approved
default. The planner in `Scripts/Editor/prepare_aura_choice.py` emits a JSON
dry-run plan for each choice and refuses `--apply` and `--save`.

The planner intentionally does not import Unreal or change a component or asset.
It describes the proposed transient state, readback needed to identify it, and
the data required to restore the starting state. Asset package identity/hash,
dirty state, runtime Niagara values, active state, component parent/socket and
relative transform must be captured before an authorized future experiment.
Rollback restores the recorded component asset, attachment and active state;
it must verify those values again. No asset save is allowed by this tool.

## Readback and visual evidence gate

For each candidate run, record route, run/build identity, boss health fraction,
camera, exact Niagara asset path, active component state, emitter/module values,
socket and relative transform. Preserve paired captures from the same route,
health, camera and framing, with hashes and the actual viewport frames. The
runtime output from the earlier comparison is not a sufficient owner-choice
package: its black frames (mean gray 0.0) do not show the aura, and a later
showcase clip reports different asset/attachment appearances. Treat the earlier
comparison as rejected visual evidence, not as proof that a renderer defect or
any particular choice is correct. Lead must use valid side-by-side visual
captures before asking the owner to choose.

The comparison must distinguish:

| Choice | Asset | Attachment | Current status |
|---|---|---|---|
| Current | `NS_Boss_PhaseTwoAura` | existing `NAME_None` attachment | approved existing behavior; baseline |
| Boosted | `NS_Boss_PhaseTwoAura_Boost` | existing `NAME_None` attachment | candidate; owner choice pending |
| Boosted on spine | `NS_Boss_PhaseTwoAura_Boost` | `spine_03` | candidate; owner choice pending |

`NAME_None` and `spine_03` describe the observed current/candidate attachment
options; confirm the actual parent, socket and relative transform from runtime
readback before comparing. This document does not authorize asset creation,
component wiring, saving, default changes, packaging, or a choice on the owner's
behalf.

## Offline validation

`python -m unittest Scripts.Editor.test_prepare_aura_choice` verifies the three
plans, required readback and rollback fields, dry-run default, and refusal of
apply/save flags. This test does not launch Unreal and does not establish visual
acceptance or asset readback.
