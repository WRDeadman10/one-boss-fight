# Queue D139 — asset referencer-safe operation audit

Date: 2026-11-03  
Method: read-only scan of current `Scripts/Editor` asset mutation sites and comparison with S161/S162; no Editor operation.

## Referencer checks found

- `fix_grey_layers_2.py` queries package referencers for its temporary copy before delete. This is the only explicit pre-delete referencer gate in the audited deletion paths; the gate applies only to that exact temporary package.
- `import_boss01_clips_r14.py` queries referencers before in-place reimport and leaves the current asset when references are present. Its checked empty-reference result is a historical observation and must not be reused as current state.
- No referencer query appears before the other scanned `delete_asset`/`delete_directory` operations or the sampled rename/move operations.

## Ungated destructive destinations

The existing S161 inventory remains applicable: `boss_pose_reset.py`, `build_asset_proof_map.py`, `cleanup_review11/12/13.py`, `import_boss01.py`, `retarget_pack_to_greystone.py`, `rpg_content_lib.py::recreate`, `setup_m1_content.py`, `setup_m3_content.py`, `setup_m4_content.py`, `setup_m7_beam_materials.py`, `setup_m7_roll.py`, `sevarog_pack_01_proxy.py`, `sevarog_pack_02_montages_abilities.py`, `sevarog_pack_03_info_style_pawn.py`, `sevarog_pack_05_parity.py`, and `sevarog_pack_05b_death_style.py` still have delete/recreate or directory-removal paths without an enforced per-target referencer check. S162 describes additional in-place replacement/import behavior; replacement is not equivalent to delete-safety.

## Result

The documented policy correctly warns against unsafe reruns, but destructive operations are not individually gated in source across the inventory. Acceptance is therefore a policy/evidence gap rather than a reason to execute or recommend those scripts. Before any such operation, an operator needs a fresh referencer query for that exact target or a separately chosen destination; this audit authorizes no mutation.
