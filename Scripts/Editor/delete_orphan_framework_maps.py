"""Delete four batches of five FrameworkProof maps with zero references.

Run only from the task-specific C-1155 runner. Every source map has a verified
rollback copy in Saved/MapCleanupBackup_20261113 before AssetTools deletion.
"""
import hashlib
import json
import os
from pathlib import Path

import unreal

ROOT = Path(__file__).resolve().parents[2]
RUN_DIR = Path(os.environ["MAP_CLEANUP_RUN_DIR"]).resolve()
MANIFEST = ROOT / "Saved" / "map_cleanup_manifest.json"
BACKUP = ROOT / "Saved" / "MapCleanupBackup_20261113"
NAMES = [
    "L_SevarogFrameworkProofAggroSwitchR13",
    "L_SevarogFrameworkProofAWR007B",
    "L_SevarogFrameworkProofFatigueR15A6",
    "L_SevarogFrameworkProofGuardChipR7",
    "L_SevarogFrameworkProofFAG5_Close250",
    "L_SevarogFrameworkProofFAG5_Gap700",
    "L_SevarogFrameworkProofFAG5_Medium375",
    "L_SevarogFrameworkProofFAG5_Melee100",
    "L_SevarogFrameworkProofMOV001_R150",
    "L_SevarogFrameworkProofMOV001_R300",
    "L_SevarogFrameworkProofMOV001_R700",
    "L_SevarogFrameworkProofParryRecoveryA4",
    "L_SevarogFrameworkProofParryRecoveryR9",
    "L_SevarogFrameworkProofParryRecoveryR9P",
    "L_SevarogFrameworkProofParryRecoveryR9Q",
    "L_SevarogFrameworkProofStrafeEdgeR3c",
    "L_SevarogFrameworkProofTelegraphScaleR11",
    "L_SevarogFrameworkProofWarpEaseR1",
    "L_SevarogFrameworkProofYawConeR5",
    "L_SevarogFrameworkProofYawConeR6A8",
]


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path, value):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def require(condition, message):
    if not condition:
        raise RuntimeError("[MAP_CLEANUP_DELETE] REFUSED: " + message)


require(RUN_DIR.is_relative_to(ROOT / "Saved" / "MapCleanup"), "run receipt path escaped Saved/MapCleanup")
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
entries = {item["path"].replace("\\", "/"): item for item in manifest["candidate_delete"]}
eal = unreal.EditorAssetLibrary
items = []

# Preflight the entire set before deleting any map.
for name in NAMES:
    rel = "Content/OneBossFight/FrameworkProof/{}.umap".format(name)
    source = ROOT / rel
    backup = BACKUP / rel
    package = "/Game/OneBossFight/FrameworkProof/" + name
    entry = entries.get(rel)
    require(entry is not None and entry.get("git_tracked") is True, "missing tracked-manifest row: " + rel)
    expected = entry.get("sha256")
    require(source.is_file() and sha256(source) == expected, "source hash differs from manifest: " + rel)
    require(backup.is_file() and sha256(backup) == expected, "rollback copy missing or hash mismatch: " + rel)
    require(entry.get("asset_registry_referencers") == [], "manifest lists asset referencers: " + rel)
    require(eal.does_asset_exist(package), "asset registry cannot find candidate: " + package)
    referencers = list(eal.find_package_referencers_for_asset(package, False))
    require(not referencers, "new package referencers appeared for {}: {}".format(package, referencers))
    items.append({"name": name, "relative_path": rel, "package": package, "sha256": expected, "backup": str(backup)})

RUN_DIR.mkdir(parents=True, exist_ok=True)
for batch_index in range(4):
    batch = items[batch_index * 5:(batch_index + 1) * 5]
    receipt = {"batch": batch_index + 1, "requested": len(batch), "deleted": [], "status": "RUNNING"}
    receipt_path = RUN_DIR / "batch_{:02d}.json".format(batch_index + 1)
    write_json(receipt_path, receipt)
    for item in batch:
        require(eal.delete_asset(item["package"]), "AssetTools delete failed: " + item["package"])
        require(not eal.does_asset_exist(item["package"]), "asset still resolves after delete: " + item["package"])
        item_path = ROOT / item["relative_path"]
        require(not item_path.exists(), "package file remains after delete: " + item["relative_path"])
        require(sha256(Path(item["backup"])) == item["sha256"], "rollback copy changed during delete: " + item["relative_path"])
        receipt["deleted"].append(item)
        write_json(receipt_path, receipt)
    receipt["status"] = "COMPLETE"
    write_json(receipt_path, receipt)
    unreal.log("[MAP_CLEANUP_DELETE] BATCH {} COMPLETE (5/5)".format(batch_index + 1))

write_json(RUN_DIR / "summary.json", {"status": "COMPLETE", "deleted_count": len(items), "preserved_play_map": "/Game/OneBossFight/Maps/L_SevarogArena", "batches": 4})
unreal.log("[MAP_CLEANUP_DELETE] COMPLETE deleted=20 batches=4")
