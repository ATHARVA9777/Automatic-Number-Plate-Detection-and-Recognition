from flask import Flask, render_template_string, request, jsonify, send_from_directory
import cv2
import os
import easyocr
import numpy as np
import imutils

app = Flask(__name__)

VIDEO_PATH = 'mycarplate.mp4'
IMAGE_FOLDER = 'C:\\Users\\Admin\\Desktop\\NumberPlate'
os.makedirs(IMAGE_FOLDER, exist_ok=True)


def capture_frames_from_video():
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print("Error: Couldn't open video.")
        return

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % 30 == 0:
            image_filename = os.path.join(IMAGE_FOLDER, f"frame_{frame_count}.jpg")
            cv2.imwrite(image_filename, frame)
            print(f"Captured image: {image_filename}")

    cap.release()



def detect_number_plate():
    reader = easyocr.Reader(['en'])
    results = []

    for filename in os.listdir(IMAGE_FOLDER):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            img_path = os.path.join(IMAGE_FOLDER, filename)
            img = cv2.imread(img_path)

            if img is None:
                continue


            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            bfilter = cv2.bilateralFilter(gray, 11, 17, 17)
            edged = cv2.Canny(bfilter, 30, 200)


            keypoints = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(imutils.grab_contours(keypoints), key=cv2.contourArea, reverse=True)[:10]

            plate_location = None
            for contour in contours:
                approx = cv2.approxPolyDP(contour, 10, True)
                if len(approx) == 4:
                    plate_location = approx
                    break

            if plate_location is None:
                continue

            mask = np.zeros(gray.shape, np.uint8)
            new_image = cv2.drawContours(mask, [plate_location], 0, 255, -1)
            new_image = cv2.bitwise_and(img, img, mask=mask)
            (x, y) = np.where(mask == 255)
            cropped_image = gray[x.min():x.max() + 1, y.min():y.max() + 1]

            ocr_result = reader.readtext(cropped_image)
            text = ocr_result[0][-2] if ocr_result else "No text detected"
            results.append({'filename': filename, 'text': text})

    return results


def delete_images_without_txt():
    image_files = [f for f in os.listdir(IMAGE_FOLDER) if
                   os.path.isfile(os.path.join(IMAGE_FOLDER, f)) and f.lower().endswith(
                       ('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

    for image_file in image_files:
        image_name = os.path.splitext(image_file)[0]
        txt_file = image_name + ".txt"

        if not os.path.exists(os.path.join(IMAGE_FOLDER, txt_file)):
            os.remove(os.path.join(IMAGE_FOLDER, image_file))
            print(f"Deleted {image_file} because {txt_file} does not exist.")


@app.route('/')
def index():
    images = os.listdir(IMAGE_FOLDER)
    return render_template_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Number Plate Detection System</title>
            <script>
                // Function to detect number plates from images
                async function detectPlates() {
                    const response = await fetch('/detect', { method: 'POST' });
                    const data = await response.json();
                    alert("Detected plates:\n" + data.results.map(r => `${r.filename}: ${r.text}`).join('\n'));
                }

                // Function to delete an image
                async function deleteImage(filename) {
                    const response = await fetch(`/delete/${filename}`, { method: 'DELETE' });
                    const result = await response.json();
                    if (result.success) {
                        alert(result.message);
                        location.reload();
                    }
                }
            </script>
        </head>
        <body>
            <h1>Number Plate Detection System</h1>
            <button onclick="detectPlates()">Detect Plate Numbers</button>
            <button onclick="location.reload()">Refresh Image List</button>

            <h2>Images</h2>
            <div id="image-gallery">
                {% for image in images %}
                    <div>
                        <img src="{{ url_for('serve_image', filename=image) }}" alt="{{ image }}" width="200">
                        <button onclick="deleteImage('{{ image }}')">Delete</button>
                    </div>
                {% endfor %}
            </div>
        </body>
        </html>
    """, images=images)


# Route to detect number plates in images
@app.route('/detect', methods=['POST'])
def detect():
    results = detect_number_plate()
    return jsonify(results=results)


# Route to delete an image
@app.route('/delete/<filename>', methods=['DELETE'])
def delete(filename):
    try:
        os.remove(os.path.join(IMAGE_FOLDER, filename))
        return jsonify(success=True, message=f"Deleted {filename}")
    except Exception as e:
        return jsonify(success=False, message=str(e))


# Route to serve images to frontend
@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)


# Route to capture frames from the video
@app.route('/capture_frames')
def capture_frames():
    capture_frames_from_video()
    return "Frames captured successfully!"


# Route to delete images without corresponding .txt files
@app.route('/clean_images', methods=['POST'])
def clean_images():
    delete_images_without_txt()
    return "Images cleaned successfully!"


# Start the app
if __name__ == '__main__':
    app.run(debug=True)
