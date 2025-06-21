import requests
import base64

# Step 1: Load and encode the image
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded

# Step 2: Send the image to the model
def run_ollama_with_image(image_path):
    url = "http://localhost:11434/api/generate"
    base64_image = encode_image_to_base64(image_path)

    payload = {
        "model": "jyan1/paligemma-mix-224",
        "prompt": "",  # You can give a prompt here, like "What's in this image?"
        "images": [base64_image],
        "stream": False
    }

    response = requests.post(url, json=payload)

    if response.ok:
        print("Response:")
        print(response.json()['response'])
    else:
        print("Error:", response.status_code, response.text)

# Example usage
run_ollama_with_image("example.jpg")
