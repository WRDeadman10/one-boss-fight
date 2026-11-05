# Round 4 evidence import guide

Use this guide when the owner returns the benchmark results zip. Keep the source zip and extracted files as received; do not overwrite or normalize the raw files.

1. Record who supplied the package, when it arrived, the original zip path, byte size, and SHA-256.
2. Extract a copy into a new, uniquely named evidence directory. Do not extract over an existing directory.
3. Run `python -I Scripts/Tools/round4_benchmark_report.py inventory <evidence-root>` to list the eight expected run labels, the presence of `summary.json` and `frames.csv`, their sizes, and hashes. Save that stdout as the receipt inventory. When rechecking after transfer, pass the saved inventory with `--expected <inventory.json>`; missing or changed listed files are reported. A missing artifact or malformed summary is an issue; inventory does not repair files.
4. Build a receipt using `Scripts/Tools/round4_benchmark.schema.json`. Include all six measured runs (legacy and selected a/b/c), the build/package SHA-256, hardware/session identity, and the summary/frame paths and hashes. Keep warmups and any `_retry` folders in the raw package and inventory output; do not substitute a retry for its original row.
5. Run the receipt through `compare` and `report`. Identity differences make relative comparison unknown; missing metrics remain `UNKNOWN`. Review the exact source summaries and the owner's verbatim report alongside the generated output.
6. Link the immutable raw package, inventory JSON, receipt, and rendered report in the owner handoff. Never claim the tool ran the package, verified a GPU physically, or saw a play-test event; those facts come from the owner's evidence.

Example commands:

```powershell
python -I Scripts/Tools/round4_benchmark_report.py inventory Saved/OwnerEvidence/Round4
python -I Scripts/Tools/round4_benchmark_report.py compare Saved/OwnerEvidence/Round4/round4_receipt.json
python -I Scripts/Tools/round4_benchmark_report.py report Saved/OwnerEvidence/Round4/round4_receipt.json
```
