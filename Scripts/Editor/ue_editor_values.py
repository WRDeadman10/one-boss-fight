"""Small Unreal Python value adapters shared by read-only G044 scripts.

Functions accept an explicit Unreal module where engine type information is
needed, so offline tests can supply faithful mocks without importing Unreal.
"""
import math
import re


def ue_path(value):
    if value is None:
        return ""
    getter = getattr(value, "get_path_name", None)
    if callable(getter):
        try:
            path = str(getter())
            if path:
                return path
        except Exception:
            pass
    exporter = getattr(value, "export_text", None)
    if callable(exporter):
        try:
            text = str(exporter()).strip()
            match = re.search(r"'(/Game/[^']+)'", text)
            return match.group(1) if match else text
        except Exception:
            pass
    formatter = getattr(value, "to_string", None)
    if callable(formatter):
        try:
            return str(formatter())
        except Exception:
            pass
    text = str(value).strip().strip("'\"")
    if text.startswith("SoftObjectPath(") and text.endswith(")"):
        text = text[len("SoftObjectPath("):-1].strip().strip("'\"")
    if "'/Game/" in text:
        text = "/Game/" + text.split("'/Game/", 1)[1].split("'", 1)[0]
    return text


def is_expected_class(asset, expected_class):
    actual = asset.get_class()
    expected_path = str(expected_class.get_path_name())
    return str(actual.get_path_name()) == expected_path or bool(actual.is_child_of(expected_class))


def _is_array(value, unreal_module):
    candidates = [list, tuple]
    engine_array = getattr(unreal_module, "Array", None) if unreal_module is not None else None
    if isinstance(engine_array, type):
        candidates.append(engine_array)
    return isinstance(value, tuple(candidates))


def _property_names_from_export(value):
    exporter = getattr(value, "export_text", None)
    if not callable(exporter):
        return []
    try:
        raw_names = re.findall(r"[(,]([A-Za-z_][A-Za-z0-9_]*)=", str(exporter()))
    except Exception:
        return []
    names = []
    for raw in raw_names:
        name = raw[1:] if re.match(r"^b[A-Z]", raw) else raw
        names.append(re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name).lower())
    return names


def _soft_object_path_from_export(text):
    match = re.fullmatch(r"(?:SoftObjectPath|FSoftObjectPath)\(\s*['\"]([^'\"]+)['\"]\s*\)", text.strip())
    return {"object_path": match.group(1)} if match else None


def stable_value(value, unreal_module=None, where="value"):
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(where + " is non-finite")
        return value
    if _is_array(value, unreal_module):
        return [stable_value(item, unreal_module, where + "[]") for item in value]
    getter = getattr(value, "get_path_name", None)
    if callable(getter):
        try:
            return {"object_path": str(getter())}
        except Exception:
            pass
    formatter = getattr(value, "to_string", None)
    if callable(formatter):
        try:
            return str(formatter())
        except Exception:
            pass
    fields = {}
    names = set(n for n in dir(value) if not n.startswith("_"))
    names.update(_property_names_from_export(value))
    for name in sorted(names):
        try:
            child = value.get_editor_property(name)
        except Exception:
            continue
        if callable(child):
            continue
        fields[name] = stable_value(child, unreal_module, where + "." + name)
    if fields:
        return fields
    exporter = getattr(value, "export_text", None)
    if callable(exporter):
        try:
            text = str(exporter())
            soft_path = _soft_object_path_from_export(text)
            return soft_path if soft_path is not None else text
        except Exception as exc:
            raise ValueError(where + " export_text failed: " + str(exc))
    return str(value)


def guid_text(value):
    if value is None:
        return ""
    try:
        return "-".join("%08X" % (int(value.get_editor_property(part)) & 0xFFFFFFFF)
                       for part in ("a", "b", "c", "d"))
    except Exception:
        return ""
