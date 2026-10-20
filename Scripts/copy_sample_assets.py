"""
Copies the packages listed in the closure file (from Scripts/Editor/sample_deps.py) from the DarkRuinsMegascansSample project into this project's Content,
keeping the same relative paths so every reference stays valid. Existing files are never overwritten (two StarterContent textures clash). Close the editor first.
Usage: python -I Scripts/copy_sample_assets.py <closure.json>
Prints the top level Content folders that were touched (add them to .gitignore: they are third party and git-ignored).
"""
import json, os, shutil, sys

SAMPLE = r"C:\Users\winss\Documents\Unreal Projects\DarkRuinsMegascansSample\Content"
TARGET = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Content"
EXTS = (".uasset", ".uexp", ".ubulk", ".uptnl", ".umap")

closure = json.load(open(sys.argv[1]))
copied = skipped = 0
tops = set()
for r in closure["packages"]:
    rel = r["pkg"][len("/Game/"):].replace("/", os.sep)
    for e in EXTS:
        src = os.path.join(SAMPLE, rel + e)
        if not os.path.exists(src):
            continue
        dst = os.path.join(TARGET, rel + e)
        if os.path.exists(dst):
            skipped += 1
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        copied += 1
        tops.add(rel.split(os.sep)[0])
print("copied", copied, "files, skipped existing", skipped)
print("top level folders:", sorted(tops))
