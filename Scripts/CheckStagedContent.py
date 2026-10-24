#!/usr/bin/env python3
"""Check C++ /Game asset literals against Content and a staged UFS manifest."""

import argparse
import os
import re
import sys
from collections import defaultdict
from pathlib import Path


STRING_PATH = re.compile(r'["\'](/Game/[A-Za-z0-9_./]+)["\']')
LINE_COMMENT = re.compile(r'//[^\n]*')
BLOCK_COMMENT = re.compile(r'/\*.*?\*/', re.DOTALL)


def strip_comments(text):
    """Remove comments without needing to interpret the Unreal C++ grammar."""
    return LINE_COMMENT.sub('', BLOCK_COMMENT.sub('', text))


def package_path(raw):
    raw = raw.rstrip('/')
    if not raw:
        return None
    leaf = raw.rsplit('/', 1)[-1]
    if '.' not in leaf:
        return None
    return raw.rsplit('.', 1)[0]


def source_packages(root):
    found = defaultdict(set)
    for path in sorted((root / 'Source' / 'OneBossFight').rglob('*')):
        if path.suffix not in {'.cpp', '.h'}:
            continue
        text = strip_comments(path.read_text(encoding='utf-8', errors='replace'))
        for raw in STRING_PATH.findall(text):
            package = package_path(raw)
            if package:
                found[package].add(path.relative_to(root).as_posix())
    return found


def content_file(root, package):
    relative = package.removeprefix('/Game/')
    base = root / 'Content' / relative
    for suffix in ('.uasset', '.umap'):
        candidate = base.with_suffix(suffix)
        if candidate.is_file():
            return candidate
    return None


def stable_manifest(path):
    before = path.stat()
    text = path.read_text(encoding='utf-8', errors='replace')
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise RuntimeError('manifest changed while it was read: %s' % path)
    return {line.split('\t', 1)[0].replace('\\', '/').lower() for line in text.splitlines() if line.strip()}


def staged_name(package, source):
    relative = package.removeprefix('/Game/')
    return ('OneBossFight/Content/' + relative + source.suffix).lower()


def group(package):
    return package.rsplit('/', 1)[0]


def print_grouped(title, packages):
    print('%s: %d' % (title, len(packages)))
    for folder in sorted({group(package) for package in packages}):
        names = sorted(package for package in packages if group(package) == folder)
        print('  %s (%d)' % (folder, len(names)))
        for package in names:
            print('    %s' % package)


def main():
    root = Path(__file__).resolve().parent.parent
    default_manifest = root / 'Saved' / 'StagedBuilds' / 'Windows' / 'Manifest_UFSFiles_Win64.txt'
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=default_manifest)
    args = parser.parse_args()
    manifest = args.manifest if args.manifest.is_absolute() else (root / args.manifest)

    packages = source_packages(root)
    existing, missing_source = {}, []
    for package in sorted(packages):
        source = content_file(root, package)
        if source is None:
            missing_source.append(package)
        else:
            existing[package] = source
    print('referenced_asset_packages: %d' % len(packages))
    print('source_assets_present: %d' % len(existing))
    print_grouped('source_assets_missing', missing_source)

    if not manifest.is_file():
        print('manifest_missing: %s' % manifest)
        return 1
    try:
        staged = stable_manifest(manifest)
    except (OSError, RuntimeError) as exc:
        print('manifest_unreadable: %s' % exc)
        return 1
    missing_staged = [package for package, source in existing.items() if staged_name(package, source) not in staged]
    print('manifest_entries: %d' % len(staged))
    print('staged_assets_present: %d' % (len(existing) - len(missing_staged)))
    print_grouped('staged_assets_missing', missing_staged)
    return 1 if missing_source or missing_staged else 0


if __name__ == '__main__':
    raise SystemExit(main())
