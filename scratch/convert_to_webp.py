import os
from PIL import Image

def main():
    comic_root = "src/assets/learning-comic"
    if not os.path.exists(comic_root):
        print(f"Error: {comic_root} not found.")
        return
        
    converted_count = 0
    deleted_count = 0
    
    for root, dirs, files in os.walk(comic_root):
        for f in files:
            if f.endswith(".png"):
                png_path = os.path.join(root, f)
                webp_name = f[:-4] + ".webp"
                webp_path = os.path.join(root, webp_name)
                
                try:
                    # Convert to webp
                    with Image.open(png_path) as img:
                        img.save(webp_path, "WEBP", quality=80)
                    converted_count += 1
                    
                    # Remove original png
                    os.remove(png_path)
                    deleted_count += 1
                    
                except Exception as e:
                    print(f"Error processing {png_path}: {e}")
                    
    print(f"WebP Conversion Complete:")
    print(f"  Converted: {converted_count} files")
    print(f"  Deleted: {deleted_count} source PNG files")

if __name__ == "__main__":
    main()
