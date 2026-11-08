# Queue AC AC-C16–AC-C20 — importer, montage trim, and cook evidence

Mailbox review for this batch was through A-592/C-981. Its task-time findings are retained below; later C-985/C-986 status is reconciled in `AC_C46_C50_FINAL_CROSSCHECK_HANDOFF.md`. Static review and focused importer fixture only; no Editor, import, asset save, build, or cook by Codex.

## AC-C16 — importer preflight and no-overwrite

- `import_er_clips.py` requires explicit `IMPORT_CLIPS`, unique known IDs/names, GATE-07 acceptance, a loadable target skeleton, and per-target FBX source. It sets `replace_existing=False`, `save=False`, checks the exact destination before import, validates class/skeleton/length, then saves only after those checks.
- Hotfix in this batch moves validation of every requested target and source ahead of destination-directory creation or any import. This prevents a missing later source from leaving earlier clips imported. The exact-target existence check repeats immediately before each import.
- The Editor script does not itself verify `ENGINE_LOCK.json`; an operator must honor the team lock before launching it. Its header claims a non-empty-track assertion that the implementation does not currently perform; class/skeleton/duration checks are present.
- Failure status was incorrect: the Editor tail called `os._exit(0)` even after `run_import()` returned false. It now exits 1 on failure and 0 on success. This is source-path/static verified only; not executed in Unreal.

## AC-C17 — malformed registry fixtures

The registry parser now requires the complete eight-column GATE-07 row shape, a non-empty status cell, and a unique row per ER ID. Duplicate, malformed-pipe, or missing-status rows fail closed for that ID. The offline fixture covers these negatives alongside delivered-only and NOT/PENDING/UN- prefix refusals.

Focused command: `python -m unittest Scripts.Tools.test_import_er_clips -q` — 11 tests passed. Importing this Editor script outside Unreal also prints its expected “Must be executed inside Unreal Engine editor environment” error from the module-level runner; the fixture suite still exits 0. Python AST parse passed.

## AC-C18 — trim-tool safeguards

Reviewed `trim_guard_counter_montage.py`, `trim_backstep_montage.py`, and `trim_air_montages.py`:

| Tool | Existing-asset behavior | Assertions before save | Lock/source gaps |
|---|---|---|---|
| GuardCounter | Loads a fixed existing path; does not create or replace a montage | Helper bool and resulting length 0.8000 s | No script-side lock guard, class/skeleton assertion, or AN source identity/length check |
| Backstep | Loads fixed montage path; reads sequence only if it exists | Helper bool and length 0.4667 s; then GuardCounter length readback 0.8000 s | Missing sequence is logged but does not abort; no script-side lock guard or montage class/skeleton assertion |
| Air montages | Loads fixed existing montage paths | Helper bool and per-montage expected lengths; each is saved before proceeding to the next | No script-side lock guard or class/skeleton assertion; source sequence absence becomes logged length 0.0 and does not block trim; a later heavy failure can leave the already-saved light trim |

These are in-place authoring scripts, so overwrite refusal is not their contract. Their intended safe boundary relies on the shared ENGINE_LOCK and current callers; the scripts themselves do not enforce it. No Editor execution occurred.

## AC-C19 — source sequence duration vs accepted montage slice

Found a metadata mismatch: importer `CLIPS.duration/frames` represented montage active-slice lengths for GuardCounter and AirLight/AirHeavy, while the import assertion measures the full AnimSequence. Mailbox evidence: A-584 says GuardCounter source AN is 50 frames/1.6667 s with accepted F10..F34/0.8000 s; A-590 says AirLight/AirHeavy ANs are each 1.4000 s while accepted montage slices are 0.5667/0.8667 s. Updated importer metadata to source-sequence values: A1 0.4667/15f, A4 1.6667/50f, A3/A2 1.4000/42f. Montage slice values remain in GATE-07 and the trim scripts. A source contract fixture now guards this distinction.

## AC-C20 — asset type and cook boundary

- Import script validates imported animation type as `AnimSequence`, skeleton binding, and source duration. Montage construction is a separate operation; A-589/A-590 provide trim/readback reports for four `AnimMontage` assets, but those receipts are distinct from the `AnimSequence` import check.
- C-978 BUILD-248 is a native automation/build and Shipping compile receipt, not proof that a staged package contains the ER or Tier 2 assets. BUILD-246 CookCoverage verifies its stated root only. A-591 created Tier 2 assets; A-592 files now exist under `Docs/BossCombatReview/Execution/Antigravity/Tier2_Art/` (recoil strip/MP4, distortion and aura before/after PNG pairs), plus an MPC parameter list. The later C-985 review accepts A-594 previews for owner review; owner review and Lead runtime/cook verification remain pending. C-986 finds zero notifies on all five new montages; see KI-193 and the C-986 hotfix table.
- Keep optional fields unassigned until the owner gates clear; an on-disk `.uasset`, animation preview, or config root does not prove runtime wiring or package inclusion.
