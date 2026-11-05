# Package evidence checklist

Complete a separate row set for Shipping and Development. Record the exact build ID and hashes; do not carry a result between configurations.

| Evidence item | Shipping | Development |
|---|---|---|
| `Scripts/Package.ps1` command, UAT log path, exit code | | |
| Build ID / executable SHA-256 / configuration | | |
| Staging root and `Manifest_UFSFiles_Win64.txt` SHA-256 | | |
| `DevelopmentAssetRegistry.bin` path and SHA-256 | | |
| `packagestore.manifest` path and SHA-256 | | |
| Authoritative UAT cook log or normalized cook export path / SHA-256 | | |
| `g044_cook_manifest.schema.json` validation and comparator output | | |
| H2 required closure count / present / missing / editor-only excluded | | |
| Each editor-only allowlist root and its review reference | | |
| Shipping smoke tokens / Development selected-route smoke evidence | | |
| Known gaps and evidence owner | | |

## Interpretation

- Package staging, cooked package inventory, startup smoke, selected-route activation, and target-hardware performance are separate claims.
- A missing manifest, UAT error, invalid normalized JSON, unresolved required path, or unexplained missing package leaves the cook gate OPEN.
- Shipping and Development are not interchangeable. Development-only selector results do not establish Shipping selector behavior.
- This sheet records package inputs and results; it does not make or imply an A7 release decision.
