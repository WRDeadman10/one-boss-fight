# BOSS-QA-001: one real game-view screenshot (needs a CONNECTED desktop session)

Why it cannot be done unattended on this machine: the session that runs the agent is DISCONNECTED (`query session` shows `Rushit Vaghela 16 Disc`), so the GPU has no live display to read back and every capture is exactly black (three methods tried, see `NOTES` in the mailbox post C-656 and the `*_FAIL_*` / `attempt*` folders here). A real screenshot needs YOUR connected console session (not RDP, not a disconnected session).

Do this once, with no Unreal process running, from a PowerShell window in your logged-in desktop session:

    cd C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude
    .\B_QA001\run_game_shot.ps1 -Map /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofQA001 -OutDir "$PWD\B_QA001\game_run_owner" -Task qa001_owner -ShotPath "$PWD\B_QA001\game_view_overlay_owner.png" -At 6 -ShowUI 0
    python -I .\B_QA001\png_stats.py .\B_QA001\game_view_overlay_owner.png

It opens a 1280 x 720 game window, runs the framework boss with the overlay switched on (`rpg.BossOverlay 1`), takes the engine's own screenshot of the GAME viewport at 6 s, and closes itself (about 30 s). A good result: `nonblack_fraction` clearly above 0 and `yellow_overlay_pixels` above 0 (the overlay is drawn in yellow). Open the PNG and look at it.
