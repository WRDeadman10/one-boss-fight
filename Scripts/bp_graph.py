"""Compact dump of Blueprint graph nodes through the UnrealClaude plugin server (editor open).
Usage: python Scripts/bp_graph.py <blueprint path> [graph name]   (no graph = list graphs)"""
import json, sys, urllib.error, urllib.request
def call(tool, params):
    req = urllib.request.Request("http://localhost:3000/mcp/tool/" + tool, data=json.dumps(params).encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit("HTTP %d %s" % (e.code, e.read().decode()[:600]))
bp = sys.argv[1]
if len(sys.argv) < 3:
    d = call("blueprint_query", {"operation": "inspect", "blueprint_path": bp, "include_graphs": True, "include_variables": True, "include_functions": True})["data"]
    print("parent:", d.get("parent_class_name"))
    print("vars:", ", ".join("%s:%s" % (v["name"], v.get("type", "?")) for v in d.get("variables", [])))
    print("graphs:", d["graph_info"]["graph_names"])
else:
    res = call("blueprint_query", {"operation": "get_nodes", "blueprint_path": bp, "graph_name": sys.argv[2]})
    nodes = res["data"]["nodes"]
    nodes.sort(key=lambda n: (n["pos_y"] // 200, n["pos_x"]))
    for n in nodes:
        title = n.get("title", "").replace("\n", " / ")
        pins = [p for p in n["pins"] if p.get("default_value") not in (None, "", "None", "0.0", "false") and p["direction"] == "Input" and p["type"] != "exec"]
        extra = ("  " + ", ".join("%s=%s" % (p["name"], p["default_value"]) for p in pins)) if pins else ""
        print("(%5d,%5d) %-22s %s%s" % (n["pos_x"], n["pos_y"], n["class"].replace("K2Node_", ""), title, extra[:120]))
