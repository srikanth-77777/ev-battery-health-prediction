import os
from PIL import Image, ImageDraw, ImageFont

def generate_sample_images(output_dir="waste_app/static/samples"):
    os.makedirs(output_dir, exist_ok=True)
    
    samples = [
        ("cardboard.jpg", "Cardboard Box", (210, 180, 140), "📦", "Corrugated Shipping Box\nFlattened Packaging"),
        ("paper.jpg", "Office Paper", (240, 240, 245), "📄", "Printed Document Sheets\nNotebook Paper"),
        ("plastic.jpg", "Plastic Bottle", (173, 216, 230), "🧴", "PET Clear Water Bottle\nPolyethylene Container"),
        ("glass.jpg", "Glass Jar", (200, 230, 225), "🫙", "Clear Soda-Lime Glass Jar\nBeverage Bottle"),
        ("metal.jpg", "Aluminum Can", (192, 192, 192), "🥫", "Crushed Soda Can\nTin Food Container"),
        ("organic.jpg", "Fruit & Veg Waste", (180, 220, 160), "🍏", "Apple Core & Peels\nBiodegradable Foliage"),
        ("trash.jpg", "Non-Recyclable Trash", (160, 160, 165), "🗑️", "Multi-layer Chip Bag\nContaminated Wrapper")
    ]
    
    for filename, name, bg_color, emoji, desc in samples:
        img = Image.new("RGB", (400, 400), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # Draw decorative inner border
        draw.rectangle([15, 15, 385, 385], outline=(100, 100, 100), width=3)
        draw.rectangle([22, 22, 378, 378], outline=(255, 255, 255), width=2)
        
        # Center card
        draw.rectangle([50, 60, 350, 340], fill=(255, 255, 255), outline=(200, 200, 200), width=2)
        
        # Top banner
        draw.rectangle([50, 60, 350, 110], fill=(15, 76, 58))
        
        # Text details
        draw.text((80, 75), name.upper(), fill=(255, 255, 255))
        draw.text((120, 160), f"[{name}]", fill=(30, 41, 59))
        draw.text((70, 240), desc, fill=(100, 116, 139))
        draw.text((85, 305), "SRM Smart Waste Dataset Sample", fill=(16, 185, 129))
        
        path = os.path.join(output_dir, filename)
        img.save(path, "JPEG", quality=95)
        print(f"Generated sample: {path}")

if __name__ == "__main__":
    generate_sample_images()
