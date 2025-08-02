"""Create placeholder sprites for new characters."""

import os
from PIL import Image, ImageDraw, ImageFont

CHARACTER_COLORS = {
    "benji": {"bg": (100, 149, 237), "accent": (30, 144, 255)},  # Blue theme
    "olive": {"bg": (60, 179, 113), "accent": (34, 139, 34)},    # Green theme  
    "uncle_bear": {"bg": (178, 34, 34), "accent": (139, 69, 19)} # Red/brown theme
}

ANIMATIONS = ["idle", "walk", "walk_extra", "jump", "victory", "hurt", "action"]
SCENES = ["hub", "pool", "ski", "vegas", "drive"]

def create_placeholder_sprite(character_name: str, animation: str, frame_num: int, size=(128, 128)):
    """Create a placeholder sprite with character initial and animation info."""
    
    colors = CHARACTER_COLORS.get(character_name, {"bg": (128, 128, 128), "accent": (64, 64, 64)})
    
    # Create image with transparent background
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw character circle
    margin = 10
    draw.ellipse([margin, margin, size[0]-margin, size[1]-margin], 
                 fill=colors["bg"], outline=colors["accent"], width=3)
    
    # Draw character initial
    try:
        font = ImageFont.truetype("arial.ttf", size[0]//3)
    except:
        font = None
    
    initial = character_name[0].upper()
    if initial == 'U':  # Uncle Bear
        initial = 'B'
    
    if font:
        bbox = draw.textbbox((0, 0), initial, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    else:
        text_width = size[0] // 4
        text_height = size[1] // 3
    
    text_x = (size[0] - text_width) // 2
    text_y = (size[1] - text_height) // 2 - 10
    
    draw.text((text_x, text_y), initial, fill="white", font=font)
    
    # Draw animation indicator
    anim_text = f"{animation[:3]}-{frame_num}"
    try:
        small_font = ImageFont.truetype("arial.ttf", size[0]//8)
    except:
        small_font = None
        
    draw.text((size[0]//2 - 20, size[1] - 25), anim_text, 
              fill="white", font=small_font, anchor="mm")
    
    return img


def generate_animation_frames(character_name: str):
    """Generate all animation frames for a character."""
    
    frame_counts = {
        "idle": 4,
        "walk": 5, 
        "walk_extra": 9,
        "jump": 3,
        "victory": 4,
        "hurt": 2,
        "action": 6
    }
    
    for scene in SCENES:
        # Create directory
        scene_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets", "images", "characters", "new_sprites", character_name, scene
        )
        os.makedirs(scene_dir, exist_ok=True)
        
        # Generate sprites for each animation
        for animation, frame_count in frame_counts.items():
            for frame in range(1, frame_count + 1):
                sprite = create_placeholder_sprite(character_name, animation, frame)
                
                filename = f"{animation}_{frame:02d}.png"
                filepath = os.path.join(scene_dir, filename)
                sprite.save(filepath)
                
                print(f"Created: {filepath}")
        
        # Create metadata file
        import json
        metadata = {
            "character": character_name,
            "art_style": "placeholder",
            "animations": {
                "idle": {"frames": 4, "frame_rate": 8, "loop": True},
                "walk": {"frames": 5, "frame_rate": 12, "loop": True},
                "walk_extra": {"frames": 9, "frame_rate": 12, "loop": True},
                "action": {"frames": 6, "frame_rate": 10, "loop": False},
                "jump": {"frames": 3, "frame_rate": 6, "loop": False},
                "victory": {"frames": 4, "frame_rate": 8, "loop": False},
                "hurt": {"frames": 2, "frame_rate": 4, "loop": False}
            },
            "source": "placeholder",
            "license": "placeholder"
        }
        
        metadata_path = os.path.join(scene_dir, "animation_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Created metadata: {metadata_path}")


def main():
    """Generate placeholder sprites for all new characters."""
    
    print("Creating placeholder sprites for new characters...")
    print("=" * 50)
    
    characters = ["benji", "olive", "uncle_bear"]
    
    for character in characters:
        print(f"\nGenerating sprites for {character}...")
        generate_animation_frames(character)
    
    print("\nPlaceholder generation complete!")
    print("These can be replaced with actual sprites later.")


if __name__ == "__main__":
    main()