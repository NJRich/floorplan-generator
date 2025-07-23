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

    # Very basic logic: place rectangles based on keywords
    rooms = {
        "exam": ("Exam Room", (50, 50, 200, 150)),
        "waiting": ("Waiting Area", (250, 50, 500, 150)),
        "office": ("Office", (50, 200, 200, 300)),
        "lounge": ("Staff Lounge", (250, 200, 500, 300))
    }

    for keyword, (label, box) in rooms.items():
        if keyword in prompt.lower():
            draw.rectangle(box, outline="black", width=3)
            draw.text((box[0]+10, box[1]+10), label, fill="black")

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

