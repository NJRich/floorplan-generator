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

    # Draw the outer boundary
    draw.rectangle([10, 10, width - 10, height - 10], outline="black", width=5)

    # Room templates and estimated size
    room_templates = {
        "exam": ("Exam Room", (150, 100)),
        "waiting": ("Waiting Area", (200, 100)),
        "office": ("Office", (150, 100)),
        "lounge": ("Staff Lounge", (200, 100))
    }

    # Count room types in prompt
    prompt_lower = prompt.lower()
    room_counts = {}
    for key in room_templates:
        count = 1  # default
        if f"2 {key}" in prompt_lower:
            count = 2
        elif f"3 {key}" in prompt_lower:
            count = 3
        elif f"{key}s" in prompt_lower:
            count = 2
        room_counts[key] = count if key in prompt_lower else 0

    # Draw rooms
    margin_x, margin_y = 20, 20
    offset_x, offset_y = 30, 30
    curr_x, curr_y = margin_x, margin_y

    for key, count in room_counts.items():
        label, (rw, rh) = room_templates[key]
        for i in range(count):
            box = [curr_x, curr_y, curr_x + rw, curr_y + rh]
            draw.rectangle(box, outline="blue", width=3)
            draw.text((curr_x + 5, curr_y + 5), f"{label} {i+1}", fill="black")
            curr_x += rw + offset_x
            if curr_x + rw > width - margin_x:
                curr_x = margin_x
                curr_y += rh + offset_y

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

