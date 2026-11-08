import os
import sys
import json
import time
import subprocess

PROJECT_DIR = r"c:\UnrealProject\OneBossFight"
LOCK_PATH = os.path.join(PROJECT_DIR, r"Docs\BossCombatReview\Execution\ENGINE_LOCK.json")
UPROJECT_PATH = os.path.join(PROJECT_DIR, "OneBossFight.uproject")
EDITOR_EXE = r"C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
SCRIPT_PATH = os.path.join(PROJECT_DIR, r"Docs\BossCombatReview\Execution\Antigravity\GuardCounter\audit_guard_counter_polish.py")

if os.path.exists(LOCK_PATH):
    print("ERROR: Lock already exists at", LOCK_PATH)
    sys.exit(1)

print("[AG] Acquiring engine lock for Guard Counter Polish Audit...")
with open(LOCK_PATH, "w", encoding="utf-8") as f:
    json.dump({
        "owner": "AG",
        "task": "AC-A06..A10 Guard Counter Polish Audit",
        "acquired_at": time.strftime("%Y-%m-%dT%H:%M:%S")
    }, f, indent=2)

try:
    cmd = [
        EDITOR_EXE,
        UPROJECT_PATH,
        "-run=pythonscript",
        f"-script={SCRIPT_PATH}",
        "-unattended",
        "-nullrhi",
        "-nosound",
        "-nosplash"
    ]
    print("[AG] Running command:", " ".join(cmd))
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    print("Return code:", res.returncode)
    
    for line in res.stdout.splitlines():
        if "[GuardCounterAudit]" in line or "Error" in line:
            print(line)
    if res.stderr:
        print("STDERR:", res.stderr[:500])

finally:
    if os.path.exists(LOCK_PATH):
        print("[AG] Releasing engine lock...")
        os.remove(LOCK_PATH)
    print("[AG] Lock released.")
