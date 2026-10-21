import sys
import json
import socket

def execute_blender(code: str) -> dict:
    host = "127.0.0.1"
    port = 9876
    req = json.dumps({"type": "execute", "code": code, "strict_json": False}) + "\0"
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(120.0)
        sock.connect((host, port))
        sock.sendall(req.encode("utf-8"))
        buf = bytearray()
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                break
            buf.extend(chunk)
            if b"\0" in buf:
                break
    line, _, _ = buf.partition(b"\0")
    return json.loads(line.decode("utf-8"))

if __name__ == "__main__":
    test_code = "import bpy\nresult = {'scene': bpy.context.scene.name, 'version': bpy.app.version_string, 'objects': len(bpy.data.objects)}"
    res = execute_blender(test_code)
    print("Response from Blender:")
    print(json.dumps(res, indent=2))
