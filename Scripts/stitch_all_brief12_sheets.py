import os
import json
from PIL import Image, ImageDraw, ImageFont

anim_dir = os.path.abspath("Import/Boss01/Animations")

def stitch_1row(prefix, frames, times, out_name, title, view_name="side"):
    panel_w = 320
    panel_h = 480
    header_h = 50
    total_w = panel_w * len(frames)
    total_h = panel_h + header_h
    
    sheet = Image.new("RGB", (total_w, total_h), (18, 19, 22))
    draw = ImageDraw.Draw(sheet)
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 20)
        font_label = ImageFont.truetype("arial.ttf", 15)
        font_sub = ImageFont.truetype("arial.ttf", 13)
    except:
        font_title = ImageFont.load_default()
        font_label = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        
    draw.rectangle([(0, 0), (total_w, header_h)], fill=(28, 30, 36))
    draw.text((20, 14), title, fill=(240, 240, 245), font=font_title)
    draw.text((total_w - 450, 16), "Yellow Post: 50cm, 100cm, 150cm, 200cm | Floor: Z=0", fill=(210, 180, 70), font=font_sub)
    
    panels_img = []
    for idx, (f, t) in enumerate(zip(frames, times)):
        fname = f"{prefix}_{f:02d}.png"
        f_path = os.path.join(anim_dir, fname)
        if not os.path.exists(f_path):
            # check with view
            f_path = os.path.join(anim_dir, f"{prefix}_{view_name}_{f:02d}.png")
            
        if os.path.exists(f_path):
            img = Image.open(f_path).convert("RGB")
            panels_img.append(img)
            x_pos = idx * panel_w
            y_pos = header_h
            sheet.paste(img, (x_pos, y_pos))
            
            if idx > 0:
                draw.line([(x_pos, header_h), (x_pos, total_h)], fill=(50, 54, 64), width=2)
                
            badge_text = f"F{f:02d} ({t:.2f}s)"
            draw.rectangle([(x_pos + 10, y_pos + 10), (x_pos + 120, y_pos + 36)], fill=(12, 14, 18))
            draw.text((x_pos + 16, y_pos + 14), badge_text, fill=(255, 255, 255), font=font_label)
        else:
            print("Missing panel:", f_path)
            
    out_path = os.path.join(anim_dir, out_name)
    sheet.save(out_path, "PNG")
    print(f"Saved {out_name} ({sheet.size})")
    return panels_img

def stitch_2row(prefix, frames, times, out_name, title):
    panel_w = 320
    panel_h = 480
    header_h = 50
    row_header_h = 28
    
    total_w = panel_w * len(frames)
    total_h = header_h + (row_header_h + panel_h) * 2
    
    sheet = Image.new("RGB", (total_w, total_h), (18, 19, 22))
    draw = ImageDraw.Draw(sheet)
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 20)
        font_sub = ImageFont.truetype("arial.ttf", 14)
        font_label = ImageFont.truetype("arial.ttf", 14)
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_label = ImageFont.load_default()
        
    draw.rectangle([(0, 0), (total_w, header_h)], fill=(28, 30, 36))
    draw.text((20, 14), title, fill=(240, 240, 245), font=font_title)
    draw.text((total_w - 480, 16), "Yellow Post: 50cm, 100cm, 150cm, 200cm | Floor: Z=0", fill=(210, 180, 70), font=font_sub)
    
    rows = [
        (0, "side", "ROW 1: SIDE PROFILE VIEW (LOOKING +X TO -X)"),
        (1, "front", "ROW 2: DIRECT FRONT VIEW (LOOKING -Y TO +Y)")
    ]
    
    panels_img = []
    for row_idx, view_name, row_title in rows:
        y_row_header = header_h + row_idx * (row_header_h + panel_h)
        y_panels = y_row_header + row_header_h
        
        draw.rectangle([(0, y_row_header), (total_w, y_row_header + row_header_h)], fill=(36, 39, 48))
        draw.text((20, y_row_header + 6), row_title, fill=(180, 205, 230), font=font_sub)
        
        for col_idx, (f, t) in enumerate(zip(frames, times)):
            f_path = os.path.join(anim_dir, f"{prefix}_{view_name}_{f:02d}.png")
            x_pos = col_idx * panel_w
            
            if os.path.exists(f_path):
                img = Image.open(f_path).convert("RGB")
                if row_idx == 0:
                    panels_img.append(img)
                sheet.paste(img, (x_pos, y_panels))
                
                if col_idx > 0:
                    draw.line([(x_pos, y_panels), (x_pos, y_panels + panel_h)], fill=(50, 54, 64), width=2)
                    
                badge_text = f"F{f:02d} ({t:.2f}s)"
                draw.rectangle([(x_pos + 8, y_panels + 8), (x_pos + 115, y_panels + 32)], fill=(12, 14, 18))
                draw.text((x_pos + 14, y_panels + 12), badge_text, fill=(255, 255, 255), font=font_label)
            else:
                print("Missing 2row panel:", f_path)
                
    out_path = os.path.join(anim_dir, out_name)
    sheet.save(out_path, "PNG")
    print(f"Saved {out_name} ({sheet.size})")
    return panels_img

