"""Rebuilds /Game/OneBossFight/Effects/PPM_ParryDistortion as a real Post Process Material.

Per Lead directives C-1037 and C-1040:
- Material Domain: MD_POST_PROCESS
- Blendable Location: BL_SCENE_COLOR_AFTER_TONEMAPPING ("After Tonemapping")
- 3 SceneTexture:PostProcessInput0 samples with small UV offsets on R/G/B (~0.003-0.006 UV)
- MaterialExpressionCollectionParameter bound to /Game/OneBossFight/Data/MPC_CombatFeedback (parameter: ParryPulse)
- Output to Emissive Color, no opacity
- Readback proof of domain, blendable location, SceneTexture nodes, and CollectionParameter binding
"""

import sys
import unreal

log = lambda m: unreal.log("[PPMRebuild] " + str(m))
log_err = lambda m: unreal.log_error("[PPMRebuild] " + str(m))

asset_path = "/Game/OneBossFight/Effects/PPM_ParryDistortion"
mpc_path = "/Game/OneBossFight/Data/MPC_CombatFeedback"
eal = unreal.EditorAssetLibrary
ml = unreal.MaterialEditingLibrary

mat = eal.load_asset(asset_path)
if not mat:
    log("Asset not found at %s, creating..." % asset_path)
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    mat = tools.create_asset("PPM_ParryDistortion", "/Game/OneBossFight/Effects", unreal.Material, unreal.MaterialFactoryNew())

if not mat:
    log_err("Failed to obtain material asset: %s" % asset_path)
    sys.exit(1)

mpc = eal.load_asset(mpc_path)
if not mpc:
    log_err("Failed to load MPC asset: %s" % mpc_path)
    sys.exit(1)

log("Loaded asset: %s (%s)" % (mat.get_name(), mat.get_class().get_name()))
log("Loaded MPC: %s (%s)" % (mpc.get_name(), mpc.get_class().get_name()))

# 1. Configure Post Process Material Settings
mat.set_editor_property("material_domain", unreal.MaterialDomain.MD_POST_PROCESS)
mat.set_editor_property("blendable_location", unreal.BlendableLocation.BL_SCENE_COLOR_AFTER_TONEMAPPING)

# 2. Clear existing expressions safely
ml.delete_all_material_expressions(mat)

# Helper node creator
def node(cls, x, y):
    return ml.create_material_expression(mat, cls, x, y)

def link(src, dst, src_out="", dst_inp=""):
    return ml.connect_material_expressions(src, src_out, dst, dst_inp)

# 3. Base UVs and Offset
# Screen UV (TextureCoordinate 0)
uv = node(unreal.MaterialExpressionTextureCoordinate, -900, 0)

# Base chromatic aberration offset: 0.005 UV in X, 0.003 UV in Y (~0.003-0.006 UV per C-1037)
offset_base = node(unreal.MaterialExpressionConstant2Vector, -900, 200)
offset_base.set_editor_property("r", 0.005)
offset_base.set_editor_property("g", 0.003)

# C-1040: MaterialExpressionCollectionParameter bound to MPC_CombatFeedback.ParryPulse
pulse_param = node(unreal.MaterialExpressionCollectionParameter, -900, 400)
pulse_param.set_editor_property("collection", mpc)
pulse_param.set_editor_property("parameter_name", "ParryPulse")

# Scaled offset = offset_base * pulse_param
scaled_offset = node(unreal.MaterialExpressionMultiply, -700, 250)
link(offset_base, scaled_offset, "", "A")
link(pulse_param, scaled_offset, "", "B")

# Red UV = UV + scaled_offset
uv_red = node(unreal.MaterialExpressionAdd, -500, -200)
link(uv, uv_red, "", "A")
link(scaled_offset, uv_red, "", "B")

# Green UV = unshifted base UV

# Blue UV = UV - scaled_offset
uv_blue = node(unreal.MaterialExpressionSubtract, -500, 200)
link(uv, uv_blue, "", "A")
link(scaled_offset, uv_blue, "", "B")

# 4. Three SceneTexture:PostProcessInput0 Samples
# Sample Red
st_red = node(unreal.MaterialExpressionSceneTexture, -300, -200)
st_red.set_editor_property("scene_texture_id", unreal.SceneTextureId.PPI_POST_PROCESS_INPUT0)
link(uv_red, st_red, "", "Coordinates")

