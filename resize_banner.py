from PIL import Image
import sys
import os

input_path = r"C:/Users/Wellyton/.gemini/antigravity/brain/3915a2c1-8dc2-42b0-bb30-72533c61171b/bigodetexas_banner_1764091407624.png"
output_path = r"C:/Users/Wellyton/.gemini/antigravity/brain/3915a2c1-8dc2-42b0-bb30-72533c61171b/bigodetexas_banner_final.png"

try:
    if not os.path.exists(input_path):
        print(f"Input file not found: {input_path}")
        sys.exit(1)

    img = Image.open(input_path)
    # Resize with high quality resampling
    # The user wants 680x240. This is 17:6 aspect ratio.
    # We force the resize to these dimensions.
    img = img.resize((680, 240), Image.Resampling.LANCZOS)
    img.save(output_path)
    print(f"Successfully resized to {output_path}")
except ImportError:
    print("Pillow not installed")
except Exception as e:
    print(f"Error: {e}")
