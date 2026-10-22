import sys
import os
import json
import socket
import subprocess
import tempfile
import shutil

def find_blender():
    candidates = [
        r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
        shutil.which("blender")
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return "blender"

def execute_blender(code: str) -> dict:
    host = "127.0.0.1"
    port = 9876
    req = json.dumps({"type": "execute", "code": code, "strict_json": False}) + "\0"
    
    # Try socket first with a short timeout
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(2.0)
            sock.connect((host, port))
            sock.settimeout(180.0)
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
    except (ConnectionRefusedError, socket.timeout, OSError):
        # Fallback to headless Blender CLI execution
        blender_bin = find_blender()
        with tempfile.TemporaryDirectory() as tmpdir:
            script_path = os.path.join(tmpdir, "run_code.py")
            result_json_path = os.path.join(tmpdir, "result.json")
            
            runner_code = f"""
import sys
import json
import io
import contextlib

code_to_run = {json.dumps(code)}
context_dict = {{}}

stdout_capture = io.StringIO()
stderr_capture = io.StringIO()

try:
    with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
        exec(code_to_run, context_dict, context_dict)
    
    res_val = context_dict.get('result', stdout_capture.getvalue())
    out_payload = {{"executed": True, "result": res_val}}
except Exception as e:
    import traceback
    out_payload = {{"executed": False, "error": str(e), "traceback": traceback.format_exc()}}

with open({json.dumps(result_json_path)}, "w", encoding="utf-8") as f:
    json.dump(out_payload, f, default=str)
"""
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(runner_code)
                
            cmd = [blender_bin, "--background", "--python", script_path]
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=300)
            
            if os.path.exists(result_json_path):
                with open(result_json_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                return {
                    "executed": False,
                    "error": f"Blender CLI failed with returncode {proc.returncode}",
                    "stdout": proc.stdout,
                    "stderr": proc.stderr
                }

if __name__ == "__main__":
    test_code = "import bpy\nresult = {'scene': bpy.context.scene.name, 'version': bpy.app.version_string, 'objects': len(bpy.data.objects)}"
    res = execute_blender(test_code)
    print("Response from Blender:")
    print(json.dumps(res, indent=2))
