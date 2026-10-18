# Asset License Register

Record every third-party asset before it ships. Verify the current license on the listing at download time.
Third-party packs are **not committed to git** (`Content/Paragon*/` is ignored): re-download them from Fab.

## Candidates (M2, not yet downloaded)

All are free on Fab, creator Epic Games, **Standard License**, listing text checked 2026-10-18. Fab lists UE 5.0 – 5.8 for Steel; the others were not checked individually.

| Candidate | Role | Fab listing | Notes |
|---|---|---|---|
| Paragon: Greystone | Player | https://www.fab.com/listings/122fd7bf-6f12-4304-a930-cccbbacdaebc | Knight; includes AnimBPs |
| Paragon: Steel | Player (alt) | https://www.fab.com/listings/5c0e13c1-8d00-4213-8a05-5c501c01548d | Sword and shield cyborg; includes AnimBPs; UE 5.0 – 5.8 |
| Paragon: Grux | Boss | https://www.fab.com/listings/8c4bac2c-f7f7-4632-a644-47f4e104f5d8 | Brute; now includes AnimBPs |
| Paragon: Sevarog | Boss (alt) | https://www.fab.com/listings/a4882b5e-cfad-4830-a3dd-46a6c31a79b2 | Reaper; now includes AnimBPs |

Terms seen on every listing: may not use the PARAGON trademark to advertise or name the game; "Allows usage with AI: No" (do not use the content to train AI models). Greystone was created from face scans (OTOY).

## Register (fill when an asset is added to the project)

| Asset | Creator | Source URL | License terms | Date | Used for | Restrictions / dependencies |
|---|---|---|---|---|---|---|
| Paragon: Greystone | Epic Games | https://www.fab.com/listings/122fd7bf-6f12-4304-a930-cccbbacdaebc | Fab Standard License; no PARAGON trademark use | 2026-10-18 | Player (provisional) | `Content/ParagonGreystone`, 2.2 GB, git-ignored |
| Paragon: Steel | Epic Games | https://www.fab.com/listings/5c0e13c1-8d00-4213-8a05-5c501c01548d | same | 2026-10-18 | Player alternative / dash source | `Content/ParagonSteel`, 2.2 GB, git-ignored |
| Paragon: Grux | Epic Games | https://www.fab.com/listings/8c4bac2c-f7f7-4632-a644-47f4e104f5d8 | same | 2026-10-18 | Boss alternative | `Content/ParagonGrux`, 3.0 GB, git-ignored |
| Paragon: Sevarog | Epic Games | https://www.fab.com/listings/a4882b5e-cfad-4830-a3dd-46a6c31a79b2 | same | 2026-10-18 | Boss (provisional) | `Content/ParagonSevarog`, 1.4 GB, git-ignored |

Unused packs should be deleted from `Content/` once the pick is final, to keep cook size and load time down.

Other notes:
- Engine tutorial mannequin (`/Engine/Tutorial/.../TutorialTPP`) is used only as a temporary placeholder mesh.
