import os
from PIL import Image, ImageDraw, ImageFont

anim_dir = os.path.abspath("Import/Boss01/Animations")

def stitch_contact_sheet(prefix, frames, times, out_name, title, note="Yellow Post: 50cm, 100cm, 150cm, 200cm Marks | Red Floor: Z=0"):
    panel_w = 320
    panel_h = 480
    header_h = 50
    total_w = panel_w * len(frames)
    total_h = panel_h + header_h
    
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
    draw.text((total_w - 480, 16), note, fill=(210, 180, 70), font=font_sub)
    
    for idx, (f, t) in enumerate(zip(frames, times)):
        frame_path = os.path.join(anim_dir, f"{prefix}_{f:02d}.png")
        x_pos = idx * panel_w
        y_pos = header_h
        
        if os.path.exists(frame_path):
            img = Image.open(frame_path)
            sheet.paste(img, (x_pos, y_pos))
            
            if idx > 0:
                draw.line([(x_pos, header_h), (x_pos, total_h)], fill=(45, 48, 55), width=2)
                
            badge_text = f"F{f:02d} ({t:.2f}s)"
            draw.rectangle([(x_pos + 10, y_pos + 10), (x_pos + 120, y_pos + 36)], fill=(15, 16, 20))
            draw.text((x_pos + 18, y_pos + 14), badge_text, fill=(255, 255, 255), font=font_label)
            
            try:
                os.remove(frame_path)
            except:
                pass
        else:
            print(f"Warning: missing frame {frame_path}")
            
    out_path = os.path.join(anim_dir, out_name)
    sheet.save(out_path, "PNG")
    print(f"Saved {out_name}: {sheet.size}")

def main():
    # 1. Player Riposte
    stitch_contact_sheet(
        "temp_cs_riposte_player",
        [0, 6, 14, 20, 24, 48],
        [0.00, 0.20, 0.47, 0.67, 0.80, 1.60],
        "contact_sheet_Riposte_Player_Front.png",
        "AN_Riposte_Player_Front (1.600 s, 30 fps) - Paired Execution Lunge (Impact at 0.80 s)",
        note="Root Motion: 90 cm forward (X=150 to X=60) | Impact at F24"
    )
    
    # 2. Boss Riposte Reaction
    stitch_contact_sheet(
        "temp_cs_riposte_boss",
        [0, 12, 20, 24, 34, 60],
        [0.00, 0.40, 0.67, 0.80, 1.13, 2.00],
        "contact_sheet_Riposte_Boss_Reaction.png",
        "AN_Riposte_Boss_Reaction (2.000 s, 30 fps) - Kneeling Riposte Recoil (Impact at 0.80 s)",
        note="In-Place | F0 == StaggerDown F30 | F60 == StaggerDown F0"
    )
    
    # 3. Boss Death Legend
    stitch_contact_sheet(
        "temp_cs_death",
        [0, 12, 24, 40, 60, 105],
        [0.00, 0.40, 0.80, 1.33, 2.00, 3.50],
        "contact_sheet_DeathLegend.png",
        "AN_Boss01_DeathLegend (3.500 s, 30 fps) - Fatal Collapse & Held Rest Pose (Frozen 2.50s - 3.50s)",
        note="In-Place | Held Rest: F75 to F105 (no motion)"
    )

if __name__ == "__main__":
    main()
