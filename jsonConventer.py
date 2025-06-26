import streamlit as st
import requests
import base64
import fitz  # PyMuPDF
import easyocr
from PIL import Image
import io

# OCR reader (global to avoid reloading)
reader = easyocr.Reader(['en'])

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

def extract_images_from_pdf(pdf_file):
    images = []
    pdf_bytes = pdf_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    for page in doc:
        image_list = page.get_images(full=True)
        for img in image_list:
            xref = img[0]
            base_image = doc.extract_image(xref)
            img_bytes = base_image["image"]
            images.append(img_bytes)
    return images

def run_easyocr(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    result = reader.readtext(image)
    text = "\n".join([line[1] for line in result])
    return text

# ------------------ Streamlit UI ------------------

st.set_page_config(
    page_title="MiniCPM-V Invoice Extractor",
    page_icon="🧾",
    layout="centered"
)

st.title("🧾 Invoice Extractor: EasyOCR + MiniCPM-V")
st.write("Upload an invoice image or PDF. We’ll extract text using EasyOCR and analyze it using MiniCPM-V.")

uploaded_file = st.file_uploader("📤 Upload File (Image or PDF)", type=["jpg", "jpeg", "png", "pdf"])
prompt = st.text_area("✏️ Prompt for MiniCPM", "Extract data in JSON format from this uploaded invoice")
submit = st.button("🚀 Process")

if uploaded_file and prompt and submit:
    with st.spinner("🧠 Processing..."):
        if uploaded_file.type == "application/pdf":
            images = extract_images_from_pdf(uploaded_file)
        else:
            images = [uploaded_file.read()]

        for idx, img_bytes in enumerate(images):
            # OCR
            ocr_text = run_easyocr(img_bytes)
            # Model
            response = run_minicpm(img_bytes, prompt)

            st.markdown(f"### 🖼️ Image {idx + 1}")
            st.image(img_bytes, use_column_width=True)

            st.subheader("🧾 OCR Extracted Text")
            st.text_area("EasyOCR Output", ocr_text, height=150)

            st.subheader("🤖 MiniCPM-V Output")
            st.code(response, language="json")

            # Save to file
            with open("output.txt", "a") as f:
                f.write(f"\nImage {idx + 1}:\nOCR:\n{ocr_text}\nMiniCPM:\n{response}\n")

        st.success("✅ All results saved to output.txt")
