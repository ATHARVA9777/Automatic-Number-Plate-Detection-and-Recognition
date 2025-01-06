import os

image_directory ="C:\\Users\\Admin\\Desktop\\NumberPlate"


image_files = [f for f in os.listdir(image_directory) if os.path.isfile(os.path.join(image_directory, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

for image_file in image_files:
    image_name = os.path.splitext(image_file)[0]
    txt_file = image_name + ".txt"

    if not os.path.exists(os.path.join(image_directory, txt_file)):
        os.remove(os.path.join(image_directory, image_file))
        print(f"Deleted {image_file} because {txt_file} does not exist.")