def stitch_topdown():
    panel_w = 480
    panel_h = 360
    header_h = 50
    total_w = panel_w * 3
    total_h = panel_h + header_h
    
    sheet = Image.new("RGB", (total_w, total_h), (18, 19, 22))
    draw = ImageDraw.Draw(sheet)
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 19)
        font_sub = ImageFont.truetype("arial.ttf", 13)
        font_label = ImageFont.truetype("arial.ttf", 13)
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_label = ImageFont.load_default()
        
    draw.rectangle([(0, 0), (total_w, header_h)], fill=(28, 30, 36))
    draw.text((20, 15), "AN_Riposte_Paired_TopDown (30 fps) - Overhead Arena Tracking (50 cm Floor Grid)", fill=(240, 240, 245), font=font_title)
    draw.text((total_w - 480, 16), "Boss: Grey at Origin (0,0) | Player: Blue (Facing Boss)", fill=(210, 180, 70), font=font_sub)
    
    panels_info = [
        ("temp_topdown_F00_Start.png", "F00 (0.00s) - Standoff Gap: 150 cm (Player at Y=150)"),
        ("temp_topdown_F24_Impact.png", "F24 (0.80s) - IMPACT: 60 cm Gap (Thrust into Chest)"),
        ("temp_topdown_F_End.png", "F48 (1.60s) - Recovery: Boss Kneeling, Player Idle")
    ]
    
    panels_img = []
    for idx, (filename, badge_text) in enumerate(panels_info):
        f_path = os.path.join(anim_dir, filename)
        x_pos = idx * panel_w
        y_pos = header_h
        
        if os.path.exists(f_path):
            img = Image.open(f_path).convert("RGB")
            panels_img.append(img)
            sheet.paste(img, (x_pos, y_pos))
            
            if idx > 0:
                draw.line([(x_pos, header_h), (x_pos, total_h)], fill=(50, 54, 64), width=2)
                
            draw.rectangle([(x_pos + 10, y_pos + 10), (x_pos + 380, y_pos + 34)], fill=(12, 14, 18))
            draw.text((x_pos + 16, y_pos + 13), badge_text, fill=(255, 255, 255), font=font_label)
            
    out_path = os.path.join(anim_dir, "contact_sheet_Riposte_Paired_TopDown.png")
    sheet.save(out_path, "PNG")
    print(f"Saved paired topdown: {out_path} ({sheet.size})")
    return panels_img

