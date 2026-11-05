# Shipping binary check plan (D80)

Date: 2026-11-03. Plan only; no Shipping binary was inspected and no package/build was run.

## Check scope

1. Select the exact staged game binary, not the top-level launcher: `Saved/StagedBuilds/Windows/OneBossFight/Binaries/Win64/OneBossFight-Win64-Shipping.exe` (or the corresponding Lead-specified staged root).
2. Record its absolute path, byte size, UTC modification time, SHA-256, packaging configuration, and the package/build log identity. Do not infer binary identity from the launcher path alone.
3. Run `python -I Scripts/CheckShippingBinary.py <exact-binary>` and retain stdout/exit status with the package evidence. The checker searches ASCII and UTF-16LE for only `rpg.Debug` and `LogRPGDebug`; these two names are the entire scope of its PASS result.
4. Preserve `SHIPPING_SYMBOL_RISK_AUDIT_S182.md` as a source-only inventory. Its unguarded `ForTest`/BlueprintCallable declarations are not proven present or absent in the staged binary by `CheckShippingBinary.py`.

## API-surface follow-up boundary

If the Lead requires proof about a specific reflected hook (for example `HoldForTest` or `ResolveForTest`), name that function and use a Shipping-target method capable of observing the reflected function registry or cooked Blueprint callable surface, tied to the exact binary hash above. A plain ASCII/UTF-16 string scan or Shipping-disabled source branch is only a heuristic. Do not make broad “all test hooks stripped” claims from the two-name checker.

## Evidence and disposition

The checker already runs as the Shipping fallback in `PackagedSmoke.ps1`; the bounded run should use the same staged binary and retain the checker result alongside package identity. A PASS supports only “the two configured debug names were not found by this byte scan.” A hit supports “name present at reported encoding/offset”; it does not by itself prove the CVar or log category is registered at runtime. No source-level suspected test hook is classified as a confirmed Shipping leak without the separate binary/API evidence.
