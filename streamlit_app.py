import streamlit as st
from PIL import Image, ImageDraw
import math

# Streamlit setup
st.set_page_config(page_title="AI Floor Plan Generator", layout="centered")
st.title("🧠 AI Floor Plan Generator")
st.write("Describe your space and we'll generate a basic floor plan layout.")

# Prompt input
prompt = st.text_area("✍️ Describe your space:", placeholder="e.g. A clinic with 2 exam rooms and a waiting area")

def generate_floorplan():
    # Constants
    scale = 10  # 1 foot = 10 pixels
    wall_thickness_ft = 0.5  # 6 inches
    corridor_width_ft = 6.0
    margin = 20

    # Default room sizes (width, depth) in feet
    default_room_sizes = {
        "exam room": (10.0, 13.0),
        "waiting area": (12.0, 12.0),
    }

    # Sample room list: [(label, width_ft, depth_ft)]
    room_list = [
        ("Exam Room 1", *default_room_sizes["exam room"]),
        ("Exam Room 2", *default_room_sizes["exam room"]),
        ("Waiting Area", *default_room_sizes["waiting area"])
    ]

    # Layout: split into top and bottom rows
    top_rooms = [room_list[0]]
    bottom_rooms = [room_list[1], room_list[2]]

    top_depth = max(r[2] for r in top_rooms)
    bottom_depth = max(r[2] for r in bottom_rooms)
    corridor_length = max(sum(r[1] for r in top_rooms), sum(r[1] for r in bottom_rooms))

    # Interior dimensions in feet
    interior_width = corridor_length
    interior_height = top_depth + corridor_width_ft + bottom_depth
    wall_px = int(wall_thickness_ft * scale)

    # Canvas setup
    img_w = int((interior_width + 2 * wall_thickness_ft) * scale) + 2 * margin
    img_h = int((interior_height + 2 * wall_thickness_ft) * scale) + 2 * margin
    img = Image.new("RGB", (img_w, img_h), "white")
    draw = ImageDraw.Draw(img)

    # Offset for drawing
    offset_x = margin + int(wall_thickness_ft * scale)
    offset_y = margin + int(wall_thickness_ft * scale)

    # Draw rooms function
    def draw_rooms(rooms, y_start_ft):
        x_cursor_ft = 0.0
        for name, width_ft, depth_ft in rooms:
            x1 = offset_x + int(x_cursor_ft * scale)
            y1 = offset_y + int(y_start_ft * scale)
            x2 = x1 + int(width_ft * scale)
            y2 = y1 + int(depth_ft * scale)
            draw.rectangle([x1, y1, x2, y2], fill="#e6f2ff", outline="black", width=wall_px)
            draw.text((x1 + 5, y1 + 5), name, fill="black")
            x_cursor_ft += width_ft

    # Draw the layout
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
        image = generate_floorplan()
        st.success("✅ Floor plan generated!")
        st.image(image, caption="Auto-generated floor plan", use_container_width=True)
        st.markdown("**Prompt:** " + prompt)
