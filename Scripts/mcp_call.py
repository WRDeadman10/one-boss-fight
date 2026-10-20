"""Call a tool of the UnrealClaude plugin's local MCP server (http://localhost:3000) while the editor is open.
Usage: python Scripts/mcp_call.py <tool> '<json params>'   (prints the JSON result)"""
import json, sys, urllib.error, urllib.request
tool, params = sys.argv[1], json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
req = urllib.request.Request("http://localhost:3000/mcp/tool/" + tool, data=json.dumps(params).encode(), headers={"Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req, timeout=600) as r:
        print(json.dumps(json.loads(r.read()), indent=1)[:int(sys.argv[3]) if len(sys.argv) > 3 else 12000])
except urllib.error.HTTPError as e:
    print("HTTP", e.code, e.read().decode()[:1500])
