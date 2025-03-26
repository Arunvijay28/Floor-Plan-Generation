import json
import cv2
import numpy as np

# Paths to files
def filter_it(image_path=r"D:\Research\FYP\App\experimentation\bin_pack\rectified_image.png"):
    #image_path = r"D:\Research\FYP\App\experimentation\bin_pack\rectified_image.png"
    boundary_json_path = "./simulated_annealing/boundary_data.json"
    inside_json_path = "./simulated_annealing/inside_data.json"

    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError("Image file not found!")

    # Load JSON files with pixel coordinates
    def load_json(file_path, has_extra=False):
        with open(file_path, 'r') as f:
            data = json.load(f)
            if has_extra:
                return set((x, y) for x, y, _ in data)  # Extract only (x, y) ignoring the third value
            return set(map(tuple, data))

    boundary_pixels = load_json(boundary_json_path, has_extra=True)
    inside_pixels = load_json(inside_json_path)
    allowed_pixels = boundary_pixels.union(inside_pixels)

    # Get image dimensions
    height, width, _ = image.shape

    # Process the image
    for y in range(height):
        for x in range(width):
            if (x, y) not in allowed_pixels:
                image[y, x] = [255, 255, 255]  # Set to white

    # Save the modified image
    output_path = image_path.replace(".png", "_filtered.png")
    cv2.imwrite(output_path, image)
    print(f"Processed image saved at: {output_path}")
