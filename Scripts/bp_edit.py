"""Small helper around blueprint_modify for scripted graph edits (editor open)."""
import json, sys, urllib.request, urllib.error
def call(tool, params):
    req = urllib.request.Request("http://localhost:3000/mcp/tool/" + tool, data=json.dumps(params).encode(), headers={"Content-Type": "application/json"})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=600).read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        # Edits made while the graph is half wired compile with errors; the edit itself is applied, so carry on.
        if "succeeded but compilation failed" in body or "compilation failed" in body and "Pins connected" in body:
            return {"success": True, "compile_error": True}
        raise SystemExit("HTTP %d %s" % (e.code, body[:700]))
class Graph:
    def __init__(self, bp, graph, function=True):
        self.bp, self.graph, self.function = bp, graph, function
    def add(self, node_type, x, y, **params):
        r = call("blueprint_modify", {"operation": "add_node", "blueprint_path": self.bp, "graph_name": self.graph, "is_function_graph": self.function,
                                      "node_type": node_type, "node_params": params, "pos_x": x, "pos_y": y})
        d = r["data"]
        print("added %-45s pins: %s" % (d["node_id"], ", ".join("%s%s:%s" % ("<" if p["direction"] == "Input" else ">", p["name"], p["type"]) for p in d["pins"])))
        return d["node_id"]
    def connect(self, a, apin, b, bpin):
        call("blueprint_modify", {"operation": "connect_pins", "blueprint_path": self.bp, "graph_name": self.graph, "is_function_graph": self.function,
                                  "source_node_id": a, "source_pin": apin, "target_node_id": b, "target_pin": bpin})
        print("  %s.%s -> %s.%s" % (a[-12:], apin, b[-12:], bpin))
    def disconnect(self, a, apin, b, bpin):
        call("blueprint_modify", {"operation": "disconnect_pins", "blueprint_path": self.bp, "graph_name": self.graph, "is_function_graph": self.function,
                                  "source_node_id": a, "source_pin": apin, "target_node_id": b, "target_pin": bpin})
        print("  x %s.%s -/-> %s.%s" % (a[-12:], apin, b[-12:], bpin))
    def pin(self, node, pin, value):
        call("blueprint_modify", {"operation": "set_pin_value", "blueprint_path": self.bp, "graph_name": self.graph, "is_function_graph": self.function,
                                  "node_id": node, "pin_name": pin, "pin_value": value})
        print("  %s.%s = %s" % (node[-12:], pin, value))
