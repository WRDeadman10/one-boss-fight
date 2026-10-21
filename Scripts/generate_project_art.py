import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

def make_project_art():
    base_dir = r"c:\Users\winss\Documents\Unreal Projects\OneBossFight"
    splash_src_path = r"C:\Users\winss\.gemini\antigravity\brain\abaa772b-7cb4-4c71-a818-f43279ec6dcc\splash_screen_ember_warden_1792521199964.jpg"
    icon_src_path = r"C:\Users\winss\.gemini\antigravity\brain\abaa772b-7cb4-4c71-a818-f43279ec6dcc\one_boss_fight_icon_1792521205642.jpg"

    splash_dir = os.path.join(base_dir, "Content", "Splash")
    build_win_dir = os.path.join(base_dir, "Build", "Windows")
    os.makedirs(splash_dir, exist_ok=True)
    os.makedirs(build_win_dir, exist_ok=True)

    # -------------------------------------------------------------
    # 1. SPLASH SCREENS (720 x 370)
    # -------------------------------------------------------------
    raw_splash = Image.open(splash_src_path).convert("RGB")
    target_w, target_h = 720, 370

    # Scale maintaining aspect ratio and crop to 720x370
    scale = max(target_w / raw_splash.width, target_h / raw_splash.height)
    new_w = int(raw_splash.width * scale + 0.5)
    new_h = int(raw_splash.height * scale + 0.5)
    resized_splash = raw_splash.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # Center crop
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    cropped_splash = resized_splash.crop((left, top, left + target_w, top + target_h))

    # Add dark vignette and bottom gradient to make room for UE loader text
    overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    # Bottom gradient (height: 70px)
    for y in range(target_h - 70, target_h):
        alpha = int(200 * ((y - (target_h - 70)) / 70.0))
        overlay_draw.line([(0, y), (target_w, y)], fill=(8, 10, 15, alpha))

    # Top gradient for title (height: 90px)
    for y in range(90):
        alpha = int(180 * (1.0 - (y / 90.0)))
        overlay_draw.line([(0, y), (target_w, y)], fill=(8, 10, 15, alpha))

    # Apply overlay
    base_splash = Image.alpha_composite(cropped_splash.convert("RGBA"), overlay)

    # Typography setup
    # Soulslike spaced title
    font_path = r"C:\Windows\Fonts\georgiab.ttf"
    if not os.path.exists(font_path):
        font_path = r"C:\Windows\Fonts\timesbd.ttf"
    
    title_font = ImageFont.truetype(font_path, 28)
    sub_font = ImageFont.truetype(font_path, 13)

    title_text = "O N E   B O S S   F I G H T"
    sub_text = "—  T H E   E M B E R   W A R D E N  —"

    # Draw Title on Game Splash
    game_splash = base_splash.copy()
    draw_game = ImageDraw.Draw(game_splash)

    # Center title horizontally
    title_bbox = draw_game.textbbox((0, 0), title_text, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    title_x = (target_w - title_w) // 2
    title_y = 26

    # Drop shadow & glow
    for dx, dy, col in [(-1, -1, (0,0,0,180)), (1, 1, (0,0,0,220)), (0, 2, (0,0,0,240)), (0, 0, (255, 140, 30, 80))]:
        draw_game.text((title_x + dx, title_y + dy), title_text, font=title_font, fill=col)
    draw_game.text((title_x, title_y), title_text, font=title_font, fill=(245, 230, 210, 255))

    # Subtitle
    sub_bbox = draw_game.textbbox((0, 0), sub_text, font=sub_font)
    sub_w = sub_bbox[2] - sub_bbox[0]
    sub_x = (target_w - sub_w) // 2
    sub_y = title_y + 36

    draw_game.text((sub_x, sub_y + 1), sub_text, font=sub_font, fill=(0, 0, 0, 200))
    draw_game.text((sub_x, sub_y), sub_text, font=sub_font, fill=(210, 160, 90, 240))

    # Thin decorative line below title
    line_y = sub_y + 20
    draw_game.line([(target_w // 2 - 120, line_y), (target_w // 2 + 120, line_y)], fill=(180, 130, 70, 160), width=1)

    # Save Game Splash (24-bit RGB BMP and PNG)
    game_splash_rgb = game_splash.convert("RGB")
    game_splash_bmp_path = os.path.join(splash_dir, "Splash.bmp")
    game_splash_png_path = os.path.join(splash_dir, "Splash.png")
    game_splash_rgb.save(game_splash_bmp_path, format="BMP")
    game_splash_rgb.save(game_splash_png_path, format="PNG")
    print(f"Saved Game Splash: {game_splash_bmp_path}")

    # Editor Splash (distinctive UE5 Developer branding in subtitle)
    ed_splash = base_splash.copy()
    draw_ed = ImageDraw.Draw(ed_splash)

    ed_sub_text = "—  U N R E A L   E N G I N E   5 . 5  —"
    ed_sub_bbox = draw_ed.textbbox((0, 0), ed_sub_text, font=sub_font)
    ed_sub_w = ed_sub_bbox[2] - ed_sub_bbox[0]
    ed_sub_x = (target_w - ed_sub_w) // 2

    # Draw title
    for dx, dy, col in [(-1, -1, (0,0,0,180)), (1, 1, (0,0,0,220)), (0, 2, (0,0,0,240)), (0, 0, (255, 140, 30, 80))]:
        draw_ed.text((title_x + dx, title_y + dy), title_text, font=title_font, fill=col)
    draw_ed.text((title_x, title_y), title_text, font=title_font, fill=(245, 230, 210, 255))

    draw_ed.text((ed_sub_x, sub_y + 1), ed_sub_text, font=sub_font, fill=(0, 0, 0, 200))
    draw_ed.text((ed_sub_x, sub_y), ed_sub_text, font=sub_font, fill=(180, 175, 170, 220))
    draw_ed.line([(target_w // 2 - 120, line_y), (target_w // 2 + 120, line_y)], fill=(140, 135, 130, 160), width=1)

    ed_splash_rgb = ed_splash.convert("RGB")
    ed_splash_bmp_path = os.path.join(splash_dir, "EdSplash.bmp")
    ed_splash_png_path = os.path.join(splash_dir, "EdSplash.png")
    ed_splash_rgb.save(ed_splash_bmp_path, format="BMP")
    ed_splash_rgb.save(ed_splash_png_path, format="PNG")
    print(f"Saved Editor Splash: {ed_splash_bmp_path}")

    # -------------------------------------------------------------
    # 2. ICONS & PROJECT THUMBNAILS
    # -------------------------------------------------------------
    raw_icon = Image.open(icon_src_path).convert("RGBA")

    # Save Windows Multi-Resolution Icon Application.ico
    # Windows icon sizes: 16, 24, 32, 48, 64, 128, 256
    ico_path = os.path.join(build_win_dir, "Application.ico")
    ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    raw_icon.save(ico_path, format="ICO", sizes=ico_sizes)
    print(f"Saved Application.ico: {ico_path}")

    # Project Thumbnail (192 x 192 PNG) at Project Root
    thumb_192 = raw_icon.resize((192, 192), Image.Resampling.LANCZOS)
    thumb_path_1 = os.path.join(base_dir, "OneBossFight.png")
    thumb_192.save(thumb_path_1, format="PNG")
    print(f"Saved Project Thumbnail: {thumb_path_1}")

    # Also Thumbnail.png at project root
    thumb_512 = raw_icon.resize((512, 512), Image.Resampling.LANCZOS)
    thumb_path_2 = os.path.join(base_dir, "Thumbnail.png")
    thumb_512.save(thumb_path_2, format="PNG")
    print(f"Saved High-Res Thumbnail: {thumb_path_2}")

    # Saved/AutoScreenshot.png (fallback checked by UE)
    saved_dir = os.path.join(base_dir, "Saved")
    os.makedirs(saved_dir, exist_ok=True)
    auto_screen_path = os.path.join(saved_dir, "AutoScreenshot.png")
    thumb_192.save(auto_screen_path, format="PNG")
    print(f"Saved AutoScreenshot: {auto_screen_path}")

    # Content/Splash/IconDefault.bmp and EdIconDefault.bmp (64x64)
    icon_64 = raw_icon.resize((64, 64), Image.Resampling.LANCZOS)
    icon_default_bmp = os.path.join(splash_dir, "IconDefault.bmp")
    ed_icon_default_bmp = os.path.join(splash_dir, "EdIconDefault.bmp")
    icon_64.save(icon_default_bmp, format="BMP")
    icon_64.save(ed_icon_default_bmp, format="BMP")
    print(f"Saved IconDefault.bmp and EdIconDefault.bmp")

if __name__ == "__main__":
    make_project_art()
