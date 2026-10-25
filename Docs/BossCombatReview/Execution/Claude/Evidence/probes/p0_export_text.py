"""P0 read-only probe: exports assets (and class default objects) as text into Evidence/exports. Log prefix [P0Export].
Never saves, compiles or modifies an asset: AssetExportTask only writes a text file. Edit the JOBS list or pass a job file in Saved/p0_jobs.txt (one '<name>|<path>|<asset|cdo>' per line)."""
import os
import unreal

OUT = "C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/Evidence/exports"
JOBS_FILE = "C:/UnrealProject/OneBossFight/Saved/p0_jobs.txt"
os.makedirs(OUT, exist_ok=True)
for line in open(JOBS_FILE).read().splitlines():
    if not line.strip() or line.startswith("#"):
        continue
    name, path, kind = line.split("|")
    try:
        if kind == "cdo":
            cls = unreal.load_class(None, path)
            obj = unreal.get_default_object(cls) if cls else None
        else:
            obj = unreal.load_asset(path)
        if obj is None:
            unreal.log("[P0Export] %s: NOT FOUND (%s)" % (name, path))
            continue
        task = unreal.AssetExportTask()
        task.object = obj
        task.filename = "%s/%s.t3d" % (OUT, name)
        task.automated = True
        task.prompt = False
        task.replace_identical = True
        ok = unreal.Exporter.run_asset_export_task(task)
        unreal.log("[P0Export] %s (%s) -> %s, %s bytes" % (name, kind, ok, os.path.getsize(task.filename) if os.path.exists(task.filename) else "no file"))
    except Exception as e:
        unreal.log("[P0Export] %s: ERR %s" % (name, e))
