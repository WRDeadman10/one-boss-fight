# Test-plan evidence identity audit — D118

**Scope:** verify retained BUILD-187 identity, paths, counts, result marker, source-state snapshots, and hash references against the current test plan. Read-only artifact inspection; no build or test rerun.

`TEST_PLAN.md:771` names BUILD-187 and the retained folder `Docs/BossCombatReview/Execution/Claude/B_CODEX_FINITE_C757/`. The folder contains `run_build187.ps1`, `build.log`, `suite.log`, `status.txt`, `pre_state.txt`, `post_state.txt`, and `evidence_sha256.txt`; all referenced run artifacts exist. The script's scope matches the test-plan description: C-757's three Source fixes followed by build and `Automation RunTests OneBossFight`.

`status.txt` states `BUILD exit 0; SUITE exit 0; success=335 fail=0`. Independent read-only counting of the retained `suite.log` found 335 `Result={Success}` records, 0 `Result={Fail|Error}` records, and `**** TEST COMPLETE. EXIT CODE: 0 ****`. `build.log` has the final successful link/write steps. SHA-256 of `pre_state.txt` and `post_state.txt` matches (`FCF4854F3307CCA1ED6E8D459D99E167CCAB3263D174B980404350169DEC2A95`), consistent with no Source status drift during the run.

The run bundle's `evidence_sha256.txt` exists but is **0 bytes**, despite the script's final `Get-FileHash`/`Out-File` command. Thus BUILD-187's log/count/exit claims are supported by retained raw files, but the bundle contains no hash manifest binding those files or a compiled binary to this run. Read-only hashes computed during this audit: `build.log` `1B38BF784D411DA00E0A57536DB4C9429F3BAB117573EFD4EC72583B4673BCEC`; `suite.log` `29E656960B9644C0F65943532D8E21FC232DE12D50811141E748298972012EA1`. These audit values are recorded here; the original run bundle was not modified.

The stale unchecked C-757 “Lead validation pending” row in `TEST_PLAN.md` was corrected to BUILD-187 Lead-verified, and the D105–D110 rows that had described the extra selector/executor reports were relabeled as out-of-order extras. The actual numbered D105–D110 tasks are now identified as the telegraph, music, hit-stop, approach, arena-edge, and MoveCard-ID audits. Earlier BUILD-182/183–186 records remain historical and are labeled by their dates/supersession; they are not the latest suite identity.

**Acceptance result:** BUILD-187's path, run scope, exit status, 335/0 counts, complete marker, and unchanged Source-state snapshots agree. The zero-byte hash manifest is an evidence packaging gap; no execution was repeated and no run artifacts were changed.
