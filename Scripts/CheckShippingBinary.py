"""Gate 4 G4-3: the staged Shipping binary must not contain the debug names (Documentation/GATE4_RUNBOOK.md, "Shipping Debug-Off Verification").
A Shipping build writes no log (logging is compiled out and the project does not enable it), so the debug-off check is a search of the executable for the names of the project's debug console variable and debug log category,
in ASCII and UTF-16. Usage: python -I Scripts/CheckShippingBinary.py [path to OneBossFight-Win64-Shipping.exe]. Exit 0 = none found."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / 'Scripts' / 'Tools'
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
import shipping_cvar_expectations

DEFAULT = ROOT / 'Saved' / 'StagedBuilds_Shipping' / 'Windows' / 'OneBossFight' / 'Binaries' / 'Win64' / 'OneBossFight-Win64-Shipping.exe'
# DrawDebugCircle is not searched: it is also the name of an Engine function (UKismetSystemLibrary), so it is always in the binary; the project's own call is inside #if !UE_BUILD_SHIPPING (RPGBossShockwave.cpp).
NAMES = ['rpg.Debug', 'LogRPGDebug']


def scan_binary(data: bytes, source_root: Path):
    exp = shipping_cvar_expectations.expectations(source_root)
    cvar_names = set(exp['expected_absent']) | set(exp['unknown'])
    scan_names = set(NAMES) | cvar_names
    hits = {}
    found_cvars = set()
    for name in sorted(scan_names):
        for label, needle in (('ascii', name.encode('ascii')), ('utf-16', name.encode('utf-16-le'))):
            at = data.find(needle)
            if at >= 0:
                hits.setdefault(name, []).append((label, at))
                if name in cvar_names:
                    found_cvars.add(name)
    cvar_problems = shipping_cvar_expectations.violations(found_cvars, exp)
    debug_hits = {name: offsets for name, offsets in hits.items() if name in NAMES}
    return exp, hits, cvar_problems, debug_hits


def main():
    exe = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    if not exe.is_file():
        print('FAIL no Shipping executable at %s' % exe)
        return 1
    data = exe.read_bytes()
    exp, hits, cvar_problems, debug_hits = scan_binary(data, ROOT)
    print('binary: %s (%d bytes)' % (exe, len(data)))
    print('CVar expectations: %d expected absent, %d expected present, %d unknown' %
          (len(exp['expected_absent']), len(exp['expected_present']), len(exp['unknown'])))
    for name in sorted(set(NAMES) | set(exp['expected_absent']) | set(exp['unknown'])):
        name_hits = hits.get(name, [])
        summary = 'FOUND %s at offset %d' % name_hits[0] if name_hits else 'absent'
        print('%-48s %s' % (name, summary))
    for problem in cvar_problems:
        print('FAIL %s' % problem)
    for name, name_hits in sorted(debug_hits.items()):
        print('FAIL debug name present: %s at %s offset %d' % (name, name_hits[0][0], name_hits[0][1]))
    failed = bool(cvar_problems or debug_hits)
    print('VERDICT %s' % ('FAIL: Shipping binary contains forbidden debug/CVar names' if failed
                          else 'PASS: no forbidden debug/CVar names in the Shipping binary'))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
