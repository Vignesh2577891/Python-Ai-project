# streamlit_app.py

import streamlit as st
import requests
import base64
import fitz  # PyMuPDF
from PIL import Image
import io
import easyocr

# ------------------ Helper Functions ------------------

def extract_images_from_pdf(uploaded_file):
    images = []
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as pdf:
        for page_index in range(len(pdf)):
            page = pdf[page_index]
            pix = page.get_pixmap(dpi=300)
            img_bytes = pix.tobytes("png")
            images.append(img_bytes)
    return images

def extract_text_with_easyocr(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    reader = easyocr.Reader(['en'], gpu=False)
    result = reader.readtext(np.array(image))
    return " ".join([text for _, text, _ in result])

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
        return f"\u274c Error: {response.status_code} - {response.text}"

# ------------------ Streamlit UI ------------------

st.set_page_config(
    page_title="MiniCPM-V Invoice Extractor",
    page_icon="\U0001f9fe",
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
    st.title("\U0001f9fe MiniCPM-V Invoice Extractor")
    st.write("Upload an invoice or document image, and enter a prompt to extract data using the MiniCPM-V model.")

    uploaded_file = st.file_uploader("\U0001f4e4 Upload File", type=["jpg", "jpeg", "png", "pdf"])

    prompt = st.text_area("\u270d\ufe0f Enter your prompt", "Extract data in JSON format from this uploaded invoice")

    submit = st.button("\U0001f680 Run Model")

    if uploaded_file and prompt and submit:
        with st.spinner("\U0001f9e0 Analyzing image... please wait..."):
            image_bytes_list = []
            if uploaded_file.type == "application/pdf":
                image_bytes_list = extract_images_from_pdf(uploaded_file)
            else:
                image_bytes_list = [uploaded_file.read()]

            for idx, image_bytes in enumerate(image_bytes_list):
                extracted_text = extract_text_with_easyocr(image_bytes)
                combined_prompt = f"{prompt}\n\nExtracted OCR text:\n{extracted_text}"
                response = run_minicpm(image_bytes, combined_prompt)

                # Display the image on left and result on right
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(image_bytes, caption=f"\U0001f4f7 Page {idx+1}", use_column_width=True)
                with col2:
                    st.subheader("\U0001f4e4 Extracted Output")
                    st.code(response, language='json')

                # Save to file
                with open("output.txt", "a") as f:
                    f.write(f"Page {idx+1}:\n{response}\n\n")

            st.success("\u2705 Output saved to `output.txt`.")
