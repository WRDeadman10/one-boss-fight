# Queue AM C16–C20: Tier 2 aura lifecycle gate

Status: five offline tasks complete; C-1042 Lead two-route lifecycle PIE passed 6/6 per route.

C-1042 Lead follow-up: both route logs in `Docs/BossCombatReview/Execution/Claude/P_C1042_AURA/` pass all six checks (`probe_legacy_lines.txt:2-10`, `probe_data_lines.txt:2-10`). Aura lifecycle is now proven for these PIE cases; first-use timing and packaged behavior remain KI-191 gates.

## Evidence and Source boundary

- C16: `Docs/BossCombatReview/Execution/Claude/P_C1033_TIER2/tier2.log:1593-1615` shows the data-route boss at 1000/2000 HP and one active `NS_Boss_PhaseTwoAura` Niagara component. It does not show the legacy route, off toggle or reset. `RPGTier2BossPresentation.cpp:23-57` ticks every 0.1 s, requires Development Tier 2, alive/non-dormant health <=60%, and latches one spawn. Lines 71-83 destroy and clear on off/invalid health/teardown. `RPGTier2BossRules.h:7-18` supplies the pure thresholds. Runtime cleanup beyond the observed data-route spawn remains unproven.
- C17: `Scripts/Editor/pie_tier2_aura.py` is a Lead-only two-route probe. It records full-health absence, 50% health presence, off removal, on respawn, reset removal and post-reset reappearance. It filters Niagara components by exact asset name, flags inactive and duplicate matches, reports actual health and route, restores the Tier 2 cvar, and emits `[Tier2Aura] SUMMARY` for RunLeadPie.
- C18: focused fake-Unreal test checks that unrelated Niagara components do not count and that inactive/duplicate aura components fail. It passed 1/1. Python syntax and the two-route `RunLeadPie.ps1 -DryRun` passed; dry run uses `-nosound` and does not acquire the engine lock.
- C19: KI-191 remains PARTIAL. Only the data-route 1000/2000 spawn and both-route parry/recoil have live proof. Legacy aura and aura lifetime remain pending; no Source-only closure is claimed.
- C20: Lead run command below. Visual quality remains a separate owner/Lead inspection gate.

```powershell
& ./Scripts/RunLeadPie.ps1 -Script Scripts/Editor/pie_tier2_aura.py -Routes @('legacy','data') -OutputDir Docs/BossCombatReview/Execution/Claude/P_AM_C16_C20_AURA
```

Acceptance: both route logs contain six passing checks, one `[Tier2Aura] SUMMARY pass=True`, actual health at the threshold, and no exception. Lead should inspect the raw component names/active values. Codex did not run PIE, Editor, build or package.
