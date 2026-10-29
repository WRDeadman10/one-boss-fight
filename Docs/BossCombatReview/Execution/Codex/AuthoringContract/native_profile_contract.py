"""Offline native-property contract. No Unreal import, asset load or editor operation.

Extracts only the simple UPROPERTY declarations in RPGEncounterBinding.h. This is
not a general C++ parser or native validator. Unsupported declaration shapes stop
extraction instead of inventing fields or Python reflection names.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import re

HEADER = Path("Source/OneBossFight/Player/RPGEncounterBinding.h")


def extract_contract(root: Path) -> dict:
    path = root / HEADER
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    records = {}
    pattern = r"(?m)^(?:struct (FRPG\w+)|class ONEBOSSFIGHT_API (URPGBossDefinition) : public UPrimaryDataAsset)\s*\n\{(.*?)^\};"
    for match in re.finditer(pattern, text.replace("\r\n", "\n"), re.S | re.M):
        name = match[1] or match[2]
        if not (name.endswith("Config") or name in {"FRPGParityField", "URPGBossDefinition"}):
            continue
        if "UPROPERTY(" not in match[3]:
            continue  # Plain transport structs are not reflected authoring records.
        fields = {}
        for line in match[3].splitlines():
            if "UPROPERTY(" not in line:
                continue
            prop = re.match(r"\s*UPROPERTY\([^)]*\)\s+(.+?)\s+(\w+)\s*(?:=\s*(.*?))?;\s*(?://.*)?$", line)
            if not prop:
                raise ValueError(f"Unsupported property declaration in {name}: {line.strip()}")
            fields[prop[2]] = {"cpp_type": prop[1], "initializer_source": prop[3]}
        if not fields:
            raise ValueError(f"No properties extracted: {name}")
        records[name] = fields
    if "URPGBossDefinition" not in records or "FRPGBossStatsConfig" not in records:
        raise ValueError("Native record discovery failed")
    return {
        "scope": "Native declaration names/types only; not Python API, runtime domain, ABI, cook or gameplay proof",
        "source": str(HEADER).replace("\\", "/"),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "records": records,
    }


def validate_record(contract: dict, record: str, value: object, *, require_all=False) -> list[str]:
    records = contract["records"]
    if record not in records:
        return [f"Unknown native record {record}"]
    if not isinstance(value, dict):
        return [f"{record}: expected object"]
    schema = records[record]
    errors = [f"{record}.{key}: unknown native property" for key in value.keys() - schema.keys()]
    if require_all:
        errors += [f"{record}.{key}: missing explicit property" for key in schema.keys() - value.keys()]
    for key in value.keys() & schema.keys():
        errors += _validate_type(contract, schema[key]["cpp_type"], value[key], f"{record}.{key}", require_all)
    return errors


def _validate_type(contract, cpp_type, value, label, require_all):
    if cpp_type in contract["records"]:
        return [f"{label}/{error}" for error in validate_record(contract, cpp_type, value, require_all=require_all)]
    if cpp_type.startswith("TArray<") and cpp_type.endswith(">"):
        if not isinstance(value, list):
            return [f"{label}: expected array"]
        return [error for i, item in enumerate(value) for error in
                _validate_type(contract, cpp_type[7:-1], item, f"{label}[{i}]", require_all)]
    if cpp_type == "bool":
        return [] if type(value) is bool else [f"{label}: expected bool"]
    if cpp_type == "int32":
        return [] if type(value) is int and -(2**31) <= value < 2**31 else [f"{label}: expected int32"]
    if cpp_type == "float":
        if type(value) not in (float, int):
            return [f"{label}: expected finite number, not bool"]
        try:
            valid = math.isfinite(float(value))
        except (ValueError, OverflowError):
            valid = False
        return [] if valid else [f"{label}: nonfinite or unrepresentable number"]
    if cpp_type == "FVector2D":
        if not isinstance(value, list) or len(value) != 2:
            return [f"{label}: expected explicit two-number array"]
        return [error for i, item in enumerate(value) for error in
                _validate_type(contract, "float", item, f"{label}[{i}]", require_all)]
    if cpp_type in {"FName", "FString"} or cpp_type.startswith(("TSoftObjectPtr<", "TSoftClassPtr<")):
        return [] if isinstance(value, str) else [f"{label}: expected string"]
    return [f"{label}: unsupported type {cpp_type}; no inferred coercion"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--input", type=Path, help="JSON with native URPGBossDefinition property spellings")
    args = parser.parse_args()
    contract = extract_contract(args.root)
    if not args.input:
        print(json.dumps(contract, indent=2))
        return 0
    payload = json.loads(args.input.read_text(encoding="utf-8-sig"))
    errors = validate_record(contract, "URPGBossDefinition", payload)
    print(json.dumps({"scope": contract["scope"], "source_sha256": contract["source_sha256"], "errors": errors}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
