import streamlit as st

# Set up the page
st.set_page_config(page_title="AI Floor Plan Generator", layout="centered")

st.title("🧠 AI Floor Plan Generator")
st.write("Describe your space and we'll generate a floor plan layout suggestion.")

# Prompt input
user_prompt = st.text_area("✍️ Describe your space:", 
                           placeholder="e.g. A medical office with 2 exam rooms, a waiting area, and a staff lounge")

if st.button("Generate Floor Plan"):
    if user_prompt.strip() == "":
        st.warning("Please enter a prompt.")
    else:
        st.info("Generating floor plan based on your prompt...")

        # Placeholder response
        # Later, connect this to OpenAI or a layout engine
        st.success("✅ Floor plan generated successfully!")
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Architectural_Floorplan_example.png/640px-Architectural_Floorplan_example.png", 
            caption="Sample floor plan (placeholder)", 
            use_container_width=True
        )

        # Show prompt as reference
        st.markdown("**Prompt:** " + user_prompt)
