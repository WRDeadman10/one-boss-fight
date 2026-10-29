# Copyright One Boss Fight. All Rights Reserved.
"""Verification script for Order A-232 staged files."""

import hashlib
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PREIMAGE_DIR = os.path.join(BASE_DIR, "preimages")
STAGED_DIR = os.path.join(BASE_DIR, "staged")

TARGETS = [
    ("RPGBossEncounter.cpp", "Player/RPGBossEncounter.h"),
    ("RPGDodgeTiming.cpp", "Player/RPGDodgeTiming.h"),
    ("RPGPlayerMovesSubsystem.cpp", "Player/RPGPlayerMovesSubsystem.h"),
]

EXPECTED_PREIMAGES = {
    "RPGBossEncounter.cpp": "3f3b62d834486c375ec9c2de1ef3423ad719fa81a81477149450d3ae542ee3be",
    "RPGDodgeTiming.cpp": "367bb788df0ab17eefd194aef0d1296cf62ad33f8befe91d60b9dcb50c634f36",
    "RPGPlayerMovesSubsystem.cpp": "5d0f0be233e6bb6f054c47c96d07244758227b46c9739a04bf1d6236d3a0c703",
}

EXPECTED_STAGED = {
    "RPGBossEncounter.cpp": "bce27a9dd7c280423301eca600edb29263250c807b3d9bc3f4be962b7bede080",
    "RPGDodgeTiming.cpp": "acafc4a8ceb4f7dbe297e3688fe88722186311c863c29073c2dcac1ec9aedbee",
    "RPGPlayerMovesSubsystem.cpp": "dd279aa717633b3f5f523df62de72ca5d8af0e0ad18c57fe3f646fe855bd6f67",
}

def verify():
    for fname, own_hdr in TARGETS:
        # Preimage check
        pre_path = os.path.join(PREIMAGE_DIR, fname)
        assert os.path.isfile(pre_path), f"Missing preimage: {pre_path}"
        with open(pre_path, "rb") as f:
            pre_bytes = f.read()
        pre_sha = hashlib.sha256(pre_bytes).hexdigest()
        assert pre_sha == EXPECTED_PREIMAGES[fname], f"Preimage hash mismatch for {fname}"
        assert pre_bytes.count(b"\r\n") == pre_bytes.count(b"\n"), f"Preimage not pure CRLF: {fname}"

        # Staged check
        stg_path = os.path.join(STAGED_DIR, fname)
        assert os.path.isfile(stg_path), f"Missing staged: {stg_path}"
        with open(stg_path, "rb") as f:
            stg_bytes = f.read()
        stg_sha = hashlib.sha256(stg_bytes).hexdigest()
        assert stg_sha == EXPECTED_STAGED[fname], f"Staged hash mismatch for {fname}"
        assert stg_bytes.count(b"\r\n") == stg_bytes.count(b"\n"), f"Staged not pure CRLF: {fname}"

        lines = stg_bytes.decode("utf-8").split("\r\n")
        assert lines[0] == "// Copyright One Boss Fight. All Rights Reserved."
        assert lines[1] == ""
        assert lines[2] == f'#include "{own_hdr}"', f"First include must be own header, got: {lines[2]}"
        assert lines[3] == '#include "Player/RPGStartupChronology.h"', f"Second include must be chronology, got: {lines[3]}"
        print(f"PASS: {fname} first include is {own_hdr}, second is RPGStartupChronology.h, pure CRLF, SHA verified.")

    print("\nALL 3 STAGED REVISIONS FULLY VERIFIED.")

if __name__ == "__main__":
    verify()
