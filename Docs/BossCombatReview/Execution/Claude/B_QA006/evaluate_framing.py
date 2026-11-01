# QA-006 evaluator (lead, Claude): reads the camera_frame lines of a PIE log and judges the boss's framing on the player's screen per distance band.
# Usage: python -I evaluate_framing.py <editor_raw.log> [out.json]
# Bands (cm, design values, proposed): near 100..160 (the fight band), 260..340, 560..640, 860..940. A sample counts for a band when its distance lies inside it and the camera has SETTLED (the last SETTLE samples of a stage are used: the camera spring arm lags a teleport).
# Thresholds (design values, proposed): the whole boss box inside the viewport with a 5 percent margin at every band; the boss covers at least 12 percent of the screen height at the farthest band (and at least that everywhere); no occlusion of the camera-to-chest line.
import json
import re
import sys

BANDS = [('near', 100, 160), ('300', 260, 340), ('600', 560, 640), ('900', 860, 940)]
MIN_HEIGHT_PCT = 12.0
SETTLE = 3   # samples (0.75 s) at the end of a stage

pat = re.compile(r'camera_frame t=([0-9.]+) distCm=([0-9.]+) screenMinX=([-0-9.]+) screenMinY=([-0-9.]+) screenMaxX=([-0-9.]+) screenMaxY=([-0-9.]+) viewX=(\d+) viewY=(\d+) cornersOnScreen=(\d+) insideMargin=(\d) heightPct=([0-9.]+) occluded=(\d)')
rows = []
for n, line in enumerate(open(sys.argv[1], encoding='utf-8', errors='replace'), 1):
    m = pat.search(line)
    if m:
        g = m.groups()
        rows.append({'line': n, 't': float(g[0]), 'dist': float(g[1]), 'inside': int(g[9]), 'height': float(g[10]), 'occluded': int(g[11]), 'corners': int(g[8]), 'view': (int(g[6]), int(g[7]))})
report = {'samples': len(rows), 'bands': {}, 'min_height_pct_threshold': MIN_HEIGHT_PCT}
ok_all = True
for name, lo, hi in BANDS:
    inb = [r for r in rows if lo <= r['dist'] <= hi]
    # settled samples: the last SETTLE of each run of consecutive in-band samples
    runs, cur = [], []
    for r in rows:
        if lo <= r['dist'] <= hi:
            cur.append(r)
        elif cur:
            runs.append(cur); cur = []
    if cur:
        runs.append(cur)
    settled = [r for run in runs for r in run[-SETTLE:]]
    if not settled:
        report['bands'][name] = {'samples': 0, 'pass': False, 'why': 'no samples in this band'}
        ok_all = False
        continue
    inside = all(r['inside'] == 1 for r in settled)
    occl = any(r['occluded'] == 1 for r in settled)
    hmin = min(r['height'] for r in settled)
    passed = inside and not occl and hmin >= MIN_HEIGHT_PCT
    ok_all = ok_all and passed
    report['bands'][name] = {'samples_in_band': len(inb), 'settled_samples': len(settled), 'all_inside_margin': inside, 'any_occluded': occl, 'min_height_pct': round(hmin, 2),
                             'first_line': settled[0]['line'], 'last_line': settled[-1]['line'], 'viewport': settled[0]['view'], 'pass': passed}
report['pass'] = ok_all
out = json.dumps(report, indent=1)
print(out)
if len(sys.argv) > 2:
    open(sys.argv[2], 'w', encoding='utf-8').write(out)
