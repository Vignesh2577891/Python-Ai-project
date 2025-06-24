# streamlit_app.py

import streamlit as st
import requests
import base64

# ------------------ Helper Functions ------------------

def encode_image_to_base64(image_bytes):
    return base64.b64encode(image_bytes).decode("utf-8")

def run_minicpm(image_bytes, prompt):
    url = "http://localhost:11434/api/generate"
    base64_image = encode_image_to_base64(image_bytes)

    payload = {
        "model": "minicpm-v",
        "prompt": prompt,
        "images": [base64_image],
        "stream": False
    }

    response = requests.post(url, json=payload)

    if response.ok:
        return response.json()['response']
    else:
        return f"❌ Error: {response.status_code} - {response.text}"

# ------------------ Streamlit UI ------------------

st.set_page_config(
    page_title="MiniCPM-V Invoice Extractor",
    page_icon="🧾",
    layout="centered"
)

st.markdown(
    """
    <style>
    .main {
        background-color: #f5f5f5;
        padding: 2rem;
        border-radius: 10px;
        max-width: 700px;
        margin: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

with st.container():
    st.title("🧾 MiniCPM-V Invoice Extractor")
    st.write("Upload an invoice or document image, and enter a prompt to extract data using the MiniCPM-V model.")

    uploaded_file = st.file_uploader("📤 Upload Image", type=["jpg", "jpeg", "png"])

    prompt = st.text_area("✏️ Enter your prompt", "Extract data in JSON format from this uploaded invoice")

    submit = st.button("🚀 Run Model")

    if uploaded_file and prompt and submit:
        with st.spinner("🧠 Analyzing image... please wait..."):
            image_bytes = uploaded_file.read()
            response = run_minicpm(image_bytes, prompt)

            # Display the image on left and result on right
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(uploaded_file, caption="📷 Uploaded Image", use_column_width=True)
            with col2:
                st.subheader("📤 Extracted Output")
                st.code(response, language='json')

            # Save to file
            with open("output.txt", "a") as f:
                f.write(response + "\n")

            st.success("✅ Output saved to `output.txt`.")
