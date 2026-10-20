import os
import math
import random
from PIL import Image, ImageDraw, ImageFilter

tex_dir = r"Import/Boss01/Weapons/Textures"
os.makedirs(tex_dir, exist_ok=True)
W, H = 4096, 4096

print("Generating rich 4K Greatsword PBR texture set...")

# ----------------------------------------------------
# 1. BaseColor Map
# ----------------------------------------------------
print("  1/4 Generating BaseColor...")
base = Image.new("RGB", (W, H), (26, 28, 32))
draw = ImageDraw.Draw(base)

# Background 2D patina variation across entire canvas
for y in range(0, H, 8):
    for x in range(0, W, 32):
        var = int(5 * math.sin(x * 0.008 + y * 0.004) + 4 * math.cos(y * 0.008 - x * 0.004))
        draw.rectangle([x, y, x + 32, y + 8], fill=(26 + var, 28 + var, 32 + var))

# Grip section: Y in [0, 1024] - Cordovan leather
for y in range(0, 1024, 2):
    phase = math.sin(y * 0.12)
    for x in range(0, W, 32):
        var = int(4 * math.sin(x * 0.01 + y * 0.005))
        r = int(45 + 15 * phase + var)
        g = int(24 + 8 * phase + var // 2)
        b = int(20 + 6 * phase + var // 2)
        draw.rectangle([x, y, x + 32, y + 2], fill=(r, g, b))

# Guard & Pommel section: Y in [1024, 2048] - Blackened iron + Bronze
for y in range(1024, 2048, 4):
    for x in range(0, W, 32):
        var = int(6 * math.sin(x * 0.012 + y * 0.006))
        r = int(22 + 10 * math.sin(y * 0.05) + var)
        g = int(24 + 10 * math.sin(y * 0.05) + var)
        b = int(27 + 10 * math.sin(y * 0.05) + var)
        draw.rectangle([x, y, x + 32, y + 4], fill=(r, g, b))

# Bronze relief bands on guard
for by in [1120, 1380, 1650, 1880]:
    for dy in range(-14, 15):
        f = 1.0 - abs(dy) / 14.0
        r = int(185 * f + 25 * (1 - f))
        g = int(135 * f + 25 * (1 - f))
        b = int(50 * f + 25 * (1 - f))
        draw.line([(0, by + dy), (W, by + dy)], fill=(r, g, b))

# Blade section: Y in [2048, 4096]
for y in range(2048, 4096, 4):
    # Central fuller: X in [1800, 2296]
    for x in range(1800, 2296, 16):
        var = int(3 * math.sin(x * 0.02 + y * 0.01))
        draw.rectangle([x, y, x + 16, y + 4], fill=(16 + var, 17 + var, 20 + var))
    # Outer sharpened cutting edges
    for dx in range(0, 480, 8):
        f = 1.0 - (dx / 480.0)
        shade_r = int(28 + 115 * f)
        shade_g = int(30 + 125 * f)
        shade_b = int(34 + 140 * f)
        draw.rectangle([dx, y, dx + 8, y + 4], fill=(shade_r, shade_g, shade_b))
        draw.rectangle([W - dx - 8, y, W - dx, y + 4], fill=(shade_r, shade_g, shade_b))

# 8 Notched battle chips
random.seed(42)
chip_y_list = [2250, 2480, 2750, 3050, 3320, 3580, 3820, 3990]
for cy in chip_y_list:
    for side in [0, 1]:
        depth = random.randint(25, 55)
        for dy in range(-30, 31):
            if 2048 <= cy + dy < H:
                w_chip = int(depth * (1.0 - (abs(dy) / 30.0)**2))
                if side == 0:
                    draw.line([(0, cy + dy), (w_chip, cy + dy)], fill=(75, 80, 88))
                else:
                    draw.line([(W - w_chip, cy + dy), (W, cy + dy)], fill=(75, 80, 88))

# Scratches and honing marks
for _ in range(1500):
    x1 = random.randint(0, W - 1)
    y1 = random.randint(1024, H - 1)
    ln = random.randint(15, 90)
    ang = random.uniform(-0.35, 0.35)
    x2 = int(x1 + ln * math.sin(ang))
    y2 = int(y1 + ln * math.cos(ang))
    sh = random.randint(85, 180)
    draw.line([(x1, y1), (x2, y2)], fill=(sh, sh + 6, sh + 14), width=random.randint(1, 2))

base = base.filter(ImageFilter.GaussianBlur(radius=0.4))
base_path = os.path.join(tex_dir, "T_Boss01_Greatsword_BaseColor.png")
base.save(base_path)
print("  BaseColor saved:", base_path)

# ----------------------------------------------------
# 2. Normal Map (Tangent Space)
# ----------------------------------------------------
print("  2/4 Generating Normal Map...")
norm = Image.new("RGB", (W, H), (128, 128, 255))
draw_n = ImageDraw.Draw(norm)

# Surface 2D curvature across the entire canvas
for y in range(0, H, 8):
    for x in range(0, W, 32):
        nx = int(128 + 12 * math.sin(x * 0.01 + y * 0.005))
        ny = int(128 + 12 * math.cos(y * 0.01 - x * 0.005))
        draw_n.rectangle([x, y, x + 32, y + 8], fill=(nx, ny, 245))

# Grip section: Spiral cord normals
for y in range(0, 1024, 2):
    phase = math.cos(y * 0.12)
    for x in range(0, W, 32):
        nx = int(128 + 8 * math.sin(x * 0.02))
        ny = int(128 + 45 * phase)
        draw_n.rectangle([x, y, x + 32, y + 2], fill=(nx, ny, 235))

# Blade section: Bevel slopes and fuller curvature
for y in range(2048, H, 4):
    # Left bevel faces -X: R in [80, 115]
    for x in range(0, 480, 8):
        t = x / 480.0
        nr = int(82 + 46 * t)
        draw_n.rectangle([x, y, x + 8, y + 4], fill=(nr, 128, 240))
    # Right bevel faces +X: R in [141, 174]
    for x in range(W - 480, W, 8):
        t = (W - x) / 480.0
        nr = int(174 - 46 * t)
        draw_n.rectangle([x, y, x + 8, y + 4], fill=(nr, 128, 240))
    # Fuller concave curvature (X in 1800..2296)
    for x in range(1800, 2296, 16):
        t = (x - 2048) / 248.0
        nr = int(128 - 36 * t)
        draw_n.rectangle([x, y, x + 16, y + 4], fill=(nr, 128, 245))

# Notched chips normal indentations
for cy in chip_y_list:
    for dy in range(-25, 26):
        if 2048 <= cy + dy < H:
            ny_val = int(128 + 35 * (dy / 25.0))
            draw_n.line([(0, cy + dy), (55, cy + dy)], fill=(162, ny_val, 225))
            draw_n.line([(W - 55, cy + dy), (W, cy + dy)], fill=(94, ny_val, 225))

# Guard bevels & relief
for by in [1120, 1380, 1650, 1880]:
    for dy in range(-12, 13):
        ny_val = int(128 - 42 * (dy / 12.0))
        draw_n.line([(0, by + dy), (W, by + dy)], fill=(128, ny_val, 235))

norm = norm.filter(ImageFilter.GaussianBlur(radius=0.5))
norm_path = os.path.join(tex_dir, "T_Boss01_Greatsword_Normal.png")
norm.save(norm_path)
print("  Normal map saved:", norm_path)

# ----------------------------------------------------
# 3. ORM Map (R=AO, G=Roughness, B=Metallic)
# ----------------------------------------------------
print("  3/4 Generating ORM Map...")
orm = Image.new("RGB", (W, H), (230, 128, 245))
draw_o = ImageDraw.Draw(orm)

# 2D surface variation across entire canvas
for y in range(0, H, 8):
    for x in range(0, W, 32):
        var_ao = int(8 * math.sin(x * 0.008 + y * 0.006))
        var_r = int(10 * math.cos(y * 0.008 - x * 0.006))
        draw_o.rectangle([x, y, x + 32, y + 8], fill=(225 + var_ao, 128 + var_r, 245))

# Grip: Non-metal (B=0), rough leather (G=190..215), AO crevice (R=90..180)
for y in range(0, 1024, 2):
    phase = math.sin(y * 0.12)
    for x in range(0, W, 32):
        var = int(5 * math.sin(x * 0.01))
        ao = int(140 + 70 * phase + var)
        rough = int(195 + 20 * phase + var)
        draw_o.rectangle([x, y, x + 32, y + 2], fill=(ao, rough, 0))

# Guard: Metallic (B=245), medium rough (G=140..170), AO relief (R=120..240)
for y in range(1024, 2048, 4):
    for x in range(0, W, 32):
        var = int(8 * math.sin(x * 0.012 + y * 0.006))
        rough = int(150 + 20 * math.sin(y * 0.05) + var)
        ao = int(210 + 35 * math.sin(y * 0.05) + var)
        draw_o.rectangle([x, y, x + 32, y + 4], fill=(ao, rough, 245))

# Blade: Metal (B=250)
for y in range(2048, H, 4):
    # Sharp edges: smooth, reflective (G=60..85, R=245)
    for dx in range(0, 480, 8):
        t = dx / 480.0
        rough = int(65 + 60 * t)
        draw_o.rectangle([dx, y, dx + 8, y + 4], fill=(245, rough, 250))
        draw_o.rectangle([W - dx - 8, y, W - dx, y + 4], fill=(245, rough, 250))
    # Fuller: rougher carbon soot (G=185), ambient shadow (R=100)
    for x in range(1800, 2296, 16):
        var = int(6 * math.sin(x * 0.02 + y * 0.01))
        draw_o.rectangle([x, y, x + 16, y + 4], fill=(100 + var, 185 + var, 220))

orm = orm.filter(ImageFilter.GaussianBlur(radius=0.5))
orm_path = os.path.join(tex_dir, "T_Boss01_Greatsword_ORM.png")
orm.save(orm_path)
print("  ORM map saved:", orm_path)

# ----------------------------------------------------
# 4. Emissive Map: Fiery runic core & pommel
# ----------------------------------------------------
print("  4/4 Generating Emissive Map...")
em = Image.new("RGB", (W, H), (0, 0, 0))
draw_e = ImageDraw.Draw(em)

# Fuller runic channel glow: Y in [2150, 3950], X in [1850, 2246]
for y in range(2150, 3950, 2):
    phase = math.sin((y - 2150) * 0.035)**2
    for dx in range(-180, 181, 2):
        f = max(0.0, 1.0 - (abs(dx) / 180.0)**1.5) * phase
        if f > 0.01:
            r = int(255 * min(1.0, f * 1.5))
            g = int(220 * (f**1.4))
            b = int(85 * (f**2.5))
            draw_e.rectangle([2048 + dx, y, 2048 + dx + 2, y + 2], fill=(r, g, b))

# Pommel ember glow: Y in [900, 1020], X in [1950, 2146]
for y in range(900, 1020, 2):
    for x in range(1950, 2146, 2):
        dist = math.sqrt((x - 2048)**2 + (y - 960)**2)
        if dist < 80:
            f = (1.0 - dist / 80.0)**1.8
            r = int(255 * f)
            g = int(185 * (f**1.3))
            b = int(55 * (f**2.2))
            draw_e.rectangle([x, y, x + 2, y + 2], fill=(r, g, b))

# Add scattered glowing ember sparks across the channels
random.seed(99)
for _ in range(1200):
    x = random.randint(1820, 2276)
    y = random.randint(2150, 3950)
    rad = random.randint(2, 6)
    draw_e.ellipse([x - rad, y - rad, x + rad, y + rad], fill=(255, random.randint(170, 245), random.randint(50, 130)))

em = em.filter(ImageFilter.GaussianBlur(radius=0.8))
em_path = os.path.join(tex_dir, "T_Boss01_Greatsword_Emissive.png")
em.save(em_path)
print("  Emissive map saved:", em_path)

# Verify color count in 128x128 downsample for all 4 maps
print("\nVerifying downsampled color counts (required >= 300):")
for p, name in [(base_path, "BaseColor"), (norm_path, "Normal"), (orm_path, "ORM"), (em_path, "Emissive")]:
    im = Image.open(p).convert("RGB")
    c = len(set(im.resize((128, 128)).getdata()))
    print(f"  {name:10s}: {c} colors (PASS if >= 300)")
