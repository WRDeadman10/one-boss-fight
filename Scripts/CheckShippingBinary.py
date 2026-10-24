"""Gate 4 G4-3: the staged Shipping binary must not contain the debug names (Documentation/GATE4_RUNBOOK.md, "Shipping Debug-Off Verification").
A Shipping build writes no log (logging is compiled out and the project does not enable it), so the debug-off check is a search of the executable for the names of the project's debug console variable and debug log category,
in ASCII and UTF-16. Usage: python -I Scripts/CheckShippingBinary.py [path to OneBossFight-Win64-Shipping.exe]. Exit 0 = none found."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT = ROOT / 'Saved' / 'StagedBuilds' / 'Windows' / 'OneBossFight' / 'Binaries' / 'Win64' / 'OneBossFight-Win64-Shipping.exe'
# DrawDebugCircle is not searched: it is also the name of an Engine function (UKismetSystemLibrary), so it is always in the binary; the project's own call is inside #if !UE_BUILD_SHIPPING (RPGBossShockwave.cpp).
NAMES = ['rpg.Debug', 'LogRPGDebug']


def main():
    exe = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    if not exe.is_file():
        print('FAIL no Shipping executable at %s' % exe)
        return 1
    data = exe.read_bytes()
    found = []
    for name in NAMES:
        for label, needle in (('ascii', name.encode('ascii')), ('utf-16', name.encode('utf-16-le'))):
            at = data.find(needle)
            if at >= 0:
                found.append((name, label, at))
    print('binary: %s (%d bytes)' % (exe, len(data)))
    for name in NAMES:
        hits = [f for f in found if f[0] == name]
        print('%-18s %s' % (name, ('FOUND %s at offset %d' % (hits[0][1], hits[0][2])) if hits else 'absent'))
    print('VERDICT %s' % ('FAIL: debug names present' if found else 'PASS: no debug names in the Shipping binary'))
    return 1 if found else 0


if __name__ == '__main__':
    sys.exit(main())
