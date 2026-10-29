"""IEEE-float32 arithmetic illustration, NOT an Unreal runtime test."""
from pathlib import Path
import struct,math,json,hashlib
here=Path(__file__).resolve().parent
root=here.parents[4]
def f32(v):
    try:return struct.unpack("<f",struct.pack("<f",v))[0]
    except OverflowError:return math.copysign(math.inf,v)
limit=struct.unpack("<f",bytes.fromhex("ffff7f7f"))[0]
dt=f32(1.0/60.0)
start=f32(limit*0.99)
speed=f32(limit*0.99)
step=f32(speed*dt)
radius=f32(start+step)
band_radius=f32(limit*0.75)
half=f32(limit*0.5)
outer=f32(band_radius+half)
p=root/"Source/OneBossFight/Player/RPGBossShockwave.cpp"
r={"scope":"IEEE-float32 source arithmetic illustration only; no Unreal execution",
   "source_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
   "float_max":limit,
   "radius_case":{"Damage":0,"StartRadius":start,"MaxRadius":limit,"Speed":speed,"Thickness":1,"JumpClearance":0.5,
                  "bEnabled":True,"MoveId":"A6","DeltaTime":dt,"step":step,"sum_overflows_float32":not math.isfinite(radius)},
   "band_case":{"Damage":0,"StartRadius":band_radius,"MaxRadius":limit,"Speed":1,"Thickness":limit,"JumpClearance":0.5,
                "bEnabled":True,"MoveId":"A6","Radius":band_radius,"half_thickness":half,"outer_overflows_float32":not math.isfinite(outer)}}
for c in [r["radius_case"],r["band_case"]]:
    assert c["Damage"]>=0 and 0<=c["StartRadius"]<c["MaxRadius"]
    assert c["Speed"]>0 and c["Thickness"]>0 and c["JumpClearance"]>0
    assert all(math.isfinite(c[k]) for k in ["Damage","StartRadius","MaxRadius","Speed","Thickness","JumpClearance"])
assert r["radius_case"]["sum_overflows_float32"] and r["band_case"]["outer_overflows_float32"]
text=json.dumps(r,indent=2)
(here/"float_boundary_results.json").write_text(text,encoding="utf-8")
print(text)
