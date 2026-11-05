#!/usr/bin/env python3
"""Report plugin enablement and declared dependencies from project descriptors."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    project = next(iter(root.glob("*.uproject")), None)
    if project is None:
        parser.error("no .uproject found at root")
    enabled = {entry.get("Name"): entry.get("Enabled") for entry in json.loads(project.read_text(encoding="utf-8")).get("Plugins", [])}
    descriptors = sorted((root / "Plugins").rglob("*.uplugin")) if (root / "Plugins").exists() else []
    found = set()
    for path in descriptors:
        data = json.loads(path.read_text(encoding="utf-8"))
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
