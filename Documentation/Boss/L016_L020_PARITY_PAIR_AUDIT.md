# Queue L Batch 4 — A4 paired parity contract

## L016 — fixed pair definition

The existing J027 policy selects the A4 low-sweep driver as the pair candidate.
Both arms must use the same map, build/binary, content and settings digests,
declared seed, exact ordered driver arguments, and input digest. Each arm gets a
new run ID, output directory, raw log, receipt, and captured command/config
record. Pair trials by scenario ID plus zero-padded occurrence ordinal, never
by timestamp or filename order.

`pie_a4_low_sweep.py::SCENARIOS` defines the asserted trial set and repeat
counts. Pair these IDs exactly between arms:

| Source scenario | Pair IDs | Count | Classification |
|---|---|---:|---|
| `S2 grounded in front 250 cm` | `A4/S2/001`–`A4/S2/020` | 20 | Scripted hit/damage/counter outcome; exact per pair. |
| `S3 jump at 0.33 s clears it` | `A4/S3/001`–`A4/S3/020` | 20 | Scripted no-hit/jump outcome; exact per pair. |
| `S4 out of reach 520 cm` | `A4/S4/001`–`A4/S4/005` | 5 | Scripted no-hit outcome; exact per pair. |
| `S5 behind the boss 250 cm` | `A4/S5/001`–`A4/S5/005` | 5 | Scripted no-hit outcome; exact per pair. |
| `S6 backward roll at 0.50 s` | `A4/S6/001`–`A4/S6/005` | 5 | Scripted invulnerability/no-hit outcome; exact per pair. |
| `S7 reset at 0.62 s` | `A4/S7/001`–`A4/S7/003` | 3 | Reset interruption/no-hit outcome; exact per pair. |
| `S8 boss dies at 0.62 s` | `A4/S8/001` | 1 | Death interruption/no-hit outcome; exact per pair. |

The script's S1 tracker/commit/active-window/yaw checks are run once on the
first S2 trial in each driver run; compare their run-level values exactly and
retain the source log. S9 rows are explicitly information-only and are excluded
from pass counts and parity observables. The repeat counts and names above are
read from `SCENARIOS`; they are source policy, not evidence that either arm ran.

## L017–L020 — status

- **L017 legacy arm: LEAD-RUN BLOCKED.** No complete v2 run receipt and retained
  source-log pair is present.
- **L018 selected-data arm: LEAD-RUN BLOCKED.** G044 assets and the trusted
  runtime snapshot bridge are not available; no data receipt can be truthful.
- **L019 comparator: TOOL READY.** `compare_encounter_parity.py` validates the
  v2 envelope, identity, selected state, participants, observables and trial
  correspondence; `--verify-source-logs` checks retained raw bytes. No pair
  exists to run it against.
- **L020 disposition: NONE.** There are no actual mismatches to disposition.
  Synthetic fixtures and standalone legacy logs are not paired-run evidence.

No receipts were generated and no tests, build, Editor or PIE were run. Any
future missing trial or identity mismatch is INCONCLUSIVE; an actual deterministic
value mismatch remains a failure to preserve and disposition, never average out.
