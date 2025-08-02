#!/usr/bin/env python3
"""Create placeholder EV sprites for The Drive minigame."""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "images" / "vehicles"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def create_professional_ev(width=128, height=192):
    """Create a clean, professional-looking EV sprite."""
    # Create image with transparent background
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Car body (electric blue)
    body_color = (30, 144, 255)  # Dodger blue
    body_rect = [width//4, height//5, 3*width//4, 4*height//5]
    draw.rounded_rectangle(body_rect, radius=15, fill=body_color)
    
    # Windows (dark blue)
    window_color = (0, 0, 139)
    # Front window
    draw.rectangle([width//3, height//3, 2*width//3, height//2], fill=window_color)
    # Rear window
    draw.rectangle([width//3, 3*height//5, 2*width//3, 2*height//3], fill=window_color)
    
    # Wheels (black)
    wheel_color = (40, 40, 40)
    wheel_size = width//8
    # Front wheels
    draw.ellipse([width//5-wheel_size//2, height//4-wheel_size//2, 
                  width//5+wheel_size//2, height//4+wheel_size//2], fill=wheel_color)
    draw.ellipse([4*width//5-wheel_size//2, height//4-wheel_size//2,
                  4*width//5+wheel_size//2, height//4+wheel_size//2], fill=wheel_color)
    # Rear wheels
    draw.ellipse([width//5-wheel_size//2, 3*height//4-wheel_size//2,
                  width//5+wheel_size//2, 3*height//4+wheel_size//2], fill=wheel_color)
    draw.ellipse([4*width//5-wheel_size//2, 3*height//4-wheel_size//2,
                  4*width//5+wheel_size//2, 3*height//4+wheel_size//2], fill=wheel_color)
    
    # Electric highlights (cyan)
    highlight_color = (0, 255, 255)
    # Front lights
    draw.rectangle([width//3, height//5+5, 2*width//3, height//5+10], fill=highlight_color)
    # Rear lights
    draw.rectangle([width//3, 4*height//5-10, 2*width//3, 4*height//5-5], fill=highlight_color)
    
    # Side mirrors (small rectangles)
    mirror_color = (192, 192, 192)
    draw.rectangle([width//4-5, 2*height//5, width//4, 2*height//5+10], fill=mirror_color)
    draw.rectangle([3*width//4, 2*height//5, 3*width//4+5, 2*height//5+10], fill=mirror_color)
    
    return img

def create_kids_drawing_ev(width=128, height=192):
    """Create a child's crayon drawing style EV sprite."""
    # Create image with transparent background
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Car body (bright green, wonky rectangle)
    body_color = (0, 255, 0)
    # Draw with slightly uneven lines
    points = [
        (width//4-5, height//5+3),
        (3*width//4+3, height//5-2),
        (3*width//4+5, 4*height//5+2),
        (width//4-3, 4*height//5-3)
    ]
    draw.polygon(points, fill=body_color)
    
    # Scribbled windows (blue)
    window_color = (0, 100, 255)
    # Front window (messy rectangle)
    for i in range(5):
        draw.line([(width//3-2+i, height//3), (width//3-2+i, height//2)], 
                  fill=window_color, width=3)
        draw.line([(2*width//3-2+i, height//3), (2*width//3-2+i, height//2)], 
                  fill=window_color, width=3)
    
    # Oversized wheels (brown/black)
    wheel_color = (139, 69, 19)
    wheel_size = width//5
    # Wonky circles
    draw.ellipse([width//6-wheel_size//2, height//4-wheel_size//2+5,
                  width//6+wheel_size//2, height//4+wheel_size//2+5], 
                 fill=wheel_color, width=3)
    draw.ellipse([5*width//6-wheel_size//2, height//4-wheel_size//2-3,
                  5*width//6+wheel_size//2, height//4+wheel_size//2-3], 
                 fill=wheel_color, width=3)
    draw.ellipse([width//6-wheel_size//2, 3*height//4-wheel_size//2-2,
                  width//6+wheel_size//2, 3*height//4+wheel_size//2-2], 
                 fill=wheel_color, width=3)
    draw.ellipse([5*width//6-wheel_size//2, 3*height//4-wheel_size//2+4,
                  5*width//6+wheel_size//2, 3*height//4+wheel_size//2+4], 
                 fill=wheel_color, width=3)
    
    # Smiley face on front (yellow)
    smile_color = (255, 255, 0)
    # Eyes
    draw.ellipse([width//2-15, height//5+20, width//2-10, height//5+25], fill=(0,0,0))
    draw.ellipse([width//2+10, height//5+20, width//2+15, height//5+25], fill=(0,0,0))
    # Smile
    draw.arc([width//2-20, height//5+25, width//2+20, height//5+40], 
             start=0, end=180, fill=smile_color, width=3)
    
    # Lightning bolt (yellow)
    lightning_points = [
        (width//2-5, height//2),
        (width//2+5, height//2+10),
        (width//2, height//2+10),
        (width//2+10, height//2+25),
        (width//2-5, height//2+15),
        (width//2, height//2+15),
    ]
    draw.polygon(lightning_points, fill=smile_color)
    
    # Random stars/flowers
    star_color = (255, 0, 255)
    # Star 1
    draw.polygon([(width//4, 3*height//5), (width//4+5, 3*height//5+5),
                  (width//4, 3*height//5+10), (width//4-5, 3*height//5+5)], 
                 fill=star_color)
    # Star 2
    draw.polygon([(3*width//4, height//3), (3*width//4+5, height//3+5),
                  (3*width//4, height//3+10), (3*width//4-5, height//3+5)], 
                 fill=star_color)
    
    # Antenna with flag
    antenna_color = (128, 128, 128)
    draw.line([(width//2, height//5), (width//2, height//5-20)], fill=antenna_color, width=2)
    # Flag
    flag_color = (255, 0, 0)
    draw.polygon([(width//2, height//5-20), (width//2+15, height//5-15),
                  (width//2, height//5-10)], fill=flag_color)
    
    return img

def main():
    """Generate placeholder EV sprites."""
    print("Creating placeholder EV sprites...")
    
    # Create professional EV
    pro_img = create_professional_ev()
    pro_path = OUTPUT_DIR / "ev_professional.png"
    pro_img.save(pro_path)
    print(f"[OK] Created: {pro_path}")
    
    # Create kids drawing EV
    kids_img = create_kids_drawing_ev()
    kids_path = OUTPUT_DIR / "ev_kids_drawing.png"
    kids_img.save(kids_path)
    print(f"[OK] Created: {kids_path}")
    
    # Create variations with different colors
    # Professional variant - red
    pro_red = create_professional_ev()
    draw = ImageDraw.Draw(pro_red)
    # Redraw body in red
    body_rect = [128//4, 192//5, 3*128//4, 4*192//5]
    draw.rounded_rectangle(body_rect, radius=15, fill=(255, 0, 0))
    pro_red_path = OUTPUT_DIR / "ev_professional_red.png"
    pro_red.save(pro_red_path)
    print(f"[OK] Created: {pro_red_path}")
    
    print("\n✅ Placeholder sprites created!")
    print(f"Location: {OUTPUT_DIR}")
    print("\nThese are simple placeholder sprites.")
    print("You can replace them with DALL-E generated sprites when available.")

if __name__ == "__main__":
    main()