from .ins_2 import calculate_pixels
import json

def main():
    img="./static/uploads/uploaded_image.png"
    boundary,inside,other=calculate_pixels(img)
    
    boundary_path = "./simulated_annealing/boundary_data.json"
    with open(boundary_path, "w") as f:
        json.dump(boundary, f)
    print(f"Coordinates saved to {boundary_path}")
    