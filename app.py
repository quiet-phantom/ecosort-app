import streamlit as st
from PIL import Image
from google import genai
import time

st.set_page_config(page_title="EcoSort - Smart Waste Classifier", page_icon="♻️")

st.title("♻️ EcoSort: Smart Waste Classification Assistant")
st.write("Upload an image of any waste item to instantly classify it and get eco-friendly disposal instructions!")

# Sidebar for API Key
st.sidebar.title("🔐 Configuration")
api_key_input = st.sidebar.text_input("Enter Gemini API Key:", type="password")

client = None
if api_key_input:
    try:
        client = genai.Client(api_key=api_key_input)
    except Exception as e:
        st.sidebar.error(f"Invalid API Key: {e}")

uploaded_file = st.file_uploader("Upload waste image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Waste Item", use_column_width=True)
    
    if st.button("Classify Waste"):
        if client is None:
            st.warning("Please enter your Gemini API key in the sidebar to proceed.")
        else:
            with st.spinner("Analyzing waste item with Gemini Vision (handling server traffic)..."):
                prompt = """
                Analyze this image of a waste item. Provide the following details clearly using headings:
                1. **Item Name:** What is the item in the image?
                2. **Category:** Strictly classify into one of these: [Recyclable, Organic/Compostable, Hazardous, E-Waste, Landfill]
                3. **Proper Disposal Instructions:** Step-by-step guide on how to dispose of or recycle this item correctly.
                4. **Environmental Impact / Tip:** A short eco-friendly tip regarding this material.
                """
                
                # Automatic Retry Logic for 503 Overload Errors
                max_retries = 3
                success = False
                response = None
                
                for attempt in range(max_retries):
                    try:
                        response = client.models.generate_content(
                            model="gemini-3.8-flash",
                            contents=[image, prompt]
                        )
                        success = True
                        break
                    except Exception as e:
                        if "503" in str(e) and attempt < max_retries - 1:
                            time.sleep(3) # 3 seconds wait karke dobara try karega
                            continue
                        else:
                            error_msg = str(e)
                
                if success and response:
                    st.subheader("📋 Classification & Disposal Guide")
                    st.markdown(response.text)
                    
                    st.download_button(
                        label="Download Disposal Report",
                        data=response.text,
                        file_name="Waste_Disposal_Report.txt",
                        mime="text/plain"
                    )
                else:
                    st.error(f"Server is busy (503 High Demand). Please wait a moment and click 'Classify Waste' again! Error details: {error_msg if 'error_msg' in locals() else 'Unknown'}")
