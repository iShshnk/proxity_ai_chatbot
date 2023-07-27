from PIL import Image
import numpy as np
import io
import face_recognition
from rembg import remove

def remove_bg(input_img_path):
    # Load the image using PIL
    original_img = Image.open(input_img_path)

    # Convert the PIL Image to numpy array for face recognition
    img_np = np.array(original_img)

    # Detect faces in the image
    face_locations = face_recognition.face_locations(img_np)

    # Check if a face is detected
    if not face_locations:
        print('No face detected in the image.')
        return

    # Get the bounding box of the first face
    top, right, bottom, left = face_locations[0]

    # Increase the size of the bounding box by 50% to include more context
    height, width, _ = img_np.shape
    x = max(0, left - int((right - left) * 0.5))
    y = max(0, top - int((bottom - top) * 0.5))
    w = min(width, right + int((right - left) * 0.5)) - x
    h = min(height, bottom + int((bottom - top) * 0.5)) - y

    # Crop the image to the bounding box
    cropped_img_np = img_np[y:y+h, x:x+w]

    # Convert the cropped image to bytes
    cropped_img_pil = Image.fromarray(cropped_img_np)
    img_bytes = io.BytesIO()
    cropped_img_pil.save(img_bytes, format='PNG')

    # Remove background
    result = remove(img_bytes.getvalue())

    # Convert the result into a PIL Image
    output_img = Image.open(io.BytesIO(result))

    # Make the background white
    bg = Image.new('RGBA', output_img.size, (255,255,255,255))
    bg.paste(output_img, mask=output_img)

    # Save the output image (change output path as needed)
    bg.save("output_image.png")

remove_bg("your_image.jpg")

"""from rembg import remove
from PIL import Image
import cv2

def remove_bg(input_img_path):
    # Load the image using OpenCV
    original_img = cv2.imread(input_img_path)

    # Convert the image to RGB (OpenCV uses BGR by default)
    original_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)

    # Load Haar cascade XML for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(original_img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Check if a face is detected
    if len(faces) == 0:
        print('No face detected in the image.')
        return

    # Get the bounding box of the first face
    x, y, w, h = faces[0]

    # Increase the size of the bounding box by 50% to include more context
    x = max(0, x - int(w * 0.5))
    y = max(0, y - int(h * 0.5))
    w += int(w * 0.63)
    h += int(h * 0.63)

    # Crop the image to the bounding box
    cropped_img = original_img[y:y+h, x:x+w]

    # Convert the cropped image to PIL Image
    cropped_img_pil = Image.fromarray(cropped_img)

    # Remove background
    output = remove(cropped_img_pil)

    # Make the background white
    bg = Image.new('RGBA', output.size, (255, 255, 255, 255))
    bg.paste(output, mask=output)

    # Save the output image
    return bg"""
