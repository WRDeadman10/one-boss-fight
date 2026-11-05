# Queue D140 — content package path normalization audit

Date: 2026-11-03  
Method: static spot-check of maintained Editor path representations/conversions; no script run.

## Distinct path forms observed

- **Long package name:** `/Game/.../Package.Asset` is not used as a filesystem path. `AssetData.package_name` is logged and passed to editor asset APIs such as `rename_asset` (`setup_m7_roll.py:68,74`; `retarget_pack_to_greystone.py:82,90`). `get_assets_by_path` receives `/Game/...` roots.
- **Object path:** code that needs a generated Blueprint class explicitly combines `package_name + "." + asset_name + "_C"` (`g0_pack_boss.py:52,77`). This adds the object name and generated-class suffix; it is not a disk filename.
- **Filesystem path:** import tasks populate `filename` from a project/import directory using `os.path.join` and normalize separators to the host OS (`import_boss01.py:19`; `import_audio.py:17`). These use `.fbx`/audio source filenames and are not package or object paths.
- **Imported object paths:** import task results are consumed as Unreal-returned asset/object references (e.g. `import_boss01.py:14`, `import_audio.py:25`), not joined to a local `Content` directory.

## Result

The sampled scripts keep these representations separate. Search found no explicit `long_package_name_to_filename`/`filename_to_long_package_name` conversion, nor a package-name-to-disk `os.path` conversion. No conversion defect found in the checked examples. `rename_asset` relies on Unreal's asset-path API semantics; this audit does not validate those calls against a live Editor registry.

## Limits

This is not a full scan of all hard-coded paths in the Editor scripts and does not resolve mounts, plugin roots, redirectors, or actual disk package filenames. Paths for this project should be confirmed through Unreal APIs before any content operation.
