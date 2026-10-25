"""P0 offline parser (no editor): reads a Blueprint text export (AssetExportTask .t3d from p0_export_text.py) and prints, for one graph, every node with its function/event and the exec and data edges
(source node.pin -> target node.pin) taken from the `LinkedTo=` entries of the pins. Changes nothing.
Usage: python -I bp_t3d_edges.py <BP.t3d> "<graph name>" [out.txt]      (no graph name: list the graph names with their node counts)
A node is printed as `Name (Class) Title/Function`, an edge as `A.PinOut -> B.PinIn`. Only exec pins are marked `EXEC`."""
import re
import sys

text = open(sys.argv[1], encoding="utf-8", errors="replace").read().split("\n")
graph_name = sys.argv[2] if len(sys.argv) > 2 else None
out = open(sys.argv[3], "w", encoding="utf-8") if len(sys.argv) > 3 else sys.stdout


def emit(s=""):
    out.write(s + "\n")


# Pass 1: split the export into top-level graph objects and their node objects (by Begin/End Object nesting).
graphs = {}          # graph name -> list of node dicts
stack = []           # (kind, name)
cur_graph = None
node = None
for line in text:
    s = line.strip()
    m = re.match(r'Begin Object Class=(\S+) Name="([^"]+)"', s)
    if m:
        cls, name = m.groups()
        stack.append((cls, name))
        if cls.endswith("EdGraph") or "EdGraph" in cls.split("/")[-1] and "Node" not in cls.split(".")[-1]:
            cur_graph = name
            graphs.setdefault(cur_graph, [])
        elif "K2Node" in cls:
            node = {"name": name, "cls": cls.split(".")[-1], "pins": [], "info": []}
            graphs.setdefault(cur_graph or "?", []).append(node)
        continue
    if re.match(r'Begin Object Name="([^"]+)"', s):
        # the property block of a node already declared above: find it
        nm = re.match(r'Begin Object Name="([^"]+)"', s).group(1)
        stack.append(("prop", nm))
        node = next((n for g in graphs.values() for n in g if n["name"] == nm), None) if not nm.startswith("EventGraph") else None
        if nm in graphs:
            cur_graph = nm
        continue
    if s.startswith("End Object"):
        if stack:
            stack.pop()
        continue
    if node is not None and stack and stack[-1][1] == node["name"]:
        if s.startswith("CustomProperties Pin"):
            pid = re.search(r"PinId=([0-9A-Fa-f]+)", s)
            pname = re.search(r'PinName="([^"]*)"', s)
            direction = re.search(r'Direction="([^"]*)"', s)
            cat = re.search(r'PinType\.PinCategory="([^"]*)"', s)
            linked = re.search(r"LinkedTo=\(([^)]*)\)", s)
            links = re.findall(r"(\S+) ([0-9A-Fa-f]{32})", linked.group(1)) if linked else []
            node["pins"].append({"id": pid.group(1) if pid else "", "name": pname.group(1) if pname else "", "dir": direction.group(1) if direction else "in", "cat": cat.group(1) if cat else "", "links": links})
        elif any(s.startswith(k) for k in ("FunctionReference=", "EventReference=", "VariableReference=", "CustomFunctionName=", "NodeComment=", "TargetType=")):
            node["info"].append(s[:200])

if graph_name is None:
    for g, nodes in graphs.items():
        emit(f"{len(nodes):5d} nodes  {g}")
    sys.exit(0)

nodes = graphs.get(graph_name)
if nodes is None:
    emit("graph not found; available: " + ", ".join(graphs))
    sys.exit(1)
pin_owner = {}
for n in nodes:
    for p in n["pins"]:
        pin_owner[p["id"]] = (n, p)
emit(f"# graph '{graph_name}': {len(nodes)} nodes")
for n in nodes:
    members = " ".join(re.findall(r'MemberName="([^"]+)"', " ".join(n["info"])))
    emit(f"NODE {n['name']} ({n['cls']}) {members}")
emit("")
emit("# edges (EXEC = execution pin)")
count = 0
for n in nodes:
    for p in n["pins"]:
        if p["dir"] != "EGPD_Output":
            continue
        for _node_ref, pid in p["links"]:
            target = pin_owner.get(pid)
            tn = f"{target[0]['name']}.{target[1]['name']}" if target else f"?.{pid[:8]}"
            emit(f"{'EXEC ' if p['cat'] == 'exec' else '     '}{n['name']}.{p['name']} -> {tn}")
            count += 1
emit(f"# {count} edges")
