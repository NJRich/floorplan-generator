import streamlit as st
from PIL import Image, ImageDraw

# Page setup
st.set_page_config(page_title="AI Floor Plan Generator", layout="centered")
st.title("🧠 AI Floor Plan Generator")
st.write("Describe your space and we'll generate a basic floor plan layout.")

# Input prompt
prompt = st.text_area("✍️ Describe your space:", placeholder="e.g. A clinic with 2 exam rooms and a waiting area")

# Function to generate a basic layout image
def generate_floorplan(prompt):
    width, height = 600, 400
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # Draw building outer boundary
    margin = 20
    building_box = (margin, margin, width - margin, height - margin)
    draw.rectangle(building_box, outline="black", width=5)

    # Define known room types and layout slots
    room_templates = {
        "exam": "Exam Room",
        "waiting": "Waiting Area",
        "office": "Office",
        "lounge": "Staff Lounge"
    }

    # Get room types from prompt
    matched_rooms = [key for key in room_templates if key in prompt.lower()]

    # Layout logic: simple grid inside the building
    cols = 2
    room_width = (width - 2 * margin) // cols
    room_height = 100
    x_start = margin
    y_start = margin + 10

    for i, key in enumerate(matched_rooms):
        col = i % cols
        row = i // cols
        x0 = x_start + col * room_width
        y0 = y_start + row * (room_height + 10)
        x1 = x0 + room_width - 10
        y1 = y0 + room_height

        draw.rectangle((x0, y0, x1, y1), outline="blue", width=2)
        draw.text((x0 + 10, y0 + 10), room_templates[key], fill="black")

    return image

# Generate button
if st.button("Generate Floor Plan"):
    if not prompt.strip():
        st.warning("Please enter a space description.")
    else:
        st.info("Generating layout...")
        image = generate_floorplan(prompt)
        st.success("✅ Floor plan generated!")
        st.image(image, caption="Auto-generated floor plan", use_container_width=True)
        st.markdown("**Prompt:** " + prompt)

