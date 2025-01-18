import os
import hashlib
import shutil

"""
    Computes the MD5 hash of a file.
    
    Args:
        file_path (str): The path to the file for which the hash is to be computed.
    
    Returns:
        str: The MD5 hash of the file in hexadecimal format.
"""

def get_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def find_duplicate_images(folder_path):
    hashes = {}
    duplicates = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_hash = get_file_hash(file_path)
            if file_hash in hashes:
                duplicates.append((file_path, hashes[file_hash]))
            else:
                hashes[file_hash] = file_path

    return duplicates

def move_duplicates(duplicates, duplicates_folder):
    if not os.path.exists(duplicates_folder):
        os.makedirs(duplicates_folder)
    for dup in duplicates:
        shutil.move(dup[0], os.path.join(duplicates_folder, os.path.basename(dup[0])))

if __name__ == "__main__":
    folder_path = input("Enter the path to the folder: ")
    duplicates_folder = os.path.join(folder_path, "duplicates")
    duplicates = find_duplicate_images(folder_path)
    if duplicates:
        print("Duplicate images found:")
        for dup in duplicates:
            print(f"{dup[0]} is a duplicate of {dup[1]}")
        move_duplicates(duplicates, duplicates_folder)
        print(f"Duplicate images have been moved to {duplicates_folder}")
    else:
        print("No duplicate images found.")