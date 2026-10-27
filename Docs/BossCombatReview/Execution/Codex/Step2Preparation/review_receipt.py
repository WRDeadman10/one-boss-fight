"""Read-only raw-file receipt; observational hashes, never acceptance or history rewriting."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[5]

def collect_receipt(root, claims):
    root = root.resolve(strict=True)
    rows, errors, seen = [], [], set()
    if not isinstance(claims, list) or not claims:
        return {'files': [], 'errors': ['nonempty list of file paths/claims required']}
    for claim in claims:
        expected = None
        if isinstance(claim, str):
            relative = claim
        elif isinstance(claim, dict):
            relative, expected = claim.get('path'), claim.get('sha256')
            if not isinstance(expected, str) or not re.fullmatch(r'[0-9a-fA-F]{64}', expected):
                errors.append('invalid expected SHA256 for ' + str(relative)); continue
        else:
            errors.append('claim must be path string or path/sha256 object'); continue
        if not isinstance(relative, str) or not relative:
            errors.append('missing path'); continue
        path = Path(relative)
        if path.is_absolute() or path.drive or '..' in path.parts or ':' in relative:
            errors.append('non-project-relative path refused: ' + relative); continue
        try:
            actual_path = (root / path).resolve(strict=True)
            if not actual_path.is_relative_to(root):
                errors.append('resolved path escapes root: ' + relative); continue
            identity = str(actual_path).casefold()
            if identity in seen:
                errors.append('duplicate resolved path: ' + relative); continue
            seen.add(identity)
            if not actual_path.is_file():
                errors.append('not a file: ' + relative); continue
            data = actual_path.read_bytes()
        except (OSError, ValueError) as exc:
            errors.append('unreadable path: ' + relative + ' (' + type(exc).__name__ + ')'); continue
        digest = hashlib.sha256(data).hexdigest()
        row = {'path': actual_path.relative_to(root).as_posix(), 'bytes': len(data),
               'sha256': digest, 'expected_sha256': expected,
               'matches_claim': None if expected is None else digest == expected.lower()}
        rows.append(row)
        if row['matches_claim'] is False:
            errors.append('SHA256 mismatch: ' + relative)
    return {'scope': 'raw bytes observed now; not authorship, runtime proof, approval or future immutability',
            'files': rows, 'errors': errors}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', nargs='*')
    parser.add_argument('--claims-stdin', action='store_true', help='Read JSON list of path/sha256 claims from stdin')
    args = parser.parse_args()
    if args.claims_stdin and args.paths:
        parser.error('choose paths OR --claims-stdin')
    try:
        claims = json.load(sys.stdin) if args.claims_stdin else args.paths
        receipt = collect_receipt(ROOT, claims)
    except (ValueError, OSError) as exc:
        receipt = {'files': [], 'errors': ['input failure: ' + type(exc).__name__]}
    print(json.dumps(receipt, indent=2))
    return 1 if receipt['errors'] else 0

if __name__ == '__main__':
    raise SystemExit(main())
