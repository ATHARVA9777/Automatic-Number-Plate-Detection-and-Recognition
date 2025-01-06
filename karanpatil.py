import cv2
import numpy as np
import easyocr
import imutils
import os

def detect_text_from_images(folder_path):
    detected_texts = []
    reader = easyocr.Reader(['en'])

    # Loop through images in the specified folder
    for filename in os.listdir(folder_path):
        if filename.endswith((".jpg", ".png", ".jpeg")):
            img_path = os.path.join(folder_path, filename)

            img = cv2.imread(img_path)
            if img is None:
                print(f"Image {filename} could not be loaded.")
                continue

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Apply bilateral filter to remove noise while preserving edges
            bfilter = cv2.bilateralFilter(gray, 11, 17, 17)

            # Detect edges in the image
            edged = cv2.Canny(bfilter, 30, 200)

            # Find contours in the image
            keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours = imutils.grab_contours(keypoints)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

            location = None
            for contour in contours:
                approx = cv2.approxPolyDP(contour, 10, True)
                if len(approx) == 4:
                    location = approx
                    break

            if location is None:
                print(f"Number plate contour not found in {filename}.")
                continue

            mask = np.zeros(gray.shape, np.uint8)
            new_image = cv2.drawContours(mask, [location], 0, 255, -1)
            new_image = cv2.bitwise_and(img, img, mask=mask)

            (x, y) = np.where(mask == 255)
            (x1, y1) = (np.min(x), np.min(y))
            (x2, y2) = (np.max(x), np.max(y))
            cropped_image = gray[x1:x2 + 1, y1:y2 + 1]

            # Use EasyOCR to read text from the cropped image
            result = reader.readtext(cropped_image)

            if result:
                text = result[0][-2]
                detected_texts.append((filename, text))
                print(f"Detected Text from {filename}: {text}")

                # Display the detected text on the image
                font = cv2.FONT_HERSHEY_SIMPLEX
                img = cv2.putText(img, text=text, org=(location[0][0][0], location[1][0][1] + 60),
                                  fontFace=font, fontScale=1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
                img = cv2.polylines(img, [location], isClosed=True, color=(0, 255, 0), thickness=3)

                # Show the image with the detected text
                cv2.imshow(f"Detected Number Plate - {filename}", img)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            else:
                print(f"No text detected in {filename}.")

    return detected_texts


if __name__ == "__main__":
    folder_path = "C:\\Users\\Admin\\Desktop\\NumberPlate"  # Update this path
    detected_texts = detect_text_from_images(folder_path)
    print("Detection complete. Found texts:", detected_texts)
