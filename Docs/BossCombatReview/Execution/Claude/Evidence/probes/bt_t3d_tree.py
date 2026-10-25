"""P0 offline parser (no editor needed): turns the BehaviorTree text export written by p0_export_text.py into an indented tree.
Usage: python -I bt_t3d_tree.py <BT.t3d> <out.md>
Reads the runtime nodes (BTComposite_*, BTTask_*, decorators, services), not the editor graph. Prints node name, class, abort mode,
decorator/service/task properties that differ from noise, and the children in order. Changes nothing."""
import re
import sys

src = open(sys.argv[1], encoding="utf-8", errors="replace").read().splitlines()

# Pass 1: collect the property blocks ("Begin Object Name=X ExportPath=..." second occurrence) and classes (first occurrence).
classes = {}
props = {}
stack = []
for line in src:
    s = line.strip()
    m = re.match(r'Begin Object Class=(\S+) Name="([^"]+)"', s)
    if m:
        classes[m.group(2)] = m.group(1)
        stack.append(m.group(2))
        props.setdefault(m.group(2), [])
        continue
    m = re.match(r'Begin Object Name="([^"]+)"', s)
    if m:
        stack.append(m.group(1))
        props.setdefault(m.group(1), [])
        continue
    if s.startswith("End Object"):
        if stack:
            stack.pop()
        continue
    if stack and stack[-1] in props:
        props[stack[-1]].append(s)

NOISE = ("ExportPath", "TreeAsset", "ParentNode", "Children(", "Services(", "Decorators(", "NodeIndex", "ExecutionIndex", "TreeDepth",
         "ExecutionIndex", "MemoryOffset", "NextExecutionNode", "bShowPropertyDetails", "BlackboardKeyA_", "BlackboardKeyB_")


def short(name):
    return name.split("'")[-2].split(":")[-1] if "'" in name else name


def node_props(name):
    out = []
    for p in props.get(name, []):
        if any(p.startswith(n) for n in NOISE):
            continue
        out.append(p)
    return out


def describe(name, indent):
    cls = classes.get(name, "?").split(".")[-1]
    pad = "  " * indent
    lines = [f"{pad}- **{name}** `{cls}`"]
    for p in node_props(name):
        lines.append(f"{pad}    - {p[:220]}")
    return lines


def walk(name, indent, out):
    out.extend(describe(name, indent))
    pad = "  " * indent
    block = props.get(name, [])
    for p in block:
        if p.startswith("Services("):
            sv = short(re.search(r'="(.*)"', p).group(1))
            out.append(f"{pad}    - SERVICE:")
            out.extend(describe(sv, indent + 3))
    kids = []
    for p in block:
        m = re.match(r"Children\((\d+)\)=\((.*)\)$", p)
        if m:
            kids.append((int(m.group(1)), m.group(2)))
    for idx, body in sorted(kids):
        comp = re.search(r'ChildComposite="([^"]+)"', body)
        task = re.search(r'ChildTask="([^"]+)"', body)
        decs = re.search(r"Decorators=\((.*?)\)(?:,DecoratorOps|$)", body)
        out.append(f"{pad}  - child {idx}:")
        if decs:
            for d in re.findall(r'"([^"]+)"', decs.group(1)):
                out.append(f"{pad}      - DECORATOR:")
                out.extend(describe(short(d), indent + 4))
        ops = re.search(r"DecoratorOps=\((.*)\)$", body)
        if ops:
            out.append(f"{pad}      - DecoratorOps: {ops.group(1)[:200]}")
        if comp:
            walk(short(comp.group(1)), indent + 2, out)
        elif task:
            out.extend(describe(short(task.group(1)), indent + 2))
            tname = short(task.group(1))
            for p in props.get(tname, []):
                if p.startswith("Services("):
                    out.append(f"{pad}      - TASK SERVICE: {short(re.search(chr(61) + chr(34) + '(.*)' + chr(34), p).group(1))}")


root = None
for name, ps in props.items():
    for p in ps:
        if p.startswith("RootNode="):
            root = short(re.search(r'RootNode="([^"]+)"', p).group(1))
bt_name = [n for n in props if n.startswith("BT_")][0] if any(n.startswith("BT_") for n in props) else None
out = [f"# Behavior tree runtime tree from {sys.argv[1].split('/')[-1]}", "", f"RootNode: {root}", f"BT asset block: {bt_name}", ""]
if bt_name:
    out.append("## Asset-level properties")
    for p in props[bt_name]:
        if not p.startswith(("Nodes(", "SubGraphs(", "Schema", "GraphGuid", "ExportPath")):
            out.append(f"- {p[:200]}")
    out.append("")
out.append("## Tree")
if root:
    walk(root, 0, out)
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(out) + "\n")
print("nodes with props:", len(props), "root:", root, "lines:", len(out))
