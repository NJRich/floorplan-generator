import streamlit as st
from PIL import Image, ImageDraw
import math, re

# Streamlit setup
st.set_page_config(page_title="AI Floor Plan Generator", layout="centered")
st.title("🧠 AI Floor Plan Generator")
st.write("Describe your space and we'll generate a basic floor plan layout.")

# Prompt input
prompt = st.text_area("✍️ Describe your space:", placeholder="e.g. A clinic with 2 exam rooms and a waiting area")

def parse_prompt_to_rooms(prompt_text):
    default_room_sizes = {
        "exam room": (10.0, 13.0),
        "waiting area": (12.0, 12.0),
        "cafe": (15.0, 15.0),
        "lobby": (18.0, 18.0),
        "staff open office": (20.0, 15.0),
        "pantry": (10.0, 10.0)
    }
    # Support plural forms
    plural_map = {k + "s": k for k in default_room_sizes}
    all_keys = set(default_room_sizes) | set(plural_map)

    # Number words
    num_words = {
        "a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4,
        "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
    }

    room_list = []
    clean = prompt_text.lower().replace(" and ", ", ")
    for phrase in re.split(r",|;", clean):
        words = phrase.strip().split()
        if not words:
            continue
        # Get count
        if words[0].isdigit():
            count = int(words[0])
            room_type = " ".join(words[1:])
        elif words[0] in num_words:
            count = num_words[words[0]]
            room_type = " ".join(words[1:])
        else:
            count = 1
            room_type = " ".join(words)
        room_type = room_type.strip()
        if room_type in plural_map:
            room_type = plural_map[room_type]
        if room_type in default_room_sizes:
            width, depth = default_room_sizes[room_type]
            for i in range(1, count + 1):
                label = f"{room_type.title()} {i}" if count > 1 else room_type.title()
                room_list.append((label, width, depth))
    return room_list

def generate_floorplan(prompt):
    scale = 10  # 1 ft = 10 pixels
    wall_thickness_ft = 0.5
    corridor_width_ft = 6.0
    margin = 20
    wall_px = int(wall_thickness_ft * scale)

    room_list = parse_prompt_to_rooms(prompt)
    if not room_list:
        return None

    # Split rooms top/bottom
    top_rooms = room_list[:len(room_list)//2]
    bottom_rooms = room_list[len(room_list)//2:]

    top_depth = max((d for _, _, d in top_rooms), default=0)
    bottom_depth = max((d for _, _, d in bottom_rooms), default=0)
    corridor_length = max(sum(w for _, w, _ in top_rooms), sum(w for _, w, _ in bottom_rooms))

    interior_width = corridor_length
    interior_height = top_depth + corridor_width_ft + bottom_depth

    img_w = int((interior_width + 2 * wall_thickness_ft) * scale) + 2 * margin
    img_h = int((interior_height + 2 * wall_thickness_ft) * scale) + 2 * margin
    img = Image.new("RGB", (img_w, img_h), "white")
    draw = ImageDraw.Draw(img)

    offset_x = margin + int(wall_thickness_ft * scale)
    offset_y = margin + int(wall_thickness_ft * scale)

    def draw_rooms(rooms, y_start_ft):
        x_cursor_ft = 0.0
        for name, width_ft, depth_ft in rooms:
            x1 = offset_x + int(x_cursor_ft * scale)
            y1 = offset_y + int(y_start_ft * scale)
            x2 = x1 + int(width_ft * scale)
            y2 = y1 + int(depth_ft * scale)
            draw.rectangle([x1, y1, x2, y2], fill="#e6f2ff", outline="black", width=wall_px)
            draw.text((x1 + 4, y1 + 4), name, fill="black")
            x_cursor_ft += width_ft

    # Draw rooms
    draw_rooms(top_rooms, 0)
    draw_rooms(bottom_rooms, top_depth + corridor_width_ft)

    # Draw corridor
    cy1 = offset_y + int(top_depth * scale)
    cy2 = cy1 + int(corridor_width_ft * scale)
    cx1 = offset_x
    cx2 = offset_x + int(corridor_length * scale)
    draw.rectangle([cx1, cy1, cx2, cy2], fill="lightgray")

    return img

# Generate button
if st.button("Generate Floor Plan"):
    if not prompt.strip():
        st.warning("Please enter a space description.")
    else:
        st.info("Generating layout...")
        image = generate_floorplan(prompt)
        if image:
            st.success("✅ Floor plan generated!")
            st.image(image, caption="Auto-generated floor plan", use_container_width=True)
            st.markdown("**Prompt:** " + prompt)
        else:
            st.error("No valid rooms detected. Please revise your prompt.")
