# Queue AM C46–C50: offline handoff

## Census and validation

`QUEUE_AM.md` contains exactly AM-C01 through AM-C50, 50 unique IDs with no gap or duplicate, grouped in ten batches of five. Each row has a file target and acceptance text. All ten offline batches have receipts; live/owner gates below remain open. This pass ran 25 scoped offline Python tests, compiled the relevant Python probes/tools, checked documentation links (`broken_links=0`) and `git diff --check` (no whitespace errors). Codex did not run Unreal Editor, build, PIE, package, commit, or push.

## Current Lead evidence

- C-1042: both-route aura lifecycle 6/6, default-wired ground/air damage 4/4, and visible PPM RGB split with steady frames. KI-191 retains first-use/package gates; KI-193 retains package proof.
- C-1044: camera open-ground 105/200/300 cm trace has full arm, no boss hit, capsule Camera ignore. No camera Source change. KI-037/KI-066 retain composition and broader coverage.
- C-1045: BUILD-259 485/485; both-route A4 block, arm, R2 and GuardCounter montage play with full player HP. Boss HP stayed 2000 at 250 cm. C-1045 revised probe starts at 140 cm and logs hand reach; KI-198 needs a damaging both-route counter result.
- C-1030 BUILD-255 full-fight MP4 has six black lead-in source frames and lacks Tier 2/counter proof. Trim-six ffconcat/ASS inputs are prepared, with no new MP4. All seven owner full-fight boxes remain unchecked.

## Next gates

1. Lead reruns `pie_er_a4_guard_counter.py` at 140 cm on legacy/data and checks blocked contact, real arm, `StrongMeleeAttackData`, counter montage and boss HP delta. If no hit, use `COUNTER_REACH` and the trace window to diagnose. KI-198 remains open until both routes pass.
2. Lead runs the no-assignment standing/moving dodge probe for KI-196, then package checks for KI-191/KI-193. The separate-stage identity preflight passed only existing roots; `Package.ps1` still has a shared staging root, KI-197 pending a distinct-root contract before the next dual build.
3. After the guard hit is proven, Lead may opt into a new Tier 2 full-fight capture with separate frame root. Render and link only a verified new MP4; owner reviews seven full-fight rows. The original BUILD-255 video remains the current link.
4. Any melee camera composition change requires owner direction and runtime wall/floor/dodge/phase-two visual proof. No collision fix is justified by C-1044 open-ground samples.

No new owner decision is needed for the current offline handoff. The next concrete input is Lead's C-1045 probe receipt.
