# HIT-009 evaluator (lead, Claude): reads the iframe_probe lines of one or more PIE logs and judges the player's invulnerability window.
# Usage: python -I evaluate_iframe.py <out.json> <log> [<log> ...]
# Per log: the probes after the REAL dodge press (one per tick, 1 HP through the damage resolver): the Rejected probes must form ONE contiguous run (throughout the window), nothing outside it may be Rejected,
# the measured window (number of Rejected probes x the tick) must equal the AUTHORED window the iframe monitor logged for the dodge montage ((end - start) / rate, real seconds) within TOLERANCE_TICKS ticks.
# Across logs: the opening offset after the press and the length are the same (reproducible) within one tick.
import json
import re
import sys

TOL_TICKS = 2
probe = re.compile(r'iframe_probe n=(\d+) sinceDodgePress=([0-9.]+) outcome=ERPGDamageOutcome::(\w+) hpApplied=([0-9.]+)')
win = re.compile(r'invulnerable on \(dodge montage\) at ([0-9.]+) s of (\S+), rate ([0-9.]+), window ([0-9.]+) to ([0-9.]+)')


def one(path):
    rows, authored = [], None
    for n, line in enumerate(open(path, encoding='utf-8', errors='replace'), 1):
        m = probe.search(line)
        if m:
            rows.append({'line': n, 'n': int(m.group(1)), 'since': float(m.group(2)), 'outcome': m.group(3)})
        w = win.search(line)
        if w and authored is None:
            authored = {'line': n, 'montage': w.group(2), 'rate': float(w.group(3)), 'start': float(w.group(4)), 'end': float(w.group(5))}
    tick = rows[1]['since'] - rows[0]['since'] if len(rows) > 1 else 1.0 / 60.0
    rej = [i for i, r in enumerate(rows) if r['outcome'] == 'RejectedInvulnerable']
    out = {'log': path, 'probes': len(rows), 'tick': round(tick, 5), 'rejected': len(rej), 'other_outcomes': sorted({r['outcome'] for r in rows if r['outcome'] not in ('RejectedInvulnerable', 'Accepted')})}
    if not rej:
        out.update({'pass': False, 'why': 'no probe was rejected'})
        return out
    first, last = rej[0], rej[-1]
    contiguous = (last - first + 1) == len(rej)
    inside_accepted = [rows[i]['n'] for i in range(first, last + 1) if rows[i]['outcome'] != 'RejectedInvulnerable']
    out.update({'first_rejected_since_press': rows[first]['since'], 'last_rejected_since_press': rows[last]['since'], 'first_line': rows[first]['line'], 'last_line': rows[last]['line'], 'contiguous': contiguous, 'accepted_inside_window': inside_accepted,
                'accepted_before': first, 'accepted_after': len(rows) - last - 1})
    measured = len(rej) * tick
    out['measured_window_seconds'] = round(measured, 4)
    ok = contiguous and not inside_accepted
    if authored:
        real = (authored['end'] - authored['start']) / authored['rate']
        out['authored'] = authored
        out['authored_window_real_seconds'] = round(real, 4)
        out['measured_minus_authored_ticks'] = round((measured - real) / tick, 2)
        ok = ok and abs(measured - real) <= TOL_TICKS * tick
    else:
        ok = False
        out['why'] = 'no authored window line from the iframe monitor in the log'
    out['pass'] = ok
    return out


results = [one(p) for p in sys.argv[2:]]
rep = {'runs': results}
if len(results) > 1 and all('first_rejected_since_press' in r for r in results):
    opens = [r['first_rejected_since_press'] for r in results]
    lens = [r['rejected'] for r in results]
    tick = results[0]['tick']
    rep['reproducible'] = (max(opens) - min(opens) <= tick + 1e-6) and (max(lens) - min(lens) <= 1)
    rep['opening_offsets'] = opens
    rep['rejected_counts'] = lens
rep['pass'] = all(r.get('pass') for r in results) and rep.get('reproducible', True)
text = json.dumps(rep, indent=1)
print(text)
open(sys.argv[1], 'w', encoding='utf-8').write(text)
