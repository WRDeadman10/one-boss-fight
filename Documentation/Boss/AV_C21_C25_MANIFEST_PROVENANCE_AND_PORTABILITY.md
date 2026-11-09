# AV-C21–C25 — manifest provenance and portability

## Completed offline

- Aura manifest schema version 1 is now explicit in producer records and required by the receipt parser.
- Each row carries build ID, map, and route provenance. The validator rejects missing/unknown build or map identifiers and invalid route values. The Lead comparison driver reads `AURA_COMPARE_BUILD_ID` and `AURA_COMPARE_MAP`; these must be supplied for any run whose manifest will be accepted. Do not guess either value.
- Optional PNG hash verification uses the host's native `Path` handling. Subprocess coverage uses a temporary path with spaces and Windows separators.
- CLI JSON now identifies run, route, schema, verification mode and verified file count, with only target summaries (no image bytes). Tests cover the opt-in hash output.
- Mailbox was refreshed through C-1123: Lead reports AU-C15/AU-C10 live, but no final receipt yet. C-1123 accepted X-1592 offline; current run folders remain untouched. Owner visual choices are still open.

## Lead invocation note

For future aura comparison runs using the updated manifest schema, include the actual current build ID and active map in `-Env`, for example:

```powershell
-Env "AURA_COMPARE_BUILD_ID=<actual-build-id>,AURA_COMPARE_MAP=L_SevarogArena,AURA_COMPARE_RUN=<fresh-run-id>"
```

The current C-1123 live run may have started before this metadata change. Its output must be evaluated against the version of the driver it actually ran; this checker does not retroactively upgrade old manifests.

## Verification and limits

Focused AU/AV regression set: **87/87**. Python syntax checks and `git diff --check` pass. No Lead capture files were read, and no Unreal, Editor/PIE, build, cook, package or media render was run. Synthetic temporary files were used for hash verification only.
