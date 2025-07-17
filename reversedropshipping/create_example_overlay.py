#!/usr/bin/env python3
"""
Create an example overlay image for testing
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_example_overlay():
    # Create a transparent image
    width, height = 400, 100
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Try to use a system font, fallback to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 36)
        except:
            font = ImageFont.load_default()
    
    # Add text with background
    text = "Let's expose a dropshipper"
    
    # Calculate text size
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Calculate position to center text
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw text background (semi-transparent black)
    padding = 10
    draw.rectangle([x-padding, y-padding, x+text_width+padding, y+text_height+padding], 
                   fill=(0, 0, 0, 128))
    
    # Draw text (white with black outline)
    # Draw outline
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx != 0 or dy != 0:
                draw.text((x+dx, y+dy), text, font=font, fill=(0, 0, 0, 255))
    
    # Draw main text
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    
    # Save the image
    output_path = os.path.join("overlay", "example_overlay.png")
    img.save(output_path)
    print(f"Example overlay created: {output_path}")
    print("You can replace this with your own overlay image in the 'overlay' folder")

if __name__ == "__main__":
    create_example_overlay()
