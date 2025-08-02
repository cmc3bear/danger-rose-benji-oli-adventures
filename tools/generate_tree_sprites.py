"""Generate tree sprites using DALL-E API for the Drive minigame scenery."""

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
OUTPUT_DIR = Path("../assets/images/scenery/trees")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# DALL-E API endpoint
DALLE_API_URL = "https://api.openai.com/v1/images/generations"

# Headers for API request
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Tree sprite configurations
tree_sprites = [
    {
        "name": "pine_tree_single",
        "prompt": "Single pine tree sprite for top-down racing game, 32x48 pixels, simple pixel art style like Kenney.nl assets, dark green pine tree with brown trunk, clean edges, no shadow, transparent background",
        "size": "256x256",
        "n": 1
    },
    {
        "name": "pine_forest_group",
        "prompt": "Group of 3-4 pine trees for racing game background, pixel art style, 128x96 pixels, varying heights, dark green color, simple clean design matching Kenney game assets, viewed from above angle",
        "size": "256x256",
        "n": 1
    },
    {
        "name": "deciduous_tree",
        "prompt": "Round leafy tree sprite for top-down game, 32x32 pixels, bright green foliage, brown trunk, simple pixel art style similar to Kenney.nl, clean design, no text, transparent background",
        "size": "256x256",
        "n": 1
    },
    {
        "name": "tree_line_background",
        "prompt": "Pixel art tree line for racing game distant background, 512x64 pixels, silhouette of various trees, dark green gradient, simple clean style for parallax scrolling, matches Kenney aesthetic",
        "size": "512x512",
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
    attribution = f"""# Tree Sprite Attribution

Generated using DALL-E 2 API on {datetime.now().strftime('%Y-%m-%d')}

## Assets Generated:
- pine_tree_single.png - Individual pine tree
- pine_forest_group.png - Group of pine trees
- deciduous_tree.png - Round leafy tree
- tree_line_background.png - Tree line for distant background

## Usage:
These sprites were generated specifically for the Danger Rose game project.
Pixel art style matching Kenney.nl aesthetic.

## Integration Notes:
- pine_tree_single.png for individual tree placement
- pine_forest_group.png for dense forest areas
- deciduous_tree.png for variety in forest sections
- tree_line_background.png for far parallax layer
"""
    
    with open(OUTPUT_DIR / "TREE_SPRITES_INFO.md", 'w') as f:
        f.write(attribution)

def main():
    """Generate all tree sprites."""
    print("Generating tree sprites for Drive minigame...")
    print(f"Output directory: {OUTPUT_DIR.absolute()}")
    
    # Generate each sprite
    for sprite_config in tree_sprites:
        generate_sprite(sprite_config)
    
    # Create attribution file
    create_attribution_file()
    
    print("\nTree sprite generation complete!")
    print(f"Check {OUTPUT_DIR} for generated sprites.")

if __name__ == "__main__":
    main()