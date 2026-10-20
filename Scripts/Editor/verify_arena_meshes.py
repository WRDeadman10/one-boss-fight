# -*- coding: utf-8 -*-
import unreal

MESH_DIR = "/Game/OneBossFight/Environment/Meshes"

def main():
    names = [
        "SM_Pillar_Intact",
        "SM_Pillar_Cracked",
        "SM_Pillar_Broken",
        "SM_Wall_Curved_Intact",
        "SM_Wall_Curved_Damaged",
        "SM_Entrance_Arch",
        "SM_Arena_Brazier",
        "SM_Arena_Rubble_Cluster"
    ]
    out_lines = []
    for n in names:
        path = MESH_DIR + "/" + n
        mesh = unreal.load_asset(path)
        if mesh is None:
            out_lines.append("MISSING: " + path)
            continue
        bounds = mesh.get_bounds()
        box_ext = bounds.box_extent
        origin = bounds.origin
        radius = bounds.sphere_radius
        out_lines.append("%s -> Extent: (X=%.1f, Y=%.1f, Z=%.1f), Origin: (X=%.1f, Y=%.1f, Z=%.1f), Radius: %.1f" % 
            (n, box_ext.x, box_ext.y, box_ext.z, origin.x, origin.y, origin.z, radius))
            
    with open("c:/Users/winss/Documents/Unreal Projects/OneBossFight/Import/verify_output.txt", "w") as f:
        f.write("\n".join(out_lines))

if __name__ == "__main__":
    main()
