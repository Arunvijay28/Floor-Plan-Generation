import cv2
import numpy as np
import json
from PIL import Image, ImageDraw
from scipy.spatial import Voronoi

def generate_voronoi_with_boundary(seeds, weights):
    with open("./simulated_annealing/boundary_data.json", "r") as file:
        boundary = json.load(file)
    with open("./simulated_annealing/inside_data.json", "r") as file:
        inside = json.load(file)

    # Image dimensions
    img_width, img_height = 256, 256
    img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)
    boundary_set = set((x, y) for x, y, c in boundary if c == 0)
    inside_set = set((x, y) for x, y in inside)
    colors = [
        (173, 216, 230),  # Light Blue
        (240, 128, 128),  # Light Coral
        (255, 215, 0),    # Gold
        (107, 142, 35),   # Olive Drab
        (255, 165, 0),    # Orange
        (238, 232, 170),  # Pale Goldenrod
    ]
    vor = Voronoi(seeds)
    for x in range(img_width):
        for y in range(img_height):
            if (x, y) in inside_set:  # Ensure pixel is inside the boundary
                min_dist = float('inf')
                closest_idx = -1
                for idx, (sx, sy) in enumerate(seeds):
                    # Apply weighted expansion
                    dist = ((x - sx) ** 2 + (y - sy) ** 2) / weights[idx]
                    if dist < min_dist:
                        min_dist = dist
                        closest_idx = idx
                img.putpixel((x, y), colors[closest_idx])
    for x, y in boundary_set:
        img.putpixel((x, y), (0, 0, 0))
    output_path = "./simulated_annealing/voronoi_expansion_weighted.png"
    img.save(output_path)    
    print("saved_path:",output_path)
    return output_path

# if __name__ == "__main__":
#     seeds = [(50, 50), (150, 50), (100, 150), (200, 200)]  # Example seeds
#     weights = [1, 2, 1.5, 3]  # Example weights
#     voronoi_image_path = generate_voronoi_with_boundary(seeds, weights)
#     output_path = r"D:\Arun\SSN\FYP\generation\arshat\to_be_sent\to_be_sent\smoothed_boundaries.png"
