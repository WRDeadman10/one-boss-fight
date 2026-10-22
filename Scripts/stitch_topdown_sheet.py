import os
from PIL import Image, ImageDraw, ImageFont

anim_dir = os.path.abspath("Import/Boss01/Animations")

def stitch_topdown():
    panel_w = 480
    panel_h = 360
    header_h = 50
    total_w = panel_w * 3
    total_h = panel_h + header_h
    
    sheet = Image.new("RGB", (total_w, total_h), (18, 19, 22))
    draw = ImageDraw.Draw(sheet)
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 20)
        font_sub = ImageFont.truetype("arial.ttf", 14)
        font_badge = ImageFont.truetype("arial.ttf", 13)
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_badge = ImageFont.load_default()
        
    # Main header bar
    draw.rectangle([(0, 0), (total_w, header_h)], fill=(28, 30, 36))
    draw.text((20, 14), "Paired Riposte Top-Down Alignment (Asset A-11) - Boss at Origin (X=0) vs Player (X=150 to X=60)", fill=(240, 240, 245), font=font_title)
    draw.text((total_w - 460, 16), "Boss: Grey (X=0, +X fwd) | Player: Blue (Facing -X)", fill=(210, 180, 70), font=font_sub)
    
    panel_info = [
        ("temp_topdown_F00_Start.png", "F00 (0.00s) - Stand-off: Boss at X=0, Player at X=150 (Gap: 150 cm)"),
        ("temp_topdown_F24_Impact.png", "F24 (0.80s) - IMPACT: Player advances to X=60 (Thrust deep into chest)"),
        ("temp_topdown_F_End.png", "Last Frame - Recovery: Boss kneeling at X=0, Player combat idle at X=60")
    ]
    
    for idx, (filename, badge_text) in enumerate(panel_info):
        f_path = os.path.join(anim_dir, filename)
        x_pos = idx * panel_w
        y_pos = header_h
        
        if os.path.exists(f_path):
            img = Image.open(f_path)
            sheet.paste(img, (x_pos, y_pos))
            
            # Panel divider line
            if idx > 0:
                draw.line([(x_pos, header_h), (x_pos, total_h)], fill=(50, 54, 64), width=2)
                
            # Badge overlay
            draw.rectangle([(x_pos + 8, y_pos + 8), (x_pos + 460, y_pos + 32)], fill=(12, 14, 18))
            draw.text((x_pos + 14, y_pos + 12), badge_text, fill=(255, 255, 255), font=font_badge)
            
            try:
                os.remove(f_path)
            except:
                pass
                
    out_path = os.path.join(anim_dir, "contact_sheet_Riposte_Paired_TopDown.png")
    sheet.save(out_path, "PNG")
    print(f"Saved paired top-down sheet: {out_path} ({sheet.size})")

if __name__ == "__main__":
    stitch_topdown()
