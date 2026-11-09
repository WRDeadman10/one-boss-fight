"""Read-only UE reflection probe for the C-1202 Niagara graph authoring path."""
import unreal


ASSET_PATH = "/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura_BoostLite"


def emit(label, value):
    unreal.log(f"[AuraGraphAPI] {label}={value}")


def attempt(label, obj, property_name):
    try:
        value = obj.get_editor_property(property_name)
        emit(f"{label}.{property_name}", f"{type(value).__name__}: {value!r}")
        return value
    except Exception as exc:
        emit(f"{label}.{property_name}.ERROR", f"{type(exc).__name__}: {exc}")
        return None


for name in (
    "NiagaraSystem", "NiagaraEmitterHandle", "NiagaraEmitter", "NiagaraScript",
    "NiagaraScriptSource", "NiagaraGraph", "NiagaraNodeFunctionCall", "EdGraphPin",
    "NiagaraSystemEditorData", "NiagaraScriptVariable", "NiagaraVariant",
    "NiagaraEditorSubsystem", "NiagaraEditorLibrary", "NiagaraParameterStore",
    "NiagaraEditorUtilities", "NiagaraCompileOptions",
):
    emit(f"class.{name}", hasattr(unreal, name))

eal = unreal.EditorAssetLibrary
asset = unreal.load_asset(ASSET_PATH)
if asset is None:
    raise RuntimeError(f"Read-only probe cannot load source {ASSET_PATH}")
emit("asset", f"{asset.get_class().get_name()} {asset.get_path_name()}")
emit("system_methods", [name for name in dir(asset) if any(t in name.lower() for t in ("compile", "editor", "emitter", "script", "parameter"))])
for property_name in ("emitter_handles", "system_spawn_script", "system_update_script", "exposed_parameters"):
    result = attempt("system", asset, property_name)
    if property_name == "emitter_handles" and result:
        for index, handle in enumerate(result):
            emit(f"handle.{index}.type", type(handle).__name__)
            emit(f"handle.{index}.dir", [name for name in dir(handle) if any(t in name.lower() for t in ("emitter", "instance", "name", "data"))])
            instance = attempt(f"handle.{index}", handle, "instance")
            attempt(f"handle.{index}", handle, "name")
            if instance is not None:
                emit(f"instance.{index}.type", f"{type(instance).__name__} {getattr(instance, 'get_class', lambda: None)()}")
                emit(f"instance.{index}.dir", [name for name in dir(instance) if any(t in name.lower() for t in ("script", "graph", "source", "version"))])
                for p in ("graph_source", "source", "scripts", "versioned_emitter"):
                    attempt(f"instance.{index}", instance, p)
    if property_name.endswith("_script") and result is not None:
        emit(property_name + ".dir", [name for name in dir(result) if any(t in name.lower() for t in ("source", "graph", "version"))])
        source = attempt(property_name, result, "latest_source")
        if source is not None:
            attempt(property_name + ".source", source, "node_graph")

editor_data = attempt("system", asset, "editor_data")
if editor_data is not None:
    emit("editor_data.type", type(editor_data).__name__)
    emit("editor_data.dir", [name for name in dir(editor_data) if any(t in name.lower() for t in ("user", "graph", "parameter"))])
    for p in ("user_parameter_meta_data", "user_parameter_hierarchy", "system_overview_graph"):
        attempt("editor_data", editor_data, p)

emit("probe", "READ_ONLY_DONE")
