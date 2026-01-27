from PIL import Image
import os

def make_transparent(img_path):
    img = Image.open(img_path).convert("RGBA")
    data = img.getdata()
    
    new_data = []
    for item in data:
        # If the pixel is black (or very close), make it transparent
        if item[0] < 20 and item[1] < 20 and item[2] < 20:
            new_data.append((0, 0, 0, 0))
        else:
            new_data.append(item)
            
    img.putdata(new_data)
    img.save(img_path, "PNG")
    print(f"Processed {img_path}")

if __name__ == "__main__":
    make_transparent("/Users/chronoai-oliverni/github/godgpt-performance/logolong.png")
