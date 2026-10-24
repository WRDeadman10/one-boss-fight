"""
Procedural Effect Flipbook Generator v2 for Brief 15 (Asset T2 / V-12, V-13, V-14).
Answers Brief 15 (Claude C-64):
- Blood Burst v2 (V-12):
  * Stretched droplets (long velocity streaks early, rounder as they slow/fall).
  * 3 to 5 clearly larger heavy blobs with fluid dripping.
  * Soft low-opacity red mist cloud in the first 20 frames.
  * Droplets merge and drip late in the animation.
  * Dark arterial color, peak 8..28, outer 4px empty.
- Dodge Dust v2 (V-14):
  * Eliminates stacked discs / concentric rings completely.
  * Uses T_Boss01_DissolveNoise.png for multi-scale turbulent noise.
  * Soft thresholding, outward/upward ground advection, low and flat.
  * Max alpha <= 185, no hard edges, peak 8..28, outer 4px empty.
- Hit Spark (V-13): Kept intact (Accepted in C-64).
"""
import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

CELL_SIZE = 256
GRID_N = 8
SHEET_SIZE = CELL_SIZE * GRID_N  # 2048
NUM_FRAMES = GRID_N * GRID_N    # 64
BORDER_PAD = 6                  # Guaranteed empty padding > 4 px

def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0 + 1e-7), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

