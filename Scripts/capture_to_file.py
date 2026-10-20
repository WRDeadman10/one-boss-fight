import base64
import json
import os
import urllib.request

def capture():
    req = urllib.request.Request(
        "http://localhost:3000/mcp/tool/capture_viewport",
        data=b'{}',
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        resp = json.loads(r.read())
        b64 = resp.get("base64") or resp.get("data", {}).get("image_base64")
        if not b64:
            print("No base64 image data in response")
            return
        os.makedirs("Saved/Screenshots", exist_ok=True)
        out_path = os.path.abspath("Saved/Screenshots/current_viewport.png")
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(b64))
        print("Saved screenshot to:", out_path)

if __name__ == "__main__":
    capture()