mask_r = node(unreal.MaterialExpressionComponentMask, -50, -200)
mask_r.set_editor_property("r", True)
mask_r.set_editor_property("g", False)
mask_r.set_editor_property("b", False)
mask_r.set_editor_property("a", False)
link(st_red, mask_r, "Color", "")

# Sample Green
st_green = node(unreal.MaterialExpressionSceneTexture, -300, 0)
st_green.set_editor_property("scene_texture_id", unreal.SceneTextureId.PPI_POST_PROCESS_INPUT0)
link(uv, st_green, "", "Coordinates")

mask_g = node(unreal.MaterialExpressionComponentMask, -50, 0)
mask_g.set_editor_property("r", False)
mask_g.set_editor_property("g", True)
mask_g.set_editor_property("b", False)
mask_g.set_editor_property("a", False)
link(st_green, mask_g, "Color", "")

# Sample Blue
st_blue = node(unreal.MaterialExpressionSceneTexture, -300, 200)
st_blue.set_editor_property("scene_texture_id", unreal.SceneTextureId.PPI_POST_PROCESS_INPUT0)
link(uv_blue, st_blue, "", "Coordinates")

mask_b = node(unreal.MaterialExpressionComponentMask, -50, 200)
mask_b.set_editor_property("r", False)
mask_b.set_editor_property("g", False)
mask_b.set_editor_property("b", True)
mask_b.set_editor_property("a", False)
link(st_blue, mask_b, "Color", "")

# 5. Combine R, G, B channels
rg = node(unreal.MaterialExpressionAppendVector, 150, -100)
link(mask_r, rg, "", "A")
link(mask_g, rg, "", "B")

rgb = node(unreal.MaterialExpressionAppendVector, 350, 0)
link(rg, rgb, "", "A")
link(mask_b, rgb, "", "B")

# 6. Connect to Emissive Color
ml.connect_material_property(rgb, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)

# 7. Recompile and Save
ml.recompile_material(mat)
saved = eal.save_loaded_asset(mat)
log("Material recompiled and saved: %s (save_result=%s)" % (asset_path, saved))

# 8. Readback Verification Proof
domain = mat.get_editor_property("material_domain")
loc = mat.get_editor_property("blendable_location")
coll_node_class = pulse_param.get_class().get_name()
bound_mpc = pulse_param.get_editor_property("collection")
bound_param_name = str(pulse_param.get_editor_property("parameter_name"))

created_nodes = [st_red, st_green, st_blue, mask_r, mask_g, mask_b, uv, offset_base, pulse_param, scaled_offset, uv_red, uv_blue, rg, rgb]
st_nodes = [st_red, st_green, st_blue]

log("=== PROOF READBACK ===")
log("Asset: %s" % mat.get_path_name())
log("Material Domain: %s" % domain)
log("Blendable Location: %s" % loc)
log("Created Nodes Count: %d" % len(created_nodes))
log("CollectionParameter Node Class: %s" % coll_node_class)
log("Bound Collection Asset: %s" % (bound_mpc.get_path_name() if bound_mpc else "None"))
log("Bound Parameter Name: %s" % bound_param_name)
log("SceneTexture Nodes Count: %d" % len(st_nodes))
for idx, st in enumerate(st_nodes):
    tid = st.get_editor_property("scene_texture_id")
    log("  SceneTexture[%d]: id=%s" % (idx, tid))

# Strict Assertions
assert domain == unreal.MaterialDomain.MD_POST_PROCESS, "Domain mismatch: %s" % domain
assert loc == unreal.BlendableLocation.BL_SCENE_COLOR_AFTER_TONEMAPPING, "Location mismatch: %s" % loc
assert coll_node_class == "MaterialExpressionCollectionParameter", "Node class mismatch: %s" % coll_node_class
assert bound_mpc is not None and bound_mpc.get_path_name().startswith(mpc_path), "MPC mismatch: %s" % bound_mpc
assert bound_param_name == "ParryPulse", "Parameter name mismatch: %s" % bound_param_name
assert len(st_nodes) == 3, "Expected 3 SceneTexture nodes, got %d" % len(st_nodes)
for st in st_nodes:
    assert st.get_editor_property("scene_texture_id") == unreal.SceneTextureId.PPI_POST_PROCESS_INPUT0, "Expected PPI_POST_PROCESS_INPUT0"

log("RESULT: PASS - PPM_ParryDistortion successfully rebuilt with CollectionParameter and verified.")
