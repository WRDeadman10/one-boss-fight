"""
Adds the Poise attribute to every PlayerInfo and EnemyInfo data asset of the Advanced ARPG pack: a Default Attributes entry
(Attribute.Poise) and BP_PoiseExtendedAttribute in ExtendedAttributes. Run inside the editor (execute_script) after
BP_PoiseExtendedAttribute exists. Idempotent. DRY = True only reports.
"""
import unreal

DRY = False
POISE_TAG = "Attribute.Poise"
POISE_CLASS = "/Game/OneBossFight/Poise/BP_PoiseExtendedAttribute.BP_PoiseExtendedAttribute_C"
PLAYER_POISE, ENEMY_POISE, BOSS_POISE = 40.0, 30.0, 100.0
log = lambda m: unreal.log("[PoiseData] " + m)

registry = unreal.AssetRegistryHelpers.get_asset_registry()
poise_class = unreal.load_object(None, POISE_CLASS)
infos = []
for data in registry.get_assets_by_path("/Game/AdvancedARPGCombat", recursive=True):
    cls = str(data.asset_class_path.asset_name)
    if cls in ("BP_PlayerInfo_C", "BP_EnemyInfo_C"):
        infos.append((cls, data))
log("%d info assets" % len(infos))
for cls, data in infos:
    asset = data.get_asset()
    name = str(data.asset_name)
    try:
        attrs = asset.get_editor_property("Default Attributes")
        ext = list(asset.get_editor_property("ExtendedAttributes"))
    except Exception as e:
        log("%s (%s): skipped: %s" % (name, cls, str(e)[:100]))
        continue
    has_attr = any(k.get_editor_property("tag_name") == POISE_TAG for k in attrs.keys())
    has_ext = any(c == poise_class for c in ext)
    poise = PLAYER_POISE if cls == "BP_PlayerInfo_C" else (BOSS_POISE if "Boss" in name else ENEMY_POISE)
    log("%s (%s): attrs=%d poiseEntry=%s poiseClass=%s -> poise %.0f" % (name, cls, len(attrs), has_attr, has_ext, poise))
    if DRY:
        continue
    if not has_attr:
        template = next(v for k, v in attrs.items() if k.get_editor_property("tag_name") in ("Attribute.Stamina", "Attribute.Health")).copy()
        text = template.export_text()
        import re
        text = re.sub(r"(BaseValue_\w+)=[-\d.]+", r"\1=%f" % poise, text)
        text = re.sub(r"(MaxValue_\w+)=[-\d.]+", r"\1=%f" % poise, text)
        text = re.sub(r"(CurrentValue_\w+)=[-\d.]+", r"\g<1>=0.000000", text)
        template.import_text(text)
        key = unreal.GameplayTag()
        key.import_text('(TagName="%s")' % POISE_TAG)
        new_attrs = dict(attrs)
        new_attrs[key] = template
        asset.set_editor_property("Default Attributes", new_attrs)
    if not has_ext:
        ext.append(poise_class)
        asset.set_editor_property("ExtendedAttributes", ext)
    unreal.EditorAssetLibrary.save_loaded_asset(asset, False)
log("done")
