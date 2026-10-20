"""Nodes of one Blueprint graph with full pin lists and link counts. Usage: python Scripts/bp_pins.py <bp> <graph>"""
import json, sys, urllib.request, urllib.error
def call(tool, params):
    req = urllib.request.Request("http://localhost:3000/mcp/tool/" + tool, data=json.dumps(params).encode(), headers={"Content-Type": "application/json"})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=600).read())
    except urllib.error.HTTPError as e:
        sys.exit("HTTP %d %s" % (e.code, e.read().decode()[:500]))
nodes = call("blueprint_query", {"operation": "get_nodes", "blueprint_path": sys.argv[1], "graph_name": sys.argv[2]})["data"]["nodes"]
for n in sorted(nodes, key=lambda n: (n["pos_x"], n["pos_y"])):
    print("%s | %s | %s | (%d,%d)" % (n["node_guid"], n["class"].replace("K2Node_", ""), n.get("title", "").replace("\n", " / "), n["pos_x"], n["pos_y"]))
    for p in n["pins"]:
        print("      %-3s %-22s %-28s %s%s" % (p["direction"][0], p["name"][:22], p["type"][:28], ("=" + p["default_value"]) if p.get("default_value") not in (None, "") else "", "  #%d" % p["connections"] if p["connections"] else ""))
