import requests
from django.conf import settings
import base64
from huggingface_hub import InferenceClient

SUMMARIZE_API_URL = (
    "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"
)

def summarize_text(text: str):
    headers = {
        "Authorization": f"Bearer {settings.HUGGINGFACE_API_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "inputs": text,
        "parameters": {
            "max_length": 130,
            "do_sample": False,
        }
    }

    response = requests.post(
        SUMMARIZE_API_URL,
        headers=headers,
        json=payload,
        timeout=60
    )

    response.raise_for_status()
    return response.json()



HF_API_URL = "https://router.huggingface.co/hf-inference/models/"

def generate_image(prompt: str) -> str:
    url = HF_API_URL + "stabilityai/stable-diffusion-xl-base-1.0"

    headers = {
        "Authorization": f"Bearer {settings.HUGGINGFACE_API_TOKEN}"
    }

    payload = {
        "inputs": prompt
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=60
    )

    response.raise_for_status()
    image_base64 = base64.b64encode(response.content).decode("utf-8")
    return image_base64

client = InferenceClient(
    provider="hf-inference",
    api_key=settings.HUGGINGFACE_API_TOKEN,
)

def translate_text(text: str):
    result = client.translation(
        text,
        model="Helsinki-NLP/opus-mt-ko-en"
    )
    return result["translation_text"]