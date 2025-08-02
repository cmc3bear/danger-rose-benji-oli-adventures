"""Create placeholder EV vehicle sprites."""

import pygame
import os

# Initialize Pygame
pygame.init()

# Create output directory if it doesn't exist
output_dir = "assets/images/vehicles"
os.makedirs(output_dir, exist_ok=True)

# Vehicle dimensions
width, height = 128, 192

# Create professional EV
professional = pygame.Surface((width, height), pygame.SRCALPHA)
# Body - sleek silver
pygame.draw.rect(professional, (192, 192, 200), (10, 40, width-20, height-80), border_radius=20)
# Windows - dark blue tint
pygame.draw.rect(professional, (20, 30, 60), (15, 50, width-30, 40), border_radius=10)
pygame.draw.rect(professional, (20, 30, 60), (15, 100, width-30, 30), border_radius=5)
# Wheels
pygame.draw.circle(professional, (40, 40, 40), (30, height-30), 15)
pygame.draw.circle(professional, (40, 40, 40), (width-30, height-30), 15)
pygame.draw.circle(professional, (40, 40, 40), (30, 30), 15)
pygame.draw.circle(professional, (40, 40, 40), (width-30, 30), 15)
# Headlights
pygame.draw.ellipse(professional, (255, 255, 200), (15, 15, 20, 10))
pygame.draw.ellipse(professional, (255, 255, 200), (width-35, 15, 20, 10))

# Create kids drawing EV
kids_drawing = pygame.Surface((width, height), pygame.SRCALPHA)
# Body - bright colors with uneven lines
pygame.draw.polygon(kids_drawing, (255, 100, 100), [
    (20, 50), (width-20, 45), (width-15, height-60), (15, height-55)
])
# Windows - scribbled
for i in range(5):
    pygame.draw.line(kids_drawing, (100, 150, 255), 
                    (25 + i*5, 60), (25 + i*5, 90), 3)
    pygame.draw.line(kids_drawing, (100, 150, 255), 
                    (width-45 + i*5, 60), (width-45 + i*5, 90), 3)
# Wheels - wobbly circles
pygame.draw.circle(kids_drawing, (80, 80, 80), (35, height-35), 18, 5)
pygame.draw.circle(kids_drawing, (80, 80, 80), (width-35, height-35), 18, 5)
pygame.draw.circle(kids_drawing, (80, 80, 80), (35, 35), 18, 5)
pygame.draw.circle(kids_drawing, (80, 80, 80), (width-35, 35), 18, 5)
# Smiley face on front
pygame.draw.circle(kids_drawing, (255, 200, 0), (width//2, 25), 15)
pygame.draw.circle(kids_drawing, (0, 0, 0), (width//2-5, 20), 3)
pygame.draw.circle(kids_drawing, (0, 0, 0), (width//2+5, 20), 3)
pygame.draw.arc(kids_drawing, (0, 0, 0), (width//2-8, 22, 16, 12), 0, 3.14, 2)

# Save the sprites
pygame.image.save(professional, os.path.join(output_dir, "professional.png"))
pygame.image.save(kids_drawing, os.path.join(output_dir, "kids_drawing.png"))

print("Created EV placeholder sprites!")