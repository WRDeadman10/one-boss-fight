#!/usr/bin/env python3
"""Report plugin enablement and declared dependencies from project descriptors."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))  # BO: helper import works as a script or as Scripts.Tools.*
from json_input import JsonInputError, fail, load_json, require_objects


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    project = next(iter(root.glob("*.uproject")), None)
    if project is None:
        parser.error("no .uproject found at root")
    descriptors = sorted((root / "Plugins").rglob("*.uplugin")) if (root / "Plugins").exists() else []
    try:  # BO-04 / KI-166: parse every descriptor up front so a bad file fails closed before any row is printed.
        entries = require_objects(project, load_json(project, dict).get("Plugins", []), "Plugins")
        parsed = {}
        for path in descriptors:
            parsed[path] = load_json(path, dict)
            require_objects(path, parsed[path].get("Plugins", []), "Plugins")
    except JsonInputError as error:
        return fail(error)
    enabled = {entry.get("Name"): entry.get("Enabled") for entry in entries}
    found = set()
    for path in descriptors:
        data = parsed[path]
        name = data.get("FriendlyName") or path.stem
        found.add(path.stem)
        deps = [x.get("Name", "") for x in data.get("Plugins", [])]
        print(f"{name}\tenabled={enabled.get(path.stem, False)}\tdependencies={','.join(deps) or '-'}\t{path.relative_to(root)}")
    for name, state in sorted(enabled.items()):
        if name not in found:
            print(f"{name}\tenabled={state}\tdescriptor=not found under project Plugins/")
    print(f"project={project.name} descriptors={len(descriptors)} enabled_entries={sum(bool(x) for x in enabled.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
