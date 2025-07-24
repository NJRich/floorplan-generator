import streamlit as st
from PIL import Image, ImageDraw
import math, re, random

# Streamlit UI setup
st.set_page_config(page_title="AI Floor Plan Generator", layout="centered")
st.title("🧠 AI Floor Plan Generator")
st.write("Describe your space and we'll generate a basic floor plan layout.")

prompt = st.text_area("✍️ Describe your space:", placeholder="e.g. A clinic with 2 exam rooms and a waiting area")

# Floor plan generation logic
def generate_floorplan_layout(prompt: str):
    scale = 10  # 1 foot = 10 pixels
    wall_thickness = 0.5  # feet (6 inches)
    corridor_width = 6.0  # feet

    default_room_sizes = {
        "exam room":  (10.0, 13.0),
        "waiting area": (12.0, 12.0),
        "lobby":      (15.0, 15.0),
        "office":     (10.0, 10.0),
        "cafe":       (12.0, 12.0),
        "café":       (12.0, 12.0),
        "restroom":   (6.0, 8.0),
        "bathroom":   (6.0, 8.0),
    }
    default_room_sizes.update({
        "exam rooms": default_room_sizes["exam room"],
        "waiting room": default_room_sizes["waiting area"],
        "offices":    default_room_sizes["office"],
        "cafes":      default_room_sizes["cafe"]
    })

    prompt_text = prompt.lower().replace(" and ", ", ")
    parts = [p.strip() for p in re.split(r'[;,]', prompt_text) if p.strip()]
    room_list = []
    num_words = {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
        "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
    }
    for part in parts:
        tokens = part.split()
        if not tokens: continue
        count = 1
        if tokens[0] in num_words:
            count = num_words[tokens[0]]
            tokens = tokens[1:]
        elif tokens[0].isdigit():
            count = int(tokens[0])
            tokens = tokens[1:]
        elif tokens[0] in ("a", "an"):
            count = 1
            tokens = tokens[1:]
        room_type = " ".join(tokens)
        if room_type.endswith("s") and room_type[:-1] in default_room_sizes:
            room_type = room_type[:-1]
        if room_type in default_room_sizes:
            width_ft, depth_ft = default_room_sizes[room_type]
            for i in range(count):
                label = f"{room_type.title()} {i+1}" if count > 1 else room_type.title()
                room_list.append((label, width_ft, depth_ft))
    if not room_list:
        return None

    # Orientation helpers
    def partition_vertical(rooms):
        left, right = [], []
        left_len = right_len = 0.0
        left_max = right_max = 0.0
        for r in sorted(rooms, key=lambda x: x[1], reverse=True):
            if left_len <= right_len:
                left.append(r); left_len += r[1]; left_max = max(left_max, r[2])
            else:
                right.append(r); right_len += r[1]; right_max = max(right_max, r[2])
        return left, right, max(left_len, right_len), left_max, right_max

    def partition_horizontal(rooms):
        top, bot = [], []
        top_len = bot_len = 0.0
        top_max = bot_max = 0.0
        for r in sorted(rooms, key=lambda x: x[1], reverse=True):
            if top_len <= bot_len:
                top.append(r); top_len += r[1]; top_max = max(top_max, r[2])
            else:
                bot.append(r); bot_len += r[1]; bot_max = max(bot_max, r[2])
        return top, bot, max(top_len, bot_len), top_max, bot_max

    lft, rgt, vlen, ld, rd = partition_vertical(room_list)
    top, bot, hlen, td, bd = partition_horizontal(room_list)

    v_area = (ld + corridor_width + rd) * vlen
    h_area = hlen * (td + corridor_width + bd)

    vertical = v_area <= h_area
    group1, group2 = (lft, rgt) if vertical else (top, bot)
    depth1, depth2 = (ld, rd) if vertical else (td, bd)
    entrance_side = random.choice(["N", "S"] if vertical else ["E", "W"])
    layout_len = vlen if vertical else hlen

    int_width = (depth1 + corridor_width + depth2) if vertical else layout_len
    int_height = layout_len if vertical else (depth1 + corridor_width + depth2)

    margin_px = 20
    img_width = int((int_width + 2 * wall_thickness) * scale) + 2 * margin_px
    img_height = int((int_height + 2 * wall_thickness) * scale) + 2 * margin_px
    image = Image.new('RGB', (img_width, img_height), color="white")
    draw = ImageDraw.Draw(image)
    wall_px = int(wall_thickness * scale)
    ox = margin_px + int(wall_thickness * scale)
    oy = margin_px + int(wall_thickness * scale)

    # Draw corridor
    if vertical:
        cx1 = ox + int(depth1 * scale)
        cx2 = cx1 + int(corridor_width * scale)
        cy1, cy2 = oy, oy + int(layout_len * scale)
    else:
        cy1 = oy + int(depth1 * scale)
        cy2 = cy1 + int(corridor_width * scale)
        cx1, cx2 = ox, ox + int(layout_len * scale)
    draw.rectangle([cx1, cy1, cx2, cy2], fill=(200, 200, 200))

    # Draw rooms
    if vertical:
        y = 0.0
        for name, w, h in group1:
            x1 = ox
            x2 = x1 + int(h * scale)
            y1 = oy + int(y * scale)
            y2 = y1 + int(w * scale)
            draw.rectangle([x1, y1, x2, y2], fill=(220, 245, 255), outline="black", width=wall_px)
            draw.text((x1+4, y1+4), name, fill="black")
            y += w
        y = 0.0
        for name, w, h in group2:
            x1 = ox + int((depth1 + corridor_width) * scale)
            x2 = x1 + int(h * scale)
            y1 = oy + int(y * scale)
            y2 = y1 + int(w * scale)
            draw.rectangle([x1, y1, x2, y2], fill=(220, 245, 255), outline="black", width=wall_px)
            draw.text((x1+4, y1+4), name, fill="black")
            y += w
    else:
        x = 0.0
        for name, w, h in group1:
            x1 = ox + int(x * scale)
            x2 = x1 + int(w * scale)
            y1 = oy
            y2 = y1 + int(h * scale)
            draw.rectangle([x1, y1, x2, y2], fill=(220, 245, 255), outline="black", width=wall_px)
            draw.text((x1+4, y1+4), name, fill="black")
            x += w
        x = 0.0
        for name, w, h in group2:
            x1 = ox + int(x * scale)
            x2 = x1 + int(w * scale)
            y1 = oy + int((depth1 + corridor_width) * scale)
            y2 = y1 + int(h * scale)
            draw.rectangle([x1, y1, x2, y2], fill=(220, 245, 255), outline="black", width=wall_px)
            draw.text((x1+4, y1+4), name, fill="black")
            x += w

    # Draw outer walls (solid black with door opening)
    right = ox + int(int_width * scale)
    bottom = oy + int(int_height * scale)

    def draw_wall_with_door(x1, y1, x2, y2, skip=False):
        if skip:
            gap_len = int((corridor_width if vertical else layout_len) * scale)
            if x1 == x2:  # vertical line
                draw.line([x1, y1, x1, y1 + (bottom - oy - gap_len) // 2], fill="black", width=wall_px)
                draw.line([x1, y1 + (bottom - oy + gap_len) // 2, x1, bottom], fill="black", width=wall_px)
            else:  # horizontal
                draw.line([x1, y1, x1 + (right - ox - gap_len) // 2, y1], fill="black", width=wall_px)
                draw.line([x1 + (right - ox + gap_len) // 2, y1, right, y1], fill="black", width=wall_px)
        else:
            draw.line([x1, y1, x2, y2], fill="black", width=wall_px)

    draw_wall_with_door(ox, oy, right, oy, entrance_side == "N")
    draw_wall_with_door(ox, bottom, right, bottom, entrance_side == "S")
    draw_wall_with_door(ox, oy, ox, bottom, entrance_side == "W")
    draw_wall_with_door(right, oy, right, bottom, entrance_side == "E")

    return image

# Streamlit output
if st.button("Generate Floor Plan"):
    if not prompt.strip():
        st.warning("Please enter a space description.")
    else:
        st.info("Generating layout...")
        image = generate_floorplan_layout(prompt)
        if image:
            st.success("✅ Floor plan generated!")
            st.image(image, caption="Auto-generated floor plan", use_container_width=True)
            st.markdown("**Prompt:** " + prompt)
        else:
            st.error("❌ Could not detect room types from your prompt.")
