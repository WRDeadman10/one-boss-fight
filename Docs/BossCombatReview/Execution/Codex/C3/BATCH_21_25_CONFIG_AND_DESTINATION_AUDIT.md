# Queue F-C C3 tasks 21–25: schema and safe authoring preflight

## Inventory and validated configuration

The catalog schema in `C3_NEW_WEAPON_UTILITY_DESIGN.md`, `C3_V1_CATALOG_ENTRY_DESIGN.md`, and `C3_NEW_WEAPON_HOWTO.md` maps the root catalog (`URPGCombatCatalog`) to weapon/build definition assets and back to the weapon attack table. `validate_weapon_config.py` is the pure input contract; pack-owned style/item/actor/ability assets remain required prerequisites.

The catalog validator now requires `catalog.register` to be a boolean. If true, it requires valid weapon, build, and root paths under the catalog directory; rejects identical definition destinations, root/destination overlap, non-expansion legacy slots, and registration in `update_existing_style` mode. A catalog block with `register: false` keeps table-only authoring possible.

## Editor utility and acceptance

`Docs/BossCombatReview/Execution/Claude/C3/new_weapon.py` remains the Editor-only application path. Before any attack-table mutation, it now verifies that definition destinations are distinct and absent and the root catalog exists. It retains a second destination check immediately before asset creation. After setting catalog definitions, it reads back all authored identity/reference/action/alias/icon/order fields and verifies the root's appended references, in addition to the existing attack-row readback.

This closes the preflight defect where a destination collision could be discovered only after attack-table rows had already been saved. Static AST parse and targeted diff checks only; no Unreal Editor, PIE, build, or tests were run. Lead should validate Unreal soft-reference readback and the end-to-end authoring path.
