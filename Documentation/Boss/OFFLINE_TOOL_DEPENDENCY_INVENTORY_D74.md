# Offline tool dependency inventory (D74)

Date: 2026-11-03. Parsed imports across the 43 maintained CLI entries in the S154 index and checked the repository for Python dependency manifests.

- All 43 maintained tools use Python standard-library modules plus in-repository support modules (`atomic_io.py`, `verify_evidence_manifest.py`, and the FrameworkProof validator under `Docs/BossCombatReview/Execution/Antigravity/Reviews`). No third-party runtime package import was found.
- The CLI set has no `requirements*.txt`, `pyproject.toml`, `Pipfile`, or Python environment manifest in the repository. No dependency installation is required for these tools beyond Python itself.
- The compatibility floor is Python 3.10: the tools use PEP 604 union annotations (`X | None`) and built-in generic annotations. The current Windows runtime reports Python 3.10.0; D66/D73 help/import checks used it.
- `Path.is_relative_to` is also used and requires Python 3.9+, so the 3.10 union syntax is the stricter minimum.

No tools were run for D74 beyond import-source classification and version inspection. The inventory excludes tests, whose test runner is standard-library `unittest`.
