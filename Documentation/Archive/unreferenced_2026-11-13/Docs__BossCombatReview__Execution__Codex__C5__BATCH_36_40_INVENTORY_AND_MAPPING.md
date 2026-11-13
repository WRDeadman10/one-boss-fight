# Queue F-C C5 tasks 36–40: weapon inventory and schema map

The existing `C5_WEAPON_DATA_AUDIT.md` supplies the value inventory and subsystem consumer traces. `weapon_parameter_coverage.json` turns the weapon-specific surface into a machine-readable crosswalk to C3 config fields and validator rules.

Classification is explicit: catalog identities and references are data-driven; attack-row tuning is data plus C++ defaults; pack stamina cost, slot selection, and table path are structural/hardcoded; combo graph and montage notify timing remain pack-authored and unresolved by offline inspection. Only data-backed fields map to C3 authoring keys. Structural and pack-authored fields are recorded with an empty C3 mapping, so they are not misrepresented as designer-tunable through `new_weapon.py`.

This batch is an inventory/mapping artifact, not a proposal to change pack or engine behavior. Source references and consumers are cited per field; the C5 audit remains the source for serialized asset offsets. No Content asset or C++ source changed.
