#!/usr/bin/env python3
"""Simple EV sprite generator."""

import requests
import json
from pathlib import Path

# API Configuration
# IMPORTANT: Set your OpenAI API key as an environment variable:
# export OPENAI_API_KEY='your-api-key-here'
import os
API_KEY = os.getenv('OPENAI_API_KEY')
if not API_KEY:
    raise ValueError("Please set OPENAI_API_KEY environment variable")

# Output directory
OUTPUT_DIR = Path("assets/images/vehicles")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("Generating EV sprite...")

# Simple prompt
prompt = "pixel art electric car, top-down view, blue color, 8-bit style, white background, family-friendly cartoon"

# API request
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "dall-e-2",  # Using DALL-E 2 for faster generation
    "prompt": prompt,
    "n": 1,
    "size": "256x256"
}

try:
    # Generate image
    response = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers=headers,
        json=data,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        image_url = result['data'][0]['url']
        print(f"Generated! URL: {image_url[:50]}...")
        
        # Download
        img_resp = requests.get(image_url, timeout=10)
        if img_resp.status_code == 200:
            with open(OUTPUT_DIR / "ev_test.png", 'wb') as f:
                f.write(img_resp.content)
            print(f"Saved to: {OUTPUT_DIR / 'ev_test.png'}")
        else:
            print("Download failed")
    else:
        print(f"Generation failed: {response.status_code}")
        print(response.text[:200])
        
except Exception as e:
    print(f"Error: {e}")