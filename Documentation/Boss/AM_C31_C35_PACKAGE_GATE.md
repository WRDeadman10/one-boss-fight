# Queue AM C31–C35: package stage and content gate

Status: five offline tasks complete. Existing stage identity preflight passed; no new package or packaged runtime run was performed.

- C31: `Scripts/Package.ps1:30,41,49,57` sends both Shipping and Development BuildCookRun output and build stamps to `Saved/StagedBuilds/Windows`. It does not allocate a configuration-specific root or remove a prior stage. `Scripts/MakeBenchKit.ps1:16-20` prefers `Saved/StagedBuilds_Shipping/Windows` for Shipping but falls back to the shared `Saved/StagedBuilds/Windows`; Development defaults to the shared root. The bench-kit checker accepts any OBF-prefixed build ID in BUILD_INFO (`check_bench_kit.py:52-55`) without comparing both source stages. This is the KI-197 stage-selection risk, not evidence of an actual contaminated package.
- C32: new read-only `Scripts/Tools/check_stage_identity.py` requires distinct resolved roots, nonempty stage entry files/manifests, correctly formatted configuration-specific `BuildStamp.txt` IDs and different IDs. It refuses a shared root, mismatched stamp, or missing manifest in focused fixture tests (1/1). Run against the present stage roots: `Saved/StagedBuilds_Shipping/Windows` has `OBF-SHIPPING-20261106T071240Z-ac05f0da`; `Saved/StagedBuilds/Windows` has `OBF-DEVELOPMENT-20261106T071240Z-ed06b4d6`; result PASS. This is identity preflight on existing files only and does not date or validate their cooked contents.
- C33: Source soft paths for four ER montages are at `RPGDodgeTiming.cpp:41-44`; Tier 2 aura at `RPGTier2BossPresentation.cpp:19`, PPM and MPC at `RPGLegend.cpp:379-380`. The containing roots appear in `Config/DefaultGame.ini:27-31,38`: Boss01, Data, Effects, VFX and Player/Animations. This establishes source reference plus cook-root configuration, not that the seven packages appeared in a specific cook or launched in a package.
- C34: KI-193 has C-1042 default-wired PIE proof (4/4 both routes), yet packaged runtime remains open. KI-197 stays open because Package.ps1 can target the same root for consecutive configurations; the current separate stamped stages passing this checker do not change the script contract. No stage cleanup or package path was changed here.
- C35: before a future Shipping/Development kit, Lead should assign and preserve distinct stage roots, run package/cook and exact-stage manifest checks, then run this identity checker and packaged smoke against the same stamped roots. Record build IDs and manifest hashes before any kit copy. The source path alignment decision and any cleanup policy remain Lead-owned.

```powershell
python Scripts/Tools/check_stage_identity.py --shipping-stage Saved/StagedBuilds_Shipping/Windows --development-stage Saved/StagedBuilds/Windows
```

Validation: focused identity fixture 1/1, current-stage read-only preflight PASS, Python compile, doc links and diff check pass. Codex did not run BuildCookRun, Editor, PIE or packaged gameplay.