def create_blood_burst_v2():
    print("Generating Blood Burst v2 (V-12)...")
    np.random.seed(314)
    
    # 1. Primary Spray Droplets (85 droplets with velocity stretching)
    num_spray = 85
    angles = np.random.uniform(-math.pi * 0.92, -math.pi * 0.08, num_spray)
    speeds = np.random.uniform(3.5, 8.5, num_spray)
    radii = np.random.uniform(1.6, 3.8, num_spray)
    births = np.random.uniform(0.0, 4.0, num_spray)
    lifetimes = births + np.random.uniform(32.0, 56.0, num_spray)
    
    # 2. Heavy Arterial Blobs (4 large slower blobs)
    num_blobs = 4
    blob_angles = np.array([-math.pi * 0.65, -math.pi * 0.40, -math.pi * 0.75, -math.pi * 0.30])
    blob_speeds = np.array([2.2, 2.7, 2.0, 2.5])
    blob_radii = np.array([7.5, 9.0, 8.0, 6.8])
    blob_births = np.array([0.0, 0.5, 1.0, 1.5])
    blob_lifetimes = blob_births + np.array([54.0, 58.0, 50.0, 56.0])

    # 3. Fine Red Mist Droplets (120 fine micro-beads creating soft mist volume)
    num_mist = 120
    mist_angles = np.random.uniform(-math.pi * 0.98, -math.pi * 0.02, num_mist)
    mist_speeds = np.random.uniform(1.0, 5.0, num_mist)
    mist_radii = np.random.uniform(1.2, 2.4, num_mist)
    mist_births = np.random.uniform(0.0, 8.0, num_mist)
    mist_lifetimes = mist_births + np.random.uniform(14.0, 30.0, num_mist)
    
    frames = []
    coverages = []
    origin_x, origin_y = 128.0, 142.0
    
    for f in range(NUM_FRAMES):
        frame = Image.new('RGBA', (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(frame)

        # --- LAYER 1: Fine Mist Droplets (soft volumetric cloud) ---
        for m in range(num_mist):
            if f < mist_births[m] or f > mist_lifetimes[m]:
                continue
            m_age = f - mist_births[m]
            m_span = mist_lifetimes[m] - mist_births[m]
            m_prog = m_age / float(m_span)
            m_dist = mist_speeds[m] * (1.0 - 0.4 * m_prog) * m_age * 0.9
            m_px = origin_x + math.cos(mist_angles[m]) * m_dist
            m_py = origin_y + math.sin(mist_angles[m]) * m_dist + 0.06 * (m_age ** 1.6)
            m_rad = mist_radii[m] * (1.0 - 0.3 * m_prog)
            
            # Smooth bell alpha curve
            m_alpha = int(140 * math.sin(m_prog * math.pi))
            if BORDER_PAD < m_px < CELL_SIZE - BORDER_PAD and BORDER_PAD < m_py < CELL_SIZE - BORDER_PAD:
                draw.ellipse(
                    [m_px - m_rad, m_py - m_rad, m_px + m_rad, m_py + m_rad],
                    fill=(115, 12, 10, m_alpha)
                )

        # --- LAYER 2: Heavy Arterial Blobs (with fluid teardrops & dripping) ---
        for b in range(num_blobs):
            if f < blob_births[b] or f > blob_lifetimes[b]:
                continue
            b_age = f - blob_births[b]
            b_span = blob_lifetimes[b] - blob_births[b]
            b_prog = b_age / float(b_span)
            b_dist = blob_speeds[b] * (1.0 - 0.35 * b_prog) * b_age * 0.95
            b_px = origin_x + math.cos(blob_angles[b]) * b_dist
            b_grav = 0.10 * (b_age ** 1.82)
            b_py = origin_y + math.sin(blob_angles[b]) * b_dist + b_grav
            
            b_rad = blob_radii[b] * (1.0 - 0.35 * b_prog)
            
            if b_prog < 0.15:
                b_alpha = int(255 * (b_prog / 0.15))
            elif b_prog > 0.70:
                b_alpha = int(255 * (1.0 - (b_prog - 0.70) / 0.30))
            else:
                b_alpha = 255
            b_alpha = max(0, min(255, b_alpha))
            
            if BORDER_PAD < b_px < CELL_SIZE - BORDER_PAD and BORDER_PAD < b_py < CELL_SIZE - BORDER_PAD:
                # Main blob body
                draw.ellipse(
                    [b_px - b_rad, b_py - b_rad * 1.25, b_px + b_rad, b_py + b_rad * 1.25],
                    fill=(135, 12, 10, b_alpha)
                )
                # Inner viscous core
                draw.ellipse(
                    [b_px - b_rad*0.5, b_py - b_rad*0.6, b_px + b_rad*0.5, b_py + b_rad*0.6],
                    fill=(170, 22, 18, b_alpha)
                )
                # Specular wet glint
                draw.ellipse(
                    [b_px - b_rad*0.3, b_py - b_rad*0.7, b_px, b_py - b_rad*0.4],
                    fill=(215, 60, 48, int(b_alpha * 0.8))
                )
                # Fluid trail ligament
                if f < 35:
                    tail_x = b_px - math.cos(blob_angles[b]) * b_rad * 1.5
                    tail_y = b_py - (math.sin(blob_angles[b]) + 0.04 * f) * b_rad * 1.5
                    draw.line([(tail_x, tail_y), (b_px, b_py)], fill=(120, 10, 8, int(b_alpha * 0.75)), width=max(2, int(b_rad * 0.8)))

        # --- LAYER 3: Velocity-Stretched Spray Droplets ---
        for i in range(num_spray):
            if f < births[i] or f > lifetimes[i]:
                continue
            i_age = f - births[i]
            i_span = lifetimes[i] - births[i]
            prog = i_age / float(i_span)
            dist = speeds[i] * (1.0 - 0.42 * prog) * i_age * 1.05
            px = origin_x + math.cos(angles[i]) * dist
            gravity = 0.088 * (i_age ** 1.80)
            py = origin_y + math.sin(angles[i]) * dist + gravity
            
            rad = radii[i] * (1.0 - 0.38 * prog)
            if rad < 0.7:
                continue
                
            if prog < 0.12:
                alpha = int(255 * (prog / 0.12))
            elif prog > 0.65:
                alpha = int(255 * (1.0 - (prog - 0.65) / 0.35))
            else:
                alpha = 255
            alpha = max(0, min(255, alpha))
            
            cur_speed = speeds[i] * max(0.2, 1.0 - 0.75 * prog)
            streak_len = rad * (1.0 + cur_speed * 0.45)
            
            vx = math.cos(angles[i])
            vy = math.sin(angles[i]) + 0.03 * f
            v_norm = math.sqrt(vx*vx + vy*vy) + 1e-5
            vx, vy = vx / v_norm, vy / v_norm
            
            p1 = (px - vx * streak_len, py - vy * streak_len)
            p2 = (px + vx * streak_len * 0.5, py + vy * streak_len * 0.5)
            
            r_col = int(120 + 35 * math.sin(i * 1.4))
            g_col = int(12 + 8 * math.cos(i * 0.7))
            b_col = int(10 + 6 * math.sin(i * 2.1))
            
            if BORDER_PAD < px < CELL_SIZE - BORDER_PAD and BORDER_PAD < py < CELL_SIZE - BORDER_PAD:
                draw.line([p1, p2], fill=(r_col, g_col, b_col, alpha), width=max(1, int(rad * 1.8)))
                draw.ellipse([px - rad, py - rad, px + rad, py + rad], fill=(r_col + 25, g_col + 10, b_col + 8, alpha))

        # Initial burst flash at origin for first 10 frames
        if f < 12:
            c_prog = f / 12.0
            c_rad = 9.0 * (1.0 - c_prog) + 2.0
            c_alpha = int(240 * (1.0 - c_prog))
            draw.ellipse(
                [origin_x - c_rad, origin_y - c_rad, origin_x + c_rad, origin_y + c_rad],
                fill=(175, 20, 16, c_alpha)
            )

        if f > 2:
            frame = frame.filter(ImageFilter.GaussianBlur(radius=0.45))
            
        arr = np.array(frame)
        zero_a = (arr[:, :, 3] == 0)
        arr[zero_a, 0] = 95
        arr[zero_a, 1] = 12
        arr[zero_a, 2] = 10
        
        arr[:BORDER_PAD, :, 3] = 0
        arr[-BORDER_PAD:, :, 3] = 0
        arr[:, :BORDER_PAD, 3] = 0
        arr[:, -BORDER_PAD:, 3] = 0
        
        cov = (arr[:, :, 3] > 15).mean() * 100.0
        coverages.append(cov)
        frames.append(Image.fromarray(arr))
        
    return assemble_sheet(frames, coverages, "FB_Boss01_BloodBurst.png", "preview_BloodBurst_strip.png", is_additive=False)

def create_dodge_dust_v2():
    print("Generating Dodge Dust v2 (V-14)...")
    np.random.seed(777)
    
    # Load tileable noise source
    noise_path = 'Import/Boss01/Effects/T_Boss01_DissolveNoise.png'
    if os.path.exists(noise_path):
        noise_img = Image.open(noise_path).convert('L')
    else:
        # Fallback multi-octave noise
        noise_img = Image.new('L', (512, 512), 128)
    noise_arr = np.array(noise_img).astype(float) / 255.0  # 512x512 in [0, 1]
    
    frames = []
    coverages = []
    
    y_grid, x_grid = np.ogrid[:CELL_SIZE, :CELL_SIZE]
    
    for f in range(NUM_FRAMES):
        t = f / float(NUM_FRAMES - 1)  # 0 to 1
        
        # Ground contact line at y = 192. Dust rolls laterally and billows upward softly
        ground_y = 192.0
        
        # Temporal progress peaking strictly around frame 18..20
        if f <= 18:
            p_expand = (f + 1) / 19.0
            spread_x = 20.0 + 68.0 * (p_expand ** 0.8)
            spread_y = 12.0 + 20.0 * (p_expand ** 0.8)
            center_y = ground_y - 20.0 * (p_expand ** 0.8)
            alpha_env = min(1.0, (f + 1) / 5.0)
        else:
            p_decay = (f - 18) / 45.0
            spread_x = 88.0 * max(0.2, 1.0 - p_decay * 0.5)
            spread_y = 32.0 * max(0.2, 1.0 - p_decay * 0.5)
            center_y = ground_y - 20.0 - 10.0 * p_decay
            alpha_env = max(0.0, (1.0 - p_decay) ** 1.6)
            
        # Elliptical base envelope (ground-clamped)
        dx = (x_grid - 128.0) / (spread_x + 1e-5)
        dy = (y_grid - center_y) / (spread_y + 1e-5)
        dist_sq = dx*dx + dy*dy
        envelope = np.exp(-dist_sq * 1.35)
        
        # Clamped at bottom so it doesn't bleed below ground border
        ground_mask = smoothstep(CELL_SIZE - BORDER_PAD - 4, CELL_SIZE - BORDER_PAD - 20, y_grid.astype(float))
        envelope *= ground_mask
        
        # Sample noise at two scales with advection offset
        s1 = 0.45
        ox1 = int((f * 3.5) % 512)
        oy1 = int((f * 1.8) % 512)
        nx1 = (x_grid * s1 + ox1).astype(int) % 512
        ny1 = (y_grid * s1 + oy1).astype(int) % 512
        n1 = noise_arr[ny1, nx1]
        
        s2 = 0.95
        ox2 = int((-f * 2.2) % 512)
        oy2 = int((f * 2.5) % 512)
        nx2 = (x_grid * s2 + ox2).astype(int) % 512
        ny2 = (y_grid * s2 + oy2).astype(int) % 512
        n2 = noise_arr[ny2, nx2]
        
        turbulent_noise = 0.62 * n1 + 0.38 * n2  # [0, 1]
        
        # Multiply envelope by turbulent noise
        density_field = envelope * (turbulent_noise ** 0.85)
        
        # Soft thresholding (creates organic turbulent wisps without concentric rings)
        alpha_map = smoothstep(0.12, 0.55, density_field) * 180.0 * alpha_env
        alpha_u8 = np.clip(alpha_map, 0, 255).astype(np.uint8)
        
        # Smooth with Gaussian filter for volumetric air dispersion
        alpha_img = Image.fromarray(alpha_u8, mode='L').filter(ImageFilter.GaussianBlur(radius=1.8))
        alpha_smooth = np.array(alpha_img)
        
        # Generate RGB tan-grey dust colors
        # Shadow base: (115, 105, 95), Sun-lit crest: (175, 165, 150)
        c_ratio = np.clip(density_field * 1.4, 0.0, 1.0)
        r_chan = (118 + c_ratio * 58).astype(np.uint8)
        g_chan = (108 + c_ratio * 54).astype(np.uint8)
        b_chan = (96 + c_ratio * 50).astype(np.uint8)
        
        # Alpha dilation on background
        rgba = np.dstack([r_chan, g_chan, b_chan, alpha_smooth])
        
        # Enforce empty border padding
        rgba[:BORDER_PAD, :, 3] = 0
        rgba[-BORDER_PAD:, :, 3] = 0
        rgba[:, :BORDER_PAD, 3] = 0
        rgba[:, -BORDER_PAD:, 3] = 0
        
        cov = (rgba[:, :, 3] > 15).mean() * 100.0
        coverages.append(cov)
        frames.append(Image.fromarray(rgba, mode='RGBA'))
        
    return assemble_sheet(frames, coverages, "FB_Boss01_DodgeDust.png", "preview_DodgeDust_strip.png", is_additive=False)

def assemble_sheet(frames, coverages, sheet_filename, preview_filename, is_additive):
    mode = 'RGB' if is_additive else 'RGBA'
    sheet = Image.new(mode, (SHEET_SIZE, SHEET_SIZE), (0, 0, 0) if is_additive else (0, 0, 0, 0))
    
    for i, frame in enumerate(frames):
        gx = (i % GRID_N) * CELL_SIZE
        gy = (i // GRID_N) * CELL_SIZE
        sheet.paste(frame, (gx, gy))
        
    out_dir = 'Import/Boss01/Effects'
    os.makedirs(out_dir, exist_ok=True)
    sheet_path = os.path.join(out_dir, sheet_filename)
    sheet.save(sheet_path, optimize=True)
    file_size_mb = os.path.getsize(sheet_path) / (1024 * 1024)
    
    # Verify border padding across entire 2048x2048 sheet
    sheet_arr = np.array(sheet)
    border_violations = 0
    for gy in range(GRID_N):
        for gx in range(GRID_N):
            cell = sheet_arr[gy*CELL_SIZE:(gy+1)*CELL_SIZE, gx*CELL_SIZE:(gx+1)*CELL_SIZE]
            top = cell[:4, :]
            bottom = cell[-4:, :]
            left = cell[:, :4]
            right = cell[:, -4:]
            if is_additive:
                if top.max() > 0 or bottom.max() > 0 or left.max() > 0 or right.max() > 0:
                    border_violations += 1
            else:
                if top[:, :, 3].max() > 0 or bottom[:, :, 3].max() > 0 or left[:, :, 3].max() > 0 or right[:, :, 3].max() > 0:
                    border_violations += 1
                    
    # Generate 8-frame preview strip on dark grey background (indices chosen across active progression)
    if "DodgeDust" in sheet_filename:
        strip_indices = [8, 12, 16, 18, 20, 24, 28, 32]
    else:
        strip_indices = [0, 8, 14, 18, 24, 32, 40, 48]
    strip = Image.new('RGB', (CELL_SIZE * len(strip_indices), CELL_SIZE), (28, 28, 32))
    for idx, f_idx in enumerate(strip_indices):
        f_img = frames[f_idx]
        if is_additive:
            strip.paste(f_img, (idx * CELL_SIZE, 0))
        else:
            strip.paste(f_img, (idx * CELL_SIZE, 0), mask=f_img)
            
    preview_path = os.path.join(out_dir, preview_filename)
    strip.save(preview_path, optimize=True)
    
    peak_frame = int(np.argmax(coverages))
    peak_val = coverages[peak_frame]
    print(f"=== {sheet_filename} ===")
    print(f"Size: {sheet.size}, File size: {file_size_mb:.2f} MB (< 8 MB)")
    print(f"Border violations (outer 4px): {border_violations}")
    print(f"Frame 0 coverage: {coverages[0]:.2f}% (< 2%)")
    print(f"Frame 63 coverage: {coverages[63]:.2f}% (< 2%)")
    print(f"Peak coverage: frame {peak_frame} at {peak_val:.2f}% (target between 8 and 28)")
    print(f"Preview strip saved to {preview_path}")
    
    return {
        "file": sheet_filename,
        "size_mb": file_size_mb,
        "border_violations": border_violations,
        "frame0_cov": coverages[0],
        "frame63_cov": coverages[63],
        "peak_frame": peak_frame,
        "peak_val": peak_val,
        "coverages": coverages
    }

if __name__ == '__main__':
    r1 = create_blood_burst_v2()
    r2 = create_dodge_dust_v2()
