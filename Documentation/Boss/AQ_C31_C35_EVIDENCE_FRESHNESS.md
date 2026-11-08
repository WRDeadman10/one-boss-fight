# AQ-C31–C35 — evidence freshness and identity

This inventory treats file timestamps and hashes as artifact metadata, not as
proof that a file's reported result is true. Raw evidence and media were read
only. `current` below means relevant to the current decision, not that an
unselected option is accepted or visually approved.

## Camera evidence

| Evidence | Observed identity and freshness | Current claim boundary |
|---|---|---|
| `B_C1088_LOCKON2/` | `status.txt` says BUILD-269, exit 0, suite 487/487. Its `evidence_sha256.txt` hashes `build.log`, `pre_state.txt`, `post_state.txt`, `run_build269.ps1`, and `suite.log`. Directory timestamps are 2026-11-08 15:29–15:31 UTC. | Fresh build/suite receipt; hashes do not cover the edited C++ source or binary. `pre_state`/`post_state` list modified file paths but no source-content hashes or commit ID. This build receipt alone is not C's camera runtime result. |
| `P_C1079_BOSSBLOCKS/engage7_*` | Eight route/config/speed log pairs are present; the two C-on 0.35 runs report timestamps 15:38:46–15:40:35 UTC and explicit legacy/data routes. `status_engage7.txt` says both routes finished. | Current C-specific PIE samples for the listed cases; they are not B+C runs. Logs contain no immutable source revision/hash field, so exact source identity remains missing. |
| `P_C1090_ATTACKCAM/` | Six attack-mode route/config logs finished at 16:19–16:25 UTC on BUILD-269; status names both routes and all off/B/B+C cases. The logs show nine A4/A6 starts and zero refusals per run. | Current B+C evidence for this tested attack-mode/speed-1.0 case: C-1090 reports 0 intrusion samples and 36–37° view-to-boss median. Off reports 9–10 capsule intrusion samples; B reports four hides/run at 96–104 cm. No source hash/immutable revision field; this does not fill the other matrix cells or prove package behavior. |
| `B_C1080_HIDEINSIDE/`, `B_C1083_LOCKON/`, `B_C1085_CAMFIX/` | Historical individual option/build evidence directories referenced by the current proposal and Lead handoff. | Retain as historical lineage; do not substitute their distinct scenarios for BUILD-268/269 or a combined run. |

Claude's C-1088 reports B and C passed their tested scenarios on both routes;
C-1090 adds one B+C attack-mode case on both routes, and the owner choice is
still pending. The current [camera proposal](CAMERA_MELEE_OCCLUSION_PROPOSAL.md)
and [matrix](AQ_C11_C15_BC_MATRIX.md) now record that limited result. Other
attack/lunge, broader terrain/input, and package gates remain open. No stale
claim of a selected shipped option was found.

## Tier 2 aura choice evidence

| Evidence | Observed identity and freshness | Current claim boundary |
|---|---|---|
| `P_C1072_AURACOMPARE/` | `status.txt` says legacy/data finished. The latest line captures are timestamped 12:28–12:29 UTC; `probe_data_lines.txt` records all three warmup frames at mean gray 0.000, the approved frame at 0.000, then an error and an error-summary. | These are failed/black comparison captures, not usable visual evidence. A completed script status does not erase its error or validate an image. No source hash/immutable build identity was found in the status receipt. |
| `P_SHOWCASE/aura_options.mp4`, `aura_compare.png`, `showcase_aura1.log` | Files are timestamped 12:32–12:33 UTC. `status_aura1.txt` says finished with 72 frames. | Claude's showcase demonstrates visible current, boost-at-origin and boost-on-spine presentation in that capture, but is not an owner selection. No owner disposition is recorded by the current KI-191 row. |

The current `KNOWN_ISSUES.md` KI-191 and C-1077/C-1075 handoffs distinguish
the black comparison from the separate showcase. No accepted owner choice was
found; all three options remain candidates. The offline AQ-C16–C20 planner
does not change that boundary.

## C32–C33 reconciliation

- Build labels and route names are present in status/log files, but a build
  label is not a source revision. The camera build receipt hashes its logs and
  state manifests, not source files. The C PIE and aura status files provide
  completion summaries without source hashes.
- Camera C-on legacy/data timestamps align with the contemporaneous C-1088
  mailbox report; the current proposal reports the same medians/p90 and IA_Look
  observations. The C-1090 route logs align with the subsequent both-route B+C
  verdict; owner choice and non-tested matrix cells remain open.
- Aura script `finished=True` on both routes conflicts with the data route's
  logged black frames and error. The current KI-191 disposition correctly
  remains PARTIAL and says the paired comparison has no accepted result.
- Timestamp recency does not upgrade proof quality. Missing source identity,
  invalid visuals, owner selection, and package evidence stay open.

## Offline classifier and limitations

`Scripts/Tools/aq_evidence_freshness.py` classifies a supplied manifest row as
CURRENT, STALE, MISSING_IDENTITY, or MISMATCH. It requires explicit build,
route, and timezone-qualified timestamp; it does not infer missing fields from
folder names or adjacent artifacts. The fixture suite covers those four cases.
This small classifier is not a parser for Unreal logs, a source-hash verifier,
or a verdict generator for the evidence inventoried above.
