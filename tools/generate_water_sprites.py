"""Generate water sprites using DALL-E API for the Drive minigame scenery."""

import os
import requests
import json
from pathlib import Path
import base64
from datetime import datetime

# Configuration
# API_KEY should be set as environment variable OPENAI_API_KEY
API_KEY = os.environ.get("OPENAI_API_KEY", "")
if not API_KEY:
    print("Please set OPENAI_API_KEY environment variable")
    exit(1)
OUTPUT_DIR = Path("../assets/images/scenery/water")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# DALL-E API endpoint
DALLE_API_URL = "https://api.openai.com/v1/images/generations"

# Headers for API request
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Water sprite configurations
water_sprites = [
    {
        "name": "lake_tiles",
        "prompt": "Simple pixel art water tiles for a top-down racing game, 32x32 pixels, bright blue water with subtle wave patterns, clean pixel art style similar to Kenney.nl assets, no text, seamless tileable pattern",
        "size": "256x256",
        "n": 1
    },
    {
        "name": "river_section",
        "prompt": "Pixel art river section viewed from above for a highway racing game background, 256x64 pixels, flowing water effect, simple clean pixel art style, blue water with white foam details, matches Kenney game assets style",
        "size": "256x256",
        "n": 1
    },
    {
        "name": "ocean_horizon",
        "prompt": "Pixel art ocean horizon for racing game background, distant water view, 512x128 pixels, gradient from light to dark blue, simple waves, clean pixel art style matching Kenney.nl aesthetic, suitable for parallax background",
        "size": "512x512",
        "n": 1
    },
    {
        "name": "pond_small",
        "prompt": "Small pixel art pond viewed from above, 64x64 pixels, round blue water body with simple ripples, clean edges, bright colors, matches Kenney.nl pixel art style for racing game scenery",
        "size": "256x256",
        "n": 1
    }
]

def generate_sprite(config):
    """Generate a single sprite using DALL-E."""
    print(f"\nGenerating {config['name']}...")
    
    # Prepare the API request
    data = {
        "model": "dall-e-2",
        "prompt": config['prompt'],
        "size": config['size'],
        "n": config['n'],
        "response_format": "b64_json"
    }
    
    try:
        # Make API request
        response = requests.post(DALLE_API_URL, headers=headers, json=data)
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        
        # Save each generated image
        for i, image_data in enumerate(result['data']):
            # Decode base64 image
            image_bytes = base64.b64decode(image_data['b64_json'])
            
            # Save to file
            filename = f"{config['name']}.png" if i == 0 else f"{config['name']}_{i+1}.png"
            filepath = OUTPUT_DIR / filename
            
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
            
            print(f"Saved: {filepath}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error generating {config['name']}: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")

def create_attribution_file():
    """Create attribution file for generated assets."""
    attribution = f"""# Water Sprite Attribution

Generated using DALL-E 2 API on {datetime.now().strftime('%Y-%m-%d')}

## Assets Generated:
- lake_tiles.png - Tileable water surface
- river_section.png - River for background scenery  
- ocean_horizon.png - Ocean horizon for distant background
- pond_small.png - Small pond decoration

## Usage:
These sprites were generated specifically for the Danger Rose game project.
Pixel art style matching Kenney.nl aesthetic.

## Integration Notes:
- lake_tiles.png can be tiled for large water surfaces
- river_section.png works well alongside roads
- ocean_horizon.png for far background parallax
- pond_small.png for scenic decoration
"""
    
    with open(OUTPUT_DIR / "WATER_SPRITES_INFO.md", 'w') as f:
        f.write(attribution)

def main():
    """Generate all water sprites."""
    print("Generating water sprites for Drive minigame...")
    print(f"Output directory: {OUTPUT_DIR.absolute()}")
    
    # Generate each sprite
    for sprite_config in water_sprites:
        generate_sprite(sprite_config)
    
    # Create attribution file
    create_attribution_file()
    
    print("\nWater sprite generation complete!")
    print(f"Check {OUTPUT_DIR} for generated sprites.")

if __name__ == "__main__":
    main()