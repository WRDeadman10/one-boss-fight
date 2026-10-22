import os
from PIL import Image, ImageDraw, ImageFont

anim_dir = os.path.abspath("Import/Boss01/Animations")

def stitch_contact_sheet_2row(prefix, frames, times, out_name, title):
    panel_w = 320
    panel_h = 480
    header_h = 50
    row_header_h = 28
    
    total_w = panel_w * len(frames)
    total_h = header_h + (row_header_h + panel_h) * 2
    
    sheet = Image.new("RGB", (total_w, total_h), (18, 19, 22))
    draw = ImageDraw.Draw(sheet)
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 22)
        font_sub = ImageFont.truetype("arial.ttf", 15)
        font_label = ImageFont.truetype("arial.ttf", 14)
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_label = ImageFont.load_default()
        
    # Main header
    draw.rectangle([(0, 0), (total_w, header_h)], fill=(28, 30, 36))
    draw.text((20, 14), title, fill=(240, 240, 245), font=font_title)
    draw.text((total_w - 480, 16), "Yellow Post: 50cm, 100cm, 150cm, 200cm | Red Line: Z=0", fill=(210, 180, 70), font=font_sub)
    
    # Rows config: (row_index, view_name, row_title)
    rows = [
        (0, "side", "ROW 1: SIDE PROFILE VIEW (LOOKING +X TO -X)"),
        (1, "front", "ROW 2: DIRECT FRONT VIEW (LOOKING -Y TO +Y)")
    ]
    
    for row_idx, view_name, row_title in rows:
        y_row_header = header_h + row_idx * (row_header_h + panel_h)
        y_panels = y_row_header + row_header_h
        
        # Row sub-header bar
        draw.rectangle([(0, y_row_header), (total_w, y_row_header + row_header_h)], fill=(36, 39, 48))
        draw.text((20, y_row_header + 6), row_title, fill=(180, 205, 230), font=font_sub)
        
        for col_idx, (f, t) in enumerate(zip(frames, times)):
            f_path = os.path.join(anim_dir, f"{prefix}_{view_name}_{f:02d}.png")
            x_pos = col_idx * panel_w
            
            if os.path.exists(f_path):
                img = Image.open(f_path)
                sheet.paste(img, (x_pos, y_panels))
                
                # Panel divider
                if col_idx > 0:
                    draw.line([(x_pos, y_panels), (x_pos, y_panels + panel_h)], fill=(50, 54, 64), width=2)
                    
                # Badge overlay
                badge_text = f"F{f:02d} ({t:.2f}s)"
                draw.rectangle([(x_pos + 8, y_panels + 8), (x_pos + 115, y_panels + 32)], fill=(12, 14, 18))
                draw.text((x_pos + 14, y_panels + 12), badge_text, fill=(255, 255, 255), font=font_label)
                
                # Clean up individual frame
                try:
                    os.remove(f_path)
                except:
                    pass
            else:
                print(f"Warning: frame file missing: {f_path}")
                
    out_path = os.path.join(anim_dir, out_name)
    sheet.save(out_path, "PNG")
    print(f"Saved 2-row contact sheet: {out_name} ({sheet.size})")

# 1. PhaseRoar
stitch_contact_sheet_2row(
    "temp_cs_roar",
    [0, 6, 15, 21, 39, 54],
    [0.00, 0.20, 0.50, 0.70, 1.30, 1.80],
    "contact_sheet_PhaseRoar.png",
    "AN_Boss01_PhaseRoar (1.800 s, 30 fps) - Phase 2 Transition (Peak Roar Notify at 0.70 s)"
)

# 2. StaggerFall
stitch_contact_sheet_2row(
    "temp_cs_fall",
    [0, 4, 9, 15, 18, 21],
    [0.00, 0.13, 0.30, 0.50, 0.60, 0.70],
    "contact_sheet_StaggerFall.png",
    "AN_Boss01_StaggerFall (0.700 s, 30 fps) - Posture Break Impact & Kneeling Collapse"
)
