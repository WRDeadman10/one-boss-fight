"""Masks ONLY the per-run epoch GUID and the UTS sponsor PID in Warning lines, then compares run A (preimage) with run B (accepted 2b)."""
import re
ROOT = r"C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\DD2b\ab_2026-10-27"
TS = re.compile(r"^\[[0-9.\-:]+\]\[[ 0-9]+\]")
def warns(tag):
    out = []
    for l in open(ROOT + r"\automation_%s_plus_test.log" % tag, encoding="utf-8", errors="replace"):
        l = TS.sub("", l.rstrip("\r\n"))
        if ": Warning:" in l:
            l = re.sub(r"epoch=[0-9A-F]{32}", "epoch=<GUID>", l)
            l = re.sub(r"--sponsor \d+", "--sponsor <PID>", l)
            out.append(l)
    return out
a, b = warns("A_preimage"), warns("B_accepted2b")
print("masked warning lists identical (order and content):", a == b, "count A", len(a), "count B", len(b))
