"""Read-only direct hard/soft Asset Registry referencer census for P35 candidates."""
import json
import unreal

PACKAGE_ROOT = "/Game/OneBossFight/FrameworkProof/"
TARGETS = (
    "DA_Sevarog_ComboOutcome_FAG23",
    "DA_Sevarog_ComboOutcome_FAG23b",
    "L_SevarogFrameworkProofComboOutcomeFAG23",
    "L_SevarogFrameworkProofComboOutcomeFAG23b",
    "L_SevarogFrameworkProofStrafeBlockerSEL008",
    "DA_Sevarog_ComboOutcome_FAG23c",
    "L_SevarogFrameworkProofComboOutcomeFAG23c",
)

registry = unreal.AssetRegistryHelpers.get_asset_registry()
options = unreal.AssetRegistryDependencyOptions(
    include_soft_package_references=True,
    include_hard_package_references=True,
    include_searchable_names=False,
    include_soft_management_references=False,
    include_hard_management_references=False,
)
rows = []
for name in TARGETS:
    package = PACKAGE_ROOT + name
    refs = sorted(str(value) for value in registry.get_referencers(package, options))
    rows.append({"package": package, "direct_referencer_count": len(refs), "direct_referencers": refs})
unreal.log("[P35_REFERENCERS_JSON] " + json.dumps(rows, sort_keys=True, separators=(",", ":")))
