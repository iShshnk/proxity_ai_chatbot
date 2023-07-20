from rembg import remove
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
    return bg