def compute_pixel_diffs(panels, name):
    if not panels or len(panels) < 2:
        return {}
    p1 = panels[0]
    p1_data = list(p1.getdata())
    total_px = len(p1_data)
    
    diff_report = {}
    for idx, p in enumerate(panels[1:], start=2):
        p_data = list(p.getdata())
        diff_count = 0
        for px1, px2 in zip(p1_data, p_data):
            # Difference threshold: level difference > 10 in any RGB channel
            if abs(px1[0] - px2[0]) > 10 or abs(px1[1] - px2[1]) > 10 or abs(px1[2] - px2[2]) > 10:
                diff_count += 1
        pct = (diff_count / float(total_px)) * 100.0
        diff_report[f"Panel_1_vs_Panel_{idx}"] = {
            "differing_pixels": diff_count,
            "total_pixels": total_px,
            "percent_difference": round(pct, 2)
        }
    return diff_report

print("--- Rendering frames and stitching ---")
# 1. PhaseRoar
p_roar = stitch_2row("temp_cs_roar", [0, 6, 15, 21, 39, 54], [0.00, 0.20, 0.50, 0.70, 1.30, 1.80], "contact_sheet_PhaseRoar.png", "AN_Boss01_PhaseRoar (1.800 s, 30 fps) - Phase 2 Transition (Roar Peak at 0.70 s)")
diff_roar = compute_pixel_diffs(p_roar, "PhaseRoar")

# 2. StaggerFall
p_fall = stitch_2row("temp_cs_fall", [0, 4, 9, 15, 18, 21], [0.00, 0.13, 0.30, 0.50, 0.60, 0.70], "contact_sheet_StaggerFall.png", "AN_Boss01_StaggerFall (0.700 s, 30 fps) - Posture Break Impact & Kneeling Collapse")
diff_fall = compute_pixel_diffs(p_fall, "StaggerFall")

# 3. Riposte Player Front
p_player = stitch_1row("temp_cs_riposte_player", [0, 6, 14, 21, 24, 48], [0.00, 0.20, 0.47, 0.70, 0.80, 1.60], "contact_sheet_Riposte_Player_Front.png", "AN_Riposte_Player_Front (1.600 s, 30 fps) - Execution Strike (90 cm Lunge, Impact at 0.80 s)", view_name="player")
diff_player = compute_pixel_diffs(p_player, "Riposte_Player")

# 4. Riposte Boss Reaction
p_react = stitch_1row("temp_cs_riposte_boss", [0, 12, 20, 24, 39, 60], [0.00, 0.40, 0.67, 0.80, 1.30, 2.00], "contact_sheet_Riposte_Boss_Reaction.png", "AN_Riposte_Boss_Reaction (2.000 s, 30 fps) - Kneeling Chest Impact Recoil (Impact at 0.80 s)", view_name="side")
diff_react = compute_pixel_diffs(p_react, "Riposte_Boss_Reaction")

# 5. DeathLegend
p_death = stitch_1row("temp_cs_death", [0, 15, 24, 40, 75, 105], [0.00, 0.50, 0.80, 1.33, 2.50, 3.50], "contact_sheet_DeathLegend.png", "AN_Boss01_DeathLegend (3.500 s, 30 fps) - Legendary Death Collapse & Slump (Slump at 2.50 s)", view_name="side")
diff_death = compute_pixel_diffs(p_death, "DeathLegend")

# 6. Paired TopDown
p_topdown = stitch_topdown()
diff_topdown = compute_pixel_diffs(p_topdown, "Paired_TopDown")

all_diffs = {
    "contact_sheet_PhaseRoar.png": diff_roar,
    "contact_sheet_StaggerFall.png": diff_fall,
    "contact_sheet_Riposte_Player_Front.png": diff_player,
    "contact_sheet_Riposte_Boss_Reaction.png": diff_react,
    "contact_sheet_DeathLegend.png": diff_death,
    "contact_sheet_Riposte_Paired_TopDown.png": diff_topdown
}

with open("contact_sheets_diff.json", "w") as f:
    json.dump(all_diffs, f, indent=2)

print("\n=== PIXEL DIFFERENCE AUDIT (PANEL 1 VS PANELS 2..6) ===")
for sheet, diffs in all_diffs.items():
    print(f"\n{sheet}:")
    for comp, data in diffs.items():
        print(f"  {comp}: {data['differing_pixels']} px ({data['percent_difference']}%)")
