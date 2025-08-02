"""Generate character sprites using DALL-E 3 API."""

import os
import sys
import json
import requests
from typing import Dict, List
from openai import OpenAI

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.vault_utils import get_api_key


CHARACTER_SPECS = {
    "benji": {
        "description": "A cheerful 8-10 year old boy with blonde hair, wearing a bright blue hoodie and sneakers. He carries a small tablet device. Simple cartoon style similar to Kenney.nl assets, flat colors, minimal shading.",
        "personality": "Energetic, tech-savvy, curious",
        "special_power": "Tech Boost",
        "age": "8-10",
        "visual_notes": "Modern tech elements, youthful energy, bright colors"
    },
    "olive": {
        "description": "A creative 7-9 year old girl with curly brown hair, wearing green overalls with paint stains on her hands. She has a flower crown. Simple cartoon style similar to Kenney.nl assets, flat colors, minimal shading.",
        "personality": "Creative, artistic, nature-loving", 
        "special_power": "Nature's Blessing",
        "age": "7-9",
        "visual_notes": "Natural/organic elements, artistic flair, earth tones"
    },
    "uncle_bear": {
        "description": "A large, friendly 35-40 year old man with a warm smile, wearing a red flannel shirt, suspenders, and a chef's hat. Big build but gentle demeanor. Simple cartoon style similar to Kenney.nl assets, flat colors, minimal shading.",
        "personality": "Gentle giant, protective, loves cooking",
        "special_power": "Bear Strength",
        "age": "35-40",
        "visual_notes": "Larger build than other characters, warm/cozy elements, friendly face"
    }
}

ANIMATION_TYPES = {
    "idle": "standing in a relaxed pose, facing forward",
    "walk": "mid-stride walking pose, one leg forward",
    "jump": "jumping up with arms raised, feet off ground",
    "victory": "celebrating with arms up in triumph",
    "hurt": "recoiling or wincing from impact",
    "action": "performing their special ability action"
}

SCENE_VARIATIONS = {
    "hub": "casual home clothes",
    "pool": "swimming attire or summer clothes", 
    "ski": "winter gear with ski goggles",
    "vegas": "adventure gear or action outfit",
    "drive": "sitting in car seat with seatbelt"
}


def generate_character_sprite(character_name: str, animation: str, scene: str, client: OpenAI) -> str:
    """Generate a single character sprite using DALL-E 3."""
    
    char_spec = CHARACTER_SPECS[character_name]
    anim_desc = ANIMATION_TYPES[animation]
    scene_desc = SCENE_VARIATIONS[scene]
    
    # Build the prompt
    prompt = f"""Create a 2D sprite of {char_spec['description']}
    
Character is {anim_desc}.
Wearing {scene_desc}.
    
Style requirements:
- Top-down/3/4 view perspective suitable for 2D games
- Simple, flat cartoon style like Kenney.nl game assets
- Bright, saturated colors with minimal shading
- Clear silhouette on transparent background
- Character should fill most of the frame
- No complex details, keep it simple and readable
- Family-friendly design

The character should be centered and facing slightly toward the camera."""

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        image_url = response.data[0].url
        
        # Download the image
        img_response = requests.get(image_url)
        if img_response.status_code == 200:
            return img_response.content
        else:
            print(f"Failed to download image: {img_response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error generating sprite for {character_name} - {animation} - {scene}: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


def save_sprite(character_name: str, animation: str, scene: str, frame_num: int, image_data: bytes):
    """Save sprite to appropriate directory."""
    
    # Create directory structure
    base_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "assets", "images", "characters", "new_sprites", character_name, scene
    )
    os.makedirs(base_dir, exist_ok=True)
    
    # Save the image
    filename = f"{animation}_{frame_num:02d}.png"
    filepath = os.path.join(base_dir, filename)
    
    with open(filepath, 'wb') as f:
        f.write(image_data)
    
    print(f"Saved: {filepath}")
    return filepath


def create_animation_metadata(character_name: str, scene: str):
    """Create animation metadata JSON file."""
    
    metadata = {
        "character": character_name,
        "art_style": "kenney_cartoon", 
        "special_ability": CHARACTER_SPECS[character_name]["special_power"].lower().replace(" ", "_"),
        "animations": {
            "idle": {"frames": 4, "frame_rate": 8, "loop": True},
            "walk": {"frames": 5, "frame_rate": 12, "loop": True},
            "walk_extra": {"frames": 9, "frame_rate": 12, "loop": True},
            "action": {"frames": 6, "frame_rate": 10, "loop": False},
            "jump": {"frames": 3, "frame_rate": 6, "loop": False},
            "victory": {"frames": 4, "frame_rate": 8, "loop": False},
            "hurt": {"frames": 2, "frame_rate": 4, "loop": False}
        },
        "source": "dall_e_generated",
        "license": "custom",
        "extracted_date": "2025-08-02"
    }
    
    # Save metadata
    base_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "assets", "images", "characters", "new_sprites", character_name, scene
    )
    os.makedirs(base_dir, exist_ok=True)
    
    metadata_path = os.path.join(base_dir, "animation_metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Created metadata: {metadata_path}")


def generate_character_set(character_name: str, scenes: List[str] = None):
    """Generate a complete set of sprites for a character."""
    
    if scenes is None:
        scenes = ["hub", "pool", "ski", "vegas"]
    
    # Initialize OpenAI client
    api_key = get_api_key("OPENAI")
    client = OpenAI(api_key=api_key)
    
    print(f"\n=== Generating sprites for {character_name.upper()} ===")
    
    for scene in scenes:
        print(f"\n--- Scene: {scene} ---")
        
        # For initial generation, create just the first frame of key animations
        key_animations = ["idle", "walk", "action", "victory"]
        
        for animation in key_animations:
            print(f"Generating {animation} sprite...")
            
            image_data = generate_character_sprite(character_name, animation, scene, client)
            if image_data:
                save_sprite(character_name, animation, scene, 1, image_data)
            else:
                print(f"Failed to generate {animation} sprite")
        
        # Create metadata for this scene
        create_animation_metadata(character_name, scene)
    
    print(f"\n=== Completed initial sprite generation for {character_name} ===")
    print("Note: Only first frames generated. Use image editor to create additional frames.")


def main():
    """Main function to generate sprites for all new characters."""
    
    print("Danger Rose Character Sprite Generator")
    print("=====================================")
    
    # Check for API key
    try:
        api_key = get_api_key("OPENAI")
        print("[OK] OpenAI API key found")
    except ValueError as e:
        print(f"[ERROR] {e}")
        print("\nPlease ensure your OpenAI API key is available:")
        print("1. Set OPENAI_API_KEY environment variable, or")
        print("2. Place key in C:\\dev\\api-key-forge\\vault\\OPENAI\\api_key.txt")
        return
    
    # Generate sprites for each new character
    characters = ["benji", "olive", "uncle_bear"]
    
    for character in characters:
        generate_character_set(character)
        print("\n" + "="*50 + "\n")
    
    print("\nSprite generation complete!")
    print("\nNext steps:")
    print("1. Review generated sprites in assets/images/characters/new_sprites/")
    print("2. Use image editor to create animation frames from base sprites")
    print("3. Test animations in game using 'make run'")


if __name__ == "__main__":
    main()