import streamlit as st
from PIL import Image, ImageDraw
import re, math

st.set_page_config(page_title="AI Floor Plan Generator", layout="centered")
st.title("🧠 AI Floor Plan Generator")
st.write("Describe your space and we'll generate a basic floor plan layout.")

prompt = st.text_area("✍️ Describe your space:", placeholder="e.g. A clinic with 3 exam rooms and a waiting area")

def parse_prompt(prompt):
    default_sizes = {
        "exam room": (10.0, 13.0),
        "waiting area": (12.0, 12.0),
        "cafe": (15.0, 15.0),
        "lobby": (18.0, 18.0),
        "staff open office": (20.0, 15.0),
        "pantry": (10.0, 10.0)
    }
    # Expand keywords to avoid plural mismatch
    keywords = list(default_sizes.keys()) + [k + "s" for k in default_sizes.keys()]
    room_counts = {}
    prompt = prompt.lower()
    for keyword in keywords:
        match = re.search(rf"(\d+|a|an)\s+{keyword}", prompt)
        if match:
            count = match.group(1)
            count = 1 if count in ["a", "an"] else int(count)
            key = keyword.rstrip("s")  # normalize plural
            room_counts[key] = room_counts.get(key, 0) + count
    rooms = []
    for room_type, count in room_counts.items():
        if room_type in default_sizes:
            w, d = default_sizes[room_type]
            for i in range(count):
                label = f"{room_type.title()} {i+1}" if count > 1 else room_type.title()
                rooms.append((label, w, d))
    return rooms

def generate_floorplan(rooms):
    scale = 10  # 1 ft = 10 px
    wall_thickness_ft = 0.5
    corridor_width_ft = 6.0
    wall_px = int(scale * wall_thickness_ft)
    margin = 20

    # Split rooms into top and bottom rows
    top, bottom = [], []
    top_len = bottom_len = 0
    for r in rooms:
        if top_len <= bottom_len:
            top.append(r)
            top_len += r[1]
        else:
            bottom.append(r)
            bottom_len += r[1]

    top_depth = max((r[2] for r in top), default=0)
    bottom_depth = max((r[2] for r in bottom), default=0)
    total_width = max(sum(r[1] for r in top), sum(r[1] for r in bottom))
    total_height = top_depth + corridor_width_ft + bottom_depth

    img_w = int((total_width + 2 * wall_thickness_ft) * scale) + 2 * margin
    img_h = int((total_height + 2 * wall_thickness_ft) * scale) + 2 * margin
    img = Image.new("RGB", (img_w, img_h), "white")
    draw = ImageDraw.Draw(img)

    ox = margin + wall_px
    oy = margin + wall_px

    def draw_row(y_start, row):
        x_cursor = 0
        for name, w, d in row:
            x1 = ox + int(x_cursor * scale)
            y1 = oy + int(y_start * scale)
            x2 = x1 + int(w * scale)
            y2 = y1 + int(d * scale)
            draw.rectangle([x1, y1, x2, y2], fill="#e6f2ff", outline="black", width=wall_px)
            draw.text((x1 + 4, y1 + 4), name, fill="black")
            x_cursor += w

    # Draw top row, corridor, bottom row
    draw_row(0, top)
    draw.rectangle(
        [ox, oy + int(top_depth * scale), ox + int(total_width * scale), oy + int((top_depth + corridor_width_ft) * scale)],
        fill="lightgray"
    )
    draw_row(top_depth + corridor_width_ft, bottom)

    return img

if st.button("Generate Floor Plan"):
    if not prompt.strip():
        st.warning("Please enter a space description.")
    else:
        st.info("Generating layout...")
        rooms = parse_prompt(prompt)
        if not rooms:
            st.error("No recognizable rooms found in the prompt.")
        else:
            image = generate_floorplan(rooms)
            st.success("✅ Floor plan generated!")
            st.image(image, caption="Auto-generated floor plan", use_container_width=True)
            st.markdown("**Prompt:** " + prompt)
