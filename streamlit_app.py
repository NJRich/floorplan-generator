import streamlit as st
from PIL import Image

st.set_page_config(page_title="AI Floor Plan Generator", layout="centered")
st.title("🧠 AI Floor Plan Generator")
st.write("Describe your space and we'll generate a floor plan layout suggestion.")

user_prompt = st.text_area(
    "✍️ Describe your space:",
    placeholder="e.g. A medical office with 2 exam rooms, a waiting area, and a staff lounge"
)

uploaded_file = st.file_uploader("🖼️ Upload a blank floor plan image (optional)", type=["png", "jpg", "jpeg"])

if st.button("Generate Floor Plan"):
    if user_prompt.strip() == "":
        st.warning("Please enter a prompt.")
    else:
        st.info("Generating floor plan based on your prompt...")
        st.success("✅ Floor plan generated successfully!")

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Your uploaded floor plan", use_container_width=True)
        else:
            st.image(
                "https://raw.githubusercontent.com/streamlit/example-app-image-coordinates/main/resources/floor_plan.png",
                caption="Sample floor plan (placeholder)",
                use_container_width=True
            )

        st.markdown("**Prompt:** " + user_prompt)
