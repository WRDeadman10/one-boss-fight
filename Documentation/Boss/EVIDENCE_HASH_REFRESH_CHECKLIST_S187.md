# Evidence hash refresh checklist (S187)

Use separate identities for source, build artifacts, and run evidence. A matching source hash does not mean the binary or evidence stayed the same; a new build from unchanged source is still a new build artifact.

## Refresh rules

| Change since last handover | Source manifest | Build/package hashes | Run evidence manifest | Handover wording |
|---|---|---|---|---|
| Source files changed, no rebuild | Generate a new, dated `make_source_manifest.py` output and compare it with the prior snapshot. | Keep the prior binary digest labeled as the last built artifact; mark it stale relative to changed source. Do not imply the new source was built. | Existing run evidence remains tied to its original source/build; do not reuse it as proof of the changed source. | “Source changed; no build/run against this source.” |
| Rebuild with identical Source manifest | Record the same source-manifest digest for traceability. The tool covers `Source/` only, so note relevant content/config deltas separately. | Recompute SHA-256 for every newly produced executable and package artifact used by the run, plus the build log. Assign a new build ID even if the source digest matches. | Any new suite/PIE/package run gets its own command, result, raw logs, and a newly generated evidence manifest. | “Same source fingerprint; new build artifact (BUILD ID, configuration, binary/package hashes).” Do not call it an unchanged build. |
| No source, build, package, or run artifact changed | No refresh required. If needed, compare existing manifests read-only. | Keep the existing build ID and digests. | Keep the original run manifest unchanged. | “No new build or run; prior evidence artifacts remain byte-identical.” |
| New suite, PIE, or packaged run without a code change | Source digest stays the same; cite it. | Cite the exact binary/build ID used; hash again only if the artifact itself changed. | Capture a new run ID and hash its exact command/result/raw logs. Never overwrite the prior run folder or manifest. | “New run against build X, source fingerprint Y.” |
| Any retained evidence file was edited, replaced, or copied differently | No source refresh unless source changed. | No build refresh unless build artifacts changed. | The old manifest is now stale. Preserve it as the record of the prior bytes; make a distinct corrected/new run bundle and manifest. Never rewrite the old hash list to erase the mismatch. | State which artifact changed and keep the old run's status/history. |

## Capture checklist for a handover

1. Give each source snapshot, build, and run its own stable ID. Record commit/revision when available, but a commit label is not a byte hash.
2. Generate a new source snapshot without replacing the prior one:

   ```powershell
   python -I Scripts/Tools/make_source_manifest.py Docs\BossCombatReview\Execution\Claude\<RUN_ID>\source_sha256.txt --root .
   ```

   This tool hashes files under `Source/` only. Content assets, project config, plugins, and generated package outputs need separate artifact identity; do not treat the Source manifest as a whole-project fingerprint.
3. For the exact built executable and package files used, record path, configuration, size, last-write time, and SHA-256 (for example, `Get-FileHash -Algorithm SHA256`). Hash the game binary inside the package as well as the launcher when both matter. Do not infer a new build from an unchanged source digest.
4. For each suite/PIE/package run, preserve the exact command, result, raw log, map/profile/configuration, and build ID together. Generate `evidence_sha256.txt` after copying the final bytes; then verify it read-only with `python Scripts/Tools/check_evidence_sha256.py .` where the bundle is covered by that checker.
5. In the handover, explicitly say whether source is unchanged, whether a new build was produced, and whether a new run was executed. A source match with a new binary is **same source/new build**. If neither binary nor logs changed and no run occurred, it is **unchanged evidence**, not a fresh validation.

Hashes establish byte identity only. They do not establish which source produced a binary, that the log is complete, that a test passed, or that a gameplay claim is proven; connect artifacts through the recorded build/run IDs and report the actual validation separately.
