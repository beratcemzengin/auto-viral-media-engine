import random
from PIL import Image, ImageDraw, ImageFont

try:
    from . import config
except ImportError:
    import config

def draw_monster(draw, x, y, size, body_color, body_type, eye_type, mouth_type, accessory):
    """Draws a cute programmatic vector monster/robot on the draw context."""
    # 1. Draw Body
    r = size // 2
    if body_type == "circle":
        draw.ellipse([x - r, y - r, x + r, y + r], fill=body_color, outline="#333333", width=6)
    elif body_type == "square":
        draw.rectangle([x - r, y - r, x + r, y + r], fill=body_color, outline="#333333", width=6)
    elif body_type == "round_rect":
        # Draw rounded rectangle using custom bounding box
        draw.rounded_rectangle([x - r, y - r, x + r, y + r], radius=r//2, fill=body_color, outline="#333333", width=6)
    elif body_type == "triangle":
        draw.polygon([x, y - r, x - r, y + r, x + r, y + r], fill=body_color, outline="#333333", width=6)

    # 2. Draw Antennae / Horns (Accessory)
    if accessory == "antenna":
        draw.line([x, y - r, x, y - r - 25], fill="#333333", width=8)
        draw.ellipse([x - 10, y - r - 35, x + 10, y - r - 15], fill="#FFD93D", outline="#333333", width=4)
    elif accessory == "horns":
        # Left horn
        draw.polygon([x - r, y - r + 10, x - r - 15, y - r - 15, x - r + 15, y - r], fill="#FF6B6B", outline="#333333", width=4)
        # Right horn
        draw.polygon([x + r, y - r + 10, x + r + 15, y - r - 15, x + r - 15, y - r], fill="#FF6B6B", outline="#333333", width=4)

    # 3. Draw Eyes
    eye_y = y - r // 4
    if eye_type == "one_eye":
        draw.ellipse([x - 20, eye_y - 20, x + 20, eye_y + 20], fill="#FFFFFF", outline="#333333", width=4)
        draw.ellipse([x - 8, eye_y - 8, x + 8, eye_y + 8], fill="#333333")  # Pupil
        draw.ellipse([x - 5, eye_y - 5, x - 1, eye_y - 1], fill="#FFFFFF")  # Eye reflection
    elif eye_type == "two_eyes":
        # Left Eye
        draw.ellipse([x - 30, eye_y - 15, x - 5, eye_y + 10], fill="#FFFFFF", outline="#333333", width=4)
        draw.ellipse([x - 22, eye_y - 7, x - 12, eye_y + 3], fill="#333333")
        # Right Eye
        draw.ellipse([x + 5, eye_y - 15, x + 30, eye_y + 10], fill="#FFFFFF", outline="#333333", width=4)
        draw.ellipse([x + 12, eye_y - 7, x + 22, eye_y + 3], fill="#333333")
    elif eye_type == "glasses":
        # Left lens
        draw.ellipse([x - 35, eye_y - 15, x - 5, eye_y + 15], fill="#B4E4FF", outline="#FF6B6B", width=6)
        draw.ellipse([x - 22, eye_y - 7, x - 12, eye_y + 3], fill="#333333")
        # Right lens
        draw.ellipse([x + 5, eye_y - 15, x + 35, eye_y + 15], fill="#B4E4FF", outline="#FF6B6B", width=6)
        draw.ellipse([x + 12, eye_y - 7, x + 22, eye_y + 3], fill="#333333")
        # Bridge
        draw.line([x - 5, eye_y, x + 5, eye_y], fill="#FF6B6B", width=6)

    # 4. Draw Mouth
    mouth_y = y + r // 3
    if mouth_type == "smile":
        draw.arc([x - 25, mouth_y - 15, x + 25, mouth_y + 10], start=0, end=180, fill="#333333", width=6)
    elif mouth_type == "surprise":
        draw.ellipse([x - 12, mouth_y - 12, x + 12, mouth_y + 12], fill="#333333")
    elif mouth_type == "tongue":
        # Mouth arc
        draw.arc([x - 25, mouth_y - 15, x + 25, mouth_y + 5], start=0, end=180, fill="#333333", width=6)
        # Tongue shape
        draw.rounded_rectangle([x - 10, mouth_y - 2, x + 10, mouth_y + 18], radius=8, fill="#FF6B6B", outline="#333333", width=3)
    elif mouth_type == "teeth":
        # Wide smile line
        draw.line([x - 30, mouth_y, x + 30, mouth_y], fill="#333333", width=6)
        # Teeth lines
        draw.line([x - 15, mouth_y, x - 15, mouth_y + 10], fill="#333333", width=4)
        draw.line([x, mouth_y, x, mouth_y + 10], fill="#333333", width=4)
        draw.line([x + 15, mouth_y, x + 15, mouth_y + 10], fill="#333333", width=4)


def build_puzzle_layout():
    """Generates the randomized monster grid layout parameters and differences."""
    monsters_base = []
    
    # 4 Grid positions: (x, y) coordinates relative to the panel center
    positions = [
        (250, 250),   # Top Left
        (650, 250),   # Top Right
        (250, 600),   # Bottom Left
        (650, 600)    # Bottom Right
    ]
    
    # Colors pool
    colors = ["#FF6B6B", "#4D96FF", "#6BCB77", "#FFD93D", "#FF9F29", "#FF8AAE", "#9E7676"]
    body_types = ["circle", "square", "round_rect", "triangle"]
    eye_types = ["one_eye", "two_eyes", "glasses"]
    mouth_types = ["smile", "surprise", "tongue", "teeth"]
    accessories = ["none", "antenna", "horns"]
    
    for x, y in positions:
        monsters_base.append({
            "x": x, "y": y,
            "size": 170,
            "body_color": random.choice(colors),
            "body_type": random.choice(body_types),
            "eye_type": random.choice(eye_types),
            "mouth_type": random.choice(mouth_types),
            "accessory": random.choice(accessories)
        })

    # Pick 3 random differences on 3 different monsters
    differences = []
    diff_targets = random.sample(range(4), 3)  # Select 3 distinct monsters to modify
    
    # Difference 1: Change body color of target 1
    m_idx = diff_targets[0]
    old_color = monsters_base[m_idx]["body_color"]
    new_color = random.choice([c for c in colors if c != old_color])
    differences.append({
        "monster_idx": m_idx,
        "type": "color",
        "old_val": old_color,
        "new_val": new_color
    })
    
    # Difference 2: Change mouth type of target 2
    m_idx = diff_targets[1]
    old_mouth = monsters_base[m_idx]["mouth_type"]
    new_mouth = random.choice([m for m in mouth_types if m != old_mouth])
    differences.append({
        "monster_idx": m_idx,
        "type": "mouth",
        "old_val": old_mouth,
        "new_val": new_mouth
    })
    
    # Difference 3: Change accessory of target 3
    m_idx = diff_targets[2]
    old_acc = monsters_base[m_idx]["accessory"]
    new_acc = random.choice([a for a in accessories if a != old_acc])
    differences.append({
        "monster_idx": m_idx,
        "type": "accessory",
        "old_val": old_acc,
        "new_val": new_acc
    })
    
    return monsters_base, differences, positions


def render_frame(monsters_base, differences, positions, frame_idx, total_frames, bg_color, bg_music=""):
    """Renders a single video frame of 1080x1920 containing the interactive game."""
    width, height = 1080, 1920
    canvas = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(canvas)
    
    # Fonts
    try:
        font_title = ImageFont.truetype(config.FONT_PATH, 74)
        font_sub = ImageFont.truetype(config.FONT_PATH, 44)
    except IOError:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # 1. Draw Title Header
    draw.text((width // 2, 100), "SPOT THE DIFFERENCES!", fill="#FF6B6B", anchor="mm", font=font_title)
    draw.text((width // 2, 160), "Can you find all 3 differences?", fill="#4D96FF", anchor="mm", font=font_sub)

    # 2. Draw Top Box (Original)
    # Box margins: x: 90 to 990, y: 220 to 1020 (height 800)
    draw.rounded_rectangle([90, 220, 990, 1020], fill="#FFFFFF", outline="#333333", width=8, radius=20)
    top_draw_img = Image.new('RGBA', (900, 800), (0, 0, 0, 0))
    top_draw = ImageDraw.Draw(top_draw_img)
    for m in monsters_base:
        draw_monster(top_draw, m["x"], m["y"], m["size"], m["body_color"], m["body_type"], m["eye_type"], m["mouth_type"], m["accessory"])
    canvas.paste(top_draw_img, (90, 220), top_draw_img)

    # 3. Draw Bottom Box (Modified)
    # Box margins: x: 90 to 990, y: 1080 to 1880 (height 800)
    draw.rounded_rectangle([90, 1080, 990, 1880], fill="#FFFFFF", outline="#333333", width=8, radius=20)
    bottom_draw_img = Image.new('RGBA', (900, 800), (0, 0, 0, 0))
    bottom_draw = ImageDraw.Draw(bottom_draw_img)
    
    # Build modified monster list
    modified_monsters = [dict(m) for m in monsters_base]
    for d in differences:
        m_idx = d["monster_idx"]
        if d["type"] == "color":
            modified_monsters[m_idx]["body_color"] = d["new_val"]
        elif d["type"] == "mouth":
            modified_monsters[m_idx]["mouth_type"] = d["new_val"]
        elif d["type"] == "accessory":
            modified_monsters[m_idx]["accessory"] = d["new_val"]

    for m in modified_monsters:
        draw_monster(bottom_draw, m["x"], m["y"], m["size"], m["body_color"], m["body_type"], m["eye_type"], m["mouth_type"], m["accessory"])
    canvas.paste(bottom_draw_img, (90, 1080), bottom_draw_img)

    # 4. Timer Bar & Reveal Logic
    # 15 seconds video (450 frames at 30 fps)
    # First 11 seconds (330 frames) = Timer ticking
    # Last 4 seconds (120 frames) = Reveal solutions
    timer_duration = int(total_frames * 0.73)  # ~11 seconds
    
    if frame_idx < timer_duration:
        # Drawing shrinking timer bar
        remaining_ratio = 1 - (frame_idx / timer_duration)
        bar_width = int((900) * remaining_ratio)
        if bar_width > 0:
            # Draw timer background track
            draw.rounded_rectangle([90, 1040, 990, 1060], fill="#EAEAEA", radius=10)
            # Draw timer progress fill
            draw.rounded_rectangle([90, 1040, 90 + bar_width, 1060], fill="#4D96FF", radius=10)
    else:
        # Reveal Phase: Draw pulsing red circle outlines over the differences!
        draw.rounded_rectangle([90, 1040, 990, 1060], fill="#EAEAEA", radius=10)
        draw.text((width // 2, 1050), "TIME'S UP!", fill="#FF6B6B", anchor="mm", font=font_sub)
        
        # Red pulsing circle reveal helper
        pulse_scale = 1.0 + 0.15 * (frame_idx % 15) / 15.0
        for d in differences:
            m_idx = d["monster_idx"]
            pos = positions[m_idx]
            # Center of the difference on bottom box is (90 + x, 1080 + y)
            cx, cy = 90 + pos[0], 1080 + pos[1]
            r = int(110 * pulse_scale)
            # Draw thick dashed/dotted indicator circle
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline="#FF6B6B", width=8)

    return canvas
