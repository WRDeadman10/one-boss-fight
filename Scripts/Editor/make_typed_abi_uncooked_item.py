"""Replaces the uncooked typed-ABI fixture (Codex X-153 review): `DA_ABI_UncookedWeaponItem` is now a copy of the REWIRED cooked fourth weapon item, so its typed edges
(own style, own actor) are as valid as the positive bundle's and its ONLY defect is that it lives outside the always-cook roots. Creates one NEW asset, refuses to overwrite,
never touches a pack asset. Log prefix [ABIUncooked]."""
import unreal

EAL = unreal.EditorAssetLibrary
SOURCE = "/Game/OneBossFight/Data/TypedABIFixtures/DA_ABI_FourthWeaponItem"
TARGET = "/Game/OneBossFight/ReviewFixtures/TypedABI/DA_ABI_UncookedWeaponItem"
log = lambda msg: unreal.log("[ABIUncooked] " + msg)
if EAL.does_asset_exist(TARGET):
    raise RuntimeError("refused: target exists " + TARGET)
if not EAL.does_asset_exist(SOURCE):
    raise RuntimeError("missing source " + SOURCE)
EAL.make_directory("/Game/OneBossFight/ReviewFixtures/TypedABI")
if EAL.duplicate_asset(SOURCE, TARGET) is None or not EAL.save_asset(TARGET):
    raise RuntimeError("duplicate or save failed")
lib = unreal.RPGScratchRouteALibrary
item = EAL.load_asset(TARGET)
log("uncooked item style edge: " + str(lib.export_property_text(item, "Combat Style"))[:240])
log("uncooked item actor edge: " + str(lib.export_property_text(item, "Equipable Actor Class"))[:240])
log("done; uncooked fixture replaced by a copy of the rewired fourth item")
