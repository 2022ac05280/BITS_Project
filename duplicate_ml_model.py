import os
import shutil
import numpy as np
import cv2
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Model
from sklearn.metrics.pairwise import cosine_similarity

def extract_features(img_path, model):
    img = image.load_img(img_path, target_size=(224, 224))
    img_data = image.img_to_array(img)
    img_data = np.expand_dims(img_data, axis=0)
    img_data = preprocess_input(img_data)
    features = model.predict(img_data)
    return features.flatten()

def is_blurred(img_path, threshold=100):
    img = cv2.imread(img_path)
    if img is None:
        print(f"Failed to read image: {img_path}")
        return False
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    print(f"Image: {img_path}, Variance: {variance}")
    return variance < threshold

def is_screenshot(img_path):
    img = cv2.imread(img_path)
    if img is None:
        print(f"Failed to read image: {img_path}")
        return False
    height, width, _ = img.shape
    aspect_ratio = width / height
    return aspect_ratio > 1.7 or aspect_ratio < 0.6

def find_duplicate_images(folder_path, model, threshold=0.9):
    features_dict = {}
    duplicates = []
    blurred_images = []
    screenshots = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if is_blurred(file_path):
                blurred_images.append(file_path)
                continue
            if is_screenshot(file_path):
                screenshots.append(file_path)
                continue
            features = extract_features(file_path, model)
            for existing_file, existing_features in features_dict.items():
                similarity = cosine_similarity([features], [existing_features])[0][0]
                if similarity > threshold:
                    duplicates.append((file_path, existing_file))
                    break
            else:
                features_dict[file_path] = features

    return duplicates, blurred_images, screenshots

def move_files(files, target_folder):
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    for file in files:
        shutil.move(file, os.path.join(target_folder, os.path.basename(file)))

if __name__ == "__main__":
    folder_path = input("Enter the path to the folder: ")
    duplicates_folder = os.path.join(folder_path, "duplicates")
    
    base_model = VGG16(weights='imagenet')
    model = Model(inputs=base_model.input, outputs=base_model.get_layer('fc1').output)
    
    duplicates, blurred_images, screenshots = find_duplicate_images(folder_path, model)
    
    if duplicates:
        print("Duplicate images found:")
        for dup in duplicates:
            print(f"{dup[0]} is a duplicate of {dup[1]}")
        move_files([dup[0] for dup in duplicates], duplicates_folder)
    
    if blurred_images:
        print("Blurred images found:")
        for img in blurred_images:
            print(f"Blurred image: {img}")
        move_files(blurred_images, duplicates_folder)
    
    if screenshots:
        print("Screenshots found:")
        for img in screenshots:
            print(f"Screenshot: {img}")
        move_files(screenshots, duplicates_folder)
    
    if not duplicates and not blurred_images and not screenshots:
        print("No duplicate, blurred images, or screenshots found.")
    else:
        print(f"All identified images have been moved to {duplicates_folder}")