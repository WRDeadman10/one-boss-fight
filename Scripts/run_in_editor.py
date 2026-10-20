"""Runs a Python file inside the open editor through the plugin server and prints its output.
Usage: python -I Scripts/run_in_editor.py Scripts/Editor/<script>.py [max_chars]   (Git Bash: MSYS_NO_PATHCONV=1)"""
import json
import os
import sys
import time
import urllib.error
import urllib.request


def call(tool, params):
    req = urllib.request.Request("http://localhost:3000/mcp/tool/" + tool, data=json.dumps(params).encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


path = os.path.abspath(sys.argv[1]).replace("\\", "/")
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 12000
head = "# /** @UnrealClaude Script\n#  * @Description: run file */\n"
r = call("execute_script", {"script_type": "python", "script_content": head + 'exec(open(r"%s", encoding="utf-8").read())' % path})
tid = r["data"]["task_id"]
st = None
for _ in range(1200):
    r = call("task_result", {"task_id": tid})
    st = r.get("data", {}).get("status")
    if st in ("completed", "failed"):
        break
    time.sleep(1)
inner = r.get("data", {}).get("data", {})
out = inner.get("output") or inner.get("error") or json.dumps(r)[:2000]
print(st)
print(out[:limit])
