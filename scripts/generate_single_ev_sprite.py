#!/usr/bin/env python3
"""Generate a single EV car sprite using DALL-E API."""

import os
import requests
import json
from pathlib import Path
from datetime import datetime

# API Configuration
# IMPORTANT: Set your OpenAI API key as an environment variable:
# export OPENAI_API_KEY='your-api-key-here'
API_KEY = os.getenv('OPENAI_API_KEY')
if not API_KEY:
    raise ValueError("Please set OPENAI_API_KEY environment variable")

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "images" / "vehicles"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Professional EV prompt
PROMPT = """Create a pixel art sprite of a modern electric vehicle in top-down view. Style: 8-bit retro gaming aesthetic with clean lines and vibrant colors. The car should be a sleek, aerodynamic EV with rounded edges. Color palette: bright electric blue body with silver/white accents, black windows, and glowing cyan highlights on the front and rear to indicate electric power. Include subtle details: door lines, side mirrors, charging port indicator, and LED headlight strips. The sprite should have a slight 3D perspective for racing game use. Background: solid white. Art style: smooth pixel art with anti-aliasing, family-friendly cartoon aesthetic, reminiscent of 16-bit racing games. Make it look fun and appealing for kids."""

def generate_sprite():
    """Generate sprite using DALL-E API."""
    print("Generating EV sprite...")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "dall-e-3",
        "prompt": PROMPT,
        "n": 1,
        "size": "1024x1024",
        "quality": "standard",
        "response_format": "url"
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers=headers,
            json=data,
            timeout=60
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('data'):
                image_url = result['data'][0]['url']
                print(f"Image URL: {image_url}")
                
                # Download image
                img_response = requests.get(image_url, timeout=30)
                if img_response.status_code == 200:
                    filename = "ev_car_professional.png"
                    filepath = OUTPUT_DIR / filename
                    
                    with open(filepath, 'wb') as f:
                        f.write(img_response.content)
                    
                    print(f"[OK] Saved: {filepath}")
                    return True
                else:
                    print(f"[ERROR] Failed to download image")
        else:
            print(f"[ERROR] API error: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] {e}")
        
    return False

if __name__ == "__main__":
    print("=== Single EV Sprite Generator ===")
    print(f"Output: {OUTPUT_DIR}")
    
    if generate_sprite():
        print("\n[OK] Sprite generated successfully!")
        print("\nNext steps:")
        print("1. Check the generated image in assets/images/vehicles/")
        print("2. Resize to 128x192 pixels if needed")
        print("3. Convert to pixel art style if necessary")
    else:
        print("\n[ERROR] Failed to generate sprite")