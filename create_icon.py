from PIL import Image, ImageDraw

def create_icon():
    # Create a 256x256 image with a dark grey background
    size = (256, 256)
    center = size[0]//2
    
    # Using a solid background
    image = Image.new('RGBA', size, (30, 30, 30, 255))
    draw = ImageDraw.Draw(image)
    
    # Draw a blue rounded rectangle (the stopwatch body)
    padding = 30
    draw.rounded_rectangle([padding, padding, size[0]-padding, size[1]-padding], 
                          radius=50, outline=(60, 164, 255, 255), width=15)
    
    # Draw a small button on top
    draw.rectangle([center-30, padding-20, center+30, padding], fill=(60, 164, 255, 255))
    
    # Draw clock hands
    # Hour hand
    draw.line([center, center, center, center - 60], fill=(255, 255, 255, 255), width=12)
    # Minute hand
    draw.line([center, center, center + 70, center], fill=(60, 164, 255, 255), width=10)
    
    # Draw a small dot at center
    draw.ellipse([center-10, center-10, center+10, center+10], fill=(255, 255, 255, 255))
    
    # Save as ICO with all standard sizes
    icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    image.save('icon.ico', format='ICO', sizes=icon_sizes)
    print("Icon created successfully: icon.ico")

if __name__ == "__main__":
    create_icon()
