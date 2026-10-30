#!/usr/bin/env python3
"""
verify_a256_pipeline.py
=======================
Offline verification of Sevarog Animation Pipeline & Blender Feasibility Study (A-256).
"""

import sys
import subprocess
from pathlib import Path

BLENDER_EXE = Path("C:/Program Files/Blender Foundation/Blender 5.1/blender.exe")
DOC_PATH = Path("Docs/BossCombatReview/Execution/Antigravity/Animation/SEVAROG_ANIM_PIPELINE.md")
REF_FBX = Path("Import/ThirdParty/Reference/REF_Sevarog_Sevarog.fbx")

def main():
    print("================================================================================")
    print(" VERIFYING A-256 SEVAROG ANIMATION PIPELINE & BLENDER FEASIBILITY")
    print("================================================================================")

    # 1. Verify SEVAROG_ANIM_PIPELINE.md
    assert DOC_PATH.is_file(), f"Missing doc file: {DOC_PATH}"
    raw_doc = DOC_PATH.read_bytes()
    assert b"\r\r\n" not in raw_doc, "No double CRLF"
    assert raw_doc.endswith(b"\r\n"), "Must end in CRLF"
    assert b"Blender 5.1" in raw_doc
    assert b"AN_Sevarog_RearSweep" in raw_doc
    assert b"AN_Sevarog_Grab_Attacker" in raw_doc
    assert b"bUsesRootMotion = false" in raw_doc
    print(f"[OK] SEVAROG_ANIM_PIPELINE.md verified: {len(raw_doc):,} bytes, clean CRLF.")

    # 2. Verify Blender Executable
    assert BLENDER_EXE.is_file(), f"Blender executable not found at: {BLENDER_EXE}"
    ver_res = subprocess.run([str(BLENDER_EXE), "--version"], capture_output=True, text=True)
    assert ver_res.returncode == 0
    assert "Blender 5.1" in ver_res.stdout
    print(f"[OK] Blender 5.1 installation confirmed: {ver_res.stdout.splitlines()[0]}")

    # 3. Verify Reference FBX Exists
    assert REF_FBX.is_file(), f"Missing reference FBX: {REF_FBX}"
    print(f"[OK] Reference FBX confirmed: {REF_FBX.name} ({REF_FBX.stat().st_size:,} bytes)")

    # 4. Execute Headless Blender Import Probe
    probe_script = Path("Docs/BossCombatReview/Execution/Antigravity/Animation/probe_blender_sevarog.py")
    assert probe_script.is_file(), f"Missing probe script: {probe_script}"
    cmd = [
        str(BLENDER_EXE), "-b",
        "--python", str(probe_script)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"Blender probe failed: {res.stderr}\n{res.stdout}"
    assert "Bones count: 154" in res.stdout, "Must confirm 154 bones in armature"
    assert "weapon_r=True" in res.stdout, "Must confirm weapon_r bone"
    assert "root_weapon_end_r=True" in res.stdout, "Must confirm root_weapon_end_r bone"
    assert "BLENDER FBX IMPORT SUCCESSFUL" in res.stdout
    print("[OK] Headless Blender 5.1 import verified: 154 bones, weapon sockets verified.")

    print("\n================================================================================")
    print(" ALL A-256 PIPELINE AND FEASIBILITY CHECKS 100% VERIFIED OFFLINE")
    print("================================================================================")

if __name__ == "__main__":
    main()
