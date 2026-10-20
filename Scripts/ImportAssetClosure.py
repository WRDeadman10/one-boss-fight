"""Copy third-party UE assets into Content/ together with everything they reference.

Package paths are preserved (/Game/Foo/Bar stays Content/Foo/Bar) so internal references keep resolving;
a plain file copy to a different folder would leave every reference dangling.

Usage: python -I Scripts/ImportAssetClosure.py [--dry-run] <seed> [<seed> ...]
A seed is either a /Game/... package path or a source folder path (every .uasset below it is a seed).
Reads only; the only writes are copies into this project's Content/.
"""
import re
import shutil
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
CONTENT = PROJECT / "Content"
UNREAL_ASSETS = Path(r"C:\Users\winss\Documents\Unreal Projects\Unreal Assets")

# (package prefix, source directory that corresponds to that prefix). Longest prefix wins.
BLOOD = UNREAL_ASSETS / "Unreal Engine Realistic Blood VFX - Niagara Blood Effects (5.0 - 5.2)" / \
    "Unreal Engine Realistic Blood VFX - Niagara Blood Effects (5.0 - 5.2)"
ROOTS = [
    ("/Game/BloodPack", BLOOD),
    ("/Game/BeamPack", UNREAL_ASSETS / "Unreal Engine Niagara Energy Beam Pack" / "BeamPack"),
    ("/Game/AdvancedARPGCombat", UNREAL_ASSETS / "Advanced ARPG Combat System V3 - Unreal Engine" / "Content" / "AdvancedARPGCombat"),
    ("/Game/Mage", UNREAL_ASSETS / "Mage Animation Pack" / "Mage Animation Pack" / "Content" / "Mage"),
    ("/Game/Deadly_Ruins", UNREAL_ASSETS / "Deadly Ruins Modular asset pack" / "Deadly Ruins Modular asset pack" /
     "Deadly_Ruins_-_Modular_asset_pack" / "data" / "Content" / "Deadly_Ruins"),
]
REF = re.compile(rb"/Game/[A-Za-z0-9_/\-]{3,}")


def package_to_source(package: str):
    """Map /Game/... to (source file, destination file); None if the package is not in a known pack."""
    for prefix, src_root in sorted(ROOTS, key=lambda r: -len(r[0])):
        if package == prefix or package.startswith(prefix + "/"):
            rel = package[len(prefix):].lstrip("/")
            if not rel:
                return None, None
            src = src_root / (rel + ".uasset")
            extension = ".uasset"
            if not src.exists() and (src_root / (rel + ".umap")).exists():
                src, extension = src_root / (rel + ".umap"), ".umap"  # a level
            dst = CONTENT / (package[len("/Game/"):] + extension)
            return src, dst
    return None, None


def source_to_package(path: Path):
    for prefix, src_root in ROOTS:
        try:
            rel = path.relative_to(src_root)
        except ValueError:
            continue
        return prefix + "/" + rel.with_suffix("").as_posix()
    return None


def main(argv):
    dry = "--dry-run" in argv
    seeds = [a for a in argv if not a.startswith("--")]
    queue = []
    for seed in seeds:
        if seed.startswith("/Game/"):
            queue.append(seed)
        else:
            for f in [*Path(seed).rglob("*.uasset"), *Path(seed).rglob("*.umap")]:
                pkg = source_to_package(f)
                if pkg:
                    queue.append(pkg)
    seen, copied, missing, total = set(), [], set(), 0
    while queue:
        pkg = queue.pop()
        if pkg in seen:
            continue
        seen.add(pkg)
        src, dst = package_to_source(pkg)
        if src is None:
            continue
        if not src.exists():
            missing.add(pkg)
            continue
        if dst.exists():
            # Already imported; its own references were handled when it was copied.
            continue
        total += src.stat().st_size
        copied.append((src, dst))
        for sibling in (".uexp", ".ubulk", ".uptnl"):
            extra = src.with_suffix(sibling)
            if extra.exists():
                copied.append((extra, dst.with_suffix(sibling)))
                total += extra.stat().st_size
        for match in REF.findall(src.read_bytes()):
            ref = match.decode("ascii").split(".")[0]
            if ref not in seen:
                queue.append(ref)
    print(f"{len(copied)} files, {total / 1048576:.1f} MB{' (dry run)' if dry else ''}")
    for src, dst in copied:
        if not dry:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    for pkg in sorted(missing):
        print("unresolved reference:", pkg)


if __name__ == "__main__":
    main(sys.argv[1:])
