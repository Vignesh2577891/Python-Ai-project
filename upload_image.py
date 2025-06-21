import requests
import base64

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def run_minicpm(image_path, prompt):
    url = "http://localhost:11434/api/generate"
    base64_image = encode_image_to_base64(image_path)

    payload = {
        "model": "minicpm-v",
        "prompt": prompt,
        "images": [base64_image],
        "stream": False
    }

    response = requests.post(url, json=payload)
    
    if response.ok:
        print("Response from model:")
        print(response.json()['response'])
    else:
        print("Error:", response.status_code, response.text)

# ✅ Example usage
run_minicpm("invoice1.jpg", "extract data in json format from this uploaded invoice")
