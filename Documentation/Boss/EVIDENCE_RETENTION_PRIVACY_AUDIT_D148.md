# D148 — evidence retention privacy audit

Date: 2026-11-03  
Scope: retained benchmark bundles and maintained offline reporting/copy tools. Read-only source and content-pattern review; no evidence was regenerated or copied.

## Findings

- No obvious credential-shaped fields were found in the maintained `Scripts/Tools` and `Scripts/SummarizeBenchmark.py` sources, the 20 `Documentation/PerfCaptures` summaries, or the retained `Saved/bench_return` benchmark bundles. The scan checked common API/access/refresh-token labels, bearer authorization fields, password fields, and private-key headers. This is a bounded pattern scan, not proof that arbitrary future caller input is secret-free.
- Benchmark `system_info.txt` intentionally records machine/user/session details and process inventory for run validity. Treat those collection files as identifying operational metadata; do not copy them to public reports without reviewing the intended audience. The accompanying summary JSONs retain machine hardware data but omit the username/session fields (see D145).
- `Scripts/Tools/evidence_pack.py` copies raw logs and state files byte-for-byte and hashes them; it does not scrub their content. Its generated manifest records basenames, byte counts, and hashes, rather than source absolute paths.
- Report tools can expose user-specific paths or raw input: `proof_report.py` prints a resolved log path; `suite_log_report.py` includes the supplied path in JSON; `token_coverage.py` can print an absolute missing/sample path; and `asset_provenance.py` can echo absolute paths and matching log lines. These are the path/raw-line risks already mapped by S177; the absolute-path and input-echo limitation remains.
- No environment-variable value or credential lookup was found in non-test Python sources under `Scripts/Tools`; the benchmark summarizer reads `LOCALAPPDATA` only to locate an optional default Shipping output root. It does not print that variable's value directly, though error/output paths can reveal a user-specific directory.

## Disposition

No evidence indicates that these maintained tools intentionally emit credentials. Absolute paths and arbitrary input lines may still reveal personal or sensitive data if a caller supplies such input. Per C-764, `EVIDENCE_RETENTION_GUIDE_S155.md` now says raw logs and `system_info.txt` stay local-only, and host/user/session identifiers must be scrubbed from separately labeled copies before external sharing. Existing evidence was not changed. This audit does not establish privacy properties for every retained raw Unreal log.
