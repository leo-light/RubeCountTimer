from PIL import Image, ImageDraw

def create_icon():
    # Create a 256x256 image with a dark grey background
    size = (256, 256)
    image = Image.new('RGBA', size, (34, 37, 42, 255))
    draw = ImageDraw.Draw(image)
    
    # Draw a blue circle (the stopwatch body)
    padding = 20
    draw.ellipse([padding, padding, size[0]-padding, size[1]-padding], 
                 outline=(60, 164, 255, 255), width=10)
    
    # Draw a small rectangle at the top (the button)
    btn_w = 40
    btn_h = 20
    draw.rectangle([size[0]//2 - btn_w//2, padding - btn_h, 
                    size[0]//2 + btn_w//2, padding], 
                   fill=(60, 164, 255, 255))
    
    # Draw a "T" (for Timer) or some clock hands
    # Let's do a simple clock hand pointing at 12 and 3
    center = size[0]//2
    draw.line([center, center, center, padding + 40], fill=(60, 164, 255, 255), width=8)
    draw.line([center, center, center + 60, center], fill=(60, 164, 255, 255), width=8)
    
    # Save as ICO
    image.save('icon.ico', format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("Icon created: icon.ico")

if __name__ == "__main__":
    create_icon()
