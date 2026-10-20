#!/bin/sh
# Usage: Scripts/shot.sh x y z pitch yaw [name]  -> moves the editor viewport and saves Saved/Screenshots/<name>.png (default current_viewport).
# Needs the editor open with the UnrealClaude plugin (port 3000). Waits a few seconds for streaming and Lumen to settle.
cd "$(dirname "$0")/.."
echo "$1 $2 $3 $4 $5" > Saved/view.txt
MSYS_NO_PATHCONV=1 python -I Scripts/run_in_editor.py Scripts/Editor/set_view.py > /dev/null 2>&1
sleep "${SHOT_WAIT:-6}"
python -I Scripts/capture_to_file.py > /dev/null 2>&1
if [ -n "$6" ]; then cp Saved/Screenshots/current_viewport.png "Saved/Screenshots/$6.png"; fi
