"""DD-1 step 0 baseline manifest (read-only): pins what the behaviour-identical foundation must not change.
Writes Docs/BossCombatReview/Execution/Claude/DD1/STEP0_MANIFEST.json (full file lists with sha256) and prints a summary.
Covers: git HEAD and the dirty list (git status --short, no git command that changes anything), Source/ and Config/ per file hashes, project content assets (Content/OneBossFight, .uasset/.umap, sha256),
the editor module DLL, the RunDrivers.ps1 regression table (name, minimum checks, script), the automation test registrations (macro, name) and the PIE driver scripts present in Scripts/Editor.
Run: python -I dd1_step0_manifest.py   (from any directory)"""
import hashlib
import json
import os
import re
import subprocess
import time

ROOT = r"C:\UnrealProject\OneBossFight"
OUT = os.path.join(ROOT, "Docs", "BossCombatReview", "Execution", "Claude", "DD1", "STEP0_MANIFEST.json")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def walk(base, exts=None):
    rows = []
    for d, _dirs, files in os.walk(os.path.join(ROOT, base)):
        for name in sorted(files):
            if exts and not name.lower().endswith(exts):
                continue
            p = os.path.join(d, name)
            rows.append({"path": os.path.relpath(p, ROOT).replace("\\", "/"), "bytes": os.path.getsize(p), "sha256": sha(p)})
    rows.sort(key=lambda r: r["path"])
    return rows


def git(*args):
    return subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True, text=True).stdout.strip()


manifest = {"created": time.strftime("%Y-%m-%d %H:%M:%S %z"), "git_head": git("rev-parse", "HEAD"), "git_branch": git("rev-parse", "--abbrev-ref", "HEAD"), "dirty": git("status", "--short").split("\n")}
manifest["source"] = walk("Source", (".cpp", ".h", ".cs"))
manifest["config"] = walk("Config", (".ini",))
manifest["content_project_assets"] = walk(os.path.join("Content", "OneBossFight"), (".uasset", ".umap"))
manifest["editor_dll"] = walk(os.path.join("Binaries", "Win64"), ("unrealeditor-onebossfight.dll",))
manifest["pie_driver_scripts"] = walk(os.path.join("Scripts", "Editor"), (".py",))
rd = open(os.path.join(ROOT, "Scripts", "RunDrivers.ps1"), encoding="utf-8", errors="replace").read()
rows = []
for line in rd.splitlines():
    if "@{" in line and "N = '" in line and "Min = " in line:
        n = re.search(r"N = '([^']+)'", line).group(1)
        sc = re.search(r"S = '([^']+)'", line)
        mn = int(re.search(r"Min = (\d+)", line).group(1))
        rows.append({"name": n, "script": sc.group(1) if sc else n, "min": mn, "balance_row": n.startswith("pie_build_fight")})
manifest["rundrivers_rows"] = rows
tests = []
for f in sorted(os.listdir(os.path.join(ROOT, "Source", "OneBossFight", "Tests"))):
    if f.endswith(".cpp"):
        t = open(os.path.join(ROOT, "Source", "OneBossFight", "Tests", f), encoding="utf-8", errors="replace").read()
        for m in re.finditer(r'IMPLEMENT_(?:SIMPLE|COMPLEX)_AUTOMATION_TEST\(\s*\w+,\s*"([^"]+)"', t):
            tests.append({"file": f, "name": m.group(1)})
manifest["automation_tests"] = tests
json.dump(manifest, open(OUT, "w", encoding="utf-8"), indent=1)
print("written", OUT, os.path.getsize(OUT), "bytes")
for k in ("source", "config", "content_project_assets", "editor_dll", "pie_driver_scripts", "rundrivers_rows", "automation_tests", "dirty"):
    print(k, len(manifest[k]))
digest = hashlib.sha256(json.dumps([manifest["source"], manifest["config"], manifest["content_project_assets"]], sort_keys=True).encode()).hexdigest()
print("combined digest (source+config+content assets):", digest)
