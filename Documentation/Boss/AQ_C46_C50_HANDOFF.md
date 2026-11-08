# AQ-C46–C50 — offline queue closeout and Lead handoff

## Queue and scope audit

`Documentation/Boss/QUEUE_AQ.md` contains **50 task rows**, **50 unique IDs in order (AQ-C01 through AQ-C50)**, ten five-task groups, and no blank acceptance descriptions. The queue is complete as an offline Codex work cycle. Completion of its docs/contracts does not close Lead runtime, owner-choice, camera-KI, aura-visual, or package gates.

All ten batch summaries are in the queue's Progress section. Batch evidence is indexed in:

- `AQ_C01_C05_CAMERA_PROBE.md` and `AQ_C06_C10_ATTACK_LUNGE_PROBE.md`
- `AQ_C11_C15_BC_MATRIX.md`
- `AQ_C16_C20_AURA_CHOICE_PREP.md`
- `AQ_C21_C25_PACKAGE_GATES.md` and `AQ_C26_C30_OPEN_KI_TRIAGE.md`
- `AQ_C31_C35_EVIDENCE_FRESHNESS.md`
- `AQ_C36_C40_CAMERA_BOUNDARY_AUDIT.md` and `AQ_C41_C45_FINAL_AUDIT.md`

The maintained driver is `Scripts/Editor/pie_camera_engage.py`. It supports `CAM_MODE=orbit|away|retreat|fixed|attack`, bounded `CAM_SPEED` (0–1), optional `CAM_LOOK_TEST=1`, `CAM_ATTACK_MOVES` (default `A4,A6`), and whitelisted `CAMERA_CVARS`. The attack case starts the tracker moves while in its 80–150 cm band. Claude's external run starts the Editor; the driver requests PIE and actively steers/injects test actions once loaded. Keep each route/config case in a fresh process. The README-level run protocol and limitations are in C06–C10 and C11–C15; no Codex PIE run is claimed here.

## Scoped verification

Final AQ checks:

```text
python -m unittest Scripts.Editor.test_pie_camera_engage_contract Scripts.Editor.test_prepare_aura_choice Scripts.Tools.test_aq_package_gates Scripts.Tools.test_aq_evidence_freshness
python -m py_compile Scripts/Editor/pie_camera_engage.py Scripts/Editor/test_pie_camera_engage_contract.py Scripts/Editor/prepare_aura_choice.py Scripts/Editor/test_prepare_aura_choice.py Scripts/Tools/aq_evidence_freshness.py Scripts/Tools/test_aq_evidence_freshness.py Scripts/Tools/test_aq_package_gates.py
python Scripts/Tools/check_doc_links.py .
git diff --check
```

Results: **24/24 tests passed**, Python syntax **PASS**, `broken_links=0`, and diff check **exit 0** (LF-to-CRLF notices only). These are offline checks. No Unreal Editor, PIE, build, native test, cook, package, commit, or push was performed by Codex.

## Latest Lead/owner gates

- Mailbox C-1092 accepted X-1531/X-1532 and says the fixed band metrics passed Lead's 10/10 probe contracts and py_compile. It noted a live rerun waits for the next camera run. X-1533/X-1534 were posted afterward; no later review or rejection was present at this audit.
- C-1090's BUILD-269 combined B+C result is limited to attack mode A4/A6 at default speed on both routes: nine tracker starts/run, no refusals, zero sampled geometry-proxy intrusions, and 36–37° reported view-to-boss median. It is not full-matrix, hit/damage, visual readability, package, or Shipping proof. The remaining matrix rows in C11–C15 are pending.
- The owner has not chosen B, C, or B+C. No `RPGCameraRig` Source or camera config change is authorized by the recorded choice; the camera experiment remains Development-only and off by default. KI-037/KI-066 and package verification remain open.
- The aura comparison's black frames remain invalid for visual selection; the separate showcase does not record an owner disposition. The dry-run planner does not apply or save the candidate.
- Package requirements and KI status distinctions remain in `AQ_C21_C25_PACKAGE_GATES.md` and `KNOWN_ISSUES.md`; no package run is claimed.

## Next action

The offline AQ queue is closed. The next project actions are owner selection of a camera direction and Claude's next identified camera PIE run against the still-pending matrix; only after selection should Claude stage the chosen Development package and perform its separate package gates. No successor Codex queue is implied by this closeout.
