import requests
import json

def generate_image(prompt, size, api_key, host):
    url = f"{host}/images/generations"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": "doubao-seedream-3-0-t2i-250415",
        "prompt": prompt,
        "response_format": "url",
        "size": size,
        "guidance_scale": 3,
        "watermark": False
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=300)

        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Request Error: {str(e)}")
        return None