import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import math, re, random

# Page setup
st.set_page_config(page_title="AI Floor Plan Generator", layout="centered")
st.title("🧠 AI Floor Plan Generator")
st.write("Describe your space and we'll generate a basic floor plan layout.")

# Input prompt
prompt = st.text_area("🍋 Describe your space:", placeholder="e.g. a clinic with 2 exam rooms and a waiting area")

# ----------- Function to generate layout ------------
def generate_floorplan_layout(prompt: str):
    scale = 10  # 1 foot = 10 pixels
    wall_thickness = 0.5
    corridor_width = 6.0

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
        "offices": default_room_sizes["office"],
        "cafes": default_room_sizes["cafe"]
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
        if not tokens:
            continue
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

    def partition_rooms(rooms):
        left, right = [], []
        l_len = r_len = 0.0
        for r in rooms:
            if l_len <= r_len:
                left.append(r); l_len += r[1]
            else:
                right.append(r); r_len += r[1]
        return left, right, max(l_len, r_len)

    left, right, corridor_len = partition_rooms(room_list)
    left_depth = max((r[2] for r in left), default=0.0)
    right_depth = max((r[2] for r in right), default=0.0)

    w = (left_depth + corridor_width + right_depth + 2 * wall_thickness) * scale
    h = (corridor_len + 2 * wall_thickness) * scale
    margin = 20
    img = Image.new("RGB", (int(w + 2 * margin), int(h + 2 * margin)), "white")
    draw = ImageDraw.Draw(img)
    offset_x = margin + int(wall_thickness * scale)
    offset_y = margin + int(wall_thickness * scale)
    
    # Corridor (gray)
    cx = offset_x + int(left_depth * scale)
    draw.rectangle([
        (cx, offset_y),
        (cx + int(corridor_width * scale), offset_y + int(corridor_len * scale))
    ], fill=(200, 200, 200))

    # Draw rooms with wall between them
    wall_px = int(wall_thickness * scale)
    y_cursor = 0.0
    for name, w_ft, d_ft in left:
        x1 = offset_x
        x2 = offset_x + int(d_ft * scale)
        y1 = offset_y + int(y_cursor * scale)
        y2 = y1 + int(w_ft * scale)
        draw.rectangle([x1, y1, x2, y2], fill=(200, 240, 255), outline="black", width=wall_px)
        draw.text((x1 + 5, y1 + 5), name, fill="black")
        y_cursor += w_ft
        draw.line([x1, y2, x2, y2], fill="black", width=wall_px)  # bottom wall

    y_cursor = 0.0
    for name, w_ft, d_ft in right:
        x1 = offset_x + int((left_depth + corridor_width) * scale)
        x2 = x1 + int(d_ft * scale)
        y1 = offset_y + int(y_cursor * scale)
        y2 = y1 + int(w_ft * scale)
        draw.rectangle([x1, y1, x2, y2], fill=(230, 230, 230), outline="black", width=wall_px)
        draw.text((x1 + 5, y1 + 5), name, fill="black")
        y_cursor += w_ft
        draw.line([x1, y2, x2, y2], fill="black", width=wall_px)

    # Outer walls
    img_w, img_h = img.size
    draw.rectangle([margin, margin, img_w - margin, img_h - margin], outline="black", width=wall_px)
    return img

# -------------- Streamlit interaction ----------------
if st.button("Generate Floor Plan"):
    if not prompt.strip():
        st.warning("Please enter a space description.")
    else:
        st.info("Generating layout...")
        image = generate_floorplan_layout(prompt)
        if image:
            st.success("✅ Floor plan generated!")
            st.image(image, caption="Auto-generated floor plan", use_container_width=True)
        else:
            st.error("Could not recognize any rooms. Try rephrasing your prompt.")
