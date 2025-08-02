#!/usr/bin/env python3
"""Generate EV car sprites using DALL-E API."""

import os
import base64
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
API_URL = "https://api.openai.com/v1/images/generations"

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "images" / "vehicles"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Sprite configurations
SPRITES = [
    {
        "name": "ev_car_professional",
        "prompt": """Create a pixel art sprite of a modern electric vehicle in top-down view, 128x192 pixels. Style: 8-bit retro gaming aesthetic with clean lines and vibrant colors. The car should be a sleek, aerodynamic EV with rounded edges, reminiscent of a Tesla Model 3 or similar. Color palette: bright electric blue body with silver/white accents, black windows, and glowing cyan highlights on the front and rear to indicate electric power. Include subtle details: door lines, side mirrors, charging port indicator, and LED headlight strips. The sprite should have a slight 3D perspective (isometric-style) for racing game use. Background: transparent. Art style: smooth pixel art with anti-aliasing, family-friendly cartoon aesthetic, reminiscent of 16-bit racing games like OutRun. Ensure the design is clear and recognizable at 64x96 display size.""",
        "variations": 3
    },
    {
        "name": "ev_car_kids_drawing",
        "prompt": """Create a pixel art sprite that looks like a child's crayon drawing of an electric car, top-down view, 128x192 pixels. Style: deliberately imperfect and charming, with slightly wobbly lines and uneven coloring as if drawn by a 6-year-old. The car should be a simple, boxy electric vehicle with exaggerated features: oversized wheels in brown/black, a bright green body with crayon-texture effects, windows colored in with blue scribbles going outside the lines. Add childlike details: a smiley face on the front "grille," lightning bolt stickers drawn in yellow, flowers or stars doodled on the sides, and maybe a small antenna with a flag. Use a limited crayon color palette: primary colors (red, blue, yellow, green) with visible "coloring outside the lines" effects. The sprite should maintain the top-down racing perspective but with that endearing hand-drawn quality. Background: transparent. Overall feel: wholesome, funny, and heartwarming - like a drawing a kid would proudly show their parents.""",
        "variations": 3
    }
]

def generate_sprite(prompt, size="256x256", n=1):
    """Generate sprite using DALL-E API."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,  # DALL-E 3 only supports n=1
        "size": "1024x1024",  # DALL-E 3 only supports 1024x1024, 1024x1792, or 1792x1024
        "quality": "standard",
        "response_format": "url"
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=60)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(response.json())
            return None
            
    except Exception as e:
        print(f"Request error: {e}")
        return None

def download_image(url, filepath):
    """Download image from URL."""
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"Download error: {e}")
    return False

def main():
    """Generate all EV sprites."""
    print("=== EV Sprite Generator ===")
    print(f"Output directory: {OUTPUT_DIR}")
    print()
    
    results = []
    
    for sprite_config in SPRITES:
        print(f"\nGenerating: {sprite_config['name']}")
        print(f"Variations: {sprite_config['variations']}")
        
        for i in range(sprite_config['variations']):
            print(f"\n  Variation {i+1}/{sprite_config['variations']}...")
            
            # Generate sprite
            result = generate_sprite(sprite_config['prompt'])
            
            if result and result.get('data'):
                image_data = result['data'][0]
                image_url = image_data.get('url')
                
                if image_url:
                    # Download image
                    filename = f"{sprite_config['name']}_v{i+1}.png"
                    filepath = OUTPUT_DIR / filename
                    
                    if download_image(image_url, filepath):
                        print(f"  [OK] Saved: {filename}")
                        results.append({
                            "name": sprite_config['name'],
                            "variation": i+1,
                            "file": filename,
                            "path": str(filepath),
                            "revised_prompt": image_data.get('revised_prompt', '')
                        })
                    else:
                        print(f"  [ERROR] Failed to download")
                else:
                    print(f"  [ERROR] No image URL in response")
            else:
                print(f"  [ERROR] Generation failed")
    
    # Save generation log
    log_file = OUTPUT_DIR / "generation_log.json"
    with open(log_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results
        }, f, indent=2)
    
    print("\n" + "="*50)
    print("GENERATION SUMMARY")
    print("="*50)
    print(f"Total sprites generated: {len(results)}")
    for result in results:
        print(f"  - {result['file']}")
    
    print(f"\nLog saved: {log_file}")
    print("\n[OK] Sprite generation complete!")
    
    # Post-processing reminder
    print("\n⚠️ POST-PROCESSING NEEDED:")
    print("1. Resize images to 128x192 pixels")
    print("2. Convert to pixel art style if needed")
    print("3. Ensure transparent backgrounds")
    print("4. Optimize for game performance")

if __name__ == "__main__":
    main()