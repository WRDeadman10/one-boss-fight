import os
from PIL import Image, ImageDraw, ImageFont

anim_dir = r"c:\Users\winss\Documents\Unreal Projects\OneBossFight\Import\Boss01\Animations"

def stitch_contact_sheet(prefix, frames, times, out_name, title):
    panel_w = 320
    panel_h = 480
    header_h = 50
    total_w = panel_w * len(frames)
    total_h = panel_h + header_h
    
    sheet = Image.new("RGB", (total_w, total_h), (18, 19, 22))
    draw = ImageDraw.Draw(sheet)
    
    # Try default or simple font
    try:
        font_title = ImageFont.truetype("arial.ttf", 22)
        font_label = ImageFont.truetype("arial.ttf", 16)
    except:
        font_title = ImageFont.load_default()
        font_label = ImageFont.load_default()
        
    # Draw header bar
    draw.rectangle([(0, 0), (total_w, header_h)], fill=(28, 30, 36))
    draw.text((20, 14), title, fill=(240, 240, 245), font=font_title)
    
    # Draw ruler guide note
    draw.text((total_w - 420, 16), "Yellow Post: 50cm, 100cm, 150cm, 200cm Marks | Red Floor: Z=0", fill=(210, 180, 70), font=font_label)
    
    for idx, (f, t) in enumerate(zip(frames, times)):
        frame_path = os.path.join(anim_dir, f"{prefix}_{f:02d}.png")
        if os.path.exists(frame_path):
            img = Image.open(frame_path)
            x_pos = idx * panel_w
            y_pos = header_h
            sheet.paste(img, (x_pos, y_pos))
            
            # Panel divider line
            if idx > 0:
                draw.line([(x_pos, header_h), (x_pos, total_h)], fill=(45, 48, 55), width=2)
                
            # Frame info overlay badge
            badge_text = f"F{f:02d} ({t:.2f}s)"
            draw.rectangle([(x_pos + 10, y_pos + 10), (x_pos + 120, y_pos + 36)], fill=(15, 16, 20, 200))
            draw.text((x_pos + 18, y_pos + 14), badge_text, fill=(255, 255, 255), font=font_label)
            
            # Remove temp frame file
            try:
                os.remove(frame_path)
            except:
                pass
                
    out_path = os.path.join(anim_dir, out_name)
    sheet.save(out_path, "PNG")
    print(f"Saved {out_name}: {sheet.size}")

# 1. Phase Roar
stitch_contact_sheet(
    "temp_cs_roar",
    [0, 6, 15, 21, 39, 54],
    [0.00, 0.20, 0.50, 0.70, 1.30, 1.80],
    "contact_sheet_PhaseRoar.png",
    "AN_Boss01_PhaseRoar (1.800 s, 30 fps) - Phase 2 Transition (Roar Peak Notify at 0.70 s)"
)

# 2. Stagger Fall
stitch_contact_sheet(
    "temp_cs_fall",
    [0, 4, 9, 15, 18, 21],
    [0.00, 0.13, 0.30, 0.50, 0.60, 0.70],
    "contact_sheet_StaggerFall.png",
    "AN_Boss01_StaggerFall (0.700 s, 30 fps) - Posture Break Impact & Kneeling Collapse"
)

# 3. Stagger Down
stitch_contact_sheet(
    "temp_cs_down",
    [0, 8, 15, 22, 28, 30],
    [0.00, 0.27, 0.50, 0.73, 0.93, 1.00],
    "contact_sheet_StaggerDown.png",
    "AN_Boss01_StaggerDown (1.000 s Loop, 30 fps) - Kneeling Exhausted Breathing Loop (F0 == F30)"
)

# 4. Stagger Get Up
stitch_contact_sheet(
    "temp_cs_getup",
    [0, 6, 15, 27, 36, 42],
    [0.00, 0.20, 0.50, 0.90, 1.20, 1.40],
    "contact_sheet_StaggerGetUp.png",
    "AN_Boss01_StaggerGetUp (1.400 s, 30 fps) - Posture Recovery & Rise to Combat Ready Idle"
)

# 5. A3a Combo 1
stitch_contact_sheet(
    "temp_cs_a3a",
    [0, 6, 12, 15, 18, 24],
    [0.00, 0.20, 0.40, 0.50, 0.60, 0.80],
    "contact_sheet_A3a_Combo1.png",
    "AN_Boss01_A3a_Combo1 (0.800 s, 25 frames, 30 fps) - Combo Slash 1 Cleave"
)

# 6. A3b Combo 2
stitch_contact_sheet(
    "temp_cs_a3b",
    [0, 4, 8, 12, 24, 40],
    [0.00, 0.13, 0.27, 0.40, 0.80, 1.33],
    "contact_sheet_A3b_Combo2.png",
    "AN_Boss01_A3b_Combo2 (1.333 s, 41 frames, 30 fps) - Combo Slash 2 Reverse Cleave"
)
