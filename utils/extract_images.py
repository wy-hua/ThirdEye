import os
import csv

# Folder containing images
image_folder = "/Users/weiying/Downloads/Presentation"
csv_file = "image_list.csv"

# Process images and write to CSV
with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["image_name"])  # Header

    # Get all image files and sort them
    image_files = []
    for filename in os.listdir(image_folder):
        if filename.lower().endswith((".jpg", ".jpeg", ".heic")):
            image_files.append(filename)
    
    # Sort filenames alphabetically
    image_files.sort()
    
    # Write sorted files to CSV
    for filename in image_files:
        print(filename)
        writer.writerow([filename])

print(f"CSV file created: {csv_file}")