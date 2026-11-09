# AY-C14 — owner Video 3 full-fight capture prep

The normal `Scripts/Editor/pie_full_fight.py` flow cycles all authored player actions and keeps opportunistic parry watching enabled. It already uses the C-1132 montage-position targets: A1b 0.12 s, A3b 0.10 s, A1 0.27 s, A3a 0.42 s, A2 1.92 s, and Mid01 0.62 s; SprintFollowUp remains log-only because C-1132 observed two distinct contact points. `ER_FIGHT_TIER2=1` enables the Development visual path. No source target retiming is proposed.

Recommended Lead launch (one DATA route; use fresh, unique frame and receipt folders):

```powershell
New-Item -ItemType Directory -Force 'D:\FightVideo\owner_video3\frames' | Out-Null
& .\Scripts\RunLeadPie.ps1 `
  -Script Scripts/Editor/pie_full_fight.py `
  -Routes data `
  -Env @('ER_FIGHT_TIER2=1','FIGHT_MAX=150','FIGHT_RUN=owner_video3',
         'FIGHT_FRAMES=D:/FightVideo/owner_video3/frames',
         'FIGHT_BUILD_ID=BUILD-276','FIGHT_MAP_NAME=L_SevarovArena') `
  -OutputDir Docs/BossCombatReview/Execution/Claude/P_FIGHTVIDEO/OWNER_VIDEO3 `
  -TimeoutSeconds 900 `
  -StopMarker '[FullFight] finished:'
```

Before launch, Lead should verify both target directories are fresh/empty, the expected editor is stopped, and C-1155 permits the run. Retain the raw `.log`, `*_lines.txt`, `status.txt`, and all `f_*.png` frames together. Review receipts for all action categories, `PARRY_CONTACT` and `PARRY_RECOIL` (real success requires the parried counter increase and recoil marker), Tier 2 enabled, 150 s completion, and matching frame/run IDs. No Codex PIE, frame capture, render, or owner-facing visual claim is made here.
