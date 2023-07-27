from rembg import remove
from PIL import Image
import numpy as np
import io

def remove_bg(input_img_path):
    # Load the image using PIL
    original_img = Image.open(input_img_path)

    # Convert the image to bytes
    img_bytes = io.BytesIO()
    original_img.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()

    # Remove background
    result = remove(img_bytes)

    # Convert the result into a PIL Image
    output_img = Image.open(io.BytesIO(result))

    # Make the background white
    bg = Image.new('RGBA', output_img.size, (255,255,255,255))
    bg.paste(output_img, mask=output_img)

    # Save the output image (change output path as needed)
    bg.save("output_image.png")

